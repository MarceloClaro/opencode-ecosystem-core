"""Reserve, prepare, and supervise approved workflow processes in the daemon."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from ngs_workbench_execution_monitoring import DEFAULT_OBSERVER_REGISTRY
from ngs_workbench_execution_monitoring.models import empty_observation

from . import input_files, ssh
from .hashing import file_identity, sha256_tree
from .persistence import (
    NewRun,
    RunRecord,
    SqlAlchemyUnitOfWork,
    default_database,
    ensure_workspace_identity,
    read_workspace_identity,
    registry_path,
)
from .persistence.repository import TERMINAL_STATUSES
from .protocol import (
    IMPLEMENTATION_ID,
    ExecutionRequest,
    canonical_plan_checksum,
    execution_request_checksum,
    run_metadata_directory,
)
from .remote_operations import read_tail
from .state import daemon_directory, execution_authorization_path, read_private_json, state_root

_STOP_TIMEOUT_SECONDS = 5.0
_DOWNLOAD_TIMEOUT_SECONDS = 300.0


class RunCanceled(Exception):
    """Cancellation was committed before the next approved operation."""


@dataclass
class OwnedRun:
    request: ExecutionRequest
    registry_run_id: str
    lock: threading.RLock = field(default_factory=threading.RLock)
    process: subprocess.Popen[Any] | None = None
    transfer: subprocess.Popen[Any] | None = None
    remote_identity: dict[str, Any] | None = None
    canceled: bool = False
    controller_signaled: bool = False


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"approved path escapes its workspace: {path}") from exc


def _validate_request(request: ExecutionRequest) -> tuple[Path, Path]:
    if canonical_plan_checksum(request.plan) != request.plan_checksum:
        raise ValueError("approved plan contents do not match the approved checksum")
    if request.plan.get("ok") is not True or request.plan.get("runnable") is not True:
        raise ValueError("approved plan is not runnable")

    approved = request.plan["request"]
    effects = request.plan.get("effects")
    argv = request.plan.get("command_argv")
    if not isinstance(effects, dict) or not isinstance(argv, list) or not argv:
        raise ValueError("approved plan is missing its execution effects or controller argv")
    readiness = request.plan.get("readiness")
    if not isinstance(readiness, dict) or readiness.get("binding") != request.binding:
        raise ValueError("execution binding does not match the approved workflow plan")
    target_id = approved.get("target", {}).get("target_id")
    remote = approved.get("remote")
    if target_id != "local":
        if not isinstance(remote, dict):
            raise ValueError("approved SSH execution requires remote target details")
        saved = read_private_json(daemon_directory(create=False) / "targets.json") or {}
        configured = saved.get(target_id)
        if not isinstance(configured, dict) or configured.get("config_hash") != remote.get(
            "config_hash"
        ):
            raise ValueError("approved compute target changed before workflow execution")
        writes = effects.get("remote_writes")
        if not isinstance(writes, list) or any(
            item.get("destination") not in writes for item in remote.get("staged_files", [])
        ):
            raise ValueError("remote staging destinations are absent from the approved plan")
    elif remote is not None:
        raise ValueError("the local execution target cannot contain SSH execution effects")
    if not all(isinstance(argument, str) for argument in argv):
        raise ValueError("approved controller argv must contain only strings")

    if effects["run_dir"] != approved["run_dir"] or (
        remote is not None and remote["run_dir"] != approved["run_dir"]
    ):
        raise ValueError("execution effects must use the approved run_dir")
    run_dir = run_metadata_directory(target_id, approved["run_dir"])
    launch_log = (
        run_dir / "logs" / f"{request.binding}.log"
        if remote is not None
        else Path(effects["launch_log"])
    )
    input_files.validate_path(run_dir)
    input_files.validate_path(launch_log)
    _relative_to(run_dir, state_root())
    _relative_to(launch_log, run_dir if remote is not None else Path(effects["run_dir"]))

    approved_writes = effects.get("local_writes")
    if not isinstance(approved_writes, list) or not all(
        isinstance(path, str) for path in approved_writes
    ):
        raise ValueError("approved plan is missing its exact local write paths")
    if remote is None and str(launch_log) not in approved_writes:
        raise ValueError("controller log destination is absent from the approved plan")
    preparation = request.plan.get("preparation")
    if preparation is not None:
        preparation_writes = (
            effects.get("remote_writes", []) if remote is not None else approved_writes
        )
        if not isinstance(preparation, dict) or not isinstance(preparation.get("operations"), list):
            raise ValueError("approved preparation operations are malformed")
        for operation in preparation["operations"]:
            if not isinstance(operation, dict) or operation.get("path") not in preparation_writes:
                raise ValueError("preparation destination is absent from the approved plan")
    approved_plan_paths = [
        Path(operation.destination)
        for operation in request.files
        if operation.kind == "write_approved_plan"
    ]
    if approved_plan_paths != [run_dir / "workflow" / "approved_plan.json"]:
        raise ValueError("execution requires one exact approved plan audit file")
    for operation in request.files:
        destination = Path(operation.destination)
        if str(destination) not in approved_writes:
            raise ValueError(f"file destination is absent from the approved plan: {destination}")
        _relative_to(
            destination,
            run_dir
            if remote is not None or operation.kind == "write_approved_plan"
            else Path(effects["run_dir"]),
        )
        if destination.is_symlink():
            raise ValueError(f"approved destination must not be a symlink: {destination}")
        if operation.kind == "write_json" and operation.content is None:
            raise ValueError("approved JSON operation is missing its exact contents")
        if operation.kind in {"copy_file", "copy_tree"} and (
            operation.source is None
            or not Path(operation.source).is_absolute()
            or operation.source_sha256 is None
        ):
            raise ValueError("approved copy operation requires an absolute source and checksum")
    return run_dir, launch_log


def _run_record(registry_run_id: str) -> RunRecord:
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        record = unit_of_work.registry.get_run(registry_run_id)
    if record is None:
        raise KeyError(registry_run_id)
    return record


def _approved_plan(record: RunRecord) -> dict[str, Any]:
    plan = json.loads(Path(record.approved_plan_path).read_text(encoding="utf-8"))
    if not isinstance(plan, dict):
        raise ValueError("approved plan must be a JSON object")
    checksum = plan.pop("plan_checksum")
    if checksum != record.plan_checksum or canonical_plan_checksum(plan) != checksum:
        raise ValueError("durable approved workflow plan no longer matches its checksum")
    return plan


def _transition(
    registry_run_id: str,
    status: str,
    *,
    pid: int | None = None,
    return_code: int | None = None,
    failure_summary: str | None = None,
) -> RunRecord:
    with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
        assert unit_of_work.registry is not None
        current = unit_of_work.registry.get_run(registry_run_id)
        if current is None:
            raise KeyError(registry_run_id)
        if current.status == status:
            return current
        updated = unit_of_work.registry.transition_run(
            current.id,
            status,
            expected_revision=current.revision,
            pid=pid,
            return_code=return_code,
            failure_summary=failure_summary,
        )
        unit_of_work.commit()
    return updated


def _set_run_pid(registry_run_id: str, pid: int | None) -> None:
    with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
        assert unit_of_work.registry is not None
        unit_of_work.registry.set_run_pid(registry_run_id, pid)
        unit_of_work.commit()


def _stop_process(process: subprocess.Popen[Any]) -> tuple[int, bool]:
    completed = process.poll()
    if completed is not None:
        return completed, False
    try:
        if os.name == "nt":
            process.terminate()
        else:
            os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return process.wait(), False
    try:
        return process.wait(timeout=_STOP_TIMEOUT_SECONDS), True
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGKILL)
        return process.wait(), True


def _stop_orphaned_process(pid: int) -> None:
    try:
        if os.name == "nt":
            os.kill(pid, signal.SIGTERM)
            return
        if os.getpgid(pid) != pid:
            return
        os.killpg(pid, signal.SIGTERM)
        deadline = time.monotonic() + _STOP_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            os.killpg(pid, 0)
            time.sleep(0.05)
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def _check_canceled(owned: OwnedRun) -> None:
    if owned.canceled or _run_record(owned.registry_run_id).status in {
        "cancel_requested",
        "canceling",
        "canceled",
    }:
        raise RunCanceled


def _reject_symlink_parents(path: Path, root: Path) -> None:
    cursor = path.parent
    while cursor != root:
        if cursor.is_symlink():
            raise ValueError(f"approved destination parent must not be a symlink: {cursor}")
        if cursor == cursor.parent:
            raise ValueError(f"approved destination escapes its root: {path}")
        cursor = cursor.parent


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    if temporary.is_symlink() or path.is_symlink():
        raise ValueError(f"approved JSON destination must not be a symlink: {path}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _download(owned: OwnedRun, executable: str, item: dict[str, Any], destination: Path) -> None:
    command = [
        executable,
        "--fail",
        "--silent",
        "--show-error",
        "--proto",
        "=https",
        "--max-redirs",
        "0",
        "--output",
        str(destination),
        str(item["url"]),
    ]
    with owned.lock:
        _check_canceled(owned)
        process = subprocess.Popen(
            command,
            env=owned.request.environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=os.name != "nt",
        )
        owned.transfer = process
        try:
            _set_run_pid(owned.registry_run_id, process.pid)
        except Exception:
            owned.transfer = None
            _stop_process(process)
            raise
    try:
        _, stderr = process.communicate(timeout=_DOWNLOAD_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        _stop_process(process)
        raise ValueError(f"verified file download timed out for {item['url']}") from None
    finally:
        with owned.lock:
            owned.transfer = None
            _set_run_pid(owned.registry_run_id, None)
    if owned.canceled:
        raise RunCanceled
    if process.returncode != 0:
        detail = stderr.strip() if stderr else f"curl exited {process.returncode}"
        raise ValueError(f"verified file download failed for {item['url']}: {detail}")


def _prepare(owned: OwnedRun) -> None:
    input_files.prepare(
        owned.request.plan.get("preparation"),
        download=lambda executable, item, destination: _download(
            owned, executable, item, destination
        ),
        lock=owned.lock,
        checkpoint=lambda: _check_canceled(owned),
    )


def _apply_files(owned: OwnedRun) -> None:
    for operation in owned.request.files:
        destination = Path(operation.destination)
        root = (
            state_root()
            if destination.is_relative_to(state_root())
            else Path(owned.request.plan["effects"]["run_dir"])
        )
        with owned.lock:
            _check_canceled(owned)
            input_files.validate_path(destination)
            _reject_symlink_parents(destination, root)
            if operation.kind == "write_json":
                assert operation.content is not None
                _write_json(destination, operation.content)
            elif operation.kind == "write_approved_plan":
                _write_json(
                    destination,
                    {"plan_checksum": owned.request.plan_checksum, **owned.request.plan},
                )
            elif operation.kind == "copy_file":
                assert operation.source is not None
                source = Path(operation.source)
                if source.is_symlink() or file_identity(source)[1] != operation.source_sha256:
                    raise ValueError("approved source file changed before it could be staged")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            else:
                assert operation.source is not None
                source = Path(operation.source)
                if sha256_tree(source) != operation.source_sha256:
                    raise ValueError("approved source tree changed before it could be staged")
                shutil.copytree(
                    source,
                    destination,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )


def _verify_files(owned: OwnedRun, run_dir: Path) -> None:
    for operation in owned.request.files:
        destination = Path(operation.destination)
        root = (
            run_dir
            if destination.is_relative_to(run_dir)
            else Path(owned.request.plan["effects"]["run_dir"])
        )
        _reject_symlink_parents(destination, root)
        if destination.is_symlink():
            raise ValueError("approved execution file changed before controller launch")
        if operation.kind == "write_json":
            if json.loads(destination.read_text(encoding="utf-8")) != operation.content:
                raise ValueError("approved generated file changed before controller launch")
        elif operation.kind == "write_approved_plan":
            expected = {"plan_checksum": owned.request.plan_checksum, **owned.request.plan}
            if json.loads(destination.read_text(encoding="utf-8")) != expected:
                raise ValueError("approved plan file changed before controller launch")
        elif operation.kind == "copy_file":
            if file_identity(destination)[1] != operation.source_sha256:
                raise ValueError("approved staged file changed before controller launch")
        else:
            ignored = frozenset(
                Path(item.destination).relative_to(destination).as_posix()
                for item in owned.request.files
                if item.kind == "write_approved_plan"
                and Path(item.destination).is_relative_to(destination)
            )
            if sha256_tree(destination, excluded=ignored) != operation.source_sha256:
                raise ValueError("approved staged tree changed before controller launch")
    if owned.request.plan["request"].get("remote") is not None:
        return
    for value, checksum in owned.request.inputs.items():
        path = Path(value)
        if path.is_symlink() or not path.is_file() or file_identity(path)[1] != checksum:
            raise ValueError("approved input file changed before controller launch")


class RunManager:
    """Own subprocesses and their existing SQLite lifecycle in one daemon."""

    def __init__(self, instance_id: str) -> None:
        self._instance_id = instance_id
        self._lock = threading.RLock()
        self._runs: dict[str, OwnedRun] = {}
        self._reconcile_orphaned_runs()

    def has_active_work(self) -> bool:
        with self._lock:
            if self._runs:
                return True
        if not registry_path().is_file():
            return False
        with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
            assert unit_of_work.registry is not None
            return unit_of_work.registry.has_active_runs(IMPLEMENTATION_ID)

    def _reconcile_orphaned_runs(self) -> None:
        if not registry_path().is_file():
            return
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
            assert unit_of_work.registry is not None
            for record in unit_of_work.registry.list_daemon_owned_active_runs():
                if record.request.get("target", {}).get("target_id") != "local":
                    continue
                owner = record.request.get("daemon_owner")
                if not isinstance(owner, dict) or owner.get("implementation") != IMPLEMENTATION_ID:
                    continue
                previous_owner = owner.get("instance_id")
                if previous_owner == self._instance_id:
                    continue
                if record.pid is not None:
                    _stop_orphaned_process(record.pid)
                unit_of_work.registry.transition_run(
                    record.id,
                    "orphaned",
                    expected_revision=record.revision,
                    failure_summary="the owning local daemon exited before the workflow completed",
                )
            unit_of_work.commit()

    def execute(self, request: ExecutionRequest) -> dict[str, Any]:
        run_dir, launch_log = _validate_request(request)
        approved = request.plan["request"]
        if request.authorization is None:
            raise ValueError("workflow execution requires native approval")
        authorization_path = execution_authorization_path(
            daemon_directory(create=False),
            request.authorization,
        )
        expected_authorization = {
            "binding": request.binding,
            "plan_checksum": request.plan_checksum,
            "plan_name": approved["display_name"],
            "run_id": approved["run_id"],
            "execution_checksum": execution_request_checksum(request),
        }
        if read_private_json(authorization_path) != expected_authorization:
            raise ValueError("workflow execution requires its exact native-approved authorization")
        try:
            authorization_path.unlink()
        except FileNotFoundError:
            raise ValueError(
                "native-approved execution authorization was already consumed"
            ) from None
        with self._lock:
            storage = state_root()
            workspace_id = ensure_workspace_identity(storage)
            with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
                assert unit_of_work.registry is not None
                unit_of_work.registry.register_workspace(workspace_id, storage)
                existing = unit_of_work.registry.get_by_run_id(str(approved["run_id"]))
                if existing is None:
                    existing = unit_of_work.registry.get_by_run_directory(
                        workspace_id,
                        _relative_to(run_dir, storage),
                    )
                if existing is not None:
                    if existing.plan_checksum != request.plan_checksum:
                        raise ValueError(
                            "run identity already belongs to a different approved plan"
                        )
                    unit_of_work.commit()
                    return self._response(existing, self._runs.get(existing.id))
                # LEGACY_CLEANUP(2026-09-07): Pre-lineage plans become root attempt 1 without
                # rewriting approved bytes. Remove defaults when those plans are unsupported.
                first_run_id = str(approved.get("first_run_id", approved["run_id"]))
                attempt_number = int(approved.get("attempt_number", 1))
                if attempt_number > 1:
                    latest = unit_of_work.registry.get_latest_attempt(first_run_id)
                    if latest is None or latest.attempt_number != attempt_number - 1:
                        raise ValueError("approved workflow attempt is stale; create a fresh plan")
                if run_dir.exists():
                    raise ValueError(f"approved run directory already exists: {run_dir}")
                if (
                    approved.get("remote") is None
                    and Path(request.plan["effects"]["run_dir"]).exists()
                ):
                    raise ValueError("approved execution directory already exists")
                registered = unit_of_work.registry.allocate_approved_run(
                    NewRun(
                        workspace_id=workspace_id,
                        workspace_dir=storage,
                        external_run_id=str(approved["run_id"]),
                        first_run_id=first_run_id,
                        attempt_number=attempt_number,
                        binding=request.binding,
                        pipeline=str(approved["pipeline"]),
                        workflow=str(approved["workflow"]),
                        plan_checksum=request.plan_checksum,
                        request={
                            **request.metadata,
                            "started_at": datetime.now(UTC).isoformat(),
                            # Old daemons reconcile every run with daemon_instance_id.
                            # A new key keeps concurrent versions from killing each other's runs.
                            "daemon_owner": {
                                "implementation": IMPLEMENTATION_ID,
                                "instance_id": self._instance_id,
                            },
                        },
                        command_argv=list(request.plan["command_argv"]),
                        run_relative_path=_relative_to(run_dir, storage),
                        approved_plan_relative_path=_relative_to(
                            run_dir / "workflow" / "approved_plan.json", storage
                        ),
                        launch_log_relative_path=_relative_to(
                            run_dir / "logs" / f"{request.binding}.log", storage
                        ),
                    )
                )
                unit_of_work.commit()

            owned = OwnedRun(request=request, registry_run_id=registered.id)
            self._runs[registered.id] = owned
            threading.Thread(
                target=self._run,
                args=(owned, run_dir, launch_log),
                name=f"ngs-run-{approved['run_id']}",
                daemon=True,
            ).start()
            return self._response(registered, owned)

    def _run(self, owned: OwnedRun, run_dir: Path, launch_log: Path) -> None:
        try:
            if owned.remote_identity is not None:
                self._finish_remote(owned)
                return
            if owned.request.plan["request"].get("remote") is None:
                _prepare(owned)
            _apply_files(owned)
            with owned.lock:
                _check_canceled(owned)
                input_files.validate_path(run_dir)
                input_files.validate_path(launch_log)
                _reject_symlink_parents(
                    launch_log,
                    state_root()
                    if launch_log.is_relative_to(run_dir)
                    else Path(owned.request.plan["effects"]["run_dir"]),
                )
                _relative_to(run_dir, state_root())
                _verify_files(owned, run_dir)
                approved = owned.request.plan["request"]
                if approved.get("remote") is None:
                    launch_log.parent.mkdir(parents=True, exist_ok=True)
                    with launch_log.open("a", encoding="utf-8") as handle:
                        process = subprocess.Popen(
                            owned.request.plan["command_argv"],
                            cwd=owned.request.plan["effects"]["run_dir"],
                            env=owned.request.environment,
                            stdout=handle,
                            stderr=subprocess.STDOUT,
                            text=True,
                            start_new_session=os.name != "nt",
                        )
                    owned.process = process
                    try:
                        _transition(owned.registry_run_id, "running", pid=process.pid)
                    except Exception:
                        _stop_process(process)
                        raise

            if approved.get("remote") is not None:

                def transfer(process: subprocess.Popen[str] | None) -> None:
                    with owned.lock:
                        if process is not None:
                            _check_canceled(owned)
                        _set_run_pid(
                            owned.registry_run_id,
                            process.pid if process is not None else None,
                        )
                        owned.transfer = process

                ssh.stage(
                    owned.request.plan,
                    run_dir,
                    checkpoint=lambda: _check_canceled(owned),
                    transfer=transfer,
                )
                with owned.lock:
                    _check_canceled(owned)
                    identity = ssh.launch(owned.request.plan, owned.request.inputs)
                    owned.remote_identity = identity
                    try:
                        _transition(owned.registry_run_id, "running", pid=identity["pid"])
                    except Exception:
                        ssh.stop(approved["remote"], identity)
                        raise
                self._finish_remote(owned)
            else:
                assert owned.process is not None
                self._finish_controller(owned, owned.process.wait())
        except RunCanceled:
            with suppress(Exception):
                _transition(owned.registry_run_id, "canceled")
        except Exception as exc:
            if owned.process is None or owned.process.poll() is None:
                with suppress(Exception):
                    current = _run_record(owned.registry_run_id)
                    if current.status in {"cancel_requested", "canceling"} and owned.canceled:
                        _transition(current.id, "canceled")
                    else:
                        _transition(current.id, "failed", failure_summary=str(exc))
        finally:
            with self._lock:
                with suppress(Exception):
                    if _run_record(owned.registry_run_id).status in TERMINAL_STATUSES:
                        self._runs.pop(owned.registry_run_id, None)

    @staticmethod
    def _finish_remote(owned: OwnedRun) -> None:
        assert owned.remote_identity is not None
        remote = owned.request.plan["request"]["remote"]
        while True:
            try:
                with owned.lock:
                    if owned.canceled and not owned.controller_signaled:
                        ssh.stop(remote, owned.remote_identity)
                        owned.controller_signaled = True
                observed = ssh.status(remote, owned.remote_identity)
            except ssh.TransportError:
                time.sleep(1)
                continue
            if observed["running"]:
                time.sleep(0.5)
                continue
            code = observed.get("return_code")
            if owned.canceled and owned.controller_signaled and code != 0:
                _transition(owned.registry_run_id, "canceled", pid=owned.remote_identity["pid"])
                return
            if not isinstance(code, int):
                raise ValueError("remote workflow controller exited without its terminal receipt")
            if code == 0:
                _transition(
                    owned.registry_run_id,
                    "completed",
                    pid=owned.remote_identity["pid"],
                    return_code=code,
                )
            else:
                _transition(
                    owned.registry_run_id,
                    "failed",
                    pid=owned.remote_identity["pid"],
                    return_code=code,
                    failure_summary=f"remote workflow controller exited with status {code}",
                )
            return

    @staticmethod
    def _finish_controller(owned: OwnedRun, return_code: int) -> RunRecord:
        assert owned.process is not None
        with owned.lock:
            current = _run_record(owned.registry_run_id)
            if current.status in TERMINAL_STATUSES:
                return current
            if current.status == "starting":
                return _transition(
                    current.id,
                    "failed",
                    pid=owned.process.pid,
                    return_code=return_code,
                    failure_summary="workflow controller exited before its running state was recorded",
                )
            if return_code == 0 and not owned.controller_signaled:
                return _transition(
                    current.id, "completed", pid=owned.process.pid, return_code=return_code
                )
            if current.status in {"cancel_requested", "canceling"} and owned.controller_signaled:
                return _transition(
                    current.id, "canceled", pid=owned.process.pid, return_code=return_code
                )
            return _transition(
                current.id,
                "failed",
                pid=owned.process.pid,
                return_code=return_code,
                failure_summary=f"workflow controller exited with status {return_code}",
            )

    def observe(self, registry_run_id: str) -> dict[str, Any]:
        try:
            registered = _run_record(registry_run_id)
        except KeyError:
            return {"ok": False, "errors": [f"registry run does not exist: {registry_run_id}"]}
        owner = registered.request.get("daemon_owner")
        if not registered.request.get("daemon_instance_id") and not (
            isinstance(owner, dict) and isinstance(owner.get("instance_id"), str)
        ):
            return self._response(registered)
        with self._lock:
            owned = self._runs.get(registered.id)
            if (
                owned is None
                and registered.status not in TERMINAL_STATUSES
                and registered.request.get("target", {}).get("target_id") != "local"
            ):
                owner = registered.request.get("daemon_owner")
                if not isinstance(owner, dict) or owner.get("implementation") != IMPLEMENTATION_ID:
                    return self._response(registered)
                if registered.status == "starting" and (
                    registered.pid is not None or not Path(registered.approved_plan_path).is_file()
                ):
                    if registered.pid is not None:
                        _stop_orphaned_process(registered.pid)
                    registered = _transition(
                        registered.id,
                        "orphaned",
                        failure_summary="the owning daemon exited during SSH workflow staging",
                    )
                    return self._response(registered)
                if registered.pid is None and registered.status != "starting":
                    raise ValueError("running remote workflow is missing its controller identity")
                plan = _approved_plan(registered)
                remote = plan["request"]["remote"]
                try:
                    recovered = ssh.identity(remote, registered.pid)
                except ssh.TransportError:
                    if registered.status == "starting":
                        return self._response(registered)
                    raise
                except ValueError:
                    if registered.status != "starting":
                        raise
                    registered = _transition(
                        registered.id,
                        "orphaned",
                        failure_summary="the owning daemon exited during SSH workflow staging",
                    )
                    return self._response(registered)
                if registered.status == "starting":
                    registered = _transition(registered.id, "running", pid=recovered["pid"])
                canceling = registered.status in {"cancel_requested", "canceling"}
                owned = OwnedRun(
                    request=ExecutionRequest(
                        binding=registered.binding,
                        plan_checksum=registered.plan_checksum,
                        plan=plan,
                    ),
                    registry_run_id=registered.id,
                    remote_identity=recovered,
                    canceled=canceling,
                )
                if canceling:
                    if registered.status == "cancel_requested":
                        registered = _transition(registered.id, "canceling", pid=registered.pid)
                    if ssh.status(remote, recovered)["running"]:
                        ssh.stop(remote, recovered)
                    owned.controller_signaled = True
                self._runs[registered.id] = owned
                threading.Thread(
                    target=self._run,
                    args=(
                        owned,
                        Path(registered.run_dir),
                        Path(registered.launch_log_path),
                    ),
                    name=f"ngs-resume-{registered.external_run_id}",
                    daemon=True,
                ).start()
        if owned is not None and owned.process is not None:
            return_code = owned.process.poll()
            if return_code is not None and registered.status not in TERMINAL_STATUSES:
                registered = self._finish_controller(owned, return_code)
                with self._lock:
                    self._runs.pop(registered.id, None)
                owned = None
        return self._response(registered, owned)

    def update_analysis_summary(self, registry_run_id: str, summary_path: str) -> dict[str, Any]:
        """Save an agent-authored local file without changing workflow lifecycle."""
        try:
            record = _run_record(registry_run_id)
        except KeyError as exc:
            raise ValueError(f"run does not exist: {registry_run_id}") from exc
        workspace = Path(record.workspace_dir)
        if workspace.is_symlink() or read_workspace_identity(workspace) != record.workspace_id:
            raise ValueError("the registered workspace is unavailable or has changed identity")
        source = Path(summary_path)
        if not source.is_absolute() or not source.is_file():
            raise ValueError("summary_path must be an absolute local regular file")

        root = Path(record.run_dir)
        destination = root / "analysis_summary.md"
        _relative_to(root, workspace)
        _reject_symlink_parents(destination, workspace)
        if destination.is_symlink():
            raise ValueError("analysis summary destination must not contain symlinks")
        root.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(dir=root, prefix=".analysis-summary-")
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as output, source.open("rb") as incoming:
                shutil.copyfileobj(incoming, output)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
        return {"ok": True, "registry_run_id": record.id, "status": record.status}

    def observe_execution(self, registry_run_id: str) -> dict[str, Any]:
        """Read evidence without holding lifecycle locks or changing run state."""
        record = _run_record(registry_run_id)
        result: dict[str, Any] = {"warnings": []}
        evidence_path = None
        evidence_kind = "unavailable"
        try:
            remote = None
            if record.request["target"]["target_id"] != "local":
                plan = _approved_plan(record)
                remote = plan["request"]["remote"]
                effects = plan["effects"]
                relative_log = PurePosixPath(effects["launch_log"]).relative_to(effects["run_dir"])
            try:
                if remote is None:
                    path = Path(record.launch_log_path)
                    if not path.is_file():
                        raise ValueError("controller log is missing or not a regular file")
                    with path.open("rb") as handle:
                        tail = read_tail(handle)
                else:
                    tail = ssh.tail_file(remote, relative_log.as_posix())
                result["log_tail"] = tail
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                result.update(
                    log_tail=None, warnings=[f"Controller log unavailable: {str(exc)[-512:]}"]
                )

            if remote is None:
                result["execution"] = DEFAULT_OBSERVER_REGISTRY.observe(
                    Path(record.execution_dir), record.binding, record.status
                ).model_dump(mode="json")
            else:
                observer = DEFAULT_OBSERVER_REGISTRY.file_observer(record.binding)
                evidence_kind = observer.evidence_kind
                evidence_path = ssh.select_file(remote, observer.file_patterns)
                if evidence_path is None:
                    raise ValueError("execution evidence has not been produced yet")
                relative = PurePosixPath(evidence_path).relative_to(remote["run_dir"])
                with ssh.stream_file(remote, relative.as_posix()) as lines:
                    observation = observer.observe_lines(
                        lines, evidence_path=evidence_path, workflow_status=record.status
                    )
                result["execution"] = observation.model_dump(mode="json")
        except (
            KeyError,
            OSError,
            TypeError,
            ValueError,
            subprocess.TimeoutExpired,
        ) as exc:
            error = str(exc)[-512:]
            if "log_tail" not in result:
                result.update(log_tail=None, warnings=[f"Controller log unavailable: {error}"])
            result.setdefault(
                "execution",
                empty_observation(
                    engine=record.binding,
                    evidence_kind=evidence_kind,
                    evidence_path=evidence_path,
                    reason=error,
                ).model_dump(mode="json"),
            )
        return result

    def cancel(self, registry_run_id: str) -> dict[str, Any]:
        observed = self.observe(registry_run_id)
        if not observed.get("ok"):
            return observed
        with self._lock:
            owned = self._runs.get(registry_run_id)
        if owned is None:
            if observed.get("status") in TERMINAL_STATUSES:
                return observed
            return {
                "ok": False,
                "errors": ["refusing to terminate a controller not owned by this daemon"],
            }

        with owned.lock:
            current = _run_record(registry_run_id)
            if current.status in TERMINAL_STATUSES:
                return self._response(current, owned)
            if current.status not in {"cancel_requested", "canceling"}:
                current = _transition(current.id, "cancel_requested", pid=current.pid)
            owned.canceled = True
            process = owned.transfer or owned.process
            if process is not None and process.poll() is None:
                current = _transition(current.id, "canceling", pid=current.pid)
                _, signaled = _stop_process(process)
                if process is owned.process:
                    owned.controller_signaled = signaled
            elif owned.remote_identity is not None:
                _transition(current.id, "canceling", pid=current.pid)
                ssh.stop(owned.request.plan["request"]["remote"], owned.remote_identity)
                owned.controller_signaled = True
        return self._response(_run_record(registry_run_id), owned)

    @staticmethod
    def _response(record: RunRecord, owned: OwnedRun | None = None) -> dict[str, Any]:
        response = {
            "ok": True,
            "status": record.status,
            "run_id": record.external_run_id,
            "registry_run_id": record.id,
            "revision": record.revision,
            "pid": record.pid,
            "workflow": record.workflow,
            "run_dir": record.execution_dir,
            "command_argv": record.command_argv,
            "plan_checksum": record.plan_checksum,
            "process_owned": owned is not None,
            "display_name": record.request.get("display_name", record.workflow),
            "target": record.request.get("target"),
        }
        if owned is not None:
            response["warnings"] = list(owned.request.plan.get("warnings", []))
        response.update(record.request.get("response", {}))
        return response
