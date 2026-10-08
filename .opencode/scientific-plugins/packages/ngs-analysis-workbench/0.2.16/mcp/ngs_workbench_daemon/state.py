"""Private daemon paths, native ownership locks, and atomic discovery state."""

from __future__ import annotations

import json
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any

from filelock import FileLock

from .hashing import sha256_hex

STATE_DIR_ENV = "NGS_ANALYSIS_WORKBENCH_STATE_DIR"
PLUGIN_STATE_DIR = Path("state") / "plugins" / "ngs-analysis-workbench"


def state_root() -> Path:
    """Resolve the configured private state root without creating it."""
    override = os.environ.get(STATE_DIR_ENV)
    if override:
        state_dir = Path(override).expanduser()
    else:
        codex_home = os.environ.get("CODEX_HOME")
        state_dir = (
            Path(codex_home).expanduser() / PLUGIN_STATE_DIR
            if codex_home
            else Path.home() / ".codex" / PLUGIN_STATE_DIR
        )
    if not state_dir.is_absolute():
        state_dir = Path.cwd() / state_dir
    if state_dir.is_symlink():
        raise OSError(f"plugin state directory must not be a symlink: {state_dir}")
    return state_dir.resolve(strict=False)


def daemon_directory(*, create: bool = True) -> Path:
    """Return one private daemon directory beneath the canonical Workbench root."""
    root = state_root()
    if not create and not root.is_dir():
        return root / "daemon"

    for directory in (root, root / "daemon"):
        if directory.is_symlink():
            raise OSError(f"daemon state directory must not be a symlink: {directory}")
        if create:
            directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        if directory.exists():
            information = directory.stat()
            if hasattr(os, "getuid") and information.st_uid != os.getuid():
                raise OSError(f"daemon state directory is not owned by this user: {directory}")
            if create:
                os.chmod(directory, 0o700)
    return root / "daemon"


def daemon_runtime_directory(implementation: str, *, create: bool = True) -> Path:
    """Return private ownership state for one MCP daemon implementation."""
    daemon = daemon_directory(create=create)
    identity = sha256_hex(implementation.encode("utf-8"))[:16]
    runtime = daemon / "runtimes" / identity
    for directory in (runtime.parent, runtime):
        if directory.is_symlink():
            raise OSError(f"daemon runtime directory must not be a symlink: {directory}")
        if create:
            directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        if directory.exists():
            information = directory.stat()
            if hasattr(os, "getuid") and information.st_uid != os.getuid():
                raise OSError(f"daemon runtime directory is not owned by this user: {directory}")
            if create:
                os.chmod(directory, 0o700)
    return runtime


def native_lock(path: Path, *, timeout: float) -> FileLock:
    """Require a crash-releasing OS lock; never fall back to a marker file."""
    return FileLock(
        path,
        timeout=timeout,
        mode=0o600,
        preserve_lock_file=True,
        fallback_to_soft=False,
    )


def read_private_json(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def write_private_json(path: Path, value: dict[str, Any]) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", prefix=f".{path.name}.", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, sort_keys=True)
            handle.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def daemon_token(directory: Path, *, create: bool = False) -> str:
    token_path = directory / "token"
    if create and not token_path.exists():
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", prefix=".token.", dir=directory, delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(secrets.token_urlsafe(32))
                handle.write("\n")
            temporary.replace(token_path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    if os.name != "nt" and token_path.stat().st_mode & 0o077:
        raise OSError(f"daemon token is not private: {token_path}")
    return token_path.read_text(encoding="utf-8").strip()


def execution_authorization_path(directory: Path, authorization: str) -> Path:
    """Resolve the private, single-use receipt for one native-approved request."""
    identity = sha256_hex(authorization.encode("utf-8"))
    return directory / f"authorization-{identity}.json"
