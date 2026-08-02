# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R359 / OCB-CULTURAL-EPISTEME-001."""

from __future__ import annotations

import copy
import json
import math
import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
AGENT_PATH = ROOT / "agents" / "catalog" / "cultural-episteme-agent.md"
ORCHESTRATOR_PATH = ROOT / "agents" / "catalog" / "literary-orchestrator-phd.md"


def _request(**overrides):
    request = {
        "schema_version": "1.0.0",
        "review_id": "review-molambudos-001",
        "segment_id": "MEM-01:L10",
        "source_language": "pt-BR",
        "target_language": "en-US",
        "source_text": "A fome tira a gente da barraca à noite.",
        "translated_text": "Hunger takes us out of the tent at night.",
        "author_voice_profile": {
            "narrator_age": "child",
            "region": "Sertão do Ceará",
            "register": "oral, memorialístico e popular",
        },
        "terminology_graph": {
            "graph_id": "molambudos-terms",
            "revision": "7",
            "concepts": [],
        },
        "historical_context": {
            "period": "1915",
            "region": "Ceará",
            "support_status": "documented",
            "provenance": [
                {
                    "source": "dossiê histórico editorial",
                    "author": "equipe editorial",
                    "date": "2026-08-01",
                    "limitations": "requer revisão histórica independente",
                }
            ],
        },
        "cultural_dossier": {
            "target_variety": "English (United States)",
            "provenance": [
                {
                    "source": "glossário R355",
                    "author": "equipe editorial",
                    "date": "2026-07-31",
                    "limitations": "rascunho editorial",
                }
            ],
            "anachronism_markers": [],
        },
        "previous_translation_decisions": [],
    }
    request.update(overrides)
    return request


def _assessment(**overrides):
    assessment = {
        "schema_version": "1.0.0",
        "analysis_status": "complete",
        "source_language": "pt-BR",
        "target_language": "en-US",
        "source_excerpt": "A fome tira a gente da barraca à noite.",
        "translated_excerpt": "Hunger takes us out of the tent at night.",
        "candidate_concerns": [
            {
                "code": "LITERALISM",
                "severity": "medium",
                "evidence_strength": "moderate",
                "source_span": [0, 45],
                "target_span": [0, 45],
                "detector": "agent",
                "evidence": "takes us out reproduz a superfície verbal",
                "rationale": "a causalidade e a oralidade ficam enfraquecidas",
            }
        ],
        "cultural_context": {
            "region": "Sertão do Ceará",
            "period": "1915",
            "narrator_profile": "criança retirante",
            "register": "oral e memorialístico",
        },
        "alternatives": [
            {
                "text": "Hunger drives you out of the shelter at night.",
                "rationale": "mantém a força causal sem elevar o registro",
                "risks": ["you pode generalizar a primeira pessoa plural"],
            }
        ],
        "conditional_preference": {
            "text": "Hunger drives you out of the shelter at night.",
            "rationale": "candidata condicionada à revisão bilíngue",
            "conditions": ["confirmar a pessoa narrativa no parágrafo"],
        },
        "heuristic_signals": {
            "symbol_consistency": 1.0,
            "cultural_fidelity": 0.86,
            "author_voice_similarity": 0.80,
        },
        "process_checks": {
            "critical_omissions_identified": 0,
            "unresolved_term_conflicts": 0,
            "back_translation_used": False,
        },
        "evidence_sufficiency": "partial",
        "uncertainty_reasons": ["não houve revisão bilíngue independente"],
        "terminology_graph_updates": [],
        "human_review_required": True,
        "release_gate": "blocked",
        "missing_data": [],
        "limits": ["avaliação heurística interna"],
    }
    assessment.update(overrides)
    return assessment


def _frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert match, "arquivo de agente deve começar com frontmatter YAML"
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def test_r359_spec_is_registered_red_or_better():
    from sdd.spec_engine import spec_registry

    spec = spec_registry.get("SPEC-935-R359")
    assert spec is not None
    assert spec.status in {"red", "green", "verified", "active"}


def test_agent_catalog_contract_and_read_only_permissions():
    assert AGENT_PATH.exists()
    text = AGENT_PATH.read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm.get("name") == "cultural-episteme-agent"
    assert fm.get("mode") == "subagent"
    assert "model" not in fm
    assert "temperature" in fm
    assert len(fm.get("description", "")) > 80
    lower = text.lower()
    for required in [
        "ocb-cultural-episteme-001",
        "contrato de saída obrigatório",
        "nunca pode ser vazia",
        "release_gate: blocked",
        "human_review_required",
        "retrotradução",
        "não exotizar",
        "não domesticar",
        "unclassified_risk",
        "approval_state: proposed",
        "anti-overclaim",
    ]:
        assert required in lower
    for issue_code in [
        "LITERALISM",
        "CULTURAL_LOSS",
        "ANACHRONISM",
        "VOICE_SHIFT",
        "REGISTER_SHIFT",
        "SYMBOL_DRIFT",
        "TERM_CONFLICT",
        "PRAGMATIC_FAILURE",
        "TARGET_VARIETY_USAGE_RISK",
        "OVERLOCALIZATION",
        "UNDERLOCALIZATION",
        "ETHICAL_RISK",
        "UNCLASSIFIED_RISK",
    ]:
        assert issue_code in text
    assert re.search(r"permission:\s*\n(?:.*\n)*?\s+edit:\s*deny", text)
    assert re.search(r"permission:\s*\n(?:.*\n)*?\s+bash:\s*deny", text)


def test_request_contract_rejects_missing_or_invalid_language():
    from translation.cultural_episteme import ContractError, validate_review_request

    valid = validate_review_request(_request())
    assert valid["source_language"] == "pt-BR"
    assert valid["target_language"] == "en-US"

    missing = _request()
    missing.pop("historical_context")
    with pytest.raises(ContractError):
        validate_review_request(missing)
    with pytest.raises(ContractError):
        validate_review_request(_request(target_language="english"))


def test_output_contract_fails_closed_and_maps_unknown_risk():
    from translation.cultural_episteme import ContractError, validate_agent_output

    normalized = validate_agent_output(_assessment())
    assert normalized["release_gate"] == "blocked"

    unknown = _assessment(
        candidate_concerns=[
            {
                **_assessment()["candidate_concerns"][0],
                "code": "NEW_UNKNOWN_RISK",
                "severity": "low",
            }
        ]
    )
    normalized_unknown = validate_agent_output(unknown)
    concern = normalized_unknown["candidate_concerns"][0]
    assert concern["code"] == "UNCLASSIFIED_RISK"
    assert concern["original_code"] == "NEW_UNKNOWN_RISK"
    assert concern["severity"] in {"high", "critical"}
    assert normalized_unknown["human_review_required"] is True

    with pytest.raises(ContractError):
        validate_agent_output({})
    with pytest.raises(ContractError):
        validate_agent_output(_assessment(analysis_status="approved"))
    with pytest.raises(ContractError):
        validate_agent_output(_assessment(release_gate="open"))


@pytest.mark.parametrize("bad_score", [math.nan, math.inf, -0.1, 1.1, True])
def test_output_contract_rejects_non_finite_or_out_of_range_signals(bad_score):
    from translation.cultural_episteme import ContractError, validate_agent_output

    signals = dict(_assessment()["heuristic_signals"])
    signals["cultural_fidelity"] = bad_score
    with pytest.raises(ContractError):
        validate_agent_output(_assessment(heuristic_signals=signals))


def test_high_risk_requires_human_review_and_scores_never_unlock_release():
    from translation.cultural_episteme import ContractError, evaluate_gate, validate_agent_output

    concern = dict(_assessment()["candidate_concerns"][0])
    concern.update(code="ETHICAL_RISK", severity="high")
    with pytest.raises(ContractError):
        validate_agent_output(
            _assessment(candidate_concerns=[concern], human_review_required=False)
        )

    perfect = _assessment(
        candidate_concerns=[],
        heuristic_signals={
            "symbol_consistency": 1.0,
            "cultural_fidelity": 1.0,
            "author_voice_similarity": 1.0,
        },
    )
    result = evaluate_gate(_request(), validate_agent_output(perfect), [])
    assert result["release_gate"] == "blocked"
    assert result["decision"] == "candidate_for_human_review"
    assert result["human_review_required"] is True


def test_preflight_detects_required_cultural_and_pragmatic_cases_without_mutation():
    from translation.cultural_episteme import run_preflight

    request = _request(
        source_text="Retirante, você é o próximo, como se a fome falasse.",
        translated_text="The migrant might be next. Hunger spoke.",
        previous_translation_decisions=[
            {"source_term": "fome", "target_term": "hunger", "symbolic": True}
        ],
    )
    before = copy.deepcopy(request)
    concerns = run_preflight(request)
    assert request == before
    codes = {item["code"] for item in concerns}
    assert "CULTURAL_LOSS" in codes or "UNDERLOCALIZATION" in codes
    assert "PRAGMATIC_FAILURE" in codes
    assert "SYMBOL_DRIFT" not in codes  # hunger foi preservado

    contextualized = _request(
        source_text="O retirante seguiu pela estrada.",
        translated_text="The retirante—a drought-displaced refugee—kept walking.",
    )
    codes = {item["code"] for item in run_preflight(contextualized)}
    assert "UNDERLOCALIZATION" not in codes


def test_preflight_detects_forbidden_term_child_register_anachronism_symbol_drift_and_zh_spacing():
    from translation.cultural_episteme import run_preflight

    term_request = _request(
        source_text="Levaram-nos ao Curral do Governo.",
        translated_text="They took us to the Government Cattle Pen.",
        terminology_graph={
            "graph_id": "molambudos-terms",
            "revision": "7",
            "concepts": [
                {
                    "source_term": "Curral do Governo",
                    "preferred_en": "Government Concentration Camp",
                    "forbidden_translations": ["Government Cattle Pen", "Government Corral"],
                }
            ],
        },
        cultural_dossier={
            **_request()["cultural_dossier"],
            "anachronism_markers": ["post-traumatic stress disorder"],
        },
        previous_translation_decisions=[
            {"source_term": "vala", "target_term": "pit", "symbolic": True}
        ],
    )
    codes = {item["code"] for item in run_preflight(term_request)}
    assert "TERM_CONFLICT" in codes

    child_request = _request(
        source_text="Eu tava com medo.",
        translated_text="Notwithstanding the circumstances, I experienced apprehension.",
    )
    child_codes = {item["code"] for item in run_preflight(child_request)}
    assert {"VOICE_SHIFT", "REGISTER_SHIFT"} & child_codes

    anachronism_request = _request(
        source_text="Chamaram aquilo de nervos.",
        translated_text="They diagnosed post-traumatic stress disorder.",
        cultural_dossier={
            **_request()["cultural_dossier"],
            "anachronism_markers": ["post-traumatic stress disorder"],
        },
    )
    assert "ANACHRONISM" in {
        item["code"] for item in run_preflight(anachronism_request)
    }

    symbol_request = _request(
        source_text="A vala tinha fome.",
        translated_text="The trench was hungry.",
        previous_translation_decisions=[
            {"source_term": "vala", "target_term": "pit", "symbolic": True}
        ],
    )
    assert "SYMBOL_DRIFT" in {item["code"] for item in run_preflight(symbol_request)}

    zh_request = _request(
        target_language="zh-CN",
        translated_text="饥 饿 把 我 们 赶 出 帐 篷。",
        cultural_dossier={
            **_request()["cultural_dossier"],
            "target_variety": "简体中文（中国大陆）",
        },
    )
    assert "TARGET_VARIETY_USAGE_RISK" in {
        item["code"] for item in run_preflight(zh_request)
    }


def test_terminology_delta_is_versioned_proposed_idempotent_and_serializable():
    from translation.cultural_episteme import build_terminology_delta

    concept = {
        "source_term": "Curral do Governo",
        "entity_type": "historical_institution",
        "preferred_en": "Government Concentration Camp",
        "preferred_zh_cn": "政府集中收容营",
        "preserve_portuguese": True,
        "first_occurrence_note": True,
        "forbidden_translations": ["Government Corral", "Government Cattle Pen"],
        "historical_context": {"period": "1915", "location": "Ceará"},
    }
    request = _request()
    first = build_terminology_delta(request, concept, "evitar leitura animalizante literal")
    second = build_terminology_delta(request, concept, "evitar leitura animalizante literal")
    assert first == second
    assert first["operation"] == "propose_upsert"
    assert first["approval_state"] == "proposed"
    assert first["base_graph_id"] == "molambudos-terms"
    assert first["base_revision"] == "7"
    assert first["delta_id"] == first["idempotency_key"]
    json.dumps(first, ensure_ascii=False)


def test_stage_adapter_is_fail_closed_with_fake_executor():
    from translation.cultural_episteme import CulturalEpistemeStage

    stage = CulturalEpistemeStage(lambda _request: _assessment())
    result = stage.run(_request())
    assert result["gate"]["release_gate"] == "blocked"
    assert result["assessment"]["analysis_status"] == "complete"

    broken = CulturalEpistemeStage(lambda _request: {"analysis_status": "approved"})
    failed = broken.run(_request())
    assert failed["assessment"] is None
    assert failed["gate"]["decision"] == "invalid_agent_output"
    assert failed["gate"]["release_gate"] == "blocked"


def test_opencode_generation_and_literary_pipeline_reference_agent():
    from integrations.opencode_cli import build_config

    config = build_config()
    agent = config["agent"]["cultural-episteme-agent"]
    assert agent["mode"] == "subagent"
    assert agent["prompt"] == "{file:./agents/catalog/cultural-episteme-agent.md}"
    assert agent["permission"]["edit"] == "deny"
    assert agent["permission"]["bash"] == "deny"
    assert "model" not in agent
    json.dumps(config, ensure_ascii=False)

    orchestrator = ORCHESTRATOR_PATH.read_text(encoding="utf-8").lower()
    assert "cultural-episteme-agent" in orchestrator
    assert "translationagent" in orchestrator
    assert "backtranslationverifier" in orchestrator
    assert "componentes ainda não implementados" in orchestrator
