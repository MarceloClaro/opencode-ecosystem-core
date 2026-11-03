"""R1049: laboratório de pesquisa file-first, sem rede e com budget."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_lab.budget import Budget, BudgetExceeded
from research_lab.run import create_run, finalize_run, load_run, record_step


def test_budget_blocks_steps_time_cost_and_external_calls():
    budget = Budget(max_steps=2, max_seconds=5.0, max_cost_usd=0.02,
                    max_external_calls=1)
    budget.consume(step_seconds=2.0, cost_usd=0.01, external_calls=1)
    budget.consume(step_seconds=2.0, cost_usd=0.005)
    with pytest.raises(BudgetExceeded):
        budget.consume(step_seconds=0.1)
    with pytest.raises(BudgetExceeded):
        Budget(max_steps=1).consume(step_seconds=1.0, external_calls=1)
    with pytest.raises(BudgetExceeded):
        Budget(max_cost_usd=0.01).consume(cost_usd=0.02)


def test_create_run_is_file_first_and_dry_run_does_not_execute(tmp_path):
    run = create_run("Avaliar a hipótese H1 com dados públicos e revisão humana.",
                     tmp_path, dry_run=True)
    directory = tmp_path / run["run_id"]
    assert run["status"] == "planned"
    assert run["human_review_required"] is True
    assert run["execution_performed"] is False
    assert (directory / "manifest.json").is_file()
    assert (directory / "plan.md").is_file()
    assert (directory / "budget.json").is_file()
    loaded = load_run(directory)
    assert loaded["objective"] == run["objective"]
    assert loaded["budget"]["used_steps"] == 0


def test_record_and_finalize_require_human_review(tmp_path):
    run = create_run("Testar uma hipótese falsificável com orçamento controlado.",
                     tmp_path, dry_run=True)
    directory = tmp_path / run["run_id"]
    updated = record_step(directory, "literatura", "Busca local registrada.",
                          step_seconds=1.5, cost_usd=0.0)
    assert updated["status"] == "in_progress"
    assert updated["budget"]["used_steps"] == 1
    with pytest.raises(ValueError):
        finalize_run(directory, reviewer="", verdict="partial")
    final = finalize_run(directory, reviewer="operador", verdict="partial",
                         notes="Hipótese ainda não refutada; falta replicação.")
    assert final["status"] == "completed_pending_external_validation"
    assert final["human_review"]["reviewer"] == "operador"
    assert final["human_review"]["verdict"] == "partial"
    assert final["external_validation"] is False
    assert (directory / "review.json").is_file()


def test_no_network_modules_are_imported(tmp_path):
    import research_lab.run as module
    source = Path(module.__file__).read_text()
    for forbidden in ("requests", "urllib", "httpx", "socket", "openai", "anthropic"):
        assert forbidden not in source
