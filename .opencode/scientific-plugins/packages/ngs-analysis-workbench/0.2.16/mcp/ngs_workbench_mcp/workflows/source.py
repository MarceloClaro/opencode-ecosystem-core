"""Observe reusable workflow source without evaluating its contents."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Literal

from ngs_workbench_daemon.hashing import sha256_tree as source_sha256
from pydantic import BaseModel, Field


class WorkflowSource(BaseModel):
    """One engine-native source tree and its server-observed identity."""

    engine: Literal["snakemake", "nextflow"]
    kind: Literal["local"] = "local"
    root: str
    entrypoint: str
    source_sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")


def observe_source(source: WorkflowSource) -> WorkflowSource:
    """Resolve and independently identify an existing workflow source tree."""
    root = Path(source.root).expanduser()
    if not root.is_absolute():
        raise ValueError("workflow source root must be an absolute path")
    if root.is_symlink():
        raise ValueError("workflow source root must not be a symlink")
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("workflow source root does not exist")
    entrypoint = PurePosixPath(source.entrypoint)
    if entrypoint.is_absolute() or ".." in entrypoint.parts:
        raise ValueError("workflow entrypoint must remain inside its source directory")
    target = root.joinpath(*entrypoint.parts)
    if not target.is_file() or not target.resolve().is_relative_to(root):
        raise ValueError("workflow entrypoint is unavailable inside its source directory")
    digest = source_sha256(root)
    if source.source_sha256 is not None and source.source_sha256 != digest:
        raise ValueError("workflow source changed since its identity was observed")
    return source.model_copy(update={"root": str(root), "source_sha256": digest})
