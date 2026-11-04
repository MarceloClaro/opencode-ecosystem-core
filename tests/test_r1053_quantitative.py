"""R1053-A — meta-análise human-gated, heterogeneidade e GRADE."""
from __future__ import annotations

import json

import pytest

from scientific_lab import quantitative


def study(study_id, effect, se, overall="low"):
    return {
        "study_id": study_id,
        "label": study_id,
        "effect_size": effect,
        "standard_error": se,
        "design": "RCT",
        "outcome": "desfecho",
        "risk_of_bias": {
            "overall": overall,
            "domains": {
                "randomization": overall,
                "missing": "low",
            },
        },
    }


def payload(**overrides):
    base = {
        "schema_version": "1.0",
        "project_id": "RP-TEST",
        "protocol": {
            "reviewer": "Revisor Teste",
            "declared_at": "2026-11-04T12:00:00Z",
            "effect_measure": "SMD",
            "model": "random",
            "confidence_level": 0.95,
            "min_studies": 3,
            "max_i2_for_pooling": 75,
            "human_confirmation": True,
        },
        "studies": [
            study("S1", 0.0, 0.1, "low"),
            study("S2", 0.8, 0.1, "high"),
            study("S3", 0.4, 0.1, "some_concerns"),
        ],
        "grade": {
            "human_confirmation": True,
            "reviewer": "Revisor Teste",
            "declared_at": "2026-11-04T12:00:00Z",
            "starting_level": "high",
            "outcome": "desfecho",
            "domains": {
                "risk_of_bias": {"judgment": "serious", "reason": "um estudo com alto risco"},
                "inconsistency": {"judgment": "serious", "reason": "I² acima de 75%"},
                "indirectness": {"judgment": "not_serious", "reason": "população similar"},
                "imprecision": {"judgment": "not_serious", "reason": "intervalo informativo"},
                "publication_bias": {"judgment": "not_serious", "reason": "busca ampla"},
            },
        },
    }
    base.update(overrides)
    return base


def test_random_effects_heterogeneity_and_prediction_interval():
    result = quantitative.analyze(payload())
    assert result["k"] == 3
    assert result["fixed"]["pooled_effect"] == pytest.approx(0.4)
    assert result["random"]["pooled_effect"] == pytest.approx(0.4)
    assert result["random"]["tau2"] == pytest.approx(0.15)
    assert result["heterogeneity"]["q"] == pytest.approx(32.0)
    assert result["heterogeneity"]["i2_percent"] == pytest.approx(93.75)
    assert result["heterogeneity"]["df"] == 2
    assert result["prediction_interval"]["status"] == "computed"
    assert result["prediction_interval"]["low"] < 0.4 < result["prediction_interval"]["high"]
    assert result["prediction_interval"]["t_method"] == "t_table"
    assert result["risk_of_bias"]["studies_with_high_risk"] == 1
    assert result["grade"]["final_level"] == "low"
    assert result["truth_claim"] is False
    assert result["external_validation"] is False
    assert result["human_review_required"] is True


def test_fixed_model_and_no_grade_are_explicit():
    data = payload()
    data["protocol"]["model"] = "fixed"
    data.pop("grade")
    result = quantitative.analyze(data)
    assert result["primary_model"] == "fixed"
    assert result["primary_result"]["model"] == "fixed"
    assert result["grade"]["status"] == "not_assessed"
    assert result["grade"]["final_level"] is None


def test_protocol_and_data_requirements_are_fail_closed():
    data = payload()
    data["protocol"]["human_confirmation"] = False
    with pytest.raises(ValueError):
        quantitative.analyze(data)

    data = payload()
    data["studies"] = data["studies"][:2]
    with pytest.raises(ValueError):
        quantitative.analyze(data)

    data = payload()
    data["studies"][0]["standard_error"] = 0
    with pytest.raises(ValueError):
        quantitative.analyze(data)

    data = payload()
    data["studies"][0].pop("risk_of_bias")
    with pytest.raises(ValueError):
        quantitative.analyze(data)

    data = payload()
    data["studies"][1]["study_id"] = "S1"
    with pytest.raises(ValueError):
        quantitative.analyze(data)


def test_grade_requires_human_and_reason_for_serious_domain():
    data = payload()
    data["grade"]["human_confirmation"] = False
    with pytest.raises(ValueError):
        quantitative.analyze(data)

    data = payload()
    data["grade"]["domains"]["risk_of_bias"]["reason"] = ""
    with pytest.raises(ValueError):
        quantitative.analyze(data)


def test_refresh_integrates_quantitative_into_manuscript_and_audit(tmp_path):
    from research.searchers import PaperRecord
    from scientific_lab import research_project as rp

    class FakeSearcher:
        def __init__(self, platforms=None):
            self.platforms = platforms

        def search(self, query, limit_per_platform=5):
            return [PaperRecord(
                title="Estudo meta-analítico",
                authors=["Ana Silva"],
                year=2024,
                doi="10.1000/meta",
                url="https://example.org/meta",
                abstract=(
                    "Este estudo descreve um experimento controlado sobre o tema. "
                    "Os resultados indicam uma associação descritiva."
                ),
                venue="Revista de Teste",
                source="openalex",
            )]

    out = tmp_path / "projeto"
    rp.run(
        "tema meta-analítico",
        out,
        question="Quais evidências permitem uma síntese quantitativa?",
        sources=["openalex"],
        searcher_factory=FakeSearcher,
    )
    data_path = tmp_path / "quant.json"
    data_path.write_text(json.dumps(payload(), ensure_ascii=False), encoding="utf-8")
    result = rp.refresh_project(out, quantitative_data=data_path)
    assert result["counts"]["quantitative_studies"] == 3
    assert result["stages"]["quantitative"] == "completed"
    manuscript = (out / "06_manuscript/manuscript.md").read_text(encoding="utf-8")
    assert "Síntese quantitativa" in manuscript
    assert "0.400" in manuscript
    audit = json.loads((out / "05_audit/audit-report.json").read_text(encoding="utf-8"))
    checks = {check["id"]: check["status"] for check in audit["checks"]}
    assert checks["quantitative_protocol"] == "pass"
    assert checks["quantitative_grade_human"] == "pass"
    assert rp.verify_manifest(out)["status"] == "pass"


def test_run_writes_artifact(tmp_path):
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps(payload(), ensure_ascii=False), encoding="utf-8")
    result = quantitative.run(data_path, tmp_path)
    assert result["k"] == 3
    artifact = json.loads(
        (tmp_path / "04_analysis/quantitative-synthesis.json").read_text(encoding="utf-8")
    )
    assert artifact["schema_version"] == "1.0"
    assert artifact["truth_claim"] is False
    assert quantitative.summary(artifact)["k"] == 3
