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
    domain_id: str = "",
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
        "domain_id": domain_id,
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


def summarize_legal_domain_route(query: str, explicit_domain_id: str = "") -> Dict[str, Any]:
    from legal.specializations import (
        route_legal_domain,
        build_domain_specialist_agent,
        get_legal_domain_profile,
    )

    profile = get_legal_domain_profile(explicit_domain_id) if explicit_domain_id else route_legal_domain(query)
    agent = build_domain_specialist_agent(profile.domain_id)
    return {
        "domain_id": profile.domain_id,
        "domain_name": profile.name,
        "specialist_agent_id": agent.id,
        "specialist_agent_name": agent.name,
    }


def resolve_domain_knowledge_base_selection(
    query: str,
    mode: str = "automatico",
    explicit_domain_id: str = "",
) -> Dict[str, Any]:
    from legal import (
        build_domain_knowledge_base,
        get_legal_domain_profile,
        route_domain_knowledge_base,
    )

    normalized = (mode or "automatico").lower()
    if normalized == "manual" and explicit_domain_id:
        kb = build_domain_knowledge_base(explicit_domain_id)
        profile = get_legal_domain_profile(explicit_domain_id)
        return {
            "domain_id": explicit_domain_id,
            "domain_name": profile.name if profile else explicit_domain_id,
            "knowledge_base": kb,
        }

    routed = route_domain_knowledge_base(query)
    profile = get_legal_domain_profile(routed["domain_id"])
    return {
        "domain_id": routed["domain_id"],
        "domain_name": profile.name if profile else routed["domain_id"],
        "knowledge_base": routed["knowledge_base"],
    }


def summarize_domain_knowledge_base(
    query: str,
    domain_id: str,
    knowledge_base,
    limit: int = 3,
) -> Dict[str, Any]:
    results = knowledge_base.search(query, max_results=limit, domain_id=domain_id)
    docs = knowledge_base.list_documents(domain_id=domain_id)
    return {
        "document_count": len(docs),
        "top_titles": [doc.title for doc, _ in results],
        "rag_context": knowledge_base.rag_context(query, max_chars=500),
    }


__all__ = [
    "build_legal_params",
    "summarize_legal_impact_section",
    "summarize_legal_domain_route",
    "resolve_domain_knowledge_base_selection",
    "summarize_domain_knowledge_base",
]
