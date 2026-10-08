"""Discover run artifacts and project them into report entries."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .files import safe_file

MAX_DISCOVERED_ARTIFACTS = 2_000
MAX_REPORT_ENTRIES = 60

RESULT_ROOTS = (
    "results",
    "output",
    "outputs",
    "out",
    "counts",
    "visualizations",
    "notebooks",
    "tables",
    "qc",
    "fastqc",
    "multiqc",
    "rnaseq_salmon",
    "provenance",
    "variants",
    "peaks",
    "tracks",
)
_WORKFLOW_REPORTS = (
    "workflow/nextflow_report.html",
    "workflow/timeline.html",
    "workflow/dag.html",
    "workflow/trace.txt",
)
_ENTRY_STATUSES = {"created", "not_available", "blocked"}


@dataclass(frozen=True)
class ArtifactCollection:
    artifacts: list[dict[str, Any]]
    truncated: bool
    indexed: bool


def collect_artifacts(root: Path, artifact_index: dict[str, Any]) -> ArtifactCollection:
    indexed = _indexed_artifacts(root, artifact_index)
    if indexed:
        return ArtifactCollection(artifacts=indexed, truncated=False, indexed=True)
    discovered, truncated = _discover_artifacts(root)
    return ArtifactCollection(artifacts=discovered, truncated=truncated, indexed=False)


def build_report_entries(
    root: Path,
    visualization: dict[str, Any],
    artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sizes = {artifact["path"]: artifact.get("bytes") for artifact in artifacts}
    entries: list[dict[str, Any]] = []
    seen_paths: set[str] = set()

    raw_entries = visualization.get("entries")
    if isinstance(raw_entries, list):
        for index, raw in enumerate(raw_entries):
            entry = _visualization_entry(root, raw, sizes, index)
            if entry is None:
                continue
            entries.append(entry)
            if entry.get("path"):
                seen_paths.add(entry["path"])
            if len(entries) >= MAX_REPORT_ENTRIES:
                return entries

    remaining = sorted(
        (artifact for artifact in artifacts if artifact["path"] not in seen_paths),
        key=lambda artifact: (_kind_priority(artifact_kind(artifact["path"])), artifact["path"]),
    )
    for artifact in remaining:
        path = artifact["path"]
        kind = artifact_kind(path)
        entries.append(
            {
                "id": _entry_id(path),
                "title": artifact_title(path),
                "path": path,
                "kind": kind,
                "status": "created",
                "description": artifact_description(kind),
                "size_bytes": artifact.get("bytes"),
            }
        )
        if len(entries) >= MAX_REPORT_ENTRIES:
            break
    return entries


def artifact_title(path: str) -> str:
    name = Path(path).name
    for suffix in (".marimo.py", ".html", ".json", ".csv", ".tsv", ".txt", ".md"):
        if name.lower().endswith(suffix):
            name = name[: -len(suffix)]
            break
    return humanize(name)


def humanize(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title()


def _indexed_artifacts(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_artifacts = payload.get("artifacts")
    if not isinstance(raw_artifacts, list):
        return []
    artifacts: list[dict[str, Any]] = []
    for raw in raw_artifacts:
        if not isinstance(raw, dict):
            continue
        path = _safe_relative_path(raw.get("path"))
        if path is None:
            continue
        resolved = safe_file(root, path)
        if resolved is None:
            continue
        try:
            size = resolved.stat().st_size
        except OSError:
            continue
        artifacts.append(
            {
                "path": path,
                "bytes": size,
            }
        )
    return artifacts


def _discover_artifacts(root: Path) -> tuple[list[dict[str, Any]], bool]:
    paths: list[Path] = []
    for relative_path in _WORKFLOW_REPORTS:
        path = safe_file(root, relative_path)
        if path is not None:
            paths.append(path)
    for dirname in RESULT_ROOTS:
        directory = root / dirname
        if not directory.is_dir():
            continue
        for parent, children, filenames in os.walk(directory, topdown=True):
            children[:] = sorted(name for name in children if not name.startswith("."))
            for name in sorted(filenames):
                if name.startswith("."):
                    continue
                path = Path(parent) / name
                if path.is_file():
                    paths.append(path)
                    if len(paths) >= MAX_DISCOVERED_ARTIFACTS:
                        break
            if len(paths) >= MAX_DISCOVERED_ARTIFACTS:
                break
        if len(paths) >= MAX_DISCOVERED_ARTIFACTS:
            break

    artifacts: list[dict[str, Any]] = []
    for path in paths[:MAX_DISCOVERED_ARTIFACTS]:
        try:
            resolved = path.resolve(strict=True)
            relative = resolved.relative_to(root).as_posix()
            size = resolved.stat().st_size
        except (OSError, ValueError):
            continue
        artifacts.append({"path": relative, "bytes": size})
    return artifacts, len(paths) >= MAX_DISCOVERED_ARTIFACTS


def _visualization_entry(
    root: Path,
    raw: object,
    sizes: dict[str, int | None],
    index: int,
) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    raw_path = raw.get("path")
    open_url = _loopback_url(raw_path)
    path = open_url or _safe_relative_path(raw_path)
    status = _string(raw.get("status")) or "not_available"
    if status not in _ENTRY_STATUSES:
        status = "not_available"
    if status == "created" and open_url is None:
        if path is None or safe_file(root, path) is None:
            path = None
            status = "not_available"
    kind = _string(raw.get("kind")) or (artifact_kind(path) if path else "file")
    title = _string(raw.get("title")) or (artifact_title(path) if path else f"Artifact {index + 1}")
    return {
        "id": _string(raw.get("id")) or f"visual-{index + 1}",
        "title": title,
        "path": path,
        "open_url": open_url,
        "kind": kind,
        "status": status,
        "description": _string(raw.get("description")) or artifact_description(kind),
        "size_bytes": sizes.get(path) if path else None,
    }


def _safe_relative_path(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts or urlparse(normalized).scheme:
        return None
    return path.as_posix()


def _loopback_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        return None
    return value


def artifact_kind(path: str | None) -> str:
    if not path:
        return "file"
    lower = path.lower()
    if lower.endswith((".html", ".htm")):
        return "html_report"
    if "/notebooks/" in f"/{lower}" or lower.endswith((".ipynb", ".marimo.py")):
        return "notebook"
    if lower.endswith((".csv", ".tsv", ".parquet", ".feather")):
        return "table"
    if lower.endswith((".png", ".jpg", ".jpeg", ".svg", ".pdf")):
        return "plot"
    if lower.endswith(".json"):
        return "json"
    if lower.endswith((".md", ".txt", ".log")):
        return "text"
    return "file"


def _kind_priority(kind: str) -> int:
    return {
        "html_report": 0,
        "notebook": 1,
        "plot": 2,
        "table": 3,
        "json": 4,
        "text": 5,
        "file": 6,
    }.get(kind, 7)


def artifact_description(kind: str) -> str:
    return {
        "html_report": "Generated HTML analysis report.",
        "notebook": "Generated interactive analysis notebook.",
        "plot": "Generated analysis figure.",
        "table": "Tabular output for downstream analysis.",
        "json": "Machine-readable analysis output.",
        "text": "Generated text output.",
    }.get(kind, "Generated workflow artifact.")


def _entry_id(path: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-") or "artifact"


def _string(value: object) -> str:
    return value.strip()[:2_000] if isinstance(value, str) else ""
