"""Contrato da rede exposta ao OpenCode; sem CLIs ou modelos externos."""
import asyncio
import json

from integrations.opencode_cli import build_config


def test_orchestrator_is_default_and_network_is_connected():
    config = build_config()
    assert config["default_agent"] == "marceloclaro"
    server = config["mcp"]["ecosystem-network"]
    assert server["enabled"] is True
    assert server["command"] == [".venv/bin/python", "-m", "integrations.ecosystem_mcp"]
    assert "ecosystem" in config["command"]


class FakeCoordinator:
    def status(self):
        return {"status": "ready", "executors": {"claude": {"available": True}}}

    def route(self, task, required_capabilities=None, ecosystem=None):
        return {"task": task, "ecosystem": ecosystem, "required": required_capabilities}

    def run(self, task, required_capabilities=None, max_steps=3, timeout=120, ecosystem=None):
        return {"success": False, "status": "blocked", "task": task,
                "max_steps": max_steps, "timeout": timeout, "ecosystem": ecosystem}


def test_mcp_lists_real_network_tools():
    from integrations.ecosystem_mcp import mcp
    names = {tool.name for tool in asyncio.run(mcp.list_tools())}
    assert names == {"ecosystem_status", "ecosystem_route", "ecosystem_run",
                     "ecosystem_workflow", "ecosystem_workflow_status",
                      "ecosystem_library_search", "ecosystem_integration_status",
                      "ecosystem_artifact_handoff", "ecosystem_skill_plan",
                      "ecosystem_knowledge_plan", "ecosystem_scientific_run",
                      "ecosystem_scientific_runtime", "ecosystem_dataset_download",
                      "ecosystem_dataset_custom", "ecosystem_scientific_plugins",
                      "ecosystem_gemini_notebook"}


def test_mcp_preserves_blocked_result_and_bounds(monkeypatch):
    from integrations import ecosystem_mcp as surface
    monkeypatch.setattr(surface, "get_coordinator", lambda: FakeCoordinator())
    result = asyncio.run(surface.ecosystem_run("analisar código", max_steps=2,
                                              timeout=30, ecosystem="codex"))
    assert result["status"] == "blocked"
    assert result["success"] is False
    assert result["max_steps"] == 2 and result["timeout"] == 30


def test_cli_status_exposes_executor_state(monkeypatch, capsys):
    from marceloclaro import cli
    from integrations import ecosystem_mcp as surface
    monkeypatch.setattr(surface, "get_coordinator", lambda: FakeCoordinator())
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "network", "status"])
    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out)["executors"]["claude"]["available"]


def test_cli_run_returns_nonzero_when_blocked(monkeypatch, capsys):
    from marceloclaro import cli
    from integrations import ecosystem_mcp as surface
    monkeypatch.setattr(surface, "get_coordinator", lambda: FakeCoordinator())
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "network", "run", "analisar",
                                         "--ecosystem", "codex", "--max-steps", "2"])
    assert cli.main() == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "blocked" and result["ecosystem"] == "codex"


def test_cli_routes_whole_description_without_flags(monkeypatch, capsys):
    from marceloclaro import cli
    from integrations import ecosystem_mcp as surface
    monkeypatch.setattr(surface, "get_coordinator", lambda: FakeCoordinator())
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "network", "route", "revisar",
                                         "código", "--ecosystem", "claude"])
    assert cli.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result["task"] == "revisar código" and result["ecosystem"] == "claude"
