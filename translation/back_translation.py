# -*- coding: utf-8 -*-
"""BackTranslationVerifier — verificação determinística de retrotradução.

Compara o original com a retrotradução e aponta divergências observáveis
por regra (números, entidades, negação, pragmática, comprimento e termos
preservados). O verificador nunca aprova: retrotradução limpa não prova
equivalência semântica; divergência é indício para revisão humana.

SPEC-935-R366 / OCB-BACK-TRANSLATION-001.
"""

from __future__ import annotations

import copy
import re
import unicodedata
from typing import Any, Dict, List, Mapping

from translation.cultural_episteme import ContractError

SCHEMA_VERSION = "1.0.0"

DISCLAIMER = (
    "Verificação determinística de retrotradução: aponta divergências "
    "observáveis por regra. Retrotradução sem achados NÃO PROVA equivalência "
    "semântica nem qualidade da tradução; decisões finais são humanas."
)

_NEGATORS = ("nao", "nunca", "nada", "ninguem", "nem", "jamais", "sem")

_LENGTH_RATIO_MIN = 0.5
_LENGTH_RATIO_MAX = 2.0

_PRAGMATIC_PATTERNS = (
    ("?", re.compile(r"[?？]")),
    ("!", re.compile(r"[!！]")),
    ("...", re.compile(r"\.\.\.|…+")),
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


def _numbers(text: str) -> List[str]:
    return re.findall(r"\d+(?:[.,]\d+)*", text)


def _negator_count(text: str) -> int:
    tokens = re.findall(r"[a-z0-9]+", _norm(text))
    return sum(1 for t in tokens if t in _NEGATORS)


def _non_empty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} deve ser texto não vazio.")
    return value.strip()


def _finding(code: str, severity: str, detail: str) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "code": code,
        "severity": severity,
        "detail": detail,
        "requires_human_review": True,
    }


_REQUIRED = (
    "schema_version", "review_id", "segment_id", "source_text",
    "back_translated_text", "source_language", "pivot_language",
    "declared_entities", "glossary_terms", "provenance",
)


def verify(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Verifica um ciclo de retrotradução. Determinístico e fail-closed."""
    if not isinstance(payload, Mapping):
        raise ContractError("payload deve ser um mapeamento.")
    envelope = copy.deepcopy(dict(payload))
    missing = [f for f in _REQUIRED if f not in envelope]
    if missing:
        raise ContractError(f"payload sem: {', '.join(missing)}.")
    if envelope["schema_version"] != SCHEMA_VERSION:
        raise ContractError("schema_version incompatível.")
    for field in ("review_id", "segment_id", "source_language", "pivot_language"):
        envelope[field] = _non_empty_text(envelope[field], field)
    if not isinstance(envelope["declared_entities"], list):
        raise ContractError("declared_entities deve ser lista.")
    if not isinstance(envelope["glossary_terms"], list):
        raise ContractError("glossary_terms deve ser lista.")
    provenance = envelope["provenance"]
    if not isinstance(provenance, list) or not provenance:
        raise ContractError("provenance deve ser lista não vazia.")

    source = envelope["source_text"]
    back = envelope["back_translated_text"]

    def _envelope_out(status: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        high = any(f["severity"] == "high" for f in findings)
        return {
            "schema_version": SCHEMA_VERSION,
            "review_id": envelope["review_id"],
            "segment_id": envelope["segment_id"],
            "analysis_status": status,
            "findings": findings,
            "human_gate": "required" if high else "recommended",
            "disclaimer": DISCLAIMER,
        }

    if (
        not isinstance(source, str) or not source.strip()
        or not isinstance(back, str) or not back.strip()
    ):
        return _envelope_out("insufficient_context", [])

    findings: List[Dict[str, Any]] = []

    # 1. números/datas devem sobreviver ao ciclo (nas duas direções)
    src_numbers, back_numbers = _numbers(source), _numbers(back)
    for number in src_numbers:
        if number not in back_numbers:
            findings.append(_finding(
                "CULTURAL_LOSS", "high",
                f"número/data {number!r} presente no original e ausente da retrotradução",
            ))
    for number in back_numbers:
        if number not in src_numbers:
            findings.append(_finding(
                "CULTURAL_LOSS", "high",
                f"número/data {number!r} surgiu na retrotradução sem estar no original",
            ))

    # 2. entidades declaradas
    for entity in envelope["declared_entities"]:
        if _contains(source, str(entity)) and not _contains(back, str(entity)):
            findings.append(_finding(
                "CULTURAL_LOSS", "high",
                f"entidade declarada {entity!r} ausente da retrotradução",
            ))

    # 3. polaridade de negação (tolerância ±1)
    src_neg, back_neg = _negator_count(source), _negator_count(back)
    if abs(src_neg - back_neg) > 1:
        findings.append(_finding(
            "PRAGMATIC_FAILURE", "high",
            f"negadores: original={src_neg}, retrotradução={back_neg}",
        ))

    # 4. marcas pragmáticas
    for label, pattern in _PRAGMATIC_PATTERNS:
        src_count = len(pattern.findall(source))
        back_count = len(pattern.findall(back))
        if src_count != back_count:
            findings.append(_finding(
                "PRAGMATIC_FAILURE", "medium",
                f"marcas pragmáticas {label!r}: original={src_count}, "
                f"retrotradução={back_count}",
            ))

    # 5. razão de comprimento
    ratio = len(back.strip()) / max(1, len(source.strip()))
    if ratio < _LENGTH_RATIO_MIN or ratio > _LENGTH_RATIO_MAX:
        findings.append(_finding(
            "CULTURAL_LOSS", "medium",
            f"razão de comprimento retrotradução/original = {ratio:.2f} "
            f"(fora de [{_LENGTH_RATIO_MIN}, {_LENGTH_RATIO_MAX}])",
        ))

    # 6. termos preservados do grafo
    for term in envelope["glossary_terms"]:
        if not isinstance(term, Mapping):
            raise ContractError("glossary_terms deve conter mapeamentos.")
        source_term = term.get("source_term")
        if not source_term:
            raise ContractError("glossary_terms[*].source_term obrigatório.")
        if (
            bool(term.get("preserve_portuguese"))
            and _contains(source, source_term)
            and not _contains(back, source_term)
        ):
            findings.append(_finding(
                "TERM_CONFLICT", "high",
                f"termo preservado {source_term!r} não sobreviveu ao ciclo",
            ))

    return _envelope_out("complete", findings)
