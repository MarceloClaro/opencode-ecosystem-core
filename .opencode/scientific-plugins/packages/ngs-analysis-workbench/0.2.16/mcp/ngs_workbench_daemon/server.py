"""Authenticated loopback control plane held by one crash-releasing owner lock."""

from __future__ import annotations

import hmac
import json
import os
import socket
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from filelock import Timeout
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from . import inspection
from .protocol import (
    IMPLEMENTATION_ID,
    LOCAL_TARGET_PAYLOAD,
    MAX_REQUEST_BYTES,
    PROTOCOL_VERSION,
    ExecutionRequest,
    TargetConfiguration,
    TargetInspection,
)
from .runs import RunManager
from .state import (
    daemon_directory,
    daemon_runtime_directory,
    daemon_token,
    native_lock,
    read_private_json,
    write_private_json,
)

_TARGET_LOCK = threading.RLock()
IDLE_TIMEOUT_SECONDS = 60.0


def _list_targets() -> dict[str, Any]:
    with _TARGET_LOCK:
        saved = read_private_json(daemon_directory() / "targets.json") or {}
        targets = [LOCAL_TARGET_PAYLOAD, *(saved[key] for key in sorted(saved))]
    return {"count": len(targets), "targets": targets}


def list_target_summaries() -> dict[str, Any]:
    fields = {
        "target_id",
        "title",
        "provider",
        "controller_transport",
        "executor",
        "workspace_access",
        "description",
        "workspace_root",
        "executor_configuration",
    }
    targets = [
        {key: value for key, value in target.items() if key in fields}
        for target in _list_targets()["targets"]
    ]
    return {"count": len(targets), "targets": targets}


def _save_target(configuration: TargetConfiguration) -> dict[str, Any]:
    if configuration.target_id == "local":
        raise ValueError("the built-in local target cannot be replaced")
    target = configuration.model_dump(mode="json")
    with _TARGET_LOCK:
        path = daemon_directory() / "targets.json"
        saved = read_private_json(path) or {}
        saved[configuration.target_id] = target
        write_private_json(path, saved)
    return target


def _inspect_target(request: TargetInspection) -> dict[str, Any]:
    target = next(
        (
            target
            for target in _list_targets()["targets"]
            if target["target_id"] == request.target_id
        ),
        None,
    )
    if target is None:
        raise ValueError("requested compute target is not configured")
    if target.get("controller_transport") == "ssh" and (
        inspection.effective_access(target["host_access"]["alias"]) != target["host_access"]
    ):
        raise ValueError("configured SSH access has changed; reconfigure the compute target")
    return inspection.inspect_target(target, request)


class DaemonServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, token: str, instance_id: str) -> None:
        self.token = token
        self.instance_id = instance_id
        self.runs = RunManager(instance_id)
        self._activity_lock = threading.Lock()
        self._requests_in_flight = 0
        self._last_activity = time.monotonic()
        super().__init__(("127.0.0.1", 0), DaemonHandler)

    def process_request(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        # Reserve before starting the worker so an accepted request cannot look idle.
        with self._activity_lock:
            self._requests_in_flight += 1
        try:
            super().process_request(request, client_address)
        except Exception:
            self._request_finished()
            raise

    def process_request_thread(
        self, request: socket.socket, client_address: tuple[str, int]
    ) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._request_finished()

    def _request_finished(self) -> None:
        with self._activity_lock:
            self._requests_in_flight -= 1
            self._last_activity = time.monotonic()

    def serve_until_idle(self) -> None:
        self.timeout = min(1.0, IDLE_TIMEOUT_SECONDS)
        while True:
            self.handle_request()
            with self._activity_lock:
                if self._requests_in_flight:
                    self._last_activity = time.monotonic()
                    continue
                try:
                    busy = self.runs.has_active_work()
                except (OSError, RuntimeError, SQLAlchemyError):
                    # Unreadable run state cannot establish that shutdown is safe.
                    busy = True
                if busy:
                    self._last_activity = time.monotonic()
                elif time.monotonic() - self._last_activity >= IDLE_TIMEOUT_SECONDS:
                    return


class DaemonHandler(BaseHTTPRequestHandler):
    server: DaemonServer

    def log_message(self, format: str, *args: object) -> None:
        return None

    def _respond(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _authenticated(self) -> bool:
        authorization = self.headers.get("Authorization", "")
        instance_id = self.headers.get("X-NGS-Daemon-Instance", "")
        return hmac.compare_digest(authorization, f"Bearer {self.server.token}") and (
            hmac.compare_digest(instance_id, self.server.instance_id)
        )

    def _body(self) -> dict[str, Any]:
        value = self.headers.get("Content-Length")
        if value is None:
            raise ValueError("daemon request is missing its content length")
        try:
            length = int(value)
        except ValueError as exc:
            raise ValueError("daemon request content length is invalid") from exc
        if length < 0 or length > MAX_REQUEST_BYTES:
            raise ValueError("daemon request exceeds its maximum approved size")
        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            raise ValueError("daemon request contains invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("daemon request must contain a JSON object")
        return payload

    def do_GET(self) -> None:
        if not self._authenticated():
            self._respond(401, {"error": "daemon authentication failed"})
            return
        if self.path != "/health":
            self._respond(404, {"error": "daemon operation does not exist"})
            return
        self._respond(
            200,
            {
                "ok": True,
                "instance_id": self.server.instance_id,
                "protocol": PROTOCOL_VERSION,
                "implementation": IMPLEMENTATION_ID,
                "pid": os.getpid(),
            },
        )

    def do_POST(self) -> None:
        if not self._authenticated():
            self._respond(401, {"error": "daemon authentication failed"})
            return
        try:
            payload = self._body()
            if self.path in {
                "/runs",
                "/run",
                "/run/evidence",
                "/run/analysis-summary",
                "/cancel",
            } and (self.headers.get("X-NGS-Client-Role") != "workbench"):
                raise ValueError("compute clients cannot launch or manage scientific workflows")
            if self.path == "/runs":
                response = self.server.runs.execute(ExecutionRequest.model_validate(payload))
            elif self.path == "/targets":
                if payload:
                    raise ValueError("target listing does not accept arguments")
                response = _list_targets()
            elif self.path == "/targets/configure":
                if self.headers.get("X-NGS-Client-Role") != "compute":
                    raise ValueError("only compute clients can configure targets")
                response = _save_target(TargetConfiguration.model_validate(payload))
            elif self.path == "/targets/inspect":
                response = _inspect_target(TargetInspection.model_validate(payload))
            elif self.path == "/run/analysis-summary":
                registry_run_id = payload.get("registry_run_id")
                summary_path = payload.get("summary_path")
                if not isinstance(registry_run_id, str) or not isinstance(summary_path, str):
                    raise ValueError("summary submission requires a registry run id and file path")
                response = self.server.runs.update_analysis_summary(registry_run_id, summary_path)
            elif self.path == "/run/evidence":
                registry_run_id = payload.get("registry_run_id")
                if not isinstance(registry_run_id, str):
                    raise ValueError("registry_run_id must be a string")
                response = self.server.runs.observe_execution(registry_run_id)
            elif self.path in {"/run", "/cancel"}:
                registry_run_id = payload.get("registry_run_id")
                if not isinstance(registry_run_id, str):
                    raise ValueError("registry_run_id must be a string")
                operation = (
                    self.server.runs.observe if self.path == "/run" else self.server.runs.cancel
                )
                response = operation(registry_run_id)
            else:
                self._respond(404, {"error": "daemon operation does not exist"})
                return
        except (OSError, RuntimeError, ValidationError, ValueError) as exc:
            self._respond(400, {"error": str(exc)})
            return
        self._respond(200, response)


def main() -> int:
    shared_directory = daemon_directory()
    directory = daemon_runtime_directory(IMPLEMENTATION_ID)
    owner = native_lock(directory / "owner.lock", timeout=0)
    try:
        owner.acquire()
    except Timeout:
        return 0

    instance_id = uuid.uuid4().hex
    endpoint_path = directory / "endpoint.json"
    try:
        server = DaemonServer(daemon_token(shared_directory, create=True), instance_id)
        with server:
            write_private_json(
                endpoint_path,
                {
                    "host": "127.0.0.1",
                    "port": server.server_address[1],
                    "pid": os.getpid(),
                    "instance_id": instance_id,
                    "protocol": PROTOCOL_VERSION,
                    "implementation": IMPLEMENTATION_ID,
                },
            )
            server.serve_until_idle()
    finally:
        try:
            current = read_private_json(endpoint_path)
            if current is not None and current.get("instance_id") == instance_id:
                endpoint_path.unlink(missing_ok=True)
        finally:
            owner.release()
    return 0
