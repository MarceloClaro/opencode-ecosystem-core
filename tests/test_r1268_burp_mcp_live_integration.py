"""SPEC-935-R1268 — contrato de segurança da configuração Burp MCP."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://127.0.0.1:9876/mcp"
DENY_BURP_TOOLS = {
    "action": "burp_*",
    "resource": "*",
    "effect": "deny",
}


def _project_config() -> dict:
    return json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))


def test_burp_server_uses_exact_loopback_streamable_http_endpoint():
    config = _project_config()
    server = config.get("mcp", {}).get("servers", {}).get("burp")
    assert server is not None, "servidor remoto burp ainda não configurado"
    assert server.get("type") == "remote"
    assert server.get("url") == ENDPOINT
    assert server.get("protocol") == "legacy"
    assert server.get("disabled", False) is False


def test_burp_tool_calls_are_denied_in_project_permissions():
    permissions = _project_config().get("permissions", [])
    assert DENY_BURP_TOOLS in permissions
    assert not any(
        rule.get("action") == "burp_*" and rule.get("effect") == "allow"
        for rule in permissions
        if isinstance(rule, dict)
    )


def test_config_generator_preserves_burp_server_and_deny_rule(tmp_path, monkeypatch):
    import integrations.opencode_cli as opencode_cli

    server = {
        "type": "remote",
        "url": ENDPOINT,
        "protocol": "legacy",
        "disabled": False,
    }
    isolated_config = tmp_path / "opencode.json"
    isolated_config.write_text(
        json.dumps(
            {
                "$schema": "https://opencode.ai/config.json",
                "mcp": {"servers": {"burp": server}},
                "permissions": [DENY_BURP_TOOLS],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(opencode_cli, "CONFIG_PATH", str(isolated_config))

    generated = opencode_cli.build_config()

    assert generated["mcp"]["servers"]["burp"] == server
    assert DENY_BURP_TOOLS in generated.get("permissions", [])
