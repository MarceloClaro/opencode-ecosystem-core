# -*- coding: utf-8 -*-
"""Helpers puros para a interface web do Legal Impact Scanner (SPEC-925)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_legal_params(
    titulo: str,
    corpus: str,
    metodologia: str = "",
    resultados: str = "",
    conclusoes: str = "",
    palavras_chave_csv: str = "",
    area_conhecimento: str = "",
) -> Dict[str, Any]:
    palavras = [p.strip() for p in palavras_chave_csv.split(",") if p.strip()]
    return {
        "titulo": titulo or "Diagnóstico Jurídico do Artefato",
        "resumo": corpus,
        "metodologia": metodologia,
        "resultados": resultados,
        "conclusoes": conclusoes,
        "palavras_chave": palavras,
        "area_conhecimento": area_conhecimento,
    }


def summarize_legal_impact_section(section: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    section = section or {}
    return {
        "overall_score": section.get("overall_score", 0.0),
        "metacognitive_gain_score": section.get("metacognitive_gain_score", 0.0),
        "legal_readiness": section.get("legal_readiness", "—"),
        "high_risk_count": len(section.get("high_risk_flags", []) or []),
        "high_risk_flags": section.get("high_risk_flags", []) or [],
    }


__all__ = ["build_legal_params", "summarize_legal_impact_section"]
