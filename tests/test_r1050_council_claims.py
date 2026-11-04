"""R1050: ledger de claims do conselho; voto/nota não viram verdade."""
from __future__ import annotations

import importlib

import pytest

SOURCES = [
    {"id": "s1", "text": "Resultado observado: 12 amostras; efeito de 12%.",
     "provenance": "fixture sintética"},
    {"id": "s2", "text": "Replicação independente: reduziu o desfecho.",
     "provenance": "fixture sintética"},
]


def council():
    return importlib.import_module("scientific_lab.council")


def claim(**overrides):
    base = {
        "id": "C1",
        "text": "A intervenção reduziu o desfecho em 12%.",
        "confidence": 0.7,
        "inference_level": "inference",
        "falsifier": "Intervalo incluindo zero ou efeito ausente na replicação.",
        "mechanism": "A intervenção altera o mediador M e reduz o desfecho.",
        "contradictions": [],
        "status": "supported",
        "evidence": [
            {"source_id": "s1", "quote": "12%"},
            {"source_id": "s2", "quote": "reduziu o desfecho"},
        ],
    }
    base.update(overrides)
    return base


def test_valid_two_source_claim_is_candidate_not_truth():
    result = council().validate_claims([claim()], SOURCES)
    assert result["status"] == "candidate"
    assert result["truth_claim"] is False
    assert result["claims"][0]["truth_claim"] is False
    assert result["policy"] == "vote_score_payoff_never_truth"


def test_supported_with_one_source_becomes_partial():
    result = council().validate_claims([claim(evidence=[{"source_id": "s1", "quote": "12%"}])], SOURCES)
    assert result["status"] == "partial"
    assert "supported_requires_two_independent_sources" in result["claims"][0]["reasons"]


def test_high_confidence_with_one_source_and_contradiction_are_partial():
    one = council().validate_claims([claim(confidence=0.9, evidence=[{"source_id": "s1", "quote": "12%"}])], SOURCES)
    assert one["status"] == "partial"
    contradicted = council().validate_claims([claim(contradictions=["Estudo B não replicou."])], SOURCES)
    assert contradicted["status"] == "partial"
    assert "unresolved_contradictions" in contradicted["claims"][0]["reasons"]


def test_quote_mismatch_and_missing_mechanism_fail_closed():
    with pytest.raises(ValueError):
        council().validate_claims([claim(evidence=[{"source_id": "s1", "quote": "inexistente"}])], SOURCES)
    with pytest.raises(ValueError):
        council().validate_claims([claim(mechanism="curto")], SOURCES)
    with pytest.raises(ValueError):
        council().validate_claims([claim(falsifier="")], SOURCES)


def test_report_can_include_claim_gate():
    mod = council()
    report = {"status": "completed", "findings": ["Descrição da fixture."],
              "evidence": [{"source_id": "s1", "quote": "12 amostras"}],
              "limitations": ["Fixture, não estudo."],
              "feynman": {"mechanism": "Explicação do procedimento.",
                          "observations": ["Há 12 amostras no texto."],
                          "inferences": ["Não inferimos causalidade."],
                          "test_oracle": "Conferir a contagem.",
                          "min_experiment": "Recontar as amostras."}}
    validated = mod.validate_report(report, SOURCES, claims=[claim()])
    assert validated["claim_gate"]["status"] == "candidate"
    assert validated["claim_gate"]["truth_claim"] is False
