"""Nextflow ``trace.txt`` execution evidence adapter."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
from typing import Any

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


class NextflowTraceObserver:
    """Normalize task attempts that Nextflow has flushed to ``trace.txt``."""

    binding = "nextflow"
    engine = "nextflow"
    evidence_kind = "nextflow_trace"
    file_patterns = ("logs/nextflow.trace.txt", "workflow/trace.txt")

    def observe(self, run_dir: Path, _workflow_status: str) -> ExecutionObservation:
        trace_path = run_dir / self.file_patterns[0]
        if not trace_path.is_file():
            trace_path = run_dir / self.file_patterns[1]
        if not trace_path.is_file():
            return empty_observation(
                engine=self.engine,
                evidence_kind=self.evidence_kind,
                evidence_path=str(trace_path),
                reason="trace.txt has not been produced yet",
            )

        try:
            with trace_path.open(encoding="utf-8-sig", newline="") as lines:
                return self.observe_lines(
                    lines,
                    evidence_path=str(trace_path),
                    workflow_status=_workflow_status,
                )
        except (OSError, UnicodeError, csv.Error) as exc:
            return empty_observation(
                engine=self.engine,
                evidence_kind=self.evidence_kind,
                evidence_path=str(trace_path),
                reason=f"trace.txt could not be read: {exc}",
            )

    def observe_lines(
        self,
        lines: Iterable[str],
        *,
        evidence_path: str,
        workflow_status: str,
    ) -> ExecutionObservation:
        """Normalize one Nextflow trace supplied by a local or remote transport."""
        del workflow_status
        try:
            attempts, ignored_records = self._read_attempts(lines)
        except csv.Error as exc:
            return empty_observation(
                engine=self.engine,
                evidence_kind=self.evidence_kind,
                evidence_path=evidence_path,
                reason=f"trace.txt could not be parsed: {exc}",
            )
        counts = count_attempts(attempts)
        finished_attempts = sum(getattr(counts, state) for state in _TERMINAL_STATES)
        reason = "the trace contains observed attempts, not a planned task denominator"
        if not attempts:
            reason = "trace.txt exists but does not contain complete task records yet"
        returned_attempts, attempts_truncated = limit_attempts(attempts)
        return ExecutionObservation(
            engine=self.engine,
            evidence=ExecutionEvidence(
                kind=self.evidence_kind,
                path=evidence_path,
                available=True,
                append_only=True,
                coverage="flushed task attempts",
                reason=reason if not attempts else None,
                record_count=len(attempts),
                ignored_record_count=ignored_records,
            ),
            counts=counts,
            progress=ExecutionProgress(
                completed=counts.completed + counts.cached,
                finished_attempts=finished_attempts,
                total=None,
                determinate=False,
                reason=reason,
            ),
            structure=discover_processes(
                attempts,
                ordering="first_terminal_observation",
            ),
            attempts_truncated=attempts_truncated,
            attempts=returned_attempts,
        )

    def _read_attempts(self, lines: Iterable[str]) -> tuple[list[TaskAttempt], int]:
        attempts: list[TaskAttempt] = []
        ignored_records = 0
        seen_attempt_ids: set[str] = set()
        reader = csv.DictReader(lines, delimiter="\t")
        if not reader.fieldnames or not {"name", "status"}.issubset(reader.fieldnames):
            return attempts, 1
        for sequence, row in enumerate(reader, start=1):
            if (
                not self._has_record(row)
                or not _optional_text(row.get("name"))
                or not _optional_text(row.get("status"))
            ):
                ignored_records += 1
                continue
            attempt = self._parse_attempt(row, sequence)
            if attempt.attempt_id in seen_attempt_ids:
                attempt.attempt_id = f"{attempt.attempt_id}:{sequence}"
            seen_attempt_ids.add(attempt.attempt_id)
            attempts.append(attempt)
        return attempts, ignored_records

    @staticmethod
    def _has_record(row: dict[str | None, Any]) -> bool:
        return any(value not in {None, ""} for key, value in row.items() if key is not None)

    @staticmethod
    def _parse_attempt(row: dict[str | None, Any], sequence: int) -> TaskAttempt:
        raw_name = _optional_text(row.get("name")) or "unknown"
        process_name, tag = _split_task_name(raw_name)
        attempt_number = _optional_int(row.get("attempt"))
        task_id = _optional_text(row.get("task_id"))
        task_hash = _optional_text(row.get("hash"))
        base_attempt_id = task_id or task_hash or str(sequence)
        attempt_id = (
            f"{base_attempt_id}:{attempt_number}"
            if attempt_number is not None and attempt_number > 1
            else base_attempt_id
        )
        return TaskAttempt(
            attempt_id=attempt_id,
            attempt_number=attempt_number,
            task_id=task_id,
            task_hash=task_hash,
            native_id=_optional_text(row.get("native_id")),
            process=process_name,
            process_label=process_name.rsplit(":", 1)[-1],
            sample_or_shard=tag or _optional_text(row.get("tag")),
            state=_normalize_state(row.get("status")),
            exit_code=_optional_int(row.get("exit")),
            submitted_at=_optional_text(row.get("submit")),
            started_at=_optional_text(row.get("start")),
            completed_at=_optional_text(row.get("complete")),
            duration=_optional_text(row.get("duration")),
            realtime=_optional_text(row.get("realtime")),
            cpu=_optional_text(row.get("%cpu")),
            peak_rss=_optional_text(row.get("peak_rss")),
            peak_vmem=_optional_text(row.get("peak_vmem")),
            workdir=_optional_text(row.get("workdir")),
            container=_optional_text(row.get("container")),
        )


def _split_task_name(value: str) -> tuple[str, str | None]:
    if value.endswith(")") and " (" in value:
        process, _, tag = value.partition(" (")
        return process, tag[:-1] or None
    return value, None


def _normalize_state(value: Any) -> TaskState:
    state = str(value or "unknown").strip().lower()
    if state in {"queued", "submitted"}:
        return "queued"
    if state == "running":
        return "running"
    if state == "completed":
        return "completed"
    if state == "cached":
        return "cached"
    if state == "failed":
        return "failed"
    if state == "aborted":
        return "aborted"
    return "unknown"


def _optional_text(value: Any) -> str | None:
    return str(value) if value is not None and value != "" else None


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None and value != "" else None
    except (TypeError, ValueError):
        return None
