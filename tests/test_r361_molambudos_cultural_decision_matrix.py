# -*- coding: utf-8 -*-
"""TDD — SPEC-935-R361, matriz cultural e correções mecânicas."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PROJECT = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
BASE = ROOT / "validacao_externa" / "cultural_episteme"
MATRIX_PATH = BASE / "molambudos_r361_decision_matrix.json"
DOSSIER_PATH = BASE / "molambudos_r361_decision_matrix.md"
SOURCES_PATH = BASE / "molambudos_r361_sources.json"
DRIFT_PATH = BASE / "molambudos_r361_provenance_drift.json"
CONTROL_PATH = BASE / "molambudos_r361_control_gates.json"
R362_MANIFEST_PATH = BASE / "molambudos_r362_change_manifest.json"

CONCEPTS = {
    "curral_do_governo",
    "retirantes",
    "rasga_mortalha",
    "molambudos",
    "hospital_colonia",
}
TARGETS = {"en-US", "zh-CN"}
BLOCKERS = {
    "patu_1915_chronology",
    "hospital_closed_1980",
    "rasga_mortalha_beak_etiology",
    "molambudo_absolute_neologism",
    "victim_count_category_drift",
    "pseudoarchive_authenticity",
    "fictional_victim_insertion",
    "living_memory_erasure",
    "psychiatric_stigma_horror",
    "reader_consent_visual_provenance",
}


def _json(path: Path) -> dict:
    assert path.exists(), f"RED: artefato ausente: {path.name}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_r361_spec_registered_red_or_better():
    from sdd.spec_engine import spec_registry

    spec = spec_registry.get("SPEC-935-R361")
    assert spec is not None
    assert spec.status in {"red", "green", "verified", "active"}


def test_r361_applies_only_three_mechanical_correction_classes():
    en_mem06 = (PROJECT / "en/fragmentos/mem/MEM-06.tex").read_text(encoding="utf-8")
    en_doc17 = (PROJECT / "en/fragmentos/doc/DOC-17.tex").read_text(encoding="utf-8")
    zh_mem06 = (PROJECT / "zh/fragmentos/mem/MEM-06.tex").read_text(encoding="utf-8")

    assert "two hundred yards wide and perhaps three hundred long" not in en_mem06
    assert "two hundred meters wide and perhaps three hundred meters long" in en_mem06
    assert "People who walked days without food or water" not in en_doc17
    assert "People who walked for days without food or water" in en_doc17
    assert "用铁丝网围起来的区域" not in zh_mem06
    assert "用带刺铁丝网围起来的区域" in zh_mem06

    matrix = _json(MATRIX_PATH)
    changes = matrix["mechanical_changes"]
    assert len(changes) == 3
    assert {item["change_class"] for item in changes} == {
        "restore_metric_unit",
        "repair_english_duration_grammar",
        "restore_barbed_wire_semantics",
    }
    assert all(item["risk_level"] == "low" for item in changes)
    assert all(item["applied"] is True for item in changes)


def test_r361_protected_cultural_terms_remain_unchanged():
    en_mem06 = (PROJECT / "en/fragmentos/mem/MEM-06.tex").read_text(encoding="utf-8")
    zh_mem06 = (PROJECT / "zh/fragmentos/mem/MEM-06.tex").read_text(encoding="utf-8")
    en_doc17 = (PROJECT / "en/fragmentos/doc/DOC-17.tex").read_text(encoding="utf-8")
    zh_doc17 = (PROJECT / "zh/fragmentos/doc/DOC-17.tex").read_text(encoding="utf-8")
    en_mem12 = (PROJECT / "en/fragmentos/mem/MEM-12.tex").read_text(encoding="utf-8")
    zh_mem12 = (PROJECT / "zh/fragmentos/mem/MEM-12.tex").read_text(encoding="utf-8")
    en_luc01 = (PROJECT / "en/fragmentos/luc/LUC-01.tex").read_text(encoding="utf-8")
    zh_luc01 = (PROJECT / "zh/fragmentos/luc/LUC-01.tex").read_text(encoding="utf-8")

    assert "Government Pen" in en_mem06
    assert "Government Concentration Camp" not in en_mem06
    assert "molambudos" in en_mem06
    assert "政府牲畜圈" in zh_mem06
    assert "政府集中收容营" not in zh_mem06
    assert "莫兰布多斯" in zh_mem06 and "破衣人" in zh_mem06
    assert "retirantes" in en_doc17 and "逃荒者" in zh_doc17
    assert "Shroud-Ripper" in en_mem12 and "裹尸布撕裂者" in zh_mem12
    assert "Hospital-Colony of Barbacena" in en_luc01
    assert "巴尔巴塞纳收容医院" in zh_luc01 and "收容院" in zh_luc01

    protected = _json(MATRIX_PATH)["protected_cultural_terms"]
    assert all(item["changed"] is False for item in protected)


def test_r361_matrix_has_five_concepts_ten_pending_human_decisions():
    matrix = _json(MATRIX_PATH)
    assert matrix["spec_id"] == "SPEC-935-R361"
    assert matrix["external_validation"] is False
    assert matrix["human_review_required"] is True
    assert matrix["release_gate"] == "blocked"
    assert matrix["quality_verdict_allowed"] is False
    assert matrix["decision_status"] == "pending_human"
    assert matrix["manuscript_cultural_edits_applied"] is False
    assert matrix["source_evidence_summary"]["target_equivalence_count"] == 0
    assert set(matrix["concepts"]) == CONCEPTS

    decisions = matrix["decisions"]
    assert len(decisions) == 10
    assert Counter(
        (item["concept_id"], item["target_language"]) for item in decisions
    ) == Counter((concept, target) for concept in CONCEPTS for target in TARGETS)
    for decision in decisions:
        assert decision["status"] == "pending_human"
        assert len(decision["options"]) >= 2
        option_ids = {option["option_id"] for option in decision["options"]}
        for option in decision["options"]:
            assert option["text"].strip()
            assert option["claim_type"] == "translation_hypothesis"
            assert option["assessment_claim_type"] == "editorial_inference"
            assert option["gains"] and option["losses"] and option["risks"]
            assert option["evidence_source_ids"]
            assert option["evidence_refs"]
            assert {item["source_id"] for item in option["evidence_refs"]} == set(
                option["evidence_source_ids"]
            )
            assert all(
                item["support_scope"] in {
                    "referent_or_lexical_context_only",
                    "target_usage_only",
                }
                for item in option["evidence_refs"]
            )
        preference = decision["conditional_preference"]
        assert preference["status"] == "conditional"
        assert preference["claim_type"] == "editorial_inference"
        assert preference["option_id"] in option_ids
        assert preference["conditions"]
        assert decision["target_equivalence_evidence"] == "none"
        assert decision["human_question"].strip()


def test_r361_sources_are_read_traceable_and_cover_every_concept():
    payload = _json(SOURCES_PATH)
    assert payload["spec_id"] == "SPEC-935-R361"
    assert payload["external_validation"] is False
    assert payload["human_review_required"] is True
    assert payload["release_gate"] == "blocked"
    assert payload["quality_verdict_allowed"] is False
    sources = payload["sources"]
    assert len(sources) >= 10
    assert len({source["source_id"] for source in sources}) == len(sources)
    coverage = Counter()
    substantive_groups = {concept: set() for concept in CONCEPTS}
    qualified = Counter()
    for source in sources:
        parsed = urlparse(source["url"])
        assert parsed.scheme in {"http", "https"} and parsed.netloc
        assert source["title"].strip()
        assert source["author_or_institution"].strip()
        assert source["accessed_at"] == "2026-08-01"
        assert source["read_status"] in {
            "full_page",
            "abstract_page",
            "dictionary_entry",
            "metadata_only",
        }
        assert source["read_status"] != "search_snippet"
        assert source["claim_supported"].strip()
        assert source["limitations"].strip()
        assert source["independent_group_id"].strip()
        assert source["evidence_scope"] in {
            "metadata",
            "source_fact",
            "target_usage",
            "target_equivalence",
        }
        assert source["locator"].strip()
        assert "target_language" in source and "target_form" in source
        assert isinstance(source["supports_target_equivalence"], bool)
        if source["read_status"] == "metadata_only":
            assert source["evidence_scope"] == "metadata"
            assert source["supports_target_equivalence"] is False
        assert source["retrieval_method"] in {"webfetch", "delegated_full_read"}
        for concept in source["concept_ids"]:
            assert concept in CONCEPTS
            coverage[concept] += 1
            if source["read_status"] != "metadata_only":
                substantive_groups[concept].add(source["independent_group_id"])
            if source["source_type"] in {
                "institutional",
                "peer_reviewed",
                "academic_outreach",
                "dictionary",
            }:
                qualified[concept] += 1
    assert all(coverage[concept] >= 2 for concept in CONCEPTS)
    assert all(len(substantive_groups[concept]) >= 2 for concept in CONCEPTS)
    assert all(qualified[concept] >= 1 for concept in CONCEPTS)
    assert not any(source["supports_target_equivalence"] for source in sources)
    assert payload["evidence_summary"]["target_equivalence_count"] == 0
    assert payload["evidence_summary"]["release_allowed"] is False


def test_r361_records_ten_historical_and_ethical_blockers_without_silent_rewrite():
    matrix = _json(MATRIX_PATH)
    blockers = matrix["historical_blockers"]
    assert {item["blocker_id"] for item in blockers} == BLOCKERS
    for blocker in blockers:
        assert blocker["status"] == "blocked_author_decision"
        assert blocker["evidence_basis"]
        assert "source_ids" in blocker
        assert blocker["affected_occurrences"]
        assert len(blocker["author_options"]) >= 2
        assert blocker["automatic_change_applied"] is False

    chronology = next(
        item for item in blockers if item["blocker_id"] == "patu_1915_chronology"
    )
    assert len(chronology["affected_occurrences"]) >= 5
    assert {"1915", "1932", "1933"} <= set(re.findall(r"\b(?:1915|1932|1933)\b", chronology["documented_conflict"]))
    rasga = next(item for item in blockers if item["blocker_id"] == "rasga_mortalha_beak_etiology")
    assert rasga["claim_type"] == "limited_source_support_gap"
    molambudo = next(item for item in blockers if item["blocker_id"] == "molambudo_absolute_neologism")
    assert molambudo["claim_type"] == "lexical_attestation_scope_uncertainty"


def test_r361_preserves_r360_snapshot_through_explicit_hash_drift_manifest():
    payload = _json(DRIFT_PATH)
    assert payload["spec_id"] == "SPEC-935-R361"
    assert payload["predecessor_spec_id"] == "SPEC-935-R360"
    assert payload["predecessor_artifact_mutated"] is False
    assert payload["external_validation"] is False
    assert payload["human_review_required"] is True
    assert payload["release_gate"] == "blocked"
    assert payload["quality_verdict_allowed"] is False
    records = payload["records"]
    r362_records = (
        _json(R362_MANIFEST_PATH)["records"] if R362_MANIFEST_PATH.exists() else []
    )
    assert len(records) == 3
    assert {item["change_class"] for item in records} == {
        "restore_metric_unit",
        "repair_english_duration_grammar",
        "restore_barbed_wire_semantics",
    }
    affected_reviews = set()
    for record in records:
        path = ROOT / record["path"]
        assert path.is_file()
        digest = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
        if digest != record["new_sha256"]:
            successors = [
                item
                for item in r362_records
                if item["path"] == record["path"]
                and item["old_sha256"] == record["new_sha256"]
                and item["new_sha256"] == digest
            ]
            assert len(successors) == 1, (
                "hash R361 divergente sem encadeamento R361→R362 único"
            )
            assert successors[0]["snapshot_preserved"] is True
        assert record["old_sha256"] != record["new_sha256"]
        assert record["cultural_terms_changed"] is False
        assert record["snapshot_preserved"] is True
        assert record["affected_reviews"]
        for review in record["affected_reviews"]:
            affected_reviews.add(review["review_id"])
            assert review["status"] in {"mechanical_segment_rechecked", "snapshot_segment_unchanged"}
    assert affected_reviews == {
        "r360-curral_do_governo-en-us",
        "r360-curral_do_governo-zh-cn",
        "r360-retirantes-en-us",
        "r360-molambudos-en-us",
        "r360-molambudos-zh-cn",
    }


def test_r361_dossier_marks_claim_types_and_anti_overclaim():
    assert DOSSIER_PATH.exists(), "RED: matriz Markdown R361 ausente"
    text = DOSSIER_PATH.read_text(encoding="utf-8")
    lower = text.casefold()
    for heading in (
        "curral do governo",
        "retirantes",
        "rasga mortalha",
        "molambudos",
        "hospital colônia",
        "bloqueios históricos e ético-memoriais",
    ):
        assert heading in lower
    for marker in (
        "fato documentado",
        "inferência editorial",
        "hipótese tradutória",
        "não constitui validação cultural externa",
        "decisão humana",
        "release bloqueado",
        "quality_verdict_allowed: false",
        "lacuna de suporte folclórico",
        "incerteza lexical",
    ):
        assert marker in lower


def test_r361_verification_records_routes_normalizer_builds_and_regression():
    verification = _json(MATRIX_PATH)["verification"]
    assert verification["quote_normalizer_pending"] == 0
    assert verification["routes"]["valid"] == 540
    assert verification["routes"]["total"] == 540
    assert verification["routes"]["missing"] == 0
    assert verification["routes"]["divergent"] == 0
    builds = verification["builds"]
    assert set(builds) == {"pt", "en", "zh", "tri", "kdp_tri"}
    assert all(item["passed"] is True for item in builds.values())
    assert all(item["fatal_errors"] == 0 for item in builds.values())
    assert all(item["undefined_references"] == 0 for item in builds.values())
    assert all(item["missing_characters"] == 0 for item in builds.values())
    assert verification["regression"]["passed"] == verification["regression"]["total"]
    assert verification["regression"]["failed"] == 0


def test_r361_internal_control_gates_pass_without_opening_release():
    control = _json(CONTROL_PATH)
    assert control["spec_id"] == "SPEC-935-R361"
    assert control["external_validation"] is False
    assert control["human_review_required"] is True
    assert control["release_gate"] == "blocked"
    assert control["quality_verdict_allowed"] is False
    assert control["spec_lifecycle_status"] == "green"
    assert control["sdd_gate"]["verified"] is True
    assert control["sdd_gate"]["passed_count"] == 9
    assert control["sdd_gate"]["total_count"] == 9
    assert control["sdd_gate"]["verifier"] == "SpecVerifier"
    assert control["sdd_gate"]["verification_scope"] == "internal_spec_conformance"
    assert control["sdd_gate"]["external_validation_conferred"] is False
    assert control["sdd_gate"]["release_conferred"] is False
    assert control["communicable_status"] == "internal_spec_checks_passed"
    assert control["behavioral_gate"]["allowed"] is True
    assert control["behavioral_gate"]["risk_level"] == "moderate"
    assert control["behavioral_gate"]["opens_release"] is False
    assert control["source_evidence_gate"]["target_equivalence_count"] == 0
    assert control["source_evidence_gate"]["target_equivalence_gate_passed"] is False
    assert control["source_evidence_gate"]["release_allowed"] is False
    adversarial = control["adversarial_review_gate"]
    assert adversarial["anti_overclaim"]["initial_status"] == "FAIL_WITH_BLOCKERS"
    assert adversarial["anti_overclaim"]["final_status"] == "PASS_INTERNAL_PROCESS"
    assert adversarial["ethics"]["final_status"] == "PASS_AS_BLOCKING_DOSSIER"
    assert adversarial["release_allowed"] is False
    failures = control["token_economy"]["failures"]
    assert len(failures) >= 7
    assert all(not item["success"] for item in failures)
    assert all(
        position["status"] == "slashed"
        for item in failures
        for position in item["positions"]
    )
