"""Read task attempts from Snakemake's native execution log."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from .models import (
    ExecutionEvidence,
    ExecutionObservation,
    ExecutionProgress,
    TaskAttempt,
    TaskState,
    count_attempts,
    discover_processes,
    empty_observation,
    limit_attempts,
)

_TERMINAL_STATES = {"completed", "failed", "cached", "aborted"}
_TERMINAL_WORKFLOW_STATUSES = {"completed", "failed", "canceled", "orphaned"}
_TIMESTAMP = re.compile(r"^\[(?P<value>.+)]$")
_RULE_START = re.compile(r"^(?:localrule|rule) (?P<name>[^:]+):$")
_FINISHED = re.compile(r"^Finished jobid: (?P<job_id>\S+) \(Rule: (?P<name>[^)]+)\)$")
_ERROR = re.compile(r"^Error in rule (?P<name>[^:]+):$")
_JOB_ID = re.compile(r"^\s+jobid:\s*(?P<job_id>\S+)\s*$")
_WILDCARDS = re.compile(r"^\s+wildcards:\s*(?P<value>.+?)\s*$")
_PROGRESS = re.compile(r"^(?P<completed>\d+) of (?P<total>\d+) steps(?: \(\d+%\))? done$")
_JOB_STATS_TOTAL = re.compile(r"^total\s+(?P<total>\d+)\s*$")

PendingKind = Literal["start", "error"]


class SnakemakeLogObserver:
    """Normalize append-only records from the newest native Snakemake log."""

    binding = "snakemake"
    engine = "snakemake"
    evidence_kind = "snakemake_native_log"
    file_patterns = ("results/.snakemake/log/*.snakemake.log",)

    def observe(self, run_dir: Path, workflow_status: str) -> ExecutionObservation:
        try:
            log_path = _newest_log(run_dir)
        except OSError as exc:
            return empty_observation(
                engine=self.engine,
                evidence_kind=self.evidence_kind,
                evidence_path=str(run_dir / "results" / ".snakemake" / "log"),
                reason=f"Snakemake log directory could not be read: {exc}",
            )
        if log_path is None:
            return empty_observation(
                engine=self.engine,
                evidence_kind=self.evidence_kind,
                evidence_path=str(run_dir / "results" / ".snakemake" / "log"),
                reason="Snakemake has not produced a native execution log yet",
            )

        try:
            with log_path.open(encoding="utf-8-sig", newline="") as lines:
                return self.observe_lines(
                    lines,
                    evidence_path=str(log_path),
                    workflow_status=workflow_status,
                )
        except (OSError, UnicodeError) as exc:
            return empty_observation(
                engine=self.engine,
                evidence_kind=self.evidence_kind,
                evidence_path=str(log_path),
                reason=f"Snakemake log could not be read: {exc}",
            )

    def observe_lines(
        self,
        lines: Iterable[str],
        *,
        evidence_path: str,
        workflow_status: str,
    ) -> ExecutionObservation:
        """Normalize one Snakemake log supplied by a local or remote transport."""
        parsed = _parse_lines(lines)
        if workflow_status in _TERMINAL_WORKFLOW_STATUSES:
            parsed.abort_unfinished()

        counts = count_attempts(parsed.attempts)
        finished_attempts = sum(getattr(counts, state) for state in _TERMINAL_STATES)
        total = parsed.progress_total or parsed.planned_total
        reason = None
        if total is None:
            reason = "the native log has not reported a planned step count yet"
        if not parsed.attempts:
            reason = "the native log does not contain complete task records yet"
        returned_attempts, attempts_truncated = limit_attempts(parsed.attempts)
        return ExecutionObservation(
            engine=self.engine,
            evidence=ExecutionEvidence(
                kind=self.evidence_kind,
                path=evidence_path,
                available=True,
                append_only=True,
                coverage="native Snakemake execution log",
                reason=reason if not parsed.attempts else None,
                record_count=parsed.line_count,
                ignored_record_count=parsed.ignored_record_count,
            ),
            counts=counts,
            progress=ExecutionProgress(
                completed=(
                    parsed.progress_completed
                    if parsed.progress_completed is not None
                    else counts.completed + counts.cached
                ),
                finished_attempts=finished_attempts,
                total=total,
                determinate=total is not None,
                reason=reason,
            ),
            structure=discover_processes(
                parsed.attempts,
                ordering="first_runtime_observation",
            ),
            attempts_truncated=attempts_truncated,
            attempts=returned_attempts,
        )


class _ParsedLog:
    def __init__(self) -> None:
        self.attempts: list[TaskAttempt] = []
        self.attempts_by_job: dict[str, list[TaskAttempt]] = {}
        self.line_count = 0
        self.ignored_record_count = 0
        self.planned_total: int | None = None
        self.progress_completed: int | None = None
        self.progress_total: int | None = None
        self.last_observed_at: str | None = None

    def start(self, job_id: str, process: str, timestamp: str | None) -> TaskAttempt:
        job_attempts = self.attempts_by_job.setdefault(job_id, [])
        if job_attempts and job_attempts[-1].state in {"queued", "running"}:
            return job_attempts[-1]
        attempt_number = len(job_attempts) + 1
        attempt = TaskAttempt(
            attempt_id=f"{job_id}:{attempt_number}",
            attempt_number=attempt_number,
            task_id=job_id,
            process=process,
            process_label=process.rsplit(":", 1)[-1],
            state="running",
            started_at=timestamp,
        )
        job_attempts.append(attempt)
        self.attempts.append(attempt)
        return attempt

    def finish(
        self,
        job_id: str,
        process: str,
        timestamp: str | None,
        state: TaskState,
    ) -> None:
        job_attempts = self.attempts_by_job.get(job_id, [])
        attempt = next(
            (
                candidate
                for candidate in reversed(job_attempts)
                if candidate.state in {"queued", "running"}
            ),
            None,
        )
        if attempt is None:
            attempt = self.start(job_id, process, timestamp)
        attempt.state = state
        attempt.completed_at = timestamp

    def abort_unfinished(self) -> None:
        for attempt in self.attempts:
            if attempt.state in {"queued", "running"}:
                attempt.state = "aborted"
                attempt.completed_at = self.last_observed_at


def _newest_log(run_dir: Path) -> Path | None:
    for pattern in SnakemakeLogObserver.file_patterns:
        logs = [path for path in run_dir.glob(pattern) if path.is_file()]
        if logs:
            return max(logs, key=lambda path: (path.stat().st_mtime_ns, path.name))
    return None


def _parse_lines(lines: Iterable[str]) -> _ParsedLog:
    parsed = _ParsedLog()
    timestamp: str | None = None
    pending_kind: PendingKind | None = None
    pending_process: str | None = None
    pending_attempt: TaskAttempt | None = None
    in_job_stats = False

    for raw_line in lines:
        parsed.line_count += 1
        line = raw_line.rstrip("\r\n")

        if match := _TIMESTAMP.match(line):
            if pending_kind == "start" and pending_attempt is None:
                parsed.ignored_record_count += 1
            timestamp = match.group("value")
            parsed.last_observed_at = timestamp
            pending_kind = None
            pending_process = None
            pending_attempt = None
            continue

        if line == "Job stats:":
            in_job_stats = True
            continue
        if in_job_stats:
            if match := _JOB_STATS_TOTAL.match(line):
                parsed.planned_total = int(match.group("total"))
                in_job_stats = False
                continue
            if line.startswith(("Select jobs", "Execute ")):
                in_job_stats = False

        if match := _PROGRESS.match(line):
            parsed.progress_completed = int(match.group("completed"))
            parsed.progress_total = int(match.group("total"))
            continue

        if match := _FINISHED.match(line):
            parsed.finish(
                match.group("job_id"),
                match.group("name"),
                timestamp,
                "completed",
            )
            continue

        if match := _RULE_START.match(line):
            pending_kind = "start"
            pending_process = match.group("name")
            pending_attempt = None
            continue

        if match := _ERROR.match(line):
            pending_kind = "error"
            pending_process = match.group("name")
            pending_attempt = None
            continue

        if match := _JOB_ID.match(line):
            job_id = match.group("job_id")
            if pending_kind == "start" and pending_process is not None:
                pending_attempt = parsed.start(job_id, pending_process, timestamp)
            elif pending_kind == "error" and pending_process is not None:
                parsed.finish(job_id, pending_process, timestamp, "failed")
            continue

        if match := _WILDCARDS.match(line):
            if pending_attempt is not None:
                pending_attempt.sample_or_shard = match.group("value")

    if pending_kind == "start" and pending_attempt is None:
        parsed.ignored_record_count += 1
    return parsed
