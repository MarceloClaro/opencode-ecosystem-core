"""Inspect and cache facts about the local execution environment."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tomllib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from ngs_workbench_daemon import client as daemon_client
from ngs_workbench_daemon.hashing import sha256_hex

from ..compute_targets import ComputeTarget, ComputeTargetRef, resolve_compute_target
from .models import (
    CondaPackage,
    ControllerRuntimeCandidate,
    DockerRuntime,
    EnvironmentManager,
    EnvironmentManagerName,
    ManagedEnvironment,
    ManagedEnvironmentRuntime,
    RuntimeCommand,
    RuntimeCommandProbe,
    RuntimeEnvironmentSnapshot,
    RuntimePlatform,
)

SNAPSHOT_TTL = timedelta(minutes=5)
PROBE_TIMEOUT_SECONDS = 5.0
MAX_MANAGED_ENVIRONMENTS = 50

_VERSION_ARGS: dict[str, tuple[str, ...]] = {
    "nextflow": ("-version",),
    "snakemake": ("--version",),
    "java": ("-version",),
    "docker": ("--version",),
    "conda": ("--version",),
    "mamba": ("--version",),
    "micromamba": ("--version",),
    "pixi": ("--version",),
    "podman": ("--version",),
    "apptainer": ("--version",),
    "singularity": ("--version",),
}
_SNAPSHOTS: dict[str, RuntimeEnvironmentSnapshot] = {}
_SNAPSHOT_PROBES: dict[str, tuple[tuple[RuntimeCommandProbe, ...], str | None]] = {}
_CONDA_ENV_LIST_MANAGERS = frozenset({"conda", "mamba", "micromamba"})
_MANAGED_ENVIRONMENT_MANAGERS = frozenset({"pixi", *_CONDA_ENV_LIST_MANAGERS})
_WORKFLOW_CONTROLLER_COMMANDS = ("nextflow", "snakemake")
_WORKFLOW_CONTROLLER_CONDA_PACKAGES = frozenset({"nextflow", "snakemake", "snakemake-minimal"})
_CONDA_PLATFORM_MARKER_PACKAGES = frozenset({"openjdk", "python"})
_CONDA_METADATA_PACKAGES = _WORKFLOW_CONTROLLER_CONDA_PACKAGES | _CONDA_PLATFORM_MARKER_PACKAGES
_CONDA_SUBDIR_OS = {"linux": "linux", "osx": "darwin", "win": "windows"}
_CONDA_SUBDIR_ARCH = {
    "32": "x86",
    "64": "amd64",
    "aarch64": "arm64",
    "arm64": "arm64",
    "ppc64le": "ppc64le",
    "riscv64": "riscv64",
    "s390x": "s390x",
}


@dataclass(frozen=True)
class _CondaMetadata:
    packages: list[CondaPackage]
    platform_subdirs: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class _PixiEnvironmentSpec:
    path: Path
    manifest_path: Path
    lockfile_path: Path | None
    channels: list[str]
    exposed_commands: dict[str, Path]


def _normalized_arch(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"aarch64", "arm64"}:
        return "arm64"
    if normalized in {"amd64", "x86_64", "x64"}:
        return "amd64"
    return normalized or "unknown"


def _probe_environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment["NXF_OFFLINE"] = "true"
    return environment


def _conda_probe_environment() -> dict[str, str]:
    environment = _probe_environment()
    environment["CONDA_OFFLINE"] = "true"
    environment["CONDA_NO_PLUGINS"] = "true"
    return environment


def _output_lines(result: subprocess.CompletedProcess[str]) -> list[str]:
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    return [line.strip() for line in combined.splitlines() if line.strip()]


def _first_output_line(result: subprocess.CompletedProcess[str]) -> str | None:
    return next(iter(_output_lines(result)), None)


def _version_output(executable: str, result: subprocess.CompletedProcess[str]) -> str | None:
    lines = _output_lines(result)
    if Path(executable).name == "nextflow":
        return next((line for line in lines if line.lower().startswith("version ")), None)
    return next(iter(lines), None)


def _resolved_executable(executable: str) -> str | None:
    if os.sep in executable or (os.altsep and os.altsep in executable):
        candidate = Path(executable).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        return None
    return shutil.which(executable)


def _probe_command(probe: RuntimeCommandProbe) -> RuntimeCommand:
    path = _resolved_executable(probe.executable)
    if path is None:
        return RuntimeCommand(
            name=probe.name,
            path=None,
            state="missing",
            message=f"command is not available: {probe.executable}",
        )
    version_args = (
        _VERSION_ARGS.get(Path(probe.executable).name) if probe.mode == "version" else None
    )
    if version_args is None:
        return RuntimeCommand(name=probe.name, path=path, state="ready")
    try:
        result = subprocess.run(
            [path, *version_args],
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
            check=False,
            env=_probe_environment(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return RuntimeCommand(name=probe.name, path=path, state="broken", message=str(exc))
    output = _version_output(probe.executable, result)
    if result.returncode != 0:
        return RuntimeCommand(
            name=probe.name,
            path=path,
            state="broken",
            message=output or f"version probe exited with status {result.returncode}",
        )
    return RuntimeCommand(name=probe.name, path=path, state="ready", version=output)


def _probe_docker(command: RuntimeCommand) -> DockerRuntime:
    if command.path is None:
        return DockerRuntime(path=None, daemon_reachable=False, message="Docker CLI is missing")
    if command.state != "ready":
        return DockerRuntime(
            path=command.path,
            daemon_reachable=False,
            message=command.message or "Docker CLI version probe failed",
        )
    context, endpoint, endpoint_is_local, endpoint_message = _probe_docker_endpoint(command)
    details = {
        "path": command.path,
        "context": context,
        "endpoint": endpoint,
        "endpoint_is_local": endpoint_is_local,
    }
    if endpoint_is_local is False:
        return DockerRuntime(
            **details,
            daemon_reachable=False,
            message="remote Docker endpoint was not contacted",
        )
    try:
        result = subprocess.run(
            [command.path, "info", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
            check=False,
            env=_probe_environment(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return DockerRuntime(**details, daemon_reachable=False, message=str(exc))
    if result.returncode != 0:
        return DockerRuntime(
            **details,
            daemon_reachable=False,
            message=_first_output_line(result)
            or f"docker info exited with status {result.returncode}",
        )
    try:
        info = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        return DockerRuntime(
            **details,
            daemon_reachable=True,
            message=f"Docker daemon responded, but its metadata was invalid: {exc}",
        )
    if not isinstance(info, dict):
        return DockerRuntime(
            **details,
            daemon_reachable=True,
            message="Docker daemon responded, but its metadata was not an object",
        )
    return DockerRuntime(
        **details,
        daemon_reachable=True,
        server_version=_optional_string(info.get("ServerVersion")),
        server_os=_optional_string(info.get("OSType")),
        server_arch=(
            _normalized_arch(info["Architecture"])
            if isinstance(info.get("Architecture"), str) and info["Architecture"]
            else None
        ),
        message=endpoint_message,
    )


def _probe_docker_endpoint(
    command: RuntimeCommand,
) -> tuple[str | None, str | None, bool | None, str | None]:
    """Resolve the endpoint Docker will use without contacting the daemon."""
    assert command.path is not None
    environment = _probe_environment()
    configured_context = environment.get("DOCKER_CONTEXT", "").strip()
    configured_host = environment.get("DOCKER_HOST", "").strip()
    if not configured_context and configured_host:
        return None, configured_host, _docker_endpoint_is_local(configured_host), None

    context = configured_context
    if not context:
        try:
            result = subprocess.run(
                [command.path, "context", "show"],
                capture_output=True,
                text=True,
                timeout=PROBE_TIMEOUT_SECONDS,
                check=False,
                env=environment,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, None, None, f"Docker context probe failed: {exc}"
        context = _first_output_line(result) or ""
        if result.returncode != 0 or not context:
            message = _first_output_line(result) or f"exited with status {result.returncode}"
            return None, None, None, f"Docker context probe failed: {message}"

    try:
        result = subprocess.run(
            [
                command.path,
                "context",
                "inspect",
                "--format",
                "{{json .Endpoints.docker.Host}}",
                context,
            ],
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
            check=False,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return context, None, None, f"Docker endpoint probe failed: {exc}"
    if result.returncode != 0:
        message = _first_output_line(result) or f"exited with status {result.returncode}"
        return context, None, None, f"Docker endpoint probe failed: {message}"
    try:
        endpoint = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        return context, None, None, f"Docker endpoint metadata was invalid: {exc}"
    if not isinstance(endpoint, str) or not endpoint:
        return context, None, None, "Docker endpoint metadata was not a string"
    return context, endpoint, _docker_endpoint_is_local(endpoint), None


def _docker_endpoint_is_local(endpoint: str) -> bool:
    return endpoint.lower().startswith(("unix://", "npipe://"))


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _environment_executable(environment: Path, executable: str) -> Path | None:
    candidates = (
        environment / "bin" / executable,
        environment / "Scripts" / executable,
        environment / "Scripts" / f"{executable}.exe",
        environment / f"{executable}.exe",
    )
    for candidate in candidates:
        if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
            return candidate
    return None


def _exposed_executable(directory: Path, executable: str) -> Path | None:
    candidates = (
        directory / executable,
        directory / f"{executable}.exe",
        directory / f"{executable}.bat",
        directory / f"{executable}.cmd",
    )
    for candidate in candidates:
        if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
            return candidate
    return None


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _read_toml_mapping(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, str(exc)
    return value, None


def _pixi_home() -> Path:
    configured = os.environ.get("PIXI_HOME", "").strip()
    return Path(configured).expanduser() if configured else Path.home() / ".pixi"


def _pixi_global_manifest_candidates() -> list[Path]:
    pixi_home = _pixi_home()
    candidates = [pixi_home / "manifests" / "pixi-global.toml"]
    if os.environ.get("PIXI_HOME", "").strip():
        return candidates
    xdg_config = os.environ.get("XDG_CONFIG_HOME", "").strip()
    if sys.platform == "darwin":
        candidates.extend(
            [
                Path.home()
                / "Library"
                / "Application Support"
                / "pixi"
                / "manifests"
                / "pixi-global.toml",
            ]
        )
    elif xdg_config:
        candidates.append(Path(xdg_config).expanduser() / "pixi" / "manifests" / "pixi-global.toml")
    else:
        candidates.append(Path.home() / ".config" / "pixi" / "manifests" / "pixi-global.toml")
    return candidates


def _pixi_global_environments() -> tuple[list[_PixiEnvironmentSpec], list[str]]:
    manifest_path = next(
        (path for path in _pixi_global_manifest_candidates() if path.is_file()),
        None,
    )
    if manifest_path is None:
        return [], []
    payload, error = _read_toml_mapping(manifest_path)
    if payload is None:
        return [], [f"could not read Pixi global manifest {manifest_path}: {error}"]
    environments = payload.get("envs")
    if not isinstance(environments, dict):
        return [], [f"Pixi global manifest did not contain an envs table: {manifest_path}"]

    pixi_home = _pixi_home().resolve(strict=False)
    specs: list[_PixiEnvironmentSpec] = []
    for name, raw_environment in environments.items():
        if not isinstance(name, str) or not isinstance(raw_environment, dict):
            continue
        exposed = raw_environment.get("exposed")
        exposed_commands: dict[str, Path] = {}
        if isinstance(exposed, dict):
            for exposed_name, environment_command in exposed.items():
                if not isinstance(exposed_name, str) or not isinstance(environment_command, str):
                    continue
                exposed_path = _exposed_executable(pixi_home / "bin", exposed_name)
                if exposed_path is not None:
                    exposed_commands[environment_command] = exposed_path.resolve(strict=False)
        specs.append(
            _PixiEnvironmentSpec(
                path=(pixi_home / "envs" / name).resolve(strict=False),
                manifest_path=manifest_path.resolve(strict=False),
                lockfile_path=None,
                channels=_string_list(raw_environment.get("channels")),
                exposed_commands=exposed_commands,
            )
        )
    return specs, []


def _pixi_project_environment(workspace: Path) -> tuple[list[_PixiEnvironmentSpec], list[str]]:
    project_manifest: Path | None = None
    pixi_payload: dict[str, Any] | None = None
    warnings: list[str] = []
    for parent in (workspace, *workspace.parents):
        for candidate in (parent / "pixi.toml", parent / "pyproject.toml"):
            if not candidate.is_file():
                continue
            payload, error = _read_toml_mapping(candidate)
            if payload is None:
                warnings.append(f"could not read Pixi project manifest {candidate}: {error}")
                continue
            if candidate.name == "pixi.toml":
                project_manifest = candidate
                pixi_payload = payload
                break
            tool = payload.get("tool")
            pixi = tool.get("pixi") if isinstance(tool, dict) else None
            if isinstance(pixi, dict):
                project_manifest = candidate
                pixi_payload = pixi
                break
        if project_manifest is not None:
            break
    if project_manifest is None or pixi_payload is None:
        return [], warnings
    workspace_payload = pixi_payload.get("workspace")
    channels = (
        _string_list(workspace_payload.get("channels"))
        if isinstance(workspace_payload, dict)
        else []
    )
    environments = pixi_payload.get("environments")
    environment_names = ["default"]
    if isinstance(environments, dict):
        environment_names.extend(
            name for name in environments if isinstance(name, str) and name != "default"
        )
    project_root = project_manifest.parent.resolve(strict=False)
    lockfile = project_root / "pixi.lock"
    return (
        [
            _PixiEnvironmentSpec(
                path=(project_root / ".pixi" / "envs" / name).resolve(strict=False),
                manifest_path=project_manifest.resolve(strict=False),
                lockfile_path=lockfile.resolve(strict=False) if lockfile.is_file() else None,
                channels=channels,
                exposed_commands={},
            )
            for name in environment_names
        ],
        warnings,
    )


def _conda_metadata(environment: Path) -> _CondaMetadata:
    metadata_dir = environment / "conda-meta"
    if not metadata_dir.is_dir():
        return _CondaMetadata([], [], [])

    packages: list[CondaPackage] = []
    platform_subdirs: set[str] = set()
    warnings: list[str] = []
    for metadata_path in sorted(metadata_dir.glob("*.json")):
        if not any(
            metadata_path.name.startswith(f"{package_name}-")
            for package_name in _CONDA_METADATA_PACKAGES
        ):
            continue
        try:
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"could not read Conda metadata {metadata_path}: {exc}")
            continue
        if not isinstance(payload, dict) or payload.get("name") not in _CONDA_METADATA_PACKAGES:
            continue
        name = str(payload["name"])
        subdir = _optional_string(payload.get("subdir"))
        if subdir is not None:
            platform_subdirs.add(subdir)
        packages.append(
            CondaPackage(
                name=name,
                version=_optional_string(payload.get("version")),
                build=_optional_string(payload.get("build")),
                channel=_optional_string(payload.get("channel")),
                subdir=subdir,
            )
        )
    return _CondaMetadata(
        packages=packages,
        platform_subdirs=sorted(platform_subdirs),
        warnings=warnings,
    )


def _conda_platform(
    subdirs: list[str],
) -> tuple[RuntimePlatform | None, str | None]:
    platforms: set[tuple[str, str]] = set()
    unknown: list[str] = []
    for subdir in subdirs:
        if subdir == "noarch":
            continue
        os_token, separator, arch_token = subdir.partition("-")
        normalized_os = _CONDA_SUBDIR_OS.get(os_token)
        normalized_arch = _CONDA_SUBDIR_ARCH.get(arch_token) if separator else None
        if normalized_os is None or normalized_arch is None:
            unknown.append(subdir)
            continue
        platforms.add((normalized_os, normalized_arch))
    if unknown:
        return None, f"unrecognized Conda platform subdirs: {', '.join(unknown)}"
    if len(platforms) > 1:
        rendered = ", ".join(f"{os_name}/{arch}" for os_name, arch in sorted(platforms))
        return None, f"conflicting Conda platforms were observed: {rendered}"
    if not platforms:
        return None, None
    os_name, arch = next(iter(platforms))
    return RuntimePlatform(os=os_name, arch=arch), None


def _managed_environment(
    path: Path,
    *,
    active: bool,
    discovered_by: set[str],
    manager_paths: dict[EnvironmentManagerName, str] | None = None,
    pixi_spec: _PixiEnvironmentSpec | None = None,
    host: RuntimePlatform,
) -> tuple[ManagedEnvironment, list[str]]:
    metadata = _conda_metadata(path)
    packages = metadata.packages
    warnings = list(metadata.warnings)
    conda_platform, platform_warning = _conda_platform(metadata.platform_subdirs)
    if platform_warning is not None:
        warnings.append(f"{path}: {platform_warning}")
    package_versions = {package.name: package.version for package in packages}
    commands: list[RuntimeCommand] = []
    for name in _WORKFLOW_CONTROLLER_COMMANDS:
        executable = _environment_executable(path, name)
        version = package_versions.get(name)
        if name == "snakemake" and version is None:
            version = package_versions.get("snakemake-minimal")
        commands.append(
            RuntimeCommand(
                name=name,
                path=str(executable) if executable is not None else None,
                state="ready" if executable is not None else "missing",
                version=version,
                message=(
                    "found by presence check inside managed environment; executable was not run"
                    if executable is not None
                    else "executable is not present in this managed environment"
                ),
            )
        )
    active_name = os.environ.get("CONDA_DEFAULT_ENV", "").strip() if active else ""
    return (
        ManagedEnvironment(
            name=active_name or path.name or "base",
            path=str(path),
            active=active,
            discovered_by=sorted(discovered_by),
            managers=[
                EnvironmentManager(name=name, path=manager_path)
                for name, manager_path in sorted((manager_paths or {}).items())
                if name in _MANAGED_ENVIRONMENT_MANAGERS
            ],
            manifest_path=str(pixi_spec.manifest_path) if pixi_spec is not None else None,
            lockfile_path=(
                str(pixi_spec.lockfile_path)
                if pixi_spec is not None and pixi_spec.lockfile_path is not None
                else None
            ),
            declared_channels=pixi_spec.channels if pixi_spec is not None else [],
            exposed_commands=[
                RuntimeCommand(
                    name=name,
                    path=str(executable),
                    state="ready",
                    version=package_versions.get(name)
                    or (package_versions.get("snakemake-minimal") if name == "snakemake" else None),
                    message="exposed by the Pixi global environment",
                )
                for name, executable in sorted(
                    pixi_spec.exposed_commands.items() if pixi_spec is not None else []
                )
                if name in _WORKFLOW_CONTROLLER_COMMANDS
            ],
            packages=packages,
            commands=commands,
            platform=conda_platform,
            platform_subdirs=metadata.platform_subdirs,
            platform_matches_host=(
                conda_platform.os == host.os and conda_platform.arch == host.arch
                if conda_platform is not None
                else None
            ),
        ),
        warnings,
    )


def _discover_managed_environment_runtime(
    commands: list[RuntimeCommand],
    host: RuntimePlatform,
    workspace: Path | None = None,
) -> ManagedEnvironmentRuntime:
    discovered: dict[Path, set[str]] = {}
    warnings: list[str] = []
    manager_paths: dict[EnvironmentManagerName, str] = {
        cast(EnvironmentManagerName, command.name): command.path
        for command in commands
        if command.name in _MANAGED_ENVIRONMENT_MANAGERS
        and command.path is not None
        and command.state == "ready"
    }
    pixi_specs: dict[Path, _PixiEnvironmentSpec] = {}
    active_prefix_value = os.environ.get("CONDA_PREFIX", "").strip()
    active_prefix = (
        Path(active_prefix_value).expanduser().resolve(strict=False)
        if active_prefix_value
        else None
    )
    if active_prefix is not None:
        discovered.setdefault(active_prefix, set()).add("CONDA_PREFIX")

    for command in commands:
        if (
            command.name not in _CONDA_ENV_LIST_MANAGERS
            or command.path is None
            or command.state != "ready"
        ):
            continue
        try:
            result = subprocess.run(
                [command.path, "env", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=PROBE_TIMEOUT_SECONDS,
                check=False,
                env=_conda_probe_environment(),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            warnings.append(f"{command.name} environment discovery failed: {exc}")
            continue
        if result.returncode != 0:
            warnings.append(
                f"{command.name} environment discovery failed: "
                f"{_first_output_line(result) or f'exited with status {result.returncode}'}"
            )
            continue
        try:
            payload = json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError) as exc:
            warnings.append(f"{command.name} environment metadata was invalid: {exc}")
            continue
        environment_paths = payload.get("envs") if isinstance(payload, dict) else None
        if not isinstance(environment_paths, list):
            warnings.append(f"{command.name} environment metadata did not contain an envs list")
            continue
        for value in environment_paths:
            if not isinstance(value, str) or not value.strip():
                continue
            path = Path(value).expanduser().resolve(strict=False)
            discovered.setdefault(path, set()).add(command.name)

    if "pixi" in manager_paths:
        global_specs, global_warnings = _pixi_global_environments()
        project_specs, project_warnings = (
            _pixi_project_environment(workspace) if workspace is not None else ([], [])
        )
        warnings.extend(global_warnings)
        warnings.extend(project_warnings)
        for spec in (*global_specs, *project_specs):
            pixi_specs[spec.path] = spec
            discovered.setdefault(spec.path, set()).add("pixi")

    ordered_paths = sorted(discovered)
    truncated = len(ordered_paths) > MAX_MANAGED_ENVIRONMENTS
    selected_paths = ordered_paths[:MAX_MANAGED_ENVIRONMENTS]
    environments: list[ManagedEnvironment] = []
    for path in selected_paths:
        if not path.is_dir():
            warnings.append(f"discovered managed environment is not accessible: {path}")
            continue
        environment, environment_warnings = _managed_environment(
            path,
            active=active_prefix == path,
            discovered_by=discovered[path],
            manager_paths={
                name: manager_path
                for name, manager_path in manager_paths.items()
                if name in discovered[path]
            },
            pixi_spec=pixi_specs.get(path),
            host=host,
        )
        warnings.extend(environment_warnings)
        if (
            environment.active
            or any(
                package.name in _WORKFLOW_CONTROLLER_CONDA_PACKAGES
                for package in environment.packages
            )
            or any(command.state == "ready" for command in environment.commands)
        ):
            environments.append(environment)
    if truncated:
        warnings.append(
            f"Managed environment discovery was limited to {MAX_MANAGED_ENVIRONMENTS} paths"
        )
    return ManagedEnvironmentRuntime(
        environments_scanned=len(selected_paths),
        environments=environments,
        truncated=truncated,
        warnings=warnings,
    )


def _controller_candidate_id(
    controller: str,
    source: str,
    executable_path: str,
    environment_path: str | None,
    launch_argv_prefix: list[str],
) -> str:
    encoded = json.dumps(
        {
            "controller": controller,
            "source": source,
            "executable_path": executable_path,
            "environment_path": environment_path,
            "launch_argv_prefix": launch_argv_prefix,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"controller-{sha256_hex(encoded)[:32]}"


def _manager_for_environment(
    environment: ManagedEnvironment,
    controller: str,
) -> tuple[EnvironmentManager | None, RuntimeCommand | None]:
    exposed = next(
        (command for command in environment.exposed_commands if command.name == controller),
        None,
    )
    pixi = next((manager for manager in environment.managers if manager.name == "pixi"), None)
    if pixi is not None and exposed is not None:
        return pixi, exposed
    for name in ("conda", "mamba", "micromamba"):
        manager = next(
            (candidate for candidate in environment.managers if candidate.name == name),
            None,
        )
        if manager is not None:
            return manager, None
    if pixi is not None:
        return pixi, None
    return None, None


def _managed_launch_prefix(
    environment: ManagedEnvironment,
    controller: str,
    executable_path: str,
    manager: EnvironmentManager | None,
    exposed: RuntimeCommand | None,
) -> list[str]:
    if exposed is not None and exposed.path is not None:
        return [exposed.path]
    if manager is None:
        return [executable_path]
    if manager.name == "pixi" and environment.manifest_path is not None:
        return [
            manager.path,
            "run",
            "--as-is",
            "--manifest-path",
            environment.manifest_path,
            "--environment",
            environment.name,
            "--executable",
            controller,
        ]
    return [manager.path, "run", "--prefix", environment.path, controller]


def _controller_candidates(
    commands: list[RuntimeCommand],
    managed_environments: ManagedEnvironmentRuntime,
    host: RuntimePlatform,
    *,
    remote: bool = False,
) -> list[ControllerRuntimeCandidate]:
    candidates: list[ControllerRuntimeCandidate] = []
    managed_executables: set[Path] = set()
    for environment in managed_environments.environments:
        for command in environment.commands:
            if command.name not in _WORKFLOW_CONTROLLER_COMMANDS or command.path is None:
                continue
            executable_path = (
                command.path if remote else str(Path(command.path).resolve(strict=False))
            )
            managed_executables.add(Path(executable_path))
            manager, exposed = _manager_for_environment(environment, command.name)
            launch_argv_prefix = _managed_launch_prefix(
                environment,
                command.name,
                executable_path,
                manager,
                exposed,
            )
            platform_compatible = environment.platform_matches_host is not False
            manager_bound = manager is not None
            recommended = platform_compatible and manager_bound
            if environment.platform_matches_host is False:
                reason = f"environment platform does not match {host.os}/{host.arch}; do not use it"
            elif environment.lockfile_path is not None:
                reason = "managed environment with an observed lockfile"
            elif manager_bound:
                reason = (
                    "managed environment is preferred over Host PATH; exact lockfile provenance "
                    "was not observed"
                )
            else:
                reason = (
                    "environment contents were observed, but no manager invocation could be bound"
                )
            declared_channels = environment.declared_channels or sorted(
                {package.channel for package in environment.packages if package.channel is not None}
            )
            candidates.append(
                ControllerRuntimeCandidate(
                    candidate_id=_controller_candidate_id(
                        command.name,
                        "managed_environment",
                        executable_path,
                        environment.path,
                        launch_argv_prefix,
                    ),
                    controller=command.name,
                    source="managed_environment",
                    manager=manager.name if manager is not None else None,
                    executable_path=executable_path,
                    environment_path=environment.path,
                    version=command.version,
                    platform=environment.platform,
                    platform_matches_host=environment.platform_matches_host,
                    active=environment.active,
                    manifest_path=environment.manifest_path,
                    lockfile_path=environment.lockfile_path,
                    declared_channels=declared_channels,
                    launch_argv_prefix=launch_argv_prefix,
                    recommended=recommended,
                    recommendation_reason=reason,
                )
            )

    for command in commands:
        if (
            command.name not in _WORKFLOW_CONTROLLER_COMMANDS
            or command.path is None
            or command.state != "ready"
        ):
            continue
        executable_path = command.path if remote else str(Path(command.path).resolve(strict=False))
        if Path(executable_path) in managed_executables:
            continue
        launch_argv_prefix = [executable_path]
        candidates.append(
            ControllerRuntimeCandidate(
                candidate_id=_controller_candidate_id(
                    command.name,
                    "host_path",
                    executable_path,
                    None,
                    launch_argv_prefix,
                ),
                controller=command.name,
                source="host_path",
                executable_path=executable_path,
                version=command.version,
                platform=host,
                platform_matches_host=True,
                active=True,
                launch_argv_prefix=launch_argv_prefix,
                recommended=False,
                recommendation_reason=(
                    "Host PATH is supported only as an explicit fallback because its package "
                    "source and dependency closure are not reproducibly bound"
                ),
            )
        )
    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.controller,
            not candidate.recommended,
            candidate.source,
            candidate.environment_path or "",
            candidate.executable_path,
        ),
    )


def _resolved_command_probes(
    command_probes: list[RuntimeCommandProbe] | None,
) -> tuple[RuntimeCommandProbe, ...]:
    probes = {
        (name, name, "version"): RuntimeCommandProbe(
            name=name,
            executable=name,
            mode="version",
        )
        for name in _VERSION_ARGS
    }
    for probe in command_probes or []:
        probes[(probe.name, probe.executable, probe.mode)] = probe
    return tuple(probes.values())


def _new_snapshot(
    now: datetime,
    probes: tuple[RuntimeCommandProbe, ...],
    target: ComputeTargetRef,
) -> RuntimeEnvironmentSnapshot:
    commands = [_probe_command(probe) for probe in probes]
    docker_command = next(command for command in commands if command.name == "docker")
    docker = _probe_docker(docker_command)
    host = RuntimePlatform(
        os=platform.system().lower() or "unknown",
        arch=_normalized_arch(platform.machine()),
    )
    managed_environments = _discover_managed_environment_runtime(commands, host)
    controller_candidates = _controller_candidates(commands, managed_environments, host)
    warnings = [
        "container image architecture is not verified until the workflow resolves concrete images"
    ]
    if docker.daemon_reachable and docker.message:
        warnings.append(docker.message)
    if docker.daemon_reachable and docker.server_arch is None:
        warnings.append("Docker server architecture was not reported")
    if docker.server_arch and docker.server_arch != host.arch:
        warnings.append(
            f"Docker server architecture {docker.server_arch} differs from "
            f"host architecture {host.arch}"
        )
    return RuntimeEnvironmentSnapshot(
        snapshot_id=f"runtime-{uuid.uuid4().hex}",
        target=target,
        observed_at=now,
        expires_at=now + SNAPSHOT_TTL,
        host=host,
        commands=commands,
        docker=docker,
        managed_environments=managed_environments,
        controller_candidates=controller_candidates,
        warnings=warnings,
    )


def _remote_snapshot(
    now: datetime,
    probes: tuple[RuntimeCommandProbe, ...],
    target: ComputeTarget,
) -> RuntimeEnvironmentSnapshot:
    observed = daemon_client.request(
        "/targets/inspect",
        {
            "target_id": target.target_id,
            "executable_paths": [probe.executable for probe in probes],
        },
        timeout=25,
    )
    if observed.get("config_hash") != target.config_hash:
        raise ValueError("compute target configuration changed during SSH inspection")
    indexed = {item["executable"]: item for item in observed["commands"]}
    commands = []
    for probe in probes:
        value = indexed.get(probe.executable)
        if value is None:
            commands.append(
                RuntimeCommand(
                    name=probe.name,
                    path=None,
                    state="unverified",
                    message="SSH host did not report this executable",
                )
            )
        else:
            scheduler_unavailable = (
                probe.executable == "squeue"
                and (observed.get("scheduler") or {}).get("control_plane") == "unavailable"
            )
            commands.append(
                RuntimeCommand(
                    name=probe.name,
                    path=value.get("path"),
                    state="broken" if scheduler_unavailable else value["state"],
                    version=value.get("version"),
                    message=(
                        "Slurm control plane is unavailable"
                        if scheduler_unavailable
                        else value.get("message")
                    ),
                )
            )
    host = RuntimePlatform(
        os=observed["host"]["os"],
        arch=_normalized_arch(observed["host"]["arch"]),
    )
    docker = DockerRuntime.model_validate(observed["docker"])
    if docker.server_arch is not None:
        docker.server_arch = _normalized_arch(docker.server_arch)
    managed = ManagedEnvironmentRuntime.model_validate(observed.get("managed_environments", {}))
    warnings = [
        "container image architecture is not verified until the workflow resolves concrete images",
        *managed.warnings,
    ]
    if observed.get("scheduler") is not None:
        warnings.append("Slurm worker runtime and shared filesystem have not been inspected")
    return RuntimeEnvironmentSnapshot(
        snapshot_id=f"runtime-{uuid.uuid4().hex}",
        target=target.ref(),
        observed_at=now,
        expires_at=now + SNAPSHOT_TTL,
        host=host,
        commands=commands,
        docker=docker,
        managed_environments=managed,
        controller_candidates=_controller_candidates(commands, managed, host, remote=True),
        warnings=warnings,
    )


def _stable_facts(snapshot: RuntimeEnvironmentSnapshot) -> dict[str, Any]:
    return snapshot.model_dump(
        mode="json",
        exclude={"snapshot_id", "observed_at", "expires_at"},
    )


def _prune_expired_snapshots(now: datetime, *, keep: str | None = None) -> None:
    for snapshot_id, snapshot in list(_SNAPSHOTS.items()):
        if snapshot_id != keep and snapshot.expires_at <= now:
            del _SNAPSHOTS[snapshot_id]
            _SNAPSHOT_PROBES.pop(snapshot_id, None)


def resolve_runtime_environment(
    runtime_snapshot_id: str | None = None,
    *,
    target_id: str = "local",
    command_probes: list[RuntimeCommandProbe] | None = None,
    refresh: bool = False,
    now: datetime | None = None,
) -> RuntimeEnvironmentSnapshot:
    """Return a fresh snapshot or safely reuse one issued by this server."""
    target = resolve_compute_target(target_id)
    target_ref = target.ref()
    observed_at = now or datetime.now(UTC)
    probes = _resolved_command_probes(command_probes)
    probe_key = (probes, target.config_hash)
    previous = None
    if runtime_snapshot_id is not None:
        previous = _SNAPSHOTS.get(runtime_snapshot_id)
        if previous is None:
            raise ValueError(
                "runtime snapshot is unknown to this server; call get_runtime_environment again"
            )
        if previous.target != target_ref:
            raise ValueError("runtime snapshot belongs to a different compute target")
        _prune_expired_snapshots(observed_at, keep=runtime_snapshot_id)
        if (
            not refresh
            and previous.expires_at > observed_at
            and _SNAPSHOT_PROBES.get(runtime_snapshot_id) == probe_key
        ):
            return previous
    else:
        _prune_expired_snapshots(observed_at)

    current = (
        _remote_snapshot(observed_at, probes, target)
        if target.controller_transport == "ssh"
        else _new_snapshot(observed_at, probes, target_ref)
    )
    if (
        previous is not None
        and _SNAPSHOT_PROBES.get(previous.snapshot_id) == probe_key
        and _stable_facts(previous) == _stable_facts(current)
    ):
        current.snapshot_id = previous.snapshot_id
    _SNAPSHOTS[current.snapshot_id] = current
    _SNAPSHOT_PROBES[current.snapshot_id] = probe_key
    _prune_expired_snapshots(observed_at, keep=current.snapshot_id)
    return current


def inspect_runtime_environment(
    target_id: str = "local",
) -> RuntimeEnvironmentSnapshot:
    """Issue a new snapshot for the read-only MCP inspection tool."""
    return resolve_runtime_environment(target_id=target_id)
