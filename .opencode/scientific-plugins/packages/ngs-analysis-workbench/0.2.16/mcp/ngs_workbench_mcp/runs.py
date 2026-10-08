"""Project durable run identity, lifecycle and evidence for MCP consumers."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any

from ngs_workbench_daemon import client as daemon_client
from ngs_workbench_daemon import input_files, ssh
from ngs_workbench_daemon.persistence import (
    RunFilters,
    RunRecord,
    SqlAlchemyUnitOfWork,
    default_database,
    read_workspace_identity,
    registry_path,
    workspace_identity_path,
)
from ngs_workbench_daemon.protocol import canonical_plan_checksum, run_metadata_directory
from ngs_workbench_daemon.state import state_root
from ngs_workbench_execution_monitoring.models import empty_observation

from .compute_targets import resolve_compute_target
from .json_io import read_json_object
from .plans import NextflowRunPlan, SnakemakeRunPlan
from .report import (
    analysis_summary_review,
    analysis_summary_takeaway,
    build_completed_report,
)


def resolve_run_directory(value: str, target_id: str) -> Path:
    path = PurePosixPath(value)
    if not path.is_absolute() or ".." in path.parts or path == PurePosixPath("/"):
        raise ValueError("run_dir must be an absolute directory on the selected target")
    return Path(path) if target_id != "local" else Path(path).resolve()


def check_run_directory(path: Path, target_id: str) -> None:
    if target_id == "local":
        input_files.check_run_directory(str(path))
    else:
        ssh.check_run_directory(resolve_compute_target(target_id).model_dump(), str(path))


def registry_effect_paths() -> list[str]:
    """Return persistence paths that an approved start may create or update."""
    return [str(workspace_identity_path(state_root())), str(registry_path())]


def execution_metadata(plan: NextflowRunPlan | SnakemakeRunPlan) -> dict[str, Any]:
    """Build the workflow-owned metadata stored with one daemon-managed run."""
    payload = plan.model_dump(mode="json")
    request = payload["request"]
    readiness = payload["readiness"]
    target = request["target"]
    return {
        "schema_version": plan.schema_version,
        "display_name": request["display_name"],
        "target": target,
        "plan_request": request,
        "execution_run_dir": payload["effects"]["run_dir"],
        "execution_launch_log": payload["effects"]["launch_log"]
        if target["target_id"] == "local"
        else None,
        "input_summary": payload["input_summary"],
        "runtime_summary": {
            "target": target,
            "scope": readiness["scope"],
            "snapshot_id": readiness.get("snapshot_id"),
            "host": readiness.get("host"),
            "commands": readiness["commands"],
            "selected_controller": readiness.get("selected_controller"),
            "docker": readiness.get("docker"),
        },
    }


def find_registered_run(target_id: str, run_dir: str) -> RunRecord | None:
    """Find an existing owner of an execution directory without allocating state."""
    storage_id = read_workspace_identity(state_root())
    if storage_id is None:
        return None
    relative = run_metadata_directory(target_id, run_dir).relative_to(state_root()).as_posix()
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        return unit_of_work.registry.get_by_run_directory(storage_id, relative)


def bind_run_lineage(
    payload: dict[str, Any],
    binding: str,
    first_run_id: str | None,
) -> dict[str, Any]:
    """Bind one independent execution to an explicit root recovery lineage."""
    if payload.get("ok") is not True:
        return payload
    request = payload.get("request")
    if not isinstance(request, dict):
        raise ValueError("workflow plan is missing its request")

    if first_run_id is None:
        request["first_run_id"] = request["run_id"]
        request["attempt_number"] = 1
        return payload

    if not registry_path().is_file():
        raise ValueError(f"first run does not exist: {first_run_id}")
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        first = unit_of_work.registry.get_first_run(first_run_id)
        latest = unit_of_work.registry.get_latest_attempt(first_run_id)
    if first is None or latest is None:
        raise ValueError(f"first run does not exist: {first_run_id}")
    if (
        first.binding != binding
        or first.pipeline != request.get("pipeline")
        or first.workflow != request.get("workflow")
    ):
        raise ValueError("first run belongs to a different workflow")
    if latest.status not in {"failed", "canceled"}:
        if latest.status == "orphaned":
            raise ValueError("orphaned run must be reconciled before recovery")
        raise ValueError(f"latest workflow attempt is not recoverable: {latest.status}")

    request["first_run_id"] = first_run_id
    request["attempt_number"] = latest.attempt_number + 1
    return payload


def _daemon_owner_instance(request: dict[str, Any]) -> str | None:
    owner = request.get("daemon_owner")
    if isinstance(owner, dict) and isinstance(owner.get("instance_id"), str):
        return owner["instance_id"]
    legacy = request.get("daemon_instance_id")
    return legacy if isinstance(legacy, str) else None


def _is_ssh(record: RunRecord) -> bool:
    return record.request.get("target", {}).get("target_id", "local") != "local"


def _cancel_registered_run(registered: RunRecord) -> dict[str, Any]:
    if registered.status in {"completed", "failed", "canceled", "orphaned"}:
        return {
            "ok": True,
            **registered.summary(),
            **_run_metadata(registered, _approved_plan(registered)),
            "plan_checksum": registered.plan_checksum,
            "target": registered.request.get("target"),
            "process_owned": False,
        }
    if not _daemon_owner_instance(registered.request):
        return {
            "ok": False,
            "errors": ["refusing to terminate a controller not owned by this daemon"],
        }
    return daemon_client.cancel(registered.id)


def list_registry_runs(
    *,
    statuses: list[str] | None = None,
    binding: str | None = None,
    pipeline: str | None = None,
    first_run_id: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """List bounded run summaries across registered workspaces."""
    filters = RunFilters(
        statuses=tuple(statuses or ()),
        binding=binding,
        pipeline=pipeline,
        first_run_id=first_run_id,
    )
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        records = unit_of_work.registry.list_runs(filters, limit=limit)
        daemon_owned = (
            []
            if filters.statuses
            and all(
                status in {"completed", "failed", "canceled", "orphaned"}
                for status in filters.statuses
            )
            else unit_of_work.registry.list_daemon_owned_active_runs(filters)
        )
    daemon_instance_id = None
    if daemon_owned:
        endpoint = daemon_client.healthy_daemon()
        if endpoint is None:
            endpoint = daemon_client.ensure_daemon_running()
            with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
                assert unit_of_work.registry is not None
                records = unit_of_work.registry.list_runs(filters, limit=limit)
        if endpoint is not None:
            daemon_instance_id = endpoint.instance_id
    return {
        "ok": True,
        "runs": [
            _registry_summary(record, daemon_instance_id=daemon_instance_id) for record in records
        ],
    }


def list_registry_run_lineages(*, limit: int = 20) -> dict[str, Any]:
    """List recent workflow groups without letting attempts consume the group limit."""
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        records = unit_of_work.registry.list_recent_lineages(lineage_limit=limit)
    daemon_owned = [
        record
        for record in records
        if record.status in {"starting", "running", "cancel_requested", "canceling"}
        and _daemon_owner_instance(record.request)
        and record.request.get("target", {}).get("target_id") == "local"
    ]
    daemon_instance_id = None
    if daemon_owned:
        endpoint = daemon_client.healthy_daemon() or daemon_client.ensure_daemon_running()
        if endpoint is not None:
            daemon_instance_id = endpoint.instance_id
            with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
                assert unit_of_work.registry is not None
                records = unit_of_work.registry.list_recent_lineages(lineage_limit=limit)
    return {
        "ok": True,
        "runs": [
            _registry_summary(record, daemon_instance_id=daemon_instance_id) for record in records
        ],
    }


def get_registry_run(registry_run_id: str) -> dict[str, Any]:
    """Return one local durable run detail without observing its controller."""
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        record = unit_of_work.registry.get_run(registry_run_id)
    if record is None:
        return {"ok": False, "errors": [f"registry run does not exist: {registry_run_id}"]}

    approved_plan = _approved_plan(record, validate_checksum=True)
    metadata = _run_metadata(record, approved_plan)
    detail = {
        "ok": True,
        "registry_run_id": record.id,
        "run_id": record.external_run_id,
        "first_run_id": record.first_run_id,
        "attempt_number": record.attempt_number,
        "binding": record.binding,
        "pipeline": record.pipeline,
        "workflow": record.workflow,
        "status": record.status,
        "revision": record.revision,
        "pid": record.pid,
        "started_at_ms": record.started_at_ms,
        "completed_at_ms": record.completed_at_ms,
        "returncode": record.return_code,
        "plan_checksum": record.plan_checksum,
        "command_argv": record.command_argv,
        "failure_summary": record.failure_summary,
        "display_name": metadata["display_name"],
        "target": metadata["target"],
        "run_dir": metadata["run_dir"],
        "profile": metadata["profile"],
        "workflow_revision": metadata["workflow_revision"],
        "input_summary": metadata["input_summary"],
        "runtime_summary": metadata["runtime_summary"],
        "warnings": (
            list(approved_plan.get("warnings", []))
            if approved_plan is not None
            else ["The durable approved plan is missing or no longer matches its checksum."]
        ),
    }
    if "workflow_source" in metadata:
        detail["workflow_source"] = metadata["workflow_source"]
    _add_analysis_summary(detail, record)
    return detail


def observe_registry_run(registry_run_id: str) -> dict[str, Any]:
    """Reconcile one run and observe its controller log and engine evidence."""
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        record = unit_of_work.registry.get_run(registry_run_id)
    if record is None:
        return {"ok": False, "errors": [f"registry run does not exist: {registry_run_id}"]}

    warnings: list[str] = []
    if record.status not in {"completed", "failed", "canceled", "orphaned"}:
        try:
            observed = daemon_client.observe(record.id)
            if observed is None:
                daemon_client.ensure_daemon_running()
                daemon_client.observe(record.id)
        except daemon_client.DaemonError as exc:
            warnings.append(f"Lifecycle observation unavailable: {str(exc)[:512]}")
        with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
            assert unit_of_work.registry is not None
            record = unit_of_work.registry.get_run(registry_run_id) or record

    try:
        evidence = daemon_client.observe_execution(record.id)
    except daemon_client.DaemonError as exc:
        reason = str(exc)[:512]
        evidence = {
            "log_tail": None,
            "warnings": [f"Execution evidence unavailable: {reason}"],
            "execution": empty_observation(
                engine=record.binding,
                evidence_kind="unavailable",
                evidence_path=None,
                reason=reason,
            ).model_dump(mode="json"),
        }
    execution_evidence = evidence["execution"]["evidence"]
    reason = execution_evidence.get("reason")
    warning = f"Execution evidence unavailable: {str(reason)[:512]}"
    if (
        execution_evidence.get("available") is False
        and reason
        and warning not in evidence["warnings"]
    ):
        evidence["warnings"].append(warning)
    return {
        "ok": True,
        "registry_run_id": record.id,
        "revision": record.revision,
        "status": record.status,
        "pid": record.pid,
        "returncode": record.return_code,
        "failure_summary": record.failure_summary,
        "log_tail": evidence.get("log_tail"),
        "execution": evidence["execution"],
        "warnings": [*warnings, *evidence.get("warnings", [])],
    }


def get_registry_run_report(registry_run_id: str) -> dict[str, Any]:
    """Build the local completed-result projection for one registered run."""
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        record = unit_of_work.registry.get_run(registry_run_id)
    if record is None:
        return {"ok": False, "errors": [f"registry run does not exist: {registry_run_id}"]}
    response: dict[str, Any] = {
        "ok": True,
        "registry_run_id": record.id,
        "revision": record.revision,
        "availability": "not_completed",
        "report": None,
    }
    if record.status != "completed":
        return response
    if _is_ssh(record):
        response["availability"] = "remote_results_not_projected"
        return response
    run_directory = Path(record.execution_dir)
    if not run_directory.is_dir():
        response["availability"] = "missing"
        return response
    approved_plan = _approved_plan(record, validate_checksum=True)
    metadata = _run_metadata(record, approved_plan)
    report = build_completed_report(
        run_directory,
        workspace_dir=run_directory,
        run_id=record.external_run_id,
        binding=record.binding,
        pipeline=record.pipeline,
        workflow=record.workflow,
        display_name=str(metadata["display_name"]),
        status=record.status,
        started_at_ms=record.started_at_ms,
        completed_at_ms=record.completed_at_ms,
    )
    if report is None:
        response["availability"] = "missing"
        return response
    report["summary"] = analysis_summary_review(
        Path(record.run_dir), workspace_dir=Path(record.workspace_dir)
    )
    response.update(availability="available", report=report)
    return response


def cancel_registry_run(registry_run_id: str) -> dict[str, Any]:
    """Cancel a durable run using its recorded workspace and engine identity."""
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.registry is not None
        record = unit_of_work.registry.get_run(registry_run_id)
    if record is None:
        return {"ok": False, "errors": [f"registry run does not exist: {registry_run_id}"]}
    return _cancel_registered_run(record)


def _registry_summary(
    record: RunRecord,
    *,
    daemon_instance_id: str | None = None,
) -> dict[str, Any]:
    approved_plan = _approved_plan(record)
    metadata = _run_metadata(record, approved_plan)
    summary = {
        **record.summary(),
        **metadata,
        "process_owned": (
            record.status not in {"completed", "failed", "canceled", "orphaned"}
            and daemon_instance_id is not None
            and _daemon_owner_instance(record.request) == daemon_instance_id
        ),
    }
    if record.failure_summary:
        summary["failure_summary"] = record.failure_summary
    summary["analysis_summary"] = analysis_summary_takeaway(
        Path(record.run_dir),
        workspace_dir=Path(record.workspace_dir),
        pipeline=record.pipeline,
        status=record.status,
    )
    return summary


def _add_analysis_summary(
    response: dict[str, Any],
    record: RunRecord,
) -> None:
    response["analysis_summary"] = analysis_summary_review(
        Path(record.run_dir), workspace_dir=Path(record.workspace_dir)
    )


def _approved_plan(
    record: RunRecord,
    *,
    validate_checksum: bool = False,
) -> dict[str, Any] | None:
    path = Path(record.approved_plan_path)
    if not path.is_file():
        return None
    try:
        payload = read_json_object(path)
        if (_is_ssh(record) or validate_checksum) and (
            payload.get("plan_checksum") != record.plan_checksum
            or canonical_plan_checksum(
                {key: value for key, value in payload.items() if key != "plan_checksum"}
            )
            != record.plan_checksum
        ):
            return None
        return payload
    except (OSError, ValueError):
        return None


def _run_metadata(
    record: RunRecord,
    approved_plan: dict[str, Any] | None,
) -> dict[str, Any]:
    plan = approved_plan
    plan_request = plan.get("request") if isinstance(plan, dict) else None
    indexed_request = record.request.get("plan_request")
    request = (
        plan_request
        if isinstance(plan_request, dict)
        else indexed_request
        if isinstance(indexed_request, dict)
        else record.request
    )
    input_summary = (
        plan.get("input_summary")
        if isinstance(plan, dict) and isinstance(plan.get("input_summary"), dict)
        else record.request.get("input_summary")
    )
    if not isinstance(input_summary, dict):
        if request.get("sample_sheet"):
            input_summary = {
                "source": "sample_sheet",
                "path": request.get("sample_sheet"),
                "sha256": request.get("sample_sheet_sha256"),
            }
        elif any(
            token.strip().lower() == "test"
            for token in str(request.get("profile") or "").split(",")
        ):
            input_summary = {"source": "workflow_test_profile"}
        elif request.get("config_file"):
            input_summary = {
                "source": "config_file",
                "path": request.get("config_file"),
                "sha256": request.get("config_sha256"),
            }
    runtime_summary = (
        plan.get("runtime")
        if isinstance(plan, dict) and isinstance(plan.get("runtime"), dict)
        else record.request.get("runtime_summary")
    )
    target = request.get("target") or record.request.get("target")
    if isinstance(target, dict):
        target = dict(target)
        remote = request.get("remote") if isinstance(plan, dict) else None
        if isinstance(remote, dict) and isinstance(remote.get("config_hash"), str):
            target["config_hash"] = remote["config_hash"]
        else:
            target.pop("config_hash", None)
    schema_version = next(
        (
            value
            for value in (
                plan.get("schema_version") if isinstance(plan, dict) else None,
                record.request.get("schema_version"),
            )
            if isinstance(value, int) and not isinstance(value, bool) and value > 0
        ),
        1,
    )
    metadata = {
        "run_dir": record.execution_dir,
        "metadata_schema_version": schema_version,
        "display_name": str(
            request.get("display_name") or record.request.get("display_name") or record.workflow
        ),
        "profile": request.get("profile"),
        "workflow_revision": request.get("revision"),
        "target": target if isinstance(target, dict) else None,
        "input_summary": input_summary if isinstance(input_summary, dict) else None,
        "runtime_summary": runtime_summary if isinstance(runtime_summary, dict) else None,
        "first_run_id": record.first_run_id,
        "attempt_number": record.attempt_number,
    }
    if isinstance(request.get("workflow_source"), dict):
        metadata["workflow_source"] = request["workflow_source"]
    return metadata
