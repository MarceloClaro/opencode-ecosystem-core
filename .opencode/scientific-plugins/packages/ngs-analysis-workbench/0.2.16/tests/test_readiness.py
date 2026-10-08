from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from daemon_test_case import DaemonTestCase  # noqa: E402
from ngs_workbench_daemon import remote_probe  # noqa: E402
from ngs_workbench_mcp import readiness_service  # noqa: E402
from ngs_workbench_mcp.compute_targets import ComputeTargetRef  # noqa: E402
from ngs_workbench_mcp.readiness import evaluate  # noqa: E402
from ngs_workbench_mcp.readiness.models import (  # noqa: E402
    RequirementSet,
    RuntimeRequirement,
)
from ngs_workbench_mcp.runtime import local as local_runtime  # noqa: E402
from ngs_workbench_mcp.runtime.models import (  # noqa: E402
    ControllerRuntimeCandidate,
    DockerRuntime,
    ManagedEnvironmentRuntime,
    RuntimeCommand,
    RuntimeCommandProbe,
    RuntimeEnvironmentSnapshot,
    RuntimePlatform,
)
from ngs_workbench_mcp.workflows import nextflow as nfcore  # noqa: E402
from ngs_workbench_mcp.workflows import snakemake  # noqa: E402


def _snapshot(
    workspace: Path,
    *commands: RuntimeCommand,
    controller_candidates: list[ControllerRuntimeCandidate] | None = None,
) -> RuntimeEnvironmentSnapshot:
    observed_at = datetime(2026, 8, 6, tzinfo=UTC)
    return RuntimeEnvironmentSnapshot(
        snapshot_id="runtime-0123456789abcdef0123456789abcdef",
        target=ComputeTargetRef(
            target_id="local",
            provider="ngs-analysis-workbench",
        ),
        observed_at=observed_at,
        expires_at=observed_at + timedelta(minutes=5),
        host=RuntimePlatform(os="darwin", arch="arm64"),
        commands=list(commands),
        docker=DockerRuntime(path=None, daemon_reachable=False),
        controller_candidates=controller_candidates or [],
    )


def _controller_requirement(controller: str = "snakemake") -> RequirementSet:
    return RequirementSet(
        binding="snakemake",
        pipeline="fastq_qc",
        requirements=[
            RuntimeRequirement(
                id=controller,
                layer="workflow_controller",
                capability="command",
                value=controller,
                source="request.binding",
            )
        ],
    )


class RemoteRuntimeTests(DaemonTestCase):
    def test_remote_managed_controller_is_available_without_host_path_activation(self) -> None:
        target = self._configure_ssh_target()
        environment = "/home/lab/.local/share/micromamba/envs/fastq-qc"
        observed = {
            "target_id": "lab",
            "config_hash": target["config_hash"],
            "host": {"hostname": "lab-node", "os": "linux", "arch": "x86_64"},
            "workspace": {
                "path": "/shared/ngs",
                "exists": True,
                "readable": True,
                "writable": True,
            },
            "commands": [
                {"executable": "snakemake", "path": None, "state": "missing"},
                {"executable": "fastqc", "path": None, "state": "missing"},
                {"executable": "multiqc", "path": None, "state": "missing"},
            ],
            "managed_environments": {
                "environments_scanned": 1,
                "environments": [
                    {
                        "name": "fastq-qc",
                        "path": environment,
                        "active": False,
                        "discovered_by": ["micromamba"],
                        "managers": [{"name": "micromamba", "path": "/usr/bin/micromamba"}],
                        "commands": [
                            {
                                "name": name,
                                "path": f"{environment}/bin/{name}",
                                "state": "ready",
                            }
                            for name in ("snakemake", "fastqc", "multiqc")
                        ],
                    }
                ],
            },
            "docker": {"path": None, "daemon_reachable": False},
            "scheduler": None,
        }
        original_request = local_runtime.daemon_client.request

        def inspect_request(path: str, payload: dict, **options: object) -> dict:
            if path == "/targets/inspect":
                return observed
            return original_request(path, payload, **options)

        with mock.patch.object(local_runtime.daemon_client, "request", side_effect=inspect_request):
            snapshot = local_runtime.inspect_runtime_environment(target_id="lab")

        candidate = snapshot.controller_candidates[0]
        self.assertEqual(candidate.controller, "snakemake")
        self.assertEqual(candidate.source, "managed_environment")
        self.assertEqual(candidate.executable_path, f"{environment}/bin/snakemake")
        self.assertTrue(candidate.recommended)
        self.assertEqual(
            candidate.launch_argv_prefix,
            ["/usr/bin/micromamba", "run", "--prefix", environment, "snakemake"],
        )
        requirements = _controller_requirement()
        requirements.requirements.extend(
            RuntimeRequirement(
                id=name,
                layer="task_software",
                capability="command",
                value=name,
                source="workflow.runtime",
            )
            for name in ("fastqc", "multiqc")
        )
        readiness = evaluate(requirements, snapshot)
        self.assertEqual(readiness.status, "ready")
        software = {command.name: command for command in readiness.commands}
        self.assertEqual(software["fastqc"].path, f"{environment}/bin/fastqc")
        self.assertEqual(software["multiqc"].path, f"{environment}/bin/multiqc")

        isolated = snapshot.model_copy(deep=True)
        isolated.commands = [
            command.model_copy(update={"path": "/usr/bin/fastqc", "state": "ready"})
            if command.name == "fastqc"
            else command
            for command in isolated.commands
        ]
        isolated.managed_environments.environments[0].commands = [
            command
            for command in isolated.managed_environments.environments[0].commands
            if command.name != "fastqc"
        ]
        unavailable = evaluate(requirements, isolated)

        self.assertEqual(unavailable.status, "blocked")
        self.assertIsNone(
            next(command for command in unavailable.commands if command.name == "fastqc").path
        )

    def test_remote_managed_environment_inspection_returns_before_its_deadline(self) -> None:
        managers = [
            {"executable": name, "path": f"/usr/bin/{name}", "state": "ready"}
            for name in ("conda", "mamba", "micromamba")
        ]
        with (
            mock.patch.object(remote_probe.time, "monotonic", side_effect=[98.0, 100.0]),
            mock.patch.object(
                remote_probe.subprocess,
                "run",
                return_value=mock.Mock(returncode=0, stdout='{"envs": []}'),
            ) as inspect,
        ):
            observed = remote_probe._managed_environments(managers, [], deadline=100.0)

        inspect.assert_called_once()
        self.assertTrue(observed["warnings"])
        snapshot = _snapshot(
            self.workspace,
            RuntimeCommand(name="snakemake", path=None, state="missing"),
        ).model_copy(update={"managed_environments": ManagedEnvironmentRuntime(**observed)})
        self.assertEqual(evaluate(_controller_requirement(), snapshot).status, "unknown")

    def test_workbench_uses_remote_host_facts_without_resolving_remote_paths_locally(self) -> None:
        target = self._configure_ssh_target()
        observed = {
            "target_id": "lab",
            "config_hash": target["config_hash"],
            "host": {"hostname": "lab-node", "os": "linux", "arch": "aarch64"},
            "workspace": {
                "path": "/shared/ngs",
                "exists": False,
                "readable": False,
                "writable": False,
            },
            "commands": [
                {
                    "executable": "snakemake",
                    "path": "/home/lab/bin/snakemake",
                    "state": "ready",
                    "version": "8.0.0",
                },
                {"executable": "sbatch", "path": None, "state": "missing"},
            ],
            "docker": {
                "path": None,
                "daemon_reachable": False,
                "message": "Docker CLI is missing",
            },
            "scheduler": {
                "kind": "slurm",
                "control_plane": "missing",
                "worker_readiness": "unknown",
                "shared_filesystem": "unknown",
            },
        }
        original_request = local_runtime.daemon_client.request

        def inspect_request(path: str, payload: dict, **options: object) -> dict:
            if path == "/targets/inspect":
                return observed
            return original_request(path, payload, **options)

        with (
            mock.patch.object(local_runtime.daemon_client, "request", side_effect=inspect_request),
            mock.patch.object(local_runtime, "_new_snapshot") as inspect_local,
        ):
            snapshot = local_runtime.inspect_runtime_environment(target_id="lab")
        inspect_local.assert_not_called()
        self.assertEqual((snapshot.host.os, snapshot.host.arch), ("linux", "arm64"))
        self.assertEqual(snapshot.target.target_id, "lab")
        self.assertEqual(
            snapshot.controller_candidates[0].executable_path, "/home/lab/bin/snakemake"
        )
        self.assertIn("Slurm worker", " ".join(snapshot.warnings))
        reused = local_runtime.resolve_runtime_environment(snapshot.snapshot_id, target_id="lab")
        self.assertEqual(reused.snapshot_id, snapshot.snapshot_id)

        observed["commands"].append(
            {"executable": "squeue", "path": "/usr/bin/squeue", "state": "ready"}
        )
        observed["scheduler"]["control_plane"] = "unavailable"
        with mock.patch.object(local_runtime.daemon_client, "request", side_effect=inspect_request):
            unavailable = local_runtime.resolve_runtime_environment(
                target_id="lab",
                command_probes=[
                    RuntimeCommandProbe(name="slurm-queue", executable="squeue", mode="version")
                ],
            )
        queue = next(command for command in unavailable.commands if command.name == "slurm-queue")
        self.assertEqual(queue.state, "broken")

        changed = self._configure_ssh_target(partition="gpu")
        observed["config_hash"] = changed["config_hash"]
        observed["host"]["arch"] = "x86_64"
        with mock.patch.object(local_runtime.daemon_client, "request", side_effect=inspect_request):
            updated = local_runtime.resolve_runtime_environment(
                snapshot.snapshot_id,
                target_id="lab",
            )
        self.assertEqual(updated.host.arch, "amd64")
        self.assertNotEqual(updated.snapshot_id, snapshot.snapshot_id)


class NfcoreRequirementTests(unittest.TestCase):
    def test_standard_docker_profile_resolves_binding_requirements_without_probing(self) -> None:
        result = nfcore.resolve_runtime_requirements(
            "rnaseq",
            "test,docker",
            workflow="nf-core/rnaseq",
            revision="3.26.0",
        )

        self.assertEqual(result.blockers, [])
        self.assertEqual(result.unknowns, [])
        self.assertEqual(
            [(item.id, item.layer, item.source) for item in result.requirements],
            [
                ("nextflow", "workflow_controller", "request.binding"),
                ("docker-command", "task_environment", "request.profile"),
                ("docker-daemon", "task_environment", "request.profile"),
            ],
        )

    def test_custom_profile_preserves_unresolved_task_environment(self) -> None:
        result = nfcore.resolve_runtime_requirements("rnaseq", "mylab")

        self.assertEqual(result.blockers, [])
        self.assertIn("task software environment is unresolved", result.unknowns[0])


class SnakemakeRequirementTests(unittest.TestCase):
    def test_snakemake_workflow_requires_the_snakemake_controller(self) -> None:
        config = PLUGIN_ROOT / "workflows" / "fastq_qc" / "config" / "config.json"

        result = snakemake.resolve_runtime_requirements("example", config)

        self.assertEqual(result.blockers, [])
        self.assertEqual(result.unknowns, [])
        self.assertEqual([item.id for item in result.requirements], ["snakemake"])


class RuntimeEnvironmentDiscoveryTests(unittest.TestCase):
    def test_discovers_controllers_in_inactive_conda_env_without_executing_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            conda_environment = root / "envs" / "workflow"
            bin_dir = conda_environment / "bin"
            metadata_dir = conda_environment / "conda-meta"
            bin_dir.mkdir(parents=True)
            metadata_dir.mkdir()

            execution_marker = root / "snakemake-was-executed"
            snakemake_executable = bin_dir / "snakemake"
            snakemake_executable.write_text(
                f"#!/bin/sh\nprintf ran > {execution_marker}\n",
                encoding="utf-8",
            )
            snakemake_executable.chmod(0o755)
            nextflow_marker = root / "nextflow-was-executed"
            nextflow_executable = bin_dir / "nextflow"
            nextflow_executable.write_text(
                f"#!/bin/sh\nprintf ran > {nextflow_marker}\n",
                encoding="utf-8",
            )
            nextflow_executable.chmod(0o755)
            (metadata_dir / "snakemake-minimal-9.24.0-0.json").write_text(
                json.dumps(
                    {
                        "name": "snakemake-minimal",
                        "version": "9.24.0",
                        "build": "pyhdfd78af_0",
                        "channel": "bioconda",
                        "subdir": "noarch",
                    }
                ),
                encoding="utf-8",
            )
            (metadata_dir / "nextflow-26.04.6-0.json").write_text(
                json.dumps(
                    {
                        "name": "nextflow",
                        "version": "26.04.6",
                        "build": "h2a3209d_0",
                        "channel": "bioconda",
                        "subdir": "noarch",
                    }
                ),
                encoding="utf-8",
            )
            (metadata_dir / "python-3.13.5-0.json").write_text(
                json.dumps(
                    {
                        "name": "python",
                        "version": "3.13.5",
                        "build": "h81fe080_0_cpython",
                        "channel": "conda-forge",
                        "subdir": "osx-arm64",
                    }
                ),
                encoding="utf-8",
            )

            manager = root / "conda"
            manager.write_text(
                f"#!{sys.executable}\n"
                "import json\n"
                f"print(json.dumps({{'envs': [{str(conda_environment)!r}]}}))\n",
                encoding="utf-8",
            )
            manager.chmod(0o755)
            commands = [RuntimeCommand(name="conda", path=str(manager), state="ready")]

            with mock.patch.dict(
                local_runtime.os.environ,
                {"CONDA_PREFIX": "", "CONDA_DEFAULT_ENV": ""},
            ):
                result = local_runtime._discover_managed_environment_runtime(
                    commands,
                    RuntimePlatform(os="darwin", arch="arm64"),
                )
            self.assertFalse(execution_marker.exists())
            self.assertFalse(nextflow_marker.exists())

        self.assertEqual(result.environments_scanned, 1)
        self.assertFalse(result.truncated)
        self.assertEqual(len(result.environments), 1)
        environment = result.environments[0]
        self.assertFalse(environment.active)
        self.assertEqual(environment.discovered_by, ["conda"])
        self.assertEqual(environment.platform, RuntimePlatform(os="darwin", arch="arm64"))
        self.assertEqual(environment.platform_subdirs, ["noarch", "osx-arm64"])
        self.assertEqual(
            [(package.name, package.subdir) for package in environment.packages],
            [
                ("nextflow", "noarch"),
                ("python", "osx-arm64"),
                ("snakemake-minimal", "noarch"),
            ],
        )
        self.assertTrue(environment.platform_matches_host)
        snakemake = next(command for command in environment.commands if command.name == "snakemake")
        self.assertEqual(snakemake.state, "ready")
        self.assertEqual(snakemake.path, str(snakemake_executable.resolve()))
        self.assertEqual(snakemake.version, "9.24.0")
        nextflow = next(command for command in environment.commands if command.name == "nextflow")
        self.assertEqual(nextflow.state, "ready")
        self.assertEqual(nextflow.path, str(nextflow_executable.resolve()))
        self.assertEqual(nextflow.version, "26.04.6")

        candidates = local_runtime._controller_candidates(
            commands,
            result,
            RuntimePlatform(os="darwin", arch="arm64"),
        )
        snakemake_candidate = next(
            candidate for candidate in candidates if candidate.controller == "snakemake"
        )
        self.assertTrue(snakemake_candidate.recommended)
        self.assertEqual(snakemake_candidate.source, "managed_environment")
        self.assertEqual(snakemake_candidate.manager, "conda")
        self.assertEqual(
            snakemake_candidate.launch_argv_prefix,
            [
                str(manager),
                "run",
                "--prefix",
                str(conda_environment.resolve()),
                "snakemake",
            ],
        )

    def test_discovers_locked_pixi_project_and_binds_non_mutating_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            environment_path = workspace / ".pixi" / "envs" / "default"
            bin_dir = environment_path / "bin"
            metadata_dir = environment_path / "conda-meta"
            bin_dir.mkdir(parents=True)
            metadata_dir.mkdir()
            (workspace / "pixi.toml").write_text(
                "[workspace]\nchannels = ['conda-forge', 'bioconda']\n"
                "platforms = ['osx-arm64']\n\n"
                "[dependencies]\nsnakemake-minimal = '==9.24.0'\n",
                encoding="utf-8",
            )
            (workspace / "pixi.lock").write_text("version: 6\n", encoding="utf-8")
            execution_marker = root / "snakemake-was-executed"
            snakemake_executable = bin_dir / "snakemake"
            snakemake_executable.write_text(
                f"#!/bin/sh\nprintf ran > {execution_marker}\n",
                encoding="utf-8",
            )
            snakemake_executable.chmod(0o755)
            (metadata_dir / "snakemake-minimal-9.24.0-0.json").write_text(
                json.dumps(
                    {
                        "name": "snakemake-minimal",
                        "version": "9.24.0",
                        "channel": "bioconda",
                        "subdir": "noarch",
                    }
                ),
                encoding="utf-8",
            )
            (metadata_dir / "python-3.13.5-0.json").write_text(
                json.dumps(
                    {
                        "name": "python",
                        "version": "3.13.5",
                        "channel": "conda-forge",
                        "subdir": "osx-arm64",
                    }
                ),
                encoding="utf-8",
            )
            pixi = root / "pixi"
            pixi.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
            pixi.chmod(0o755)
            commands = [RuntimeCommand(name="pixi", path=str(pixi), state="ready")]
            host = RuntimePlatform(os="darwin", arch="arm64")

            with mock.patch.dict(
                local_runtime.os.environ,
                {
                    "PIXI_HOME": str(root / "pixi-home"),
                    "CONDA_PREFIX": "",
                    "CONDA_DEFAULT_ENV": "",
                },
            ):
                environments = local_runtime._discover_managed_environment_runtime(
                    commands,
                    host,
                    workspace,
                )
                candidates = local_runtime._controller_candidates(
                    commands,
                    environments,
                    host,
                )

            self.assertFalse(execution_marker.exists())

        self.assertEqual(len(environments.environments), 1)
        environment = environments.environments[0]
        self.assertEqual(environment.discovered_by, ["pixi"])
        self.assertEqual(environment.lockfile_path, str((workspace / "pixi.lock").resolve()))
        self.assertEqual(environment.declared_channels, ["conda-forge", "bioconda"])
        candidate = next(item for item in candidates if item.controller == "snakemake")
        self.assertTrue(candidate.recommended)
        self.assertEqual(candidate.manager, "pixi")
        self.assertEqual(candidate.lockfile_path, environment.lockfile_path)
        self.assertEqual(
            candidate.launch_argv_prefix,
            [
                str(pixi),
                "run",
                "--as-is",
                "--manifest-path",
                str((workspace / "pixi.toml").resolve()),
                "--environment",
                "default",
                "--executable",
                "snakemake",
            ],
        )

    def test_marks_foreign_conda_platform_without_executing_controller(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            environment_path = Path(temporary)
            (environment_path / "bin").mkdir()
            metadata_dir = environment_path / "conda-meta"
            metadata_dir.mkdir()
            execution_marker = environment_path / "controller-was-executed"
            controller = environment_path / "bin" / "nextflow"
            controller.write_text(
                f"#!/bin/sh\nprintf ran > {execution_marker}\n",
                encoding="utf-8",
            )
            controller.chmod(0o755)
            (metadata_dir / "nextflow-26.04.6-0.json").write_text(
                json.dumps({"name": "nextflow", "version": "26.04.6", "subdir": "noarch"}),
                encoding="utf-8",
            )
            (metadata_dir / "openjdk-21.0.7-0.json").write_text(
                json.dumps({"name": "openjdk", "version": "21.0.7", "subdir": "linux-64"}),
                encoding="utf-8",
            )

            environment, warnings = local_runtime._managed_environment(
                environment_path,
                active=False,
                discovered_by={"conda"},
                host=RuntimePlatform(os="darwin", arch="arm64"),
            )
            self.assertFalse(execution_marker.exists())

        self.assertEqual(warnings, [])
        self.assertEqual(environment.platform, RuntimePlatform(os="linux", arch="amd64"))
        self.assertFalse(environment.platform_matches_host)
        self.assertEqual(
            [(package.name, package.subdir) for package in environment.packages],
            [("nextflow", "noarch"), ("openjdk", "linux-64")],
        )

    def test_keeps_noarch_only_conda_platform_unknown(self) -> None:
        platform_result, warning = local_runtime._conda_platform(["noarch"])

        self.assertIsNone(platform_result)
        self.assertIsNone(warning)


class ReadinessEvaluationTests(unittest.TestCase):
    def test_truncated_environment_discovery_keeps_controller_availability_unknown(self) -> None:
        requirements = _controller_requirement()
        requirements.requirements.append(
            RuntimeRequirement(
                id="fastqc",
                layer="task_software",
                capability="command",
                value="fastqc",
                source="workflow contract",
            )
        )
        snapshot = _snapshot(
            Path("/workspace"),
            RuntimeCommand(name="snakemake", path=None, state="missing"),
            RuntimeCommand(name="fastqc", path=None, state="missing"),
        ).model_copy(update={"managed_environments": ManagedEnvironmentRuntime(truncated=True)})

        result = evaluate(requirements, snapshot)

        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.blockers, [])
        self.assertIsNone(result.selected_controller)

    def test_managed_controller_is_selected_instead_of_host_path(self) -> None:
        workspace = Path("/workspace")
        managed = ControllerRuntimeCandidate(
            candidate_id=f"controller-{'1' * 32}",
            controller="snakemake",
            source="managed_environment",
            manager="mamba",
            executable_path="/env/bin/snakemake",
            environment_path="/env",
            platform=RuntimePlatform(os="darwin", arch="arm64"),
            platform_matches_host=True,
            launch_argv_prefix=[
                "/opt/mamba",
                "run",
                "--prefix",
                "/env",
                "snakemake",
            ],
            recommended=True,
            recommendation_reason="managed environment",
        )
        host_path = ControllerRuntimeCandidate(
            candidate_id=f"controller-{'2' * 32}",
            controller="snakemake",
            source="host_path",
            executable_path="/usr/local/bin/snakemake",
            platform=RuntimePlatform(os="darwin", arch="arm64"),
            platform_matches_host=True,
            active=True,
            launch_argv_prefix=["/usr/local/bin/snakemake"],
            recommended=False,
            recommendation_reason="explicit fallback only",
        )

        result = evaluate(
            _controller_requirement(),
            _snapshot(
                workspace,
                RuntimeCommand(
                    name="snakemake",
                    path="/usr/local/bin/snakemake",
                    state="ready",
                ),
                controller_candidates=[host_path, managed],
            ),
        )

        self.assertEqual(result.status, "ready")
        self.assertEqual(result.selected_controller, managed)
        self.assertTrue(any("no observed lockfile" in warning for warning in result.warnings))

    def test_host_path_requires_explicit_candidate_selection(self) -> None:
        workspace = Path("/workspace")
        host_path = ControllerRuntimeCandidate(
            candidate_id=f"controller-{'3' * 32}",
            controller="snakemake",
            source="host_path",
            executable_path="/usr/local/bin/snakemake",
            platform=RuntimePlatform(os="darwin", arch="arm64"),
            platform_matches_host=True,
            active=True,
            launch_argv_prefix=["/usr/local/bin/snakemake"],
            recommended=False,
            recommendation_reason="explicit fallback only",
        )
        snapshot = _snapshot(
            workspace,
            RuntimeCommand(
                name="snakemake",
                path="/usr/local/bin/snakemake",
                state="ready",
            ),
            controller_candidates=[host_path],
        )

        unresolved = evaluate(_controller_requirement(), snapshot)
        selected = evaluate(
            _controller_requirement(),
            snapshot,
            controller_candidate_id=host_path.candidate_id,
        )

        self.assertEqual(unresolved.status, "unknown")
        self.assertIn("obtain user confirmation", unresolved.unknowns[0])
        self.assertEqual(selected.status, "ready")
        self.assertEqual(selected.selected_controller, host_path)
        self.assertTrue(any("not reproducibly bound" in warning for warning in selected.warnings))

    def test_multiple_managed_environments_require_an_exact_choice(self) -> None:
        workspace = Path("/workspace")
        candidates = [
            ControllerRuntimeCandidate(
                candidate_id=f"controller-{digit * 32}",
                controller="snakemake",
                source="managed_environment",
                manager=manager,
                executable_path=f"/{manager}/bin/snakemake",
                environment_path=f"/{manager}",
                platform=RuntimePlatform(os="darwin", arch="arm64"),
                platform_matches_host=True,
                launch_argv_prefix=[f"/opt/{manager}", "run", "snakemake"],
                recommended=True,
                recommendation_reason="managed environment",
            )
            for digit, manager in (("4", "conda"), ("5", "pixi"))
        ]

        result = evaluate(
            _controller_requirement(),
            _snapshot(workspace, controller_candidates=candidates),
        )

        self.assertEqual(result.status, "unknown")
        self.assertIn("multiple recommended", result.unknowns[0])
        self.assertTrue(
            all(candidate.candidate_id in result.unknowns[0] for candidate in candidates)
        )

    def test_presence_probe_does_not_execute_request_sourced_lookalike_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "docker"
            executable.write_text("not executed", encoding="utf-8")
            executable.chmod(0o755)
            probe = RuntimeCommandProbe(
                name="fastqc",
                executable=str(executable),
                mode="presence",
            )
            with mock.patch.object(local_runtime.subprocess, "run") as run:
                result = local_runtime._probe_command(probe)

        self.assertEqual(result.state, "ready")
        self.assertEqual(result.path, str(executable))
        run.assert_not_called()

    def test_known_missing_executable_is_blocked(self) -> None:
        workspace = Path("/workspace")
        requirements = RequirementSet(
            binding="snakemake",
            pipeline="fastq_qc",
            requirements=[
                RuntimeRequirement(
                    id="fastqc",
                    layer="task_software",
                    capability="command",
                    value="fastqc",
                    source="workflow contract",
                )
            ],
        )
        result = evaluate(
            requirements,
            _snapshot(workspace, RuntimeCommand(name="fastqc", path=None, state="missing")),
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.unknowns, [])
        self.assertEqual(result.blockers, ["required executable is not available: fastqc"])

    def test_absent_observation_is_unknown_instead_of_guessed(self) -> None:
        workspace = Path("/workspace")
        requirements = RequirementSet(
            binding="snakemake",
            pipeline="fastq_qc",
            requirements=[
                RuntimeRequirement(
                    id="fastqc",
                    layer="task_software",
                    capability="command",
                    value="fastqc",
                    source="workflow contract",
                )
            ],
        )
        result = evaluate(requirements, _snapshot(workspace))

        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.blockers, [])
        self.assertEqual(result.unknowns, ["runtime did not observe required executable: fastqc"])

    def test_orchestration_observes_a_real_requested_executable(self) -> None:
        requirements = RequirementSet(
            binding="snakemake",
            pipeline="test",
            requirements=[
                RuntimeRequirement(
                    id="current-python",
                    layer="task_software",
                    capability="command",
                    value=sys.executable,
                    source="test request",
                )
            ],
        )
        result = readiness_service.assess(requirements)

        observation = next(
            command for command in result.commands if command.name == "current-python"
        )
        self.assertEqual(result.status, "ready")
        self.assertEqual(result.target.target_id, "local")
        self.assertEqual(observation.state, "ready")
        self.assertEqual(observation.path, sys.executable)

    def test_slurm_control_plane_is_required_but_worker_uncertainty_is_not_blocking(self) -> None:
        workspace = Path("/workspace")
        requirements = RequirementSet(binding="nextflow", pipeline="fastq_qc", requirements=[])
        snapshot = _snapshot(
            workspace,
            RuntimeCommand(name="slurm-submit", path="/usr/bin/sbatch", state="ready"),
            RuntimeCommand(name="slurm-queue", path="/usr/bin/squeue", state="ready"),
        )
        snapshot.warnings.append("Slurm worker runtime and shared filesystem remain unknown")
        with (
            mock.patch.object(
                readiness_service,
                "resolve_compute_target",
                return_value=mock.Mock(executor="slurm"),
            ),
            mock.patch.object(
                readiness_service.runtime,
                "resolve_runtime_environment",
                return_value=snapshot,
            ),
        ):
            result = readiness_service.assess(requirements, target_id="cluster")
        self.assertEqual(result.status, "ready")
        self.assertEqual(result.unknowns, [])
        self.assertTrue(any("worker" in warning for warning in result.warnings))
        self.assertEqual(
            [requirement.id for requirement in result.requirements],
            ["slurm-submit", "slurm-queue"],
        )


if __name__ == "__main__":
    unittest.main()
