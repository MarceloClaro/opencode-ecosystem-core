"""R1050: gate metacognitivo — evidência literal, calibração e anti-overclaim."""
from __future__ import annotations

import hashlib

import pytest

from mci.metacognitive_gate import aggregate, evaluate_claim

SHA = hashlib.sha256(b"fonte").hexdigest()
VALID_EXTERNAL = {"independent": True, "verifier": "auditor-externo",
                  "artifact_sha256": hashlib.sha256(b"artefato").hexdigest()}


def claim(**overrides):
    base = {
        "id": "C1",
        "text": "A intervenção reduziu o desfecho em 12% na amostra.",
        "confidence": 0.7,
        "inference_level": "inference",
        "falsifier": "Se o intervalo incluir zero ou o efeito desaparecer na replicação.",
        "contradictions": [],
        "mechanism": "A intervenção altera o mediador M, que reduz o desfecho.",
        "evidence": [
            {"source_id": "s1", "quote": "12%", "source_sha256": SHA,
             "literal_verified": True},
            {"source_id": "s2", "quote": "reduziu o desfecho", "source_sha256": SHA,
             "literal_verified": True},
        ],
    }
    base.update(overrides)
    return base


def test_two_literal_sources_with_external_validation_is_supported_not_truth():
    result = evaluate_claim(claim(), external_validation=VALID_EXTERNAL,
                            calibration={"brier": 0.12, "samples": 10})
    assert result["status"] == "externally_supported"
    assert result["truth_claim"] is False
    assert result["external_validation"] is True
    assert result.get("confidence_promoted", False) is False


def test_no_evidence_blocks_and_unverified_evidence_raises():
    result = evaluate_claim(claim(evidence=[]))
    assert result["status"] == "blocked"
    assert "no_literal_evidence" in result["reasons"]
    bad = claim(evidence=[{"source_id": "s1", "quote": "12%", "source_sha256": SHA,
                           "literal_verified": False}])
    with pytest.raises(ValueError):
        evaluate_claim(bad)


def test_high_confidence_with_one_source_is_partial():
    result = evaluate_claim(claim(confidence=0.9, evidence=[
        {"source_id": "s1", "quote": "12%", "source_sha256": SHA,
         "literal_verified": True}]))
    assert result["status"] == "partial"
    assert "high_confidence_requires_two_independent_sources" in result["reasons"]


def test_contradiction_or_miscalibration_prevents_support():
    contradicted = evaluate_claim(claim(contradictions=["Estudo B não replicou."]),
                                  external_validation=VALID_EXTERNAL)
    assert contradicted["status"] == "partial"
    assert "unresolved_contradictions" in contradicted["reasons"]
    miscalibrated = evaluate_claim(claim(), external_validation=VALID_EXTERNAL,
                                   calibration={"brier": 0.4, "samples": 8})
    assert miscalibrated["status"] == "partial"
    assert "calibration_brier_above_0.25" in miscalibrated["reasons"]


def test_inference_without_mechanism_and_missing_falsifier():
    no_mechanism = evaluate_claim(claim(mechanism="curto"))
    assert no_mechanism["status"] == "partial"
    no_falsifier = evaluate_claim(claim(falsifier=""))
    assert no_falsifier["status"] == "blocked"
    assert "missing_falsifier" in no_falsifier["reasons"]


def test_without_external_validation_is_candidate_and_aggregate_is_conservative():
    result = evaluate_claim(claim())
    assert result["status"] == "candidate"
    aggregate_result = aggregate([claim(), claim(id="C2", contradictions=["divergência"])],
                                 external_validation=VALID_EXTERNAL)
    assert aggregate_result["status"] == "partial"
    assert aggregate_result["truth_claim"] is False
    assert aggregate_result["policy"] == "vote_score_payoff_never_truth"
    assert aggregate_result["human_review_required"] is True


def test_orchestrator_records_gate_without_promoting_confidence():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
    result = orchestrator.metacognitive_claim_gate(claim(evidence=[]))
    assert result["status"] == "blocked"
    assert result["truth_claim"] is False
    assert result["observation_id"]
    assert result["confidence_promoted"] is False
