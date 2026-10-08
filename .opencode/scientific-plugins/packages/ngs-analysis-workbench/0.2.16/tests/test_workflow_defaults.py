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

from ngs_workbench_daemon.persistence import SqlAlchemyUnitOfWork, default_database  # noqa: E402
from ngs_workbench_daemon.persistence.workflows import (  # noqa: E402
    WorkflowEntryRecord,
    WorkflowRepository,
    WorkflowVersionRecord,
)
from ngs_workbench_mcp.workflows import defaults  # noqa: E402


def _manifest(revision: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "workflows": [
            {
                "workflow_id": "example",
                "name": "Example",
                "description": "Example remote workflow.",
                "engine": "nextflow",
                "source": {
                    "kind": "remote",
                    "workflow": "example/workflow",
                    "revision": revision,
                },
                "execution": {"parameter_contract": "generic"},
            }
        ],
    }


class WorkflowDefaultsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.environment = mock.patch.dict(
            os.environ,
            {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(self.root / "state")},
        )
        self.environment.start()

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary.cleanup()

    def _records(self) -> tuple[list[object], dict[str, list[object]]]:
        with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
            assert unit_of_work.session is not None
            repository = WorkflowRepository(unit_of_work.session)
            entries = repository.list_entries()
            versions = {entry.id: repository.list_versions(entry.id) for entry in entries}
        return entries, versions

    def test_installed_manifest_is_idempotent_and_globally_unique(self) -> None:
        self.assertEqual(defaults.bootstrap_default_workflows(), [])
        self.assertEqual(defaults.bootstrap_default_workflows(), [])

        entries, versions = self._records()
        self.assertEqual(len(entries), 12)
        self.assertEqual(len({entry.id for entry in entries}), 12)
        self.assertTrue(all(entry.owner == "bundled" for entry in entries))
        self.assertTrue(all(len(versions[entry.id]) == 1 for entry in entries))
        self.assertTrue(
            all(entry.current_version_id == versions[entry.id][0].id for entry in entries)
        )
        self.assertEqual(versions["fastq_qc"][0].execution, {"parameter_contract": "nf-core"})

    def test_upgrade_and_rollback_reuse_immutable_versions(self) -> None:
        path = self.root / "defaults.json"
        path.write_text(json.dumps(_manifest("1.0.0")), encoding="utf-8")
        defaults.bootstrap_default_workflows(path)
        first_entry = self._records()[0][0]

        path.write_text(json.dumps(_manifest("2.0.0")), encoding="utf-8")
        defaults.bootstrap_default_workflows(path)
        upgraded_entries, upgraded_versions = self._records()
        self.assertEqual(len(upgraded_versions["example"]), 2)
        self.assertNotEqual(upgraded_entries[0].current_version_id, first_entry.current_version_id)

        path.write_text(json.dumps(_manifest("1.0.0")), encoding="utf-8")
        defaults.bootstrap_default_workflows(path)
        rolled_back_entries, rolled_back_versions = self._records()
        self.assertEqual(len(rolled_back_versions["example"]), 2)
        self.assertEqual(rolled_back_entries[0].current_version_id, first_entry.current_version_id)

    def test_removed_bundled_entry_is_archived_and_restored(self) -> None:
        path = self.root / "defaults.json"
        path.write_text(json.dumps(_manifest("1.0.0")), encoding="utf-8")
        defaults.bootstrap_default_workflows(path)
        path.write_text(json.dumps({"schema_version": 1, "workflows": []}), encoding="utf-8")
        defaults.bootstrap_default_workflows(path)
        self.assertIsNotNone(self._records()[0][0].archived_at_ms)

        path.write_text(json.dumps(_manifest("1.0.0")), encoding="utf-8")
        defaults.bootstrap_default_workflows(path)
        self.assertIsNone(self._records()[0][0].archived_at_ms)
        self.assertEqual(len(self._records()[1]["example"]), 1)

    def test_user_owned_id_collision_is_preserved(self) -> None:
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
            assert unit_of_work.session is not None
            repository = WorkflowRepository(unit_of_work.session)
            repository.add_entry(
                WorkflowEntryRecord(
                    id="example",
                    name="User example",
                    engine="nextflow",
                    description=None,
                    metadata={},
                    owner="user",
                    current_version_id="user-version",
                    archived_at_ms=None,
                    created_at_ms=1,
                    updated_at_ms=1,
                )
            )
            repository.add_version(
                WorkflowVersionRecord(
                    id="user-version",
                    workflow_id="example",
                    source_kind="remote",
                    local_root=None,
                    entrypoint=None,
                    source_sha256=None,
                    remote_workflow="user/example",
                    revision="1.0.0",
                    execution={"parameter_contract": "generic"},
                    created_at_ms=1,
                )
            )
            unit_of_work.commit()
        path = self.root / "defaults.json"
        path.write_text(json.dumps(_manifest("1.0.0")), encoding="utf-8")

        self.assertEqual(
            defaults.bootstrap_default_workflows(path),
            ["default workflow 'example' conflicts with a user-owned entry"],
        )
        entry = self._records()[0][0]
        self.assertEqual(entry.name, "User example")
        self.assertEqual(entry.current_version_id, "user-version")


if __name__ == "__main__":
    unittest.main()
