"""Regressões R1245 para política de elegibilidade e lifecycle do Blackboard."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from mci.blackboard import AgentCard, BlackboardTask, blackboard
from mci.metabus import metabus
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from transformer.attention import AttentionRouter


@pytest.fixture(autouse=True)
def isolate_blackboard(monkeypatch, tmp_path):
    metabus_module = importlib.import_module("mci.metabus")
    previous_registry = blackboard.registry
    previous_tasks = blackboard.tasks
    previous_ledger = metabus.memory.confidence_ledger
    blackboard.registry = {}
    blackboard.tasks = {}
    metabus.memory.confidence_ledger = {}
    monkeypatch.setattr(metabus_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    events = []
    monkeypatch.setattr(
        metabus,
        "publish",
        lambda topic, payload, source_agent="system": events.append(
            {"topic": topic, "payload": payload, "source": source_agent}
        ) or 1,
    )
    yield events
    blackboard.registry = previous_registry
    blackboard.tasks = previous_tasks
    metabus.memory.confidence_ledger = previous_ledger


def _card(agent_id: str, capabilities: list[str], *, status: str = "available"):
    card = AgentCard(agent_id, agent_id, "agente de teste", capabilities, {})
    card.status = status
    blackboard.registry[agent_id] = card
    return card


def test_volunteer_must_belong_to_current_cfp_and_still_be_eligible(isolate_blackboard):
    task = BlackboardTask("task-1", "implementar", ["python"], {})
    blackboard.tasks[task.task_id] = task
    _card("worker", ["python"])
    _card("stale-worker", ["python"], status="busy")

    blackboard._match_task(task)
    assert task.eligible_agents == ["worker"]

    # A stale CFP cannot reserve an agent who was not eligible when issued,
    # even if that agent becomes available before the volunteer event arrives.
    blackboard.registry["stale-worker"].status = "available"
    blackboard._handle_volunteer({"payload": {"task_id": task.task_id, "agent_id": "stale-worker"}})

    assert task.status == "open"
    assert task.assigned_to is None
    assert blackboard.registry["stale-worker"].status == "available"

    blackboard.registry["worker"].status = "busy"
    blackboard._handle_volunteer({"payload": {"task_id": task.task_id, "agent_id": "worker"}})
    assert task.status == "open"
    assert task.assigned_to is None


def test_live_load_counts_only_assigned_tasks():
    from mci.blackboard import _live_load

    _card("worker", ["python"])
    for index, status in enumerate(("assigned", "assigned", "completed", "failed", "blocked")):
        task = BlackboardTask(f"task-{index}", "x", [], {})
        task.status = status
        task.assigned_to = "worker"
        blackboard.tasks[task.task_id] = task

    assert _live_load("worker") == pytest.approx(2 / 5)


def test_completion_accepts_only_assignee_and_terminal_status_once(isolate_blackboard):
    task = BlackboardTask("task-2", "implementar", [], {})
    task.status = "assigned"
    task.assigned_to = "worker"
    blackboard.tasks[task.task_id] = task
    _card("worker", [])

    blackboard._handle_completion({"payload": {
        "task_id": task.task_id, "agent_id": "impostor", "status": "completed", "result": "spoof"
    }})
    blackboard._handle_completion({"payload": {
        "task_id": task.task_id, "agent_id": "worker", "status": "cancelled", "result": "invalid"
    }})
    assert task.status == "assigned"
    assert task.result is None

    blackboard._handle_completion({"payload": {
        "task_id": task.task_id, "agent_id": "worker", "status": "completed", "result": "accepted"
    }})
    blackboard._handle_completion({"payload": {
        "task_id": task.task_id, "agent_id": "worker", "status": "failed", "result": "duplicate"
    }})
    assert task.status == "completed"
    assert task.result == "accepted"


def test_agent_is_released_only_when_no_other_task_is_assigned(isolate_blackboard):
    _card("worker", [])
    first = BlackboardTask("first", "one", [], {})
    second = BlackboardTask("second", "two", [], {})
    for task in (first, second):
        task.status = "assigned"
        task.assigned_to = "worker"
        blackboard.tasks[task.task_id] = task

    blackboard._handle_completion({"payload": {
        "task_id": first.task_id, "agent_id": "worker", "status": "completed"
    }})
    assert blackboard.registry["worker"].status == "busy"

    blackboard._handle_completion({"payload": {
        "task_id": second.task_id, "agent_id": "worker", "status": "failed"
    }})
    assert blackboard.registry["worker"].status == "available"


def _orchestrator(trust_score: float, *, confidence: float = 0.95):
    class Trust:
        def execute(self, _action):
            return SimpleNamespace(allowed=True, reason="test allowed", trust_score=trust_score)

    class Reduction:
        def route(self, _description):
            return {"agent": "worker", "confidence": 1.0, "method": "test"}

    class Economy:
        def post_task(self, *_args, **_kwargs):
            return None

        def commit(self, *_args, **_kwargs):
            return None

    metabus.memory.confidence_ledger["worker"] = confidence
    orchestrator = object.__new__(MarceloClaroOrchestrator)
    orchestrator.id = "test-coordinator"
    orchestrator.pending_cfps = {}
    orchestrator.trust = Trust()
    orchestrator.reduction_layer = Reduction()
    orchestrator.reduction_threshold = 0.85
    orchestrator.attention_router = AttentionRouter()
    orchestrator.economy = Economy()
    orchestrator.task_stakes = {}
    orchestrator._llm_calls_saved = 0
    orchestrator._task_counter = 0
    return orchestrator


def test_trust_below_point_three_requires_supervision_without_auto_volunteer(isolate_blackboard):
    task = BlackboardTask("task-low-trust", "implementar", ["python"], {})
    task.eligible_agents = ["worker"]
    blackboard.tasks[task.task_id] = task
    _card("worker", ["python"])

    _orchestrator(0.29)._on_cfp({"payload": {
        "task_id": task.task_id,
        "description": task.description,
        "eligible_agents": ["worker"],
    }})

    assert task.status == "awaiting_supervision"
    assert task.assigned_to is None
    assert task.supervision_candidates == [{
        "agent_id": "worker", "trust_score": 0.29,
        "trust_score_source": "behavioral_gate", "confidence_score": 0.95,
        "confidence_score_source": "metabus.confidence_ledger",
    }]
    assert not [event for event in isolate_blackboard if event["topic"] == "task.volunteer"]
    request = next(event for event in isolate_blackboard if event["topic"] == "task.supervision_required")
    assert request["payload"]["task_id"] == task.task_id


def test_trust_at_point_three_is_eligible_and_confidence_remains_distinct(isolate_blackboard):
    task = BlackboardTask("task-boundary", "implementar", ["python"], {})
    task.eligible_agents = ["worker"]
    blackboard.tasks[task.task_id] = task
    _card("worker", ["python"])

    _orchestrator(0.30, confidence=0.11)._on_cfp({"payload": {
        "task_id": task.task_id,
        "description": task.description,
        "eligible_agents": ["worker"],
    }})

    volunteer = next(event for event in isolate_blackboard if event["topic"] == "task.volunteer")
    assert volunteer["payload"] == {"task_id": task.task_id, "agent_id": "worker"}
    # The fixture captures publications; dispatch the recorded A2A event into
    # the Blackboard callback as the live MetaBus would.
    blackboard._handle_volunteer(volunteer)
    assert task.status == "assigned"
    assert task.assigned_to == "worker"
    assert metabus.memory.confidence_ledger["worker"] == pytest.approx(0.11)
