"""R644: contrato de workflows e seleção pela saúde observada."""
import asyncio
import json

import pytest

from marceloclaro.autonomous import AutonomousCoordinator


class Runtime:
    def status(self):
        return {"executors": {
            "claude": {"available": True, "eligible_for_auto": False},
            "codex": {"available": True, "eligible_for_auto": True},
            "antigravity": {"available": False, "eligible_for_auto": False},
        }}


class Registry:
    def route(self, task, required):
        return {"ranking": []}

    def inventory(self):
        return {"discovered": 0}


def test_automatic_route_skips_executor_in_cooldown():
    result = AutonomousCoordinator(runtime=Runtime(), registry=Registry()).route("Analisar")
    assert result["executor"] == "codex"
    assert result["available_executors"] == ["codex"]
    assert result["installed_executors"] == ["claude", "codex"]


def test_explicit_executor_can_retry_during_cooldown():
    result = AutonomousCoordinator(runtime=Runtime(), registry=Registry()).route("Analisar", ecosystem="claude")
    assert result["executor"] == "claude" and result["status"] == "ready"


def test_status_distinguishes_installed_and_automatic():
    result = AutonomousCoordinator(runtime=Runtime(), registry=Registry()).status()
    assert result["available_executors"] == ["claude", "codex"]
    assert result["automatic_executors"] == ["codex"]


class FakeWorkflows:
    def __init__(self):
        self.calls = []

    def run(self, nodes, **kwargs):
        self.calls.append((nodes, kwargs))
        return {"success": True, "status": "completed", "workflow_id": "wf-1", "nodes": {}}

    def status(self, workflow_id):
        self.calls.append(workflow_id)
        return {"success": True, "status": "completed", "workflow_id": workflow_id}


def test_mcp_exposes_workflows_and_passes_resume_flags(monkeypatch):
    from integrations import ecosystem_mcp as surface
    workflows = FakeWorkflows()
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: workflows, raising=False)
    assert {"ecosystem_workflow", "ecosystem_workflow_status"} <= {
        tool.name for tool in asyncio.run(surface.mcp.list_tools())
    }
    nodes = [{"id": "analyse", "task": "Analisar"}]
    result = asyncio.run(surface.ecosystem_workflow(nodes, max_steps=2, timeout=30,
                                                  workflow_id="wf-1", resume=True, retry_failed=True))
    assert result["status"] == "completed"
    assert workflows.calls == [(nodes, {"max_steps": 2, "timeout": 30, "workflow_id": "wf-1",
                                       "resume": True, "retry_failed": True})]


def test_mcp_status_never_executes_workflow(monkeypatch):
    from integrations import ecosystem_mcp as surface
    workflows = FakeWorkflows()
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: workflows, raising=False)
    result = asyncio.run(surface.ecosystem_workflow_status("wf-1"))
    assert result["workflow_id"] == "wf-1" and workflows.calls == ["wf-1"]


def test_busy_network_rejects_workflow_before_any_child(monkeypatch):
    from integrations import ecosystem_mcp as surface
    workflows = FakeWorkflows()
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: workflows, raising=False)
    with surface._execution_lock:
        result = asyncio.run(surface.ecosystem_workflow([{"id": "a", "task": "Analisar"}]))
    assert result["status"] == "blocked" and not workflows.calls


def test_cli_workflow_reads_definition_and_resume_flags(monkeypatch, tmp_path, capsys):
    from integrations import ecosystem_mcp as surface
    from marceloclaro import cli
    workflows = FakeWorkflows()
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: workflows, raising=False)
    nodes = [{"id": "a", "task": "Analisar"}]
    definition = tmp_path / "nodes.json"
    definition.write_text(json.dumps({"nodes": nodes}), encoding="utf-8")
    assert cli._cmd_network(["workflow", str(definition), "--workflow-id", "wf-1", "--resume",
                             "--retry-failed", "--max-steps", "2", "--timeout", "30"]) == 0
    assert json.loads(capsys.readouterr().out)["workflow_id"] == "wf-1"
    assert workflows.calls[0][0] == nodes
    assert workflows.calls[0][1]["resume"] is True


def test_cli_bad_file_is_explicit_without_creating_coordinator(monkeypatch, tmp_path, capsys):
    from integrations import ecosystem_mcp as surface
    from marceloclaro import cli
    workflows = FakeWorkflows()
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: workflows, raising=False)
    definition = tmp_path / "bad.json"
    definition.write_text("{", encoding="utf-8")
    assert cli._cmd_network(["workflow", str(definition)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "invalid" and not workflows.calls


def test_cli_checkpoint_query_is_read_only(monkeypatch, capsys):
    from integrations import ecosystem_mcp as surface
    from marceloclaro import cli
    workflows = FakeWorkflows()
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: workflows, raising=False)
    assert cli._cmd_network(["workflow-status", "wf-1"]) == 0
    assert json.loads(capsys.readouterr().out)["workflow_id"] == "wf-1"
    assert workflows.calls == ["wf-1"]


@pytest.mark.parametrize("option", [["--ecosystem", "codex"], ["--capabilities", "audit"]])
def test_cli_workflow_never_ignores_executor_or_capability_selection(tmp_path, option, monkeypatch):
    from integrations import ecosystem_mcp as surface
    from marceloclaro import cli
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: FakeWorkflows())
    definition = tmp_path / "nodes.json"
    definition.write_text('[{"id":"a","task":"Analisar"}]', encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        cli._cmd_network(["workflow", str(definition), *option])
    assert exc.value.code == 2
