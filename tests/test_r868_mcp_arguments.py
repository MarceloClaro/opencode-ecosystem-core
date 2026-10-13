"""Validação MCP estrita antes de qualquer análise; primário é fixture controlada."""
import asyncio

import pytest
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import ValidationError


def server_fixture(monkeypatch):
    from integrations.rea_assistant_mcp import create_mcp_server
    from marceloclaro import orchestrator
    calls = []
    class Primary:
        def __init__(self, **kwargs):
            pass
        def rea_assistant_action(self, config):
            calls.append(config)
            return {"success": True, "operation": "inspect"}
    monkeypatch.setattr(orchestrator, "MarceloClaroOrchestrator", Primary)
    return create_mcp_server(), calls


def test_empty_optional_arguments_use_declared_defaults(monkeypatch):
    server, calls = server_fixture(monkeypatch)
    failure_type = None
    try:
        asyncio.run(server.call_tool("core_rea_inspect", {"path": "fixture.html", "kind": "",
            "timeout_seconds": "", "procedure": ""}))
    except Exception as error:
        failure_type = type(error).__name__
    assert failure_type is None, f"SDK recusou defaults opcionais: {failure_type}"
    assert calls == [{"operation": "inspect", "path": "fixture.html", "kind": "auto",
                      "timeout_seconds": 60, "procedure": "main"}]


@pytest.mark.parametrize("value", [True, False, "30", None, float("nan"), -1, 181])
def test_invalid_timeout_never_reaches_primary(monkeypatch, value):
    server, calls = server_fixture(monkeypatch)
    rejected = None
    try:
        asyncio.run(server.call_tool("core_rea_inspect", {"path": "fixture.html", "timeout_seconds": value}))
    except ToolError as error:
        rejected = error
    assert isinstance(rejected, ToolError)
    assert isinstance(rejected.__cause__, ValidationError)
    assert calls == []


def test_numeric_timeout_is_preserved(monkeypatch):
    server, calls = server_fixture(monkeypatch)
    asyncio.run(server.call_tool("core_rea_inspect", {"path": "fixture.html", "timeout_seconds": 30}))
    assert calls[0]["timeout_seconds"] == 30
