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
    )

    assert params["titulo"] == "Diagnóstico jurídico"
    assert params["resumo"] == "texto base"
    assert params["palavras_chave"] == ["lgpd", "compliance", "precedentes", "risco"]
    assert params["area_conhecimento"] == "direito digital"


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

    assert "Incluir Visão Jurídica de Impacto (SPEC-924)" in source
    assert "⚖️ Resumo da Visão Jurídica" in source
    assert "build_legal_params" in source
    assert "summarize_legal_impact_section" in source


def test_webapp_source_contains_dedicated_legal_tab():
    source = Path("webapp/app.py").read_text(encoding="utf-8")

    assert '"⚖️ Jurídico"' in source
    assert "⚖️ Visão Jurídica Dedicada" in source
    assert "⚖️ Avaliar Impacto Jurídico" in source
    assert "JSON Auditável Completo" in source
