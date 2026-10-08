from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
import uuid
from dataclasses import replace
from pathlib import Path
from unittest import mock

from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from ngs_workbench_daemon.persistence import (  # noqa: E402
    NewRun,
    RunFilters,
    RunRecord,
    SqlAlchemyUnitOfWork,
    StaleRunRevision,
    default_database,
    ensure_workspace_identity,
)
from ngs_workbench_daemon.persistence import database as persistence_database  # noqa: E402
from ngs_workbench_daemon.persistence import paths as persistence_paths  # noqa: E402
from ngs_workbench_daemon.persistence.repository import RunConflict  # noqa: E402
from ngs_workbench_daemon.protocol import canonical_plan_checksum  # noqa: E402
from ngs_workbench_mcp import runs  # noqa: E402


def new_run(
    workspace: Path,
    workspace_id: str,
    run_id: str,
    binding: str,
    *,
    first_run_id: str | None = None,
    attempt_number: int = 1,
) -> NewRun:
    run_root = Path("ngs_runs") / binding / "fastq_qc" / run_id
    return NewRun(
        workspace_id=workspace_id,
        workspace_dir=workspace,
        external_run_id=run_id,
        first_run_id=first_run_id or run_id,
        attempt_number=attempt_number,
        binding=binding,
        pipeline="fastq_qc",
        workflow="example/workflow",
        plan_checksum="sha256:" + "0" * 64,
        request={"run_id": run_id},
        command_argv=["true"],
        run_relative_path=run_root.as_posix(),
        approved_plan_relative_path=(run_root / "workflow" / "approved_plan.json").as_posix(),
        launch_log_relative_path=(run_root / "logs" / "run.log").as_posix(),
    )


class RegistryRepositoryTests(unittest.TestCase):
    def test_workflow_entry_requires_an_existing_current_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(Path(temporary) / "state")},
            ):
                database = default_database()
                with database.engine.connect() as connection:
                    connection.exec_driver_sql(
                        "INSERT INTO workflows "
                        "(id, name, engine, description, metadata_json, owner, "
                        "current_version_id, archived_at_ms, created_at_ms, updated_at_ms) "
                        "VALUES ('broken', 'Broken', 'nextflow', NULL, '{}', 'user', "
                        "'missing-version', NULL, 1, 1)"
                    )
                    with self.assertRaises(IntegrityError):
                        connection.commit()

    def test_lineage_migration_preserves_runs_and_discards_retired_zip_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    created = unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "legacy-run", "nextflow")
                    )
                    unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "fallback-run", "snakemake")
                    )
                    unit_of_work.registry.transition_run(
                        created.id, "running", expected_revision=created.revision
                    )
                    unit_of_work.commit()
                config = Config()
                config.set_main_option("script_location", str(persistence_database.MIGRATIONS_DIR))
                with database.engine.connect() as connection:
                    config.attributes["connection"] = connection
                    command.downgrade(config, "0002_saved_workflows")
                    connection.exec_driver_sql(
                        "INSERT INTO workflows "
                        "(id, name, engine, entrypoint, description, metadata_json, "
                        "archive_sha256, source_run_id, created_at_ms, updated_at_ms) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            "saved-workflow",
                            "Saved workflow",
                            "nextflow",
                            "main.nf",
                            None,
                            "{}",
                            "sha256:" + "1" * 64,
                            created.id,
                            1,
                            1,
                        ),
                    )
                    connection.exec_driver_sql(
                        "UPDATE runs SET request_json = ? WHERE id = ?",
                        (json.dumps({"plan_request": {"run_id": "public-run"}}), created.id),
                    )
                    before = (
                        connection.exec_driver_sql("SELECT * FROM runs WHERE id = ?", (created.id,))
                        .mappings()
                        .one()
                    )
                    connection.commit()
                    for invalid_id in (None, "", 17, "public-run"):
                        with self.subTest(invalid_id=invalid_id):
                            connection.exec_driver_sql(
                                "UPDATE runs SET request_json = ? WHERE external_run_id = 'fallback-run'",
                                (json.dumps({"plan_request": {"run_id": invalid_id}}),),
                            )
                            snapshot = connection.exec_driver_sql(
                                "SELECT * FROM runs ORDER BY id"
                            ).all()
                            connection.commit()
                            with self.assertRaises(ValueError):
                                command.upgrade(config, "head")
                            self.assertEqual(
                                connection.exec_driver_sql("SELECT * FROM runs ORDER BY id").all(),
                                snapshot,
                            )
                            self.assertEqual(
                                connection.exec_driver_sql(
                                    "SELECT version_num FROM alembic_version"
                                ).scalar_one(),
                                "0002_saved_workflows",
                            )
                            connection.commit()
                    connection.exec_driver_sql(
                        "UPDATE runs SET request_json = '{}' WHERE external_run_id = 'fallback-run'"
                    )
                    connection.commit()
                    rebuilds = 0

                    def interrupt_rebuild(_conn, _cursor, statement, _parameters, _context, _many):
                        nonlocal rebuilds
                        if "CREATE TABLE _alembic_tmp_runs" in statement:
                            rebuilds += 1
                            if rebuilds == 2:
                                raise InterruptedError

                    event.listen(connection, "before_cursor_execute", interrupt_rebuild)
                    try:
                        with self.assertRaises(InterruptedError):
                            command.upgrade(config, "head")
                    finally:
                        event.remove(connection, "before_cursor_execute", interrupt_rebuild)
                    self.assertEqual(
                        connection.exec_driver_sql("SELECT * FROM runs WHERE id = ?", (created.id,))
                        .mappings()
                        .one(),
                        before,
                    )
                    connection.commit()
                    command.upgrade(config, "head")
                    row = (
                        connection.exec_driver_sql("SELECT * FROM runs WHERE id = ?", (created.id,))
                        .mappings()
                        .one()
                    )
                    event_count = connection.exec_driver_sql(
                        "SELECT COUNT(*) FROM run_events WHERE run_id = ?", (created.id,)
                    ).scalar_one()
                    workflow_count = connection.exec_driver_sql(
                        "SELECT COUNT(*) FROM workflows"
                    ).scalar_one()
                    self.assertEqual(
                        connection.exec_driver_sql(
                            "SELECT first_run_id, attempt_number FROM runs WHERE external_run_id = 'fallback-run'"
                        ).one(),
                        ("fallback-run", 1),
                    )
                    with self.assertRaises(IntegrityError):
                        connection.exec_driver_sql(
                            "INSERT INTO run_events (run_id, sequence, event_type, actor_type, details_json, created_at_ms) VALUES ('missing', 1, 'test', 'test', '{}', 1)"
                        )

                self.assertEqual(
                    dict(row),
                    {
                        **before,
                        "external_run_id": "public-run",
                        "first_run_id": "public-run",
                        "attempt_number": 1,
                    },
                )
                self.assertEqual(event_count, 2)
                self.assertEqual(workflow_count, 0)
                with SqlAlchemyUnitOfWork(database) as unit_of_work:
                    registry = unit_of_work.registry
                    self.assertEqual(registry.get_by_run_id("public-run").id, created.id)

    def test_workspace_identity_loser_reads_only_the_completed_winner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            identity_path = persistence_paths.workspace_identity_path(workspace)
            winner_id = str(uuid.uuid4())
            observed: dict[str, object] = {}

            def publish_winner(source: str, destination: str) -> None:
                source_path = Path(source)
                destination_path = Path(destination)
                observed["destination_existed"] = destination_path.exists()
                observed["candidate"] = json.loads(source_path.read_text(encoding="utf-8"))
                destination_path.write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "workspace_id": winner_id,
                            "created_at_ms": 1,
                        }
                    ),
                    encoding="utf-8",
                )
                raise FileExistsError

            with mock.patch.object(
                persistence_paths.os,
                "link",
                side_effect=publish_winner,
            ):
                identity = ensure_workspace_identity(workspace)

            self.assertEqual(identity, winner_id)
            self.assertFalse(observed["destination_existed"])
            self.assertIsInstance(observed["candidate"], dict)
            self.assertEqual(list(identity_path.parent.glob(".workspace.*.tmp")), [])

    def test_history_persists_and_filters_across_workspaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_dir = root / "state"
            first_workspace = root / "first"
            second_workspace = root / "second"
            first_workspace.mkdir()
            second_workspace.mkdir()
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(state_dir)},
            ):
                database = default_database()
                first_id = ensure_workspace_identity(first_workspace)
                second_id = ensure_workspace_identity(second_workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(first_id, first_workspace)
                    first = unit_of_work.registry.allocate_approved_run(
                        new_run(first_workspace, first_id, "run-one", "nextflow")
                    )
                    unit_of_work.registry.register_workspace(second_id, second_workspace)
                    unit_of_work.registry.allocate_approved_run(
                        new_run(second_workspace, second_id, "run-two", "snakemake")
                    )
                    unit_of_work.registry.transition_run(
                        first.id,
                        "running",
                        expected_revision=first.revision,
                        pid=1234,
                    )
                    unit_of_work.commit()

                with SqlAlchemyUnitOfWork(database) as unit_of_work:
                    assert unit_of_work.registry is not None
                    all_runs = unit_of_work.registry.list_runs(RunFilters())
                    nfcore_runs = unit_of_work.registry.list_runs(
                        RunFilters(binding="nextflow", statuses=("running",))
                    )

                self.assertEqual({run.external_run_id for run in all_runs}, {"run-one", "run-two"})
                self.assertEqual([run.external_run_id for run in nfcore_runs], ["run-one"])
                self.assertEqual(nfcore_runs[0].revision, 2)
                self.assertEqual(state_dir.stat().st_mode & 0o777, 0o700)
                self.assertEqual((state_dir / "registry.sqlite3").stat().st_mode & 0o777, 0o600)
                self.assertEqual(
                    (state_dir / "registry.sqlite3.migrate.lock").stat().st_mode & 0o777,
                    0o600,
                )
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    with self.assertRaises(RunConflict):
                        unit_of_work.registry.allocate_approved_run(
                            new_run(second_workspace, second_id, "run-one", "snakemake")
                        )

    def test_recovery_lineage_uses_the_first_run_and_a_new_execution_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "historical-workspace"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                request = {
                    "run_id": "first",
                    "pipeline": "fastq_qc",
                    "workflow": "example/workflow",
                    "run_dir": str(root / "first-execution"),
                }
                first_payload = runs.bind_run_lineage(
                    {"ok": True, "request": dict(request)}, "nextflow", None
                )
                workspace_id = ensure_workspace_identity(workspace)
                first_request = new_run(workspace, workspace_id, "first", "nextflow")
                first_request.request["plan_request"] = first_payload["request"]
                with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    first = unit_of_work.registry.allocate_approved_run(first_request)
                    first = unit_of_work.registry.transition_run(
                        first.id, "running", expected_revision=first.revision
                    )
                    unit_of_work.registry.transition_run(
                        first.id, "failed", expected_revision=first.revision
                    )
                    unit_of_work.commit()

                request["run_id"] = "second"
                request["run_dir"] = str(root / "second-execution")
                self.assertEqual(first.summary()["run_id"], "first")
                recovery_id = first.summary()["first_run_id"]
                rerun_payload = runs.bind_run_lineage(
                    {"ok": True, "request": dict(request)}, "nextflow", recovery_id
                )
                with self.assertRaisesRegex(ValueError, "different workflow"):
                    runs.bind_run_lineage(
                        {"ok": True, "request": dict(request)}, "snakemake", recovery_id
                    )
                with self.assertRaisesRegex(ValueError, "different workflow"):
                    runs.bind_run_lineage(
                        {
                            "ok": True,
                            "request": {
                                **request,
                                "workflow": "other/workflow",
                            },
                        },
                        "nextflow",
                        recovery_id,
                    )

            self.assertEqual(first_payload["request"]["first_run_id"], "first")
            self.assertEqual(first_payload["request"]["attempt_number"], 1)
            self.assertEqual(rerun_payload["request"]["run_id"], "second")
            self.assertEqual(rerun_payload["request"]["first_run_id"], "first")
            self.assertEqual(rerun_payload["request"]["attempt_number"], 2)

    def test_completed_history_does_not_start_or_reconcile_a_daemon(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                workspace_id = ensure_workspace_identity(workspace)
                active = new_run(workspace, workspace_id, "active", "nextflow")
                active.request.update(
                    {"daemon_instance_id": "previous-owner", "target": {"target_id": "local"}}
                )
                with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    completed = unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "completed", "nextflow")
                    )
                    completed = unit_of_work.registry.transition_run(
                        completed.id, "running", expected_revision=completed.revision
                    )
                    unit_of_work.registry.transition_run(
                        completed.id, "completed", expected_revision=completed.revision
                    )
                    active_record = unit_of_work.registry.allocate_approved_run(active)
                    unit_of_work.commit()

                for status, expected in (("completed", ["completed"]), ("orphaned", [])):
                    with (
                        self.subTest(status=status),
                        mock.patch.object(runs.daemon_client, "healthy_daemon") as healthy,
                        mock.patch.object(runs.daemon_client, "ensure_daemon_running") as start,
                    ):
                        history = runs.list_registry_runs(statuses=[status])
                        self.assertEqual([record["run_id"] for record in history["runs"]], expected)
                        healthy.assert_not_called()
                        start.assert_not_called()
                with (
                    mock.patch.object(runs.daemon_client, "healthy_daemon") as healthy,
                    mock.patch.object(runs.daemon_client, "ensure_daemon_running") as start,
                ):
                    lineage = runs.list_registry_runs(first_run_id="completed")
                    self.assertEqual(
                        [record["run_id"] for record in lineage["runs"]], ["completed"]
                    )
                    healthy.assert_not_called()
                    start.assert_not_called()
                with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unchanged = unit_of_work.registry.get_run(active_record.id)
                self.assertIsNotNone(unchanged)
                self.assertEqual(unchanged.status, "starting")

    def test_recent_lineage_limit_is_not_consumed_by_attempt_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    for run_id in ("lineage-a", "lineage-b", "lineage-c"):
                        unit_of_work.registry.allocate_approved_run(
                            new_run(workspace, workspace_id, run_id, "nextflow")
                        )
                    storage = root / "state"
                    storage_id = ensure_workspace_identity(storage)
                    unit_of_work.registry.register_workspace(storage_id, storage)
                    for attempt_number in range(2, 9):
                        unit_of_work.registry.allocate_approved_run(
                            new_run(
                                storage,
                                storage_id,
                                f"lineage-c-{attempt_number}",
                                "nextflow",
                                first_run_id="lineage-c",
                                attempt_number=attempt_number,
                            )
                        )
                    recent = unit_of_work.registry.list_recent_lineages(lineage_limit=2)

            self.assertEqual({run.first_run_id for run in recent}, {"lineage-b", "lineage-c"})
            self.assertEqual(
                [run.attempt_number for run in recent if run.first_run_id == "lineage-c"],
                [3, 4, 5, 6, 7, 8],
            )

    def test_migration_lock_times_out_when_held(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "registry.sqlite3"
            lock_path = Path(f"{database_path}.migrate.lock")
            held_lock = persistence_database.FileLock(
                lock_path,
                mode=0o600,
                preserve_lock_file=True,
            )
            with held_lock:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "timed out waiting for registry migration lock",
                ):
                    with persistence_database._migration_lock(
                        database_path,
                        timeout_seconds=0.5,
                    ):
                        self.fail("lock should not be acquired")

    def test_revision_guard_rejects_a_stale_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    created = unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "run-stale", "nextflow")
                    )
                    unit_of_work.registry.transition_run(
                        created.id,
                        "running",
                        expected_revision=created.revision,
                    )
                    unit_of_work.commit()

                with self.assertRaises(StaleRunRevision):
                    with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                        assert unit_of_work.registry is not None
                        unit_of_work.registry.transition_run(
                            created.id,
                            "failed",
                            expected_revision=created.revision,
                        )


class RunRegistryIntegrationTests(unittest.TestCase):
    def _register_historical_run(
        self, workspace: Path, request: dict[str, object], *, pid: int | None = None
    ) -> RunRecord:
        workspace_id = ensure_workspace_identity(workspace)
        run_id = str(request["run_id"])
        candidate = replace(
            new_run(workspace, workspace_id, run_id, "nextflow"),
            workflow=str(request["workflow"]),
            plan_checksum=str(request["plan_checksum"]),
            request=request,
        )
        with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
            assert unit_of_work.registry is not None
            unit_of_work.registry.register_workspace(workspace_id, workspace)
            created = unit_of_work.registry.allocate_approved_run(candidate)
            running = unit_of_work.registry.transition_run(
                created.id, "running", expected_revision=created.revision, pid=pid
            )
            unit_of_work.commit()
        return running

    def test_history_reads_versioned_metadata_from_approved_plan_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            run_id = "run-with-plan-metadata"
            plan_path = (
                workspace
                / "ngs_runs"
                / "nextflow"
                / "fastq_qc"
                / run_id
                / "workflow"
                / "approved_plan.json"
            )
            plan_path.parent.mkdir(parents=True)
            plan = {
                "schema_version": 2,
                "request": {
                    "display_name": "PBMC FASTQ intake",
                    "target": {
                        "target_id": "local",
                        "provider": "ngs-analysis-workbench",
                    },
                    "profile": "test,docker",
                    "revision": "1.2.0",
                },
                "input_summary": {
                    "source": "workflow_test_profile",
                    "sample_count": None,
                },
                "readiness": {},
                "runtime": {"scope": "local", "commands": []},
            }
            checksum = canonical_plan_checksum(plan)
            plan_path.write_text(
                json.dumps({"plan_checksum": checksum, **plan}),
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    unit_of_work.registry.allocate_approved_run(
                        replace(
                            new_run(workspace, workspace_id, run_id, "nextflow"),
                            plan_checksum=checksum,
                        )
                    )
                    unit_of_work.commit()

                summary = runs.list_registry_runs(limit=1)["runs"][0]

            self.assertEqual(summary["metadata_schema_version"], 2)
            self.assertEqual(summary["display_name"], "PBMC FASTQ intake")
            self.assertEqual(summary["profile"], "test,docker")
            self.assertEqual(summary["workflow_revision"], "1.2.0")
            self.assertEqual(
                summary["target"],
                {"target_id": "local", "provider": "ngs-analysis-workbench"},
            )
            self.assertEqual(summary["input_summary"]["source"], "workflow_test_profile")
            self.assertEqual(summary["runtime_summary"]["scope"], "local")

    def test_history_ignores_invalid_metadata_schema_versions(self) -> None:
        record = mock.Mock(
            id=str(uuid.uuid4()),
            request={"schema_version": 3},
            workflow="example/workflow",
        )

        indexed_fallback = runs._run_metadata(
            record,
            {"schema_version": "not-an-integer", "request": {}},
        )
        default_fallback = runs._run_metadata(
            mock.Mock(
                id=str(uuid.uuid4()),
                request={"schema_version": False},
                workflow="example/workflow",
            ),
            {"schema_version": [2], "request": {}},
        )

        self.assertEqual(indexed_fallback["metadata_schema_version"], 3)
        self.assertEqual(default_fallback["metadata_schema_version"], 1)

    def test_lineage_comes_from_the_registry_row_not_workspace_plan(self) -> None:
        record = mock.Mock(
            id=str(uuid.uuid4()),
            request={},
            workflow="example/workflow",
            first_run_id="first",
            attempt_number=2,
        )
        metadata = runs._run_metadata(
            record, {"request": {"first_run_id": "forged", "attempt_number": 9}}
        )
        self.assertEqual(metadata["first_run_id"], "first")
        self.assertEqual(metadata["attempt_number"], 2)

    def test_historical_completion_remains_visible_from_durable_registry_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            run_dir = workspace / "ngs_runs" / "nextflow" / "fastq_qc" / "run-persisted"
            run_dir.mkdir(parents=True)
            (run_dir / "results").mkdir()
            (run_dir / "results" / "counts.tsv").write_text("gene\tsample\n", encoding="utf-8")
            scientific_takeaway = (
                "For treatment-response comparison, input reads support "
                "downstream quantification after duplication review."
            )
            (run_dir / "analysis_summary.md").write_text(
                f"# Scientific analysis summary\n\nTakeaway: {scientific_takeaway}\n\n"
                "This treatment-response analysis assessed whether the input libraries "
                "support downstream quantification. Duplication requires review.\n\n"
                "## Limitations\nDifferential expression was not performed.\n",
                encoding="utf-8",
            )
            record = {
                "run_id": "run-persisted",
                "pipeline": "fastq_qc",
                "workflow": "nf-core/demo",
                "status": "running",
                "workspace_dir": str(workspace),
                "run_dir": str(run_dir),
                "plan_checksum": "sha256:" + "1" * 64,
            }
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                registered = self._register_historical_run(workspace, record, pid=4321)
                history = runs.list_registry_runs(binding="nextflow")
                self.assertEqual(history["runs"][0]["status"], "running")
                self.assertEqual(
                    history["runs"][0]["analysis_summary"],
                    f"Running: {scientific_takeaway}",
                )
                running = runs.get_registry_run(registered.id)
                self.assertEqual(running["status"], "running")
                self.assertIn("This treatment-response analysis", running["analysis_summary"])
                self.assertNotIn("Takeaway:", running["analysis_summary"])
                self.assertNotIn("result", running)
                self.assertFalse(
                    (
                        workspace / "ngs_runs" / "nextflow" / ".mcp" / "runs" / "run-persisted.json"
                    ).exists()
                )

                with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.transition_run(
                        registered.id,
                        "completed",
                        expected_revision=registered.revision,
                        return_code=0,
                    )
                    unit_of_work.commit()
                completed = runs.get_registry_run(registered.id)
                completed_report = runs.get_registry_run_report(registered.id)["report"]
                self.assertEqual(completed["status"], "completed")
                self.assertEqual(completed["plan_checksum"], record["plan_checksum"])
                self.assertIn("registry_run_id", completed)
                self.assertEqual(completed_report["artifact_count"], 1)
                self.assertEqual(completed_report["entries"][0]["path"], "results/counts.tsv")
                self.assertIn(
                    "This treatment-response analysis",
                    completed_report["summary"],
                )
                self.assertIn(
                    {"label": "Scientific analysis", "path": "analysis_summary.md"},
                    completed_report["sources"],
                )

                completed_history = runs.list_registry_runs(binding="nextflow")
                self.assertEqual(
                    completed_history["runs"][0]["analysis_summary"],
                    scientific_takeaway,
                )

                restored = runs.get_registry_run(registered.id)
                restored_report = runs.get_registry_run_report(registered.id)["report"]
                self.assertEqual(restored["status"], "completed")
                self.assertEqual(restored["registry_run_id"], completed["registry_run_id"])
                self.assertEqual(restored_report, completed_report)

    def test_non_owner_query_does_not_orphan_an_active_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            run_dir = workspace / "ngs_runs" / "nextflow" / "fastq_qc" / "run-orphaned"
            run_dir.mkdir(parents=True)
            record = {
                "run_id": "run-orphaned",
                "pipeline": "fastq_qc",
                "workflow": "nf-core/demo",
                "status": "running",
                "workspace_dir": str(workspace),
                "run_dir": str(run_dir),
                "plan_checksum": "sha256:" + "2" * 64,
            }
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                registered = self._register_historical_run(workspace, record, pid=4321)
                result = runs.get_registry_run(registered.id)

            self.assertEqual(result["status"], "running")
            self.assertEqual(result["revision"], 2)
            self.assertNotIn("process_owned", result)

    def test_historical_status_uses_the_updated_registry_storage_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original_workspace = root / "original"
            moved_workspace = root / "moved"
            original_workspace.mkdir()
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(original_workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, original_workspace)
                    created = unit_of_work.registry.allocate_approved_run(
                        new_run(original_workspace, workspace_id, "run-moved", "nextflow")
                    )
                    unit_of_work.registry.transition_run(
                        created.id,
                        "running",
                        expected_revision=created.revision,
                    )
                    unit_of_work.commit()

                original_workspace.rename(moved_workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    unit_of_work.registry.register_workspace(workspace_id, moved_workspace)
                    unit_of_work.commit()
                result = runs.get_registry_run(created.id)
                with SqlAlchemyUnitOfWork(database) as unit_of_work:
                    assert unit_of_work.registry is not None
                    refreshed = unit_of_work.registry.get_run(created.id)

            assert refreshed is not None
            self.assertEqual(result["status"], "running")
            self.assertEqual(
                result["run_dir"],
                str(moved_workspace.resolve() / "ngs_runs" / "nextflow" / "fastq_qc" / "run-moved"),
            )
            self.assertEqual(refreshed.workspace_dir, str(moved_workspace.resolve()))
            self.assertEqual(result["analysis_summary"], "")
            self.assertNotIn("result", result)

    def test_global_detail_keeps_durable_state_when_storage_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = str(uuid.uuid4())
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    created = unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "run-missing", "nextflow")
                    )
                    unit_of_work.commit()

                workspace.rmdir()
                detail = runs.get_registry_run(created.id)
                [summary] = runs.list_registry_runs(binding="nextflow")["runs"]

            self.assertTrue(detail["ok"])
            self.assertEqual(detail["status"], summary["status"])
            self.assertEqual(detail["registry_run_id"], created.id)
            self.assertEqual(detail["analysis_summary"], "")
            self.assertEqual(summary["analysis_summary"], "")
            self.assertFalse(workspace.exists())

    def test_failed_prelaunch_without_run_directory_uses_only_durable_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    requested = new_run(
                        workspace,
                        workspace_id,
                        "run-blocked-before-launch",
                        "nextflow",
                    )
                    requested.request["objective"] = {
                        "scientific_question": "Can treated PBMC libraries support immune profiling?"
                    }
                    created = unit_of_work.registry.allocate_approved_run(requested)
                    failed = unit_of_work.registry.transition_run(
                        created.id,
                        "failed",
                        expected_revision=created.revision,
                        failure_summary="Docker daemon is unreachable",
                    )
                    unit_of_work.commit()

                detail = runs.get_registry_run(failed.id)
                [summary] = runs.list_registry_runs(binding="nextflow")["runs"]

            self.assertTrue(detail["ok"])
            self.assertEqual(detail["status"], "failed")
            self.assertEqual(detail["failure_summary"], "Docker daemon is unreachable")
            self.assertEqual(detail["analysis_summary"], "")
            self.assertEqual(summary["analysis_summary"], "")
            self.assertEqual(summary["failure_summary"], "Docker daemon is unreachable")
            self.assertNotIn("result", detail)
            self.assertFalse(Path(failed.run_dir).exists())

    def test_missing_completed_workspace_preserves_recorded_status_without_qc_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            run_dir = workspace / "ngs_runs" / "nextflow" / "fastq_qc" / "run-finished-missing"
            run_dir.mkdir(parents=True)
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    created = unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "run-finished-missing", "nextflow")
                    )
                    running = unit_of_work.registry.transition_run(
                        created.id,
                        "running",
                        expected_revision=created.revision,
                    )
                    completed = unit_of_work.registry.transition_run(
                        running.id,
                        "completed",
                        expected_revision=running.revision,
                    )
                    unit_of_work.commit()

                shutil.rmtree(workspace)
                detail = runs.get_registry_run(completed.id)
                report = runs.get_registry_run_report(completed.id)
                [history] = runs.list_registry_runs(binding="nextflow")["runs"]

            self.assertTrue(detail["ok"])
            self.assertEqual(detail["status"], "completed")
            self.assertEqual(detail["analysis_summary"], "")
            self.assertEqual(history["status"], "completed")
            self.assertEqual(history["analysis_summary"], "")
            self.assertNotIn("result", detail)
            self.assertEqual(report["availability"], "missing")
            self.assertIsNone(report["report"])

    def test_completed_run_remains_terminal_before_and_after_agent_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            run_dir = workspace / "ngs_runs" / "nextflow" / "fastq_qc" / "run-pending-summary"
            run_dir.mkdir(parents=True)
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    created = unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "run-pending-summary", "nextflow")
                    )
                    running = unit_of_work.registry.transition_run(
                        created.id,
                        "running",
                        expected_revision=created.revision,
                    )
                    completed = unit_of_work.registry.transition_run(
                        running.id,
                        "completed",
                        expected_revision=running.revision,
                    )
                    unit_of_work.commit()

                detail = runs.get_registry_run(completed.id)
                report = runs.get_registry_run_report(completed.id)
                [history] = runs.list_registry_runs(binding="nextflow")["runs"]

                takeaway = (
                    "FastQC of paired SRR6357072: high-quality reads; review "
                    "duplication and sequence-content warnings."
                )
                (run_dir / "analysis_summary.md").write_text(
                    f"Takeaway: {takeaway}\n\n"
                    "Both mates passed base-quality and adapter screening. "
                    "Review elevated duplication before downstream analysis.\n",
                    encoding="utf-8",
                )
                recovered = runs.get_registry_run(completed.id)
                recovered_report = runs.get_registry_run_report(completed.id)
                [recovered_history] = runs.list_registry_runs(binding="nextflow")["runs"]

            self.assertEqual(detail["status"], "completed")
            self.assertEqual(detail["analysis_summary"], "")
            self.assertEqual(history["analysis_summary"], "")
            self.assertEqual(report["report"]["summary"], "")
            self.assertEqual(recovered["status"], "completed")
            self.assertEqual(recovered["revision"], detail["revision"])
            self.assertIn("passed base-quality", recovered["analysis_summary"])
            self.assertIn("passed base-quality", recovered_report["report"]["summary"])
            self.assertEqual(recovered_history["analysis_summary"], takeaway)

    def test_failed_partial_review_persists_across_registry_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            run_dir = workspace / "ngs_runs" / "snakemake" / "fastq_qc" / "run-partial"
            (run_dir / "fastqc").mkdir(parents=True)
            (run_dir / "fastqc" / "sample_fastqc.html").write_text(
                "<html>partial QC</html>",
                encoding="utf-8",
            )
            takeaway = (
                "The lung inflammation comparison failed after FastQC; quantification "
                "did not run because the Salmon index was unavailable."
            )
            (run_dir / "analysis_summary.md").write_text(
                f"# Scientific analysis summary\n\n{takeaway} "
                "No differential expression or biological conclusion is supported.\n\n"
                "## Limitations\nAdditional reference details remain available in the full review.\n"
                "## Recommended next step\nVerify the approved reference index.\n",
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
            ):
                database = default_database()
                workspace_id = ensure_workspace_identity(workspace)
                with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                    assert unit_of_work.registry is not None
                    unit_of_work.registry.register_workspace(workspace_id, workspace)
                    created = unit_of_work.registry.allocate_approved_run(
                        new_run(workspace, workspace_id, "run-partial", "snakemake")
                    )
                    running = unit_of_work.registry.transition_run(
                        created.id,
                        "running",
                        expected_revision=created.revision,
                        pid=2345,
                    )
                    failed = unit_of_work.registry.transition_run(
                        running.id,
                        "failed",
                        expected_revision=running.revision,
                        return_code=1,
                        failure_summary="Salmon index is unavailable",
                    )
                    unit_of_work.commit()

                first = runs.get_registry_run(failed.id)
                reopened = runs.get_registry_run(failed.id)
                [history] = runs.list_registry_runs(binding="snakemake")["runs"]

            self.assertEqual(first["status"], "failed")
            self.assertIn(takeaway, first["analysis_summary"])
            self.assertIn("No differential expression", first["analysis_summary"])
            self.assertEqual(reopened["analysis_summary"], first["analysis_summary"])
            self.assertTrue(
                history["analysis_summary"].startswith(
                    "Failed: FastQC on lung inflammation comparison"
                )
            )
            self.assertIn("Salmon index was unavailable", history["analysis_summary"])
            self.assertLessEqual(len(history["analysis_summary"]), 125)
            self.assertEqual(history["failure_summary"], "Salmon index is unavailable")
            self.assertNotIn("result", first)

    def test_existing_canceled_and_orphaned_runs_remain_evidence_bounded(self) -> None:
        for final_status in ("canceled", "orphaned"):
            with self.subTest(status=final_status), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                workspace = root / "workspace"
                run_dir = workspace / "ngs_runs" / "nextflow" / "fastq_qc" / f"run-{final_status}"
                (run_dir / "fastqc").mkdir(parents=True)
                (run_dir / "fastqc" / "partial.html").write_text("partial", encoding="utf-8")
                with mock.patch.dict(
                    os.environ,
                    {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")},
                ):
                    database = default_database()
                    workspace_id = ensure_workspace_identity(workspace)
                    with SqlAlchemyUnitOfWork(database, immediate=True) as unit_of_work:
                        assert unit_of_work.registry is not None
                        unit_of_work.registry.register_workspace(workspace_id, workspace)
                        created = unit_of_work.registry.allocate_approved_run(
                            new_run(workspace, workspace_id, f"run-{final_status}", "nextflow")
                        )
                        running = unit_of_work.registry.transition_run(
                            created.id,
                            "running",
                            expected_revision=created.revision,
                        )
                        if final_status == "canceled":
                            running = unit_of_work.registry.transition_run(
                                running.id,
                                "cancel_requested",
                                expected_revision=running.revision,
                            )
                        terminal = unit_of_work.registry.transition_run(
                            running.id,
                            final_status,
                            expected_revision=running.revision,
                        )
                        unit_of_work.commit()

                    detail = runs.get_registry_run(terminal.id)
                    [history] = runs.list_registry_runs(binding="nextflow")["runs"]

                self.assertEqual(detail["status"], final_status)
                self.assertEqual(detail["analysis_summary"], "")
                self.assertEqual(history["status"], final_status)
                self.assertEqual(history["analysis_summary"], "")
                self.assertNotIn("result", detail)


if __name__ == "__main__":
    unittest.main()
