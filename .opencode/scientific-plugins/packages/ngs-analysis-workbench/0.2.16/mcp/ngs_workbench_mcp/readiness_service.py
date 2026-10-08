"""Compose binding requirements, runtime observation, and readiness evaluation."""

from __future__ import annotations

from . import readiness, runtime
from .compute_targets import resolve_compute_target
from .readiness.models import ReadinessAssessment, RequirementSet, RuntimeRequirement
from .runtime.models import RuntimeCommandProbe


def _command_probes(requirement_set: RequirementSet) -> list[RuntimeCommandProbe]:
    return [
        RuntimeCommandProbe(
            name=name,
            executable=executable,
            mode=requirement.probe_mode,
        )
        for requirement in requirement_set.requirements
        for name, executable in requirement.command_candidates()
    ]


def assess(
    requirement_set: RequirementSet,
    runtime_snapshot_id: str | None = None,
    *,
    target_id: str = "local",
    controller_candidate_id: str | None = None,
    refresh: bool = False,
) -> ReadinessAssessment:
    """Observe the target for a resolved requirement set, then evaluate it."""
    if resolve_compute_target(target_id).executor == "slurm":
        requirement_set = requirement_set.model_copy(deep=True)
        requirement_set.requirements.extend(
            RuntimeRequirement(
                id=f"slurm-{name}",
                layer="compute_executor",
                capability="command",
                value=executable,
                source="target.executor",
                probe_mode="version",
            )
            for name, executable in (("submit", "sbatch"), ("queue", "squeue"))
        )
    snapshot = runtime.resolve_runtime_environment(
        runtime_snapshot_id,
        target_id=target_id,
        command_probes=_command_probes(requirement_set),
        refresh=refresh,
    )
    return readiness.evaluate(
        requirement_set,
        snapshot,
        controller_candidate_id=controller_candidate_id,
    )
