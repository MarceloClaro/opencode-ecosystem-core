"""Load installation-owned workflows into the durable catalog."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from ngs_workbench_daemon.hashing import sha256_hex, sha256_tree
from ngs_workbench_daemon.persistence import SqlAlchemyUnitOfWork, default_database
from ngs_workbench_daemon.persistence.workflows import (
    WorkflowEntryRecord,
    WorkflowRepository,
    WorkflowVersionRecord,
)

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WORKFLOWS_PATH = PLUGIN_ROOT / "references" / "default-workflows.json"
logger = logging.getLogger(__name__)


def load_default_workflows(path: Path = DEFAULT_WORKFLOWS_PATH) -> list[dict[str, Any]]:
    """Read the installation-maintained workflow records."""
    return json.loads(path.read_text(encoding="utf-8"))["workflows"]


def _local_source_sha256(workflow: dict[str, Any]) -> str:
    source = workflow["source"]
    root = PLUGIN_ROOT / source["root"]
    entrypoint = root / source["entrypoint"]
    config = root / workflow["execution"]["default_config"]
    if not root.is_dir() or not entrypoint.is_file() or not config.is_file():
        raise ValueError(f"bundled workflow files are unavailable: {workflow['workflow_id']}")
    return sha256_tree(root)


def _version(workflow: dict[str, Any], timestamp: int) -> WorkflowVersionRecord:
    source = workflow["source"]
    local = source["kind"] == "local"
    source_sha256 = _local_source_sha256(workflow) if local else None
    execution = workflow["execution"]
    identity = {
        "workflow_id": workflow["workflow_id"],
        "engine": workflow["engine"],
        "source": source,
        "source_sha256": source_sha256,
        "execution": execution,
    }
    digest = sha256_hex(json.dumps(identity, sort_keys=True).encode("utf-8"))
    return WorkflowVersionRecord(
        id=f"version-{digest[:32]}",
        workflow_id=workflow["workflow_id"],
        source_kind=source["kind"],
        local_root=source.get("root"),
        entrypoint=source.get("entrypoint"),
        source_sha256=source_sha256,
        remote_workflow=source.get("workflow"),
        revision=source.get("revision"),
        execution=execution,
        created_at_ms=timestamp,
    )


def bootstrap_default_workflows(path: Path = DEFAULT_WORKFLOWS_PATH) -> list[str]:
    """Reconcile the installed JSON records in one catalog transaction."""
    timestamp = time.time_ns() // 1_000_000
    desired = {
        item["workflow_id"]: (item, _version(item, timestamp))
        for item in load_default_workflows(path)
    }
    warnings: list[str] = []
    with SqlAlchemyUnitOfWork(default_database(), immediate=True) as unit_of_work:
        assert unit_of_work.session is not None
        repository = WorkflowRepository(unit_of_work.session)
        existing = {entry.id: entry for entry in repository.list_entries()}
        for entry in existing.values():
            if (
                entry.owner == "bundled"
                and entry.id not in desired
                and entry.archived_at_ms is None
            ):
                repository.archive_entry(entry.id, archived_at_ms=timestamp)
        for workflow_id, (workflow, version) in desired.items():
            current = existing.get(workflow_id)
            if current is not None and current.owner != "bundled":
                warning = f"default workflow {workflow_id!r} conflicts with a user-owned entry"
                logger.warning(warning)
                warnings.append(warning)
                continue
            if current is not None and current.engine != workflow["engine"]:
                raise ValueError(f"bundled workflow {workflow_id!r} cannot change engine")
            metadata = {"collection": workflow["collection"]} if workflow.get("collection") else {}
            if current is None:
                repository.add_entry(
                    WorkflowEntryRecord(
                        id=workflow_id,
                        name=workflow["name"],
                        engine=workflow["engine"],
                        description=workflow.get("description"),
                        metadata=metadata,
                        owner="bundled",
                        current_version_id=version.id,
                        archived_at_ms=None,
                        created_at_ms=timestamp,
                        updated_at_ms=timestamp,
                    )
                )
                repository.add_version(version)
                continue
            versions = {item.id for item in repository.list_versions(workflow_id)}
            if version.id not in versions:
                repository.add_version(version)
            repository.reconcile_entry(
                workflow_id,
                name=workflow["name"],
                description=workflow.get("description"),
                metadata=metadata,
                current_version_id=version.id,
                archived_at_ms=None,
                updated_at_ms=timestamp,
            )
        unit_of_work.commit()
    return warnings
