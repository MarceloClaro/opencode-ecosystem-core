"""R839: histórico RED→GREEN de processos pytest locais.

HMAC detecta alteração posterior de recibos. Não isola o dono do host nem
certifica a qualidade do oráculo. Nenhuma declaração recebida do agente emite
evidência: somente processos executados aqui podem entrar no histórico.
"""

from __future__ import annotations

import contextlib
import hashlib
import hmac
import json
import math
import os
import re
import signal
import stat
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

_ID = re.compile(r"tdd-[0-9a-f]{32}\Z")
_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "outputs",
    "output",
    ".state",
    ".cache",
    "vendor",
}
_LIMIT = 64 * 1024 * 1024
_SOURCE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".mjs",
    ".c",
    ".cpp",
    ".h",
    ".rs",
    ".go",
    ".lean",
}
_CONFIG_NAMES = {
    "pytest.ini",
    ".pytest.ini",
    "tox.ini",
    "pytest.toml",
    ".pytest.toml",
    "pyproject.toml",
    "setup.cfg",
    "opencode.json",
    "package.json",
    "tsconfig.json",
}


def _json_bytes(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha_file(path):
    if path.is_symlink() or path.stat().st_size > _LIMIT:
        raise ValueError("artifact_unsafe_or_oversized")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path):
    if path.stat().st_size > _LIMIT or path.is_symlink():
        raise ValueError("artifact_unsafe_or_oversized")
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class HistoryReceipt:
    receipt_id: str
    receipt_path: str | None
    phase: str
    accepted: bool
    status: str
    reason_codes: tuple[str, ...] = ()

    def to_dict(self):
        return {
            "receipt_id": self.receipt_id,
            "receipt_path": self.receipt_path,
            "phase": self.phase,
            "accepted": self.accepted,
            "status": self.status,
            "reason_codes": list(self.reason_codes),
        }


class TDDHistory:
    def __init__(self, root=None, state_dir=None):
        self.root = Path(root or Path(__file__).resolve().parent.parent).resolve()
        base = Path(os.environ.get("MCI_STATE_DIR", self.root / ".mci_state"))
        self.state_dir = Path(state_dir or base / "tdd-history").resolve()
        if any(part in {"outputs", "output"} for part in self.state_dir.parts):
            raise ValueError("private_history_must_be_outside_outputs")
        self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        (self.state_dir / "runs").mkdir(exist_ok=True, mode=0o700)
        key_path = self.state_dir / "hmac.key"
        if key_path.is_symlink():
            raise ValueError("unsafe_key_path")
        try:
            descriptor = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(os.urandom(32))
                stream.flush()
                os.fsync(stream.fileno())
        if os.name == "posix" and stat.S_IMODE(key_path.stat().st_mode) & 0o077:
            raise ValueError("unsafe_key_permissions")
        self._key = key_path.read_bytes()
        if len(self._key) != 32:
            raise ValueError("invalid_history_key")

    @contextlib.contextmanager
    def _lock(self):
        lock_path = self.state_dir / "ledger.lock"
        if lock_path.is_symlink():
            raise ValueError("unsafe_lock_path")
        with lock_path.open("a+b") as stream:
            if os.name == "posix":
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            else:
                import msvcrt

                if stream.tell() == 0:
                    stream.write(b"0")
                    stream.flush()
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                if os.name == "posix":
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
                else:
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)

    def _contained(self, root, relative):
        if (
            not isinstance(relative, str)
            or not relative
            or "\\" in relative
            or any(ord(c) < 32 for c in relative)
        ):
            raise ValueError("unsafe_path")
        parts = relative.split("/")
        if (
            any(part in {"", ".", ".."} for part in parts)
            or Path(relative).is_absolute()
        ):
            raise ValueError("unsafe_path")
        path = root / relative
        resolved = path.resolve()
        if resolved.relative_to(root).as_posix() != relative or path.is_symlink():
            raise ValueError("noncanonical_path")
        return resolved

    def _context(self, spec):
        if isinstance(spec, dict) or not callable(getattr(spec, "to_dict", None)):
            raise TypeError("specification_object_required")
        definition = dict(spec.to_dict())
        for mutable in ("status", "declared_status"):
            definition.pop(mutable, None)
        spec_id = definition.get("spec_id")
        if not isinstance(spec_id, str) or not spec_id.strip() or len(spec_id) > 256:
            raise ValueError("invalid_spec_id")
        scope_text = getattr(spec, "test_file", "")
        if not isinstance(scope_text, str) or not scope_text:
            raise ValueError("missing_test_file")
        if scope_text.rstrip("/") != "tests" and not scope_text.startswith("tests/"):
            raise ValueError("core_test_scope_must_be_tests")
        scope = self._contained(self.root, scope_text.rstrip("/"))
        if not scope.exists():
            raise ValueError("missing_test_file")
        mappings = getattr(spec, "criterion_test_targets", {}) or {}
        targets = (
            sorted({target for values in mappings.values() for target in values})
            if mappings
            else [scope_text.rstrip("/")]
        )
        files = {}
        for target in targets:
            if not isinstance(target, str) or any(ord(c) < 32 for c in target):
                raise ValueError("invalid_test_target")
            filename, *selectors = target.split("::")
            if any(not part or part.startswith("-") for part in selectors):
                raise ValueError("invalid_test_target")
            physical = self._contained(self.root, filename)
            if scope.is_file() and physical != scope:
                raise ValueError("target_outside_test_file")
            if scope.is_dir():
                physical.relative_to(scope)
            paths = sorted(physical.rglob("*.py")) if physical.is_dir() else [physical]
            if not paths or any(not path.is_file() for path in paths):
                raise ValueError("missing_test_target")
            for path in paths:
                relative = path.relative_to(self.root).as_posix()
                files[relative] = _sha_file(self._contained(self.root, relative))
        if not files:
            raise ValueError("empty_test_scope")
        # Dados do oráculo fazem parte da versão dos testes; alterar o valor
        # esperado de uma fixture não é correção da implementação.
        oracle_root = self.root / "tests"
        for path in sorted(oracle_root.rglob("*")):
            if path.is_file() and not any(
                part in _SKIP_DIRS for part in path.relative_to(oracle_root).parts
            ):
                relative = path.relative_to(self.root).as_posix()
                files[relative] = _sha_file(self._contained(self.root, relative))
        for name in (*_CONFIG_NAMES, "conftest.py"):
            path = self.root / name
            if path.is_file():
                files[name] = _sha_file(self._contained(self.root, name))
        if (
            len(files) > 20000
            or sum((self.root / name).stat().st_size for name in files) > _LIMIT
        ):
            raise ValueError("test_manifest_limit")
        markdown = {}
        for path in sorted((self.root / "specs").glob(spec_id + "*.md")):
            if path.stem != spec_id and not path.stem.startswith(spec_id + "-"):
                continue
            relative = path.relative_to(self.root).as_posix()
            raw = self._contained(self.root, relative).read_text(encoding="utf-8")
            match = re.match(r"\A---\s*\n(.*?)\n---", raw, re.DOTALL)
            if match:
                front = re.sub(r"(?m)^status:.*$", "status: <mutable>", match.group(1))
                raw = "---\n" + front + "\n---" + raw[match.end() :]
            markdown[relative] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        snapshot = {"definition": definition, "markdown_sources": markdown}
        return {
            "spec_id": spec_id,
            "spec_fingerprint": hashlib.sha256(_json_bytes(snapshot)).hexdigest(),
            "spec_snapshot": snapshot,
            "targets": targets,
            "test_hashes": files,
        }

    def _sources(self):
        files = {}
        for directory, dirs, names in os.walk(self.root, followlinks=False):
            dirs[:] = sorted(
                name
                for name in dirs
                if name not in _SKIP_DIRS
                and not (Path(directory) / name)
                .resolve()
                .is_relative_to(self.state_dir)
            )
            for name in sorted(names):
                if not (Path(name).suffix in _SOURCE_SUFFIXES or name in _CONFIG_NAMES):
                    continue
                path = Path(directory) / name
                if path.is_symlink():
                    raise ValueError("source_symlink_not_attested")
                files[path.relative_to(self.root).as_posix()] = _sha_file(path)
                if len(files) > 20000:
                    raise ValueError("source_manifest_limit")
        try:
            revision = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            git_head = revision.stdout.strip() if revision.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            git_head = None
        return {"git_head": git_head, "files": files}

    def _signature(self, digest):
        return hmac.new(self._key, digest.encode("ascii"), hashlib.sha256).hexdigest()

    def _ledger(self, check_artifacts=True):
        path = self.state_dir / "ledger.jsonl"
        if not path.exists():
            return []
        if path.is_symlink() or path.stat().st_size > _LIMIT:
            raise ValueError("unsafe_ledger")
        records, previous = [], "0" * 64
        for sequence, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            entry = json.loads(line)
            identifier = entry.get("receipt_id", "")
            if not isinstance(identifier, str) or not _ID.fullmatch(identifier):
                raise ValueError("invalid_receipt_id")
            receipt_path = self._contained(
                self.state_dir, f"runs/{identifier}/receipt.json"
            )
            if _sha_file(receipt_path) != entry.get("receipt_file_sha256"):
                raise ValueError("receipt_file_tampered")
            envelope = _read_json(receipt_path)
            payload = envelope["payload"]
            digest = hashlib.sha256(_json_bytes(payload)).hexdigest()
            signature = self._signature(digest)
            if (
                envelope.get("receipt_hash") != digest
                or entry.get("receipt_hash") != digest
                or not hmac.compare_digest(
                    str(envelope.get("signature", "")), signature
                )
                or not hmac.compare_digest(str(entry.get("signature", "")), signature)
            ):
                raise ValueError("receipt_signature_invalid")
            if (
                payload.get("sequence") != sequence
                or payload.get("previous_receipt_hash") != previous
                or payload.get("receipt_id") != identifier
                or payload.get("root") != str(self.root)
            ):
                raise ValueError("history_chain_invalid")
            if check_artifacts:
                for relative, expected in payload["artifacts"].items():
                    artifact = self._contained(receipt_path.parent, relative)
                    if _sha_file(artifact) != expected:
                        raise ValueError("history_artifact_tampered")
            records.append(payload)
            previous = digest
        return records

    def _analyse(self, folder, phase, returncode, timed_out):
        reasons = []
        counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "passed": 0}
        try:
            if (folder / "junit.xml").stat().st_size > _LIMIT:
                raise ValueError("junit_limit")
            xml = ET.parse(folder / "junit.xml").getroot()
            cases = list(xml.iter("testcase"))
            counts["tests"] = len(cases)
            for case in cases:
                outcome = (
                    "errors"
                    if case.find("error") is not None
                    else "failures"
                    if case.find("failure") is not None
                    else "skipped"
                    if case.find("skipped") is not None
                    else "passed"
                )
                counts[outcome] += 1
            reports = [
                json.loads(line)
                for line in (folder / "reports.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            collected = _read_json(folder / "collected.json")["nodeids"]
            calls = [report for report in reports if report["when"] == "call"]
            targets = _read_json(folder / "targets.json")

            def belongs(nodeid, target):
                filename = target.split("::", 1)[0]
                if (self.root / filename).is_dir():
                    return nodeid.split("::", 1)[0].startswith(
                        filename.rstrip("/") + "/"
                    )
                return nodeid == target or nodeid.startswith(
                    (target + "::", target + "[")
                )

            if not targets or any(
                not any(belongs(nodeid, target) for target in targets)
                for nodeid in collected
            ):
                reasons.append("execution_outside_registered_targets")
            if any(
                not any(belongs(nodeid, target) for nodeid in collected)
                for target in targets
            ):
                reasons.append("registered_target_not_executed")
            if sorted(report["nodeid"] for report in calls) != sorted(collected):
                reasons.append("execution_nodeids_mismatch")
            if len(calls) != len(cases) or len(collected) != len(cases):
                reasons.append("incomplete_execution_records")
            if (
                any(report["skipped"] or report["xfail"] for report in reports)
                or counts["skipped"]
            ):
                reasons.append("skipped_or_xfail")
            if counts["errors"] or any(
                report["failed"] and report["when"] != "call" for report in reports
            ):
                reasons.append("collection_setup_or_teardown_error")
            assertions = sum(
                report["failed"] and report["assertion"] for report in calls
            )
            if phase == "red":
                if (
                    returncode != 1
                    or assertions < 1
                    or assertions != counts["failures"]
                ):
                    reasons.append("red_assertion_failure_required")
            elif returncode != 0 or counts["passed"] < 1 or counts["failures"]:
                reasons.append("green_success_required")
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError):
            collected = []
            reasons.append("invalid_execution_artifacts")
        if timed_out:
            reasons.append("pytest_timeout")
        if not counts["tests"]:
            reasons.append("zero_tests")
        return not reasons, reasons, counts, sorted(collected)

    def _result(self, verified=False, reasons=(), red=None, green=None):
        return {
            "verified": verified,
            "reason_codes": list(reasons),
            "reasons": list(reasons),
            "red_receipt_id": red,
            "green_receipt_id": green,
            "verification": "local_executed_history",
            "externally_validated": False,
        }

    def _matches(self, payload, context):
        return all(
            payload.get(key) == context[key]
            for key in ("spec_id", "spec_fingerprint", "targets", "test_hashes")
        )

    def _valid_execution(self, payload):
        folder = self.state_dir / "runs" / payload["receipt_id"]
        valid, _, counts, collected = self._analyse(
            folder, payload["phase"], payload["returncode"], payload["timed_out"]
        )
        before, after = (
            _read_json(folder / "source-before.json"),
            _read_json(folder / "source-after.json"),
        )
        return (
            valid
            and before == after
            and counts == payload["counts"]
            and collected == payload["collected_nodeids"]
            and payload["accepted"] is True
        )

    def preflight(self, spec):
        try:
            context = self._context(spec)
            with self._lock():
                records = self._ledger()
            for record in reversed(records):
                if (
                    record["phase"] == "red"
                    and self._matches(record, context)
                    and self._valid_execution(record)
                ):
                    if record["finished_at_ns"] > time.time_ns():
                        return self._result(reasons=["red_timestamp_in_future"])
                    return self._result(True, red=record["receipt_id"])
            return self._result(reasons=["executed_red_history_missing"])
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return self._result(reasons=["history_invalid", str(exc)])

    def validate_pair(self, spec, green_receipt):
        identifier = (
            green_receipt.receipt_id
            if isinstance(green_receipt, HistoryReceipt)
            else green_receipt
        )
        if not isinstance(identifier, str) or not _ID.fullmatch(identifier):
            return self._result(reasons=["issued_receipt_reference_required"])
        try:
            context = self._context(spec)
            with self._lock():
                records = self._ledger()
            indexed = {record["receipt_id"]: record for record in records}
            green = indexed.get(identifier)
            if (
                green is None
                or green["phase"] != "green"
                or not self._matches(green, context)
            ):
                return self._result(
                    reasons=["green_contract_mismatch"], green=identifier
                )
            red = indexed.get(green.get("paired_red_receipt_id"))
            if red is None or red["phase"] != "red" or not self._matches(red, context):
                return self._result(
                    reasons=["red_pair_missing_or_mismatched"], green=identifier
                )
            if not self._valid_execution(red) or not self._valid_execution(green):
                return self._result(
                    reasons=["invalid_executed_pair"],
                    red=red["receipt_id"],
                    green=identifier,
                )
            if (
                red["finished_at_ns"] > green["started_at_ns"]
                or red["sequence"] >= green["sequence"]
                or red["collected_nodeids"] != green["collected_nodeids"]
            ):
                return self._result(
                    reasons=["red_green_order_or_tests_mismatch"],
                    red=red["receipt_id"],
                    green=identifier,
                )
            green_sources = _read_json(
                self.state_dir / "runs" / identifier / "source-after.json"
            )
            if self._sources() != green_sources:
                return self._result(
                    reasons=["current_sources_differ_from_green"],
                    red=red["receipt_id"],
                    green=identifier,
                )
            return self._result(True, red=red["receipt_id"], green=identifier)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return self._result(reasons=["history_invalid", str(exc)], green=identifier)

    def _write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
        with temporary.open("xb") as stream:
            stream.write(_json_bytes(value) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def run(self, spec, phase="red", timeout_seconds=1200):
        if phase not in {"red", "green"}:
            raise ValueError("phase_must_be_red_or_green")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
        ):
            raise ValueError("positive_finite_timeout_required")
        identifier = "tdd-" + uuid.uuid4().hex
        folder = self.state_dir / "runs" / identifier
        reasons = []
        try:
            context = self._context(spec)
            preflight = self.preflight(spec) if phase == "green" else None
            folder.mkdir(mode=0o700)
            self._write_json(folder / "spec.json", context["spec_snapshot"])
            self._write_json(folder / "test-manifest.json", context["test_hashes"])
            self._write_json(folder / "targets.json", context["targets"])
            for relative in context["test_hashes"]:
                destination = folder / "test-bytes" / relative
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                destination.write_bytes(
                    self._contained(self.root, relative).read_bytes()
                )
            source_before = self._sources()
            self._write_json(folder / "source-before.json", source_before)
            (folder / "reports.jsonl").write_text("", encoding="utf-8")
            self._write_json(folder / "collected.json", {"nodeids": []})
            plugin_name = "_tdd_probe_" + identifier.replace("-", "_")
            plugin = folder / (plugin_name + ".py")
            plugin.write_text(
                "import json, pytest\nfrom pathlib import Path\n"
                f"REPORTS=Path({str(folder / 'reports.jsonl')!r})\nCOLLECTED=Path({str(folder / 'collected.json')!r})\n"
                "def _save(item):\n    with REPORTS.open('a', encoding='utf-8') as stream:\n        stream.write(json.dumps(item)+'\\n')\n"
                "@pytest.hookimpl(hookwrapper=True)\ndef pytest_runtest_makereport(item, call):\n"
                "    outcome=yield\n    report=outcome.get_result()\n"
                "    _save({'nodeid':report.nodeid,'when':report.when,'failed':report.failed,'passed':report.passed,'skipped':report.skipped,"
                "'xfail':hasattr(report,'wasxfail'),'assertion':bool(call.excinfo is not None and isinstance(call.excinfo.value,AssertionError))})\n"
                "def pytest_collectreport(report):\n    if report.failed:\n        _save({'nodeid':report.nodeid,'when':'collect','failed':True,'passed':False,'skipped':False,'xfail':False,'assertion':False})\n"
                "def pytest_collection_finish(session):\n    COLLECTED.write_text(json.dumps({'nodeids':[item.nodeid for item in session.items]}),encoding='utf-8')\n",
                encoding="utf-8",
            )
            command = [
                sys.executable,
                "-B",
                "-X",
                f"pycache_prefix={folder / 'bytecode'}",
                "-m",
                "pytest",
                f"--confcutdir={self.root}",
                "-p",
                plugin_name,
                "-q",
                "--tb=short",
                f"--junitxml={folder / 'junit.xml'}",
                "-o",
                "junit_family=xunit2",
                "-o",
                "addopts=",
                "-o",
                f"cache_dir={folder / 'pytest-cache'}",
                "--",
                *context["targets"],
            ]
            environment = dict(os.environ)
            environment["PYTHONPATH"] = os.pathsep.join(
                [str(folder), str(self.root), environment.get("PYTHONPATH", "")]
            )
            environment["PYTEST_ADDOPTS"] = ""
            environment["PYTEST_PLUGINS"] = ""
            started = time.time_ns()
            timed_out = False
            with (folder / "raw.log").open("wb") as log:
                process = subprocess.Popen(
                    command,
                    cwd=self.root,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=os.name == "posix",
                )
                try:
                    returncode = process.wait(timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    if os.name == "posix":
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                    else:
                        process.terminate()
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        if os.name == "posix":
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        else:
                            process.kill()
                        process.wait(timeout=5)
                    returncode = process.returncode
                finally:
                    # O grupo pertence exclusivamente à fase; descendentes
                    # também são encerrados quando pytest já terminou.
                    from integrations.harness_runtime import HarnessRuntime

                    HarnessRuntime._stop_process_tree(process)
                    process.wait(timeout=5)
            finished = time.time_ns()
            source_after = self._sources()
            self._write_json(folder / "source-after.json", source_after)
            phase_valid, phase_reasons, counts, collected = self._analyse(
                folder, phase, returncode, timed_out
            )
            reasons.extend(phase_reasons)
            if source_before != source_after:
                reasons.append("sources_changed_during_execution")
            if self._context(spec) != context:
                reasons.append("test_or_spec_changed_during_execution")
            if phase == "green" and not preflight["verified"]:
                reasons.append("executed_red_history_missing")
            accepted = phase_valid and not reasons
            payload = {
                "schema": "tdd-history-v1",
                "root": str(self.root),
                "receipt_id": identifier,
                "phase": phase,
                "spec_id": context["spec_id"],
                "spec_fingerprint": context["spec_fingerprint"],
                "targets": context["targets"],
                "test_hashes": context["test_hashes"],
                "started_at_ns": started,
                "finished_at_ns": finished,
                "returncode": returncode,
                "timed_out": timed_out,
                "counts": counts,
                "collected_nodeids": collected,
                "accepted": accepted,
                "reason_codes": reasons,
                "paired_red_receipt_id": preflight["red_receipt_id"]
                if preflight
                else None,
                "artifacts": {
                    path.relative_to(folder).as_posix(): _sha_file(path)
                    for path in sorted(folder.rglob("*"))
                    if path.is_file()
                    and "pytest-cache" not in path.parts
                    and "bytecode" not in path.parts
                },
                "verification": "local_executed_history",
                "externally_validated": False,
            }
            with self._lock():
                records = self._ledger()
                ledger_path = self.state_dir / "ledger.jsonl"
                previous = "0" * 64
                if records:
                    last = self._contained(
                        self.state_dir, f"runs/{records[-1]['receipt_id']}/receipt.json"
                    )
                    previous = _read_json(last)["receipt_hash"]
                payload.update(
                    sequence=len(records) + 1, previous_receipt_hash=previous
                )
                digest = hashlib.sha256(_json_bytes(payload)).hexdigest()
                signature = self._signature(digest)
                receipt_path = folder / "receipt.json"
                self._write_json(
                    receipt_path,
                    {
                        "payload": payload,
                        "receipt_hash": digest,
                        "signature": signature,
                    },
                )
                entry = {
                    "receipt_id": identifier,
                    "receipt_hash": digest,
                    "signature": signature,
                    "receipt_file_sha256": _sha_file(receipt_path),
                }
                with ledger_path.open("ab") as ledger:
                    ledger.write(_json_bytes(entry) + b"\n")
                    ledger.flush()
                    os.fsync(ledger.fileno())
            return HistoryReceipt(
                identifier,
                str(receipt_path),
                phase,
                accepted,
                "recorded_" + phase if accepted else "rejected",
                tuple(reasons),
            )
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            subprocess.SubprocessError,
        ) as exc:
            return HistoryReceipt(
                identifier,
                None,
                phase,
                False,
                "rejected",
                ("history_execution_or_persistence_error", str(exc)),
            )


TDDHistoryReceipt = HistoryReceipt
