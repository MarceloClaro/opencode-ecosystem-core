"""R1148 — grafo de claims, proveniência e contraprovas."""
from __future__ import annotations

import json

import pytest

from mci import claims_graph

PSY = {
    "instrument": "Core Self-Report",
    "version": "1.0",
    "scale": "Likert 1-7",
    "reliability": {"omega": 0.82},
    "validity": {"construct": "autonomia", "notes": "fonte declarada"},
    "provenance": "doi:10.0000/exemplo",
    "license": "CC-BY-4.0",
}


def _certificate(tmp_path, accepted=True, theorem="lemma_x", counterproof="cpt_x"):
    payload = {
        "gate": {"accepted": accepted},
        "axioms": {
            theorem: {"classification": "kernel_checked"},
            counterproof: {"classification": "kernel_checked"},
        },
        "lean_file": {"sha256": "abc123"},
    }
    path = tmp_path / "certificate.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _claim_with_real_evidence(graph, claim_id="c1", value=0.8):
    graph.add_source("src1", title="Fonte", doi="10.0000/x")
    graph.add_claim(claim_id, "A intervenção reduz offloading.", kind="empirical")
    graph.add_evidence("ev1", domain="real", value=value, source_id="src1")
    graph.add_edge("ev1", claim_id, "supports", weight=0.9)
    return claim_id


def test_real_evidence_supports_claim():
    graph = claims_graph.ClaimsGraph()
    claim_id = _claim_with_real_evidence(graph)
    result = graph.warrant(claim_id)
    assert result["status"] == "supported"
    assert result["abstain"] is False
    assert result["warrant"] >= 0.6
    assert result["domains"] == {"real": 1}


def test_irreal_evidence_is_discounted():
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("c1", "Simulação prevê redução.", kind="empirical")
    graph.add_evidence(
        "ev1",
        domain="irreal",
        value=0.8,
        synthetic=True,
        scenario="mundo sintético A",
    )
    graph.add_edge("ev1", "c1", "supports", weight=0.9)
    result = graph.warrant("c1")
    assert result["status"] == "simulation_only"
    assert result["warrant"] <= 0.5
    assert result["abstain"] is True


def test_subjective_claim_requires_psychometrics():
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("c1", "Eu me sinto mais autônomo.", kind="subjective")
    graph.add_evidence("ev1", domain="real", value=0.8)
    graph.add_edge("ev1", "c1", "supports", weight=0.9)
    blocked = graph.warrant("c1")
    assert blocked["status"] == "insufficient_psychometric"
    assert blocked["warrant"] == 0.0
    graph.add_psychometric("c1", PSY)
    accepted = graph.warrant("c1")
    assert accepted["status"] == "subjective_review"
    assert accepted["warrant"] <= 0.6
    assert accepted["abstain"] is True


def test_axiom_is_declared_not_proved():
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("ax1", "Há um observador.", kind="axiom")
    result = graph.warrant("ax1")
    assert result["status"] == "declared_axiom"
    assert result["warrant"] <= 0.5
    assert result["abstain"] is True


def test_formal_link_requires_kernel_checked(tmp_path):
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("c1", "Identidade formal.", kind="lemma")
    path = _certificate(tmp_path)
    link = graph.add_formal_link(
        "c1", theorem_id="lemma_x", counterproof_id="cpt_x", certificate_path=path
    )
    assert link["lean_file_sha256"] == "abc123"
    result = graph.warrant("c1")
    assert result["status"] == "formal_only"
    assert result["abstain"] is False

    bad = _certificate(tmp_path, accepted=False)
    graph.add_claim("c2", "Identidade formal 2.", kind="lemma")
    with pytest.raises(claims_graph.FormalLinkError):
        graph.add_formal_link(
            "c2", theorem_id="lemma_x", counterproof_id="cpt_x", certificate_path=bad
        )


def test_mixed_evidence_is_conflicted():
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("c1", "Há efeito.", kind="hypothesis")
    graph.add_evidence("ev1", domain="real", value=0.8)
    graph.add_evidence("ev2", domain="real", value=0.1)
    graph.add_edge("ev1", "c1", "supports", weight=0.9)
    graph.add_edge("ev2", "c1", "contradicts", weight=0.9)
    result = graph.warrant("c1")
    assert result["status"] == "conflicted"
    assert result["abstain"] is True


def test_contradiction_detection_by_polarity():
    graph = claims_graph.ClaimsGraph()
    graph.add_claim(
        "c1", "A intervenção funciona.", polarity="affirm", proposition_key="k"
    )
    graph.add_claim(
        "c2", "A intervenção não funciona.", polarity="deny", proposition_key="k"
    )
    graph.add_evidence("ev1", domain="real", value=0.8)
    graph.add_evidence("ev2", domain="real", value=0.7)
    graph.add_edge("ev1", "c1", "supports")
    graph.add_edge("ev2", "c2", "supports")
    findings = graph.detect_contradictions()
    assert any(finding["type"] == "polarity_conflict" for finding in findings)


def test_complex_evidence_is_accepted():
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("c1", "Amplitude complexa.", kind="empirical")
    graph.add_evidence(
        "ev1", domain="complex", value={"real": 0.6, "imag": 0.8}
    )
    graph.add_edge("ev1", "c1", "supports")
    result = graph.warrant("c1")
    assert result["domains"] == {"complex": 1}
    assert result["status"] == "supported"


def test_duplicate_node_is_rejected():
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("c1", "x")
    with pytest.raises(ValueError):
        graph.add_claim("c1", "y")


def test_irreal_requires_synthetic_and_scenario():
    graph = claims_graph.ClaimsGraph()
    with pytest.raises(ValueError):
        graph.add_evidence("ev1", domain="irreal", value=0.5)
    with pytest.raises(ValueError):
        graph.add_evidence(
            "ev1", domain="irreal", value=0.5, synthetic=True
        )
