from __future__ import annotations

import contextlib
import json
import os
import select
import shutil
import signal
import subprocess
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from http.client import HTTPConnection, RemoteDisconnected
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from daemon_test_case import DaemonTestCase  # noqa: E402
from ngs_workbench_daemon import client, server, state  # noqa: E402
from ngs_workbench_daemon.persistence import (  # noqa: E402
    NewRun,
    RunFilters,
    SqlAlchemyUnitOfWork,
    default_database,
    ensure_workspace_identity,
    registry_path,
)
from ngs_workbench_daemon.protocol import (  # noqa: E402
    IMPLEMENTATION_ID,
    canonical_plan_checksum,
    run_metadata_directory,
)
from ngs_workbench_daemon.runs import RunManager  # noqa: E402
from ngs_workbench_mcp import (  # noqa: E402
    app,
    approved_execution,
    plan_registry,
    preparation,
    runs,
)
from ngs_workbench_mcp.workflows import nextflow as nfcore  # noqa: E402
from ngs_workbench_mcp.workflows import snakemake  # noqa: E402
from ngs_workbench_mcp.workflows.source import WorkflowSource  # noqa: E402
from test_run_persistence import new_run  # noqa: E402

_plan_catalog_workflow = nfcore.plan_remote_run


def _plan_with_catalog_source(*args: object, **kwargs: object) -> dict[str, object]:
    kwargs.setdefault("workflow", "nf-core/demo")
    return _plan_catalog_workflow(*args, **kwargs)


nfcore.plan_remote_run = _plan_with_catalog_source


def _readiness(controller: str = "nextflow") -> dict[str, object]:
    return {
        "ok": True,
        "status": "ready",
        "scope": "executable_presence_only",
        "commands": [{"name": controller, "path": sys.executable}],
        "blockers": [],
    }


class DaemonLifecycleTests(DaemonTestCase):
    def _runtime_directory(self, implementation: str = IMPLEMENTATION_ID) -> Path:
        return state.daemon_runtime_directory(implementation)

    def _start_idle_daemon(self) -> subprocess.Popen[bytes]:
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                (
                    "from ngs_workbench_daemon import server; "
                    "server.IDLE_TIMEOUT_SECONDS = 0.2; server.main()"
                ),
            ],
            env={**os.environ, "PYTHONPATH": str(MCP_ROOT)},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        client._SPAWNED_DAEMON = process
        self._await_path(self._runtime_directory() / "endpoint.json")
        return process

    def test_internal_record_keeps_local_execution_evidence_and_submitted_analysis(self) -> None:
        command = [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "Path('results').mkdir(); Path('results/metrics.tsv').write_text('reads\\n42\\n'); "
                "Path('logs/nextflow.trace.txt').write_text('name\\tstatus\\nQC\\tCOMPLETED\\n'); "
                "print('controller finished')"
            ),
        ]
        _, started = self._start_nfcore(command)
        completed = self._await_status(started["registry_run_id"], {"completed"})
        observation = runs.observe_registry_run(started["registry_run_id"])
        with SqlAlchemyUnitOfWork(default_database()) as uow:
            record = uow.registry.get_run(started["registry_run_id"])
        self.assertTrue(Path(record.run_dir).is_relative_to(registry_path().parent / "runs"))
        self.assertNotEqual(record.run_dir, completed["run_dir"])
        self.assertIn("controller finished", observation["log_tail"])
        self.assertEqual(observation["execution"]["counts"]["completed"], 1)
        self.assertTrue((Path(completed["run_dir"]) / "results/metrics.tsv").is_file())
        source = self.root / "review.md"
        source.write_text("Takeaway: 42 reads observed.\n\nThe metrics report 42 reads.\n")
        app.update_ngs_run_analysis_summary(record.id, str(source))
        report = runs.get_registry_run_report(record.id)
        self.assertIn("42 reads", report["report"]["summary"])
        self.assertFalse(Path(completed["run_dir"]).is_relative_to(self.workspace))
        _, other = self._start_nfcore(
            command, run_id="another-run", run_dir=self.root / "another-execution"
        )
        self._await_status(other["registry_run_id"], {"completed"})
        self.assertNotEqual(other["registry_run_id"], record.id)
        self.assertEqual(
            {run["registry_run_id"] for run in runs.list_registry_runs()["runs"]},
            {record.id, other["registry_run_id"]},
        )
        moved = self.root / "moved-project"
        self.workspace.rename(moved)
        try:
            self.assertIn("42 reads", runs.get_registry_run(record.id)["analysis_summary"])
        finally:
            moved.rename(self.workspace)

    def test_relocated_historical_record_keeps_its_recorded_project_and_results(self) -> None:
        project_id = ensure_workspace_identity(self.workspace)
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as uow:
            uow.registry.register_workspace(project_id, self.workspace)
            created = uow.registry.allocate_approved_run(
                replace(
                    new_run(self.workspace, project_id, "historical", "nextflow"),
                    request={
                        "plan_request": {
                            "workspace_dir": str(self.workspace),
                            "run_id": "historical",
                        }
                    },
                )
            )
            running = uow.registry.transition_run(created.id, "running", expected_revision=1)
            uow.registry.transition_run(created.id, "completed", expected_revision=running.revision)
            uow.commit()
        Path(created.run_dir).mkdir(parents=True)
        (Path(created.run_dir) / "analysis_summary.md").write_text(
            "Historical QC interpretation.\n"
        )
        moved = self.root / "moved-project"
        self.workspace.rename(moved)
        try:
            with SqlAlchemyUnitOfWork(default_database(), immediate=True) as uow:
                uow.registry.register_workspace(project_id, moved)
                uow.commit()
            detail = runs.get_registry_run(created.id)
            report = runs.get_registry_run_report(created.id)
            self.assertEqual(
                detail["run_dir"], str(moved / Path(created.run_dir).relative_to(self.workspace))
            )
            self.assertEqual(report["report"]["summary"], "Historical QC interpretation.")
        finally:
            moved.rename(self.workspace)

    def test_registry_identity_observes_and_cancels_without_workspace_marker(self) -> None:
        _, started = self._start_nfcore([sys.executable, "-c", "import time; time.sleep(30)"])
        self._await_status(started["registry_run_id"], {"running"})
        registry_id = started["registry_run_id"]
        with SqlAlchemyUnitOfWork(default_database()) as uow:
            record = uow.registry.get_run(registry_id)
        marker = Path(record.workspace_dir) / "ngs_runs/.mcp/workspace.json"
        moved_marker = marker.with_suffix(".hidden")
        marker.rename(moved_marker)
        moved_workspace = self.root / "hidden-project"
        self.workspace.rename(moved_workspace)
        try:
            self.assertEqual(runs.get_registry_run(registry_id)["status"], "running")
            canceled = app.cancel_ngs_run(registry_id)
            self.assertTrue(canceled["ok"], canceled)
            self.assertIn(canceled["status"], {"cancel_requested", "canceling", "canceled"})
        finally:
            moved_workspace.rename(self.workspace)
            moved_marker.rename(marker)
            app.cancel_ngs_run(registry_id)
        self._await_status(registry_id, {"canceled"})

    def test_agent_summary_submission_survives_restart_without_changing_run_lifecycle(self) -> None:
        workspace_id = ensure_workspace_identity(self.workspace)
        summary = (
            "Takeaway: QC needs review.\n\nAgent interpretation from selected metrics.\n"
            "\n# Evidence\n" + "Detailed analysis.\n" * 4000
        )
        for target in ("local", "lab"):
            for status in ("completed", "failed"):
                with self.subTest(target=target, status=status):
                    run_id = f"summary-{target}-{status}"
                    with SqlAlchemyUnitOfWork(default_database(), immediate=True) as uow:
                        uow.registry.register_workspace(workspace_id, self.workspace)
                        created = uow.registry.allocate_approved_run(
                            replace(
                                new_run(self.workspace, workspace_id, run_id, "nextflow"),
                                request={
                                    "target": {"target_id": target},
                                    "remote": {"run_dir": f"/remote/{run_id}"},
                                }
                                if target != "local"
                                else {"target": {"target_id": target}},
                            )
                        )
                        running = uow.registry.transition_run(
                            created.id, "running", expected_revision=created.revision
                        )
                        terminal = uow.registry.transition_run(
                            running.id,
                            status,
                            expected_revision=running.revision,
                            return_code=0 if status == "completed" else 1,
                        )
                        uow.commit()
                    before = runs.get_registry_run(terminal.id)
                    self.assertEqual(before["analysis_summary"], "")
                    source = (self.workspace if target == "local" else self.root) / f"{run_id}.md"
                    source.write_text(summary, encoding="utf-8")
                    receipt = app.update_ngs_run_analysis_summary(terminal.id, str(source))
                    self.assertTrue(receipt["ok"])
                    source.unlink()
                    self.assertEqual(
                        (Path(terminal.run_dir) / "analysis_summary.md").read_text(), summary
                    )
                    self._crash_daemon()
                    detail = runs.get_registry_run(terminal.id)
                    history = next(
                        row
                        for row in runs.list_registry_runs()["runs"]
                        if row["registry_run_id"] == terminal.id
                    )
                    self.assertEqual(
                        detail["analysis_summary"], "Agent interpretation from selected metrics."
                    )
                    self.assertIn("QC needs review.", history["analysis_summary"])
                    for field in ("status", "revision", "completed_at_ms", "returncode"):
                        self.assertEqual(detail[field], before[field])
                    if target != "local":
                        self.assertEqual(detail["run_dir"], f"/remote/{run_id}")
                        self.assertFalse((Path(terminal.run_dir) / "results").exists())

                    with self.assertRaises(client.DaemonError):
                        app.update_ngs_run_analysis_summary(terminal.id, str(source))
                    with self.assertRaises(client.DaemonError):
                        client.request(
                            "/run/analysis-summary",
                            {"registry_run_id": terminal.id, "summary_path": str(source)},
                            role="compute",
                        )
                    self.assertEqual(
                        (Path(terminal.run_dir) / "analysis_summary.md").read_text(), summary
                    )

    def _start_nfcore(
        self,
        command: list[str],
        *,
        attempt_number: int = 1,
        first_run_id: str | None = None,
        run_id: str = "nfcore-fastq-qc-daemon",
        run_dir: Path | None = None,
        preparation_spec: object | None = None,
    ) -> tuple[dict[str, object], dict[str, object]]:
        with (
            mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=_readiness()),
            mock.patch.object(nfcore, "build_nextflow_argv", return_value=command),
        ):
            planned = nfcore.plan_remote_run(
                pipeline="fastq_qc",
                run_dir=str(run_dir or self.root / "execution" / run_id),
                profile="test,docker",
                revision="1.2.0",
                run_id=run_id,
                first_run_id=first_run_id,
                attempt_number=attempt_number,
                preparation_spec=preparation_spec,
            )
            registered = plan_registry.register_plan("nextflow", planned)
            started = approved_execution.execute_registered_plan(
                str(registered["plan_name"]),
                str(registered["plan_id"]),
                str(registered["plan_checksum"]),
            )
        return registered, started

    def _plan_nfcore_recovery(
        self,
        command: list[str],
        *,
        attempt_number: int,
        first_run_id: str,
        run_id: str,
    ) -> dict[str, object]:
        with (
            mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=_readiness()),
            mock.patch.object(nfcore, "build_nextflow_argv", return_value=command),
        ):
            planned = nfcore.plan_remote_run(
                pipeline="fastq_qc",
                run_dir=str(self.root / "execution" / run_id),
                profile="test,docker",
                revision="1.2.0",
                run_id=run_id,
                first_run_id=first_run_id,
                attempt_number=attempt_number,
            )
            return plan_registry.register_plan("nextflow", planned)

    def _await_status(self, registry_run_id: str, statuses: set[str]) -> dict[str, object]:
        deadline = time.monotonic() + 10
        result: dict[str, object] = {}
        while time.monotonic() < deadline:
            result = runs.get_registry_run(registry_run_id)
            if result.get("status") in statuses:
                return result
            time.sleep(0.025)
        self.fail(f"run did not reach {sorted(statuses)}: {result}")

    def _await_path(self, path: Path) -> None:
        deadline = time.monotonic() + 10
        while not path.exists() and time.monotonic() < deadline:
            time.sleep(0.025)
        self.assertTrue(path.exists(), f"expected controller or transfer marker: {path}")

    def _await_process_exit(self, pid: int) -> None:
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.025)
        self.fail(f"replacement daemon left process {pid} running")

    def _alternate_installation(self, version: str = "999.0.0") -> Path:
        installation = self.root / "another-installation"
        shutil.copytree(
            MCP_ROOT / "ngs_workbench_daemon",
            installation / "mcp" / "ngs_workbench_daemon",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        shutil.copytree(
            MCP_ROOT / "ngs_workbench_execution_monitoring",
            installation / "mcp" / "ngs_workbench_execution_monitoring",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        manifest_directory = installation / ".codex-plugin"
        manifest_directory.mkdir()
        (manifest_directory / "plugin.json").write_text(
            json.dumps({"version": version}), encoding="utf-8"
        )
        return installation

    def _ensure_from_installation(
        self, installation: Path, *, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        script = (
            "import json; "
            "from ngs_workbench_daemon.client import ensure_daemon_running; "
            "from ngs_workbench_daemon.protocol import IMPLEMENTATION_ID; "
            "owner=ensure_daemon_running(); "
            "print(json.dumps({'instance_id': owner.instance_id, "
            "'implementation': IMPLEMENTATION_ID}))"
        )
        return subprocess.run(
            [sys.executable, "-c", script],
            cwd=self.root,
            env={**os.environ, "PYTHONPATH": str(installation / "mcp")},
            capture_output=True,
            text=True,
            timeout=20,
            check=check,
        )

    def test_concurrent_clients_elect_one_private_native_locked_daemon(self) -> None:
        script = (
            "import json; from ngs_workbench_daemon.client import ensure_daemon_running; "
            "owner=ensure_daemon_running(); "
            "print(json.dumps({'instance_id': owner.instance_id, 'port': owner.port}))"
        )
        environment = {**os.environ, "PYTHONPATH": str(MCP_ROOT)}
        processes = [
            subprocess.Popen(
                [sys.executable, "-c", script],
                cwd=self.root,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in range(6)
        ]
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, stderr)
            results.append(json.loads(stdout))

        self.assertEqual(len({item["instance_id"] for item in results}), 1)
        self.assertEqual(len({item["port"] for item in results}), 1)
        shared = self.state_dir / "daemon"
        directory = self._runtime_directory()
        self.assertTrue(client._owner_is_held(directory))
        self.assertEqual(shared.stat().st_mode & 0o777, 0o700)
        self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
        for name in ("startup.lock", "token"):
            self.assertEqual((shared / name).stat().st_mode & 0o777, 0o600)
        for name in ("owner.lock", "endpoint.json"):
            self.assertEqual((directory / name).stat().st_mode & 0o777, 0o600)

    def test_different_versions_start_concurrently_with_one_shared_token(self) -> None:
        installation = self._alternate_installation()
        script = (
            "import json; from ngs_workbench_daemon.client import ensure_daemon_running; "
            "from ngs_workbench_daemon.protocol import IMPLEMENTATION_ID; "
            "owner=ensure_daemon_running(); "
            "print(json.dumps({'implementation': IMPLEMENTATION_ID, "
            "'instance_id': owner.instance_id}))"
        )
        processes = [
            subprocess.Popen(
                [sys.executable, "-c", script],
                cwd=self.root,
                env={**os.environ, "PYTHONPATH": str(root)},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for root in (MCP_ROOT, installation / "mcp")
        ]

        observed = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, stderr)
            observed.append(json.loads(stdout))

        self.assertEqual(
            {item["implementation"] for item in observed}, {IMPLEMENTATION_ID, "999.0.0"}
        )
        self.assertEqual(len({item["instance_id"] for item in observed}), 2)
        token = state.daemon_token(self.state_dir / "daemon")
        self.assertTrue(token)

    def test_legacy_daemon_owner_does_not_block_versioned_daemon(self) -> None:
        shared = state.daemon_directory()
        legacy_owner = state.native_lock(shared / "owner.lock", timeout=0)
        legacy_owner.acquire()
        try:
            endpoint = client.ensure_daemon_running()
        finally:
            legacy_owner.release()

        self.assertEqual(endpoint.implementation, IMPLEMENTATION_ID)
        self.assertTrue((self._runtime_directory() / "endpoint.json").is_file())

    def test_endpoint_requires_the_private_token_and_instance_identity(self) -> None:
        endpoint = client.ensure_daemon_running()
        connection = HTTPConnection("127.0.0.1", endpoint.port, timeout=2)
        try:
            connection.request("GET", "/health")
            self.assertEqual(connection.getresponse().status, 401)
        finally:
            connection.close()

    def test_idle_version_exits_and_restarts_without_removing_shared_state(self) -> None:
        process = self._start_idle_daemon()
        owner = client.ensure_daemon_running()
        token = state.daemon_token(state.daemon_directory())
        result = self._ensure_from_installation(self._alternate_installation())
        observed = json.loads(result.stdout)
        self.assertNotEqual(observed["instance_id"], owner.instance_id)
        self.assertEqual(observed["implementation"], "999.0.0")
        self.assertEqual(process.wait(timeout=5), 0)
        self.assertFalse((self._runtime_directory() / "endpoint.json").exists())
        self.assertTrue((self._runtime_directory("999.0.0") / "endpoint.json").is_file())
        self.assertNotEqual(client.ensure_daemon_running().instance_id, owner.instance_id)
        self.assertEqual(state.daemon_token(state.daemon_directory()), token)

    def test_idle_exit_waits_for_an_accepted_request(self) -> None:
        entered, release = threading.Event(), threading.Event()

        def blocked_targets() -> dict[str, object]:
            entered.set()
            release.wait(5)
            return {"targets": []}

        token = state.daemon_token(state.daemon_directory(), create=True)
        with (
            server.DaemonServer(token, "idle-request") as daemon,
            mock.patch.object(server, "IDLE_TIMEOUT_SECONDS", 0.1),
            mock.patch.object(server, "_list_targets", side_effect=blocked_targets),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            serving = pool.submit(daemon.serve_until_idle)
            endpoint = client.DaemonEndpoint(
                "127.0.0.1", daemon.server_port, "idle-request", IMPLEMENTATION_ID
            )
            response = pool.submit(client._request, endpoint, "/targets", {})
            try:
                self.assertTrue(entered.wait(3))
                with self.assertRaises(TimeoutError):
                    serving.result(timeout=0.3)
            finally:
                release.set()
            self.assertEqual(response.result(timeout=3), {"targets": []})
            serving.result(timeout=3)

    def test_only_connection_failure_before_sending_is_retried(self) -> None:
        endpoint = client.ensure_daemon_running()
        with (
            mock.patch.object(client, "ensure_daemon_running", return_value=endpoint),
            mock.patch.object(client, "HTTPConnection") as transport,
        ):
            connection = transport.return_value
            connection.connect.side_effect = [ConnectionRefusedError(), None]
            connection.getresponse.return_value.status = 200
            connection.getresponse.return_value.read.return_value = b'{"ok":true}'
            self.assertTrue(client.request("/runs", {})["ok"])
            self.assertEqual(connection.request.call_count, 1)
            connection.reset_mock()
            connection.connect.side_effect = None
            connection.getresponse.side_effect = RemoteDisconnected()
            with self.assertRaises(client.DaemonError):
                client.request("/runs", {})
            self.assertEqual(connection.request.call_count, 1)

    def test_same_plugin_version_reuses_daemon_across_installations(self) -> None:
        owner = client.ensure_daemon_running()

        result = self._ensure_from_installation(
            self._alternate_installation(version=IMPLEMENTATION_ID)
        )

        self.assertEqual(json.loads(result.stdout)["instance_id"], owner.instance_id)

    def test_new_plugin_implementation_does_not_interrupt_active_daemon(self) -> None:
        run_id = "nfcore-version-replacement"
        _, started = self._start_nfcore(
            [sys.executable, "-c", "import time; time.sleep(30)"], run_id=run_id
        )
        self._await_status(started["registry_run_id"], {"running"})
        owner = client.ensure_daemon_running()
        installation = self._alternate_installation()

        with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
            assert unit_of_work.registry is not None
            record = unit_of_work.registry.get_run(str(started["registry_run_id"]))
            daemon_owned = unit_of_work.registry.list_daemon_owned_active_runs()
        assert record is not None
        self.assertNotIn("daemon_instance_id", record.request)
        self.assertEqual(
            record.request["daemon_owner"],
            {"implementation": IMPLEMENTATION_ID, "instance_id": owner.instance_id},
        )
        self.assertIn(record.id, {item.id for item in daemon_owned})

        observed = json.loads(self._ensure_from_installation(installation).stdout)

        self.assertNotEqual(observed["instance_id"], owner.instance_id)
        self.assertEqual(observed["implementation"], "999.0.0")
        self.assertEqual(client._request(owner, "/health")["instance_id"], owner.instance_id)
        self.assertEqual(client.ensure_daemon_running().instance_id, owner.instance_id)
        self.assertEqual(runs.get_registry_run(started["registry_run_id"])["status"], "running")

        canceled = app.cancel_ngs_run(str(started["registry_run_id"]))
        self.assertTrue(canceled["ok"], canceled)
        self._await_status(started["registry_run_id"], {"canceled"})

    def test_new_daemon_does_not_adopt_another_implementations_remote_run(self) -> None:
        workspace_id = ensure_workspace_identity(self.workspace)
        run_root = Path("ngs_runs/nextflow/fastq_qc/remote-old-version")
        request = {
            "target": {"target_id": "lab"},
            "daemon_owner": {
                "implementation": "older-version",
                "instance_id": "older-instance",
            },
        }
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
            assert unit_of_work.registry is not None
            unit_of_work.registry.register_workspace(workspace_id, self.workspace)
            new_run = NewRun(
                workspace_id=workspace_id,
                workspace_dir=self.workspace,
                external_run_id="remote-old-version",
                binding="nextflow",
                pipeline="fastq_qc",
                workflow="nf-core/demo",
                plan_checksum="sha256:" + "0" * 64,
                request=request,
                command_argv=["nextflow", "run"],
                run_relative_path=run_root.as_posix(),
                approved_plan_relative_path=(run_root / "workflow/approved_plan.json").as_posix(),
                launch_log_relative_path=(run_root / "logs/run.log").as_posix(),
            )
            registered = unit_of_work.registry.allocate_approved_run(new_run)
            registered = unit_of_work.registry.transition_run(
                registered.id,
                "running",
                expected_revision=registered.revision,
                pid=42,
            )
            unit_of_work.commit()

        with mock.patch("ngs_workbench_daemon.runs.ssh.identity") as identify:
            observed = RunManager("current-instance").observe(registered.id)

        identify.assert_not_called()
        self.assertFalse(observed["process_owned"])

        request["daemon_owner"]["implementation"] = IMPLEMENTATION_ID
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
            owned = unit_of_work.registry.allocate_approved_run(
                replace(new_run, external_run_id="remote-current-version", request=request)
            )
            owned = unit_of_work.registry.transition_run(
                owned.id, "running", expected_revision=owned.revision, pid=43
            )
            unit_of_work.commit()
        process = self._start_idle_daemon()
        with self.assertRaises(subprocess.TimeoutExpired):
            process.wait(timeout=0.6)
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
            unit_of_work.registry.transition_run(
                owned.id, "completed", expected_revision=owned.revision, return_code=0
            )
            unit_of_work.commit()
        self.assertEqual(process.wait(timeout=5), 0)

    def test_incompatible_protocol_does_not_replace_an_active_daemon(self) -> None:
        run_id = "nfcore-incompatible-daemon"
        _, started = self._start_nfcore(
            [sys.executable, "-c", "import time; time.sleep(30)"], run_id=run_id
        )
        self._await_status(started["registry_run_id"], {"running"})
        owner = client.ensure_daemon_running()

        with (
            mock.patch.object(client, "PROTOCOL_VERSION", client.PROTOCOL_VERSION + 1),
            mock.patch.object(client, "_spawn_daemon") as spawn,
        ):
            with self.assertRaisesRegex(client.DaemonError, "incompatible protocol"):
                client.ensure_daemon_running()
        spawn.assert_not_called()
        self.assertEqual(client.ensure_daemon_running().instance_id, owner.instance_id)
        self.assertEqual(runs.get_registry_run(started["registry_run_id"])["status"], "running")

        canceled = app.cancel_ngs_run(str(started["registry_run_id"]))
        self.assertTrue(canceled["ok"], canceled)
        self._await_status(started["registry_run_id"], {"canceled"})

    def test_approved_run_is_reserved_before_background_preparation_and_completion(self) -> None:
        prepared = preparation.normalize_preparation(
            {
                "destination_dir": str(self.workspace / "prepared"),
                "generated_files": [
                    {
                        "relative_path": "inputs.json",
                        "content": "{}\n",
                        "media_type": "application/json",
                    }
                ],
            }
        )
        command = [sys.executable, "-c", "import time; time.sleep(0.6)"]

        with mock.patch.object(client, "_spawn_daemon", side_effect=self._start_idle_daemon):
            registered, started = self._start_nfcore(command, preparation_spec=prepared)
        self.assertTrue(started["ok"])
        self.assertIn(started["status"], {"starting", "running"})
        self.assertTrue(registry_path().is_file())

        completed = self._await_status(started["registry_run_id"], {"completed"})
        self.assertEqual(completed["plan_checksum"], registered["plan_checksum"])
        self.assertEqual((self.workspace / "prepared" / "inputs.json").read_text(), "{}\n")
        with SqlAlchemyUnitOfWork(default_database()) as uow:
            approved = runs._approved_plan(uow.registry.get_run(completed["registry_run_id"]))
        assert approved is not None
        self.assertEqual(approved.pop("plan_checksum"), registered["plan_checksum"])
        self.assertEqual(approved["request"]["run_id"], completed["run_id"])
        self.assertEqual(approved["command_argv"], command)

    def test_repeated_approved_identity_does_not_launch_a_second_controller(self) -> None:
        launches = self.root / "launches.txt"
        command = [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; import time; "
                f"p=Path({str(launches)!r}); "
                "p.write_text(p.read_text() + '1' if p.exists() else '1'); "
                "time.sleep(0.35)"
            ),
        ]
        registered, first = self._start_nfcore(command, run_id="nfcore-idempotent")
        self._await_status(first["registry_run_id"], {"running"})

        second = approved_execution.execute_registered_plan(
            str(registered["plan_name"]),
            str(registered["plan_id"]),
            str(registered["plan_checksum"]),
        )
        self._await_status(first["registry_run_id"], {"completed"})

        self.assertEqual(first["registry_run_id"], second["registry_run_id"])
        self.assertEqual(launches.read_text(encoding="utf-8"), "1")
        self.assertEqual(len(runs.list_registry_runs()["runs"]), 1)

    def test_pre_lineage_v3_approvals_execute_once_without_changing_the_approved_plan(self) -> None:
        controller = self.root / "controller"
        controller.write_text(
            f"#!{sys.executable}\nfrom pathlib import Path\n"
            "p = Path('launches'); p.write_text(p.read_text() + '1' if p.exists() else '1')\n"
        )
        controller.chmod(0o755)
        config = self.workspace / "config.json"
        config.write_text("{}\n")
        (self.workspace / "main.nf").write_text("workflow {}\n")
        (self.workspace / "Snakefile").write_text("rule all:\n    input: []\n")
        readiness = {**_readiness(), "commands": [{"name": "nextflow", "path": str(controller)}]}
        with (
            mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=readiness),
            mock.patch.object(nfcore, "assess_readiness", return_value=readiness),
            mock.patch.object(nfcore, "build_nextflow_argv", return_value=[str(controller)]),
            mock.patch.object(snakemake, "assess_readiness", return_value=_readiness("snakemake")),
            mock.patch.object(snakemake, "build_snakemake_argv", return_value=[str(controller)]),
        ):
            plans = [
                (
                    "nextflow",
                    nfcore.plan_remote_run("fastq_qc", str(self.root / "curated"), "test,docker"),
                ),
                (
                    "nextflow",
                    nfcore.plan_run(
                        "example",
                        str(self.root / "generic"),
                        workflow_source=WorkflowSource(
                            engine="nextflow", root=str(self.workspace), entrypoint="main.nf"
                        ),
                    ),
                ),
                (
                    "snakemake",
                    snakemake.plan_run(
                        "fastq_qc",
                        str(self.root / "snake"),
                        str(config),
                        workflow_source=WorkflowSource(
                            engine="snakemake", root=str(self.workspace), entrypoint="Snakefile"
                        ),
                    ),
                ),
            ]
            for binding, payload in plans:
                with self.subTest(binding=binding, workflow=payload["request"]["workflow"]):
                    # Reproduce the persisted envelope from before lineage existed, without
                    # passing it through the new model or recalculating it after loading.
                    payload["schema_version"] = 3
                    for field in ("first_run_id", "attempt_number"):
                        del payload["request"][field]
                    checksum = canonical_plan_checksum(payload)
                    plan_id = f"ngs-plan-{checksum.removeprefix('sha256:')[:16]}"
                    name = payload["request"]["display_name"]
                    record = dict(
                        schema_version=1,
                        binding=binding,
                        plan_name=name,
                        plan_id=plan_id,
                        plan_checksum=checksum,
                        plan=payload,
                    )
                    path = self.state_dir / "plans" / f"{plan_id}.json"
                    path.parent.mkdir(exist_ok=True, parents=True)
                    original = json.dumps(record)
                    path.write_text(original)
                    started = approved_execution.execute_registered_plan(name, plan_id, checksum)
                    completed = self._await_status(started["registry_run_id"], {"completed"})
                    self.assertEqual(completed["first_run_id"], payload["request"]["run_id"])
                    self.assertEqual(completed["attempt_number"], 1)
                    self.assertEqual(completed["plan_checksum"], checksum)
                    with SqlAlchemyUnitOfWork(default_database()) as uow:
                        approved = runs._approved_plan(
                            uow.registry.get_run(completed["registry_run_id"])
                        )
                    self.assertEqual(approved, {"plan_checksum": checksum, **payload})
                    self.assertEqual(Path(completed["run_dir"], "launches").read_text(), "1")
                    self.assertEqual(path.read_text(), original)

    def test_run_directory_is_reserved_across_engines_before_background_writes(self) -> None:
        execution_dir = self.root / "shared-execution"
        config = self.workspace / "config.json"
        config.write_text("{}\n")
        (self.workspace / "Snakefile").write_text("rule all:\n    input: []\n")
        manager = RunManager("reservation-test")
        with (
            mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=_readiness()),
            mock.patch.object(snakemake, "assess_readiness", return_value=_readiness("snakemake")),
        ):
            plans = [
                (
                    "nextflow",
                    nfcore.plan_remote_run("fastq_qc", str(execution_dir), "test,docker"),
                    nfcore.approved_nfcore_execution_request,
                ),
                (
                    "snakemake",
                    snakemake.plan_run(
                        "fastq_qc",
                        str(execution_dir),
                        str(config),
                        workflow_source=WorkflowSource(
                            engine="snakemake", root=str(self.workspace), entrypoint="Snakefile"
                        ),
                    ),
                    snakemake.approved_execution_request,
                ),
            ]
        requests = []
        for binding, planned, build_request in plans:
            registered = plan_registry.register_plan(binding, planned)
            _, model = plan_registry.load_approved_plan(
                registered["plan_name"], registered["plan_id"], registered["plan_checksum"]
            )
            requests.append(
                build_request(model, registered["plan_checksum"], refresh_runtime=False)
            )
        # Hold the scheduler so the competing approval arrives before any directory is created.
        with mock.patch("ngs_workbench_daemon.runs.threading.Thread.start"):
            with approved_execution._native_authorization(requests[0]) as authorized:
                accepted = manager.execute(authorized)
            with SqlAlchemyUnitOfWork(default_database()) as uow:
                record = uow.registry.get_run(accepted["registry_run_id"])
            self.assertFalse(Path(record.run_dir).exists())
            self.assertFalse(execution_dir.exists())
            with approved_execution._native_authorization(requests[1]) as authorized:
                with self.assertRaises(ValueError):
                    manager.execute(authorized)
        with SqlAlchemyUnitOfWork(default_database()) as uow:
            records = uow.registry.list_runs(RunFilters())
        self.assertEqual([record.id for record in records], [accepted["registry_run_id"]])

    def test_competing_recovery_plans_reserve_only_one_next_attempt(self) -> None:
        _, first = self._start_nfcore(
            [sys.executable, "-c", "raise SystemExit(7)"],
            run_id="nfcore-recovery-root",
        )
        self._await_status(str(first["registry_run_id"]), {"failed"})

        # Model a historical root whose metadata lives in a project workspace.
        project_id = ensure_workspace_identity(self.workspace)
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as uow:
            root_record = uow.registry.get_run(first["registry_run_id"])
            uow.registry.register_workspace(project_id, self.workspace)
            uow.commit()
        shutil.move(root_record.run_dir, self.workspace / "historical")
        with default_database().engine.begin() as connection:
            connection.exec_driver_sql(
                "UPDATE runs SET workspace_id = ?, run_relative_path = 'historical', "
                "approved_plan_relative_path = 'historical/workflow/approved_plan.json', "
                "launch_log_relative_path = 'historical/logs/nextflow.log' WHERE id = ?",
                (project_id, root_record.id),
            )

        command = [sys.executable, "-c", "import time; time.sleep(0.3)"]
        candidates = [
            self._plan_nfcore_recovery(
                command,
                attempt_number=2,
                first_run_id="nfcore-recovery-root",
                run_id=run_id,
            )
            for run_id in ("nfcore-recovery-a", "nfcore-recovery-b")
        ]
        with (
            mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=_readiness()),
            mock.patch.object(nfcore, "build_nextflow_argv", return_value=command),
        ):
            winner = approved_execution.execute_registered_plan(
                str(candidates[0]["plan_name"]),
                str(candidates[0]["plan_id"]),
                str(candidates[0]["plan_checksum"]),
            )
            with self.assertRaisesRegex(client.DaemonError, "attempt is stale"):
                approved_execution.execute_registered_plan(
                    str(candidates[1]["plan_name"]),
                    str(candidates[1]["plan_id"]),
                    str(candidates[1]["plan_checksum"]),
                )

        self.assertNotEqual(first["registry_run_id"], winner["registry_run_id"])
        with SqlAlchemyUnitOfWork(default_database()) as uow:
            recovered = uow.registry.get_run(winner["registry_run_id"])
            self.assertNotEqual(recovered.workspace_id, project_id)
            self.assertEqual(uow.registry.get_first_run("nfcore-recovery-root").id, root_record.id)
        lineage = runs.list_registry_runs(first_run_id="nfcore-recovery-root")["runs"]
        self.assertEqual(
            [(run["run_id"], run["attempt_number"]) for run in lineage],
            [("nfcore-recovery-a", 2), ("nfcore-recovery-root", 1)],
        )
        losing_dir = self.root / "execution" / "nfcore-recovery-b"
        self.assertFalse(losing_dir.exists())
        self.assertFalse(run_metadata_directory("local", str(losing_dir)).exists())

    @unittest.skipIf(os.name == "nt", "daemon crash recovery uses POSIX process groups")
    def test_replacement_orphans_the_crashed_daemons_run(self) -> None:
        ready = self.root / "controller-ignores-termination"
        _, started = self._start_nfcore(
            [
                sys.executable,
                "-c",
                (
                    "import pathlib,signal,time; "
                    "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                    f"pathlib.Path({str(ready)!r}).touch(); time.sleep(30)"
                ),
            ],
            run_id="nfcore-daemon-crash",
        )
        running = self._await_status(started["registry_run_id"], {"running"})
        self._await_path(ready)
        controller_pid = int(running["pid"])

        try:
            endpoint = self._crash_daemon()
            os.kill(controller_pid, 0)

            detail = runs.observe_registry_run(str(started["registry_run_id"]))
            replacement = client.healthy_daemon()

            self.assertIsNotNone(replacement)
            assert replacement is not None
            self.assertNotEqual(replacement.instance_id, endpoint.instance_id)
            self.assertEqual(detail["status"], "orphaned")
            self._await_process_exit(controller_pid)
        finally:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(controller_pid, signal.SIGKILL)

    @unittest.skipIf(os.name == "nt", "POSIX process-group detachment requires a POSIX runner")
    def test_daemon_and_controller_survive_initiating_process_group_termination(self) -> None:
        run_id = "nfcore-initiator-survival"
        run_dir = self.root / "execution" / run_id
        marker = run_dir / "results" / "done.txt"
        command = [
            sys.executable,
            "-c",
            (
                "import pathlib,time; time.sleep(0.75); "
                f"path=pathlib.Path({str(marker)!r}); "
                "path.parent.mkdir(parents=True,exist_ok=True); "
                "path.write_text('completed')"
            ),
        ]
        script = (
            "import json,time\n"
            "from unittest import mock\n"
            "from ngs_workbench_mcp import approved_execution,plan_registry\n"
            "from ngs_workbench_mcp.workflows import nextflow as nfcore\n"
            f"readiness={_readiness()!r}\n"
            f"command={command!r}\n"
            f"run_dir={str(run_dir)!r}\n"
            "with mock.patch.object(nfcore,'assess_nfcore_readiness',return_value=readiness), "
            "mock.patch.object(nfcore,'build_nextflow_argv',return_value=command):\n"
            f" plan=nfcore.plan_remote_run('fastq_qc',run_dir,'test,docker',run_id={run_id!r},workflow='nf-core/demo')\n"
            " registered=plan_registry.register_plan('nextflow',plan)\n"
            " result=approved_execution.execute_registered_plan("
            "registered['plan_name'],registered['plan_id'],registered['plan_checksum'])\n"
            " print(json.dumps(result),flush=True)\n"
            " time.sleep(30)\n"
        )
        process = subprocess.Popen(
            [sys.executable, "-c", script],
            cwd=self.root,
            env={**os.environ, "PYTHONPATH": str(MCP_ROOT)},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            assert process.stdout is not None
            ready, _, _ = select.select([process.stdout], [], [], 20)
            self.assertTrue(ready, "initiating Workbench process did not report its approved run")
            line = process.stdout.readline()
            if not line:
                self.fail(process.stderr.read() if process.stderr is not None else "")
            started = json.loads(line)
            endpoint = client.ensure_daemon_running()

            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            completed = self._await_status(started["registry_run_id"], {"completed"})

            self.assertTrue(started["ok"])
            self.assertEqual(completed["registry_run_id"], started["registry_run_id"])
            self.assertEqual(marker.read_text(encoding="utf-8"), "completed")
            self.assertEqual(client.ensure_daemon_running().instance_id, endpoint.instance_id)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()

    def test_controller_that_handles_cancellation_with_exit_zero_is_canceled(self) -> None:
        ready = self.root / "signal-handler-ready"
        command = [
            sys.executable,
            "-c",
            (
                "import pathlib,signal,sys,time; "
                "signal.signal(signal.SIGTERM,lambda *_: sys.exit(0)); "
                f"pathlib.Path({str(ready)!r}).write_text('ready'); "
                "time.sleep(30)"
            ),
        ]
        _, started = self._start_nfcore(command, run_id="nfcore-cancel-exit-zero")
        self._await_status(started["registry_run_id"], {"running"})
        self._await_path(ready)

        canceled = runs.cancel_registry_run(started["registry_run_id"])
        terminal = self._await_status(started["registry_run_id"], {"canceled"})

        self.assertTrue(canceled["ok"])
        self.assertEqual(terminal["status"], "canceled")
        self.assertEqual(terminal["returncode"], 0)

    def test_each_controller_observes_the_current_callers_runtime_environment(self) -> None:
        inherited = {
            "JAVA_HOME": "/daemon/original",
            "NXF_HOME": "/daemon/nextflow",
            "AWS_PROFILE": "daemon-account",
            "DAEMON_ONLY_SECRET": "previous-session",
        }
        with mock.patch.dict(os.environ, inherited):
            client.ensure_daemon_running()

        for run_id, values in (
            (
                "nfcore-current-environment",
                {
                    "JAVA_HOME": "/caller/current",
                    "NXF_HOME": "/caller/nextflow",
                    "AWS_PROFILE": "caller-account",
                },
            ),
            ("nfcore-cleared-environment", {}),
        ):
            with self.subTest(run_id=run_id), mock.patch.dict(os.environ):
                for key in inherited:
                    os.environ.pop(key, None)
                os.environ.update(values)
                os.environ["CALLER_ONLY_SECRET"] = "current-session"
                marker = self.root / f"{run_id}.txt"
                command = [
                    sys.executable,
                    "-c",
                    (
                        "import json,os,pathlib; "
                        f"keys={(*inherited, 'CALLER_ONLY_SECRET')!r}; "
                        f"pathlib.Path({str(marker)!r}).write_text("
                        "json.dumps({key: os.environ[key] for key in keys if key in os.environ}))"
                    ),
                ]

                _, started = self._start_nfcore(command, run_id=run_id)
                self._await_status(started["registry_run_id"], {"completed"})

                self.assertEqual(json.loads(marker.read_text(encoding="utf-8")), values)

    def test_controller_failure_is_visible_in_the_durable_run(self) -> None:
        _, started = self._start_nfcore(
            [sys.executable, "-c", "raise SystemExit(7)"], run_id="nfcore-controller-failure"
        )
        failed = self._await_status(started["registry_run_id"], {"failed"})
        self.assertEqual(failed["returncode"], 7)
        self.assertIn("7", str(failed["failure_summary"]))

    def test_preparation_rejects_a_symlinked_destination_parent(self) -> None:
        destination = self.workspace / "prepared"
        destination.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        (destination / "escaped").symlink_to(outside, target_is_directory=True)
        prepared = preparation.normalize_preparation(
            {
                "destination_dir": str(destination),
                "generated_files": [
                    {
                        "relative_path": "escaped/inputs.json",
                        "content": "{}\n",
                        "media_type": "application/json",
                    }
                ],
            }
        )

        _, started = self._start_nfcore(
            [sys.executable, "-c", "raise SystemExit(0)"],
            run_id="nfcore-symlink-preparation",
            preparation_spec=prepared,
        )
        failed = self._await_status(started["registry_run_id"], {"failed"})

        self.assertIn("symlink", str(failed["failure_summary"]))
        self.assertFalse((outside / "inputs.json").exists())

    def test_checksum_tampering_is_rejected_before_workspace_identity_or_reservation(self) -> None:
        with (
            mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=_readiness()),
            mock.patch.object(
                nfcore,
                "build_nextflow_argv",
                return_value=[sys.executable, "-c", "raise SystemExit(0)"],
            ),
        ):
            planned = nfcore.plan_remote_run(
                "fastq_qc",
                str(self.root / "execution" / "tampered"),
                "test,docker",
                run_id="nfcore-tampered-plan",
            )
            registered = plan_registry.register_plan("nextflow", planned)
            _, model = plan_registry.load_approved_plan(
                str(registered["plan_name"]),
                str(registered["plan_id"]),
                str(registered["plan_checksum"]),
            )
            request = nfcore.approved_nfcore_execution_request(
                model, str(registered["plan_checksum"])
            )
        changed = json.loads(json.dumps(request.plan))
        changed["command_argv"] = [sys.executable, "-c", "raise SystemExit(9)"]

        with self.assertRaisesRegex(client.DaemonError, "approved checksum"):
            client.execute(request.model_copy(update={"plan": changed}))
        with self.assertRaisesRegex(client.DaemonError, "binding"):
            client.execute(request.model_copy(update={"binding": "snakemake"}))
        injected = request.model_dump(mode="json")
        injected["files"] = [
            {
                "kind": "write_json",
                "destination": str(self.workspace / "unauthorized.json"),
                "value": {"argv": [sys.executable, "-c", "raise SystemExit(9)"]},
            }
        ]
        with self.assertRaisesRegex(client.DaemonError, "Extra inputs"):
            client._request(client.ensure_daemon_running(), "/runs", injected)

        self.assertFalse((self.workspace / "ngs_runs").exists())
        self.assertFalse(registry_path().exists())

    def test_registered_plan_requires_one_single_use_native_approval_receipt(self) -> None:
        with (
            mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=_readiness()),
            mock.patch.object(
                nfcore,
                "build_nextflow_argv",
                return_value=[sys.executable, "-c", "import time; time.sleep(0.2)"],
            ),
        ):
            planned = nfcore.plan_remote_run(
                "fastq_qc",
                str(self.root / "execution" / "single-use"),
                "test,docker",
                run_id="nfcore-single-use-approval",
            )
            registered = plan_registry.register_plan("nextflow", planned)
            _, model = plan_registry.load_approved_plan(
                str(registered["plan_name"]),
                str(registered["plan_id"]),
                str(registered["plan_checksum"]),
            )
            request = nfcore.approved_nfcore_execution_request(
                model,
                str(registered["plan_checksum"]),
                refresh_runtime=False,
            )
        with self.assertRaisesRegex(client.DaemonError, "native approval"):
            client.execute(request)
        self.assertFalse((self.workspace / "ngs_runs").exists())

        with approved_execution._native_authorization(request) as authorized:
            tampered = authorized.model_copy(
                update={"metadata": {**authorized.metadata, "display_name": "changed"}}
            )
            with self.assertRaisesRegex(client.DaemonError, "authorization"):
                client.execute(tampered)
            accepted = client.execute(authorized)
            with self.assertRaisesRegex(client.DaemonError, "authorization"):
                client.execute(authorized)

        self.assertTrue(accepted["ok"])
        self._await_status(accepted["registry_run_id"], {"completed"})
        self.assertEqual(list((self.state_dir / "daemon").glob("authorization-*.json")), [])


if __name__ == "__main__":
    unittest.main()
