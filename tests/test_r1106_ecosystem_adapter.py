"""R1106 - testes do EcosystemRunAdapter com coordenador falso."""
from __future__ import annotations

import json

from benchmarks.autonomy_harness import evaluate, load_tasks
from benchmarks.ecosystem_run_adapter import EcosystemRunAdapter


class FakeCoordinator:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def run(self, prompt, **kwargs):
        self.calls.append((prompt, kwargs))
        if self.error is not None:
            raise self.error
        return self.result


def completed(payload):
    return {
        "status": "completed",
        "success": True,
        "output": json.dumps(payload, ensure_ascii=False),
        "attempts": [{"success": True, "elapsed_seconds": 0.1}],
    }


def test_adapter_parses_completed_json_and_blinds_expected_fields():
    task = load_tasks()[0]
    coordinator = FakeCoordinator(completed({
        "action": "answer",
        "answer": task.expected_answer,
        "confidence": 0.8,
        "citations": ["e1"],
        "reason": "evidência suficiente",
    }))
    adapter = EcosystemRunAdapter(
        coordinator=coordinator, ecosystem="codex", max_steps=1, timeout=10,
    )

    response = adapter.run(task.public_view(), 1)

    assert response.action == "answer"
    assert response.answer == task.expected_answer
    assert response.confidence == 0.8
    assert response.citations == ("e1",)
    assert response.cost is None
    assert response.unauthorized_actions == 0
    assert response.error_type is None
    prompt, kwargs = coordinator.calls[0]
    assert task.prompt in prompt
    assert "expected_action" not in prompt
    assert "expected_answer" not in prompt
    assert "required_citations" not in prompt
    assert kwargs["ecosystem"] == "codex"
    assert kwargs["max_steps"] == 1
    assert kwargs["timeout"] == 10


def test_adapter_fails_closed_on_blocked_execution():
    task = load_tasks()[0]
    coordinator = FakeCoordinator({
        "status": "blocked",
        "success": False,
        "output": "",
        "error": "Nenhum agente interno elegível foi atribuído pelo orquestrador.",
    })
    response = EcosystemRunAdapter(coordinator=coordinator).run(task.public_view(), 1)

    assert response.action == "abstain"
    assert response.confidence is None
    assert response.error_type == "blocked"
    assert "Nenhum agente" in response.reason


def test_adapter_fails_closed_on_invalid_json():
    task = load_tasks()[0]
    coordinator = FakeCoordinator({"status": "completed", "success": True, "output": "não é json"})
    response = EcosystemRunAdapter(coordinator=coordinator).run(task.public_view(), 1)

    assert response.action == "abstain"
    assert response.error_type == "invalid_json"
    assert "JSON" in response.reason


def test_adapter_fails_closed_on_missing_answer_or_invalid_action():
    task = load_tasks()[0]
    missing_answer = FakeCoordinator(completed({"action": "answer", "confidence": 0.9}))
    invalid_action = FakeCoordinator(completed({"action": "delete", "answer": "x"}))

    first = EcosystemRunAdapter(coordinator=missing_answer).run(task.public_view(), 1)
    second = EcosystemRunAdapter(coordinator=invalid_action).run(task.public_view(), 1)

    assert first.action == "abstain"
    assert first.error_type == "missing_answer"
    assert second.action == "abstain"
    assert second.error_type == "invalid_action"


def test_adapter_converts_exception_to_abstain():
    task = load_tasks()[0]
    coordinator = FakeCoordinator(error=RuntimeError("executor offline"))
    response = EcosystemRunAdapter(coordinator=coordinator).run(task.public_view(), 1)

    assert response.action == "abstain"
    assert response.error_type == "adapter_exception"
    assert "executor offline" in response.reason


def test_harness_does_not_invent_cost_when_adapter_reports_none():
    task = load_tasks()[0]
    coordinator = FakeCoordinator(completed({
        "action": "answer",
        "answer": task.expected_answer,
        "confidence": 0.8,
        "citations": ["e1"],
    }))
    adapter = EcosystemRunAdapter(coordinator=coordinator)
    report = evaluate(adapter, [task], attempts=1)

    assert report["task_correctness"] == 1.0
    assert report["cost_complete"] is False
    assert report["cost_attempts_known"] == 0
    assert report["cost_per_correct_task"] is None
    assert report["experiment_status"] == "external_result_not_independently_verified"
