"""R1020 — Qdrant MCP em modo HTTP, sem lock local compartilhado."""

from __future__ import annotations

from pathlib import Path

from integrations.federation_sync import runtime


def test_qdrant_spec_uses_http_url() -> None:
    spec = runtime.server_specs(Path.cwd())["qdrant"]
    assert spec.env.get("QDRANT_URL") == "http://127.0.0.1:6333"
    assert "QDRANT_LOCAL_PATH" not in spec.env


def test_qdrant_entry_exposes_http_url() -> None:
    spec = runtime.server_specs(Path.cwd())["qdrant"]
    environment = runtime._entry(spec)["environment"]
    assert environment.get("QDRANT_URL") == "http://127.0.0.1:6333"
    assert "QDRANT_LOCAL_PATH" not in environment


def test_qdrant_server_command_remains_stdio() -> None:
    spec = runtime.server_specs(Path.cwd())["qdrant"]
    assert spec.command[-2:] == ("--transport", "stdio")
    assert "mcp-server-qdrant" in spec.command[0]
