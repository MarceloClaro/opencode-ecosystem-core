"""R1088: regressões offline de recuperação; sem inferência nem downloads."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from integrations import opencode_cli
from integrations.colibri import colibri_mcp_server as colibri


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    path = tmp_path / "opencode.json"
    monkeypatch.setattr(opencode_cli, "CONFIG_PATH", str(path))
    monkeypatch.setattr(opencode_cli, "_federation_activated_mcp", lambda: {})
    return path


def test_colibri_config_uses_versioned_module(config_file):
    command = opencode_cli.build_config()["mcp"]["colibri-mcp"]["command"]
    assert command[1:] == ["-m", "integrations.colibri.colibri_mcp_server"]


def test_reference_node_prefers_installed_pinned_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(opencode_cli, "ROOT", str(tmp_path))
    path = tmp_path / ".opencode/mcp/reference-node/node_modules/.bin/latexmk-mcp"
    path.parent.mkdir(parents=True)
    path.write_text("#!/bin/sh\nexit 0\n")
    path.chmod(0o755)
    fallback = ["npx", "-y", "latexmk-mcp"]
    assert opencode_cli._reference_node_command("latexmk-mcp", fallback) == [str(path)]
    path.chmod(0o644)
    assert opencode_cli._reference_node_command("latexmk-mcp", fallback) == fallback


@pytest.mark.parametrize("nested", [False, True])
def test_stale_federated_config_cannot_bypass_gate(config_file, nested):
    entries = {
        "mcp-time": {"type": "local", "command": ["/absent/mcp-server-time"], "enabled": True},
        "operator-custom": {"type": "local", "command": ["/operator/server"], "enabled": False},
    }
    section = {"servers": entries, "timeout": {"startup": 45000}} if nested else entries
    config_file.write_text(json.dumps({"mcp": section}))
    result = opencode_cli.build_config()["mcp"]
    actual = result.get("servers", {}) if nested else result
    assert "mcp-time" not in actual
    assert actual["operator-custom"] == entries["operator-custom"]
    if nested:
        assert result["timeout"] == {"startup": 45000}


def test_validated_federation_replaces_stale_entry(config_file, monkeypatch):
    stale = {"type": "local", "command": ["/old/mcp-server-time"]}
    valid = {"type": "local", "command": ["/validated/mcp-server-time"], "enabled": True}
    config_file.write_text(json.dumps({"mcp": {"mcp-time": stale}}))
    monkeypatch.setattr(opencode_cli, "_federation_activated_mcp", lambda: {"mcp-time": valid})
    assert opencode_cli.build_config()["mcp"]["mcp-time"] == valid


def test_colibri_lists_tools_without_instantiating_backend(monkeypatch):
    def forbidden():
        raise AssertionError("catalog must not start a backend")
    monkeypatch.setattr(colibri, "ColibriBridge", forbidden)
    response = colibri.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = response["result"]["tools"]
    assert len(tools) == 6
    assert "colibri:status" in {tool["name"] for tool in tools}
    assert all(tool["inputSchema"]["type"] == "object" for tool in tools)


def test_colibri_initialize_advertises_capabilities_not_tool_definitions():
    response = colibri.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                       "params": {"protocolVersion": "2024-11-05"}})
    assert response["result"]["capabilities"] == {"tools": {}}
    assert response["result"]["protocolVersion"] == "2024-11-05"


def test_colibri_notifications_never_receive_response():
    assert colibri.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


@pytest.mark.parametrize("message,code", [
    ([], -32600),
    ({"jsonrpc": "1.0", "id": 5, "method": "ping"}, -32600),
    ({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": []}, -32602),
    ({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
      "params": {"name": "colibri:status", "arguments": []}}, -32602),
])
def test_colibri_invalid_requests_are_protocol_errors(message, code):
    response = colibri.handle_request(message)
    assert response["error"]["code"] == code


def test_colibri_ping():
    assert colibri.handle_request({"jsonrpc": "2.0", "id": 9, "method": "ping"}) == {
        "jsonrpc": "2.0", "id": 9, "result": {}}


def test_colibri_status_is_available_without_models():
    response = colibri.handle_request({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                       "params": {"name": "colibri:status", "arguments": {}}})
    payload = json.loads(response["result"]["content"][0]["text"])
    assert isinstance(payload["models"], list)
    assert "available" in payload["olmoe"]


def test_colibri_stdio_smoke_protocol():
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "colibri:status", "arguments": {}}},
    ]
    result = subprocess.run(
        [sys.executable, "-m", "integrations.colibri.colibri_mcp_server"],
        input="".join(json.dumps(row) + "\n" for row in messages), text=True,
        capture_output=True, timeout=20, cwd=Path(__file__).resolve().parents[1],
    )
    assert result.returncode == 0, result.stderr
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["id"] for row in responses] == [1, 2, 3]
    assert all("error" not in row for row in responses)


def test_editor_rejects_missing_root(tmp_path):
    from integrations.video_editor_mcp import create_server
    with pytest.raises(ValueError, match="existing directory"):
        create_server(tmp_path / "missing")


def test_editor_accepts_explicit_existing_root(tmp_path):
    from integrations.video_editor_mcp import create_server
    assert create_server(tmp_path) is not None
