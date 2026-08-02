# -*- coding: utf-8 -*-
"""AuthorVoiceGuardian — guarda de voz autoral em tradução.

Detecta, por regras observáveis, indícios de apagamento de marcadores
regionais/orais, modernismos proibidos e deriva de registro pragmático.
Instrumento heurístico: não mede fidelidade de voz; aponta indícios e
exige revisão humana para alto risco. Ausência de achado significa apenas
que nenhum indício foi observado pelas regras no escopo examinado.

SPEC-935-R365 / OCB-AUTHOR-VOICE-001.
"""

from __future__ import annotations

import copy
import re
import unicodedata
from typing import Any, Dict, List, Mapping

from translation.cultural_episteme import ContractError

SCHEMA_VERSION = "1.0.0"

_KINDS = frozenset({"regionalism", "orality", "symbol", "institution"})
_STRATEGIES = frozenset({"preserve", "gloss", "adapt"})
_RENDERING_LANGS = ("en", "zh_cn")

DISCLAIMER = (
    "Instrumento heurístico de apoio editorial: aponta indícios observáveis "
    "por regra, não mede fidelidade de voz. Ausência de achado não é "
    "atestado de preservação; decisões finais são humanas."
)


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _contains(text: str, term: str) -> bool:
    norm_text, norm_term = _norm(text), _norm(term)
    if re.search(r"[a-z0-9]", norm_term):
        return re.search(
            rf"(?<![a-z0-9]){re.escape(norm_term)}(?![a-z0-9])", norm_text
        ) is not None
    return norm_term in norm_text


def _non_empty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} deve ser texto não vazio.")
    return value.strip()


def _rendering_lang(target_language: str) -> str:
    lang = target_language.lower()
    if lang.startswith("zh"):
        return "zh_cn"
    return "en"


def validate_voice_profile(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Valida o perfil de voz; qualquer inconsistência falha fechado."""
    if not isinstance(payload, Mapping):
        raise ContractError("perfil deve ser um mapeamento.")
    profile = copy.deepcopy(dict(payload))
    required = (
        "schema_version", "profile_id", "work_id", "register",
        "voice_markers", "forbidden_modernisms", "provenance",
    )
    missing = [f for f in required if f not in profile]
    if missing:
        raise ContractError(f"perfil sem: {', '.join(missing)}.")
    if profile["schema_version"] != SCHEMA_VERSION:
        raise ContractError("schema_version do perfil incompatível.")
    for field in ("profile_id", "work_id", "register"):
        profile[field] = _non_empty_text(profile[field], field)

    markers = profile["voice_markers"]
    if not isinstance(markers, list) or not markers:
        raise ContractError("voice_markers deve ser lista não vazia.")
    for i, marker in enumerate(markers):
        if not isinstance(marker, Mapping):
            raise ContractError(f"voice_markers[{i}] deve ser mapeamento.")
        marker = dict(marker)
        marker["marker"] = _non_empty_text(marker.get("marker"), f"voice_markers[{i}].marker")
        kind = marker.get("kind")
        if kind not in _KINDS:
            raise ContractError(f"voice_markers[{i}].kind inválido: {kind!r}.")
        strategy = marker.get("strategy")
        if strategy not in _STRATEGIES:
            raise ContractError(f"voice_markers[{i}].strategy inválida: {strategy!r}.")
        if strategy == "adapt":
            renderings = marker.get("approved_renderings")
            if not isinstance(renderings, Mapping) or not any(
                isinstance(renderings.get(lang), list) and renderings.get(lang)
                for lang in _RENDERING_LANGS
            ):
                raise ContractError(
                    f"voice_markers[{i}]: strategy=adapt exige "
                    "approved_renderings não vazio por idioma."
                )
        markers[i] = marker

    if not isinstance(profile["forbidden_modernisms"], list):
        raise ContractError("forbidden_modernisms deve ser lista.")
    provenance = profile["provenance"]
    if not isinstance(provenance, list) or not provenance:
        raise ContractError("provenance deve ser lista não vazia.")
    return profile


def _finding(code: str, severity: str, marker: str, detail: str) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "code": code,
        "severity": severity,
        "marker": marker,
        "detail": detail,
        "requires_human_review": True,
    }


_PRAGMATIC_PATTERNS = (
    ("?", re.compile(r"[?？]")),
    ("!", re.compile(r"[!！]")),
    ("...", re.compile(r"\.\.\.|…+")),
)


def review_segment(
    profile_payload: Mapping[str, Any],
    source_text: str,
    translated_text: str,
    target_language: str,
) -> Dict[str, Any]:
    """Revisa um segmento contra o perfil de voz. Determinístico."""
    profile = validate_voice_profile(profile_payload)

    def _envelope(status: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        high = any(f["severity"] == "high" for f in findings)
        return {
            "schema_version": SCHEMA_VERSION,
            "profile_id": profile["profile_id"],
            "analysis_status": status,
            "findings": findings,
            "human_gate": "required" if high else "recommended",
            "disclaimer": DISCLAIMER,
        }

    if (
        not isinstance(source_text, str) or not source_text.strip()
        or not isinstance(translated_text, str) or not translated_text.strip()
    ):
        return _envelope("insufficient_context", [])

    findings: List[Dict[str, Any]] = []
    lang_key = _rendering_lang(target_language)

    for marker in profile["voice_markers"]:
        term = marker["marker"]
        if not _contains(source_text, term):
            continue
        strategy = marker["strategy"]
        if strategy == "preserve" and not _contains(translated_text, term):
            findings.append(_finding(
                "VOICE_SHIFT", "high", term,
                "marcador com strategy=preserve ausente do texto-alvo",
            ))
        elif strategy == "adapt":
            renderings = marker.get("approved_renderings", {}).get(lang_key, [])
            if renderings and not any(
                _contains(translated_text, r) for r in renderings
            ):
                findings.append(_finding(
                    "VOICE_SHIFT", "high", term,
                    "nenhuma tradução aprovada do marcador presente no alvo",
                ))
        elif strategy == "gloss" and not _contains(translated_text, term):
            findings.append(_finding(
                "VOICE_SHIFT", "medium", term,
                "marcador com strategy=gloss ausente do alvo (glosa esperada)",
            ))

    for modernism in profile["forbidden_modernisms"]:
        if _contains(translated_text, modernism):
            findings.append(_finding(
                "ANACHRONISM", "high", modernism,
                "modernismo proibido pelo perfil presente no texto-alvo",
            ))

    for label, pattern in _PRAGMATIC_PATTERNS:
        src_count = len(pattern.findall(source_text))
        dst_count = len(pattern.findall(translated_text))
        if src_count != dst_count:
            findings.append(_finding(
                "REGISTER_SHIFT", "medium", label,
                f"marcas pragmáticas {label!r}: fonte={src_count}, alvo={dst_count}",
            ))

    return _envelope("complete", findings)
