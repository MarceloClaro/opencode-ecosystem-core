from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from daemon_test_case import DaemonTestCase  # noqa: E402
from ngs_workbench_daemon import runs as daemon_runs  # noqa: E402
from ngs_workbench_daemon import ssh  # noqa: E402
from ngs_workbench_mcp import app, approved_execution, plan_registry, runs  # noqa: E402
from ngs_workbench_mcp.plans import (  # noqa: E402
    NextflowRunPlan,
    PreparationOperation,
    PreparationSpec,
    plan_checksum,
)
from ngs_workbench_mcp.workflows import catalog_store, defaults, nextflow  # noqa: E402
from ngs_workbench_mcp.workflows.source import WorkflowSource  # noqa: E402

_plan_catalog_workflow = nextflow.plan_remote_run


def _plan_with_catalog_source(*args: Any, **kwargs: Any) -> dict[str, Any]:
    kwargs.setdefault("workflow", "nf-core/demo")
    return _plan_catalog_workflow(*args, **kwargs)


nextflow.plan_remote_run = _plan_with_catalog_source


def _plan_checksum(payload: dict[str, object]) -> str:
    return plan_checksum(NextflowRunPlan.model_validate(payload))


@contextmanager
def target_input_transport() -> Iterator[None]:
    run = subprocess.run

    def execute(_remote: dict[str, Any], source: str, _operation: str, timeout: int = 30) -> Any:
        result = run(
            [sys.executable, "-"], input=source, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode:
            raise ValueError(result.stderr)
        return json.loads(result.stdout)

    with mock.patch.object(ssh, "_run_program", side_effect=execute):
        yield


def ready(
    nextflow: str = "/runtime/nextflow",
    *,
    observation: int | None = None,
    docker_platform: tuple[str, str] = ("linux", "amd64"),
) -> dict[str, object]:
    result: dict[str, object] = {
        "ok": True,
        "status": "ready",
        "scope": "executable_presence_only",
        "commands": [
            {"name": "nextflow", "path": nextflow},
            {"name": "docker", "path": "/runtime/docker"},
        ],
        "blockers": [],
        "docker": {
            "path": "/runtime/docker",
            "daemon_reachable": True,
            "server_os": docker_platform[0],
            "server_arch": docker_platform[1],
        },
    }
    if observation is not None:
        identity = f"{observation:032x}"
        snapshot_id = f"runtime-{identity}"
        result.update(
            {
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
        )
    return result


class CuratedNextflowPlanTests(unittest.TestCase):
    def test_nextflow_planner_discovers_samplesheet_from_native_parameters_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            sample_sheet = workspace / "samples.csv"
            sample_sheet.write_text(
                "sample,fastq_1,fastq_2\nSAMPLE,/data/R1.fastq.gz,/data/R2.fastq.gz\n",
                encoding="utf-8",
            )
            params = workspace / "params.json"
            params.write_text(
                json.dumps({"input": str(sample_sheet), "genome": "GRCh38"}),
                encoding="utf-8",
            )
            with (
                mock.patch.dict(
                    os.environ,
                    {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(workspace / "state")},
                ),
                mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()),
            ):
                defaults.bootstrap_default_workflows()
                planned = app.plan_nextflow(
                    "rnaseq",
                    str(workspace / "run"),
                    params_file=str(params),
                    profile="docker",
                )

                self.assertTrue(planned["runnable"], planned)
                self.assertEqual(planned["request"]["sample_sheet"], str(sample_sheet.resolve()))
                self.assertEqual(planned["request"]["params_file"], str(params.resolve()))
                self.assertIn(str(sample_sheet.resolve()), planned["command_argv"])

                with mock.patch.object(
                    approved_execution.daemon_client, "execute", return_value={"ok": True}
                ) as dispatch:
                    result = approved_execution.execute_registered_plan(
                        planned["plan_name"], planned["plan_id"], planned["plan_checksum"]
                    )

                self.assertTrue(result["ok"])
                self.assertEqual(dispatch.call_args.args[0].binding, "nextflow")

    def test_nextflow_parameters_remain_workflow_owned_without_trim_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            params = workspace / "params.json"
            params.write_text(json.dumps({"skip_trim": False}), encoding="utf-8")
            with (
                mock.patch.dict(
                    os.environ,
                    {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(workspace / "state")},
                ),
                mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()),
            ):
                defaults.bootstrap_default_workflows()
                planned = app.plan_nextflow(
                    "fastq_qc",
                    str(workspace / "run"),
                    params_file=str(params),
                    profile="test,docker",
                )
                preserved_parameters = json.loads(params.read_text(encoding="utf-8"))

        self.assertNotIn("trim", planned["request"])
        self.assertNotIn("--skip_trim", planned["command_argv"])
        self.assertEqual(preserved_parameters, {"skip_trim": False})

    def test_nextflow_discovers_approved_generated_parameters_without_writing_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            directory = workspace / "prepared"
            params = directory / "params.json"
            sample_sheet = directory / "samples.csv"
            preparation = {
                "destination_dir": str(directory),
                "generated_files": [
                    {
                        "relative_path": params.name,
                        "content": json.dumps({"input": str(sample_sheet)}),
                    },
                    {
                        "relative_path": sample_sheet.name,
                        "content": "sample,fastq_1,fastq_2\nSAMPLE,/data/R1.fastq.gz,\n",
                    },
                ],
            }
            with (
                mock.patch.dict(
                    os.environ,
                    {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(workspace / "state")},
                ),
                mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()),
            ):
                defaults.bootstrap_default_workflows()
                planned = app.plan_nextflow(
                    "rnaseq",
                    str(workspace / "run"),
                    params_file=str(params),
                    profile="docker",
                    preparation=preparation,
                )

            self.assertTrue(planned["runnable"], planned)
            self.assertTrue(planned["request"]["params_file_sha256"].startswith("sha256:"))
            self.assertTrue(planned["request"]["sample_sheet_sha256"].startswith("sha256:"))
            self.assertFalse(params.exists())
            self.assertFalse(sample_sheet.exists())

    def test_curated_workflow_plans_and_executes_under_its_nextflow_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(
                os.environ,
                {"NGS_ANALYSIS_WORKBENCH_STATE_DIR": str(Path(temporary) / "state")},
            ):
                defaults.bootstrap_default_workflows()
                with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()):
                    registered = app.plan_nextflow(
                        "fastq_qc",
                        str(Path(temporary) / "run"),
                        profile="test,docker",
                    )

                self.assertEqual(registered["binding"], "nextflow")
                self.assertEqual(registered["readiness"]["binding"], "nextflow")
                self.assertEqual(registered["request"]["revision"], "1.2.0")

                with (
                    mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()),
                    mock.patch.object(
                        approved_execution.daemon_client,
                        "execute",
                        return_value={"ok": True},
                    ) as dispatch,
                ):
                    result = approved_execution.execute_registered_plan(
                        registered["plan_name"],
                        registered["plan_id"],
                        registered["plan_checksum"],
                    )

                self.assertTrue(result["ok"])
                self.assertEqual(result["binding"], "nextflow")
                self.assertEqual(dispatch.call_args.args[0].binding, "nextflow")

    def test_plan_binds_the_selected_managed_environment_invocation(self) -> None:
        candidate_id = f"controller-{'7' * 32}"
        managed_readiness = {
            **ready(),
            "selected_controller": {
                "candidate_id": candidate_id,
                "controller": "nextflow",
                "source": "managed_environment",
                "manager": "conda",
                "executable_path": "/env/bin/nextflow",
                "environment_path": "/env",
                "platform_matches_host": True,
                "launch_argv_prefix": [
                    "/runtime/conda",
                    "run",
                    "--prefix",
                    "/env",
                    "nextflow",
                ],
                "recommended": True,
                "recommendation_reason": "managed environment",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(
                nextflow,
                "assess_nfcore_readiness",
                return_value=managed_readiness,
            ):
                plan = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(Path(temporary) / "run"),
                    "test,docker",
                    controller_candidate_id=candidate_id,
                    run_id="nfcore-fastq-qc-managed",
                )

        self.assertTrue(plan["runnable"])
        self.assertEqual(plan["request"]["controller_candidate_id"], candidate_id)
        self.assertEqual(
            plan["command_argv"][:6],
            [
                "/runtime/conda",
                "run",
                "--prefix",
                "/env",
                "nextflow",
                "run",
            ],
        )

    def test_plan_preserves_unknown_readiness_and_is_not_runnable(self) -> None:
        unknown = {
            **ready(),
            "ok": False,
            "status": "unknown",
            "unknowns": ["effective task software environment is unresolved"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            with mock.patch.object(
                nextflow,
                "assess_nfcore_readiness",
                return_value=unknown,
            ):
                result = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(workspace / "run"),
                    "mylab",
                    run_id="nfcore-fastq-qc-unknown",
                )
            wrote_runs = (workspace / "run").exists()

        self.assertTrue(result["ok"])
        self.assertFalse(result["runnable"])
        self.assertEqual(result["readiness"]["status"], "unknown")
        self.assertTrue(any("readiness unresolved" in item for item in result["blockers"]))
        self.assertFalse(wrote_runs)

    def test_plan_rejects_an_invalid_explicit_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()):
                result = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(workspace / "run"),
                    "test,docker",
                    run_id="../../escape",
                )

            self.assertFalse(result["ok"])
            self.assertFalse((workspace / "run").exists())

    def test_plan_is_read_only_and_checksum_is_stable_for_a_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            with mock.patch.object(
                nextflow,
                "assess_nfcore_readiness",
                return_value=ready(docker_platform=("linux", "arm64")),
            ):
                first = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(workspace / "run"),
                    "test,docker,arm64",
                    revision="1.2.0",
                    run_id="nfcore-fastq-qc-fixed",
                )
                second = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(workspace / "run"),
                    "test,docker,arm64",
                    revision="1.2.0",
                    run_id="nfcore-fastq-qc-fixed",
                )

            self.assertTrue(first["ok"])
            self.assertTrue(first["runnable"])
            self.assertEqual(_plan_checksum(first), _plan_checksum(second))
            self.assertEqual(first["request"]["profile"], "test,docker,arm64")
            self.assertFalse((workspace / "run").exists())

    def test_plan_binds_agent_name_and_opaque_samplesheet(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            sample_sheet = workspace / "samplesheet.csv"
            sample_sheet.write_text(
                "sample,fastq_1,fastq_2\nS1,/data/S1_R1.fastq.gz,/data/S1_R2.fastq.gz\n"
                "S2,/data/S2_R1.fastq.gz,/data/S2_R2.fastq.gz\n",
                encoding="utf-8",
            )
            with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()):
                plan = nextflow.plan_remote_run(
                    "rnaseq",
                    str(workspace / "run"),
                    "docker",
                    display_name="  PBMC   pilot RNA-seq  ",
                    sample_sheet=str(sample_sheet),
                    run_id="nfcore-rnaseq-named",
                )

            self.assertEqual(plan["request"]["display_name"], "PBMC pilot RNA-seq")
            self.assertEqual(plan["input_summary"]["source"], "sample_sheet")
            self.assertEqual(plan["input_summary"]["path"], str(sample_sheet.resolve()))
            self.assertIsNone(plan["input_summary"]["sample_count"])
            self.assertIsNone(plan["input_summary"]["record_count"])
            self.assertIsNone(plan["input_summary"]["read_layout"])

    def test_plan_rejects_an_unregistered_target_without_checking_local_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(nextflow, "assess_nfcore_readiness") as readiness:
                result = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(Path(temporary) / "run"),
                    "test,docker",
                    target_id="lab-slurm",
                    run_id="nfcore-fastq-qc-remote",
                )

        self.assertFalse(result["ok"])
        self.assertIn("compute target is not registered", result["errors"][0])
        readiness.assert_not_called()

    def test_missing_sample_sheet_is_not_reported_as_test_profile_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()):
                blocked = nextflow.plan_remote_run(
                    "rnaseq",
                    str(Path(temporary) / "run"),
                    "contest,docker",
                    run_id="nfcore-rnaseq-missing-input",
                )
                test_plan = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(Path(temporary) / "run"),
                    "test,docker",
                    run_id="nfcore-fastq-qc-test-input",
                )

            self.assertFalse(blocked["runnable"])
            self.assertEqual(blocked["input_summary"]["source"], "missing")
            self.assertEqual(test_plan["input_summary"]["source"], "workflow_test_profile")

    def test_approved_request_rejects_docker_platform_drift_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            with mock.patch.object(
                nextflow,
                "assess_nfcore_readiness",
                return_value=ready(docker_platform=("linux", "arm64")),
            ):
                plan = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(workspace / "run"),
                    "test,docker,arm64",
                    revision="1.2.0",
                    run_id="nfcore-fastq-qc-drift",
                )
            with mock.patch.object(
                nextflow,
                "assess_nfcore_readiness",
                return_value=ready(docker_platform=("linux", "amd64")),
            ):
                result = nextflow.approved_nfcore_execution_request(
                    NextflowRunPlan.model_validate(plan), _plan_checksum(plan)
                )

            self.assertFalse(result["ok"])
            self.assertIn("checksum", result["errors"][0])
            self.assertFalse((workspace / "run").exists())

    def test_approved_request_accepts_refreshed_readiness_when_facts_are_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            with mock.patch.object(
                nextflow,
                "assess_nfcore_readiness",
                side_effect=[ready(observation=1), ready(observation=2)],
            ):
                plan = nextflow.plan_remote_run(
                    "fastq_qc",
                    str(workspace / "run"),
                    "test,docker",
                    revision="1.2.0",
                    run_id="nfcore-fastq-qc-refreshed",
                )
                request = nextflow.approved_nfcore_execution_request(
                    NextflowRunPlan.model_validate(plan), _plan_checksum(plan)
                )

            self.assertEqual(request.plan_checksum, _plan_checksum(plan))
            self.assertFalse((workspace / "run").exists())

    def test_approved_request_rejects_params_file_content_drift_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            params_file = workspace / "params.json"
            params_file.write_text('{"aligner":"star_salmon"}\n', encoding="utf-8")
            with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=ready()):
                plan = nextflow.plan_remote_run(
                    "rnaseq",
                    str(workspace / "run"),
                    "test,docker",
                    params_file=str(params_file),
                    revision="3.26.0",
                    run_id="nfcore-rnaseq-params-drift",
                )
                params_file.write_text('{"aligner":"hisat2"}\n', encoding="utf-8")
                result = nextflow.approved_nfcore_execution_request(
                    NextflowRunPlan.model_validate(plan), _plan_checksum(plan)
                )

            self.assertFalse(result["ok"])
            self.assertFalse((workspace / "run").exists())


class RemoteNextflowPlanTests(DaemonTestCase):
    def setUp(self) -> None:
        super().setUp()
        defaults.bootstrap_default_workflows()
        self.enterContext(target_input_transport())
        self.target_files = self.root / "target-files"
        self.target_files.mkdir()

    def test_slurm_plan_binds_target_configuration_and_exact_controller_argv(self) -> None:
        target = self._configure_ssh_target()
        readiness = {
            **ready(nextflow="/remote/bin/nextflow"),
            "host": {"os": "linux", "arch": "arm64"},
        }
        with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=readiness):
            planned = nextflow.plan_remote_run(
                "fastq_qc",
                str(self.workspace / "run"),
                "test,docker",
                run_id="nfcore-fastq-qc-ssh-plan",
                target_id="lab",
            )

        self.assertTrue(planned["runnable"])
        remote = planned["request"]["remote"]
        remote_root = str(self.workspace / "run")
        self.assertEqual(remote["config_hash"], target["config_hash"])
        self.assertEqual(remote["host_access"], target["host_access"])
        self.assertEqual(remote["executor_configuration"], {"partition": "cpu"})
        self.assertEqual(remote["run_dir"], remote_root)
        self.assertEqual(planned["effects"]["run_dir"], remote_root)
        for field, relative in (
            ("output_dir", "results"),
            ("work_dir", "work"),
            ("launch_log", "logs/nextflow.log"),
        ):
            self.assertEqual(planned["effects"][field], f"{remote_root}/{relative}")
        self.assertTrue(
            all(
                path.startswith(f"{remote_root}/")
                for field in ("log_paths", "artifact_paths")
                for path in planned["monitoring"][field]
            )
        )
        self.assertIn(f"{remote_root}/results", planned["command_argv"])
        self.assertIn(f"{remote_root}/workflow/trace.txt", planned["command_argv"])
        self.assertIn(f"{remote_root}/workflow/trace.txt", planned["effects"]["remote_writes"])
        self.assertIn(f"{remote_root}/results", planned["effects"]["remote_writes"])
        configuration = next(
            item
            for item in remote["staged_files"]
            if item["destination"].endswith("nextflow.config")
        )
        self.assertIn("executor = 'slurm'", configuration["content"])
        self.assertIn('queue = "cpu"', configuration["content"])
        self.assertNotIn("memory = '1536 MB'", configuration["content"])
        self.assertIn(configuration["destination"], planned["command_argv"])
        self.assertFalse((self.workspace / "run").exists())

        registered = plan_registry.register_plan("nextflow", planned)
        with (
            mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=readiness),
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

        self.assertEqual(accepted["run_dir"], remote_root)
        request = dispatch.call_args.args[0]
        metadata_root = Path(request.files[-1].destination).parents[1]
        self.assertTrue(metadata_root.is_relative_to(self.root / "state/runs"))
        self.assertTrue(
            all(Path(item.destination).is_relative_to(metadata_root) for item in request.files)
        )
        self.assertEqual(daemon_runs._validate_request(request)[0], metadata_root)

        changed = self._configure_ssh_target(partition="gpu")
        self.assertNotEqual(changed["config_hash"], target["config_hash"])
        with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=readiness):
            updated = nextflow.plan_remote_run(
                "fastq_qc",
                str(self.workspace / "run"),
                "test,docker",
                run_id="nfcore-fastq-qc-ssh-plan",
                target_id="lab",
            )
        self.assertNotEqual(_plan_checksum(updated), _plan_checksum(planned))

    def test_remote_inputs_remain_in_place_and_checksum_bound(self) -> None:
        self._configure_ssh_target(executor="local_process", partition=None)
        sample_sheet = self.target_files / "samples.csv"
        sample_content = "sample,read_one,group\nS1,/data/S1_R1.fastq.gz,control\n"
        sample_sheet.write_text(sample_content, encoding="utf-8")
        params = self.target_files / "params.json"
        content = json.dumps(
            {
                "input": str(sample_sheet),
                "reference": "/data/genome",
                "nested": {"label": "sample.v2"},
            }
        )
        params.write_text(content, encoding="utf-8")
        readiness = {**ready(), "host": {"os": "linux", "arch": "arm64"}}
        with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=readiness):
            planned = app.plan_nextflow(
                "fastq_qc",
                str(self.workspace / "run"),
                profile="test,docker",
                params_file=str(params),
                target_id="lab",
            )
            self.assertTrue(planned["runnable"], planned)
            self.assertIn(str(params), planned["command_argv"])
            self.assertIn(str(sample_sheet), planned["command_argv"])
            self.assertEqual(planned["request"]["remote"]["staged_files"], [])
            self.assertEqual(params.read_text(), content)
            request = nextflow.approved_nfcore_execution_request(
                NextflowRunPlan.model_validate(planned), planned["plan_checksum"]
            )
            self.assertEqual(
                request.inputs[str(sample_sheet)],
                f"sha256:{hashlib.sha256(sample_content.encode()).hexdigest()}",
            )
            sample_sheet.write_text(sample_content.replace("S1_R1", "changed_R1"), encoding="utf-8")
            rejected = nextflow.approved_nfcore_execution_request(
                NextflowRunPlan.model_validate(planned), planned["plan_checksum"]
            )
            self.assertFalse(rejected["ok"])
            with self.assertRaises(ValueError):
                app.plan_nextflow(
                    "fastq_qc",
                    str(self.workspace / "run"),
                    profile="test,docker",
                    params_file="params.json",
                    target_id="lab",
                )

        future = self.target_files / "downloads" / "samples.csv"
        prepared = PreparationSpec(
            destination_dir=str(future.parent),
            operations=[
                PreparationOperation(
                    operation="download_verified_file",
                    relative_path=future.name,
                    path=str(future),
                    bytes=0,
                    sha256=f"sha256:{'0' * 64}",
                )
            ],
            download_bytes=0,
            writes=[str(future)],
        )
        with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=readiness):
            prepared_plan = nextflow.plan_remote_run(
                "fastq_qc",
                str(self.workspace / "run"),
                "test,docker",
                sample_sheet=str(future),
                preparation_spec=prepared,
                run_id="nfcore-fastq-qc-ssh-download",
                target_id="lab",
            )
        self.assertTrue(prepared_plan["runnable"], prepared_plan)
        self.assertIn(str(future), prepared_plan["effects"]["remote_writes"])
        self.assertNotIn(str(future), prepared_plan["effects"]["local_writes"])
        generated = prepared_plan["request"]["remote"]["staged_files"][0]
        self.assertEqual(json.loads(generated["content"])["input"], str(future))
        self.assertFalse(future.exists())
        self.assertFalse((self.workspace / "run").exists())

    def test_unknown_profiles_remain_workflow_owned_without_generated_configuration(self) -> None:
        self._configure_ssh_target(executor="local_process", partition=None)
        requirements = nextflow.resolve_runtime_requirements("fastq_qc", "test,host")
        self.assertEqual({item.id for item in requirements.requirements}, {"nextflow"})
        self.assertTrue(requirements.unknowns)
        readiness = {
            **ready(nextflow=sys.executable),
            "host": {"os": "linux", "arch": "arm64"},
        }
        with mock.patch.object(nextflow, "assess_nfcore_readiness", return_value=readiness):
            planned = nextflow.plan_remote_run(
                "fastq_qc",
                str(self.workspace / "run"),
                "test,docker,HOST",
                run_id="nfcore-fastq-qc-ssh-native-profile",
                target_id="lab",
            )

        remote = planned["request"]["remote"]
        self.assertFalse(
            any(item["destination"].endswith("/nextflow.config") for item in remote["staged_files"])
        )
        self.assertEqual(planned["command_argv"][:2], [sys.executable, "run"])
        self.assertIn("test,docker,HOST", planned["command_argv"])
        self.assertTrue(any("container" in item for item in planned["effects"]["downloads"]))
        self.assertTrue(planned["runnable"])

        with mock.patch.object(
            nextflow,
            "assess_nfcore_readiness",
            return_value={**readiness, "host": {"os": "darwin", "arch": "arm64"}},
        ):
            unsupported = nextflow.plan_remote_run(
                "fastq_qc", str(self.workspace / "run"), "test,docker", target_id="lab"
            )
        self.assertFalse(unsupported["runnable"])


class GenericNextflowTests(DaemonTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.root / "nextflow"
        self.controller.write_text(
            f"#!{sys.executable}\n"
            "import json, pathlib, sys\n"
            "assert sys.argv[1] == 'run'\n"
            "assert pathlib.Path(sys.argv[2]).is_file()\n"
            "trace = pathlib.Path(sys.argv[sys.argv.index('-with-trace') + 1])\n"
            "trace.write_text('task_id\\tname\\tstatus\\n1\\tREPORT\\tCOMPLETED\\n')\n"
            "params_path = pathlib.Path(sys.argv[sys.argv.index('-params-file') + 1]) "
            "if '-params-file' in sys.argv else None\n"
            "params = json.loads(params_path.read_text()) if params_path else {}\n"
            "output = pathlib.Path(sys.argv[sys.argv.index('-output-dir') + 1])\n"
            "result = output / 'output' / 'message.txt'\n"
            "result.parent.mkdir(parents=True, exist_ok=True)\n"
            "result.write_text(params.get('message', 'default'))\n",
            encoding="utf-8",
        )
        self.controller.chmod(0o755)
        root = self.workspace / "source"
        root.mkdir()
        (root / "main.nf").write_text("workflow { log.info 'example' }\n", encoding="utf-8")
        self.source = WorkflowSource(engine="nextflow", root=str(root), entrypoint="main.nf")
        self._save_source("custom_nextflow")
        self.readiness = {
            "ok": True,
            "status": "ready",
            "scope": "executable_presence_only",
            "commands": [{"name": "nextflow", "path": str(self.controller)}],
            "blockers": [],
        }

    def _save_source(self, workflow_id: str, source: WorkflowSource | None = None) -> None:
        selected = source or self.source
        assert selected.root is not None
        catalog_store.save_workflow(
            workflow_id,
            workflow_id,
            "nextflow",
            catalog_store.LocalWorkflowSource(
                kind="local", root=selected.root, entrypoint=selected.entrypoint
            ),
        )

    def _execute(self, plan: dict[str, object]) -> dict[str, object]:
        started = approved_execution.execute_registered_plan(
            str(plan["plan_name"]), str(plan["plan_id"]), str(plan["plan_checksum"])
        )
        self.assertTrue(started["ok"], started)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            observation = app.observe_ngs_run(str(started["registry_run_id"]))
            if observation["status"] in {"completed", "failed"}:
                self.assertEqual(observation["status"], "completed", observation)
                return app.get_ngs_run(str(started["registry_run_id"]))
            time.sleep(0.025)
        self.fail("approved Nextflow workflow did not finish")

    def test_generic_remote_parameters_remain_opaque(self) -> None:
        catalog_store.save_workflow(
            "community_remote",
            "Community remote",
            "nextflow",
            catalog_store.RemoteWorkflowSource(
                kind="remote", workflow="community/example", revision="1.0.0"
            ),
        )
        params = self.workspace / "remote-params.json"
        params.write_text(json.dumps({"input": ["a", "b"]}), encoding="utf-8")

        with mock.patch.object(nextflow, "assess_readiness", return_value=self.readiness):
            planned = app.plan_nextflow(
                "community_remote", str(self.workspace / "remote-run"), params_file=str(params)
            )

        self.assertTrue(planned["ok"], planned)
        self.assertEqual(planned["request"]["parameter_contract"], "generic")
        self.assertEqual(planned["request"]["workflow"], "community/example")
        self.assertEqual(planned["request"]["revision"], "1.0.0")
        self.assertIn("-output-dir", planned["command_argv"])
        self.assertNotIn("--outdir", planned["command_argv"])

    def test_generic_source_executes(self) -> None:
        (self.workspace / "first").write_text("incidental filename collision", encoding="utf-8")
        params = self.workspace / "params.json"
        params.write_text(json.dumps({"message": "first"}), encoding="utf-8")
        with mock.patch.object(nextflow, "assess_readiness", return_value=self.readiness):
            original = app.plan_nextflow(
                "custom_nextflow",
                str(self.workspace / "run"),
                params_file=str(params),
            )
            self.assertEqual(original["binding"], "nextflow")
            self.assertEqual(original["request"]["params_file"], str(params))
            self.assertFalse((self.workspace / "run").exists())
            self.assertFalse(
                {"-profile", "--input", "--outdir", "--skip_trim"}.intersection(
                    original["command_argv"]
                )
            )
            output_index = original["command_argv"].index("-output-dir")
            self.assertEqual(
                original["command_argv"][output_index + 1], original["effects"]["output_dir"]
            )
            self.assertEqual(
                original["effects"]["output_dir"],
                str(Path(original["effects"]["run_dir"]) / "results"),
            )
            self.assertIn(original["effects"]["output_dir"], original["effects"]["local_writes"])
            self.assertIn(
                original["effects"]["output_dir"], original["monitoring"]["artifact_paths"]
            )
            first = self._execute(original)
            observation = app.observe_ngs_run(str(first["registry_run_id"]))
            report = runs.get_registry_run_report(str(first["registry_run_id"]))["report"]
            self.assertTrue(observation["execution"]["evidence"]["available"])
            self.assertEqual(
                (Path(first["run_dir"]) / "results" / "output" / "message.txt").read_text(),
                "first",
            )
            self.assertIn(
                "results/output/message.txt",
                {entry["path"] for entry in report["entries"]},
            )
            repeated = approved_execution.execute_registered_plan(
                original["plan_name"], original["plan_id"], original["plan_checksum"]
            )
            self.assertEqual(repeated["run_id"], first["run_id"])

    def test_saved_snapshot_is_separate_from_its_execution_directory(self) -> None:
        (self.workspace / "main.nf").write_text("workflow {}\n", encoding="utf-8")
        source = WorkflowSource(engine="nextflow", root=str(self.workspace), entrypoint="main.nf")
        self._save_source("overlapping", source)

        planned = app.plan_nextflow("overlapping", str(self.workspace / "run"))

        self.assertTrue(planned["ok"], planned)
        self.assertNotEqual(planned["request"]["workflow_source"]["root"], str(self.workspace))
        self.assertFalse((self.workspace / "run").exists())

    def test_long_workflow_identifier_and_opaque_parameters_remain_executable(self) -> None:
        params = self.workspace / "params.json"
        workflow_parameters = {
            "message": "workflow-owned",
            "custom_options": {"strategy": "paired"},
        }
        params.write_text(json.dumps(workflow_parameters), encoding="utf-8")
        workflow_id = "a" * 96
        self._save_source(workflow_id)
        with mock.patch.object(nextflow, "assess_readiness", return_value=self.readiness):
            planned = app.plan_nextflow(
                workflow_id,
                str(self.workspace / "run"),
                params_file=str(params),
            )
            self.assertTrue(planned["runnable"], planned)
            self.assertLessEqual(len(planned["request"]["run_id"]), 96)
            self.assertEqual(planned["request"]["params_file"], str(params))
            result = self._execute(planned)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(
            json.loads((Path(result["run_dir"]) / "config" / params.name).read_text()),
            workflow_parameters,
        )
        self.assertEqual(
            (Path(result["run_dir"]) / "results" / "output" / "message.txt").read_text(),
            "workflow-owned",
        )

    def test_parameters_changing_after_approval_cannot_start_a_run(self) -> None:
        params = self.workspace / "params.json"
        params.write_text('{"message":"original"}', encoding="utf-8")
        with mock.patch.object(nextflow, "assess_readiness", return_value=self.readiness):
            plan = app.plan_nextflow(
                "custom_nextflow",
                str(self.workspace / "run"),
                params_file=str(params),
            )
            params.write_text('{"message":"changed"}', encoding="utf-8")
            result = approved_execution.execute_registered_plan(
                plan["plan_name"], plan["plan_id"], plan["plan_checksum"]
            )
            self.assertFalse(result["ok"])
            self.assertFalse((self.workspace / "run").exists())

    def test_readiness_for_another_engine_cannot_authorize_a_nextflow_run(self) -> None:
        readiness = {**self.readiness, "binding": "snakemake"}
        with mock.patch.object(nextflow, "assess_readiness", return_value=readiness):
            planned = app.plan_nextflow("custom_nextflow", str(self.workspace / "run"))

        self.assertFalse(planned["ok"])
        self.assertFalse((self.workspace / "run").exists())

    def test_remote_nextflow_deploys_source_and_uses_native_parameters(self) -> None:
        self._configure_ssh_target(executor="local_process", partition=None)
        params = self.root / "remote-params.yaml"
        content = "sample: sample.v2\ninput: /data/samples.csv\nreference: /data/genome\n"
        params.write_text(content, encoding="utf-8")
        readiness = {**self.readiness, "host": {"os": "linux", "arch": "arm64"}}
        with (
            target_input_transport(),
            mock.patch.object(nextflow, "assess_readiness", return_value=readiness),
        ):
            self._save_source("remote_nextflow")
            planned = app.plan_nextflow(
                "remote_nextflow",
                str(self.workspace / "run"),
                params_file=str(params),
                target_id="lab",
            )
            request = nextflow.approved_execution_request(
                NextflowRunPlan.model_validate(planned), planned["plan_checksum"]
            )

        self.assertTrue(planned["runnable"], planned)
        remote = planned["request"]["remote"]
        self.assertEqual(
            [item["destination"] for item in remote["staged_files"]],
            [f"{remote['run_dir']}/workflow/main.nf"],
        )
        self.assertIn(str(params), planned["command_argv"])
        self.assertIn(f"{remote['run_dir']}/workflow/main.nf", planned["command_argv"])
        self.assertEqual(
            request.inputs, {str(params): f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"}
        )
        self.assertEqual(params.read_text(), content)
        self.assertFalse((self.workspace / "run").exists())

    def test_generic_nextflow_does_not_claim_unimplemented_slurm_execution(self) -> None:
        self._configure_ssh_target()
        with (
            target_input_transport(),
            mock.patch.object(
                nextflow.readiness_service,
                "assess",
                side_effect=lambda requirements, *_args, **_kwargs: {
                    **self.readiness,
                    "ok": not requirements.blockers,
                    "status": "blocked" if requirements.blockers else "ready",
                    "blockers": requirements.blockers,
                },
            ),
        ):
            readiness = app.check_nextflow_readiness(
                "custom_nextflow",
                str(self.workspace / "run"),
                target_id="lab",
            )
        planned = app.plan_nextflow("custom_nextflow", str(self.workspace / "run"), target_id="lab")
        self.assertEqual(readiness.status, "blocked")
        self.assertFalse(planned["ok"])
        self.assertFalse((self.workspace / "run").exists())

    def test_remote_parameters_can_be_prepared_after_approval(self) -> None:
        self._configure_ssh_target(executor="local_process", partition=None)
        destination = self.root / "target-files" / "params.json"
        preparation = {
            "destination_dir": str(destination.parent),
            "downloads": [
                {
                    "relative_path": destination.name,
                    "url": "https://raw.githubusercontent.com/example/project/main/params.json",
                    "bytes": 2,
                    "sha256": "0" * 64,
                }
            ],
        }
        readiness = {**self.readiness, "host": {"os": "linux", "arch": "arm64"}}
        with (
            target_input_transport(),
            mock.patch.object(nextflow, "assess_readiness", return_value=readiness),
        ):
            planned = app.plan_nextflow(
                "custom_nextflow",
                str(self.workspace / "run"),
                target_id="lab",
                params_file=str(destination),
                preparation=preparation,
            )

        self.assertTrue(planned["runnable"], planned)
        self.assertIn(str(destination), planned["effects"]["remote_writes"])
        self.assertNotIn(str(destination), planned["effects"]["local_writes"])
        self.assertFalse(destination.exists())
        self.assertFalse((self.workspace / "run").exists())

    def test_preparation_downloads_are_visible_before_execution_approval(self) -> None:
        download = "https://raw.githubusercontent.com/example/project/main/reads.fastq"
        preparation = {
            "destination_dir": str(self.workspace / "prepared"),
            "downloads": [
                {
                    "relative_path": "reads.fastq",
                    "url": download,
                    "bytes": 4,
                    "sha256": "0" * 64,
                }
            ],
        }
        with mock.patch.object(nextflow, "assess_readiness", return_value=self.readiness):
            planned = app.plan_nextflow(
                "custom_nextflow",
                str(self.workspace / "run"),
                preparation=preparation,
            )

        self.assertTrue(any(download in item for item in planned["effects"]["downloads"]))
        self.assertTrue(any(download in item for item in planned["effects"]["network_access"]))
        self.assertFalse((self.workspace / "prepared").exists())


if __name__ == "__main__":
    unittest.main()
