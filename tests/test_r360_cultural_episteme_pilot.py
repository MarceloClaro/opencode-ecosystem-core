# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R360, piloto cultural real de Molambudos."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REVIEWS_PATH = (
    ROOT
    / "validacao_externa"
    / "cultural_episteme"
    / "molambudos_r360_reviews.json"
)
DOSSIER_PATH = REVIEWS_PATH.with_name("molambudos_r360_dossier.md")
CONTROL_PATH = REVIEWS_PATH.with_name("molambudos_r360_control_gates.json")
UNITS = {
    "curral_do_governo",
    "retirantes",
    "rasga_mortalha",
    "molambudos",
    "hospital_colonia",
    "ameaca_proximo",
}
TARGETS = {"en-US", "zh-CN"}
HIGH_RISK_UNITS = {
    "curral_do_governo",
    "rasga_mortalha",
    "molambudos",
    "hospital_colonia",
}


def _artifact() -> dict:
    assert REVIEWS_PATH.exists(), "RED: dossiê JSON R360 ainda não foi gerado"
    return json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))


def test_r360_spec_is_registered_red_or_better():
    from sdd.spec_engine import spec_registry

    spec = spec_registry.get("SPEC-935-R360")
    assert spec is not None
    assert spec.status in {"red", "green", "verified", "active"}


def test_r360_spec_verifier_executes_acceptance_gate():
    from sdd.spec_engine import spec_registry, spec_verifier

    spec = spec_registry.get("SPEC-935-R360")
    assert spec is not None
    if not spec.criteria:
        spec.add_criterion(
            "Doze pareceres runtime",
            lambda out: len(out.get("reviews", [])) == 12,
        )
        spec.add_criterion(
            "Contratos runtime revalidados",
            lambda out: all(
                review.get("agent_runtime", {}).get("contract_valid") is True
                for review in out.get("reviews", [])
            ),
        )
        spec.add_criterion(
            "Release permanece bloqueado",
            lambda out: all(
                review.get("gate", {}).get("release_gate") == "blocked"
                for review in out.get("reviews", [])
            ),
        )
        spec.add_criterion(
            "Nenhuma edição automática",
            lambda out: out.get("manuscript_edits_applied") is False
            and not out.get("aggregate", {}).get("automatic_changes"),
        )
        spec.add_criterion(
            "Sem validação externa alegada",
            lambda out: out.get("external_validation") is False,
        )
        spec.add_criterion(
            "Deltas permanecem propostos",
            lambda out: bool(
                out.get("aggregate", {}).get("proposed_terminology_deltas")
            )
            and all(
                delta.get("approval_state") == "proposed"
                for delta in out["aggregate"]["proposed_terminology_deltas"]
            ),
        )
    result = spec_verifier.verify("SPEC-935-R360", _artifact())
    assert result["verified"] is True
    assert result["status"] == "green"
    assert result["passed_count"] == result["total_count"] == 6


def test_r360_has_exactly_twelve_runtime_reviews_and_never_opens_release():
    artifact = _artifact()
    assert artifact["spec_id"] == "SPEC-935-R360"
    assert artifact["contract_id"] == "OCB-CULTURAL-EPISTEME-001"
    assert artifact["external_validation"] is False
    assert artifact["manuscript_edits_applied"] is False

    reviews = artifact["reviews"]
    assert len(reviews) == 12
    assert len({review["review_id"] for review in reviews}) == 12
    assert Counter(
        (review["unit_id"], review["target_language"]) for review in reviews
    ) == Counter((unit, target) for unit in UNITS for target in TARGETS)
    for review in reviews:
        runtime = review["agent_runtime"]
        assert runtime["agent_slug"] == "cultural-episteme-agent"
        assert runtime["task_id"].strip()
        assert runtime["output_non_empty"] is True
        assert runtime["contract_valid"] is True
        assert review["gate"]["release_gate"] == "blocked"
        assert review["gate"]["human_review_required"] is True
        assert review["assessment"]["human_review_required"] is True
        assert review["assessment"]["release_gate"] == "blocked"


def test_r360_requests_assessments_preflight_and_gates_revalidate_independently():
    from translation.cultural_episteme import (
        evaluate_gate,
        run_preflight,
        validate_agent_output,
        validate_review_request,
    )

    for review in _artifact()["reviews"]:
        request = validate_review_request(review["request"])
        assessment = validate_agent_output(review["assessment"])
        assert request["review_id"] == review["review_id"]
        assert request["source_language"] == "pt-BR"
        assert request["target_language"] == review["target_language"]
        assert assessment["source_language"] == "pt-BR"
        assert assessment["target_language"] == review["target_language"]
        assert assessment["source_excerpt"] == request["source_text"]
        assert assessment["translated_excerpt"] == request["translated_text"]
        assert assessment["alternatives"]
        assert assessment["conditional_preference"] is not None

        preflight = run_preflight(request)
        assert preflight == review["preflight"]
        assert evaluate_gate(request, assessment, preflight) == review["gate"]


def test_r360_provenance_points_to_immutable_corpus_snapshot():
    drift_path = (
        ROOT
        / "validacao_externa/cultural_episteme/molambudos_r361_provenance_drift.json"
    )
    drift_records = []
    if drift_path.exists():
        drift_payload = json.loads(drift_path.read_text(encoding="utf-8"))
        assert drift_payload["predecessor_spec_id"] == "SPEC-935-R360"
        assert drift_payload["predecessor_artifact_mutated"] is False
        drift_records = drift_payload["records"]
    r362_path = drift_path.with_name("molambudos_r362_change_manifest.json")
    r362_records = []
    if r362_path.exists():
        r362_payload = json.loads(r362_path.read_text(encoding="utf-8"))
        assert r362_payload["predecessor_spec_id"] == "SPEC-935-R361"
        assert r362_payload["predecessor_artifact_mutated"] is False
        r362_records = r362_payload["records"]
    for review in _artifact()["reviews"]:
        locators = review["source_locators"]
        assert set(locators) == {"source", "target"}
        for locator_role, locator in locators.items():
            relative_path = locator["path"]
            corpus_file = ROOT / relative_path
            assert corpus_file.is_file()
            assert locator["line_start"] >= 1
            assert locator["line_end"] >= locator["line_start"]
            digest = hashlib.sha256(corpus_file.read_bytes()).hexdigest()
            if locator["sha256"] != digest:
                predecessor_matches = [
                    record
                    for record in drift_records
                    if record["path"] == relative_path
                    and record["old_sha256"] == locator["sha256"]
                    and any(
                        item["review_id"] == review["review_id"]
                        and item["locator_role"] == locator_role
                        for item in record["affected_reviews"]
                    )
                ]
                direct = [
                    record for record in predecessor_matches
                    if record["new_sha256"] == digest
                ]
                chained = [
                    (record, successor)
                    for record in predecessor_matches
                    for successor in r362_records
                    if successor["path"] == relative_path
                    and successor["old_sha256"] == record["new_sha256"]
                    and successor["new_sha256"] == digest
                ]
                inherited_successors = [
                    successor
                    for successor in r362_records
                    if successor["path"] == relative_path
                    and successor["old_sha256"] == locator["sha256"]
                    and successor["new_sha256"] == digest
                    and any(
                        item["review_id"] == review["review_id"]
                        and item["locator_role"] == locator_role
                        for item in successor.get("affected_reviews", [])
                    )
                ]
                assert len(direct) + len(chained) + len(inherited_successors) == 1, (
                    "hash R360 divergente sem encadeamento de proveniência único"
                )
                if direct:
                    assert direct[0]["snapshot_preserved"] is True
                elif chained:
                    assert chained[0][0]["snapshot_preserved"] is True
                    assert chained[0][1]["snapshot_preserved"] is True
                else:
                    assert inherited_successors[0]["snapshot_preserved"] is True
        for context_name in ("historical_context", "cultural_dossier"):
            provenance = review["request"][context_name]["provenance"]
            assert provenance
            assert all(item["source"] and item["limitations"] for item in provenance)


def test_r360_high_risk_terms_are_human_decisions_and_deltas_stay_proposed():
    artifact = _artifact()
    for review in artifact["reviews"]:
        if review["unit_id"] in HIGH_RISK_UNITS:
            assert review["editorial_classification"] == "high_risk_human_decision"
        for delta in review["assessment"]["terminology_graph_updates"]:
            assert delta["operation"] == "propose_upsert"
            assert delta["approval_state"] == "proposed"
            assert delta["delta_id"] == delta["idempotency_key"]

    deltas = artifact["aggregate"]["proposed_terminology_deltas"]
    assert deltas, "o conflito terminológico observado deve produzir proposta, não edição"
    assert all(delta["approval_state"] == "proposed" for delta in deltas)
    assert not artifact["aggregate"]["automatic_changes"]


def test_r360_uses_canonical_taxonomy_and_preserves_uncertainty():
    from translation.cultural_episteme import ISSUE_CODES

    artifact = _artifact()
    all_concerns = []
    for review in artifact["reviews"]:
        all_concerns.extend(review["assessment"]["candidate_concerns"])
        all_concerns.extend(review["preflight"])
        assert review["assessment"]["uncertainty_reasons"]
        assert review["assessment"]["limits"]
        assert review["assessment"]["evidence_sufficiency"] in {
            "insufficient",
            "partial",
            "substantial",
            "contested",
        }
    assert all_concerns
    assert {item["code"] for item in all_concerns} <= ISSUE_CODES
    assert any(
        item["code"] in {"TERM_CONFLICT", "LITERALISM", "CULTURAL_LOSS"}
        for item in all_concerns
    )


def test_r360_markdown_dossier_is_explicitly_non_authoritative():
    assert DOSSIER_PATH.exists(), "RED: dossiê Markdown R360 ainda não foi gerado"
    text = DOSSIER_PATH.read_text(encoding="utf-8")
    lower = text.casefold()
    for heading in (
        "curral do governo",
        "retirantes",
        "rasga mortalha",
        "molambudos",
        "hospital colônia",
        "você é o próximo",
    ):
        assert heading in lower
    for safeguard in (
        "auditoria heurística interna",
        "não constitui validação cultural externa",
        "revisão humana",
        "release bloqueado",
        "nenhuma alteração automática",
    ):
        assert safeguard in lower


def test_r360_control_gates_record_sdd_behavioral_and_slashing_outcomes():
    assert CONTROL_PATH.exists(), "RED: evidência dos gates de controle não gerada"
    control = json.loads(CONTROL_PATH.read_text(encoding="utf-8"))
    assert control["spec_id"] == "SPEC-935-R360"
    assert control["external_validation"] is False
    assert control["sdd_gate"]["verified"] is True
    assert control["sdd_gate"]["status"] == "green"
    assert control["sdd_gate"]["passed_count"] == 6
    assert control["sdd_gate"]["total_count"] == 6
    assert control["behavioral_gate"]["allowed"] is True
    assert control["behavioral_gate"]["risk_level"] in {"moderate", "safe"}
    assert control["trust_outcome"]["success"] is True
    assert control["token_economy"]["report"]["stakes"]["slashed"] == 4
    assert control["token_economy"]["report"]["stakes"]["released"] == 3
    assert len(control["token_economy"]["failures"]) == 4
    assert all(item["positions"] for item in control["token_economy"]["failures"])
    assert control["release_gate"] == "blocked"
    assert control["human_review_required"] is True
