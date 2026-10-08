"""Bounded, workspace-contained access to completed-run files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_SUMMARY_BYTES = 64 * 1024


def contained_run_directory(run_dir: Path, workspace_dir: Path) -> Path | None:
    try:
        root = run_dir.resolve(strict=True)
        workspace = workspace_dir.resolve(strict=True)
        root.relative_to(workspace)
    except (OSError, ValueError):
        return None
    return root if root.is_dir() else None


def safe_file(root: Path, relative_path: str) -> Path | None:
    candidate = root / relative_path
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def read_json(root: Path, relative_path: str) -> dict[str, Any]:
    path = safe_file(root, relative_path)
    if path is None:
        return {}
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def read_text(root: Path, relative_path: str, limit: int) -> str:
    path = safe_file(root, relative_path)
    if path is None:
        return ""
    try:
        with path.open("rb") as handle:
            return handle.read(limit + 1)[:limit].decode("utf-8", errors="replace")
    except OSError:
        return ""
