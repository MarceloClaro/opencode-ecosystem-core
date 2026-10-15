"""Contratos das superfícies governadas, além dos testes de cada backend."""
import asyncio
import json

import pytest


def test_all_requested_plugins_pass_primary_validator():
    from integrations.scientific_plugins import REQUESTED_PLUGIN_IDS
    from marceloclaro.runtime_actions import validate_action
    config = {"operation": "sync", "plugin_ids": list(REQUESTED_PLUGIN_IDS)}
    assert validate_action("plugins", config) == config


def test_python_graph_cli_and_mcp_share_primary(monkeypatch, capsys):
    from marceloclaro.code_context_cli import run_code_context_cli
    from integrations import ecosystem_mcp
    calls = []
    class Primary:
        def code_context_action(self, config):
            calls.append(config)
            return {"success": True, "status": "completed", "static_only": True}
    p = Primary()
    assert run_code_context_cli(["python_graph", "--tool", "get_call_tree", "--arguments", '{"symbol_name":"example.py::f"}'], lambda **_: p) == 0
    assert json.loads(capsys.readouterr().out)["static_only"] is True
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: p)
    result = asyncio.run(ecosystem_mcp.ecosystem_code_context({"operation": "python_graph", "tool": "get_call_tree", "arguments": {"symbol_name": "example.py::f"}, "timeout_seconds": 30.0}))
    assert result["static_only"] is True
    assert calls[0] == calls[1]


@pytest.mark.parametrize("config", [{"operation": "start", "command": "echo hello"}, {"operation": "runs", "limit": True}, {"operation": "cancel"}])
def test_ci_rejects_unknown_or_truthy_requests_before_primary(monkeypatch, config):
    from integrations import ecosystem_mcp
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: pytest.fail("Late validation"))
    with pytest.raises(ValueError):
        asyncio.run(ecosystem_mcp.ecosystem_local_ci(config))


def test_ci_cli_and_mcp_use_single_primary(monkeypatch, capsys):
    from marceloclaro.governed_cli import run_governed_cli
    from integrations import ecosystem_mcp
    calls = []
    class Primary:
        def local_ci_action(self, config):
            calls.append(config)
            return {"status": "idle", "remote_check_created": False}
    p = Primary()
    assert run_governed_cli("ci-local", ["status"], lambda **_: p) == 0
    assert json.loads(capsys.readouterr().out)["remote_check_created"] is False
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: p)
    assert asyncio.run(ecosystem_mcp.ecosystem_local_ci({"operation": "status"}))["status"] == "idle"
    assert calls == [{"operation": "status"}] * 2


@pytest.mark.parametrize("contents", [None, "{bad-json", "x" * (128 * 1024 + 1)], ids=["missing", "invalid-json", "oversized"])
def test_agent_cli_config_errors_are_structured_before_primary(tmp_path, capsys, contents):
    from marceloclaro.governed_cli import run_governed_cli
    config_path = tmp_path / "profile.json"
    if contents is not None:
        config_path.write_text(contents)
    code = run_governed_cli("agentes", ["criar", "--config", str(config_path)],
                            lambda **_: pytest.fail("Invalid config reached primary"))
    assert code == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "blocked"
    assert result["executed"] is False


@pytest.fixture
def isolated_primary(tmp_path, monkeypatch):
    import copy
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from mci.blackboard import blackboard
    import importlib
    bus = importlib.import_module("mci.metabus")
    monkeypatch.setattr(bus, "MEMORY_FILE", str(tmp_path / "memory.json"))
    monkeypatch.setattr(bus, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(bus.metabus, "memory", bus.MetacognitiveMemory())
    registry, tasks = copy.deepcopy(blackboard.registry), copy.deepcopy(blackboard.tasks)
    try:
        yield MarceloClaroOrchestrator(auto_load_agents=False)
    finally:
        blackboard.registry.clear()
        blackboard.registry.update(registry)
        blackboard.tasks.clear()
        blackboard.tasks.update(tasks)


def test_primary_rejects_foreign_assignment_before_reporting_activation(isolated_primary, monkeypatch):
    from mci.blackboard import blackboard, AgentCard, BlackboardTask
    from mci.metabus import metabus
    import copy
    before = copy.deepcopy(metabus.memory.confidence_ledger)
    wrong = AgentCard("wrong-profile", "Wrong", "Fixture", [], {})
    wrong.status = "busy"
    blackboard.registry[wrong.agent_id] = wrong
    def wrong_delegate(description, required_capabilities, context):
        task = BlackboardTask("wrong-assignment", description, required_capabilities, context)
        task.assigned_to, task.status = wrong.agent_id, "assigned"
        blackboard.tasks[task.task_id] = task
        return task.task_id
    monkeypatch.setattr(isolated_primary, "delegate", wrong_delegate)
    report = isolated_primary.agent_profile_action({"operation": "activate",
             "agent_id": "readme-contract-audit", "task": "Auditar contrato do README"})
    assert report["status"] == "blocked"
    assert report["reason"] == "profile_assignment_mismatch"
    assert report["executed"] is False
    assert blackboard.tasks[report["task_id"]].status == "blocked"
    assert blackboard.tasks[report["task_id"]].assigned_to is None
    assert wrong.status == "available"
    assert metabus.memory.confidence_ledger == before


def test_primary_rechecks_source_before_publishing_registration(isolated_primary, tmp_path, monkeypatch):
    from pathlib import Path
    from agents.lifecycle import AgentLifecycleService
    from mci.metabus import metabus
    original_root = Path(__file__).resolve().parents[1]
    source = original_root / "agents/catalog/readme-contract-audit.md"
    target = tmp_path / "agents/catalog/readme-contract-audit.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    metadata = AgentLifecycleService(original_root).validate("readme-contract-audit")["profile"]
    for key in ("spec_file", "test_file"):
        ref = tmp_path / metadata[key]
        ref.parent.mkdir(parents=True, exist_ok=True)
        ref.write_text("# Fixture local")
    service = AgentLifecycleService(tmp_path)
    validate = service.validate
    def mutate_after_validation(agent_id):
        result = validate(agent_id)
        target.write_bytes(target.read_bytes() + b"\nChanged after validation")
        return result
    monkeypatch.setattr(service, "validate", mutate_after_validation)
    isolated_primary._agent_lifecycle = service
    published = []
    monkeypatch.setattr(metabus, "publish", lambda *args, **kwargs: published.append(args))
    with pytest.raises(ValueError, match="Perfil alterado"):
        isolated_primary.agent_profile_action({"operation": "register", "agent_id": "readme-contract-audit"})
    assert published == []


@pytest.fixture
def managed_primary(isolated_primary, tmp_path):
    from pathlib import Path
    from agents.lifecycle import AgentLifecycleService

    original_root = Path(__file__).resolve().parents[1]
    relative = "agents/catalog/readme-contract-audit.md"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_bytes((original_root / relative).read_bytes())
    metadata = AgentLifecycleService(original_root).validate("readme-contract-audit")["profile"]
    for key in ("spec_file", "test_file"):
        ref = tmp_path / metadata[key]
        ref.parent.mkdir(parents=True, exist_ok=True)
        ref.write_text("# Fixture local de referência")
    isolated_primary._agent_lifecycle = AgentLifecycleService(tmp_path)
    return isolated_primary, target


def test_repeated_activation_keeps_busy_profile_and_does_not_delegate(managed_primary):
    from mci.blackboard import blackboard

    primary, _ = managed_primary
    config = {"operation": "activate", "agent_id": "readme-contract-audit", "task": "Auditar contrato local"}
    first = primary.agent_profile_action(config)
    assert first["status"] == "assigned"
    card = blackboard.registry[config["agent_id"]]
    task = blackboard.tasks[first["task_id"]]
    tasks_before = dict(blackboard.tasks)

    second = primary.agent_profile_action(config)

    assert second["status"] == "busy"
    assert second["reason"] == "profile_busy"
    assert second["executed"] is False
    assert blackboard.registry[config["agent_id"]] is card
    assert card.status == "busy"
    assert blackboard.tasks == tasks_before
    assert blackboard.tasks[first["task_id"]] is task
    assert task.status == "assigned"
    assert task.assigned_to == config["agent_id"]


def test_registration_is_idempotent_while_profile_is_busy(managed_primary):
    from mci.blackboard import blackboard

    primary, _ = managed_primary
    aid = "readme-contract-audit"
    first = primary.agent_profile_action({"operation": "activate", "agent_id": aid, "task": "Auditar contrato local"})
    assert first["status"] == "assigned"
    card = blackboard.registry[aid]
    task = blackboard.tasks[first["task_id"]]

    registered = primary.agent_profile_action({"operation": "register", "agent_id": aid})

    assert registered["status"] == "registered"
    assert registered["registered"] is True
    assert registered["executed"] is False
    assert blackboard.registry[aid] is card
    assert card.status == "busy"
    assert blackboard.tasks[first["task_id"]] is task
    assert task.status == "assigned" and task.assigned_to == aid


@pytest.mark.parametrize("operation", ["register", "activate"])
def test_changed_profile_cannot_replace_busy_card_or_task(managed_primary, operation):
    from mci.blackboard import blackboard

    primary, target = managed_primary
    aid = "readme-contract-audit"
    first = primary.agent_profile_action({"operation": "activate", "agent_id": aid, "task": "Auditar contrato local"})
    assert first["status"] == "assigned"
    card = blackboard.registry[aid]
    old_schema = dict(card.input_schema)
    tasks_before = dict(blackboard.tasks)
    target.write_bytes(target.read_bytes() + b"\nChanged valid instructions\n")
    config = {"operation": operation, "agent_id": aid}
    if operation == "activate":
        config["task"] = "Outra tarefa que deve aguardar"

    report = primary.agent_profile_action(config)

    assert report["status"] == "blocked"
    assert report["reason"] == "profile_changed_while_busy"
    assert report["executed"] is False
    assert blackboard.registry[aid] is card
    assert card.input_schema == old_schema
    assert card.status == "busy"
    assert blackboard.tasks == tasks_before
    assert blackboard.tasks[first["task_id"]].assigned_to == aid
