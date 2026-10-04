# -*- coding: utf-8 -*-
"""Testes da cobertura Awesome MCP Servers (SPEC-935-R652) — sem rede."""

import sys

sys.path.insert(0, ".")

from integrations.opencode_cli import build_config  # noqa: E402


def test_mcp_referencia_presentes():
    mcp = build_config()["mcp"]
    assert mcp["fetch"]["command"] == ["uvx", "mcp-server-fetch"]
    assert mcp["sequential-thinking"]["command"] == [
        "npx", "-y", "@modelcontextprotocol/server-sequential-thinking"]
    fs_cmd = mcp["filesystem"]["command"]
    assert fs_cmd[:2] == ["npx", "-y"]
    assert "server-filesystem" in fs_cmd[2]
    assert len(fs_cmd) == 4  # bin + pacote + escopo


def test_mcp_todos_habilitados():
    mcp = build_config()["mcp"]
    for name in ("fetch", "sequential-thinking", "filesystem"):
        assert mcp[name]["enabled"] is True
        assert mcp[name]["type"] == "local"
