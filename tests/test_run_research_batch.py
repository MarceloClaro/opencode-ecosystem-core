# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from research.pipelines.run_research_batch import (
    aggregate,
    ensure_dirs,
    iter_scenarios,
    load_matrix,
    run_one_scenario,
    save_aggregated,
    save_raw_results,
    save_report_md,
)


@pytest.fixture
def minimal_matrix(tmp_path: Path) -> Path:
    """Cria uma matriz mínima de cenários para testes locais."""
    matrix = {
        "version": "1.0.0",
        "global_defaults": {
            "repetitions_per_scenario": 1
        },
        "scenario_groups": [
            {
                "group_id": "G_TEST_OQS",
                "group_type": "oqs_focus",
                "scenarios": [
                    {
                        "scenario_id": "TEST_OQS_0001",
                        "domain": "scientific_reasoning",
                        "difficulty": 2,
                        "input_problem": "Qual pergunta reduz melhor a incerteza inicial?",
                        "uncertainty_profile": {
                            "conceptual_gaps": 1,
                            "undefined_terms": 1,
                            "conflicting_assumptions": 0
                        },
                        "risk_profile": {
                            "ethical_risk": "low",
                            "operational_risk": "low",
                            "epistemic_risk": "medium"
                        },
                        "environment_profile": {
                            "noise_level": "low",
                            "ambiguity_level": "medium",
                            "adversarial_level": "low",
                            "cost_profile": "low"
                        },
                        "expected_behavior": {
                            "minimum_expected_cs": 0.40
                        },
                        "expected_verdict": {
                            "oqs_pass": True
                        },
                        "tags": ["test", "oqs"],
                        "seed": 12345
                    }
                ]
            },
            {
                "group_id": "G_TEST_VSEE",
                "group_type": "vsee_focus",
                "scenarios": [
                    {
                        "scenario_id": "TEST_VSEE_0001",
                        "domain": "optimization",
                        "difficulty": 3,
                        "input_problem": "Executar caminho vetorial com fidelidade mínima de 0.90.",
                        "uncertainty_profile": {
                            "conceptual_gaps": 0,
                            "undefined_terms": 0,
                            "conflicting_assumptions": 0
                        },
                        "risk_profile": {
                            "ethical_risk": "low",
                            "operational_risk": "medium",
                            "epistemic_risk": "low"
                        },
                        "environment_profile": {
                            "noise_level": "low",
                            "ambiguity_level": "low",
                            "adversarial_level": "medium",
                            "cost_profile": "high"
                        },
                        "expected_behavior": {
                            "vsee_should_choose": "vector"
                        },
                        "expected_verdict": {
                            "vsee_pass": True
                        },
                        "tags": ["test", "vsee"],
                        "seed": 22345
                    }
                ]
            }
        ]
    }

    matrix_path = tmp_path / "scenario_matrix_test.json"
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    return matrix_path


def test_load_matrix_and_iter_scenarios(minimal_matrix: Path):
    matrix = load_matrix(minimal_matrix)
    scenarios = iter_scenarios(matrix)

    assert matrix["version"] == "1.0.0"
    assert len(scenarios) == 2
    assert scenarios[0]["scenario_id"] == "TEST_OQS_0001"
    assert scenarios[1]["scenario_id"] == "TEST_VSEE_0001"
    assert "_group_type" in scenarios[0]


def test_ensure_dirs_creates_structure(tmp_path: Path):
    dirs = ensure_dirs(tmp_path / "results")

    assert dirs["raw"].exists()
    assert dirs["aggregated"].exists()
    assert dirs["reports"].exists()
    assert dirs["raw"].is_dir()
    assert dirs["aggregated"].is_dir()
    assert dirs["reports"].is_dir()


def test_run_one_scenario_returns_expected_shape(minimal_matrix: Path):
    matrix = load_matrix(minimal_matrix)
    scenario = iter_scenarios(matrix)[0]

    row = run_one_scenario(scenario, repetition_idx=0)

    assert row.scenario_id == "TEST_OQS_0001"
    assert row.group_type == "oqs_focus"
    assert isinstance(row.duration_ms, float)
    assert row.duration_ms >= 0.0

    # Campos críticos do pipeline
    assert isinstance(row.selected_question, str)
    assert "CS" in row.oqs_scores
    assert row.scientific_verdict in {"supported", "inconclusive", "refuted", "error"}

    # VSEE
    assert row.chosen_path in {"original", "vector"}
    assert set(row.telemetry.keys()) == {"EG", "TRR", "RI", "EFS"}

    # EGS
    assert 0.0 <= row.alignment_score <= 1.0
    assert row.ethical_decision in {"approve", "approve_with_constraints", "block"}

    # Flags
    assert {"oqs", "vsee", "egs", "pipeline"} <= set(row.pass_flags.keys())


def test_aggregate_computes_metrics(minimal_matrix: Path):
    matrix = load_matrix(minimal_matrix)
    scenarios = iter_scenarios(matrix)

    rows = [run_one_scenario(scenarios[0], 0), run_one_scenario(scenarios[1], 0)]
    summary = aggregate(rows)

    assert summary["total_runs"] == 2

    pass_rates = summary["pass_rates"]
    assert set(pass_rates.keys()) == {"oqs", "vsee", "egs", "pipeline"}
    assert all(0.0 <= v <= 1.0 for v in pass_rates.values())

    averages = summary["averages"]
    for key in ["CS", "EG", "TRR", "RI", "EFS", "alignment_score", "duration_ms"]:
        assert key in averages

    counts = summary["counts"]
    assert "hard_blocks" in counts
    assert "fallbacks" in counts


def test_save_raw_and_summary_and_report(minimal_matrix: Path, tmp_path: Path):
    matrix = load_matrix(minimal_matrix)
    scenarios = iter_scenarios(matrix)
    rows = [run_one_scenario(sc, 0) for sc in scenarios]

    dirs = ensure_dirs(tmp_path / "results")
    batch_id = "batch_test_001"

    raw_path = save_raw_results(dirs["raw"], batch_id, rows)
    assert raw_path.exists()

    summary = aggregate(rows)
    summary_path = save_aggregated(dirs["aggregated"], batch_id, summary)
    assert summary_path.exists()

    report_path = save_report_md(dirs["reports"], batch_id, summary, raw_path, summary_path)
    assert report_path.exists()

    report_text = report_path.read_text(encoding="utf-8")
    assert "Research Batch Report" in report_text
    assert "Taxas de aprovação" in report_text
    assert "Médias" in report_text

    lines = raw_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(rows)
    parsed_first = json.loads(lines[0])
    assert "scenario_id" in parsed_first
    assert "telemetry" in parsed_first


def test_aggregate_empty_returns_zero():
    summary = aggregate([])
    assert summary["total_runs"] == 0
