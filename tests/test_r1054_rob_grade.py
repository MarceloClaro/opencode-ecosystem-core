"""R1054 — risco de viés e GRADE automáticos como sugestão auditável."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scientific_lab import quantitative, rob_grade_auto


def base_data():
    return {
        "project_id": "RP-ROB",
        "protocol": {
            "reviewer": "Revisor",
            "declared_at": "2026-11-04T12:00:00Z",
            "effect_measure": "SMD",
            "model": "random",
            "random_effects_method": "DL",
            "confidence_level": 0.95,
            "min_studies": 2,
            "max_i2_for_pooling": 100,
            "human_confirmation": True,
        },
        "studies": [
            {
                "study_id": "S1", "label": "A",
                "effect_size": -0.2, "standard_error": 0.1,
            },
            {
                "study_id": "S2", "label": "B",
                "effect_size": 0.8, "standard_error": 0.1,
            },
        ],
    }


def test_risk_of_bias_rules_low_and_high():
    low = rob_grade_auto.assess_risk_of_bias(
        "Participants were randomly assigned. Analysis used intention-to-treat. "
        "Loss to follow-up was 5%. The outcome was double-blind and the trial "
        "was registered in a public protocol."
    )
    assert low["overall"] == "low"
    assert low["domains"]["randomization"] == "low"
    assert low["automated"] is True
    assert low["authoritative"] is False

    high = rob_grade_auto.assess_risk_of_bias(
        "This quasi-experimental study used alternate allocation and per-protocol "
        "analysis. Missing outcome data were 25%. The outcome was self-reported."
    )
    assert high["overall"] == "high"
    assert high["domains"]["missing"] == "high"


def test_grade_automated_downgrades_and_requires_human():
    meta = {
        "k": 5,
        "primary_result": {"ci_low": -0.2, "ci_high": 0.8},
        "heterogeneity": {"i2_percent": 80},
        "risk_of_bias": {"studies_with_high_risk": 1},
    }
    with pytest.raises(ValueError):
        rob_grade_auto.assess_grade(
            meta, ["randomized trial"], reviewer="Revisor",
            human_confirmation=False,
        )
    grade = rob_grade_auto.assess_grade(
        meta, ["randomized trial"], reviewer="Revisor",
        human_confirmation=True,
    )
    assert grade["starting_level"] == "high"
    assert grade["domains"]["inconsistency"]["judgment"] == "very_serious"
    assert grade["domains"]["imprecision"]["judgment"] == "serious"
    assert grade["final_level_preview"] == "very_low"
    assert grade["automated"] is True
    assert grade["authoritative"] is False
    assert grade["human_review_required"] is True


def test_enrich_fills_rob_and_grade(tmp_path):
    data = base_data()
    result = rob_grade_auto.enrich(
        data,
        {
            "S1": "Participants were randomly assigned and analyzed by intention-to-treat. "
                  "Loss to follow-up was 5%. The trial was registered.",
            "S2": "This quasi-experimental study used alternate allocation and per-protocol "
                  "analysis. Missing data were 25%. The outcome was self-reported.",
        },
        reviewer="Revisor",
        human_confirmation=True,
        out=tmp_path,
    )
    enriched = result["enriched"]
    assert enriched["studies"][0]["risk_of_bias"]["overall"] == "low"
    assert enriched["studies"][1]["risk_of_bias"]["overall"] == "high"
    assert enriched["grade"]["automated"] is True
    assert result["report"]["status"] == "automated_suggestion"
    assert (tmp_path / "04_analysis/auto-rob-grade.json").exists()
    assert (tmp_path / "04_analysis/quantitative-auto.json").exists()
    final = quantitative.analyze(enriched)
    assert final["grade"]["automated"] is True
    assert final["grade"]["authoritative"] is False
    assert final["truth_claim"] is False
