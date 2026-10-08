"""Typed observations produced by local runtime inspection."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..compute_targets import ComputeTargetRef

EnvironmentManagerName = Literal["pixi", "conda", "mamba", "micromamba"]


class RuntimeCommandProbe(BaseModel):
    """One generic executable observation requested from a runtime target."""

    model_config = ConfigDict(frozen=True)

    name: str
    executable: str
    mode: Literal["presence", "version"] = "presence"


class RuntimeCommand(BaseModel):
    """One workflow runtime executable observed on the compute target."""

    name: str
    path: str | None
    state: Literal["ready", "missing", "broken", "unverified"] = "unverified"
    version: str | None = None
    message: str | None = None


class RuntimePlatform(BaseModel):
    """Operating-system and CPU architecture facts for one compute target."""

    os: str
    arch: str


class EnvironmentManager(BaseModel):
    """One manager that can address an isolated package environment."""

    name: EnvironmentManagerName
    path: str


class CondaPackage(BaseModel):
    """Relevant Conda-package metadata read from one managed environment."""

    name: str
    version: str | None = None
    build: str | None = None
    channel: str | None = None
    subdir: str | None = None


class ManagedEnvironment(BaseModel):
    """Workflow-controller installations discovered in one managed environment."""

    name: str
    path: str
    active: bool
    discovered_by: list[str] = Field(default_factory=list)
    managers: list[EnvironmentManager] = Field(default_factory=list)
    manifest_path: str | None = None
    lockfile_path: str | None = None
    declared_channels: list[str] = Field(default_factory=list)
    exposed_commands: list[RuntimeCommand] = Field(default_factory=list)
    packages: list[CondaPackage] = Field(default_factory=list)
    commands: list[RuntimeCommand] = Field(default_factory=list)
    platform: RuntimePlatform | None = None
    platform_subdirs: list[str] = Field(default_factory=list)
    platform_matches_host: bool | None = None


class ManagedEnvironmentRuntime(BaseModel):
    """Bounded, read-only inventory of managed environments with NGS controllers."""

    environments_scanned: int = 0
    environments: list[ManagedEnvironment] = Field(default_factory=list)
    truncated: bool = False
    warnings: list[str] = Field(default_factory=list)


class ControllerRuntimeCandidate(BaseModel):
    """One server-observed workflow-controller runtime available on a target."""

    candidate_id: str = Field(pattern=r"^controller-[0-9a-f]{32}$")
    controller: Literal["nextflow", "snakemake"]
    source: Literal["managed_environment", "host_path"]
    manager: EnvironmentManagerName | None = None
    executable_path: str
    environment_path: str | None = None
    version: str | None = None
    platform: RuntimePlatform | None = None
    platform_matches_host: bool | None = None
    active: bool = False
    manifest_path: str | None = None
    lockfile_path: str | None = None
    declared_channels: list[str] = Field(default_factory=list)
    launch_argv_prefix: list[str] = Field(min_length=1)
    recommended: bool
    recommendation_reason: str


class DockerRuntime(BaseModel):
    """Docker CLI target and locally observed daemon facts."""

    path: str | None
    context: str | None = None
    endpoint: str | None = None
    endpoint_is_local: bool | None = None
    daemon_reachable: bool
    server_version: str | None = None
    server_os: str | None = None
    server_arch: str | None = None
    message: str | None = None


class RuntimeEnvironmentSnapshot(BaseModel):
    """Server-issued, short-lived facts about one registered compute target."""

    ok: Literal[True] = True
    snapshot_id: str = Field(pattern=r"^runtime-[0-9a-f]{32}$")
    target: ComputeTargetRef
    observed_at: datetime
    expires_at: datetime
    host: RuntimePlatform
    commands: list[RuntimeCommand]
    docker: DockerRuntime
    managed_environments: ManagedEnvironmentRuntime = Field(
        default_factory=ManagedEnvironmentRuntime
    )
    controller_candidates: list[ControllerRuntimeCandidate] = Field(default_factory=list)
    container_image_architecture: Literal["unverified"] = "unverified"
    warnings: list[str] = Field(default_factory=list)
