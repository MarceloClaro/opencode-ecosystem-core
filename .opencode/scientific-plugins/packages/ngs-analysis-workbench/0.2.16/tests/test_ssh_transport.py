from __future__ import annotations

import hashlib
import itertools
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

MCP_ROOT = Path(__file__).resolve().parents[1] / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from daemon_test_case import DaemonTestCase  # noqa: E402
from ngs_workbench_daemon import (  # noqa: E402
    client,
    inspection,
    remote_controller,
    remote_operations,
    remote_probe,
    runs,
    server,
    ssh,
)
from ngs_workbench_daemon.persistence import (  # noqa: E402
    SqlAlchemyUnitOfWork,
    default_database,
    ensure_workspace_identity,
)
from ngs_workbench_daemon.protocol import (  # noqa: E402
    ExecutionRequest,
    TargetInspection,
    canonical_plan_checksum,
)
from ngs_workbench_daemon.state import daemon_directory, daemon_token  # noqa: E402
from ngs_workbench_execution_monitoring import DEFAULT_OBSERVER_REGISTRY  # noqa: E402
from ngs_workbench_mcp import runs as mcp_runs  # noqa: E402
from test_run_persistence import new_run  # noqa: E402


class ControllerLogTests(DaemonTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.server = server.DaemonServer(daemon_token(daemon_directory(), create=True), "test")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.thread.join, 2)
        self.addCleanup(self.server.shutdown)
        endpoint = client.DaemonEndpoint("127.0.0.1", self.server.server_port, "test", "test")
        self.enterContext(mock.patch.object(client, "ensure_daemon_running", return_value=endpoint))
        self.enterContext(mock.patch.object(client, "healthy_daemon", return_value=endpoint))
        self.access = {"alias": "approved-test-host"}
        self.enterContext(mock.patch.object(ssh, "effective_access", return_value=self.access))
        local_python = subprocess.run
        local_process = subprocess.Popen
        self.stream_transport = self.enterContext(
            mock.patch.object(
                ssh.subprocess,
                "Popen",
                side_effect=lambda argv, **options: local_process([sys.executable, "-"], **options),
            )
        )
        # Run the actual uploaded program in a subprocess, substituting only SSH transport.
        self.transport = self.enterContext(
            mock.patch.object(
                ssh.subprocess,
                "run",
                side_effect=lambda argv, **options: local_python([sys.executable, "-"], **options),
            )
        )

    def _register(self, binding="nextflow", target="lab", status="completed", warnings=()):
        workspace_id = ensure_workspace_identity(self.workspace)
        candidate = new_run(self.workspace, workspace_id, f"{binding}-{target}-{status}", binding)
        local = self.workspace / candidate.run_relative_path
        remote = self.root / "remote" / candidate.external_run_id
        log_name = f"logs/{binding}.log"
        plan = {
            "command_argv": ["nextflow", "-with-trace", str(remote / "workflow/trace.txt")],
            "readiness": {},
            "warnings": list(warnings),
            "effects": {"run_dir": str(local), "launch_log": str(local / log_name)},
            "request": {
                "target": {"target_id": target},
                "remote": {
                    "run_dir": str(remote),
                    "workspace_root": str(self.root),
                    "host_access": self.access,
                },
            },
        }
        checksum = canonical_plan_checksum(plan)
        audit = self.workspace / candidate.approved_plan_relative_path
        audit.parent.mkdir(parents=True)
        audit.write_text(json.dumps({**plan, "plan_checksum": checksum}))
        candidate = replace(
            candidate,
            plan_checksum=checksum,
            request={
                "daemon_instance_id": "test",
                "target": {"target_id": target},
                "plan_request": plan["request"],
            },
            launch_log_relative_path=f"{candidate.run_relative_path}/{log_name}",
        )
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as uow:
            uow.registry.register_workspace(workspace_id, self.workspace)
            record = uow.registry.allocate_approved_run(candidate)
            record = uow.registry.transition_run(
                record.id, "running", expected_revision=record.revision
            )
            if status == "canceled":
                for state in ("cancel_requested", "canceling"):
                    record = uow.registry.transition_run(
                        record.id, state, expected_revision=record.revision
                    )
            if status != "running":
                record = uow.registry.transition_run(
                    record.id, status, expected_revision=record.revision
                )
            uow.commit()
        log = (local if target == "local" else remote) / log_name
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("old output\n" * 2000 + "final controller output\n")
        if status == "running":
            self.server.runs._runs[record.id] = runs.OwnedRun(
                request=ExecutionRequest(binding=binding, plan_checksum=checksum, plan=plan),
                registry_run_id=record.id,
                remote_identity={"pid": 123},
            )
        return record, log

    def test_remote_detail_uses_one_shared_parser_and_list_reads_no_evidence(self) -> None:
        fixtures = Path(__file__).parent / "fixtures/execution_observation"
        manifest = json.loads((fixtures / "fixture_manifest.json").read_text())
        for binding, target in itertools.product(("nextflow", "snakemake"), ("local", "lab")):
            with self.subTest(binding=binding, target=target):
                record, log = self._register(
                    binding=binding, target=target, status="running", warnings=["Plan warning"]
                )
                root = log.parent.parent
                evidence = root / "workflow/trace.txt"
                if binding == "snakemake":
                    evidence = root / "results/.snakemake/log/run.snakemake.log"
                evidence.parent.mkdir(parents=True, exist_ok=True)
                evidence.write_bytes((fixtures / manifest[binding]["fixture_path"]).read_bytes())
                if binding == "snakemake":
                    older = evidence.with_name("older.snakemake.log")
                    older.write_text("old native log\n")
                    os.utime(older, ns=(1, 1))
                observer = DEFAULT_OBSERVER_REGISTRY.observers[binding]
                with evidence.open() as lines:
                    expected = observer.observe_lines(
                        lines, evidence_path=str(evidence), workflow_status="running"
                    ).model_dump(mode="json")
                with mock.patch.object(
                    observer, "observe_lines", wraps=observer.observe_lines
                ) as parse:
                    observation = mcp_runs.observe_registry_run(record.id)
                    self.assertEqual(observation["execution"], expected)
                    self.assertEqual(observation["warnings"], [])
                    self.assertEqual(observation["log_tail"], log.read_bytes()[-12_000:].decode())
                    self.assertEqual(
                        mcp_runs.get_registry_run(record.id)["warnings"], ["Plan warning"]
                    )
                    parse.assert_called_once()
                    parse.reset_mock()
                    self.stream_transport.reset_mock()
                    mcp_runs.list_registry_runs()
                    parse.assert_not_called()
                    self.stream_transport.assert_not_called()
                log.unlink()
                observation = mcp_runs.observe_registry_run(record.id)
                self.assertEqual(len(observation["warnings"]), 1)
                self.assertEqual(observation["execution"], expected)
                if target == "lab":
                    self.assertFalse((Path(record.run_dir) / "results").exists())
                    self.assertFalse(Path(record.launch_log_path).exists())

    def test_run_detail_never_observes_the_daemon_or_ssh(self) -> None:
        for status in ("running", "completed"):
            with self.subTest(status=status):
                record, _ = self._register(status=status)
                with (
                    mock.patch.object(
                        mcp_runs.daemon_client,
                        "observe",
                        side_effect=AssertionError("detail observed lifecycle"),
                    ),
                    mock.patch.object(
                        mcp_runs.daemon_client,
                        "observe_execution",
                        side_effect=AssertionError("detail observed evidence"),
                    ),
                    mock.patch.object(
                        mcp_runs.daemon_client,
                        "ensure_daemon_running",
                        side_effect=AssertionError("detail started daemon"),
                    ),
                ):
                    detail = mcp_runs.get_registry_run(record.id)
                self.assertEqual(detail["status"], status)
                self.transport.assert_not_called()

    def test_remote_completed_report_is_not_projected_or_read_over_ssh(self) -> None:
        record, _ = self._register(status="completed")
        report = mcp_runs.get_registry_run_report(record.id)
        self.assertEqual(report["availability"], "remote_results_not_projected")
        self.assertIsNone(report["report"])
        self.transport.assert_not_called()

    def test_remote_trace_counts_are_complete_and_independent_of_controller_log(self) -> None:
        record, log = self._register(warnings=["Plan warning"])
        trace = log.parent.parent / "workflow/trace.txt"
        trace.parent.mkdir()
        trace.write_text(
            "task_id\tname\tstatus\n" + "".join(f"{index}\tqc\tCOMPLETED\n" for index in range(240))
        )
        log.unlink()
        observation = mcp_runs.observe_registry_run(record.id)
        self.assertEqual(len(observation["warnings"]), 1)
        self.assertEqual(mcp_runs.get_registry_run(record.id)["warnings"], ["Plan warning"])
        self.assertEqual(observation["execution"]["counts"]["completed"], 240)
        self.assertEqual(len(observation["execution"]["attempts"]), 200)
        self.assertTrue(observation["execution"]["attempts_truncated"])
        trace.unlink()
        log.write_text("controller still readable\n")
        observation = mcp_runs.observe_registry_run(record.id)
        self.assertEqual(observation["log_tail"], log.read_text())
        self.assertEqual(len(observation["warnings"]), 1)
        self.assertFalse(observation["execution"]["evidence"]["available"])

    def test_large_remote_results_complete_without_copyback(self) -> None:
        for binding in ("nextflow", "snakemake"):
            with self.subTest(binding=binding):
                record, log = self._register(binding=binding, status="running")
                root = log.parent.parent
                result = root / "results" / "large.bin"
                result.parent.mkdir()
                with result.open("wb") as handle:
                    handle.truncate(65 * 1024 * 1024)
                evidence = root / (
                    "workflow/trace.txt"
                    if binding == "nextflow"
                    else "results/.snakemake/log/run.snakemake.log"
                )
                evidence.parent.mkdir(parents=True, exist_ok=True)
                evidence.write_text(
                    "name\tstatus\nqc\tCOMPLETED\n"
                    if binding == "nextflow"
                    else "Finished jobid: 1 (Rule: qc)\n"
                )
                owned = self.server.runs._runs.pop(record.id)
                with (
                    mock.patch.object(
                        ssh,
                        "status",
                        side_effect=[
                            ssh.TransportError("offline"),
                            {"running": False, "return_code": 0},
                        ],
                    ),
                    mock.patch.object(runs.time, "sleep"),
                ):
                    self.server.runs._finish_remote(owned)
                detail = mcp_runs.get_registry_run(record.id)
                observation = mcp_runs.observe_registry_run(record.id)
                self.assertEqual(detail["status"], "completed")
                self.assertEqual(detail["run_dir"], str(root))
                self.assertEqual(observation["execution"]["evidence"]["path"], str(evidence))
                self.assertEqual(observation["execution"]["counts"]["completed"], 1)
                self.assertEqual(observation["log_tail"], log.read_bytes()[-12_000:].decode())
                self.assertFalse((Path(record.run_dir) / "results").exists())
                self.assertFalse(Path(record.launch_log_path).exists())
                self.assertEqual(result.stat().st_size, 65 * 1024 * 1024)
                local = Path(record.run_dir)
                (local / "results").mkdir()
                (local / "results/stale.txt").write_text("obsolete copied result")
                historical = mcp_runs.get_registry_run(record.id)
                self.assertNotIn("result", historical)
                self.assertNotIn("artifacts", historical)
                summary = next(
                    item
                    for item in mcp_runs.list_registry_runs()["runs"]
                    if item["registry_run_id"] == record.id
                )
                self.assertEqual(summary["run_dir"], str(root))
                self.assertEqual(mcp_runs.cancel_registry_run(record.id)["run_dir"], str(root))
                Path(record.approved_plan_path).unlink()
                unavailable = mcp_runs.get_registry_run(record.id)
                self.assertEqual(unavailable["run_dir"], str(root))
                self.assertNotIn("config_hash", unavailable["target"])
                self.assertTrue(unavailable["warnings"])
                self.assertEqual(unavailable["status"], "completed")

    def test_stream_validates_completion_and_reaps_on_abort(self) -> None:
        record, log = self._register()
        log.write_text("first line\n" + "remaining output\n" * 65_536)
        remote = runs._approved_plan(record)["request"]["remote"]
        original = self.stream_transport.side_effect
        processes = []

        def track(*args, **kwargs):
            process = original(*args, **kwargs)
            processes.append(process)
            return process

        with mock.patch.object(ssh.subprocess, "Popen", side_effect=track):
            for read_all in (False, True):
                with self.subTest(read_all=read_all):
                    with ssh.stream_file(remote, "logs/nextflow.log") as lines:
                        self.assertEqual(
                            lines.read() if read_all else next(lines),
                            log.read_text() if read_all else "first line\n",
                        )
                    self.assertEqual(processes[-1].returncode, 0)
            for failure, read_all in (
                ("consumer_error", False),
                ("deadline", False),
                ("failed_exit", False),
                ("deadline", True),
                ("failed_exit", True),
            ):
                program = (
                    "import json, sys, time\n"
                    "def execute(request, controller):\n"
                    "    sys.stdout.write('first line\\n'); sys.stdout.flush()\n"
                    + ("    sys.exit(7)\n" if failure == "failed_exit" else "    time.sleep(30)\n")
                )
                with (
                    self.subTest(failure=failure, read_all=read_all),
                    mock.patch.object(ssh, "_REMOTE_PROGRAM", program),
                ):
                    if failure == "consumer_error":
                        error = RuntimeError("parser stopped")
                        with self.assertRaises(RuntimeError) as raised:
                            with ssh.stream_file(remote, "logs/nextflow.log") as lines:
                                self.assertEqual(next(lines), "first line\n")
                                raise error
                        self.assertIs(raised.exception, error)
                    else:
                        with self.assertRaises(ssh.TransportError):
                            with ssh.stream_file(remote, "logs/nextflow.log", timeout=0.5) as lines:
                                if read_all:
                                    lines.read()
                                else:
                                    self.assertEqual(next(lines), "first line\n")
                self.assertIsNotNone(processes[-1].poll())

    def test_malformed_snakemake_evidence_preserves_controller_diagnostics(self) -> None:
        for target in ("local", "lab"):
            record, log = self._register(binding="snakemake", target=target)
            log.write_bytes(b"non-UTF8 tool output: \xff\nuseful final diagnostic\n")
            native = log.parent.parent / "results/.snakemake/log/run.snakemake.log"
            native.parent.mkdir(parents=True)
            for content in (b"\xff\n", b"9" * 5000 + b" of 1 steps done\n"):
                with self.subTest(target=target, content=content[:10]):
                    native.write_bytes(content)
                    detail = mcp_runs.observe_registry_run(record.id)
                    self.assertEqual(detail["log_tail"], log.read_bytes().decode(errors="replace"))
                    self.assertEqual(len(detail["warnings"]), 1)
                    self.assertIn("Execution evidence unavailable", detail["warnings"][0])
                    self.assertFalse(detail["execution"]["evidence"]["available"])

    def test_remote_only_controller_log_reaches_run_detail_without_copyback(self) -> None:
        for binding in ("nextflow", "snakemake"):
            for status in ("running", "completed", "failed", "canceled", "orphaned"):
                with self.subTest(binding=binding, status=status):
                    record, log = self._register(binding=binding, status=status)
                    detail = mcp_runs.observe_registry_run(record.id)
                    self.assertEqual(detail["log_tail"], log.read_bytes()[-12_000:].decode())
                    self.assertEqual(
                        (detail["status"], detail["revision"]), (status, record.revision)
                    )
                    self.assertFalse(Path(record.launch_log_path).exists())
                    self.assertFalse(detail["execution"]["evidence"]["available"])
        self.transport.reset_mock()
        mcp_runs.list_registry_runs(statuses=["completed"])
        self.transport.assert_not_called()

    def test_local_controller_log_remains_readable_without_its_approved_plan(self) -> None:
        record, log = self._register(target="local")
        Path(record.approved_plan_path).unlink()
        detail = mcp_runs.observe_registry_run(record.id)
        self.assertEqual(detail["log_tail"], log.read_bytes()[-12_000:].decode())
        self.transport.assert_not_called()

    def test_evidence_errors_preserve_lifecycle_and_never_fall_back_to_stale_local_logs(
        self,
    ) -> None:
        record, log = self._register()
        local = Path(record.launch_log_path)
        local.parent.mkdir(parents=True)
        local.write_text("stale collected log")
        audit = Path(record.approved_plan_path)
        original = audit.read_text()
        for failure in ("checksum", "target_drift", "unreachable", "missing"):
            with self.subTest(failure=failure):
                audit.write_text(original)
                self.transport.reset_mock()
                with mock.patch.object(ssh, "effective_access", return_value=self.access) as access:
                    if failure == "checksum":
                        plan = json.loads(original)
                        plan["effects"]["launch_log"] += ".changed"
                        audit.write_text(json.dumps(plan))
                    elif failure == "target_drift":
                        access.return_value = {"alias": "different-host"}
                    elif failure == "unreachable":
                        access.side_effect = subprocess.TimeoutExpired("ssh -G", 5)
                    else:
                        log.unlink()
                    detail = mcp_runs.observe_registry_run(record.id)
                self.assertIsNone(detail["log_tail"])
                self.assertTrue(detail["warnings"])
                self.assertEqual(
                    (detail["status"], detail["revision"]), ("completed", record.revision)
                )
                if failure != "missing":
                    self.transport.assert_not_called()

    def test_blocked_evidence_does_not_block_cancellation(self) -> None:
        record, _ = self._register(status="running")
        entered, release = threading.Event(), threading.Event()

        def blocked_tail(*args):
            entered.set()
            release.wait(5)
            raise ssh.TransportError("unreachable")

        with (
            mock.patch.object(ssh, "tail_file", side_effect=blocked_tail),
            mock.patch.object(ssh, "stop") as stop,
        ):
            observer = threading.Thread(target=client.observe_execution, args=(record.id,))
            observer.start()
            try:
                self.assertTrue(entered.wait(2))
                canceled = client.request(
                    "/cancel",
                    {"registry_run_id": record.id},
                    timeout=1,
                )
                self.assertEqual(canceled["status"], "canceling")
                stop.assert_called_once()
            finally:
                release.set()
                observer.join(2)
        self.assertEqual(runs._run_record(record.id).status, "canceling")

    def test_cancel_completed_run_is_noop(self) -> None:
        record, _ = self._register()
        canceled = mcp_runs.cancel_registry_run(record.id)
        self.assertEqual(
            (canceled["status"], canceled["registry_run_id"]), ("completed", record.id)
        )
        self.transport.assert_not_called()

    def test_tail_rejects_paths_outside_the_run_symlinks_and_special_files(self) -> None:
        record, log = self._register()
        remote = runs._approved_plan(record)["request"]["remote"]
        root = Path(remote["run_dir"])
        (root / "link").symlink_to(log)
        os.mkfifo(root / "pipe")
        for relative in ("../outside", str(self.root / "outside"), "link", "pipe", "logs"):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                ssh.tail_file(remote, relative)
            with self.subTest(stream=relative), self.assertRaises(ValueError):
                with ssh.stream_file(remote, relative) as lines:
                    lines.read()
        for pattern in ("../*", "link", str(self.root / "*")):
            with self.subTest(selection=pattern), self.assertRaises(ValueError):
                ssh.select_file(remote, (pattern,))

    def test_compute_client_cannot_read_workflow_evidence(self) -> None:
        record, _ = self._register()
        with self.assertRaises(client.DaemonError):
            client.request("/run/evidence", {"registry_run_id": record.id}, role="compute")
        self.transport.assert_not_called()

    def test_evidence_lookup_requires_a_string_id_but_ignores_extra_fields(self) -> None:
        record, log = self._register(target="local")
        observation = client.request(
            "/run/evidence", {"registry_run_id": record.id, "unused": True}
        )
        self.assertEqual(observation["log_tail"], log.read_bytes()[-12_000:].decode())
        for payload in ({}, {"registry_run_id": []}):
            with self.subTest(payload=payload), self.assertRaises(client.DaemonError):
                client.request("/run/evidence", payload)


class SshInspectionTests(DaemonTestCase):
    def test_ssh_inspection_uses_only_the_fixed_remote_program(self) -> None:
        nextflow = self.workspace / "nextflow"
        nextflow.write_text('#!/bin/sh\nprintf "nextflow %s\\n" "$NXF_OFFLINE"\n')
        nextflow.chmod(0o755)
        payload = {
            "workspace_root": str(self.workspace),
            "executor": "slurm",
            "executable_paths": [sys.executable],
        }
        completed = subprocess.run(
            [sys.executable, str(Path(remote_probe.__file__)), json.dumps(payload)],
            capture_output=True,
            text=True,
            env={**os.environ, "PATH": str(self.workspace)},
            check=True,
        )
        facts = json.loads(completed.stdout)
        commands = {item["executable"]: item for item in facts["commands"]}
        self.assertEqual(commands["nextflow"]["version"], "nextflow true")
        self.assertEqual(commands[sys.executable]["state"], "ready")
        self.assertEqual(facts["workspace"]["path"], str(self.workspace))
        self.assertEqual(facts["scheduler"]["worker_readiness"], "unknown")
        self.assertEqual(facts["scheduler"]["shared_filesystem"], "unknown")

        target = self._configure_ssh_target()
        request = TargetInspection(
            target_id="lab", executable_paths=["/remote/bin/fastqc", "sbatch"]
        )
        forged = subprocess.CompletedProcess(
            [], 0, json.dumps({"target_id": "forged", "config_hash": "forged"})
        )
        with mock.patch.object(inspection.subprocess, "run", return_value=forged):
            observed = inspection.inspect_target(target, request)
        self.assertEqual(
            (observed["target_id"], observed["config_hash"]),
            ("lab", target["config_hash"]),
        )

        with (
            mock.patch.object(server, "_list_targets", return_value={"targets": [target]}),
            mock.patch.object(
                inspection,
                "effective_access",
                return_value={**target["host_access"], "port": 2222},
            ),
            mock.patch.object(inspection, "inspect_target") as inspect_changed,
        ):
            with self.assertRaisesRegex(ValueError, "SSH access has changed"):
                server._inspect_target(request)
        inspect_changed.assert_not_called()


class SshTransportTests(unittest.TestCase):
    def test_staged_inputs_are_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            run_dir = workspace / "run"
            (run_dir / "workflow").mkdir(parents=True)
            (run_dir / "workflow" / "approved_plan.json").write_text("{}")
            source = workspace / "input.txt"
            content = b"approved workflow input\n"
            source.write_bytes(content)
            checksum = f"sha256:{hashlib.sha256(content).hexdigest()}"
            remote = {
                "run_dir": "/remote/run",
                "workspace_root": "/remote",
                "host_access": {"alias": "lab"},
                "staged_files": [
                    {
                        "source": str(source),
                        "destination": "/remote/run/input.txt",
                        "bytes": len(content),
                        "sha256": checksum,
                    }
                ],
            }
            with mock.patch.object(ssh, "_invoke"), mock.patch.object(ssh, "_upload") as upload:
                ssh.stage(
                    {"request": {"remote": remote}},
                    run_dir,
                    checkpoint=lambda: None,
                    transfer=lambda _process: None,
                )
            upload.assert_called_once()

    def test_transfer_timeout_scales_with_approved_file_size(self) -> None:
        access = {"alias": "lab"}
        process = mock.MagicMock(returncode=0)
        process.communicate.return_value = (None, "")
        with (
            mock.patch.object(ssh, "effective_access", return_value=access),
            mock.patch.object(ssh.subprocess, "Popen", return_value=process),
        ):
            ssh._upload(
                {"host_access": access},
                "source",
                "destination",
                expected_bytes=5 * 1024**3,
            )
        process.communicate.assert_called_once_with(timeout=120 + 5 * 1024)

    def test_fixed_remote_program_verifies_staged_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            root = workspace / "run"
            content = "approved input\n"
            destination = str(root / "results" / "result.txt")
            request = {
                "workspace_root": str(workspace),
                "run_dir": str(root),
                "operation": "prepare",
                "destinations": [],
                "generated": [{"destination": destination, "content": content}],
            }
            prepared = subprocess.run(
                [sys.executable, str(Path(remote_operations.__file__)), json.dumps(request)],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(json.loads(prepared.stdout), {"ok": True})
            self.assertEqual(root.stat().st_mode & 0o777, 0o700)
            checksum = f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"
            files = [{"destination": destination, "bytes": len(content), "sha256": checksum}]
            request.update(operation="verify", files=files)
            self.assertEqual(remote_operations.execute(request, ""), {"ok": True})
            Path(destination).write_text("changed", encoding="utf-8")
            request.update(operation="verify", files=files)
            with self.assertRaises(ValueError):
                remote_operations.execute(request, "")

    def test_remote_cancellation_retries_after_transport_failure(self) -> None:
        remote: dict[str, object] = {}
        identity = {"pid": 42}
        owned = runs.OwnedRun(
            request=ExecutionRequest(
                binding="nextflow",
                plan_checksum="sha256:" + "0" * 64,
                plan={"request": {"remote": remote}},
            ),
            registry_run_id="remote-run",
            remote_identity=identity,
            canceled=True,
        )
        with (
            mock.patch.object(
                ssh, "stop", side_effect=(ssh.TransportError("offline"), None)
            ) as stop,
            mock.patch.object(ssh, "status", return_value={"running": False, "return_code": -15}),
            mock.patch.object(runs, "_transition") as transition,
            mock.patch.object(runs.time, "sleep"),
        ):
            runs.RunManager._finish_remote(owned)

        self.assertEqual(stop.call_count, 2)
        self.assertTrue(owned.controller_signaled)
        transition.assert_called_once_with("remote-run", "canceled", pid=42)

    def test_controller_script_writes_its_actual_exit_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = {
                "argv": [sys.executable, "-c", "print('completed')"],
                "run_dir": str(root),
                "log": str(root / "controller.log"),
                "exit": str(root / "controller.exit"),
            }
            subprocess.run(
                [sys.executable, str(Path(remote_controller.__file__)), json.dumps(request)],
                check=True,
            )
            self.assertEqual((root / "controller.exit").read_text(), "0")
            self.assertEqual((root / "controller.log").read_text().strip(), "completed")
