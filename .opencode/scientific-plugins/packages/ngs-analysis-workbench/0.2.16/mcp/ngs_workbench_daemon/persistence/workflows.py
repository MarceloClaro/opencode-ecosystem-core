"""Persist reusable workflows with the existing registry transaction."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .orm import WorkflowRow, WorkflowVersionRow


@dataclass(frozen=True)
class WorkflowEntryRecord:
    id: str
    name: str
    engine: str
    description: str | None
    metadata: dict[str, Any]
    owner: str
    current_version_id: str
    archived_at_ms: int | None
    created_at_ms: int
    updated_at_ms: int


@dataclass(frozen=True)
class WorkflowVersionRecord:
    id: str
    workflow_id: str
    source_kind: str
    local_root: str | None
    entrypoint: str | None
    source_sha256: str | None
    remote_workflow: str | None
    revision: str | None
    execution: dict[str, Any]
    created_at_ms: int


class WorkflowRepository:
    """Own only saved-workflow rows within the existing SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_entry(self, workflow_id: str) -> WorkflowEntryRecord | None:
        row = self._session.get(WorkflowRow, workflow_id)
        return self._entry_record(row) if row is not None else None

    def get_current_version(self, workflow_id: str) -> WorkflowVersionRecord | None:
        row = self._session.get(WorkflowRow, workflow_id)
        if row is None:
            return None
        version = self._session.get(WorkflowVersionRow, row.current_version_id)
        if version is None or version.workflow_id != workflow_id:
            raise ValueError("workflow current version is unavailable")
        return self._version_record(version)

    def list_entries(self) -> list[WorkflowEntryRecord]:
        rows = self._session.scalars(select(WorkflowRow).order_by(WorkflowRow.name)).all()
        return [self._entry_record(row) for row in rows]

    def list_versions(self, workflow_id: str) -> list[WorkflowVersionRecord]:
        rows = self._session.scalars(
            select(WorkflowVersionRow)
            .where(WorkflowVersionRow.workflow_id == workflow_id)
            .order_by(WorkflowVersionRow.created_at_ms, WorkflowVersionRow.id)
        ).all()
        return [self._version_record(row) for row in rows]

    def get_version(self, version_id: str) -> WorkflowVersionRecord | None:
        row = self._session.get(WorkflowVersionRow, version_id)
        return self._version_record(row) if row is not None else None

    def add_entry(self, entry: WorkflowEntryRecord) -> None:
        self._session.add(
            WorkflowRow(
                id=entry.id,
                name=entry.name,
                engine=entry.engine,
                description=entry.description,
                metadata_json=json.dumps(entry.metadata, sort_keys=True),
                owner=entry.owner,
                current_version_id=entry.current_version_id,
                archived_at_ms=entry.archived_at_ms,
                created_at_ms=entry.created_at_ms,
                updated_at_ms=entry.updated_at_ms,
            )
        )

    def add_version(self, version: WorkflowVersionRecord) -> None:
        self._session.add(
            WorkflowVersionRow(
                id=version.id,
                workflow_id=version.workflow_id,
                source_kind=version.source_kind,
                local_root=version.local_root,
                entrypoint=version.entrypoint,
                source_sha256=version.source_sha256,
                remote_workflow=version.remote_workflow,
                revision=version.revision,
                execution_json=json.dumps(version.execution, sort_keys=True),
                created_at_ms=version.created_at_ms,
            )
        )

    def reconcile_entry(
        self,
        workflow_id: str,
        *,
        name: str,
        description: str | None,
        metadata: dict[str, Any],
        current_version_id: str,
        archived_at_ms: int | None,
        updated_at_ms: int,
    ) -> None:
        row = self._session.get(WorkflowRow, workflow_id)
        if row is None:
            raise ValueError("workflow entry is unavailable")
        row.name = name
        row.description = description
        row.metadata_json = json.dumps(metadata, sort_keys=True)
        row.current_version_id = current_version_id
        row.archived_at_ms = archived_at_ms
        row.updated_at_ms = updated_at_ms

    def archive_entry(self, workflow_id: str, *, archived_at_ms: int) -> None:
        row = self._session.get(WorkflowRow, workflow_id)
        if row is None:
            raise ValueError("workflow entry is unavailable")
        row.archived_at_ms = archived_at_ms
        row.updated_at_ms = archived_at_ms

    def set_entry_state(
        self,
        workflow_id: str,
        *,
        current_version_id: str | None = None,
        archived_at_ms: int | None,
        updated_at_ms: int,
    ) -> None:
        row = self._session.get(WorkflowRow, workflow_id)
        if row is None:
            raise ValueError("workflow entry is unavailable")
        if current_version_id is not None:
            version = self._session.get(WorkflowVersionRow, current_version_id)
            if version is None or version.workflow_id != workflow_id:
                raise ValueError("workflow version does not belong to this entry")
            row.current_version_id = current_version_id
        row.archived_at_ms = archived_at_ms
        row.updated_at_ms = updated_at_ms

    @staticmethod
    def _entry_record(row: WorkflowRow) -> WorkflowEntryRecord:
        return WorkflowEntryRecord(
            id=row.id,
            name=row.name,
            engine=row.engine,
            description=row.description,
            metadata=json.loads(row.metadata_json),
            owner=row.owner,
            current_version_id=row.current_version_id,
            archived_at_ms=row.archived_at_ms,
            created_at_ms=row.created_at_ms,
            updated_at_ms=row.updated_at_ms,
        )

    @staticmethod
    def _version_record(row: WorkflowVersionRow) -> WorkflowVersionRecord:
        return WorkflowVersionRecord(
            id=row.id,
            workflow_id=row.workflow_id,
            source_kind=row.source_kind,
            local_root=row.local_root,
            entrypoint=row.entrypoint,
            source_sha256=row.source_sha256,
            remote_workflow=row.remote_workflow,
            revision=row.revision,
            execution=json.loads(row.execution_json),
            created_at_ms=row.created_at_ms,
        )
