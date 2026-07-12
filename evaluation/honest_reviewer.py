# -*- coding: utf-8 -*-
"""
Honest Evaluation Engine — SPEC-935-R142
========================================
A disciplina antioverclaim como capacidade reutilizável.

Princípios (codificados, não apenas documentados):

  1. **Cobertura ≠ qualidade.** Uma métrica de processo (quantos scanners
     rodaram, quantos eixos foram varridos) NÃO é um veredito de mérito.
  2. **Nota/rótulo de topo exige validação externa.** Sem ela, o teto de
     qualidade é limitado (`INTERNAL_QUALITY_CEILING`) e termos como
     best-seller / obra-prima / Qualis A1 / verified / superhuman / 9.5–10/10
     são tratados como inflação.
  3. **Emitir faixa, não ponto.** O engine devolve uma faixa honesta
     (piso–teto) que expressa a incerteza, em vez de um número inflado.

Reusa (não duplica) a política de
`mci.metacognitive_evaluator.classify_metacognitive_tier`, que já garante que
`metacognitive_superhuman_verified` só surge com `external_validation`.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from mci.metacognitive_evaluator import classify_metacognitive_tier


# Teto de qualidade admissível sem validação externa (escala 0–10).
INTERNAL_QUALITY_CEILING = 8.5


# ── Léxicos ──────────────────────────────────────────────────────────

_COVERAGE_MARKERS = (
    "cobertura", "coverage", "scanner", "varrid", "eixos",
    "checklist", "todos os eixos", "processo completo", "abrangência",
    "abrangencia",
)

_QUALITY_MARKERS = (
    "obra-prima", "obra prima", "best-seller", "bestseller", "mérito",
    "merito", "/10", " nota ", "estrelas", "qualis", "superhuman",
    "super-humano", "obra de arte", "melhor do mundo",
)

# Termos que só deixam de ser inflação COM validação externa.
_EXTERNAL_REQUIRED = (
    "best-seller", "bestseller", "obra-prima", "obra prima", "qualis a1",
    "superhuman", "super-humano", "verified", "verificado",
    "estado da arte", "state of the art", "melhor do mundo",
    "nota máxima", "nota maxima",
)

# Alegações de perfeição absoluta: suspeitas mesmo com validação externa.
_ABSOLUTE = (
    "100%", "perfeito", "perfeita", "sem falhas", "garantido", "garantida",
    "impecável", "impecavel", "infalível", "infalivel",
)

# Nota numérica de topo (≥9/10). Só admissível com validação externa.
_TOP_SCORE_RE = re.compile(r"(?:10(?:[.,]0)?|9[.,]\d)\s*/\s*10")


# ── Normalização de escala ───────────────────────────────────────────

def _to_0_10(value: Optional[float]) -> float:
    """Aceita fração (0–1), pontos (1–10) ou porcentagem (10–100)."""
    if value is None:
        return 0.0
    v = float(value)
    if v <= 0:
        return 0.0
    if v <= 1:
        v *= 10.0
    elif v > 10:
        v /= 10.0
    return round(max(0.0, min(10.0, v)), 4)


def _to_0_100(value: Optional[float]) -> float:
    """Normaliza para a escala 0–100 esperada por classify_metacognitive_tier."""
    if value is None:
        return 0.0
    v = float(value)
    if v <= 0:
        return 0.0
    if v <= 1:
        v *= 100.0
    elif v <= 10:
        v *= 10.0
    return round(max(0.0, min(100.0, v)), 2)


# ── classify_claim ───────────────────────────────────────────────────

def classify_claim(text: str) -> Dict[str, Any]:
    """Rotula a natureza de uma alegação: cobertura, qualidade, mista ou neutra."""
    low = (text or "").lower()
    has_cov = any(m in low for m in _COVERAGE_MARKERS)
    has_qual = any(m in low for m in _QUALITY_MARKERS)
    if has_cov and has_qual:
        kind = "mixed"
    elif has_qual:
        kind = "quality"
    elif has_cov:
        kind = "coverage"
    else:
        kind = "neutral"
    return {
        "kind": kind,
        "is_quality_verdict": has_qual,
        "has_coverage_language": has_cov,
    }


# ── detect_inflation ─────────────────────────────────────────────────

def detect_inflation(text: str, external_validation: bool = False) -> List[Dict[str, Any]]:
    """Encontra linguagem inflacionária que exigiria validação externa.

    Termos de ``_EXTERNAL_REQUIRED`` e notas de topo deixam de ser achados
    quando ``external_validation=True``. Alegações de perfeição absoluta
    permanecem suspeitas mesmo validadas.
    """
    low = (text or "").lower()
    findings: List[Dict[str, Any]] = []
    seen: set = set()

    def _add(term: str, category: str, requires_external: bool) -> None:
        if requires_external and external_validation:
            return
        if term in seen:
            return
        seen.add(term)
        findings.append({
            "term": term,
            "category": category,
            "requires_external": requires_external,
        })

    for term in _EXTERNAL_REQUIRED:
        if term in low:
            _add(term, "external_required", True)
    for term in _ABSOLUTE:
        if term in low:
            _add(term, "absolute_perfection", False)
    for match in _TOP_SCORE_RE.finditer(low):
        _add(match.group(0).strip(), "top_score", True)

    return findings


# ── honest_score_band ────────────────────────────────────────────────

def honest_score_band(coverage: Optional[float] = None,
                      external_validation: bool = False,
                      quality_signal: Optional[float] = None) -> Dict[str, Any]:
    """Faixa honesta (piso–teto) em escala 0–10.

    Sem validação externa o teto é limitado a ``INTERNAL_QUALITY_CEILING`` e
    ``verdict_allowed`` (nota-topo ≥ 9) é ``False``. Cobertura contribui
    apenas como piso fraco de processo — cobertura ≠ qualidade.
    """
    cov = _to_0_10(coverage)
    ceiling = 10.0 if external_validation else INTERNAL_QUALITY_CEILING

    # Cobertura é processo, não mérito: sustenta no máximo metade como piso.
    process_floor = round(cov * 0.5, 2)
    floor = min(process_floor, ceiling)
    if quality_signal is not None:
        q = _to_0_10(quality_signal)
        floor = min(max(floor, round(q * 0.8, 2)), ceiling)
    floor = round(min(floor, ceiling), 2)

    return {
        "floor": floor,
        "ceiling": ceiling,
        "band": f"{floor:.1f}–{ceiling:.1f}",
        "verdict_allowed": bool(external_validation),
        "coverage_normalized": cov,
        "cap_reason": (
            "validação externa presente: teto liberado"
            if external_validation
            else "sem validação externa: teto de qualidade limitado a "
                 f"{INTERNAL_QUALITY_CEILING}/10 (cobertura não é qualidade)"
        ),
    }


# ── review — pipeline completo ───────────────────────────────────────

def review(text: str,
           coverage: Optional[float] = None,
           external_validation: bool = False,
           quality_signal: Optional[float] = None) -> Dict[str, Any]:
    """Avaliação honesta ponta-a-ponta de uma alegação/artefato.

    Combina classificação da alegação, detecção de inflação, faixa honesta
    e o tier metacognitivo (reusando a política existente). ``publishable``
    é ``True`` apenas quando não há inflação bloqueante.
    """
    claim = classify_claim(text)
    inflation = detect_inflation(text, external_validation=external_validation)
    band = honest_score_band(coverage, external_validation, quality_signal)
    tier = classify_metacognitive_tier(_to_0_100(coverage), external_validation)

    recommendations: List[str] = [
        "Cobertura mede processo, não qualidade; nota de topo exige "
        "validação externa.",
    ]
    if inflation:
        termos = ", ".join(sorted({f["term"] for f in inflation}))
        recommendations.append(
            f"Remover/hedgear linguagem inflada sem validação externa: {termos}."
        )
    if claim["is_quality_verdict"] and not external_validation:
        recommendations.append(
            "Reformular como faixa estimada (ex.: "
            f"{band['band']}), não como veredito definitivo."
        )
    if not inflation and not (claim["is_quality_verdict"] and not external_validation):
        recommendations.append(
            "Manter postura conservadora: candidate interno, verified só "
            "com validação externa."
        )

    return {
        "claim": claim,
        "inflation": inflation,
        "band": band,
        "tier": tier,
        "external_validation": bool(external_validation),
        "publishable": len(inflation) == 0,
        "recommendations": recommendations,
        "policy": "cobertura ≠ qualidade; verified requer validação externa",
    }
