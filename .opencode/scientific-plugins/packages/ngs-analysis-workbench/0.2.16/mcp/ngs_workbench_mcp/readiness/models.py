"""Typed results produced by execution-readiness evaluation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ..compute_targets import ComputeTargetRef
from ..runtime.models import (
    ControllerRuntimeCandidate,
    DockerRuntime,
    RuntimeCommand,
    RuntimePlatform,
)

WorkflowEngine = Literal["nextflow", "snakemake"]


class RuntimeRequirement(BaseModel):
    """One runtime-layer capability required by an exact execution binding."""

    id: str
    layer: Literal[
        "workflow_controller",
        "compute_executor",
        "task_environment",
        "task_software",
    ]
    capability: Literal["command", "command_group", "daemon"]
    value: str
    source: str
    detail: str | None = None
    probe_mode: Literal["presence", "version"] = "presence"

    def command_candidates(self) -> list[tuple[str, str]]:
        """Return stable observation names and executables for command capabilities."""
        if self.capability == "command":
            return [(self.id, self.value)]
        if self.capability == "command_group":
            values = [value.strip() for value in self.value.split("|") if value.strip()]
            return [(f"{self.id}:{value}", value) for value in values]
        return []


class ReadinessEvidence(BaseModel):
    """Provenance for one requirement or observation used by readiness."""

    kind: str
    source: str
    detail: str


class RequirementSet(BaseModel):
    """Binding-owned requirements for one exact proposed execution."""

    binding: WorkflowEngine
    pipeline: str
    requirements: list[RuntimeRequirement]
    evidence: list[ReadinessEvidence] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ReadinessAssessment(BaseModel):
    """Binding-specific readiness derived from a runtime snapshot."""

    ok: bool
    status: Literal["ready", "blocked", "unknown"]
    binding: WorkflowEngine | None = None
    pipeline: str | None = None
    target: ComputeTargetRef | None = None
    readiness_id: str | None = Field(
        default=None,
        pattern=r"^readiness-[0-9a-f]{32}$",
    )
    scope: str
    snapshot_id: str | None = Field(default=None, pattern=r"^runtime-[0-9a-f]{32}$")
    observed_at: datetime | None = None
    expires_at: datetime | None = None
    host: RuntimePlatform | None = None
    commands: list[RuntimeCommand]
    controller_candidates: list[ControllerRuntimeCandidate] = Field(default_factory=list)
    selected_controller: ControllerRuntimeCandidate | None = None
    docker: DockerRuntime | None = None
    requirements: list[RuntimeRequirement] = Field(default_factory=list)
    evidence: list[ReadinessEvidence] = Field(default_factory=list)
    blockers: list[str]
    unknowns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_status(self) -> ReadinessAssessment:
        if self.ok != (self.status == "ready"):
            raise ValueError("ok must be true exactly when readiness status is ready")
        if self.status == "ready" and (self.blockers or self.unknowns):
            raise ValueError("ready status cannot contain blockers or unknowns")
        if self.status == "blocked" and not self.blockers:
            raise ValueError("blocked status requires at least one blocker")
        if self.status == "unknown" and (self.blockers or not self.unknowns):
            raise ValueError("unknown status requires unknowns and no concrete blockers")
        return self
