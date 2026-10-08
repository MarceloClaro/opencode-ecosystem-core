from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from ngs_workbench_mcp import approved_execution, plan_registry  # noqa: E402
from ngs_workbench_mcp.workflows import nextflow as nfcore  # noqa: E402

_plan_catalog_workflow = nfcore.plan_remote_run


def _plan_with_catalog_source(*args: object, **kwargs: object) -> dict[str, object]:
    kwargs.setdefault("workflow", "nf-core/demo")
    return _plan_catalog_workflow(*args, **kwargs)


nfcore.plan_remote_run = _plan_with_catalog_source


def ready() -> dict[str, object]:
    return {
        "ok": True,
        "status": "ready",
        "scope": "executable_presence_only",
        "commands": [
            {"name": "nextflow", "path": "/runtime/nextflow"},
            {"name": "docker", "path": "/runtime/docker"},
        ],
        "blockers": [],
        "docker": {
            "path": "/runtime/docker",
            "daemon_reachable": True,
            "server_os": "linux",
            "server_arch": "amd64",
        },
    }


class NativeApprovalTests(unittest.TestCase):
    def _registered_nfcore_plan(self, workspace: Path) -> dict[str, object]:
        with mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=ready()):
            plan = nfcore.plan_remote_run(
                "fastq_qc",
                str(workspace / "execution"),
                "test,docker",
                display_name="Public example FASTQ QC",
                revision="1.2.0",
                run_id="nfcore-fastq-qc-native-approval",
            )
        return plan_registry.register_plan("nextflow", plan)

    def test_plan_registration_is_immutable_and_has_no_workspace_effects(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            state_dir = root / "state"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(state_dir)},
            ):
                registered = self._registered_nfcore_plan(workspace)
                binding, loaded = plan_registry.load_approved_plan(
                    str(registered["plan_name"]),
                    str(registered["plan_id"]),
                    str(registered["plan_checksum"]),
                )

            self.assertEqual(binding, "nextflow")
            self.assertEqual(loaded.request.display_name, "Public example FASTQ QC")
            self.assertNotIn("approval_arguments", registered)
            self.assertNotIn("checksum", registered)
            self.assertEqual(
                registered["plan_id"],
                f"ngs-plan-{str(registered['plan_checksum']).removeprefix('sha256:')[:16]}",
            )
            self.assertFalse((workspace / "execution").exists())
            self.assertTrue((state_dir / "plans" / f"{registered['plan_id']}.json").is_file())

    def test_registered_plan_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            state_dir = root / "state"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(state_dir)},
            ):
                registered = self._registered_nfcore_plan(workspace)
                path = state_dir / "plans" / f"{registered['plan_id']}.json"
                record = json.loads(path.read_text(encoding="utf-8"))
                record["plan"]["request"]["profile"] = "test,singularity"
                path.write_text(json.dumps(record), encoding="utf-8")

                with self.assertRaisesRegex(ValueError, "approved checksum"):
                    plan_registry.load_approved_plan(
                        str(registered["plan_name"]),
                        str(registered["plan_id"]),
                        str(registered["plan_checksum"]),
                    )

    def test_execute_plan_rejects_unknown_identity_before_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary) / "state"
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(state_dir)},
            ):
                with mock.patch.object(approved_execution.daemon_client, "execute") as execute:
                    with self.assertRaisesRegex(ValueError, "unknown plan_id"):
                        approved_execution.execute_registered_plan(
                            "Unknown plan",
                            "ngs-plan-0123456789abcdef",
                            f"sha256:{'0' * 64}",
                        )
            execute.assert_not_called()

    def test_execute_plan_rejects_input_drift_before_workspace_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            state_dir = root / "state"
            workspace.mkdir()
            sample_sheet = workspace / "samplesheet.csv"
            sample_sheet.write_text(
                "sample,fastq_1\nS1,/data/r1.fastq.gz\n",
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(state_dir)},
            ):
                with mock.patch.object(nfcore, "assess_nfcore_readiness", return_value=ready()):
                    planned = nfcore.plan_remote_run(
                        "rnaseq",
                        str(workspace / "execution"),
                        "docker",
                        sample_sheet=str(sample_sheet),
                        revision="3.26.0",
                        run_id="nfcore-rnaseq-native-drift",
                    )
                    registered = plan_registry.register_plan("nextflow", planned)
                    sample_sheet.write_text(
                        "sample,fastq_1\nS2,/data/changed.fastq.gz\n",
                        encoding="utf-8",
                    )
                    with mock.patch.object(approved_execution.daemon_client, "execute") as execute:
                        result = approved_execution.execute_registered_plan(
                            str(registered["plan_name"]),
                            str(registered["plan_id"]),
                            str(registered["plan_checksum"]),
                        )

            self.assertFalse(result["ok"])
            self.assertIn("checksum", str(result["errors"][0]))
            execute.assert_not_called()
            self.assertFalse((workspace / "execution").exists())


if __name__ == "__main__":
    unittest.main()
