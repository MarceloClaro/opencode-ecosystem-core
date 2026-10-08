from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

MCP_ROOT = Path(__file__).resolve().parents[1] / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from daemon_test_case import DaemonTestCase  # noqa: E402
from ngs_compute_mcp import __main__ as compute_mcp  # noqa: E402
from ngs_workbench_daemon import client, state  # noqa: E402
from ngs_workbench_daemon import inspection as daemon_inspection  # noqa: E402
from ngs_workbench_daemon.protocol import LOCAL_TARGET_PAYLOAD  # noqa: E402


class ComputeMcpTests(DaemonTestCase):
    def test_compute_targets_are_shared_private_durable_and_canonically_hashed(self) -> None:
        self.assertEqual(compute_mcp.list_compute_targets()["targets"], [LOCAL_TARGET_PAYLOAD])
        target = self._configure_ssh_target()
        listed = compute_mcp.list_compute_targets()["targets"]
        self.assertEqual(listed[0], LOCAL_TARGET_PAYLOAD)
        self.assertEqual(listed[1], target)
        self.assertEqual(target["executor_configuration"], {"partition": "cpu"})
        self.assertNotIn("proxycommand", target["host_access"])

        normalized = self._configure_ssh_target(workspace_root="/shared//ngs/")
        self.assertEqual(normalized["workspace_root"], "/shared/ngs")
        self.assertEqual(normalized["config_hash"], target["config_hash"])
        changed_root = self._configure_ssh_target(workspace_root="/other/ngs")
        self.assertNotEqual(changed_root["config_hash"], target["config_hash"])
        changed_partition = self._configure_ssh_target(partition="gpu")
        self.assertNotEqual(changed_partition["config_hash"], target["config_hash"])
        with self.assertRaisesRegex(ValueError, "executor configuration"):
            self._configure_ssh_target(account="research; unsafe")

        owner = self._crash_daemon()
        restarted = compute_mcp.list_compute_targets()
        self.assertEqual(restarted["count"], 2)
        self.assertNotEqual(client.ensure_daemon_running().instance_id, owner.instance_id)

        persisted = self.state_dir / "daemon" / "targets.json"
        self.assertEqual(persisted.stat().st_mode & 0o777, 0o600)
        self.assertNotIn(state.daemon_token(self.state_dir / "daemon"), persisted.read_text())

    def test_ssh_alias_is_passed_after_the_end_of_options(self) -> None:
        with mock.patch.object(
            daemon_inspection.subprocess, "run", wraps=subprocess.run
        ) as invocation:
            target = self._configure_ssh_target(ssh_alias="analyst@localhost")

        self.assertEqual(invocation.call_args.args[0][-2:], ["--", "analyst@localhost"])
        self.assertEqual(target["host_access"]["alias"], "analyst@localhost")
        with self.assertRaisesRegex(ValueError, "credentials") as rejected:
            self._configure_ssh_target(ssh_alias="analyst:CREDENTIAL_SENTINEL@localhost")
        self.assertNotIn("CREDENTIAL_SENTINEL", str(rejected.exception))
        with self.assertRaisesRegex(ValueError, "cannot resolve") as rejected:
            self._configure_ssh_target(ssh_alias="analyst:CREDENTIAL_SENTINEL@bad host")
        self.assertNotIn("CREDENTIAL_SENTINEL", str(rejected.exception))

    def test_compute_clients_cannot_launch_workflows_or_persist_secret_fields(self) -> None:
        endpoint = client.ensure_daemon_running()
        for operation in ("/runs", "/run", "/cancel"):
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(client.DaemonError, "scientific workflows"):
                    client._request(endpoint, operation, {}, role="compute")
        self.assertFalse((self.workspace / "ngs_runs").exists())
        with self.assertRaisesRegex(client.DaemonError, "only compute"):
            client._request(endpoint, "/targets/configure", {})

        secret = "PRIVATE-KEY-SENTINEL-NOT-PERSISTED"
        target = self._configure_ssh_target()
        injected = {
            **target,
            "host_access": {**target["host_access"], "private_key": secret},
        }
        with self.assertRaisesRegex(client.DaemonError, "unsupported") as rejected:
            client._request(endpoint, "/targets/configure", injected, role="compute")
        self.assertNotIn(secret, str(rejected.exception))
        self.assertNotIn(secret, (self.state_dir / "daemon" / "targets.json").read_text())

        forged = {**target, "host_access": {**target["host_access"], "host": "changed.example"}}
        with self.assertRaisesRegex(client.DaemonError, "identity"):
            client._request(endpoint, "/targets/configure", forged, role="compute")
