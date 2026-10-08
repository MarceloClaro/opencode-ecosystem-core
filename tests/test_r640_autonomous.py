"""R640: cadeia real Blackboard/Transformer com executores herméticos."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from integrations.harness_federation.artifact import build_artifact
from marceloclaro.autonomous import AutonomousCoordinator
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from mci.blackboard import AgentCard, blackboard
from mci.metabus import metabus
from mci.reflexion import reflexion_engine
from sdd.loop_spec import loop_spec_registry
from transformer.harness_head import HarnessRegistry


class RuntimeDouble:
    def __init__(self, responses=None, available=("claude",)):
        self.responses = list(responses or [])
        self.available = available
        self.calls = []

    def status(self):
        return {"executors": {
            ecosystem: {"available": ecosystem in self.available}
            for ecosystem in ("claude", "codex", "antigravity", "opencode", "chatgpt")
        }}

    def execute(self, ecosystem, prompt, timeout=120, agent_id=None):
        self.calls.append((ecosystem, prompt, timeout, agent_id))
        if self.responses:
            return self.responses.pop(0)
        return {"success": True, "output": "Revisar código: análise concluída com explicação e evidências locais.",
                "ecosystem": ecosystem, "execution_mode": "native_cli"}


@pytest.fixture()
def isolated_orchestrator(monkeypatch, tmp_path):
    metabus_module = importlib.import_module("mci.metabus")
    for obj, attr, value in (
        (metabus, "subscribers", {}), (blackboard, "registry", {}),
        (blackboard, "tasks", {}), (metabus.memory, "episodic", []),
        (metabus.memory, "semantic", {}), (metabus.memory, "confidence_ledger", {}),
        (loop_spec_registry, "loops", {}),
    ):
        monkeypatch.setattr(obj, attr, value)
    monkeypatch.setattr(metabus_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(metabus.memory, "_save", lambda: None)
    metabus.subscribe("agent.register", blackboard._handle_registration)
    metabus.subscribe("task.post", blackboard._handle_task_post)
    metabus.subscribe("task.volunteer", blackboard._handle_volunteer)
    metabus.subscribe("task.complete", blackboard._handle_completion)
    metabus.subscribe("metacognition.reflect_request", reflexion_engine._handle_reflection)
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
    orchestrator.attention_router._semantic_matcher = False
    orchestrator.reduction_layer = SimpleNamespace(route=lambda _: {"confidence": 0.0})
    orchestrator.trust = SimpleNamespace(
        execute=lambda _: SimpleNamespace(allowed=True, reason="local", trust_score=0.8),
        learn=lambda *args, **kwargs: None,
    )
    blackboard.registry["code-reviewer"] = AgentCard(
        agent_id="code-reviewer", name="Revisor", description="Revisar código",
        capabilities=["code_review"], schema={},
    )
    return orchestrator


@pytest.fixture()
def registry(tmp_path):
    source = tmp_path / "SKILL.md"
    source.write_text("---\nname: revisar\ndescription: Revisar código\n---\n"
                      "INSTRUÇÃO IMPORTADA: examine os invariantes do código.\n", encoding="utf-8")
    artifact = build_artifact(source_path=str(source), ecosystem="codex", kind="skill",
                              origin="user", name="revisar", description="Revisar código",
                              capabilities=["code_review"])
    result = HarnessRegistry(repo_root=str(tmp_path))
    result._artifacts = [artifact]
    result._harvester = SimpleNamespace(inventory=lambda: {"discovered": 1})
    return result


def test_run_executes_assigned_agent_and_reports_metabus_feedback(isolated_orchestrator, registry):
    runtime = RuntimeDouble()
    coordinator = AutonomousCoordinator(orchestrator=isolated_orchestrator, runtime=runtime, registry=registry)
    result = coordinator.run("Revisar código", ["code_review"])

    assert result["status"] == "completed" and result["success"] is True
    task = blackboard.tasks[result["task_id"]]
    assert task.assigned_to == result["agent_id"] == "code-reviewer"
    assert task.status == "completed"
    assert blackboard.registry["code-reviewer"].status == "available"
    assert result["ecosystem"] == "claude"
    assert result["origin_ecosystem"] == "codex"
    assert result["execution_mode"] == "adapted_instructions"
    assert "INSTRUÇÃO IMPORTADA" in runtime.calls[0][1]
    assert metabus.memory.confidence_ledger["code-reviewer"] > 0.5
    assert metabus.memory.episodic


def test_requested_missing_executor_blocks_before_delegation(isolated_orchestrator, registry):
    runtime = RuntimeDouble()
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", ecosystem="codex")
    assert result["status"] == "blocked" and result["success"] is False
    assert runtime.calls == [] and blackboard.tasks == {}
    assert "codex" in result["error"]


def test_no_executor_never_reports_catalog_as_execution(isolated_orchestrator, registry):
    runtime = RuntimeDouble(available=())
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código")
    assert result["status"] == "blocked" and not result["success"]
    assert result["steps"] == 0 and not runtime.calls


def test_route_is_read_only_and_keeps_provenance(isolated_orchestrator, registry):
    runtime = RuntimeDouble()
    route = AutonomousCoordinator(isolated_orchestrator, runtime, registry).route("Revisar código")
    assert route["status"] == "ready"
    assert route["artifact"]["ecosystem"] == "codex"
    assert route["executor"] == "claude"
    assert route["ranking"]
    assert blackboard.tasks == {} and runtime.calls == []


def test_no_internal_agent_is_blocked_without_running_external_cli(isolated_orchestrator, registry):
    runtime = RuntimeDouble()
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", ["nonexistent"])
    assert result["status"] == "blocked" and result["steps"] == 0
    assert runtime.calls == []
    assert blackboard.tasks[result["task_id"]].status == "blocked"


def test_pipeline_revision_receives_previous_output_and_bounded_budget(isolated_orchestrator, registry):
    runtime = RuntimeDouble(responses=[
        {"success": True, "output": "incompleto"},
        {"success": True, "output": "Revisar código: diagnóstico preciso dos invariantes e evidências locais."},
    ])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", max_steps=2)
    assert result["status"] == "completed" and result["steps"] == 2
    assert "incompleto" in runtime.calls[1][1]
    assert "REVISÃO" in runtime.calls[1][1]
    assert 0 < runtime.calls[1][2] <= runtime.calls[0][2] <= 120
    assert result["evaluation_kind"] == "heuristic"


def test_short_valid_output_is_delivered_without_claiming_verification(isolated_orchestrator, registry):
    runtime = RuntimeDouble(responses=[{"success": True, "output": "OK"}])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Diga OK", max_steps=1)
    assert result["success"] and result["output"] == "OK"
    assert result["final_grade"]["passed"] is False
    assert result["evaluation_kind"] == "heuristic"


@pytest.mark.parametrize("response", [
    {"success": False, "output": "", "error": "timeout"},
    {"success": True, "output": ""},
    {"success": True, "output": "somente fila", "status": "queued"},
])
def test_failure_empty_or_queued_output_cannot_complete(isolated_orchestrator, registry, response):
    runtime = RuntimeDouble(responses=[response])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código")
    assert result["status"] == "failed" and not result["success"]
    assert result["steps"] == 1 and len(runtime.calls) == 1
    assert blackboard.tasks[result["task_id"]].status == "failed"
    assert blackboard.registry["code-reviewer"].status == "available"


def test_exception_releases_blackboard_assignment(isolated_orchestrator, registry):
    runtime = RuntimeDouble()
    runtime.execute = lambda *args, **kwargs: (_ for _ in ()).throw(OSError("CLI ausente"))
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código")
    assert result["status"] == "failed" and "CLI ausente" in result["error"]
    assert blackboard.registry["code-reviewer"].status == "available"


def test_hook_manifest_never_enters_executor_prompt(isolated_orchestrator, registry, tmp_path):
    source = tmp_path / "hooks.json"
    source.write_text('{"hooks":{"PreToolUse":[]}}', encoding="utf-8")
    registry._artifacts = [build_artifact(
        source_path=str(source), ecosystem="claude", kind="hook", name="guard",
        description="Revisar código", hook_events=["PreToolUse"],
        hook_commands=["DO_NOT_EXECUTE_THIS_COMMAND"],
    )]
    runtime = RuntimeDouble()
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código")
    assert result["success"]
    assert "DO_NOT_EXECUTE_THIS_COMMAND" not in runtime.calls[0][1]
    assert result["artifact"] is None


def test_changed_import_is_excluded_and_never_read_as_instructions(isolated_orchestrator, registry):
    artifact = registry.artifacts()[0]
    from pathlib import Path
    Path(artifact.source_path).write_text("CORRUPTED_INSTRUCTIONS", encoding="utf-8")
    runtime = RuntimeDouble()
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código")
    assert result["artifact"] is None
    assert "source_changed" in result["routing"]["excluded_artifacts"][artifact.artifact_id]
    assert "CORRUPTED_INSTRUCTIONS" not in runtime.calls[0][1]


def test_sdd_rejection_is_reflected_in_return_value(isolated_orchestrator, registry, monkeypatch, tmp_path):
    import json
    complete = isolated_orchestrator.report_completion
    monkeypatch.setattr(isolated_orchestrator, "report_completion",
                        lambda task_id, agent_id, result, success=True: complete(task_id, agent_id, result, success=False))
    result = AutonomousCoordinator(isolated_orchestrator, RuntimeDouble(), registry).run("Revisar código")
    assert result["status"] == "failed" and not result["success"]
    assert blackboard.tasks[result["task_id"]].status == "failed"
    stored = blackboard.tasks[result["task_id"]].result
    assert stored["status"] == "failed" and stored["success"] is False
    assert stored["error"] == result["error"]
    assert isolated_orchestrator.results[result["task_id"]] == stored
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    completions = [event["payload"] for event in events if event["topic"] == "task.complete"]
    assert len(completions) == 1
    assert completions[0]["status"] == "failed"
    assert completions[0]["result"].get("success") is not True
    assert completions[0]["result"].get("status") != "completed"
    assert metabus.memory.confidence_ledger["code-reviewer"] < 0.5


def test_accepted_completion_is_synchronized_without_duplicate_events(isolated_orchestrator, registry, tmp_path):
    import json
    result = AutonomousCoordinator(isolated_orchestrator, RuntimeDouble(), registry).run("Revisar código")
    stored = blackboard.tasks[result["task_id"]].result
    assert stored["status"] == "completed" and stored["success"] is True
    assert isolated_orchestrator.results[result["task_id"]] == stored
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    completions = [event for event in events if event["topic"] == "task.complete"]
    reflections = [event for event in events if event["topic"] == "metacognition.reflected"]
    assert len(completions) == len(reflections) == 1
    assert completions[0]["payload"]["status"] == "completed"


@pytest.mark.parametrize("parameters", [{"max_steps": 0}, {"max_steps": True},
                                         {"max_steps": 11}, {"timeout": 0},
                                         {"timeout": float("nan")}])
def test_invalid_budget_is_rejected_before_any_side_effect(isolated_orchestrator, registry, parameters):
    runtime = RuntimeDouble()
    with pytest.raises(ValueError):
        AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", **parameters)
    assert runtime.calls == [] and blackboard.tasks == {}


def test_time_budget_expires_before_next_revision(isolated_orchestrator, registry, monkeypatch):
    module = importlib.import_module("marceloclaro.autonomous")
    clock = iter([0.0, 0.0, 0.0, 121.0])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(clock))
    runtime = RuntimeDouble(responses=[{"success": True, "output": "incompleto"}])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", max_steps=2)
    assert result["status"] == "exhausted" and not result["success"]
    assert len(runtime.calls) == 1
    assert blackboard.tasks[result["task_id"]].status == "failed"


def test_default_fallback_is_visible_and_codex_can_complete(isolated_orchestrator, registry):
    registry._artifacts = []
    runtime = RuntimeDouble(available=("claude", "codex", "antigravity"), responses=[
        {"success": False, "output": "", "error": "autenticação Claude"},
        {"success": True, "output": "Revisar código: resultado concreto após inspeção local dos invariantes."},
    ])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", max_steps=2)
    assert result["success"] and result["ecosystem"] == "codex"
    assert result["steps"] == 2
    assert [call[0] for call in runtime.calls] == ["claude", "codex"]
    assert result["attempts"][0]["error"] == "autenticação Claude"
    assert result["fallbacks"][0]["from"] == "claude"
    assert blackboard.tasks[result["task_id"]].status == "completed"
    assert blackboard.registry["code-reviewer"].status == "available"


def test_fallback_cannot_exceed_shared_step_budget(isolated_orchestrator, registry):
    registry._artifacts = []
    runtime = RuntimeDouble(available=("claude", "codex"), responses=[{"success": False, "error": "autenticação"}])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", max_steps=1)
    assert not result["success"] and result["steps"] == 1
    assert [call[0] for call in runtime.calls] == ["claude"]
    assert blackboard.registry["code-reviewer"].status == "available"


def test_explicit_executor_never_falls_back(isolated_orchestrator, registry):
    runtime = RuntimeDouble(available=("claude", "codex"), responses=[{"success": False, "error": "autenticação"}])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", ecosystem="claude")
    assert not result["success"] and result["ecosystem"] == "claude"
    assert [call[0] for call in runtime.calls] == ["claude"]


def test_success_after_fallback_preserves_short_output_at_step_limit(isolated_orchestrator, registry):
    registry._artifacts = []
    runtime = RuntimeDouble(available=("claude", "codex"), responses=[
        {"success": False, "error": "autenticação"}, {"success": True, "output": "OK"},
    ])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Diga OK", max_steps=2)
    assert result["success"] and result["output"] == "OK"
    assert result["steps"] == 2 and len(runtime.calls) == 2
    assert not result["final_grade"]["passed"]


def test_failed_executor_is_not_retried_after_all_alternatives_fail(isolated_orchestrator, registry):
    registry._artifacts = []
    runtime = RuntimeDouble(available=("claude", "codex", "antigravity"), responses=[
        {"success": False, "error": "a"}, {"success": False, "error": "b"},
        {"success": False, "error": "c"},
    ])
    result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", max_steps=5)
    assert not result["success"] and result["steps"] == 3
    assert [call[0] for call in runtime.calls] == ["claude", "codex", "antigravity"]
    assert blackboard.tasks[result["task_id"]].status == "failed"


def test_runtime_trace_does_not_persist_whole_inventory_or_duplicate_output(isolated_orchestrator, registry, monkeypatch):
    import json
    monkeypatch.setattr(registry, "route", lambda *args: {
        "ranking": [(f"missing:{index}", 0.1) for index in range(2000)],
        "heads": {"semantic": [0.1] * 2000}, "utility": [0.1] * 2000,
        "weights": {"semantic": 1.0}, "spec_id": "SPEC-935-R621",
    })
    result = AutonomousCoordinator(isolated_orchestrator, RuntimeDouble(), registry).run("Revisar código")
    assert result["success"]
    assert result["routing"]["excluded_count"] == 2000
    assert len(json.dumps(result["routing"])) < 2500
    persisted = blackboard.tasks[result["task_id"]].result
    assert persisted["output"] == result["output"]
    assert all("output" not in attempt for attempt in persisted["attempts"])
