# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from pathlib import Path


def _rows():
    return [
        {
            "scenario_id": "B1",
            "pass_flags": {"oqs": True, "vsee": True, "egs": True, "pipeline": True},
            "oqs_scores": {"CS": 0.62, "URS": 0.70, "DRI": 0.21},
            "telemetry": {"EG": 1.12, "TRR": 0.22, "RI": 1.05, "EFS": 0.91},
            "alignment_score": 0.81,
            "hard_block": False,
            "ethical_decision": "approve",
            "duration_ms": 120.0,
            "error_flags": [],
        },
        {
            "scenario_id": "B2",
            "pass_flags": {"oqs": True, "vsee": True, "egs": True, "pipeline": False},
            "oqs_scores": {"CS": 0.58, "URS": 0.66, "DRI": 0.25},
            "telemetry": {"EG": 1.08, "TRR": 0.20, "RI": 1.03, "EFS": 0.89},
            "alignment_score": 0.77,
            "hard_block": True,
            "ethical_decision": "block",
            "duration_ms": 140.0,
            "error_flags": [],
        },
    ]


def _baseline_rows():
    return [
        {
            "scenario_id": "P1",
            "pass_flags": {"oqs": True, "vsee": True, "egs": True, "pipeline": False},
            "oqs_scores": {"CS": 0.41, "URS": 0.52, "DRI": 0.33},
            "telemetry": {"EG": 1.01, "TRR": 0.11, "RI": 1.00, "EFS": 0.72},
            "alignment_score": 0.64,
            "hard_block": False,
            "ethical_decision": "approve_with_constraints",
            "duration_ms": 180.0,
            "error_flags": [],
        },
        {
            "scenario_id": "P2",
            "pass_flags": {"oqs": True, "vsee": True, "egs": True, "pipeline": False},
            "oqs_scores": {"CS": 0.44, "URS": 0.53, "DRI": 0.31},
            "telemetry": {"EG": 1.00, "TRR": 0.10, "RI": 1.00, "EFS": 0.74},
            "alignment_score": 0.66,
            "hard_block": False,
            "ethical_decision": "approve_with_constraints",
            "duration_ms": 175.0,
            "error_flags": [],
        },
    ]


def test_mean_ci_95_returns_bounds():
    from research.pipelines.analyze_research_batch import mean_ci_95

    ci = mean_ci_95([1.0, 2.0, 3.0, 4.0])

    assert round(ci.mean, 2) == 2.50
    assert ci.lower <= ci.mean <= ci.upper
    assert ci.sample_size == 4


def test_compute_baseline_comparison_returns_key_metrics():
    from research.pipelines.analyze_research_batch import compute_baseline_comparison

    comparisons = compute_baseline_comparison(_baseline_rows(), _rows())
    metric_names = {c.metric_name for c in comparisons}

    assert "pipeline_success_rate" in metric_names
    assert "efs_fidelity" in metric_names
    assert "alignment_score" in metric_names


def test_evaluate_maturity_returns_scorecard():
    from research.pipelines.analyze_research_batch import (
        analyze_egs_metrics,
        analyze_oqs_metrics,
        analyze_pipeline_metrics,
        analyze_vsee_metrics,
        compute_baseline_comparison,
        evaluate_maturity,
    )

    rows = _rows()
    comparisons = compute_baseline_comparison(_baseline_rows(), rows)
    scorecard = evaluate_maturity(
        analyze_oqs_metrics(rows),
        analyze_vsee_metrics(rows),
        analyze_egs_metrics(rows),
        analyze_pipeline_metrics(rows),
        comparisons,
    )

    assert 0.0 <= scorecard.readiness_percent <= 100.0
    assert isinstance(scorecard.critical_blockers, list)
    assert isinstance(scorecard.recommendations, list)
    assert isinstance(scorecard.decision_rationale, str)


def test_generate_analysis_report_writes_markdown(tmp_path: Path):
    from research.pipelines.analyze_research_batch import generate_analysis_report

    raw_path = tmp_path / "raw.jsonl"
    with raw_path.open("w", encoding="utf-8") as f:
        for row in _rows():
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    output_path = tmp_path / "analysis.md"
    generate_analysis_report(raw_path, None, output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "# Análise Estatística" in text
    assert "## 2. Análise OQS" in text
    assert "## 3. Análise VSEE" in text
    assert "## 4. Análise EGS" in text
    assert "## 5. Análise Pipeline Integrado" in text


def test_generate_final_report_uses_template_and_outputs_sections(tmp_path: Path):
    from research.pipelines.analyze_research_batch import generate_final_report

    raw_path = tmp_path / "raw.jsonl"
    summary_path = tmp_path / "summary.json"
    analysis_path = tmp_path / "analysis.md"
    output_path = tmp_path / "final_report.md"

    with raw_path.open("w", encoding="utf-8") as f:
        for row in _rows():
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "total_runs": 2,
        "pass_rates": {"oqs": 1.0, "vsee": 1.0, "egs": 1.0, "pipeline": 0.5},
        "averages": {"CS": 0.60, "EG": 1.10, "TRR": 0.21, "RI": 1.04, "EFS": 0.90, "alignment_score": 0.79, "duration_ms": 130.0},
        "counts": {"hard_blocks": 1, "fallbacks": 0},
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    analysis_path.write_text("# Análise Estatística\n\nConteúdo.", encoding="utf-8")

    generate_final_report(raw_path, summary_path, analysis_path, output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "# Relatório Final de Pesquisa" in text
    assert "## 1. Resumo Executivo" in text
    assert "## 3. Método" in text
    assert "## 4. Resultados" in text
    assert "## 8. Recomendação de Release" in text


def test_template_file_exists_in_repo():
    template = Path("research/results/reports/final_report_template.md")
    assert template.exists()
