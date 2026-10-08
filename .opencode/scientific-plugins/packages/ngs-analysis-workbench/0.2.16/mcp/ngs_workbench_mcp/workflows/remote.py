"""Bind reusable workflow source deployment to SSH plans."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from ngs_workbench_daemon.hashing import file_identity, source_files

from ..plans import RemoteStagedFile


def staged_source_files(
    *,
    source_root: Path,
    local_run_dir: Path,
    remote_run_dir: PurePosixPath,
) -> list[RemoteStagedFile]:
    """Describe future approved files from an immutable local source snapshot."""
    entries = [
        (path.relative_to(source_root).as_posix(), *file_identity(path))
        for path in source_files(source_root)
    ]
    return [
        RemoteStagedFile(
            source=str(local_run_dir / "workflow" / relative),
            destination=(remote_run_dir / "workflow" / relative).as_posix(),
            bytes=size,
            sha256=digest,
        )
        for relative, size, digest in entries
    ]
