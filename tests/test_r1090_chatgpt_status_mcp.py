"""R1090: superfície mínima local; não atesta conexão no ChatGPT Chat."""
import asyncio
import importlib
import importlib.util
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def load_surface():
    name = "integrations.chatgpt_status_mcp"
    assert importlib.util.find_spec(name) is not None, "Fachada MCP de status ausente"
    return importlib.import_module(name)


def test_only_status_is_published_with_read_only_contract():
    server = load_surface().create_server()
    tools = asyncio.run(server.list_tools())
    assert [tool.name for tool in tools] == ["ecosystem_integration_status"]
    tool = tools[0]
    assert tool.inputSchema.get("properties", {}) == {}
    assert not tool.inputSchema.get("required")
    assert tool.annotations.readOnlyHint is True
    assert tool.annotations.destructiveHint is False
    assert tool.annotations.idempotentHint is True
    assert tool.annotations.openWorldHint is False
    assert asyncio.run(server.list_resources()) == []
    assert asyncio.run(server.list_resource_templates()) == []
    assert asyncio.run(server.list_prompts()) == []


def test_facade_does_not_remove_full_core_tools():
    surface = load_surface()
    from integrations.ecosystem_mcp import mcp as core

    before = {tool.name for tool in asyncio.run(core.list_tools())}
    server = surface.create_server()
    after = {tool.name for tool in asyncio.run(core.list_tools())}
    assert server is not core
    assert before == after
    assert {"ecosystem_run", "ecosystem_workflow", "ecosystem_agent_profile"} <= after


def test_fresh_process_rejects_execution_and_returns_real_status():
    load_surface()
    root = Path(__file__).resolve().parents[1]

    async def exchange():
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "integrations.chatgpt_status_mcp"],
            cwd=str(root),
        )
        async with asyncio.timeout(90):
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    assert initialized.serverInfo.name == "opencode-core-status"
                    tools = await session.list_tools()
                    assert [tool.name for tool in tools.tools] == ["ecosystem_integration_status"]
                    rejected = await session.call_tool("ecosystem_run", {})
                    assert rejected.isError is True
                    called = await session.call_tool("ecosystem_integration_status", {})
                    assert called.isError is False
                    report = called.structuredContent
                    if not report:
                        report = json.loads(called.content[0].text)
                    assert report["spec_id"] == "SPEC-935-R662"
                    assert report["orchestrator"] == "marceloclaro"
                    assert report["executed"] is False
                    assert report["execution_verified"] is False
                    assert report["readiness"]["state"] == "CONFIG_ONLY"
                    assert report["readiness"]["checked"] == ["configuration", "inventory"]
                    assert "tool_discovery" in report["readiness"]["not_probed"]
                    assert report["readiness"]["external_clients"] == "not_observable"
                    assert set(report["components"]) == {
                        "agents", "hooks", "mcp", "cli", "plugins", "skills"
                    }
                    assert isinstance(report["issues"], list)

    asyncio.run(exchange())
