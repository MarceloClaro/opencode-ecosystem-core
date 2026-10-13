"""SPEC-935-R841: camadas de provedor REA; transporte MCP hermético, sem alvo real."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest

from integrations import rea_layers
from integrations.rea_bridge import ReaBridge


FAKE_SERVER = r'''
import json, os, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
mode = (root / "mode").read_text().strip()
tools = [
    {"name": "binary_session", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "analyze_javascript_application", "inputSchema": {"type": "object", "required": ["input_path"],
        "properties": {"input_path": {"type": "string"}, "detail": {"type": "string"},
                       "format": {"type": "string"}, "integrity_policy": {"type": "string"}}}},
    {"name": "inspect_binary_layout", "inputSchema": {"type": "object", "required": ["path"],
        "properties": {"path": {"type": "string"}}}},
    {"name": "inspect_evm_interface", "inputSchema": {"type": "object", "required": ["path", "encoding"],
        "properties": {"path": {"type": "string"}, "encoding": {"enum": ["raw", "hex"]}}}},
    {"name": "decode_android_resources", "inputSchema": {"type": "object", "required": ["path"],
        "properties": {"path": {"type": "string"}}}},
]
for line in sys.stdin:
    message = json.loads(line)
    with (root / "requests.jsonl").open("a") as log:
        log.write(json.dumps(message) + "\n")
    method = message.get("method")
    if "id" not in message:
        continue
    if method == "initialize":
        result = {"protocolVersion": message["params"]["protocolVersion"], "capabilities": {"tools": {}},
                  "serverInfo": {"name": "rea-hermetic", "version": "6.4.0"}}
    elif method == "tools/list":
        result = {"tools": tools if mode != "missing-tool" else tools[:1]}
    elif method == "tools/call":
        name = message["params"]["name"]
        arguments = message["params"]["arguments"]
        if mode == "structured-error":
            value = {"error": {"code": "LAYER_FAILURE", "message": "hermetic"}}
        elif mode == "empty-evidence":
            value = {}
        elif mode == "invalid-evidence-id":
            value = {"evidence_id": ""}
        else:
            value = {"evidence_id": "hermetic-layer", "operation": name,
                     "limitations": ["Static inference only"], "data": {"arguments": arguments}}
        result = {"content": [{"type": "text", "text": json.dumps(value)}],
                  "structuredContent": value, "isError": mode == "tool-error"}
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}), flush=True)
'''


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    source = tmp_path / "rea runtime"
    (source / "scripts").mkdir(parents=True)
    (source / "dist").mkdir()
    (source / "node_modules").mkdir()
    (source / "package.json").write_text(json.dumps({"name": "rea-agents", "version": "6.4.0"}))
    (source / "scripts" / "rea.mjs").write_text(FAKE_SERVER)
    (source / "dist" / "main.js").write_text("// marker")
    (source / "mode").write_text("success")
    monkeypatch.setenv("REA_SOURCE_DIR", str(source))
    monkeypatch.setenv("REA_NODE_BIN", sys.executable)
    return source


def requests(runtime):
    return [json.loads(line) for line in (runtime / "requests.jsonl").read_text().splitlines()]


# --- registro -----------------------------------------------------------------

def test_registry_ids_unique_and_inspection_tools_belong_to_layer():
    ids = [layer["id"] for layer in rea_layers.LAYERS]
    assert len(ids) == len(set(ids))
    for layer in rea_layers.LAYERS:
        inspection = layer.get("inspection")
        if inspection:
            assert inspection["tool"] in layer["tools"]
            assert inspection["path_field"]
    assert {"javascript", "firmware", "evm", "android_jadx", "artifact"} <= set(ids)


def test_inspection_only_for_layers_that_declare_it():
    assert rea_layers.layer_inspection("evm")["tool"] == "inspect_evm_interface"
    assert rea_layers.layer_inspection("native_ghidra") is None
    assert rea_layers.layer_inspection("unknown") is None


def test_declared_tools_match_recorded_catalog_when_available():
    surfaces = _catalog_surfaces()
    if not surfaces:
        pytest.skip("catálogo MCP real não preservado localmente")
    for layer in rea_layers.LAYERS:
        declared = rea_layers.layer_surfaces(layer["id"])
        assert declared, layer["id"]
        allowed = set().union(*(surfaces.get(name, set()) for name in declared))
        unexpected = sorted(set(layer["tools"]) - allowed)
        assert not unexpected, (layer["id"], unexpected)
        inspection = layer.get("inspection")
        if inspection:
            assert any(inspection["tool"] in surfaces.get(name, set()) for name in declared), layer["id"]


def _catalog_surfaces():
    evidence = Path(__file__).resolve().parents[1] / ".opencode/rea/evidence"
    files = sorted(evidence.glob("*.json")) if evidence.is_dir() else []
    for path in files:
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        found = _find_tools(data)
        if not found:
            continue
        grouping = {}
        for tool in found:
            grouping.setdefault(tool.get("surface"), set()).add(tool["name"])
        if len(grouping) > 1:
            return grouping
    return {}


def _find_tools(value):
    if isinstance(value, dict):
        tools = value.get("tools")
        if isinstance(tools, list) and tools and isinstance(tools[0], dict) and "name" in tools[0]:
            return tools
        for child in value.values():
            found = _find_tools(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_tools(child)
            if found:
                return found
    return None


# --- sonda de prontidão -------------------------------------------------------

def test_layers_status_is_local_and_independent_of_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("REA_SOURCE_DIR", str(tmp_path / "absent"))
    result = ReaBridge(tmp_path).action({"operation": "layers"})
    assert result["status"] == "completed" and result["success"] is True
    assert result["verification"] == "local_readiness_probe"
    assert result["summary"]["total"] == len(rea_layers.LAYERS)
    assert result["response_sha256"] if "response_sha256" in result else True


def test_bundled_ready_and_engine_pending_until_configured(monkeypatch, tmp_path):
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    for name in ("REA_IDA_MCP_CONFIG", "HOPPER_LAUNCHER_PATH",
                 "REA_JEB_MCP_URL", "REA_ADB_PATH"):
        monkeypatch.delenv(name, raising=False)
    assert rea_layers.probe_layer("javascript")["ready"] is True
    pending = rea_layers.probe_layer("native_ida")
    assert pending["ready"] is False and "REA_IDA_MCP_CONFIG" in pending["reason"]
    config = tmp_path / "ida.json"
    config.write_text("{}")  # fail-closed: registro vazio não é configuração válida (R843)
    monkeypatch.setenv("REA_IDA_MCP_CONFIG", str(config))
    assert rea_layers.probe_layer("native_ida")["ready"] is False
    config.write_text(json.dumps({"command": "python", "args": ["server.py"]}))
    ready = rea_layers.probe_layer("native_ida")
    assert ready["ready"] is True and ready["env"][0]["ok"] is True
    tool = tmp_path / "engine"
    tool.write_text("#!/bin/sh\nexit 0\n")
    tool.chmod(0o755)
    monkeypatch.setenv("REA_ADB_PATH", str(tool))
    assert rea_layers.probe_layer("android_adb")["ready"] is True


def test_child_environment_exports_only_existing_engines(monkeypatch, tmp_path):
    monkeypatch.setattr(rea_layers, "NATIVE_ROOT", tmp_path)
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    monkeypatch.delenv("REA_UNBLOB_COMMAND", raising=False)
    monkeypatch.delenv("REA_BINWALK_COMMAND", raising=False)
    assert ReaBridge._child_environment().get("REA_UNBLOB_COMMAND") is None
    (tmp_path / "bin").mkdir()
    wrapper = tmp_path / "bin" / "unblob"
    wrapper.write_text("#!/bin/sh\nexit 0\n")
    wrapper.chmod(0o755)
    environment = ReaBridge._child_environment()
    assert environment["REA_UNBLOB_COMMAND"] == str(wrapper)
    assert "REA_BINWALK_COMMAND" not in environment
    monkeypatch.setenv("REA_UNBLOB_COMMAND", "/operator/unblob")
    assert ReaBridge._child_environment()["REA_UNBLOB_COMMAND"] == "/operator/unblob"


# --- validação ----------------------------------------------------------------

def test_validate_layer_configuration(tmp_path):
    target = tmp_path / "artifact.bin"
    target.write_bytes(b"\x7fELF")
    bridge = ReaBridge(tmp_path)
    assert bridge._validate({"operation": "layers"}) == {"operation": "layers", "timeout_seconds": 60.0}
    validated = bridge._validate({"operation": "layer", "layer": "native_offline_elf", "path": str(target)})
    assert validated["tool"] == "inspect_binary_layout" and validated["path_field"] == "path"
    evm = bridge._validate({"operation": "layer", "layer": "evm", "path": str(target), "encoding": "hex"})
    assert evm["encoding"] == "hex"
    assert bridge._validate({"operation": "layer", "layer": "evm", "path": str(target)})["encoding"] == "raw"


@pytest.mark.parametrize("config", [
    {"operation": "layer", "layer": "unknown", "path": "x"},
    {"operation": "layer", "layer": "native_ghidra", "path": "x"},
    {"operation": "layer", "layer": "evm"},
    {"operation": "layer", "layer": "evm", "path": "missing"},
    {"operation": "layer", "layer": "evm", "path": "x", "extra": 1},
    {"operation": "layer", "layer": "native_offline_elf", "path": "x", "encoding": "hex"},
    {"operation": "layer", "layer": "evm", "path": "x", "encoding": "base64"},
    {"operation": "layers", "path": "x"},
    {"operation": "layers", "layer": "evm"},
    {"operation": "session", "layer": "evm"},
    {"operation": "analyze", "path": "x", "encoding": "raw"},
])
def test_invalid_layer_configuration_rejected(tmp_path, config):
    with pytest.raises(ValueError):
        ReaBridge(tmp_path)._validate(config)


def test_layer_rejects_non_inspectable_before_transport(runtime, tmp_path):
    with pytest.raises(ValueError):
        ReaBridge(tmp_path).action({"operation": "layer", "layer": "native_ghidra", "path": str(runtime)})
    assert not (runtime / "pid").exists()
    assert not (runtime / "requests.jsonl").exists()


# --- despacho -----------------------------------------------------------------

def test_layer_dispatch_calls_declared_tool_and_preserves_evidence(runtime, tmp_path):
    target = tmp_path / "payload.bin"
    target.write_bytes(b"\x7fELF payload")
    result = ReaBridge(tmp_path).action(
        {"operation": "layer", "layer": "native_offline_elf", "path": str(target), "timeout_seconds": 5})
    assert result["status"] == "completed" and result["success"] is True
    assert result["provenance"]["layer"] == "native_offline_elf"
    assert result["provenance"]["layer_tool"] == "inspect_binary_layout"
    assert result["provenance"]["response_sha256"]
    calls = [row for row in requests(runtime) if row["method"] == "tools/call"]
    assert calls[0]["params"]["name"] == "inspect_binary_layout"
    assert set(calls[0]["params"]["arguments"]) == {"path"}
    assert Path(calls[0]["params"]["arguments"]["path"]).resolve() == target.resolve()
    evidence = result["response"]["structuredContent"]
    assert evidence["evidence_id"] == "hermetic-layer"
    assert Path(evidence["data"]["arguments"]["path"]).resolve() == target.resolve()


def test_layer_evm_passes_encoding(runtime, tmp_path):
    target = tmp_path / "runtime.hex"
    target.write_text("0x6080")
    result = ReaBridge(tmp_path).action(
        {"operation": "layer", "layer": "evm", "path": str(target), "encoding": "hex"})
    assert result["success"] and result["provenance"]["layer_tool"] == "inspect_evm_interface"
    call = [row for row in requests(runtime) if row["method"] == "tools/call"][0]
    assert call["params"]["arguments"]["encoding"] == "hex"
    assert Path(call["params"]["arguments"]["path"]).resolve() == target.resolve()


@pytest.mark.parametrize("mode", ["tool-error", "structured-error", "empty-evidence", "invalid-evidence-id"])
def test_layer_errors_never_promoted(runtime, tmp_path, mode):
    (runtime / "mode").write_text(mode)
    target = tmp_path / "payload.bin"
    target.write_bytes(b"\x7fELF")
    result = ReaBridge(tmp_path).action(
        {"operation": "layer", "layer": "native_offline_elf", "path": str(target)})
    assert result["status"] == "failed" and result["success"] is False
    assert result["error"] and result["response"] is not None
    assert result["provenance"]["response_sha256"]


def test_layer_missing_tool_in_handshake_fails_without_success(runtime, tmp_path):
    (runtime / "mode").write_text("missing-tool")
    target = tmp_path / "payload.bin"
    target.write_bytes(b"\x7fELF")
    result = ReaBridge(tmp_path).action(
        {"operation": "layer", "layer": "native_offline_elf", "path": str(target)})
    assert result["status"] == "failed" and result["success"] is False
    assert result["error_code"] in {"tool_failure", "mcp_failure"}


# --- gateway e CLI ------------------------------------------------------------

def test_compact_layers_is_bounded(tmp_path):
    from marceloclaro.rea_reports import compact_rea_report
    raw = ReaBridge(tmp_path).action({"operation": "layers"})
    compact = compact_rea_report(raw, tmp_path)
    assert compact["summary"]["total"] == len(rea_layers.LAYERS)
    assert all(set(row["env"][0]) == {"name", "ok", "source", "resolved", "reason"}
               for row in compact["layers"] if row["env"])
    assert len(json.dumps(compact)) < 12_000


def test_cli_builds_layer_configuration(monkeypatch, capsys):
    from marceloclaro import cli
    calls = []

    class Primary:
        def __init__(self, **kwargs):
            assert kwargs == {"auto_load_agents": False}

        def rea_action(self, config):
            calls.append(config)
            return {"status": "completed", "success": True}

    monkeypatch.setattr(cli, "MarceloClaroOrchestrator", Primary)
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "rea", "layers"])
    assert cli.main() == 0
    monkeypatch.setattr(cli.sys, "argv",
                        ["marceloclaro", "rea", "layer", "--layer", "evm", "--encoding", "hex", "/tmp/x.hex"])
    assert cli.main() == 0
    assert calls == [{"operation": "layers", "timeout_seconds": 60.0},
                     {"operation": "layer", "timeout_seconds": 60.0, "path": "/tmp/x.hex",
                      "layer": "evm", "encoding": "hex"}]


def test_cli_rejects_layer_without_path(monkeypatch):
    from marceloclaro import cli
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "rea", "layer", "--layer", "evm"])
    assert cli.main() == 2
