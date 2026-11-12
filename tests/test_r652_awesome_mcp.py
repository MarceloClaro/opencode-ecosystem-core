# -*- coding: utf-8 -*-
"""Testes da cobertura Awesome MCP Servers (SPEC-935-R652) — sem rede."""

import sys
from pathlib import Path

sys.path.insert(0, ".")

from integrations.opencode_cli import build_config, _mcp_launcher  # noqa: E402


def test_mcp_referencia_presentes():
    mcp = build_config()["mcp"]
    assert mcp["fetch"]["command"] == [_mcp_launcher("uvx"), "mcp-server-fetch"]
    seq_cmd = mcp["sequential-thinking"]["command"]
    assert seq_cmd == ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"] or (
        len(seq_cmd) == 1 and Path(seq_cmd[0]).name == "mcp-server-sequential-thinking"
    )
    fs_cmd = mcp["filesystem"]["command"]
    assert fs_cmd[:-1] == ["npx", "-y", "@modelcontextprotocol/server-filesystem"] or (
        len(fs_cmd) == 2 and Path(fs_cmd[0]).name == "mcp-server-filesystem"
    )
    assert Path(fs_cmd[-1]).resolve() == Path(__file__).resolve().parents[1]


def test_mcp_todos_habilitados():
    mcp = build_config()["mcp"]
    for name in ("fetch", "sequential-thinking", "filesystem"):
        assert mcp[name]["enabled"] is True
        assert mcp[name]["type"] == "local"
