"""Lazy, authenticated access to the one detached Workbench state owner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from http.client import HTTPConnection, HTTPException
from pathlib import Path
from typing import Any, Literal

from filelock import Timeout

from .protocol import IMPLEMENTATION_ID, PROTOCOL_VERSION, ExecutionRequest
from .state import (
    STATE_DIR_ENV,
    daemon_directory,
    daemon_runtime_directory,
    daemon_token,
    native_lock,
    read_private_json,
    state_root,
)

STARTUP_TIMEOUT_SECONDS = 15.0
REQUEST_TIMEOUT_SECONDS = 10.0
_SPAWNED_DAEMON: subprocess.Popen[bytes] | None = None


class DaemonError(RuntimeError):
    """The authenticated local execution owner could not satisfy a request."""


class _ConnectionUnavailable(DaemonError):
    """Connection failed before any HTTP request bytes were sent."""


@dataclass(frozen=True)
class DaemonEndpoint:
    host: str
    port: int
    instance_id: str
    implementation: str


def _endpoint(directory: Path) -> DaemonEndpoint | None:
    metadata = read_private_json(directory / "endpoint.json")
    if metadata is None:
        return None
    if metadata.get("host") != "127.0.0.1" or metadata.get("protocol") != PROTOCOL_VERSION:
        return None
    port = metadata.get("port")
    instance_id = metadata.get("instance_id")
    implementation = metadata.get("implementation", "")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        return None
    if not isinstance(instance_id, str) or not isinstance(implementation, str):
        return None
    return DaemonEndpoint("127.0.0.1", port, instance_id, implementation)


def _request(
    endpoint: DaemonEndpoint,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
    role: Literal["workbench", "compute"] = "workbench",
) -> dict[str, Any]:
    directory = daemon_directory(create=False)
    token = daemon_token(directory)
    encoded = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    connection = HTTPConnection(endpoint.host, endpoint.port, timeout=timeout)
    try:
        try:
            connection.connect()
        except OSError as exc:
            raise _ConnectionUnavailable(
                f"local Workbench daemon connection failed: {exc}"
            ) from exc
        connection.request(
            "GET" if payload is None else "POST",
            path,
            body=encoded,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-NGS-Daemon-Instance": endpoint.instance_id,
                "X-NGS-Client-Role": role,
            },
        )
        response = connection.getresponse()
        value = json.loads(response.read())
        if response.status >= 400:
            detail = value.get("error") if isinstance(value, dict) else None
            raise DaemonError(str(detail or f"daemon request failed with status {response.status}"))
    except (OSError, HTTPException, json.JSONDecodeError) as exc:
        raise DaemonError(f"local Workbench daemon request failed: {exc}") from exc
    finally:
        connection.close()
    if not isinstance(value, dict):
        raise DaemonError("local Workbench daemon returned an invalid response")
    return value


def healthy_daemon() -> DaemonEndpoint | None:
    """Discover the authenticated owner for this MCP implementation."""
    directory = daemon_runtime_directory(IMPLEMENTATION_ID, create=False)
    if not directory.is_dir():
        return None
    try:
        endpoint = _endpoint(directory)
        if endpoint is None:
            return None
        response = _request(endpoint, "/health", timeout=0.5)
    except (DaemonError, OSError, ValueError):
        return None
    if (
        response.get("instance_id") != endpoint.instance_id
        or response.get("protocol") != PROTOCOL_VERSION
        or response.get("implementation", "") != endpoint.implementation
    ):
        return None
    if endpoint.implementation != IMPLEMENTATION_ID:
        return None
    return endpoint


def _owner_is_held(directory: Path) -> bool:
    owner = native_lock(directory / "owner.lock", timeout=0)
    try:
        owner.acquire()
    except Timeout:
        return True
    else:
        owner.release()
        return False


def _spawn_daemon() -> subprocess.Popen[bytes]:
    global _SPAWNED_DAEMON

    mcp_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment[STATE_DIR_ENV] = str(state_root())
    search_paths = [str(mcp_root)]
    if environment.get("PYTHONPATH"):
        search_paths.extend(
            str(Path(path).resolve()) if path else str(Path.cwd())
            for path in environment["PYTHONPATH"].split(os.pathsep)
        )
    environment["PYTHONPATH"] = os.pathsep.join(search_paths)
    options: dict[str, Any] = {
        "cwd": str(mcp_root),
        "env": environment,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    else:
        options["start_new_session"] = True
    _SPAWNED_DAEMON = subprocess.Popen([sys.executable, "-m", "ngs_workbench_daemon"], **options)
    return _SPAWNED_DAEMON


def ensure_daemon_running() -> DaemonEndpoint:
    """Return the live daemon for this MCP implementation."""
    endpoint = healthy_daemon()
    if endpoint is not None:
        return endpoint

    shared_directory = daemon_directory()
    directory = daemon_runtime_directory(IMPLEMENTATION_ID)
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    lock = native_lock(shared_directory / "startup.lock", timeout=STARTUP_TIMEOUT_SECONDS)
    try:
        lock.acquire()
    except Timeout:
        raise DaemonError("timed out waiting for the Workbench daemon startup lock") from None
    try:
        process = None
        while time.monotonic() < deadline:
            endpoint = healthy_daemon()
            if endpoint is not None:
                return endpoint
            if process is not None and process.poll() not in {None, 0}:
                raise DaemonError(
                    f"local Workbench daemon exited during startup: {process.returncode}"
                )
            if _owner_is_held(directory):
                metadata = read_private_json(directory / "endpoint.json")
                if metadata is not None and metadata.get("protocol") != PROTOCOL_VERSION:
                    raise DaemonError(
                        "the running Workbench daemon uses an incompatible protocol; "
                        "stop the existing daemon and retry"
                    )
            elif process is None or process.poll() is not None:
                process = _spawn_daemon()
            time.sleep(0.05)
        raise DaemonError("timed out waiting for the authenticated Workbench daemon owner")
    finally:
        lock.release()


def execute(execution_request: ExecutionRequest) -> dict[str, Any]:
    return request("/runs", execution_request.model_dump(mode="json"))


def request(
    path: str,
    payload: dict[str, Any],
    *,
    role: Literal["workbench", "compute"] = "workbench",
    timeout: float = REQUEST_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Send one authenticated request to the shared local daemon."""
    try:
        return _request(ensure_daemon_running(), path, payload, role=role, timeout=timeout)
    except _ConnectionUnavailable:
        return _request(ensure_daemon_running(), path, payload, role=role, timeout=timeout)


def observe(registry_run_id: str) -> dict[str, Any] | None:
    endpoint = healthy_daemon()
    if endpoint is None:
        return None
    try:
        return _request(
            endpoint,
            "/run",
            {"registry_run_id": registry_run_id},
        )
    except DaemonError:
        if healthy_daemon() is None:
            return None
        raise


def observe_execution(registry_run_id: str) -> dict[str, Any]:
    return request("/run/evidence", {"registry_run_id": registry_run_id}, timeout=50)


def cancel(registry_run_id: str) -> dict[str, Any]:
    return request(
        "/cancel",
        {"registry_run_id": registry_run_id},
    )
