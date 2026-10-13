"""SPEC-935-R808: transporte MCP hermético; REA e providers não simulam prova real."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time

import pytest

from integrations.rea_bridge import ReaBridge


FAKE_SERVER = r'''
import json, os, signal, subprocess, sys, time
from pathlib import Path
root = Path(__file__).resolve().parent.parent
mode = (root / "mode").read_text().strip()
(root / "pid").write_text(str(os.getpid()))
if mode == "stall":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    child = subprocess.Popen([sys.executable, "-c", "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(60)"])
    (root / "child_pid").write_text(str(child.pid))
tools = [
    {"name": "binary_session", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "analyze_javascript_application", "inputSchema": {"type": "object", "required": ["input_path"], "properties": {"input_path": {"type": "string"}, "detail": {"enum": ["complete", "summary"]}}}, "outputSchema": {"type": "object"}},
    {"name": "run_binary", "inputSchema": {"type": "object", "properties": {}}},
]
for line in sys.stdin:
    message = json.loads(line)
    with (root / "requests.jsonl").open("a") as log:
        log.write(json.dumps(message) + "\n")
    method = message.get("method")
    if "id" not in message:
        continue
    if mode == "stall":
        time.sleep(60)
    if method == "initialize":
        result = {"protocolVersion": message["params"]["protocolVersion"], "capabilities": {"tools": {}}, "serverInfo": {"name": "rea-hermetic", "version": "6.4.0"}}
    elif method == "tools/list":
        result = {"tools": tools if mode != "missing-tool" else tools[:1]}
    elif method == "tools/call":
        params = message["params"]
        value = {"result": {"server_identity": {"package": {"name": "rea-agents", "version": "6.4.0"}, "server": {"name": "rea-hermetic", "version": "6.4.0"}}, "open": False}}
        if params["name"] == "analyze_javascript_application":
            value = {"evidence_id": "hermetic-evidence", "operation": params["name"], "provenance": {"authority": "local-file", "confidence": "observed"}, "limitations": ["Static inference only"], "data": {"input_path": params["arguments"]["input_path"], "modules": [{"id": "index.js", "unknown": True}]}}
        if mode in ("tool-error", "structured-error"):
            value = {"error": {"code": "TEST_FAILURE", "message": "hermetic failure"}}
        if mode == "empty-error":
            value = {"error": {}}
        if mode == "failed-status":
            value = {"status": "failed"}
        if mode == "malformed-evidence":
            value = {"message": "no Evidence delivered"}
        if mode == "empty-session":
            value = {}
        if mode == "missing-session-result":
            value = {"message": "no session delivered"}
        if mode == "null-session-result":
            value = {"result": None}
        if mode == "missing-session-identity":
            value = {"result": {"open": False}}
        if mode == "null-session-identity":
            value = {"result": {"server_identity": None}}
        if mode == "empty-session-identity":
            value = {"result": {"server_identity": {}}}
        if mode == "invalid-session-version":
            value["result"]["server_identity"]["package"]["version"] = False
        if mode == "missing-session-server":
            value["result"]["server_identity"].pop("server")
        if mode == "nested-session-error":
            value["result"]["error"] = {"code": "TEST_SESSION_FAILURE"}
        if mode == "empty":
            result = {"content": [], "isError": False}
        else:
            result = {"content": [{"type": "text", "text": json.dumps(value)}], "structuredContent": value, "isError": mode == "tool-error"}
    else:
        result = {}
    if mode == "protocol-error" and method == "tools/list":
        reply = {"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32000, "message": "hermetic protocol failure"}}
    else:
        reply = {"jsonrpc": "2.0", "id": message["id"], "result": result}
    print(json.dumps(reply), flush=True)
'''


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    source = tmp_path / "rea runtime"
    (source / "scripts").mkdir(parents=True)
    (source / "dist").mkdir()
    (source / "node_modules").mkdir()
    (source / "package.json").write_text(json.dumps({"name": "rea-agents", "version": "6.4.0"}))
    (source / "scripts" / "rea.mjs").write_text(FAKE_SERVER)
    (source / "dist" / "main.js").write_text("// Hermetic runtime marker")
    (source / "mode").write_text("success")
    monkeypatch.setenv("REA_SOURCE_DIR", str(source))
    monkeypatch.setenv("REA_NODE_BIN", sys.executable)
    return source


def requests(runtime):
    return [json.loads(line) for line in (runtime / "requests.jsonl").read_text().splitlines()]


def test_status_reads_installation_without_starting_mcp_or_target(runtime, tmp_path):
    result = ReaBridge(tmp_path).status()
    assert result["status"] == "completed" and result["success"]
    assert result["verification"] == "installation_only"
    assert result["provenance"]["repository"] == "https://github.com/MarceloClaro/rea"
    assert result["provenance"]["version"] == "6.4.0"
    assert result["provenance"]["runtime"]["source_dir"] == str(runtime)
    assert not (runtime / "pid").exists()


def test_absent_runtime_is_unavailable_without_starting_process(monkeypatch, tmp_path):
    monkeypatch.setenv("REA_SOURCE_DIR", str(tmp_path / "absent"))
    result = ReaBridge(tmp_path).action({"operation": "session"})
    assert result["status"] == "unavailable" and result["success"] is False
    assert result["response"] is None


@pytest.mark.parametrize("config", [
    None, [], "session", {}, {"operation": "run_binary"}, {"operation": True},
    {"operation": "session", "command": "echo fail"},
    {"operation": "session", "path": "x"},
    {"operation": "analyze"}, {"operation": "analyze", "path": False},
    {"operation": "analyze", "path": " "},
    {"operation": "session", "timeout_seconds": True},
    {"operation": "session", "timeout_seconds": "60"},
    {"operation": "session", "timeout_seconds": float("inf")},
    {"operation": "session", "timeout_seconds": float("nan")},
    {"operation": "session", "timeout_seconds": 0},
    {"operation": "session", "timeout_seconds": -1},
    {"operation": "session", "timeout_seconds": 181},
    {"operation": "session", "timeout_seconds": 10**1000},
])
def test_invalid_configuration_rejected_before_transport(runtime, tmp_path, config):
    with pytest.raises(ValueError):
        ReaBridge(tmp_path).action(config)
    assert not (runtime / "pid").exists()


def test_analysis_requires_existing_local_path(runtime, tmp_path):
    with pytest.raises(ValueError):
        ReaBridge(tmp_path).action({"operation": "analyze", "path": "missing"})
    assert not (runtime / "pid").exists()


def test_catalog_comes_from_handshake_and_preserves_schema_once(runtime, tmp_path):
    result = ReaBridge(tmp_path).action({"operation": "catalog"})
    assert result["status"] == "completed" and result["success"]
    tools = result["response"]["tools"]
    assert result["tool_count"] == 3
    assert tools[1]["name"] == "analyze_javascript_application"
    assert tools[1]["inputSchema"]["required"] == ["input_path"]
    assert tools[1]["outputSchema"] == {"type": "object"}
    assert "tools" not in result
    assert [row["method"] for row in requests(runtime)] == ["initialize", "notifications/initialized", "tools/list"]


def test_session_calls_only_target_free_tool(runtime, tmp_path):
    result = ReaBridge(tmp_path).action({"operation": "session"})
    assert result["success"] and result["verification"] == "mcp_execution"
    calls = [row for row in requests(runtime) if row["method"] == "tools/call"]
    assert calls[0]["params"] == {"name": "binary_session", "arguments": {}}
    assert result["response"]["structuredContent"]["result"]["open"] is False


@pytest.mark.parametrize("mode", [
    "empty-session", "missing-session-result", "null-session-result",
    "missing-session-identity", "null-session-identity", "empty-session-identity",
    "invalid-session-version", "missing-session-server", "nested-session-error",
])
def test_malformed_session_never_claims_identity_or_success(runtime, tmp_path, mode):
    (runtime / "mode").write_text(mode)
    result = ReaBridge(tmp_path).action({"operation": "session"})
    assert result["status"] == "failed" and result["success"] is False
    assert result["error"] and result["error_code"] == "tool_failure"
    assert result["response"] is not None
    payload = json.dumps(result["response"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert result["provenance"]["response_sha256"] == hashlib.sha256(payload).hexdigest()


def test_analysis_preserves_evidence_and_does_not_execute_target(runtime, tmp_path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "index.js").write_text("throw new Error('never execute');")
    result = ReaBridge(tmp_path).action({"operation": "analyze", "path": "app", "timeout_seconds": 5})
    assert result["success"] and result["status"] == "completed"
    evidence = result["response"]["structuredContent"]
    assert evidence["evidence_id"] == "hermetic-evidence"
    assert evidence["limitations"] == ["Static inference only"]
    assert evidence["provenance"]["confidence"] == "observed"
    assert evidence["data"]["modules"] == [{"id": "index.js", "unknown": True}]
    calls = [row for row in requests(runtime) if row["method"] == "tools/call"]
    assert calls[0]["params"]["name"] == "analyze_javascript_application"
    assert calls[0]["params"]["arguments"]["input_path"] == str(target)
    assert calls[0]["params"]["arguments"]["detail"] == "complete"
    encoded = json.dumps(result["response"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert result["provenance"]["response_sha256"] == hashlib.sha256(encoded).hexdigest()


@pytest.mark.parametrize("mode", ["tool-error", "structured-error", "empty", "protocol-error", "missing-tool", "empty-error", "failed-status", "malformed-evidence"])
def test_errors_never_promoted_to_completed(runtime, tmp_path, mode):
    (runtime / "mode").write_text(mode)
    target = tmp_path / "app.js"
    target.write_text("export const value = 1;")
    result = ReaBridge(tmp_path).action({"operation": "analyze", "path": str(target)})
    assert result["status"] == "failed" and result["success"] is False
    assert result["error"]
    if mode in ("tool-error", "structured-error"):
        assert result["response"]["structuredContent"]["error"]["code"] == "TEST_FAILURE"
        assert result["provenance"]["response_sha256"]


@pytest.mark.skipif(os.name == "nt", reason="Process group cleanup is exercised in WSL/POSIX")
def test_timeout_terminates_real_process_tree(runtime, tmp_path):
    (runtime / "mode").write_text("stall")
    started = time.monotonic()
    result = ReaBridge(tmp_path).action({"operation": "session", "timeout_seconds": 0.2})
    assert result["status"] == "failed" and result["success"] is False
    assert result["error_code"] == "timeout"
    assert time.monotonic() - started < 12
    for name in ("pid", "child_pid"):
        pid = int((runtime / name).read_text())
        stat = Path(f"/proc/{pid}/stat")
        assert not stat.exists() or stat.read_text().split()[2] == "Z"


def test_mcp_entrypoint_replaces_process_with_runtime(runtime, monkeypatch):
    import integrations.rea_bridge as bridge_module
    recorded = {}
    monkeypatch.setattr(bridge_module.os, "execve", lambda executable, args, environment: recorded.update(executable=executable, args=args, environment=environment))
    assert bridge_module.main(["mcp"]) == 0
    assert recorded["executable"] == str(Path(sys.executable).resolve())
    assert recorded["args"] == [str(Path(sys.executable).resolve()), str(runtime / "scripts" / "rea.mjs"), "mcp"]
    assert recorded["environment"]["REA_SOURCE_DIR"] == str(runtime)


def test_sync_action_works_when_gateway_event_loop_is_running(runtime, tmp_path):
    import asyncio

    async def gateway():
        return ReaBridge(tmp_path).action({"operation": "session"})

    assert asyncio.run(gateway())["success"]


def test_gateway_thread_with_inherited_anyio_context_runs_transport(runtime, tmp_path):
    import anyio
    import asyncio

    async def gateway():
        return await asyncio.to_thread(ReaBridge(tmp_path).action, {"operation": "session"})

    result = anyio.run(gateway)
    assert result["success"], result["error"]
    assert result["response"]["structuredContent"]["result"]["open"] is False
