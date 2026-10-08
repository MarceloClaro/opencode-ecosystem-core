from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from daemon_test_case import DaemonTestCase  # noqa: E402
from ngs_workbench_daemon import client as daemon_client  # noqa: E402
from ngs_workbench_mcp import (  # noqa: E402
    app,
    approved_execution,
    plan_registry,
    preparation,
    runs,
)
from ngs_workbench_mcp.plans import SnakemakeRunPlan, plan_checksum  # noqa: E402
from ngs_workbench_mcp.workflows import catalog_store, defaults, snakemake  # noqa: E402
from ngs_workbench_mcp.workflows.source import WorkflowSource  # noqa: E402
from test_nextflow_mcp import target_input_transport  # noqa: E402

READINESS = {
    "ok": True,
    "status": "ready",
    "scope": "executable_presence_only",
    "commands": [{"name": "snakemake", "path": "/runtime/snakemake"}],
    "blockers": [],
}


def _plan_checksum(payload: dict[str, object]) -> str:
    return plan_checksum(SnakemakeRunPlan.model_validate(payload))


def _observed_readiness(observation: int) -> dict[str, object]:
    identity = f"{observation:032x}"
    snapshot_id = f"runtime-{identity}"
    return {
        **READINESS,
        "readiness_id": f"readiness-{identity}",
        "snapshot_id": snapshot_id,
        "observed_at": f"2026-08-06T00:0{observation}:00Z",
        "expires_at": f"2026-08-06T00:0{observation + 5}:00Z",
        "evidence": [
            {
                "kind": "runtime_snapshot",
                "source": snapshot_id,
                "detail": "unchanged local runtime facts",
            }
        ],
    }


def _config(workspace: Path, name: str = "config.json") -> Path:
    path = workspace / name
    path.write_text(
        json.dumps({"samples": {"sample": {"r1": "/data/r1.fastq.gz"}}}),
        encoding="utf-8",
    )
    return path


def _argv(run_dir: Path, config_name: str, cores: int) -> list[str]:
    return [
        "/runtime/snakemake",
        "--snakefile",
        str(run_dir / "workflow" / "Snakefile"),
        "--configfile",
        str(run_dir / "config" / config_name),
        "--directory",
        str(run_dir / "results"),
        "--cores",
        str(cores),
        "--printshellcmds",
    ]


def _external_workflow(workspace: Path) -> WorkflowSource:
    root = workspace / "reusable-workflow"
    root.mkdir()
    (root / "Snakefile").write_text("rule all:\n    input: []\n", encoding="utf-8")
    return WorkflowSource(engine="snakemake", root=str(root), entrypoint="Snakefile")


def _bundled_workflow() -> WorkflowSource:
    return WorkflowSource(
        engine="snakemake",
        root=str(PLUGIN_ROOT / "workflows" / "fastq_qc"),
        entrypoint="workflow/Snakefile",
    )


class SnakemakeBindingTests(unittest.TestCase):
    def test_bundled_workflow_uses_its_packaged_default_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            with (
                mock.patch.dict(
                    os.environ,
                    {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(workspace / "state")},
                ),
                mock.patch.object(
                    snakemake, "assess_readiness", return_value=READINESS
                ) as assess_readiness,
            ):
                defaults.bootstrap_default_workflows()
                planned = app.plan_snakemake("oai_fastq_qc", str(workspace / "run"))

        default_config = PLUGIN_ROOT / "workflows" / "fastq_qc" / "config" / "config.json"
        self.assertEqual(assess_readiness.call_args_list[0].args[1], default_config)
        self.assertEqual(planned["request"]["config_file"], str(default_config))
        self.assertEqual(planned["request"]["display_name"], "Bundled FASTQ QC")

    def test_bundled_multiqc_commands_support_older_versions_without_network_checks(self) -> None:
        workflow_files = [
            PLUGIN_ROOT / "workflows" / "fastq_qc" / "workflow" / "Snakefile",
            PLUGIN_ROOT / "workflows" / "fastq_qc" / "workflow" / "rules" / "trimmed_qc.smk",
            PLUGIN_ROOT / "workflows" / "bulk_rnaseq_counts_qc" / "workflow" / "Snakefile",
        ]
        multiqc_commands = [
            shlex.split(arguments)
            for path in workflow_files
            for arguments in re.findall(
                r"\{MULTIQC:q\}([^\"\n]+)", path.read_text(encoding="utf-8")
            )
        ]

        self.assertEqual(len(multiqc_commands), 4)
        for arguments in multiqc_commands:
            with self.subTest(arguments=arguments):
                self.assertNotIn("--no-version-check", arguments)
                self.assertIn("--no-megaqc-upload", arguments)
                self.assertEqual(
                    arguments[arguments.index("--cl-config") + 1],
                    "no_version_check: true",
                )

    def test_globally_unique_workflow_identifier_selects_snakemake(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            config = _config(workspace)
            with (
                mock.patch.dict(
                    os.environ,
                    {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(workspace / "state")},
                ),
                mock.patch.object(snakemake, "assess_readiness", return_value=READINESS),
            ):
                defaults.bootstrap_default_workflows()
                planned = app.plan_snakemake(
                    "oai_fastq_qc", str(workspace / "run"), config_file=str(config)
                )

        self.assertEqual(planned["binding"], "snakemake")
        self.assertEqual(planned["request"]["pipeline"], "oai_fastq_qc")
        self.assertEqual(planned["request"]["config_file"], str(config.resolve()))

    def test_readiness_for_another_engine_cannot_authorize_a_snakemake_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            config = _config(workspace)
            with mock.patch.object(
                snakemake,
                "assess_readiness",
                return_value={**READINESS, "binding": "nextflow"},
            ):
                planned = snakemake.plan_run(
                    "fastq_qc",
                    str(workspace / "run"),
                    str(config),
                    workflow_source=_bundled_workflow(),
                )

            self.assertFalse(planned["ok"])
            self.assertFalse((workspace / "run").exists())

    def test_plan_preserves_unknown_readiness_and_is_not_runnable(self) -> None:
        unknown = {
            **READINESS,
            "ok": False,
            "status": "unknown",
            "unknowns": ["workflow dependencies are not machine-resolvable"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            config = _config(workspace)
            with mock.patch.object(
                snakemake,
                "assess_readiness",
                return_value=unknown,
            ):
                result = snakemake.plan_run(
                    pipeline="fastq_qc",
                    run_dir=str(workspace / "run"),
                    config_file=str(config),
                    run_id="snakemake-fastq-qc-unknown",
                    workflow_source=_bundled_workflow(),
                )
            wrote_runs = (workspace / "run").exists()

        self.assertTrue(result["ok"])
        self.assertFalse(result["runnable"])
        self.assertEqual(result["readiness"]["status"], "unknown")
        self.assertIn("readiness unresolved", result["blockers"][0])
        self.assertFalse(wrote_runs)

    def test_plan_is_read_only_and_binds_config_workflow_and_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            config = _config(workspace)
            run_id = "snakemake-fastq-qc-plan"
            run_dir = workspace / "run"

            with mock.patch.object(
                snakemake,
                "assess_readiness",
                return_value=READINESS,
            ) as readiness:
                payload = snakemake.plan_run(
                    pipeline="fastq_qc",
                    run_dir=str(workspace / "run"),
                    config_file=str(config),
                    cores=3,
                    run_id=run_id,
                    workflow_source=_bundled_workflow(),
                )

            plan = SnakemakeRunPlan.model_validate(payload)
            canonical_workspace = workspace.resolve()
            canonical_config = config.resolve()
            readiness.assert_called_once_with(
                "fastq_qc",
                canonical_config,
                None,
                None,
                target_id="local",
                controller_candidate_id=None,
                refresh=False,
            )
            self.assertTrue(plan.runnable)
            self.assertEqual(plan.request.pipeline, "fastq_qc")
            self.assertEqual(plan.request.run_dir, str(canonical_workspace / "run"))
            self.assertEqual(plan.request.config_file, str(canonical_config))
            self.assertEqual(
                plan.request.config_sha256,
                f"sha256:{hashlib.sha256(config.read_bytes()).hexdigest()}",
            )
            self.assertEqual(
                plan.request.workflow_source,
                _bundled_workflow().model_copy(
                    update={
                        "root": str((PLUGIN_ROOT / "workflows" / "fastq_qc").resolve()),
                        "source_sha256": plan.request.workflow_sha256,
                    }
                ),
            )
            self.assertEqual(
                plan.command_argv[2],
                str(canonical_workspace / "run" / "workflow" / "workflow" / "Snakefile"),
            )
            canonical_run_dir = canonical_workspace / run_dir.relative_to(workspace)
            self.assertNotIn("--log-handler-script", plan.command_argv)
            self.assertEqual(plan.effects.output_dir, str(canonical_run_dir / "results"))
            self.assertEqual(plan.effects.work_dir, plan.effects.output_dir)
            self.assertIn(str(canonical_run_dir / "results"), plan.effects.local_writes)
            self.assertIn(
                str(canonical_run_dir / "results" / ".snakemake"), plan.effects.local_writes
            )
            self.assertIn(
                str(canonical_run_dir / "results" / ".snakemake" / "log"),
                plan.monitoring.log_paths,
            )
            self.assertEqual(
                {path.relative_to(workspace) for path in workspace.rglob("*") if path.is_file()},
                {Path(config.name)},
            )

    def test_plan_binds_prospective_config_and_downloads_in_one_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            destination = workspace / "demo"
            config = destination / "fastq-qc-config.json"
            config_text = json.dumps(
                {"samples": {"sample": {"r1": str(destination / "inputs" / "reads.fastq.gz")}}}
            )
            preparation_spec = preparation.normalize_preparation(
                {
                    "destination_dir": str(destination),
                    "downloads": [
                        {
                            "relative_path": "inputs/reads.fastq.gz",
                            "url": (
                                "https://raw.githubusercontent.com/example/data/"
                                "abc123/reads.fastq.gz"
                            ),
                            "bytes": 12,
                            "sha256": "1" * 64,
                        }
                    ],
                    "generated_files": [
                        {
                            "relative_path": config.name,
                            "media_type": "application/json",
                            "content": config_text,
                        }
                    ],
                }
            )
            with mock.patch.object(
                snakemake,
                "assess_readiness",
                return_value=READINESS,
            ) as readiness:
                payload = snakemake.plan_run(
                    pipeline="fastq_qc",
                    run_dir=str(workspace / "run"),
                    config_file=str(config),
                    run_id="snakemake-fastq-qc-compound-plan",
                    preparation_spec=preparation_spec,
                    workflow_source=_bundled_workflow(),
                )

            plan = SnakemakeRunPlan.model_validate(payload)
            self.assertTrue(plan.runnable)
            self.assertFalse(destination.exists())
            self.assertEqual(plan.preparation, preparation_spec)
            self.assertEqual(plan.request.config_sha256, preparation_spec.operations[-1].sha256)
            self.assertIn(preparation_spec.writes[0], plan.effects.local_writes)
            readiness.assert_called_once_with(
                "fastq_qc",
                config.resolve(),
                None,
                config_text,
                target_id="local",
                controller_candidate_id=None,
                refresh=False,
            )

    def test_plan_binds_the_selected_managed_environment_invocation(self) -> None:
        candidate_id = f"controller-{'6' * 32}"
        managed_readiness = {
            **READINESS,
            "selected_controller": {
                "candidate_id": candidate_id,
                "controller": "snakemake",
                "source": "managed_environment",
                "manager": "micromamba",
                "executable_path": "/env/bin/snakemake",
                "environment_path": "/env",
                "platform_matches_host": True,
                "launch_argv_prefix": [
                    "/runtime/micromamba",
                    "run",
                    "--prefix",
                    "/env",
                    "snakemake",
                ],
                "recommended": True,
                "recommendation_reason": "managed environment",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            config = _config(workspace)
            with mock.patch.object(
                snakemake,
                "assess_readiness",
                return_value=managed_readiness,
            ):
                payload = snakemake.plan_run(
                    pipeline="fastq_qc",
                    run_dir=str(workspace / "run"),
                    config_file=str(config),
                    controller_candidate_id=candidate_id,
                    run_id="snakemake-fastq-qc-managed",
                    workflow_source=_bundled_workflow(),
                )

        plan = SnakemakeRunPlan.model_validate(payload)
        self.assertTrue(plan.runnable)
        self.assertEqual(plan.request.controller_candidate_id, candidate_id)
        self.assertEqual(
            plan.command_argv[:5],
            [
                "/runtime/micromamba",
                "run",
                "--prefix",
                "/env",
                "snakemake",
            ],
        )

    def test_planner_accepts_a_catalog_resolved_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workflow_root = root / "workflows" / "custom"
            workflow_dir = workflow_root / "workflow"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "Snakefile").write_text(
                "rule all:\n    input: []\n",
                encoding="utf-8",
            )
            workspace = root / "workspace"
            workspace.mkdir()
            config = _config(workspace, "custom.yaml")
            source = WorkflowSource(
                engine="snakemake",
                root=str(workflow_root),
                entrypoint="workflow/Snakefile",
            )

            with mock.patch.object(
                snakemake,
                "assess_readiness",
                return_value=READINESS,
            ):
                payload = snakemake.plan_run(
                    pipeline="custom",
                    run_dir=str(workspace / "run"),
                    config_file=str(config),
                    run_id="snakemake-custom-plan",
                    workflow_source=source,
                )

            plan = SnakemakeRunPlan.model_validate(payload)
            self.assertTrue(plan.runnable)
            self.assertEqual(plan.request.workflow, "workflow/Snakefile")
            self.assertEqual(
                Path(plan.command_argv[2]),
                workspace.resolve() / "run" / "workflow" / "workflow" / "Snakefile",
            )

    def test_config_drift_rejects_start_without_creating_a_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            config = _config(workspace)
            arguments = {
                "pipeline": "scrnaseq",
                "run_dir": str(workspace / "run"),
                "config_file": str(config),
                "run_id": "snakemake-scrnaseq-drift",
                "workflow_source": _bundled_workflow(),
            }

            with mock.patch.object(
                snakemake,
                "assess_readiness",
                return_value=READINESS,
            ):
                approved_plan = snakemake.plan_run(**arguments)
                approved_checksum = _plan_checksum(approved_plan)
                config.write_text(json.dumps({"changed": True}), encoding="utf-8")
                result = snakemake.approved_execution_request(
                    SnakemakeRunPlan.model_validate(approved_plan), approved_checksum
                )

            self.assertFalse(result["ok"])
            self.assertEqual(result["supplied_checksum"], approved_checksum)
            self.assertNotEqual(result["expected_checksum"], approved_checksum)
            self.assertFalse((workspace / "run").exists())

    def test_external_workflow_runs_without_being_bundled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            source = _external_workflow(workspace)
            config = _config(workspace)
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                assert source.root is not None
                catalog_store.save_workflow(
                    "custom_workflow",
                    "Custom workflow",
                    "snakemake",
                    catalog_store.LocalWorkflowSource(
                        kind="local", root=source.root, entrypoint=source.entrypoint
                    ),
                )
                try:
                    with (
                        mock.patch.object(snakemake, "assess_readiness", return_value=READINESS),
                        mock.patch.object(
                            snakemake,
                            "build_snakemake_argv",
                            return_value=[sys.executable, "-c", "raise SystemExit(0)"],
                        ),
                    ):
                        registered = app.plan_snakemake(
                            workflow_id="custom_workflow",
                            run_dir=str(workspace / "run"),
                            config_file=str(config),
                        )
                        plan = registered
                        self.assertTrue(plan["runnable"])
                        self.assertFalse((workspace / "run").exists())
                        started = approved_execution.execute_registered_plan(
                            str(registered["plan_name"]),
                            str(registered["plan_id"]),
                            str(registered["plan_checksum"]),
                        )
                    deadline = time.monotonic() + 10
                    while time.monotonic() < deadline:
                        observation = app.observe_ngs_run(str(started["registry_run_id"]))
                        if observation["status"] in {"completed", "failed"}:
                            break
                        time.sleep(0.025)
                    result = app.get_ngs_run(str(started["registry_run_id"]))

                    self.assertEqual(result["status"], "completed", result)
                    staged_snakefile = Path(str(result["run_dir"])) / "workflow" / "Snakefile"
                    self.assertTrue(staged_snakefile.is_file())
                    self.assertEqual(
                        result["workflow_source"]["source_sha256"],
                        plan["request"]["workflow_source"]["source_sha256"],
                    )
                    self.assertEqual(result["workflow_source"]["kind"], "local")
                finally:
                    process = daemon_client._SPAWNED_DAEMON
                    if process is not None and process.poll() is None:
                        process.terminate()
                        process.wait(timeout=5)

    def test_source_cannot_contain_its_execution_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            (workspace / "Snakefile").write_text("rule all:\n    input: []\n", encoding="utf-8")
            config = _config(workspace)
            source = WorkflowSource(engine="snakemake", root=str(workspace), entrypoint="Snakefile")

            planned = snakemake.plan_run(
                "overlapping", str(workspace / "run"), str(config), workflow_source=source
            )

            self.assertFalse(planned["ok"])
            self.assertFalse((workspace / "run").exists())

    def test_long_workflow_identifier_preserves_a_valid_run_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            source = _external_workflow(workspace)
            config = _config(workspace)
            workflow_id = "a" * 96
            with mock.patch.object(snakemake, "assess_readiness", return_value=READINESS):
                planned = snakemake.plan_run(
                    workflow_id, str(workspace / "run"), str(config), workflow_source=source
                )

            self.assertTrue(planned["runnable"], planned)
            self.assertEqual(planned["request"]["pipeline"], workflow_id)
            self.assertLessEqual(len(planned["request"]["run_id"]), 96)
            self.assertFalse((workspace / "run").exists())

    def test_external_workflow_without_default_profile_can_be_planned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = _external_workflow(workspace)
            config = _config(workspace)
            with (
                mock.patch.dict(
                    os.environ,
                    {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(workspace / "private-state")},
                ),
                mock.patch.object(
                    snakemake.readiness_service,
                    "assess",
                    side_effect=lambda requirements, *_args, **_kwargs: {
                        **READINESS,
                        "warnings": requirements.warnings,
                    },
                ),
            ):
                assert source.root is not None
                catalog_store.save_workflow(
                    "ordinary_workflow",
                    "Ordinary workflow",
                    "snakemake",
                    catalog_store.LocalWorkflowSource(
                        kind="local", root=source.root, entrypoint=source.entrypoint
                    ),
                )
                readiness = app.check_snakemake_readiness(
                    workflow_id="ordinary_workflow",
                    run_dir=str(workspace / "run"),
                    config_file=str(config),
                )
                result = snakemake.plan_run(
                    "ordinary_workflow",
                    str(workspace / "run"),
                    str(config),
                    workflow_source=source,
                )

            self.assertTrue(result["runnable"])
            self.assertEqual(readiness.warnings, [])
            self.assertEqual(readiness.warnings, result["readiness"]["warnings"])
            self.assertFalse((workspace / "run").exists())

    def test_external_task_without_default_profile_preserves_readiness_limitation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = _external_workflow(workspace)
            root = Path(str(source.root))
            (root / "Snakefile").write_text(
                "rule run:\n    output: 'result.txt'\n    shell: 'missing_tool > {output}'\n",
                encoding="utf-8",
            )
            config = _config(workspace)
            with mock.patch.object(
                snakemake.readiness_service,
                "assess",
                side_effect=lambda requirements, *_args, **_kwargs: {
                    **READINESS,
                    "warnings": requirements.warnings,
                },
            ):
                result = snakemake.plan_run(
                    "ordinary_workflow", str(workspace / "run"), str(config), workflow_source=source
                )

            self.assertTrue(result["runnable"])
            self.assertEqual(result["readiness"]["warnings"], [])

    def test_external_source_drift_rejects_execution_without_creating_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = _external_workflow(workspace)
            config = _config(workspace)
            with mock.patch.object(snakemake, "assess_readiness", return_value=READINESS):
                plan = snakemake.plan_run(
                    "custom_workflow",
                    str(workspace / "run"),
                    str(config),
                    run_id="snakemake-custom-source-drift",
                    workflow_source=source,
                )
                (Path(str(source.root)) / "Snakefile").write_text(
                    "rule changed:\n    input: []\n", encoding="utf-8"
                )
                result = snakemake.approved_execution_request(
                    SnakemakeRunPlan.model_validate(plan), _plan_checksum(plan)
                )

            self.assertFalse(result["ok"])
            self.assertFalse((workspace / "run").exists())

    def test_run_configuration_does_not_change_reusable_workflow_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = _external_workflow(workspace)
            first_config = _config(workspace, "first.json")
            second_config = _config(workspace, "second.json")
            second_config.write_text(json.dumps({"different_sample": True}), encoding="utf-8")
            with mock.patch.object(snakemake, "assess_readiness", return_value=READINESS):
                first = snakemake.plan_run(
                    "custom_workflow",
                    str(workspace / "run"),
                    str(first_config),
                    workflow_source=source,
                )
                second = snakemake.plan_run(
                    "custom_workflow",
                    str(workspace / "run"),
                    str(second_config),
                    workflow_source=source,
                )

            self.assertEqual(
                first["request"]["workflow_source"]["source_sha256"],
                second["request"]["workflow_source"]["source_sha256"],
            )
            self.assertNotEqual(
                first["request"]["config_sha256"], second["request"]["config_sha256"]
            )

    def test_run_configuration_inside_reusable_source_is_bound_by_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = _external_workflow(workspace)
            config = _config(Path(str(source.root)))
            result = snakemake.plan_run(
                "custom_workflow", str(workspace / "run"), str(config), workflow_source=source
            )

            self.assertTrue(result["ok"], result)
            self.assertEqual(result["request"]["config_file"], str(config.resolve()))
            self.assertIsNotNone(result["request"]["config_sha256"])
            self.assertFalse((workspace / "run").exists())

    def test_approved_workflow_stages_configuration_and_completes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            config = _config(workspace)
            controller = root / "snakemake"
            controller.write_text(
                f"#!{sys.executable}\n"
                "import pathlib, sys\n"
                "output = pathlib.Path(sys.argv[sys.argv.index('--directory') + 1])\n"
                "report = output / 'multiqc' / 'report.html'\n"
                "report.parent.mkdir(parents=True, exist_ok=True)\n"
                "report.write_text('<html>observed</html>')\n"
                "(output / 'artifact_index.json').write_text("
                '\'{"artifacts":[{"path":"multiqc/report.html"}]}\')\n'
                "native = output / '.snakemake' / 'log' / 'run.snakemake.log'\n"
                "native.parent.mkdir(parents=True, exist_ok=True)\n"
                "native.write_text('[Thu Aug  6 01:00:00 2026]\\nlocalrule report:\\n"
                "    jobid: 1\\nFinished jobid: 1 (Rule: report)\\n')\n",
                encoding="utf-8",
            )
            controller.chmod(0o755)
            readiness = {
                **READINESS,
                "commands": [{"name": "snakemake", "path": str(controller)}],
            }
            with mock.patch.dict(
                os.environ, {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(root / "state")}
            ):
                try:
                    with mock.patch.object(snakemake, "assess_readiness", return_value=readiness):
                        plan = snakemake.plan_run(
                            "fastq_qc",
                            str(workspace / "run"),
                            str(config),
                            run_id="snakemake-approved-workflow",
                            workflow_source=_bundled_workflow(),
                        )
                        registered = plan_registry.register_plan("snakemake", plan)
                        started = approved_execution.execute_registered_plan(
                            str(registered["plan_name"]),
                            str(registered["plan_id"]),
                            str(registered["plan_checksum"]),
                        )
                    deadline = time.monotonic() + 10
                    while time.monotonic() < deadline:
                        observation = app.observe_ngs_run(str(started["registry_run_id"]))
                        if observation["status"] in {"completed", "failed"}:
                            break
                        time.sleep(0.025)
                    result = app.get_ngs_run(str(started["registry_run_id"]))

                    self.assertEqual(result["status"], "completed", result)
                    staged = Path(str(result["run_dir"])) / "config" / config.name
                    self.assertEqual(staged.read_bytes(), config.read_bytes())
                    observation = app.observe_ngs_run(str(started["registry_run_id"]))
                    report = runs.get_registry_run_report(str(started["registry_run_id"]))["report"]
                    self.assertTrue(observation["execution"]["evidence"]["available"])
                    self.assertIn(
                        "results/multiqc/report.html",
                        {entry["path"] for entry in report["entries"]},
                    )
                    self.assertFalse(
                        any(".snakemake" in entry["path"] for entry in report["entries"])
                    )
                    self.assertEqual(result["plan_checksum"], registered["plan_checksum"])
                finally:
                    process = daemon_client._SPAWNED_DAEMON
                    if process is not None and process.poll() is None:
                        process.terminate()
                        process.wait(timeout=5)


class RemoteSnakemakePlanTests(DaemonTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.enterContext(target_input_transport())

    def test_snakemake_does_not_claim_slurm_execution(self) -> None:
        self._configure_ssh_target()
        config = _config(self.workspace)
        with mock.patch.object(
            snakemake.readiness_service,
            "assess",
            side_effect=lambda requirements, *_args, **_kwargs: {
                **READINESS,
                "ok": not requirements.blockers,
                "status": "blocked" if requirements.blockers else "ready",
                "blockers": requirements.blockers,
            },
        ):
            defaults.bootstrap_default_workflows()
            readiness = app.check_snakemake_readiness(
                "oai_fastq_qc",
                str(self.workspace / "run"),
                config_file=str(config),
                target_id="lab",
            )
        planned = snakemake.plan_run(
            "fastq_qc",
            str(self.workspace / "run"),
            str(config),
            target_id="lab",
            workflow_source=_bundled_workflow(),
        )

        self.assertEqual(readiness.status, "blocked")
        self.assertFalse(planned["ok"])
        self.assertFalse((self.workspace / "run").exists())

    def test_remote_plan_uses_target_config_and_stages_only_workflow(self) -> None:
        target = self._configure_ssh_target(executor="local_process", partition=None)
        source = _external_workflow(self.workspace)
        config = self.workspace / "run.json"
        config.write_text(
            json.dumps(
                {
                    "input": "/data/reads.fastq",
                    "sample_id": "S1.v2",
                    "reference_uri": "s3://references/GRCh38.fa",
                }
            ),
            encoding="utf-8",
        )
        readiness = {**READINESS, "host": {"os": "linux", "arch": "arm64"}}
        with mock.patch.object(snakemake, "assess_readiness", return_value=readiness):
            planned = snakemake.plan_run(
                "custom_workflow",
                str(self.workspace / "run"),
                str(config),
                workflow_source=source,
                run_id="snakemake-custom-ssh",
                target_id="lab",
            )

        self.assertTrue(planned["runnable"], planned)
        remote = planned["request"]["remote"]
        staged = {item["destination"]: item for item in remote["staged_files"]}
        self.assertEqual(remote["config_hash"], target["config_hash"])
        self.assertEqual(planned["effects"]["run_dir"], remote["run_dir"])
        self.assertEqual(planned["effects"]["output_dir"], f"{remote['run_dir']}/results")
        self.assertEqual(
            planned["effects"]["launch_log"], f"{remote['run_dir']}/logs/snakemake.log"
        )
        self.assertTrue(
            all(
                path.startswith(f"{remote['run_dir']}/")
                for path in planned["monitoring"]["log_paths"]
            )
        )
        self.assertEqual(set(staged), {f"{remote['run_dir']}/workflow/Snakefile"})
        config_argument = planned["command_argv"].index("--configfile")
        self.assertEqual(planned["command_argv"][config_argument + 1], str(config))
        self.assertIn(f"{remote['run_dir']}/workflow/Snakefile", planned["command_argv"])
        directory = planned["command_argv"].index("--directory")
        self.assertEqual(planned["command_argv"][directory + 1], f"{remote['run_dir']}/results")
        self.assertTrue(set(staged).issubset(planned["effects"]["remote_writes"]))
        self.assertFalse((self.workspace / "run").exists())

        registered = plan_registry.register_plan("snakemake", planned)
        with (
            mock.patch.object(snakemake, "assess_readiness", return_value=readiness),
            mock.patch.object(
                approved_execution.daemon_client, "execute", return_value={"ok": True}
            ) as dispatch,
        ):
            accepted = approved_execution.execute_registered_plan(
                str(registered["plan_name"]),
                str(registered["plan_id"]),
                str(registered["plan_checksum"]),
            )
        self.assertTrue(accepted["ok"])
        dispatch.assert_called_once()
        self.assertEqual(
            dispatch.call_args.args[0].inputs,
            {str(config): f"sha256:{hashlib.sha256(config.read_bytes()).hexdigest()}"},
        )
        self.assertEqual(
            {item.kind for item in dispatch.call_args.args[0].files},
            {"copy_tree", "write_approved_plan"},
        )

        self.assertEqual(accepted["run_dir"], remote["run_dir"])
        metadata_root = Path(dispatch.call_args.args[0].files[-1].destination).parents[1]
        self.assertTrue(metadata_root.is_relative_to(self.root / "state/runs"))
        self.assertTrue(
            all(
                Path(item.destination).is_relative_to(metadata_root)
                for item in dispatch.call_args.args[0].files
            )
        )

    def test_remote_plan_blocks_missing_target_config(self) -> None:
        self._configure_ssh_target(executor="local_process", partition=None)
        source = _external_workflow(self.workspace)
        readiness = {**READINESS, "host": {"os": "linux", "arch": "arm64"}}
        with mock.patch.object(snakemake, "assess_readiness", return_value=readiness):
            planned = snakemake.plan_run(
                "custom_workflow",
                str(self.workspace / "run"),
                str(self.workspace / "missing.json"),
                target_id="lab",
                workflow_source=source,
            )
        self.assertFalse(planned["runnable"], planned)
        self.assertFalse((self.workspace / "run").exists())

    def test_remote_plan_prepares_inputs_directly_on_target(self) -> None:
        self._configure_ssh_target(executor="local_process", partition=None)
        source = _external_workflow(self.workspace)
        generated = self.workspace / "prepared" / "reads.fastq"
        config = generated.parent / "remote.json"
        content = json.dumps({"input": str(generated)})
        prepared = preparation.normalize_preparation(
            {
                "destination_dir": str(generated.parent),
                "generated_files": [
                    {"relative_path": generated.name, "content": "ACGT\n"},
                    {"relative_path": config.name, "content": content},
                ],
            },
            target_id="lab",
        )
        readiness = {**READINESS, "host": {"os": "linux", "arch": "arm64"}}
        with mock.patch.object(snakemake, "assess_readiness", return_value=readiness):
            planned = snakemake.plan_run(
                "custom_workflow",
                str(self.workspace / "run"),
                str(config),
                preparation_spec=prepared,
                target_id="lab",
                workflow_source=source,
            )
        self.assertTrue(planned["runnable"], planned)
        self.assertFalse(generated.exists())
        self.assertFalse(config.exists())
        self.assertEqual(
            planned["request"]["config_sha256"],
            f"sha256:{hashlib.sha256(content.encode()).hexdigest()}",
        )
        self.assertTrue(set(prepared.writes).issubset(planned["effects"]["remote_writes"]))
        self.assertTrue(set(prepared.writes).isdisjoint(planned["effects"]["local_writes"]))
        self.assertEqual(
            [
                Path(item["destination"]).name
                for item in planned["request"]["remote"]["staged_files"]
            ],
            ["Snakefile"],
        )


if __name__ == "__main__":
    unittest.main()
