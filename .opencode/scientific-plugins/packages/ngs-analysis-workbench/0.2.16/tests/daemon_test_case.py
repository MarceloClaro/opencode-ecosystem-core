from __future__ import annotations

import json
import os
import signal
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from ngs_workbench_daemon import client, state


class DaemonTestCase(unittest.TestCase):
    def _configure_ssh_target(self, **overrides: object) -> dict[str, object]:
        from ngs_compute_mcp import __main__ as compute_mcp

        return compute_mcp.configure_ssh_target(
            **{
                "target_id": "lab",
                "title": "Lab host",
                "ssh_alias": "localhost",
                "workspace_root": "/shared/ngs",
                "executor": "slurm",
                "partition": "cpu",
                **overrides,
            }
        )

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.state_dir = self.root / "state"
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.environment = mock.patch.dict(
            os.environ,
            {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(self.state_dir)},
        )
        self.environment.start()

    def tearDown(self) -> None:
        shared = self.state_dir / "daemon"
        endpoint_paths = [shared / "endpoint.json", *shared.glob("runtimes/*/endpoint.json")]
        endpoints = []
        for endpoint_path in endpoint_paths:
            if not endpoint_path.is_file():
                continue
            endpoint = json.loads(endpoint_path.read_text(encoding="utf-8"))
            endpoints.append((endpoint_path.parent, int(endpoint["pid"])))
            try:
                os.kill(int(endpoint["pid"]), signal.SIGTERM)
            except ProcessLookupError:
                pass
        for directory, _ in endpoints:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and client._owner_is_held(directory):
                time.sleep(0.025)
        process = client._SPAWNED_DAEMON
        if process is not None and (
            process.poll() is not None or any(process.pid == pid for _, pid in endpoints)
        ):
            process.wait(timeout=5)
        self.environment.stop()
        self.temporary.cleanup()

    def _crash_daemon(self) -> client.DaemonEndpoint:
        endpoint = client.ensure_daemon_running()
        directory = state.daemon_runtime_directory(client.IMPLEMENTATION_ID)
        daemon_pid = int(
            json.loads((directory / "endpoint.json").read_text(encoding="utf-8"))["pid"]
        )
        os.kill(daemon_pid, signal.SIGKILL)
        deadline = time.monotonic() + 5
        while client._owner_is_held(directory):
            if time.monotonic() > deadline:
                self.fail("crashed daemon did not release its owner lock")
            time.sleep(0.025)
        process = client._SPAWNED_DAEMON
        if process is not None and process.pid == daemon_pid:
            process.wait(timeout=5)
        return endpoint
