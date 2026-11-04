"""R1054 — extração automática de efeitos com rastro e confirmação humana."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scientific_lab import effect_extraction, quantitative


def test_extract_odds_ratio_with_ci():
    candidates = effect_extraction.extract_from_text(
        "The odds ratio was 0.45 (95% CI 0.30 to 0.68)."
    )
    assert candidates
    item = candidates[0]
    assert item["measure"] == "OR"
    assert item["reported_effect"] == 0.45
    assert item["analysis_scale"] == "log"
    assert item["standard_error"] == pytest.approx(
        (__import__("math").log(0.68) - __import__("math").log(0.30)) / (2 * 1.959963984540054)
    )
    assert item["status"] == "complete"
    assert item["automated"] is True
    assert item["human_review_required"] is True


def test_extract_smd_and_p_value():
    smd = effect_extraction.extract_from_text(
        "SMD = -0.32 (95% CI -0.55 to -0.09)."
    )[0]
    assert smd["measure"] == "SMD"
    assert smd["standard_error"] == pytest.approx(0.46 / (2 * 1.959963984540054))

    p_value = effect_extraction.extract_from_text(
        "OR = 0.5, p = 0.03."
    )[0]
    assert p_value["measure"] == "OR"
    assert p_value["se_method"] == "p_value"
    assert p_value["standard_error"] > 0


def test_incomplete_effect_is_marked_incomplete():
    candidates = effect_extraction.extract_from_text("OR = 0.5.")
    assert candidates
    assert candidates[0]["status"] == "incomplete"
    assert candidates[0]["standard_error"] is None


def test_draft_requires_confirmation_and_feeds_quantitative_module():
    candidates = [
        {
            "candidate_id": "E1", "study_id": "S1", "measure": "OR",
            "reported_effect": 0.5, "analysis_effect": -0.6931,
            "analysis_scale": "log", "standard_error": 0.2,
            "confidence": 0.9, "status": "complete", "quote": "OR = 0.5",
            "locator": "p.1", "source_file": "a.pdf", "source_sha256": "a" * 64,
            "page": 1, "title": "Estudo A",
        },
        {
            "candidate_id": "E2", "study_id": "S2", "measure": "OR",
            "reported_effect": 0.7, "analysis_effect": -0.3567,
            "analysis_scale": "log", "standard_error": 0.25,
            "confidence": 0.9, "status": "complete", "quote": "OR = 0.7",
            "locator": "p.1", "source_file": "b.pdf", "source_sha256": "b" * 64,
            "page": 1, "title": "Estudo B",
        },
    ]
    with pytest.raises(ValueError):
        effect_extraction.draft_quantitative_dataset(
            candidates, reviewer="Revisor", human_confirmation=False,
        )
    draft = effect_extraction.draft_quantitative_dataset(
        candidates, reviewer="Revisor", human_confirmation=True,
    )
    assert draft["status"] == "automated_draft"
    assert draft["protocol"]["automated_extraction"] is True
    assert len(draft["studies"]) == 2
    result = quantitative.analyze(draft)
    assert result["automated_extraction"] is True
    assert result["extraction_origin"] == "automated"
    assert result["truth_claim"] is False
    assert any("revisão humana" in item for item in result["limitations"])


def test_run_extracts_from_two_fulltexts(tmp_path):
    texts = tmp_path / "texts"
    texts.mkdir()
    (texts / "a.md").write_text(
        "# Estudo A\n\nDOI: 10.1000/a\n\n"
        "This study evaluated a controlled experiment with adult participants "
        "and reported the primary outcome after a predefined follow-up period. "
        "The odds ratio was 0.45 (95% CI 0.30 to 0.68). The authors described "
        "the analysis as exploratory and did not claim causality.\n",
        encoding="utf-8",
    )
    (texts / "b.md").write_text(
        "# Estudo B\n\nDOI: 10.1000/b\n\n"
        "This study evaluated a controlled experiment with adult participants "
        "and reported the primary outcome after a predefined follow-up period. "
        "The odds ratio was 0.70 (95% CI 0.50 to 0.98). The authors described "
        "the analysis as exploratory and did not claim causality.\n",
        encoding="utf-8",
    )
    studies = [
        {"study_id": "S1", "canonical_title": "Estudo A",
         "identifiers": {"doi": "10.1000/a"}, "source_records": ["ART-0001"]},
        {"study_id": "S2", "canonical_title": "Estudo B",
         "identifiers": {"doi": "10.1000/b"}, "source_records": ["ART-0002"]},
    ]
    records = [
        {"article_id": "ART-0001", "title": "Estudo A", "doi": "10.1000/a"},
        {"article_id": "ART-0002", "title": "Estudo B", "doi": "10.1000/b"},
    ]
    out = tmp_path / "projeto"
    result = effect_extraction.run(
        out, texts, studies, records,
        reviewer="Revisor", human_confirmation=True,
    )
    assert result["candidates"]["count"] >= 2
    assert result["draft"]["status"] == "automated_draft"
    assert (out / "04_analysis/auto-effect-candidates.json").exists()
    assert (out / "04_analysis/auto-quantitative-draft.json").exists()
    draft = json.loads(
        (out / "04_analysis/auto-quantitative-draft.json").read_text(encoding="utf-8")
    )
    assert len(draft["studies"]) == 2
