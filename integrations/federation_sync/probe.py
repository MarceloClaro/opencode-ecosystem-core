# -*- coding: utf-8 -*-
"""R1014 — prova de protocolo MCP por stdio.

``probe`` prova transporte, handshake e catálogo. ``call_tool`` executa uma
única ferramenta e devolve o resultado. Nenhuma ferramenta é chamada sem que o
operador tenha autorizado o servidor correspondente.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import threading
import time
from typing import Any, Dict, Optional, Sequence

PROTOCOL_VERSION = "2024-11-05"
DEFAULT_TIMEOUT = 45


def _reader(stream, sink: "queue.Queue[str]") -> None:
    for line in iter(stream.readline, ""):
        sink.put(line)
    sink.put("")


def _extract(line: str) -> Optional[Dict[str, Any]]:
    line = line.strip()
    if not line.startswith("{"):
        return None
    try:
        value = json.loads(line)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def _wait_for(queue_in: "queue.Queue[str]", request_id: int,
              deadline: float) -> Optional[Dict[str, Any]]:
    while time.monotonic() < deadline:
        remaining = max(0.1, deadline - time.monotonic())
        try:
            line = queue_in.get(timeout=remaining)
        except queue.Empty:
            return None
        if line == "":
            return None
        message = _extract(line)
        if message and message.get("id") == request_id:
            return message
    return None


def _open(command: Sequence[str], cwd: Optional[Path], env: Optional[Dict[str, str]]):
    merged_env = dict(os.environ)
    merged_env.setdefault("NO_COLOR", "1")
    merged_env.update({str(k): str(v) for k, v in (env or {}).items()})
    process = subprocess.Popen(
        list(command), cwd=str(cwd) if cwd else None, env=merged_env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, start_new_session=True,
    )
    sink: "queue.Queue[str]" = queue.Queue()
    threading.Thread(target=_reader, args=(process.stdout, sink), daemon=True).start()
    return process, sink


def _close(process: subprocess.Popen) -> str:
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except (OSError, ProcessLookupError):
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except (OSError, ProcessLookupError):
            pass
    try:
        return (process.stderr.read() if process.stderr else "")[-600:]
    except (OSError, ValueError):
        return ""


def _initialize(process: subprocess.Popen, sink: "queue.Queue[str]",
                deadline: float) -> Optional[Dict[str, Any]]:
    process.stdin.write(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                   "clientInfo": {"name": "core-federation", "version": "1.0"}},
    }) + "\n")
    process.stdin.flush()
    response = _wait_for(sink, 1, deadline)
    if response and "error" not in response:
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        process.stdin.flush()
    return response


def probe(
    command: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Executa o handshake MCP e devolve o catálogo observado."""

    started = time.monotonic()
    result: Dict[str, Any] = {
        "ok": False, "command": list(command), "protocol_version": None,
        "server": {}, "tools": [], "tools_count": 0, "duration_ms": 0,
        "error": "", "stderr_tail": "",
    }
    try:
        process, sink = _open(command, cwd, env)
    except (OSError, ValueError) as exc:
        result["error"] = f"spawn: {exc}"
        return result

    deadline = time.monotonic() + timeout
    try:
        response = _initialize(process, sink, deadline)
        if not response:
            result["error"] = "sem resposta ao initialize"
            return result
        if "error" in response:
            result["error"] = f"initialize: {response['error']}"
            return result
        payload = response.get("result") or {}
        if not isinstance(payload, dict):
            result["error"] = "initialize: resultado inválido"
            return result
        result["protocol_version"] = payload.get("protocolVersion")
        result["server"] = payload.get("serverInfo") or {}

        process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}) + "\n")
        process.stdin.flush()
        listing = _wait_for(sink, 2, deadline)
        if not listing:
            result["error"] = "sem resposta ao tools/list"
            return result
        if "error" in listing or not isinstance(listing.get("result"), dict):
            result["error"] = f"tools/list: {listing.get('error', 'resultado inválido')}"
            return result
        tools = (listing.get("result") or {}).get("tools") or []
        if not isinstance(tools, list):
            result["error"] = "tools/list: catálogo inválido"
            return result
        result["tools"] = [str(tool.get("name")) for tool in tools if isinstance(tool, dict)]
        result["tools_count"] = len(result["tools"])
        result["ok"] = True
        return result
    except (BrokenPipeError, OSError) as exc:
        result["error"] = f"stdio: {exc}"
        return result
    finally:
        result["duration_ms"] = int((time.monotonic() - started) * 1000)
        result["stderr_tail"] = _close(process)


def call_tool(
    command: Sequence[str],
    tool: str,
    arguments: Dict[str, Any],
    *,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: int = 90,
) -> Dict[str, Any]:
    """Executa uma única ferramenta MCP e devolve o resultado observado."""

    started = time.monotonic()
    result: Dict[str, Any] = {
        "ok": False, "tool": tool, "error": "", "result": None,
        "duration_ms": 0, "stderr_tail": "",
    }
    try:
        process, sink = _open(command, cwd, env)
    except (OSError, ValueError) as exc:
        result["error"] = f"spawn: {exc}"
        return result

    deadline = time.monotonic() + timeout
    try:
        initialization = _initialize(process, sink, deadline)
        if not initialization:
            result["error"] = "sem resposta ao initialize"
            return result
        if "error" in initialization:
            result["error"] = f"initialize: {initialization['error']}"
            return result
        process.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        }) + "\n")
        process.stdin.flush()
        response = _wait_for(sink, 2, deadline)
        if not response:
            result["error"] = "sem resposta ao tools/call"
            return result
        if "error" in response:
            result["error"] = f"tools/call: {response['error']}"
            return result
        payload = response.get("result")
        result["result"] = payload
        if not isinstance(payload, dict):
            result["error"] = "tools/call: resultado inválido"
            return result
        if payload.get("isError") is True:
            content = payload.get("content")
            texts = [part.get("text", "") for part in content if isinstance(part, dict)
                     and isinstance(part.get("text"), str)] if isinstance(content, list) else []
            result["error"] = "tools/call isError: " + " ".join(texts)[:300]
            return result
        result["ok"] = True
        return result
    except (BrokenPipeError, OSError) as exc:
        result["error"] = f"stdio: {exc}"
        return result
    finally:
        result["duration_ms"] = int((time.monotonic() - started) * 1000)
        result["stderr_tail"] = _close(process)
