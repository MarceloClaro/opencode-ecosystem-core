"""Resolve daemon registry and workspace identity paths without planning effects."""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

from ..state import PLUGIN_STATE_DIR as PLUGIN_STATE_DIR
from ..state import STATE_DIR_ENV as STATE_DIR_ENV
from ..state import state_root


def registry_path() -> Path:
    """Return the canonical registry path without touching the filesystem."""
    return state_root() / "registry.sqlite3"


def prepare_registry_path(path: Path) -> Path:
    """Create the private state directory and reject symlinked registry targets."""
    path = path.expanduser()
    directory = path.parent
    if directory.is_symlink() or path.is_symlink():
        raise OSError(f"registry path must not be a symlink: {path}")
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    if hasattr(os, "getuid") and directory.stat().st_uid != os.getuid():
        raise OSError(f"plugin state directory is not owned by this user: {directory}")
    os.chmod(directory, 0o700)
    if path.exists() and not path.is_file():
        raise OSError(f"registry path is not a regular file: {path}")
    return path


def workspace_identity_path(workspace: Path) -> Path:
    """Return the identity document path for a workspace."""
    return workspace / "ngs_runs" / ".mcp" / "workspace.json"


def ensure_workspace_identity(workspace: Path) -> str:
    """Return the stable workspace UUID, creating it only for an approved start."""
    path = workspace_identity_path(workspace)
    if path.is_file():
        return _read_workspace_identity(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    identity = str(uuid.uuid4())
    payload = {
        "schema_version": 1,
        "workspace_id": identity,
        "created_at_ms": int(datetime.now(UTC).timestamp() * 1000),
    }
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".workspace.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError:
            return _read_workspace_identity(path)
        return identity
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def read_workspace_identity(workspace: Path) -> str | None:
    """Read an existing workspace identity without creating one."""
    path = workspace_identity_path(workspace)
    return _read_workspace_identity(path) if path.is_file() else None


def _read_workspace_identity(path: Path) -> str:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError(f"unsupported workspace identity document: {path}")
    workspace_id = value.get("workspace_id")
    if not isinstance(workspace_id, str):
        raise ValueError(f"workspace identity is missing a UUID: {path}")
    try:
        parsed = uuid.UUID(workspace_id)
    except ValueError as exc:
        raise ValueError(f"workspace identity is not a UUID: {path}") from exc
    if str(parsed) != workspace_id:
        raise ValueError(f"workspace identity UUID is not canonical: {path}")
    return workspace_id
