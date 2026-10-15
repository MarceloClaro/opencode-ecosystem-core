"""R897: CI local de perfil fechado, com supervisor efêmero e recibos locais.

Não registra runner remoto, não executa comandos recebidos do usuário e não
publica checks GitHub. HMAC detecta alterações dos registros; não isola o dono
do host nem transforma uma execução local em validação científica externa.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid

import psutil

_CORE = Path(__file__).resolve().parents[1]
if str(_CORE) not in sys.path:
    sys.path.insert(0, str(_CORE))
# O supervisor também pode ser iniciado pelo caminho direto deste arquivo.
from scripts import validate_scientific_profile as _profile  # noqa: E402

_RUNNER = Path(_profile.__file__).resolve()
_RUNNER_SHA = hashlib.sha256(_RUNNER.read_bytes()).hexdigest()
_SELECTION = [{"name": name, "targets": list(targets)} for name, targets in _profile.PROFILE_GROUPS]
_MAX_SECONDS = len(_SELECTION) * (_profile.DEFAULT_GROUP_TIMEOUT + 5) + 30
_MAX_RSS = _profile.DEFAULT_MAX_RSS_BYTES
_ID = re.compile(r"lci-[0-9a-f]{32}\Z")
_REPLACE = os.replace
_SCOPE = "enumerated_scientific_regression_profile"
_TERMINAL = {"passed", "blocked", "cancelled"}


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def _sha(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("unsafe_artifact")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _no_links(path):
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("symlink_not_allowed")


def _json(path):
    _no_links(path)
    if not path.is_file() or path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("invalid_json_artifact")
    def invalid(value):
        raise ValueError("nonfinite_json:" + value)
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=invalid)


def _atomic(path, value):
    _no_links(path)
    descriptor, temporary = tempfile.mkstemp(prefix="record-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(_canonical(value) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        _REPLACE(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _same_process(pid, created):
    if type(pid) is not int or not isinstance(created, (int, float)) or isinstance(created, bool):
        return False
    try:
        process = psutil.Process(pid)
        return process.create_time() == created and process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


def _belongs(nodeid, target):
    if "::" not in target:
        return nodeid.split("::", 1)[0] == target
    return nodeid == target or nodeid.startswith((target + "[", target + "::"))


def _observe(process, observed):
    try:
        parent = psutil.Process(process.pid)
        for item in [parent, *parent.children(recursive=True)]:
            observed[(item.pid, item.create_time())] = item
    except psutil.NoSuchProcess:
        pass


def _rss(observed):
    total = 0
    for (pid, created), item in list(observed.items()):
        try:
            if _same_process(pid, created):
                total += item.memory_info().rss
        except psutil.NoSuchProcess:
            pass
    return total


def _cleanup(process, observed):
    """Inclui filhos em outras sessões e confere criação antes de sinalizar."""
    _observe(process, observed)
    for method in ("terminate", "kill"):
        for (pid, created), item in reversed(list(observed.items())):
            if _same_process(pid, created):
                try:
                    getattr(item, method)()
                except psutil.NoSuchProcess:
                    pass
        try:
            process.wait(timeout=0.5 if method == "terminate" else 2)
        except subprocess.TimeoutExpired:
            pass
        psutil.wait_procs(list(observed.values()), timeout=0.2)
    survivors = [pid for pid, created in observed if _same_process(pid, created)]
    return not survivors, survivors


class LocalCIService:
    """Raiz é configuração confiável do primário; start não recebe código/targets."""

    def __init__(self, repo_root=None, state_dir=None):
        raw_root = Path(repo_root) if repo_root is not None else _CORE
        _no_links(raw_root)
        self.root = raw_root.resolve()
        base = Path(os.environ.get("MCI_STATE_DIR", self.root / ".mci_state"))
        self.state_dir = Path(state_dir) if state_dir is not None else base / "local-ci"
        _no_links(self.state_dir)
        self.state_dir = self.state_dir.absolute()
        self._limits = {"timeout_seconds": _MAX_SECONDS, "max_rss_bytes": _MAX_RSS}

    @staticmethod
    def _validate_id(run_id):
        if type(run_id) is not str or not _ID.fullmatch(run_id):
            raise ValueError("invalid_run_id")
        return run_id

    def _folder(self, run_id):
        path = self.state_dir / "runs" / self._validate_id(run_id)
        _no_links(path)
        return path

    def _prepare(self):
        _no_links(self.state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        (self.state_dir / "runs").mkdir(exist_ok=True, mode=0o700)
        _no_links(self.state_dir / "runs")

    def _key(self, *, create=False):
        path = self.state_dir / "hmac.key"
        _no_links(path)
        if create:
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                pass
            else:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(os.urandom(32))
                    stream.flush()
                    os.fsync(stream.fileno())
        key = path.read_bytes()
        if len(key) != 32 or path.stat().st_mode & 0o077:
            raise ValueError("unsafe_private_key")
        return key

    def _save(self, path, payload):
        signature = hmac.new(self._key(), _canonical(payload), hashlib.sha256).hexdigest()
        _atomic(path, {"payload": payload, "hmac_sha256": signature})

    def _load(self, path):
        envelope = _json(path)
        payload = envelope["payload"]
        signature = hmac.new(self._key(), _canonical(payload), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, envelope["hmac_sha256"]):
            raise ValueError("metadata_signature_mismatch")
        return payload

    def _record(self, run_id):
        record = self._load(self._folder(run_id) / "record.json")
        if (record.get("kind") != "local_ci_run" or record.get("run_id") != run_id
                or record.get("root") != str(self.root) or record.get("profile") != "scientific"
                or record.get("status") not in {"queued", "running", *_TERMINAL}
                or type(record.get("created_ns")) is not int
                or not isinstance(record.get("selection"), list)):
            raise ValueError("invalid_run_record")
        limits = record["limits"]
        seconds, rss = limits["timeout_seconds"], limits["max_rss_bytes"]
        if (isinstance(seconds, bool) or not isinstance(seconds, (int, float))
                or not math.isfinite(seconds) or not 0 < seconds <= _MAX_SECONDS
                or type(rss) is not int or not 0 < rss <= _MAX_RSS):
            raise ValueError("invalid_run_limits")
        return record

    def _head(self):
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, capture_output=True,
                                text=True, check=True, timeout=10)
        head = result.stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{40,64}", head):
            raise ValueError("invalid_head")
        return head

    def _workspace(self):
        return self._head(), _profile.source_snapshot(self.root)["digest"]

    def _lock(self):
        if os.name != "posix":
            raise ValueError("local_ci_requires_posix_lock")
        import fcntl
        self._prepare()
        path = self.state_dir / "writer.lock"
        _no_links(path)
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(descriptor)
            return None
        return descriptor

    def start(self, profile="scientific"):
        if type(profile) is not str or profile != "scientific":
            raise ValueError("only_scientific_profile_is_allowed")
        descriptor = self._lock()
        if descriptor is None:
            return {"status": "busy", "reason_codes": ["single_writer_busy"], "profile": profile}
        try:
            self._key(create=True)
            runner = self.root / "scripts/validate_scientific_profile.py"
            _no_links(runner)
            if _sha(runner) != _RUNNER_SHA:
                raise ValueError("runner_is_not_current_canonical_R891")
            head, digest = self._workspace()
            run_id = "lci-" + uuid.uuid4().hex
            folder = self._folder(run_id)
            folder.mkdir(mode=0o700)
            record = {"kind": "local_ci_run", "run_id": run_id, "profile": profile,
                      "root": str(self.root), "status": "queued", "created_ns": time.time_ns(),
                      "head_start": head, "source_digest_start": digest, "selection": _SELECTION,
                      "selection_sha256": hashlib.sha256(_canonical(_SELECTION)).hexdigest(),
                      "runner_sha256": _RUNNER_SHA, "backend_sha256": _sha(Path(__file__).resolve()),
                      "limits": dict(self._limits), "reason_codes": [], "cleanup_complete": False}
            self._save(folder / "record.json", record)
            command = [sys.executable, str(Path(__file__).resolve()), "--_worker", run_id,
                       "--root", str(self.root), "--state", str(self.state_dir), "--lock-fd", str(descriptor)]
            with (folder / "supervisor.log").open("wb") as log:
                process = subprocess.Popen(command, cwd=self.root, stdin=subprocess.DEVNULL, stdout=log,
                                           stderr=subprocess.STDOUT, pass_fds=(descriptor,), start_new_session=True)
            record.update(supervisor_pid=process.pid, supervisor_create_time=psutil.Process(process.pid).create_time())
            self._save(folder / "record.json", record)
            return {"status": "queued", "run_id": run_id, "profile": profile, "run_dir": str(folder),
                    "scope": _SCOPE, "github_check_created": False, "external_validation": False}
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
            return {"status": "blocked", "profile": profile, "reason_codes": [str(exc)],
                    "github_check_created": False, "external_validation": False}
        finally:
            # Não chamar LOCK_UN: o mesmo open-file-description foi herdado.
            os.close(descriptor)

    def _compatibility(self, record, workspace):
        head, digest = workspace
        return {"sources_match": digest is not None and digest == record["source_digest_start"],
                "head_matches": head is not None and head == record["head_start"],
                "applicable": digest is not None and digest == record["source_digest_start"]
                and head is not None and head == record["head_start"]}

    def _artifact(self, folder, relative):
        if type(relative) is not str or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("artifact_path_escape")
        path = folder / relative
        _no_links(path)
        path.resolve().relative_to(folder.resolve())
        return path

    def _validate_output(self, record, end_ns, *, manifest=None):
        folder = self._folder(record["run_id"])
        if manifest is not None:
            for relative, expected in manifest.items():
                if _sha(self._artifact(folder, relative)) != expected:
                    raise ValueError("artifact_hash_mismatch")
        candidates = list((folder / "reports").glob("*/summary.json"))
        if len(candidates) != 1:
            raise ValueError("exactly_one_fresh_runner_summary_required")
        summary_path = candidates[0]
        _no_links(summary_path)
        summary = _json(summary_path)
        if (summary["status"] != "passed" or summary["root"] != str(self.root)
                or summary["scope"] != _SCOPE
                or summary["run_id"] != summary_path.parent.name
                or Path(summary["report_path"]) != summary_path
                or Path(summary["run_dir"]) != summary_path.parent
                or summary["profile_selection"] != record["selection"]
                or summary["global_suite_executed"] is not False
                or summary["external_scientific_validation"] is not False
                or summary["scientific_scale_validated"] is not False
                or summary["not_executed_groups"] != [] or summary["problems"] != []
                or summary["changed_sources"] != []
                or summary["source_before"]["digest"] != record["source_digest_start"]
                or summary["source_after"]["digest"] != record["source_digest_start"]):
            raise ValueError("runner_summary_contract_mismatch")
        if (summary["limits"]["group_timeout_seconds"] != _profile.DEFAULT_GROUP_TIMEOUT
                or summary["limits"]["max_rss_bytes"] != _profile.DEFAULT_MAX_RSS_BYTES):
            raise ValueError("runner_bounds_mismatch")
        if (type(summary["started_ns"]) is not int or type(summary["ended_ns"]) is not int
                or not record["created_ns"] <= summary["started_ns"] <= summary["ended_ns"] <= end_ns):
            raise ValueError("runner_summary_not_fresh")
        groups = summary["groups"]
        if len(groups) != len(record["selection"]):
            raise ValueError("incomplete_profile")
        paths = [summary_path]
        totals = dict.fromkeys(("total", "passed", "failed", "errors", "skipped"), 0)
        for index, (group, selection) in enumerate(zip(groups, record["selection"]), 1):
            target_dir = summary_path.parent / f"{index:02d}-{selection['name']}"
            expected = {"junit_path": target_dir / "junit.xml", "ledger_path": target_dir / "execution.json",
                        "log_path": target_dir / "pytest.log", "selection_path": target_dir / "selection.json"}
            if (group["name"] != selection["name"] or group["targets"] != selection["targets"]
                    or group["status"] != "passed" or group["problems"] != []
                    or type(group["exit_code"]) is not int or group["exit_code"] != 0
                    or type(group["started_ns"]) is not int or type(group["ended_ns"]) is not int
                    or not summary["started_ns"] <= group["started_ns"] <= group["ended_ns"] <= summary["ended_ns"]):
                raise ValueError("group_contract_mismatch")
            for name, path in expected.items():
                if Path(group[name]) != path:
                    raise ValueError("group_path_escape")
                _no_links(path)
                paths.append(path)
            selected = _json(expected["selection_path"])
            if selected["run_id"] != summary["run_id"] or selected["targets"] != selection["targets"]:
                raise ValueError("selection_mismatch")
            checked = _profile.validate_group_receipts(target_dir, summary["run_id"], group["started_ns"],
                                                       group["ended_ns"], group["exit_code"])
            if checked["status"] != "passed":
                raise ValueError("group_receipt_invalid")
            nodeids = checked["selected_nodeids"]
            if (any(not any(_belongs(nodeid, target) for target in selection["targets"]) for nodeid in nodeids)
                    or any(not any(_belongs(nodeid, target) for nodeid in nodeids) for target in selection["targets"])):
                raise ValueError("registered_target_scope_mismatch")
            for key in ("counts", "selected_nodeids", "executed_nodeids", "junit_sha256", "ledger_sha256"):
                if checked[key] != group[key]:
                    raise ValueError("group_receipt_mismatch")
            for name in ("log", "selection"):
                if _sha(expected[name + "_path"]) != group[name + "_sha256"]:
                    raise ValueError("group_artifact_hash_mismatch")
            result_path = target_dir / "result.json"
            if _json(result_path) != group:
                raise ValueError("group_result_mismatch")
            paths.append(result_path)
            for key, value in checked["counts"].items():
                if type(value) is not int or value < 0:
                    raise ValueError("invalid_count_type")
                totals[key] += value
        if (summary["totals"] != totals or any(type(value) is not int for value in summary["totals"].values())
                or totals["passed"] < 1):
            raise ValueError("totals_mismatch")
        artifacts = {str(path.relative_to(folder)): _sha(path) for path in paths}
        if manifest is not None and artifacts != manifest:
            raise ValueError("artifact_manifest_mismatch")
        return {"verified": True, "reason_codes": [], "report_path": str(summary_path),
                "totals": totals, "artifact_hashes": artifacts}

    def _view(self, run_id, workspace):
        folder = self._folder(run_id)
        if not folder.exists():
            return {"run_id": run_id, "status": "not_found"}
        try:
            record = self._record(run_id)
            result = {**record, "run_dir": str(folder), "record_path": str(folder / "record.json"),
                      "scope": _SCOPE, "github_check_created": False, "external_validation": False,
                      "recorded_status": record["status"], "current_compatibility": self._compatibility(record, workspace),
                      "receipt_validation": {"verified": False, "reason_codes": record["reason_codes"]}}
            if record["status"] == "passed":
                if (record["cleanup_complete"] is not True or type(record["exit_code"]) is not int
                        or record["exit_code"] != 0 or record["head_end"] != record["head_start"]
                        or record["source_digest_end"] != record["source_digest_start"]):
                    raise ValueError("successful_run_metadata_mismatch")
                result["receipt_validation"] = self._validate_output(record, record["finished_ns"], manifest=record["artifact_hashes"])
            elif record["status"] in {"queued", "running"}:
                if not _same_process(record.get("supervisor_pid"), record.get("supervisor_create_time")):
                    result.update(status="blocked", reason_codes=["supervisor_unavailable"], cleanup_complete=False)
            return result
        except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
            return {"run_id": run_id, "status": "blocked", "scope": _SCOPE,
                    "reason_codes": ["metadata_or_receipt_invalid", str(exc)],
                    "receipt_validation": {"verified": False, "reason_codes": [str(exc)]},
                    "current_compatibility": {"sources_match": False, "head_matches": False, "applicable": False},
                    "github_check_created": False, "external_validation": False}

    def _ids(self):
        directory = self.state_dir / "runs"
        _no_links(directory)
        if not directory.exists():
            return []
        return [p.name for p in sorted(directory.iterdir(), key=lambda p: p.stat().st_mtime_ns, reverse=True)
                if _ID.fullmatch(p.name)]

    def _current(self):
        try:
            return self._workspace()
        except (OSError, ValueError, subprocess.SubprocessError):
            return None, None

    def status(self, run_id=None):
        if run_id is None:
            ids = self._ids()
            if not ids:
                return {"status": "idle", "scope": _SCOPE, "github_check_created": False}
            run_id = ids[0]
        self._validate_id(run_id)
        return self._view(run_id, self._current())

    def runs(self, limit=20):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit_must_be_integer_between_1_and_100")
        ids = self._ids()[:limit]
        workspace = self._current() if ids else (None, None)
        return {"status": "available", "scope": _SCOPE, "runs": [self._view(run_id, workspace) for run_id in ids]}

    def cancel(self, run_id):
        self._validate_id(run_id)
        try:
            record = self._record(run_id)
        except FileNotFoundError:
            return {"status": "not_found", "run_id": run_id}
        if record["status"] in _TERMINAL:
            return {"status": "not_running", "run_id": run_id}
        self._save(self._folder(run_id) / "cancel.json", {"kind": "local_ci_cancel", "run_id": run_id,
                                                         "requested_ns": time.time_ns()})
        return {"status": "cancellation_requested", "run_id": run_id}

    def _cancel_requested(self, run_id):
        path = self._folder(run_id) / "cancel.json"
        if not path.exists():
            return False
        record = self._load(path)
        if record.get("kind") != "local_ci_cancel" or record.get("run_id") != run_id:
            raise ValueError("cancel_request_invalid")
        return True

    def _work(self, run_id, descriptor):
        folder = self._folder(run_id)
        record, process, observed = None, None, {}
        signalled = []
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda *_: signalled.append(True))
        try:
            import fcntl
            if os.fstat(descriptor).st_ino != (self.state_dir / "writer.lock").stat().st_ino:
                raise ValueError("writer_lock_mismatch")
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                record = self._record(run_id)
                if record.get("supervisor_pid") == os.getpid():
                    break
                time.sleep(0.01)
            else:
                raise ValueError("supervisor_handshake_missing")
            if (record["selection"] != _SELECTION or record["runner_sha256"] != _RUNNER_SHA
                    or _sha(self.root / "scripts/validate_scientific_profile.py") != _RUNNER_SHA
                    or record["backend_sha256"] != _sha(Path(__file__).resolve())
                    or self._workspace() != (record["head_start"], record["source_digest_start"])):
                raise ValueError("sources_changed_before_execution")
            record.update(status="running", started_ns=time.time_ns())
            self._save(folder / "record.json", record)
            (folder / "reports").mkdir()
            command = [sys.executable, str(self.root / "scripts/validate_scientific_profile.py"),
                       "--output", str(folder / "reports")]
            with (folder / "runner.log").open("wb") as log:
                process = subprocess.Popen(command, cwd=self.root, stdin=subprocess.DEVNULL, stdout=log,
                                           stderr=subprocess.STDOUT, env=_profile._environment(folder),
                                           pass_fds=(descriptor,), start_new_session=True)
            record.update(runner_pid=process.pid, runner_create_time=psutil.Process(process.pid).create_time())
            self._save(folder / "record.json", record)
            start, stop_reason, peak = time.monotonic(), None, 0
            while process.poll() is None:
                _observe(process, observed)
                rss = _rss(observed)
                peak = max(peak, rss)
                if signalled or self._cancel_requested(run_id):
                    stop_reason = "cancelled"
                elif time.monotonic() - start > record["limits"]["timeout_seconds"]:
                    stop_reason = "timeout"
                elif rss > record["limits"]["max_rss_bytes"]:
                    stop_reason = "memory_limit"
                if stop_reason:
                    break
                time.sleep(0.025)
            clean, survivors = _cleanup(process, observed)
            record.update(exit_code=process.poll(), peak_rss_bytes=peak, cleanup_complete=clean,
                          surviving_pids=survivors, finished_ns=time.time_ns())
            if not clean:
                raise ValueError("cleanup_incomplete")
            cancelled = bool(signalled) or self._cancel_requested(run_id)
            if stop_reason or cancelled:
                record.update(status="cancelled" if stop_reason == "cancelled" or cancelled else "blocked",
                              reason_codes=[stop_reason or "cancelled"])
            elif record["exit_code"] != 0:
                record.update(status="blocked", reason_codes=["runner_failed"])
            else:
                if self._workspace() != (record["head_start"], record["source_digest_start"]):
                    raise ValueError("sources_or_head_changed_during_execution")
                verified = self._validate_output(record, record["finished_ns"])
                record.update(status="passed", head_end=self._head(),
                              source_digest_end=record["source_digest_start"], **verified)
        except (OSError, ValueError, TypeError, KeyError, psutil.Error, subprocess.SubprocessError) as exc:
            if process is not None:
                clean, survivors = _cleanup(process, observed)
            else:
                clean, survivors = True, []
            if record is not None:
                record.update(status="blocked", reason_codes=[type(exc).__name__ + ":" + str(exc)],
                              cleanup_complete=clean, surviving_pids=survivors, finished_ns=time.time_ns())
        finally:
            if record is not None:
                self._save(folder / "record.json", record)
            os.close(descriptor)


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--_worker", required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--lock-fd", type=int, required=True)
    options = parser.parse_args()
    LocalCIService(options.root, options.state)._work(options._worker, options.lock_fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
