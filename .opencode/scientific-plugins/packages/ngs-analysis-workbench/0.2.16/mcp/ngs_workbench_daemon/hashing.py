"""Shared SHA-256 identities for workflow bytes, files, and source trees."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO

_CHUNK_SIZE = 1024 * 1024


def sha256_hex(value: bytes) -> str:
    """Return the unprefixed identity used by existing opaque identifiers."""
    return hashlib.sha256(value).hexdigest()


def sha256_bytes(value: bytes) -> str:
    """Return the canonical prefixed SHA-256 identity for exact bytes."""
    return f"sha256:{sha256_hex(value)}"


def stream_identity(stream: BinaryIO) -> tuple[int, str]:
    """Measure and hash the same bounded stream without buffering its contents."""
    digest = hashlib.sha256()
    size = 0
    for chunk in iter(lambda: stream.read(_CHUNK_SIZE), b""):
        size += len(chunk)
        digest.update(chunk)
    return size, f"sha256:{digest.hexdigest()}"


def file_identity(path: Path) -> tuple[int, str]:
    """Measure and hash the same streamed file contents."""
    with path.open("rb") as handle:
        return stream_identity(handle)


def sha256_file(path: Path) -> str:
    """Return the canonical identity of a file without loading it into memory."""
    return file_identity(path)[1]


def source_files(root: Path, *, excluded: frozenset[str] = frozenset()) -> list[Path]:
    """Return the deterministic, symlink-free reusable workflow source closure."""
    if root.is_symlink():
        raise ValueError(f"approved workflow tree must not be a symlink: {root}")
    entries = list(root.rglob("*"))
    if any(path.is_symlink() for path in entries):
        raise ValueError(f"approved workflow tree contains a symlink: {root}")
    return sorted(
        (
            path
            for path in entries
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
            and path.relative_to(root).as_posix() not in excluded
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def sha256_tree(root: Path, *, excluded: frozenset[str] = frozenset()) -> str:
    """Hash reusable source paths and bytes; preserved file modes are not source identity."""
    digest = hashlib.sha256()
    for path in source_files(root, excluded=excluded):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"
