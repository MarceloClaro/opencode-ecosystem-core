"""Shared typed, engine-neutral execution observation models."""

from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import BaseModel, Field

MAX_RETURNED_ATTEMPTS = 200

TaskState = Literal[
    "queued",
    "running",
    "completed",
    "cached",
    "failed",
    "aborted",
    "unknown",
]


class AttemptCounts(BaseModel):
    """Counts of immutable task attempts by normalized state."""

    total: int = Field(ge=0)
    queued: int = Field(default=0, ge=0)
    running: int = Field(default=0, ge=0)
    completed: int = Field(default=0, ge=0)
    cached: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    aborted: int = Field(default=0, ge=0)
    unknown: int = Field(default=0, ge=0)


class ExecutionEvidence(BaseModel):
    """Description of the engine-owned evidence consumed by an adapter."""

    kind: str
    path: str | None
    available: bool
    append_only: bool
    coverage: str
    reason: str | None = None
    record_count: int | None = Field(default=None, ge=0)
    ignored_record_count: int = Field(default=0, ge=0)


class ExecutionProgress(BaseModel):
    """Observed progress without claiming an unavailable denominator."""

    completed: int = Field(ge=0)
    finished_attempts: int | None = Field(default=None, ge=0)
    total: int | None = Field(default=None, ge=0)
    determinate: bool
    reason: str | None = None


class TaskAttempt(BaseModel):
    """One engine attempt normalized for the run API."""

    attempt_id: str
    attempt_number: int | None = Field(default=None, ge=1)
    task_id: str | None = None
    task_hash: str | None = None
    native_id: str | None = None
    process: str
    process_label: str
    sample_or_shard: str | None = None
    state: TaskState
    exit_code: int | None = None
    submitted_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    duration: str | None = None
    realtime: str | None = None
    cpu: str | None = None
    peak_rss: str | None = None
    peak_vmem: str | None = None
    workdir: str | None = None
    container: str | None = None


class ProcessObservation(BaseModel):
    """Runtime-discovered process grouping, not a semantic workflow stage."""

    name: str
    label: str
    counts: AttemptCounts


class ExecutionStructure(BaseModel):
    """Observed process ordering exposed separately from semantic stages."""

    kind: Literal["discovered_processes"] = "discovered_processes"
    semantic_stages: Literal[False] = False
    ordering: str
    processes: list[ProcessObservation]


class ExecutionObservation(BaseModel):
    """Stable read model returned by any execution evidence adapter."""

    schema_version: Literal[1] = 1
    engine: str
    evidence: ExecutionEvidence
    counts: AttemptCounts
    count_unit: Literal["task_attempts"] = "task_attempts"
    progress: ExecutionProgress
    structure: ExecutionStructure
    attempts_truncated: bool = False
    attempts: list[TaskAttempt]


def count_attempts(attempts: list[TaskAttempt]) -> AttemptCounts:
    counts: Counter[str] = Counter(attempt.state for attempt in attempts)
    return AttemptCounts(
        total=len(attempts),
        queued=counts["queued"],
        running=counts["running"],
        completed=counts["completed"],
        cached=counts["cached"],
        failed=counts["failed"],
        aborted=counts["aborted"],
        unknown=counts["unknown"],
    )


def discover_processes(
    attempts: list[TaskAttempt],
    *,
    ordering: str,
) -> ExecutionStructure:
    grouped: dict[str, list[TaskAttempt]] = {}
    for attempt in attempts:
        grouped.setdefault(attempt.process, []).append(attempt)
    return ExecutionStructure(
        ordering=ordering,
        processes=[
            ProcessObservation(
                name=name,
                label=process_attempts[0].process_label,
                counts=count_attempts(process_attempts),
            )
            for name, process_attempts in grouped.items()
        ],
    )


def limit_attempts(attempts: list[TaskAttempt]) -> tuple[list[TaskAttempt], bool]:
    """Return a bounded recent tail while aggregate views retain the full history."""
    return attempts[-MAX_RETURNED_ATTEMPTS:], len(attempts) > MAX_RETURNED_ATTEMPTS


def empty_observation(
    *,
    engine: str,
    evidence_kind: str,
    evidence_path: str | None,
    reason: str,
) -> ExecutionObservation:
    attempts: list[TaskAttempt] = []
    return ExecutionObservation(
        engine=engine,
        evidence=ExecutionEvidence(
            kind=evidence_kind,
            path=evidence_path,
            available=False,
            append_only=True,
            coverage="none",
            reason=reason,
        ),
        counts=count_attempts(attempts),
        progress=ExecutionProgress(
            completed=0,
            total=None,
            determinate=False,
            reason=reason,
        ),
        structure=discover_processes(attempts, ordering="unknown"),
        attempts=attempts,
    )
