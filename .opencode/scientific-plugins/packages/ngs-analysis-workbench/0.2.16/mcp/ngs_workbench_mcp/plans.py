"""Typed execution-plan models shared by the MCP bindings."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Literal

from ngs_workbench_daemon.hashing import sha256_bytes
from ngs_workbench_daemon.protocol import canonical_plan_checksum
from pydantic import BaseModel, Field, model_validator

from .compute_targets import ComputeTargetRef
from .readiness.models import ReadinessAssessment
from .workflows.source import WorkflowSource


def normalize_display_name(value: str | None, fallback: str) -> str:
    """Return a compact user-facing name suitable for a checksum-bound request."""
    normalized = " ".join((value or fallback).split())
    if not normalized:
        normalized = fallback
    return normalized[:120]


def controller_launch_argv(
    readiness: ReadinessAssessment,
    controller: Literal["nextflow", "snakemake"],
) -> list[str]:
    """Return the exact server-resolved prefix for a selected controller."""
    if readiness.selected_controller is not None:
        return list(readiness.selected_controller.launch_argv_prefix)
    path = next(
        (
            command.path
            for command in readiness.commands
            if command.name == controller and command.path is not None
        ),
        None,
    )
    return [path or controller]


class RunEffects(BaseModel):
    """Expected filesystem and network effects of an approved run."""

    run_dir: str
    output_dir: str
    work_dir: str
    launch_log: str
    local_writes: list[str]
    remote_writes: list[str] = Field(default_factory=list, exclude_if=lambda value: not value)
    downloads: list[str]
    network_access: list[str]


class RemoteStagedFile(BaseModel):
    """Exact approved bytes copied or generated at one remote destination."""

    destination: str
    sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    bytes: int = Field(ge=0)
    source: str | None = Field(default=None, exclude_if=lambda value: value is None)
    content: str | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def validate_origin(self) -> RemoteStagedFile:
        if (self.source is None) == (self.content is None):
            raise ValueError("approved remote staging requires exactly one source or content")
        destination = PurePosixPath(self.destination)
        if not destination.is_absolute() or ".." in destination.parts:
            raise ValueError("approved remote staging destination must be an absolute POSIX path")
        if self.content is not None:
            content = self.content.encode("utf-8")
            if self.bytes != len(content) or self.sha256 != sha256_bytes(content):
                raise ValueError("approved remote content does not match its digest or byte count")
        return self


class RemoteExecution(BaseModel):
    """Frozen, nonsecret SSH effects bound to one approved workflow plan."""

    config_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    host_access: dict[str, Any]
    workspace_root: str
    run_dir: str
    executor: Literal["local_process", "slurm"]
    executor_configuration: dict[str, str] = Field(default_factory=dict)
    staged_files: list[RemoteStagedFile]

    @model_validator(mode="after")
    def validate_remote_paths(self) -> RemoteExecution:
        root = PurePosixPath(self.run_dir)
        if not root.is_absolute() or ".." in root.parts:
            raise ValueError("approved run_dir must be an absolute POSIX path")
        destinations = [PurePosixPath(item.destination) for item in self.staged_files]
        if any(not destination.is_relative_to(root) for destination in destinations):
            raise ValueError("approved remote staging destination escapes its run")
        if len(set(destinations)) != len(destinations):
            raise ValueError("approved remote staging contains duplicate destinations")
        return self


class PreparationOperation(BaseModel):
    """One exact file effect performed before the workflow process starts."""

    operation: Literal["download_verified_file", "write_generated_file"]
    relative_path: str
    path: str
    bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    role: str | None = None
    url: str | None = None
    media_type: Literal["application/json", "text/csv", "text/plain"] | None = None
    content: str | None = None


class PreparationSpec(BaseModel):
    """Analysis-owned preparation embedded in one workflow plan."""

    destination_dir: str
    operations: list[PreparationOperation]
    transfer_executable: str | None = None
    download_bytes: int = Field(ge=0)
    writes: list[str]


class MonitoringPlan(BaseModel):
    """How a caller should observe a started run."""

    terminal_statuses: list[str]
    log_paths: list[str]
    artifact_paths: list[str]


class InputSummary(BaseModel):
    """Small, engine-neutral summary of the inputs bound by a plan."""

    source: Literal[
        "sample_sheet", "workflow_test_profile", "config_file", "params_file", "missing"
    ]
    path: str | None = None
    sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    record_count: int | None = Field(default=None, ge=0)
    sample_count: int | None = Field(default=None, ge=0)
    read_layout: Literal["single-end", "paired-end", "mixed"] | None = None


class NextflowPlanRequest(BaseModel):
    """Normalized generic or curated Nextflow inputs bound by a plan checksum."""

    pipeline: str
    workflow_version_id: str | None = Field(default=None, exclude_if=lambda value: value is None)
    parameter_contract: str | None = Field(default=None, exclude_if=lambda value: value is None)
    target: ComputeTargetRef
    remote: RemoteExecution | None = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )
    display_name: str = Field(min_length=1, max_length=120)
    # LEGACY_CLEANUP(2026-09-07): Pre-lineage v3 plans omit these fields; keep their approved
    # serialization unchanged until support for those saved plans is retired.
    first_run_id: str | None = Field(default=None, exclude_if=lambda value: value is None)
    attempt_number: int | None = Field(default=None, ge=1, exclude_if=lambda value: value is None)
    workflow: str
    run_dir: str
    profile: str
    sample_sheet: str | None
    sample_sheet_sha256: str | None = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    revision: str | None
    params_file: str | None
    params_file_sha256: str | None = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    runtime_snapshot_id: str | None = Field(
        default=None,
        pattern=r"^runtime-[0-9a-f]{32}$",
    )
    controller_candidate_id: str | None = Field(
        default=None,
        pattern=r"^controller-[0-9a-f]{32}$",
    )
    workflow_source: WorkflowSource | None = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )
    workflow_parameters: dict[str, str | int | float | bool] | None = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )
    run_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,95}$")


class NextflowRunPlan(BaseModel):
    """A read-only, checksum-bound plan for one Nextflow workflow run."""

    schema_version: Literal[3] = 3
    ok: bool = True
    runnable: bool
    request: NextflowPlanRequest
    command_argv: list[str]
    readiness: ReadinessAssessment
    input_summary: InputSummary
    effects: RunEffects
    preparation: PreparationSpec | None = None
    blockers: list[str]
    warnings: list[str]
    monitoring: MonitoringPlan


class SnakemakePlanRequest(BaseModel):
    """Generic Snakemake inputs bound by a plan checksum."""

    pipeline: str
    workflow_version_id: str | None = Field(default=None, exclude_if=lambda value: value is None)
    target: ComputeTargetRef
    remote: RemoteExecution | None = Field(default=None, exclude_if=lambda value: value is None)
    display_name: str = Field(min_length=1, max_length=120)
    # LEGACY_CLEANUP(2026-09-07): Pre-lineage v3 plans omit these fields; keep their approved
    # serialization unchanged until support for those saved plans is retired.
    first_run_id: str | None = Field(default=None, exclude_if=lambda value: value is None)
    attempt_number: int | None = Field(default=None, ge=1, exclude_if=lambda value: value is None)
    workflow: str
    run_dir: str
    config_file: str
    config_sha256: str | None = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    workflow_sha256: str | None = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    cores: int = Field(ge=1)
    runtime_snapshot_id: str | None = Field(
        default=None,
        pattern=r"^runtime-[0-9a-f]{32}$",
    )
    controller_candidate_id: str | None = Field(
        default=None,
        pattern=r"^controller-[0-9a-f]{32}$",
    )
    workflow_source: WorkflowSource
    run_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,95}$")


class SnakemakeRunPlan(BaseModel):
    """A read-only, checksum-bound plan for one Snakemake run."""

    schema_version: Literal[3] = 3
    ok: bool = True
    runnable: bool
    request: SnakemakePlanRequest
    command_argv: list[str]
    readiness: ReadinessAssessment
    input_summary: InputSummary
    effects: RunEffects
    preparation: PreparationSpec | None = None
    blockers: list[str]
    warnings: list[str]
    monitoring: MonitoringPlan


def plan_checksum(value: NextflowRunPlan | SnakemakeRunPlan) -> str:
    """Bind stable plan inputs and runtime facts while ignoring observation identity."""
    return canonical_plan_checksum(value.model_dump(mode="json"))
