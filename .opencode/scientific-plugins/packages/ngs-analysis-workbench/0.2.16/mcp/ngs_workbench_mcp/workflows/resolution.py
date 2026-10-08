"""Resolve one catalog version into an engine execution binding."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ngs_workbench_daemon.persistence import SqlAlchemyUnitOfWork, default_database
from ngs_workbench_daemon.persistence.workflows import (
    WorkflowEntryRecord,
    WorkflowRepository,
    WorkflowVersionRecord,
)

from .defaults import PLUGIN_ROOT
from .source import WorkflowSource


@dataclass(frozen=True)
class ResolvedWorkflow:
    entry: WorkflowEntryRecord
    version: WorkflowVersionRecord

    def local_execution_source(self) -> WorkflowSource | None:
        version = self.version
        if version.source_kind != "local":
            return None
        assert version.local_root is not None and version.entrypoint is not None
        root = Path(version.local_root)
        if self.entry.owner == "bundled":
            root = PLUGIN_ROOT / root
        return WorkflowSource(
            engine=self.entry.engine,
            kind="local",
            root=str(root.resolve()),
            entrypoint=version.entrypoint,
            source_sha256=version.source_sha256,
        )


def resolve_workflow(workflow_id: str, engine: str | None = None) -> ResolvedWorkflow:
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.session is not None
        repository = WorkflowRepository(unit_of_work.session)
        entry = repository.get_entry(workflow_id)
        version = repository.get_current_version(workflow_id)
    if entry is None or version is None or entry.archived_at_ms is not None:
        raise ValueError(f"workflow is unavailable: {workflow_id}")
    if engine is not None and entry.engine != engine:
        raise ValueError(f"workflow {workflow_id!r} is not a {engine} workflow")
    return ResolvedWorkflow(entry=entry, version=version)
