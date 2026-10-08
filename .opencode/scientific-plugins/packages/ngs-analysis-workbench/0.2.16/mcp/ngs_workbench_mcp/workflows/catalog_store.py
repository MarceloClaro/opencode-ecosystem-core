"""Public workflow catalog operations over stable entries and immutable versions."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import time
from dataclasses import replace
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal

from ngs_workbench_daemon.hashing import sha256_hex, sha256_tree
from ngs_workbench_daemon.persistence import SqlAlchemyUnitOfWork, default_database
from ngs_workbench_daemon.persistence.workflows import (
    WorkflowEntryRecord,
    WorkflowRepository,
    WorkflowVersionRecord,
)
from ngs_workbench_daemon.state import state_root
from pydantic import BaseModel, ConfigDict, Field


class LocalWorkflowSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["local"]
    root: str = Field(min_length=1)
    entrypoint: str = Field(min_length=1)


class RemoteWorkflowSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["remote"]
    workflow: str = Field(min_length=1)
    revision: str = Field(min_length=1)


WorkflowSaveSource = Annotated[
    LocalWorkflowSource | RemoteWorkflowSource, Field(discriminator="kind")
]


def _workflow_id(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,95}", value):
        raise ValueError("workflow ID must be a safe lowercase identifier")
    return value


def _observe_source(engine: str, source: WorkflowSaveSource) -> tuple[dict[str, str], str | None]:
    if isinstance(source, RemoteWorkflowSource):
        if engine != "nextflow":
            raise ValueError("remote workflow sources are currently supported only by Nextflow")
        workflow = source.workflow.strip()
        revision = source.revision.strip()
        if not workflow or not revision:
            raise ValueError("remote workflow and revision must be non-empty")
        if workflow.startswith("-") or revision.startswith("-"):
            raise ValueError("remote workflow and revision must not start with '-'")
        return {"kind": "remote", "workflow": workflow, "revision": revision}, None
    root = Path(source.root).expanduser()
    if not root.is_absolute() or root.is_symlink():
        raise ValueError("local workflow root must be an absolute, non-symlink directory")
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("local workflow root does not exist")
    entrypoint = PurePosixPath(source.entrypoint)
    if entrypoint.is_absolute() or not entrypoint.parts or ".." in entrypoint.parts:
        raise ValueError("workflow entrypoint must remain inside its source directory")
    target = root.joinpath(*entrypoint.parts)
    if not target.is_file() or not target.resolve().is_relative_to(root):
        raise ValueError("workflow entrypoint is unavailable inside its source directory")
    return {
        "kind": "local",
        "root": str(root),
        "entrypoint": entrypoint.as_posix(),
    }, sha256_tree(root)


def _new_version(
    workflow_id: str,
    engine: str,
    source: WorkflowSaveSource,
    timestamp: int,
) -> WorkflowVersionRecord:
    observed, source_sha256 = _observe_source(engine, source)
    execution = {"parameter_contract": "generic"} if engine == "nextflow" else {}
    identity_source = (
        observed
        if observed["kind"] == "remote"
        else {"kind": "local", "entrypoint": observed["entrypoint"]}
    )
    identity = {
        "workflow_id": workflow_id,
        "engine": engine,
        "source": identity_source,
        "source_sha256": source_sha256,
        "execution": execution,
    }
    digest = sha256_hex(json.dumps(identity, sort_keys=True).encode("utf-8"))
    version = WorkflowVersionRecord(
        id=f"version-{digest[:32]}",
        workflow_id=workflow_id,
        source_kind=observed["kind"],
        local_root=observed.get("root"),
        entrypoint=observed.get("entrypoint"),
        source_sha256=source_sha256,
        remote_workflow=observed.get("workflow"),
        revision=observed.get("revision"),
        execution=execution,
        created_at_ms=timestamp,
    )
    if observed["kind"] == "local":
        assert source_sha256 is not None
        managed_root = _snapshot_local_source(
            workflow_id,
            version.id,
            Path(observed["root"]),
            source_sha256,
        )
        version = replace(version, local_root=str(managed_root))
    return version


def _snapshot_local_source(
    workflow_id: str,
    version_id: str,
    source_root: Path,
    expected_sha256: str,
) -> Path:
    catalog_root = (state_root() / "workflow-catalog").resolve()
    if catalog_root.is_relative_to(source_root) or source_root.is_relative_to(catalog_root):
        raise ValueError("workflow source must not overlap the managed catalog directory")
    parent = catalog_root / workflow_id
    destination = parent / version_id
    parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if destination.exists():
        if not destination.is_dir() or sha256_tree(destination) != expected_sha256:
            raise ValueError("managed workflow version does not match its catalog identity")
        return destination
    with tempfile.TemporaryDirectory(prefix=".snapshot-", dir=parent) as temporary:
        staged = Path(temporary) / "source"
        shutil.copytree(source_root, staged)
        if sha256_tree(staged) != expected_sha256:
            raise ValueError("workflow source changed while it was being saved")
        os.replace(staged, destination)
    return destination


def _source_descriptor(version: WorkflowVersionRecord) -> dict[str, Any]:
    if version.source_kind == "local":
        return {
            "kind": "local",
            "root": version.local_root,
            "entrypoint": version.entrypoint,
            "source_sha256": version.source_sha256,
        }
    if version.source_kind == "remote":
        return {
            "kind": "remote",
            "workflow": version.remote_workflow,
            "revision": version.revision,
        }
    raise ValueError(f"unsupported workflow source kind: {version.source_kind}")


def _descriptor(entry: WorkflowEntryRecord, version: WorkflowVersionRecord) -> dict[str, Any]:
    return {
        "workflow_id": entry.id,
        "name": entry.name,
        "engine": entry.engine,
        "description": entry.description,
        "source": _source_descriptor(version),
        "current_version_id": entry.current_version_id,
        "catalog": entry.owner,
        "archived": entry.archived_at_ms is not None,
        **({"collection": entry.metadata["collection"]} if "collection" in entry.metadata else {}),
    }


def _current_descriptor(
    repository: WorkflowRepository, entry: WorkflowEntryRecord
) -> dict[str, Any]:
    version = repository.get_current_version(entry.id)
    if version is None:
        raise ValueError("workflow current version is unavailable")
    return _descriptor(entry, version)


def list_workflows(engine: str | None = None, *, include_archived: bool = False) -> dict[str, Any]:
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.session is not None
        repository = WorkflowRepository(unit_of_work.session)
        entries = repository.list_entries()
        selected = [
            _current_descriptor(repository, entry)
            for entry in entries
            if (engine is None or entry.engine == engine)
            and (include_archived or entry.archived_at_ms is None)
        ]
    return {"count": len(selected), "workflows": selected}


def save_workflow(
    workflow_id: str,
    name: str,
    engine: Literal["nextflow", "snakemake"],
    source: WorkflowSaveSource,
    description: str | None = None,
) -> dict[str, Any]:
    workflow_id = _workflow_id(workflow_id)
    name = name.strip()
    if not name:
        raise ValueError("workflow name is required")
    timestamp = time.time_ns() // 1_000_000
    with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
        assert unit_of_work.session is not None
        repository = WorkflowRepository(unit_of_work.session)
        if repository.get_entry(workflow_id) is not None:
            raise ValueError("a workflow with this ID already exists")
        version = _new_version(workflow_id, engine, source, timestamp)
        entry = WorkflowEntryRecord(
            id=workflow_id,
            name=name,
            engine=engine,
            description=description,
            metadata={},
            owner="user",
            current_version_id=version.id,
            archived_at_ms=None,
            created_at_ms=timestamp,
            updated_at_ms=timestamp,
        )
        repository.add_entry(entry)
        repository.add_version(version)
        unit_of_work.commit()
    return _descriptor(entry, version)


def update_workflow(workflow_id: str, source: WorkflowSaveSource) -> dict[str, Any]:
    workflow_id = _workflow_id(workflow_id)
    timestamp = time.time_ns() // 1_000_000
    with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
        assert unit_of_work.session is not None
        repository = WorkflowRepository(unit_of_work.session)
        entry = repository.get_entry(workflow_id)
        if entry is None:
            raise ValueError("workflow entry is unavailable")
        if entry.owner != "user":
            raise ValueError("bundled workflows cannot be updated")
        version = _new_version(workflow_id, entry.engine, source, timestamp)
        if repository.get_version(version.id) is None:
            repository.add_version(version)
        else:
            version = repository.get_version(version.id)
            assert version is not None
        repository.set_entry_state(
            workflow_id,
            current_version_id=version.id,
            archived_at_ms=None,
            updated_at_ms=timestamp,
        )
        unit_of_work.commit()
        updated = repository.get_entry(workflow_id)
        assert updated is not None
    return _descriptor(updated, version)


def list_workflow_versions(workflow_id: str) -> dict[str, Any]:
    workflow_id = _workflow_id(workflow_id)
    with SqlAlchemyUnitOfWork(default_database()) as unit_of_work:
        assert unit_of_work.session is not None
        repository = WorkflowRepository(unit_of_work.session)
        entry = repository.get_entry(workflow_id)
        if entry is None:
            raise ValueError("workflow entry is unavailable")
        versions = repository.list_versions(workflow_id)
    return {
        "workflow_id": workflow_id,
        "current_version_id": entry.current_version_id,
        "versions": [
            {
                "version_id": version.id,
                "source": _source_descriptor(version),
                "created_at_ms": version.created_at_ms,
                "active": version.id == entry.current_version_id,
            }
            for version in versions
        ],
    }


def activate_workflow_version(workflow_id: str, version_id: str) -> dict[str, Any]:
    return _set_state(workflow_id, version_id=version_id, archived=False)


def archive_workflow(workflow_id: str) -> dict[str, Any]:
    return _set_state(workflow_id, archived=True)


def restore_workflow(workflow_id: str) -> dict[str, Any]:
    return _set_state(workflow_id, archived=False)


def _set_state(
    workflow_id: str,
    *,
    version_id: str | None = None,
    archived: bool,
) -> dict[str, Any]:
    workflow_id = _workflow_id(workflow_id)
    timestamp = time.time_ns() // 1_000_000
    with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
        assert unit_of_work.session is not None
        repository = WorkflowRepository(unit_of_work.session)
        entry = repository.get_entry(workflow_id)
        if entry is None:
            raise ValueError("workflow entry is unavailable")
        if entry.owner != "user":
            raise ValueError("bundled workflow lifecycle is managed by the installation")
        repository.set_entry_state(
            workflow_id,
            current_version_id=version_id,
            archived_at_ms=timestamp if archived else None,
            updated_at_ms=timestamp,
        )
        unit_of_work.commit()
        updated = repository.get_entry(workflow_id)
        version = repository.get_current_version(workflow_id)
        assert updated is not None and version is not None
    return _descriptor(updated, version)
