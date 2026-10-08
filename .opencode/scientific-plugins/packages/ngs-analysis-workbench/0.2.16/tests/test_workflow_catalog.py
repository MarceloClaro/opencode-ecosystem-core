from __future__ import annotations

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

from ngs_workbench_mcp.workflows import catalog_store, defaults  # noqa: E402
from ngs_workbench_mcp.workflows.resolution import resolve_workflow  # noqa: E402
from ngs_workbench_mcp.workflows.source import observe_source  # noqa: E402


class WorkflowCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.environment = mock.patch.dict(
            os.environ,
            {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(self.root / "state")},
        )
        self.environment.start()
        defaults.bootstrap_default_workflows()
        self.source_root = self.root / "workflow"
        self.source_root.mkdir()
        (self.source_root / "Snakefile").write_text("rule all:\n    input: []\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary.cleanup()

    def _local_source(self) -> catalog_store.LocalWorkflowSource:
        return catalog_store.LocalWorkflowSource(
            kind="local", root=str(self.source_root), entrypoint="Snakefile"
        )

    def test_save_and_list_share_one_descriptor(self) -> None:
        saved = catalog_store.save_workflow(
            "my_qc",
            "My QC",
            "snakemake",
            self._local_source(),
            "A selected local workflow.",
        )

        listed = next(
            item
            for item in catalog_store.list_workflows("snakemake")["workflows"]
            if item["workflow_id"] == "my_qc"
        )
        self.assertEqual(saved, listed)
        self.assertNotEqual(saved["source"]["root"], str(self.source_root.resolve()))
        self.assertEqual(
            (Path(saved["source"]["root"]) / "Snakefile").read_text(encoding="utf-8"),
            "rule all:\n    input: []\n",
        )

    def test_update_creates_versions_and_activation_rolls_back(self) -> None:
        first = catalog_store.save_workflow("my_qc", "My QC", "snakemake", self._local_source())
        (self.source_root / "Snakefile").write_text(
            "rule changed:\n    input: []\n", encoding="utf-8"
        )
        second = catalog_store.update_workflow("my_qc", self._local_source())

        history = catalog_store.list_workflow_versions("my_qc")
        self.assertEqual(len(history["versions"]), 2)
        self.assertNotEqual(first["current_version_id"], second["current_version_id"])
        restored = catalog_store.activate_workflow_version("my_qc", first["current_version_id"])
        self.assertEqual(restored["current_version_id"], first["current_version_id"])
        self.assertEqual(len(catalog_store.list_workflow_versions("my_qc")["versions"]), 2)
        source = resolve_workflow("my_qc", "snakemake").local_execution_source()
        assert source is not None
        observed = observe_source(source)
        self.assertEqual(
            (Path(observed.root) / "Snakefile").read_text(encoding="utf-8"),
            "rule all:\n    input: []\n",
        )

    def test_archive_hides_without_deleting_and_restore_reveals(self) -> None:
        saved = catalog_store.save_workflow("my_qc", "My QC", "snakemake", self._local_source())
        archived = catalog_store.archive_workflow("my_qc")
        self.assertTrue(archived["archived"])
        self.assertFalse(
            any(
                item["workflow_id"] == "my_qc"
                for item in catalog_store.list_workflows()["workflows"]
            )
        )
        self.assertEqual(len(catalog_store.list_workflow_versions("my_qc")["versions"]), 1)
        self.assertTrue(
            any(
                item["workflow_id"] == "my_qc"
                for item in catalog_store.list_workflows(include_archived=True)["workflows"]
            )
        )

        restored = catalog_store.restore_workflow("my_qc")
        self.assertFalse(restored["archived"])
        self.assertEqual(restored["current_version_id"], saved["current_version_id"])

    def test_source_and_ownership_rules_are_enforced(self) -> None:
        remote = catalog_store.RemoteWorkflowSource(
            kind="remote", workflow="community/example", revision="1.0.0"
        )
        with self.assertRaises(ValueError):
            catalog_store.save_workflow("remote_smk", "Remote", "snakemake", remote)
        with self.assertRaises(ValueError):
            catalog_store.save_workflow(
                "unpinned",
                "Unpinned",
                "nextflow",
                catalog_store.RemoteWorkflowSource(
                    kind="remote", workflow="community/example", revision="   "
                ),
            )
        for workflow, revision in (("-resume", "1.0.0"), ("community/example", "-latest")):
            with self.subTest(workflow=workflow, revision=revision), self.assertRaises(ValueError):
                catalog_store.save_workflow(
                    "unsafe_remote",
                    "Unsafe",
                    "nextflow",
                    catalog_store.RemoteWorkflowSource(
                        kind="remote", workflow=workflow, revision=revision
                    ),
                )
        nested_source = self.root / "state" / "workflow-catalog" / "nested"
        nested_source.mkdir(parents=True)
        (nested_source / "Snakefile").write_text("rule all:\n    input: []\n")
        with self.assertRaises(ValueError):
            catalog_store.save_workflow(
                "overlap",
                "Overlap",
                "snakemake",
                catalog_store.LocalWorkflowSource(
                    kind="local", root=str(nested_source), entrypoint="Snakefile"
                ),
            )
        with self.assertRaises(ValueError):
            catalog_store.update_workflow("rnaseq", remote)
        with self.assertRaises(ValueError):
            catalog_store.archive_workflow("rnaseq")


if __name__ == "__main__":
    unittest.main()
