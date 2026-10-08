"""The single repository for the daemon-owned host-local registry."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from ..protocol import execution_run_directory
from .orm import RunEventRow, RunRow, WorkspaceRow

TERMINAL_STATUSES = {"completed", "failed", "canceled", "orphaned"}
ALLOWED_TRANSITIONS = {
    "starting": {"running", "cancel_requested", "failed", "orphaned"},
    "running": {"cancel_requested", "completed", "failed", "orphaned"},
    "cancel_requested": {"canceling", "canceled", "completed", "failed", "orphaned"},
    "canceling": {"canceled", "completed", "failed", "orphaned"},
    "completed": set(),
    "failed": set(),
    "canceled": set(),
    "orphaned": set(),
}


class RunConflict(RuntimeError):
    """A workspace path or external run id is already registered."""


class StaleRunRevision(RuntimeError):
    """A guarded run update lost a revision race."""


class InvalidRunTransition(RuntimeError):
    """A run state transition is not part of the lifecycle."""


@dataclass(frozen=True)
class NewRun:
    workspace_id: str
    workspace_dir: Path
    external_run_id: str
    binding: str
    pipeline: str
    workflow: str
    plan_checksum: str
    request: dict[str, Any]
    command_argv: list[str]
    run_relative_path: str
    approved_plan_relative_path: str
    launch_log_relative_path: str
    first_run_id: str | None = None
    attempt_number: int = 1


@dataclass(frozen=True)
class RunFilters:
    workspace_id: str | None = None
    statuses: tuple[str, ...] = ()
    binding: str | None = None
    pipeline: str | None = None
    first_run_id: str | None = None


@dataclass(frozen=True)
class RunRecord:
    id: str
    workspace_id: str
    workspace_dir: str
    external_run_id: str
    first_run_id: str
    attempt_number: int
    binding: str
    pipeline: str
    workflow: str
    status: str
    revision: int
    plan_checksum: str
    request: dict[str, Any]
    command_argv: list[str]
    run_dir: str
    approved_plan_path: str
    launch_log_path: str
    pid: int | None
    started_at_ms: int | None
    completed_at_ms: int | None
    return_code: int | None
    failure_summary: str | None
    cancel_requested_at_ms: int | None
    created_at_ms: int
    updated_at_ms: int

    @property
    def execution_dir(self) -> str | None:
        return self.request.get("execution_run_dir") or execution_run_directory(
            self.request.get("plan_request", self.request), self.run_dir
        )

    def summary(self) -> dict[str, Any]:
        return {
            "registry_run_id": self.id,
            "run_id": self.external_run_id,
            "first_run_id": self.first_run_id,
            "attempt_number": self.attempt_number,
            "binding": self.binding,
            "pipeline": self.pipeline,
            "workflow": self.workflow,
            "status": self.status,
            "revision": self.revision,
            "run_dir": self.execution_dir,
            "pid": self.pid,
            "started_at_ms": self.started_at_ms,
            "completed_at_ms": self.completed_at_ms,
            "returncode": self.return_code,
            "created_at_ms": self.created_at_ms,
            "updated_at_ms": self.updated_at_ms,
        }

    def detail(self) -> dict[str, Any]:
        return {
            **self.summary(),
            "plan_checksum": self.plan_checksum,
            "request": self.request,
            "command_argv": self.command_argv,
            "approved_plan_path": self.approved_plan_path,
            "launch_log_path": self.launch_log_path,
            "failure_summary": self.failure_summary,
            "cancel_requested_at_ms": self.cancel_requested_at_ms,
        }


class RegistryRepository:
    """Persist registry operations within a caller-owned SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def register_workspace(self, workspace_id: str, workspace: Path) -> None:
        now_ms = _now_ms()
        canonical_path = str(workspace.resolve())
        existing = self._session.get(WorkspaceRow, workspace_id)
        path_owner = self._session.scalar(
            select(WorkspaceRow).where(WorkspaceRow.canonical_path == canonical_path)
        )
        if path_owner is not None and path_owner.id != workspace_id:
            raise RunConflict(f"workspace path is already registered: {canonical_path}")
        if existing is None:
            self._session.add(
                WorkspaceRow(
                    id=workspace_id,
                    canonical_path=canonical_path,
                    display_name=workspace.name or canonical_path,
                    state="available",
                    created_at_ms=now_ms,
                    last_seen_at_ms=now_ms,
                )
            )
            return
        existing.canonical_path = canonical_path
        existing.display_name = workspace.name or canonical_path
        existing.state = "available"
        existing.last_seen_at_ms = now_ms

    def allocate_approved_run(self, new_run: NewRun) -> RunRecord:
        existing = self.get_by_run_id(new_run.external_run_id)
        if existing is not None:
            raise RunConflict(f"run id is already registered: {new_run.external_run_id}")

        now_ms = _now_ms()
        row = RunRow(
            id=str(uuid.uuid4()),
            workspace_id=new_run.workspace_id,
            external_run_id=new_run.external_run_id,
            first_run_id=new_run.first_run_id or new_run.external_run_id,
            attempt_number=new_run.attempt_number,
            binding=new_run.binding,
            pipeline=new_run.pipeline,
            workflow=new_run.workflow,
            status="starting",
            revision=1,
            plan_checksum=new_run.plan_checksum,
            request_json=_json(new_run.request),
            command_json=_json({"schema_version": 1, "argv": new_run.command_argv}),
            run_relative_path=new_run.run_relative_path,
            approved_plan_relative_path=new_run.approved_plan_relative_path,
            launch_log_relative_path=new_run.launch_log_relative_path,
            created_at_ms=now_ms,
            updated_at_ms=now_ms,
        )
        self._session.add(row)
        self._session.flush()
        self._session.add(
            RunEventRow(
                run_id=row.id,
                sequence=1,
                event_type="run_allocated",
                from_status=None,
                to_status="starting",
                actor_type="mcp",
                details_json="{}",
                created_at_ms=now_ms,
            )
        )
        self._session.flush()
        return self._record(row, str(new_run.workspace_dir))

    def get_run(self, registry_run_id: str) -> RunRecord | None:
        result = self._session.execute(
            select(RunRow, WorkspaceRow.canonical_path)
            .join(WorkspaceRow, WorkspaceRow.id == RunRow.workspace_id)
            .where(RunRow.id == registry_run_id)
        ).one_or_none()
        return self._record(*result) if result is not None else None

    def get_by_run_directory(self, workspace_id: str, relative_path: str) -> RunRecord | None:
        result = self._session.execute(
            select(RunRow, WorkspaceRow.canonical_path)
            .join(WorkspaceRow, WorkspaceRow.id == RunRow.workspace_id)
            .where(RunRow.workspace_id == workspace_id, RunRow.run_relative_path == relative_path)
        ).first()
        return self._record(result[0], result[1]) if result is not None else None

    def get_by_run_id(
        self,
        external_run_id: str,
    ) -> RunRecord | None:
        result = self._session.execute(
            select(RunRow, WorkspaceRow.canonical_path)
            .join(WorkspaceRow, WorkspaceRow.id == RunRow.workspace_id)
            .where(
                RunRow.external_run_id == external_run_id,
            )
        ).one_or_none()
        return self._record(*result) if result is not None else None

    def get_first_run(
        self,
        first_run_id: str,
    ) -> RunRecord | None:
        result = self._session.execute(
            select(RunRow, WorkspaceRow.canonical_path)
            .join(WorkspaceRow, WorkspaceRow.id == RunRow.workspace_id)
            .where(
                RunRow.external_run_id == first_run_id,
                RunRow.first_run_id == first_run_id,
                RunRow.attempt_number == 1,
            )
        ).one_or_none()
        return self._record(*result) if result is not None else None

    def get_latest_attempt(
        self,
        first_run_id: str,
    ) -> RunRecord | None:
        result = self._session.execute(
            select(RunRow, WorkspaceRow.canonical_path)
            .join(WorkspaceRow, WorkspaceRow.id == RunRow.workspace_id)
            .where(
                RunRow.first_run_id == first_run_id,
            )
            .order_by(RunRow.attempt_number.desc())
            .limit(1)
        ).one_or_none()
        return self._record(*result) if result is not None else None

    def list_runs(self, filters: RunFilters, *, limit: int = 50) -> list[RunRecord]:
        statement = select(RunRow, WorkspaceRow.canonical_path).join(
            WorkspaceRow,
            WorkspaceRow.id == RunRow.workspace_id,
        )
        if filters.workspace_id:
            statement = statement.where(
                func.coalesce(
                    func.json_extract(RunRow.request_json, "$.workspace_id"), RunRow.workspace_id
                )
                == filters.workspace_id
            )
        if filters.statuses:
            statement = statement.where(RunRow.status.in_(filters.statuses))
        if filters.binding:
            statement = statement.where(RunRow.binding == filters.binding)
        if filters.pipeline:
            statement = statement.where(RunRow.pipeline == filters.pipeline)
        if filters.first_run_id:
            statement = statement.where(RunRow.first_run_id == filters.first_run_id)
        rows = self._session.execute(
            statement.order_by(RunRow.updated_at_ms.desc(), RunRow.id.desc()).limit(
                max(1, min(limit, 200))
            )
        )
        return [self._record(run, workspace_path) for run, workspace_path in rows]

    def has_active_runs(self, implementation: str) -> bool:
        statement = select(RunRow.id).where(
            RunRow.status.not_in(TERMINAL_STATUSES),
            func.json_extract(RunRow.request_json, "$.daemon_owner.implementation")
            == implementation,
        )
        return bool(self._session.scalar(select(statement.exists())))

    def list_recent_lineages(
        self,
        *,
        lineage_limit: int = 20,
        attempts_per_lineage: int = 6,
    ) -> list[RunRecord]:
        """Return recent workflow groups with their newest bounded attempts."""
        latest_update = func.max(RunRow.updated_at_ms).label("latest_update")
        roots = self._session.execute(
            select(
                RunRow.first_run_id,
                latest_update,
            )
            .group_by(RunRow.first_run_id)
            .order_by(latest_update.desc(), RunRow.first_run_id.desc())
            .limit(max(1, min(lineage_limit, 50)))
        )
        records: list[RunRecord] = []
        for first_run_id, _ in roots:
            attempts = list(
                self._session.execute(
                    select(RunRow, WorkspaceRow.canonical_path)
                    .join(WorkspaceRow, WorkspaceRow.id == RunRow.workspace_id)
                    .where(
                        RunRow.first_run_id == first_run_id,
                    )
                    .order_by(RunRow.attempt_number.desc())
                    .limit(max(1, min(attempts_per_lineage, 20)))
                )
            )
            records.extend(
                self._record(run, workspace_path) for run, workspace_path in reversed(attempts)
            )
        return records

    def list_daemon_owned_active_runs(self, filters: RunFilters | None = None) -> list[RunRecord]:
        """Select every owned local active run within an optional non-status scope."""
        statement = (
            select(RunRow, WorkspaceRow.canonical_path)
            .join(WorkspaceRow, WorkspaceRow.id == RunRow.workspace_id)
            .where(
                RunRow.status.in_(("starting", "running", "cancel_requested", "canceling")),
                or_(
                    (func.json_type(RunRow.request_json, "$.daemon_instance_id") == "text")
                    & (func.json_extract(RunRow.request_json, "$.daemon_instance_id") != ""),
                    (func.json_type(RunRow.request_json, "$.daemon_owner.instance_id") == "text")
                    & (func.json_extract(RunRow.request_json, "$.daemon_owner.instance_id") != ""),
                ),
                func.json_extract(RunRow.request_json, "$.target.target_id") == "local",
            )
        )
        if filters is not None:
            if filters.workspace_id:
                statement = statement.where(
                    func.coalesce(
                        func.json_extract(RunRow.request_json, "$.workspace_id"),
                        RunRow.workspace_id,
                    )
                    == filters.workspace_id
                )
            if filters.binding:
                statement = statement.where(RunRow.binding == filters.binding)
            if filters.pipeline:
                statement = statement.where(RunRow.pipeline == filters.pipeline)
            if filters.first_run_id:
                statement = statement.where(RunRow.first_run_id == filters.first_run_id)
        rows = self._session.execute(statement)
        return [self._record(run, workspace_path) for run, workspace_path in rows]

    def set_run_pid(self, registry_run_id: str, pid: int | None) -> None:
        """Update owned process identity without inventing a lifecycle transition."""
        updated_id = self._session.scalar(
            update(RunRow)
            .where(RunRow.id == registry_run_id, RunRow.status.not_in(TERMINAL_STATUSES))
            .values(pid=pid)
            .returning(RunRow.id)
        )
        if updated_id is None:
            raise RunConflict(f"active run does not exist: {registry_run_id}")

    def transition_run(
        self,
        registry_run_id: str,
        next_status: str,
        *,
        expected_revision: int,
        pid: int | None = None,
        return_code: int | None = None,
        failure_summary: str | None = None,
    ) -> RunRecord:
        current = self.get_run(registry_run_id)
        if current is None:
            raise KeyError(registry_run_id)
        if current.status == next_status:
            return current
        if next_status not in ALLOWED_TRANSITIONS[current.status]:
            raise InvalidRunTransition(f"{current.status} -> {next_status}")

        now_ms = _now_ms()
        values: dict[str, Any] = {
            "status": next_status,
            "revision": RunRow.revision + 1,
            "updated_at_ms": now_ms,
        }
        if pid is not None:
            values["pid"] = pid
        if next_status == "running" and current.started_at_ms is None:
            values["started_at_ms"] = now_ms
        if next_status in TERMINAL_STATUSES:
            values["completed_at_ms"] = now_ms
        if next_status == "cancel_requested":
            values["cancel_requested_at_ms"] = now_ms
        if return_code is not None:
            values["return_code"] = return_code
        if failure_summary is not None:
            values["failure_summary"] = failure_summary[:1000]

        updated_id = self._session.scalar(
            update(RunRow)
            .where(
                RunRow.id == registry_run_id,
                RunRow.revision == expected_revision,
            )
            .values(**values)
            .returning(RunRow.id)
        )
        if updated_id is None:
            raise StaleRunRevision(registry_run_id)
        next_revision = expected_revision + 1
        self._session.add(
            RunEventRow(
                run_id=registry_run_id,
                sequence=next_revision,
                event_type="status_changed",
                from_status=current.status,
                to_status=next_status,
                actor_type="mcp",
                details_json=_json({"return_code": return_code}),
                created_at_ms=now_ms,
            )
        )
        self._session.flush()
        refreshed = self.get_run(registry_run_id)
        assert refreshed is not None
        return refreshed

    @staticmethod
    def _record(row: RunRow, workspace_path: str) -> RunRecord:
        command = json.loads(row.command_json)
        request = json.loads(row.request_json)
        workspace = Path(workspace_path)
        return RunRecord(
            id=row.id,
            workspace_id=row.workspace_id,
            workspace_dir=workspace_path,
            external_run_id=row.external_run_id,
            first_run_id=row.first_run_id,
            attempt_number=row.attempt_number,
            binding=row.binding,
            pipeline=row.pipeline,
            workflow=row.workflow,
            status=row.status,
            revision=row.revision,
            plan_checksum=row.plan_checksum,
            request=request,
            command_argv=list(command["argv"]),
            run_dir=str(workspace / row.run_relative_path),
            approved_plan_path=str(workspace / row.approved_plan_relative_path),
            launch_log_path=request.get("execution_launch_log")
            or str(workspace / row.launch_log_relative_path),
            pid=row.pid,
            started_at_ms=row.started_at_ms,
            completed_at_ms=row.completed_at_ms,
            return_code=row.return_code,
            failure_summary=row.failure_summary,
            cancel_requested_at_ms=row.cancel_requested_at_ms,
            created_at_ms=row.created_at_ms,
            updated_at_ms=row.updated_at_ms,
        )


def _now_ms() -> int:
    return int(datetime.now(UTC).timestamp() * 1000)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
