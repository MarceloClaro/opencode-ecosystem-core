"""R1105 P1 - testes do harness de autonomia e tarefas reservadas."""
from __future__ import annotations

import json
from dataclasses import replace

import pytest

from benchmarks.autonomy_harness import (
    Response,
    ScriptedAdapter,
    build_noisy_adapter,
    build_perfect_adapter,
    evaluate,
    load_tasks,
    run_dry_run,
    task_suite_sha256,
    validate_tasks,
)


def test_task_suite_schema_and_hash():
    tasks = load_tasks()
    assert len(tasks) >= 12
    assert len({task.id for task in tasks}) == len(tasks)
    assert all(task.split == "heldout" for task in tasks)
    for task in tasks:
        assert task.category
        assert task.prompt
        assert task.risk in {"low", "medium", "high"}
        assert task.expected_action in {"answer", "abstain", "escalate"}
        if task.expected_action == "answer":
            assert task.expected_answer is not None
        else:
            assert task.expected_answer is None
        evidence_ids = {item["id"] for item in task.evidence}
        assert set(task.required_citations) <= evidence_ids
    assert len(task_suite_sha256(tasks)) == 64


def test_validate_rejects_duplicate_and_invalid_tasks():
    task = load_tasks()[0]
    with pytest.raises(ValueError):
        validate_tasks([task, task])
    with pytest.raises(ValueError):
        validate_tasks([replace(task, expected_action="delete")])
    with pytest.raises(ValueError):
        validate_tasks([replace(task, expected_action="answer", expected_answer=None)])
    with pytest.raises(ValueError):
        validate_tasks([replace(task, required_citations=["missing-evidence"])])


def test_perfect_scripted_adapter_scores():
    tasks = load_tasks()
    report = evaluate(build_perfect_adapter(tasks), tasks, attempts=1)

    assert report["task_correctness"] == 1.0
    assert report["brier_score"] == pytest.approx(0.01, abs=1e-9)
    assert report["citation_support"]["f1"] == pytest.approx(1.0)
    assert report["unauthorized_actions"] == 0
    assert report["cost_per_correct_task"] == pytest.approx(10.0)
    assert report["abstention_rate"] > 0
    assert report["experiment_status"] == "harness_validation_only_not_model_result"


def test_noisy_adapter_exposes_calibration_and_repeated_errors():
    tasks = load_tasks()
    perfect = evaluate(build_perfect_adapter(tasks), tasks, attempts=1)
    noisy = evaluate(build_noisy_adapter(tasks), tasks, attempts=3)

    assert noisy["attempts_total"] == 3 * len(tasks)
    assert noisy["brier_score"] > perfect["brier_score"]
    assert noisy["repeated_error_rate"] == pytest.approx(1.0)
    assert noisy["unauthorized_actions"] == 1
    assert noisy["cost_per_correct_task"] > perfect["cost_per_correct_task"]
    assert noisy["task_correctness"] == 1.0


def test_citation_support_distinguishes_missing_citation():
    tasks = load_tasks()
    responses = {task.id: [Response(
        action=task.expected_action,
        answer=task.expected_answer,
        confidence=0.9,
        citations=list(task.required_citations),
        cost=10,
        latency_seconds=0.01,
        unauthorized_actions=0,
    )] for task in tasks}
    target = next(task for task in tasks if task.required_citations)
    responses[target.id] = [Response(
        action=target.expected_action,
        answer=target.expected_answer,
        confidence=0.9,
        citations=[],
        cost=10,
        latency_seconds=0.01,
        unauthorized_actions=0,
    )]

    report = evaluate(ScriptedAdapter(responses), tasks, attempts=1)

    assert report["citation_support"]["tasks"] >= 1
    assert report["citation_support"]["recall"] < 1.0
    assert report["citation_support"]["f1"] < 1.0


def test_risk_coverage_is_monotonic_in_threshold():
    tasks = load_tasks()
    report = evaluate(build_perfect_adapter(tasks), tasks, attempts=1)
    curve = report["risk_coverage"]

    assert [row["threshold"] for row in curve] == [0.0, 0.5, 0.7, 0.9]
    coverages = [row["coverage"] for row in curve]
    assert coverages == sorted(coverages, reverse=True)
    assert all(0.0 <= coverage <= 1.0 for coverage in coverages)


def test_heldout_loader_rejects_empty_split():
    assert all(task.split == "heldout" for task in load_tasks(split="heldout"))
    with pytest.raises(ValueError):
        load_tasks(split="dev")


def test_dry_run_writes_labeled_report(tmp_path):
    output = tmp_path / "dry-run.json"
    data = run_dry_run(output_path=output)

    assert output.exists()
    assert data["experiment_status"] == "harness_validation_only_not_model_result"
    assert data["tasks_sha256"] == task_suite_sha256(load_tasks())
    assert "perfect" in data["reports"]
    assert "noisy" in data["reports"]
    assert data["limitations"]
    assert data["claim_policy"]


def test_adapter_receives_blinded_task_view():
    tasks = load_tasks()
    adapter = build_perfect_adapter(tasks)
    original_run = adapter.run

    def checked_run(task, attempt):
        assert not hasattr(task, "expected_answer")
        assert not hasattr(task, "expected_action")
        assert not hasattr(task, "required_citations")
        return original_run(task, attempt)

    adapter.run = checked_run
    report = evaluate(adapter, tasks, attempts=1)
    assert report["task_correctness"] == 1.0


def test_report_has_no_superiority_claim():
    tasks = load_tasks()
    report = evaluate(build_perfect_adapter(tasks), tasks, attempts=1)
    policy = report["claim_policy"].lower()

    assert "não declara" in policy
    assert "validação externa" in policy
    assert report["experiment_status"] == "harness_validation_only_not_model_result"
    assert "superioridade" in policy  # apenas como negação explícita
