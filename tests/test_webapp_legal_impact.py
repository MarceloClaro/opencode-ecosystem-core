# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-925: interface web para Legal Impact Scanner."""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_build_legal_params_parses_keywords_csv():
    from webapp.legal_impact_helpers import build_legal_params

    params = build_legal_params(
        titulo="Diagnóstico jurídico",
        corpus="texto base",
        metodologia="método",
        resultados="resultados",
        conclusoes="conclusões",
        palavras_chave_csv="lgpd, compliance, precedentes , risco",
        area_conhecimento="direito digital",
        domain_id="digital_lgpd",
    )

    assert params["titulo"] == "Diagnóstico jurídico"
    assert params["resumo"] == "texto base"
    assert params["palavras_chave"] == ["lgpd", "compliance", "precedentes", "risco"]
    assert params["area_conhecimento"] == "direito digital"
    assert params["domain_id"] == "digital_lgpd"


def test_resolve_domain_knowledge_base_selection_auto_and_manual():
    from webapp.legal_impact_helpers import resolve_domain_knowledge_base_selection

    auto = resolve_domain_knowledge_base_selection(
        query="habeas corpus e prisão preventiva",
        mode="automatico",
    )
    manual = resolve_domain_knowledge_base_selection(
        query="qualquer texto",
        mode="manual",
        explicit_domain_id="tributario",
    )

    assert auto["domain_id"] == "penal"
    assert manual["domain_id"] == "tributario"
    assert manual["knowledge_base"].count() >= 1


def test_summarize_domain_knowledge_base_returns_preview():
    from webapp.legal_impact_helpers import resolve_domain_knowledge_base_selection, summarize_domain_knowledge_base

    routed = resolve_domain_knowledge_base_selection(
        query="execução fiscal e crédito tributário",
        mode="manual",
        explicit_domain_id="tributario",
    )
    preview = summarize_domain_knowledge_base(
        query="execução fiscal e crédito tributário",
        domain_id=routed["domain_id"],
        knowledge_base=routed["knowledge_base"],
    )

    assert preview["document_count"] >= 1
    assert len(preview["top_titles"]) >= 1
    assert isinstance(preview["rag_context"], str)


def test_summarize_legal_impact_section_extracts_metrics():
    from webapp.legal_impact_helpers import summarize_legal_impact_section

    summary = summarize_legal_impact_section({
        "overall_score": 82.5,
        "metacognitive_gain_score": 61.0,
        "legal_readiness": "alta",
        "high_risk_flags": ["data_protection", "contractual_liability"],
    })

    assert summary["overall_score"] == 82.5
    assert summary["metacognitive_gain_score"] == 61.0
    assert summary["legal_readiness"] == "alta"
    assert summary["high_risk_count"] == 2


def test_summarize_legal_domain_route_returns_specialist():
    from webapp.legal_impact_helpers import summarize_legal_domain_route

    route = summarize_legal_domain_route(
        "dados pessoais, consentimento, controlador e incidente de segurança"
    )

    assert route["domain_id"] == "digital_lgpd"
    assert "Especialista" in route["specialist_agent_name"]


def test_orchestrator_diagnose_supports_legal_impact():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orch = MarceloClaroOrchestrator()
    report = orch.diagnose(
        corpus=(
            "Pesquisa com LGPD, consentimento, licença Creative Commons, "
            "revisão jurídica, precedentes do STF e limitações metodológicas."
        ),
        domain="direito digital",
        include_legal_impact=True,
        legal_params={
            "titulo": "Avaliação web",
            "resumo": "Pesquisa com LGPD e revisão jurídica.",
            "metodologia": "Anonimização e compliance.",
            "resultados": "Mitigação de risco.",
            "conclusoes": "Abstenção quando necessário.",
            "palavras_chave": ["lgpd", "compliance", "stf"],
        },
    )

    assert "legal_impact" in report
    assert 0.0 <= report["legal_impact"]["overall_score"] <= 100.0
    assert 0.0 <= report["legal_impact"]["metacognitive_gain_score"] <= 100.0


def test_webapp_source_contains_legal_impact_controls():
    source = Path("webapp/app.py").read_text(encoding="utf-8")

    # Legais helpers importados e usados
    assert "build_legal_params" in source
    assert "summarize_legal_impact_section" in source
    assert "summarize_legal_domain_route" in source
    assert "resolve_domain_knowledge_base_selection" in source
    assert "summarize_domain_knowledge_base" in source
    # UI elements for legal analysis
    assert "Analisar Impacto Juridico" in source or "analise juridica" in source.lower()
    assert "Score Juridico" in source
    assert "Ganho Metacognitivo" in source
    assert "Legal Impact Scanner" in source


def test_webapp_source_contains_dedicated_legal_tab():
    source = Path("webapp/app.py").read_text(encoding="utf-8")

    assert "⚖️" in source  # emoji juridico presente
    assert "analise juridica" in source.lower() or "impacto juridico" in source.lower()
    assert "legal_impact" in source
    assert "legal_params" in source
    assert "high_risk_flags" in source
    assert "build_legal_params" in source
