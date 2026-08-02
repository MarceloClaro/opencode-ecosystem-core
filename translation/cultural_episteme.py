# -*- coding: utf-8 -*-
"""CulturalEpistemeAgent — contrato, preflight e gate fail-closed.

Este módulo não pretende decidir equivalência cultural ou substituir revisão
humana. Ele valida envelopes estruturados, executa regras observáveis de
preflight e mantém o release bloqueado até revisão humana documentada.

SPEC-935-R359 / OCB-CULTURAL-EPISTEME-001.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any


SCHEMA_VERSION = "1.0.0"

ISSUE_CODES = frozenset(
    {
        "LITERALISM",
        "CULTURAL_LOSS",
        "ANACHRONISM",
        "VOICE_SHIFT",
        "REGISTER_SHIFT",
        "SYMBOL_DRIFT",
        "TERM_CONFLICT",
        "PRAGMATIC_FAILURE",
        "CJK_UNNATURALNESS",
        "TARGET_VARIETY_USAGE_RISK",
        "OVERLOCALIZATION",
        "UNDERLOCALIZATION",
        "ETHICAL_RISK",
        "HISTORICAL_SOURCE_GAP",
        "HISTORICAL_CONTESTATION",
        "EXOTICIZATION_RISK",
        "DOMESTICATION_ERASURE_RISK",
        "RELAY_TRANSLATION_RISK",
        "REPRESENTATION_HARM_RISK",
        "UNCLASSIFIED_RISK",
    }
)

_SEVERITIES = frozenset({"low", "medium", "high", "critical"})
_EVIDENCE_STRENGTHS = frozenset(
    {"unknown", "weak", "moderate", "strong", "contested"}
)
_DETECTORS = frozenset({"rule", "agent", "human"})
_ANALYSIS_STATUSES = frozenset(
    {"complete", "insufficient_context", "invalid_agent_output"}
)
_EVIDENCE_SUFFICIENCY = frozenset(
    {"insufficient", "partial", "substantial", "contested"}
)
_HIGH_RISK_CODES = frozenset(
    {
        "ANACHRONISM",
        "TERM_CONFLICT",
        "ETHICAL_RISK",
        "HISTORICAL_SOURCE_GAP",
        "HISTORICAL_CONTESTATION",
        "RELAY_TRANSLATION_RISK",
        "REPRESENTATION_HARM_RISK",
        "UNCLASSIFIED_RISK",
    }
)
_BCP47_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
_CJK_SPACING_RE = re.compile(r"[\u3400-\u9fff]\s+[\u3400-\u9fff]")

_REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "review_id",
    "segment_id",
    "source_language",
    "target_language",
    "source_text",
    "translated_text",
    "author_voice_profile",
    "terminology_graph",
    "historical_context",
    "cultural_dossier",
    "previous_translation_decisions",
)

_REQUIRED_OUTPUT_FIELDS = (
    "schema_version",
    "analysis_status",
    "source_language",
    "target_language",
    "source_excerpt",
    "translated_excerpt",
    "candidate_concerns",
    "cultural_context",
    "alternatives",
    "conditional_preference",
    "heuristic_signals",
    "process_checks",
    "evidence_sufficiency",
    "uncertainty_reasons",
    "terminology_graph_updates",
    "human_review_required",
    "release_gate",
    "missing_data",
    "limits",
)


class ContractError(ValueError):
    """Indica violação do contrato R359; sempre deve resultar em bloqueio."""


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{field} deve ser um objeto.")
    return value


def _list(value: Any, field: str) -> list[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ContractError(f"{field} deve ser uma lista.")
    return list(value)


def _non_empty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} deve ser texto não vazio.")
    return value.strip()


def _language(value: Any, field: str) -> str:
    language = _non_empty_text(value, field)
    if not _BCP47_RE.fullmatch(language):
        raise ContractError(f"{field} deve usar etiqueta BCP-47.")
    return language


def _bounded_signal(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{field} deve ser número entre 0 e 1.")
    signal = float(value)
    if not math.isfinite(signal) or not 0.0 <= signal <= 1.0:
        raise ContractError(f"{field} deve ser finito e estar entre 0 e 1.")
    return signal


def _non_negative_count(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError(f"{field} deve ser inteiro não negativo.")
    return value


def _validate_provenance(container: Mapping[str, Any], field: str) -> None:
    provenance = _list(container.get("provenance"), f"{field}.provenance")
    if not provenance:
        raise ContractError(f"{field}.provenance não pode ser vazia.")
    for index, item in enumerate(provenance):
        entry = _mapping(item, f"{field}.provenance[{index}]")
        _non_empty_text(entry.get("source"), f"{field}.provenance[{index}].source")
        _non_empty_text(
            entry.get("limitations"),
            f"{field}.provenance[{index}].limitations",
        )


def validate_review_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Valida e copia uma solicitação de revisão sem mutar a entrada."""

    request = copy.deepcopy(dict(_mapping(payload, "request")))
    missing = [field for field in _REQUIRED_REQUEST_FIELDS if field not in request]
    if missing:
        raise ContractError(f"Campos obrigatórios ausentes: {', '.join(missing)}.")
    if request["schema_version"] != SCHEMA_VERSION:
        raise ContractError("schema_version incompatível.")
    for field in ("review_id", "segment_id", "source_text", "translated_text"):
        request[field] = _non_empty_text(request[field], field)
    request["source_language"] = _language(
        request["source_language"], "source_language"
    )
    request["target_language"] = _language(
        request["target_language"], "target_language"
    )
    for field in (
        "author_voice_profile",
        "terminology_graph",
        "historical_context",
        "cultural_dossier",
    ):
        request[field] = copy.deepcopy(dict(_mapping(request[field], field)))
    request["previous_translation_decisions"] = _list(
        request["previous_translation_decisions"],
        "previous_translation_decisions",
    )
    graph = request["terminology_graph"]
    _non_empty_text(graph.get("graph_id"), "terminology_graph.graph_id")
    _non_empty_text(graph.get("revision"), "terminology_graph.revision")
    concepts = graph.get("concepts", [])
    graph["concepts"] = _list(concepts, "terminology_graph.concepts")
    _validate_provenance(request["historical_context"], "historical_context")
    _validate_provenance(request["cultural_dossier"], "cultural_dossier")
    return request


def _validate_span(value: Any, field: str) -> list[int]:
    span = _list(value, field)
    if len(span) != 2 or any(
        isinstance(item, bool) or not isinstance(item, int) or item < 0
        for item in span
    ):
        raise ContractError(f"{field} deve conter dois inteiros não negativos.")
    if span[1] < span[0]:
        raise ContractError(f"{field} possui fim anterior ao início.")
    return span


def _normalize_concern(value: Any, index: int) -> dict[str, Any]:
    concern = copy.deepcopy(dict(_mapping(value, f"candidate_concerns[{index}]")))
    required = (
        "code",
        "severity",
        "evidence_strength",
        "source_span",
        "target_span",
        "detector",
        "evidence",
        "rationale",
    )
    missing = [field for field in required if field not in concern]
    if missing:
        raise ContractError(
            f"candidate_concerns[{index}] sem: {', '.join(missing)}."
        )
    code = _non_empty_text(concern["code"], f"candidate_concerns[{index}].code")
    severity = _non_empty_text(
        concern["severity"], f"candidate_concerns[{index}].severity"
    ).lower()
    if severity not in _SEVERITIES:
        raise ContractError(f"Severidade desconhecida: {severity}.")
    if code not in ISSUE_CODES:
        concern["original_code"] = code
        code = "UNCLASSIFIED_RISK"
        severity = "critical" if severity == "critical" else "high"
    concern["code"] = code
    concern["severity"] = severity
    strength = _non_empty_text(
        concern["evidence_strength"],
        f"candidate_concerns[{index}].evidence_strength",
    ).lower()
    if strength not in _EVIDENCE_STRENGTHS:
        raise ContractError(f"Força de evidência desconhecida: {strength}.")
    concern["evidence_strength"] = strength
    detector = _non_empty_text(
        concern["detector"], f"candidate_concerns[{index}].detector"
    ).lower()
    if detector not in _DETECTORS:
        raise ContractError(f"Detector desconhecido: {detector}.")
    concern["detector"] = detector
    concern["source_span"] = _validate_span(
        concern["source_span"], f"candidate_concerns[{index}].source_span"
    )
    concern["target_span"] = _validate_span(
        concern["target_span"], f"candidate_concerns[{index}].target_span"
    )
    concern["evidence"] = _non_empty_text(
        concern["evidence"], f"candidate_concerns[{index}].evidence"
    )
    concern["rationale"] = _non_empty_text(
        concern["rationale"], f"candidate_concerns[{index}].rationale"
    )
    return concern


def _validate_terminology_delta(delta: Any, field: str) -> dict[str, Any]:
    item = copy.deepcopy(dict(_mapping(delta, field)))
    required = (
        "delta_id",
        "idempotency_key",
        "base_graph_id",
        "base_revision",
        "operation",
        "approval_state",
        "source_term",
        "entity_type",
        "rationale",
        "provenance",
    )
    missing = [name for name in required if name not in item]
    if missing:
        raise ContractError(f"{field} sem: {', '.join(missing)}.")
    for name in required:
        if name != "provenance":
            item[name] = _non_empty_text(item[name], f"{field}.{name}")
    if item["operation"] != "propose_upsert":
        raise ContractError(f"{field}.operation deve ser propose_upsert.")
    if item["approval_state"] != "proposed":
        raise ContractError(f"{field}.approval_state deve ser proposed.")
    if item["delta_id"] != item["idempotency_key"]:
        raise ContractError(f"{field} possui chave de idempotência divergente.")
    item["provenance"] = _list(item["provenance"], f"{field}.provenance")
    if not item["provenance"]:
        raise ContractError(f"{field}.provenance não pode ser vazia.")
    return item


def validate_agent_output(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Valida a avaliação candidata produzida pelo agente sem confiar em status."""

    assessment = copy.deepcopy(dict(_mapping(payload, "assessment")))
    missing = [field for field in _REQUIRED_OUTPUT_FIELDS if field not in assessment]
    if missing:
        raise ContractError(f"Saída obrigatória incompleta: {', '.join(missing)}.")
    if assessment["schema_version"] != SCHEMA_VERSION:
        raise ContractError("schema_version da saída incompatível.")
    status = _non_empty_text(assessment["analysis_status"], "analysis_status")
    if status not in _ANALYSIS_STATUSES:
        raise ContractError(f"analysis_status inválido: {status}.")
    assessment["analysis_status"] = status
    assessment["source_language"] = _language(
        assessment["source_language"], "source_language"
    )
    assessment["target_language"] = _language(
        assessment["target_language"], "target_language"
    )
    assessment["source_excerpt"] = _non_empty_text(
        assessment["source_excerpt"], "source_excerpt"
    )
    assessment["translated_excerpt"] = _non_empty_text(
        assessment["translated_excerpt"], "translated_excerpt"
    )

    concerns = _list(assessment["candidate_concerns"], "candidate_concerns")
    assessment["candidate_concerns"] = [
        _normalize_concern(value, index) for index, value in enumerate(concerns)
    ]
    assessment["cultural_context"] = copy.deepcopy(
        dict(_mapping(assessment["cultural_context"], "cultural_context"))
    )
    alternatives = _list(assessment["alternatives"], "alternatives")
    normalized_alternatives: list[dict[str, Any]] = []
    for index, value in enumerate(alternatives):
        alternative = copy.deepcopy(
            dict(_mapping(value, f"alternatives[{index}]"))
        )
        alternative["text"] = _non_empty_text(
            alternative.get("text"), f"alternatives[{index}].text"
        )
        alternative["rationale"] = _non_empty_text(
            alternative.get("rationale"), f"alternatives[{index}].rationale"
        )
        alternative["risks"] = _list(
            alternative.get("risks", []), f"alternatives[{index}].risks"
        )
        normalized_alternatives.append(alternative)
    assessment["alternatives"] = normalized_alternatives
    if assessment["conditional_preference"] is not None:
        preference = copy.deepcopy(
            dict(_mapping(assessment["conditional_preference"], "conditional_preference"))
        )
        preference["text"] = _non_empty_text(
            preference.get("text"), "conditional_preference.text"
        )
        preference["rationale"] = _non_empty_text(
            preference.get("rationale"), "conditional_preference.rationale"
        )
        preference["conditions"] = _list(
            preference.get("conditions", []), "conditional_preference.conditions"
        )
        assessment["conditional_preference"] = preference

    signals = copy.deepcopy(
        dict(_mapping(assessment["heuristic_signals"], "heuristic_signals"))
    )
    for name in (
        "symbol_consistency",
        "cultural_fidelity",
        "author_voice_similarity",
    ):
        if name not in signals:
            raise ContractError(f"heuristic_signals.{name} ausente.")
        signals[name] = _bounded_signal(signals[name], f"heuristic_signals.{name}")
    assessment["heuristic_signals"] = signals

    checks = copy.deepcopy(dict(_mapping(assessment["process_checks"], "process_checks")))
    checks["critical_omissions_identified"] = _non_negative_count(
        checks.get("critical_omissions_identified"),
        "process_checks.critical_omissions_identified",
    )
    checks["unresolved_term_conflicts"] = _non_negative_count(
        checks.get("unresolved_term_conflicts"),
        "process_checks.unresolved_term_conflicts",
    )
    if not isinstance(checks.get("back_translation_used"), bool):
        raise ContractError("process_checks.back_translation_used deve ser booleano.")
    assessment["process_checks"] = checks

    sufficiency = _non_empty_text(
        assessment["evidence_sufficiency"], "evidence_sufficiency"
    )
    if sufficiency not in _EVIDENCE_SUFFICIENCY:
        raise ContractError(f"evidence_sufficiency inválida: {sufficiency}.")
    assessment["evidence_sufficiency"] = sufficiency
    for field in ("uncertainty_reasons", "missing_data", "limits"):
        assessment[field] = _list(assessment[field], field)
    updates = _list(
        assessment["terminology_graph_updates"], "terminology_graph_updates"
    )
    assessment["terminology_graph_updates"] = [
        _validate_terminology_delta(value, f"terminology_graph_updates[{index}]")
        for index, value in enumerate(updates)
    ]
    if not isinstance(assessment["human_review_required"], bool):
        raise ContractError("human_review_required deve ser booleano.")
    if assessment["release_gate"] != "blocked":
        raise ContractError("release_gate deve permanecer blocked.")

    high_risk = any(
        concern["severity"] in {"high", "critical"}
        or concern["code"] in _HIGH_RISK_CODES
        for concern in assessment["candidate_concerns"]
    )
    if (high_risk or status != "complete") and not assessment["human_review_required"]:
        raise ContractError("Alto risco ou contexto insuficiente exige revisão humana.")
    # R359: toda saída editorial permanece candidata à revisão humana.
    if not assessment["human_review_required"]:
        raise ContractError("A publicação exige revisão humana documentada.")
    return assessment


def _span(text: str, term: str) -> list[int]:
    start = text.casefold().find(term.casefold())
    return [0, 0] if start < 0 else [start, start + len(term)]


def _concern(
    code: str,
    severity: str,
    source: str,
    target: str,
    source_term: str,
    target_term: str,
    evidence: str,
    rationale: str,
    *,
    strength: str = "moderate",
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "evidence_strength": strength,
        "source_span": _span(source, source_term),
        "target_span": _span(target, target_term),
        "detector": "rule",
        "evidence": evidence,
        "rationale": rationale,
    }


def run_preflight(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Executa detectores observáveis; resultados são indícios, não veredictos."""

    request = validate_review_request(payload)
    source = request["source_text"]
    target = request["translated_text"]
    source_lower = source.casefold()
    target_lower = target.casefold()
    concerns: list[dict[str, Any]] = []

    if "retirant" in source_lower and "migrant" in target_lower:
        contextualizers = (
            "drought",
            "refugee",
            "displaced",
            "retirante",
            "sertão",
            "ceará",
        )
        if not any(token in target_lower for token in contextualizers):
            concerns.append(
                _concern(
                    "CULTURAL_LOSS",
                    "medium",
                    source,
                    target,
                    "retirant",
                    "migrant",
                    "migrant aparece sem marcador de seca ou deslocamento histórico",
                    "o equivalente isolado pode apagar a condição histórica do retirante",
                )
            )

    if "tira a gente" in source_lower and "takes us out" in target_lower:
        concerns.append(
            _concern(
                "LITERALISM",
                "medium",
                source,
                target,
                "tira a gente",
                "takes us out",
                "correspondência verbal superficial detectada",
                "a força causal e a oralidade podem não ter sido preservadas",
            )
        )

    graph = request["terminology_graph"]
    for concept in graph.get("concepts", []):
        if not isinstance(concept, Mapping):
            continue
        source_term = str(concept.get("source_term", "")).strip()
        if not source_term or source_term.casefold() not in source_lower:
            continue
        for forbidden in concept.get("forbidden_translations", []):
            forbidden_text = str(forbidden).strip()
            if forbidden_text and forbidden_text.casefold() in target_lower:
                concerns.append(
                    _concern(
                        "TERM_CONFLICT",
                        "high",
                        source,
                        target,
                        source_term,
                        forbidden_text,
                        f"tradução proibida pelo snapshot do grafo: {forbidden_text}",
                        "a decisão terminológica humana anterior diverge do segmento",
                        strength="strong",
                    )
                )

    voice = request["author_voice_profile"]
    age = str(voice.get("narrator_age", "")).casefold()
    register = str(voice.get("register", "")).casefold()
    academic_markers = (
        "notwithstanding",
        "inasmuch as",
        "henceforth",
        "therefore",
        "experienced apprehension",
    )
    marker = next((item for item in academic_markers if item in target_lower), None)
    if marker and (
        age in {"child", "criança", "menino", "menina"} or "oral" in register
    ):
        concerns.extend(
            [
                _concern(
                    "VOICE_SHIFT",
                    "high",
                    source,
                    target,
                    source,
                    marker,
                    f"marcador acadêmico detectado em voz infantil/oral: {marker}",
                    "o narrador pode ter adquirido maturidade discursiva indevida",
                ),
                _concern(
                    "REGISTER_SHIFT",
                    "medium",
                    source,
                    target,
                    source,
                    marker,
                    f"registro-alvo contém {marker}",
                    "o nível de formalidade diverge do perfil de voz fornecido",
                ),
            ]
        )

    for marker_value in request["cultural_dossier"].get(
        "anachronism_markers", []
    ):
        marker_text = (
            str(marker_value.get("term", ""))
            if isinstance(marker_value, Mapping)
            else str(marker_value)
        ).strip()
        if marker_text and marker_text.casefold() in target_lower:
            concerns.append(
                _concern(
                    "ANACHRONISM",
                    "high",
                    source,
                    target,
                    source,
                    marker_text,
                    f"termo marcado pelo dossiê como potencialmente anacrônico: {marker_text}",
                    "a atualização silenciosa pode alterar a episteme histórica",
                    strength="strong",
                )
            )

    source_hedges = ("como se", "parecia", "parece", "talvez", "quem sabe")
    target_hedges = ("as if", "seemed", "seems", "perhaps", "maybe", "like")
    source_hedge = next((item for item in source_hedges if item in source_lower), None)
    if source_hedge and not any(item in target_lower for item in target_hedges):
        concerns.append(
            _concern(
                "PRAGMATIC_FAILURE",
                "medium",
                source,
                target,
                source_hedge,
                target,
                "marcador de hipótese/metáfora presente na fonte e ausente no alvo",
                "a tradução pode ter convertido sugestão em afirmação",
            )
        )

    threat_markers = (
        "você é o próximo",
        "você será o próximo",
        "vai morrer",
        "não vai escapar",
    )
    target_weakening = ("may", "might", "perhaps", "maybe", "could be")
    threat = next((item for item in threat_markers if item in source_lower), None)
    weakening = next((item for item in target_weakening if item in target_lower), None)
    if threat and weakening:
        concerns.append(
            _concern(
                "PRAGMATIC_FAILURE",
                "high",
                source,
                target,
                threat,
                weakening,
                f"ameaça direta modalizada por {weakening}",
                "a função de ameaça pode ter sido enfraquecida",
            )
        )

    for decision in request["previous_translation_decisions"]:
        if not isinstance(decision, Mapping) or not decision.get("symbolic"):
            continue
        source_term = str(decision.get("source_term", "")).strip()
        target_term = str(decision.get("target_term", "")).strip()
        if (
            source_term
            and target_term
            and source_term.casefold() in source_lower
            and target_term.casefold() not in target_lower
        ):
            concerns.append(
                _concern(
                    "SYMBOL_DRIFT",
                    "high",
                    source,
                    target,
                    source_term,
                    target,
                    f"símbolo aprovado {source_term} não usa {target_term} no alvo",
                    "a recorrência simbólica diverge da decisão humana anterior",
                    strength="strong",
                )
            )

    if request["target_language"].casefold().startswith("zh") and _CJK_SPACING_RE.search(target):
        match = _CJK_SPACING_RE.search(target)
        assert match is not None
        concerns.append(
            _concern(
                "TARGET_VARIETY_USAGE_RISK",
                "medium",
                source,
                target,
                source,
                match.group(0),
                "espaçamento artificial entre ideogramas detectado",
                "o padrão pode ser tipograficamente artificial na variante-alvo",
            )
        )

    pivot = request["cultural_dossier"].get("pivot_language")
    if pivot:
        concerns.append(
            _concern(
                "RELAY_TRANSLATION_RISK",
                "high",
                source,
                target,
                source,
                target,
                f"dossiê registra língua-pivô: {pivot}",
                "a versão precisa de cotejo humano direto entre fonte e alvo",
            )
        )

    return sorted(
        concerns,
        key=lambda item: (
            item["code"],
            item["source_span"],
            item["target_span"],
            item["evidence"],
        ),
    )


def evaluate_gate(
    request_payload: Mapping[str, Any],
    assessment_payload: Mapping[str, Any],
    preflight: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Deriva decisão editorial; nunca abre o release automaticamente."""

    validate_review_request(request_payload)
    assessment = validate_agent_output(assessment_payload)
    preflight_items = [copy.deepcopy(dict(item)) for item in (preflight or [])]
    reasons: list[str] = []

    if assessment["analysis_status"] != "complete":
        decision = assessment["analysis_status"]
        reasons.append("análise incompleta ou saída inválida")
    else:
        all_concerns = assessment["candidate_concerns"] + preflight_items
        high_risk = any(
            item.get("severity") in {"high", "critical"}
            or item.get("code") in _HIGH_RISK_CODES
            for item in all_concerns
        )
        checks = assessment["process_checks"]
        signals = assessment["heuristic_signals"]
        low_signals = (
            signals["symbol_consistency"] < 0.98
            or signals["cultural_fidelity"] < 0.90
            or signals["author_voice_similarity"] < 0.88
        )
        unresolved = (
            checks["critical_omissions_identified"] > 0
            or checks["unresolved_term_conflicts"] > 0
        )
        if high_risk:
            decision = "human_review"
            reasons.append("alerta histórico, ético ou de alta severidade")
        elif all_concerns or low_signals or unresolved:
            decision = "revise"
            reasons.append("há indícios, sinais baixos ou checks não resolvidos")
        else:
            decision = "candidate_for_human_review"
            reasons.append("nenhum indício detectado no escopo; revisão humana continua obrigatória")

    return {
        "decision": decision,
        "release_gate": "blocked",
        "human_review_required": True,
        "reasons": reasons,
        "scores_are_non_authoritative": True,
    }


def build_terminology_delta(
    request_payload: Mapping[str, Any],
    concept_payload: Mapping[str, Any],
    rationale: str,
) -> dict[str, Any]:
    """Gera proposta idempotente; não aplica nem aprova alteração no grafo."""

    request = validate_review_request(request_payload)
    concept = copy.deepcopy(dict(_mapping(concept_payload, "concept")))
    source_term = _non_empty_text(concept.get("source_term"), "concept.source_term")
    entity_type = _non_empty_text(concept.get("entity_type"), "concept.entity_type")
    rationale_text = _non_empty_text(rationale, "rationale")
    if not any(
        isinstance(value, str) and value.strip()
        for key, value in concept.items()
        if key.startswith("preferred_")
    ):
        raise ContractError("concept deve conter ao menos uma tradução preferida.")
    forbidden = _list(
        concept.get("forbidden_translations", []),
        "concept.forbidden_translations",
    )
    canonical = {
        "schema_version": SCHEMA_VERSION,
        "review_id": request["review_id"],
        "segment_id": request["segment_id"],
        "base_graph_id": request["terminology_graph"]["graph_id"],
        "base_revision": request["terminology_graph"]["revision"],
        "operation": "propose_upsert",
        "approval_state": "proposed",
        "source_term": source_term,
        "entity_type": entity_type,
        "preferred_en": concept.get("preferred_en"),
        "preferred_zh_cn": concept.get("preferred_zh_cn"),
        "preserve_portuguese": bool(concept.get("preserve_portuguese", False)),
        "first_occurrence_note": bool(concept.get("first_occurrence_note", False)),
        "forbidden_translations": forbidden,
        "historical_context": copy.deepcopy(concept.get("historical_context", {})),
        "rationale": rationale_text,
        "provenance": copy.deepcopy(request["historical_context"]["provenance"]),
    }
    digest = hashlib.sha256(
        json.dumps(
            canonical,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()[:24]
    delta = {"delta_id": f"ced-{digest}", "idempotency_key": f"ced-{digest}", **canonical}
    return _validate_terminology_delta(delta, "terminology_delta")


class CulturalEpistemeStage:
    """Seam testável para um executor externo de análise cultural.

    O executor pode ser um cliente OpenCode, MCP ou outro transporte futuro.
    Nesta spec ele é apenas uma callable injetável; isso não constitui ponte
    runtime prompt→Python nem integração ponta a ponta.
    """

    def __init__(self, executor: Callable[[Mapping[str, Any]], Mapping[str, Any]]):
        if not callable(executor):
            raise TypeError("executor deve ser callable.")
        self._executor = executor

    @staticmethod
    def _failure(decision: str, reason: str) -> dict[str, Any]:
        return {
            "assessment": None,
            "preflight": [],
            "gate": {
                "decision": decision,
                "release_gate": "blocked",
                "human_review_required": True,
                "reasons": [reason],
                "scores_are_non_authoritative": True,
            },
        }

    def run(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        try:
            request = validate_review_request(payload)
            preflight = run_preflight(request)
        except ContractError as exc:
            return self._failure("invalid_request", str(exc))
        try:
            raw_output = self._executor(copy.deepcopy(request))
            assessment = validate_agent_output(raw_output)
        except Exception as exc:  # transportes e modelos falham fechados
            return self._failure("invalid_agent_output", str(exc))
        gate = evaluate_gate(request, assessment, preflight)
        return {
            "assessment": assessment,
            "preflight": preflight,
            "gate": gate,
        }
