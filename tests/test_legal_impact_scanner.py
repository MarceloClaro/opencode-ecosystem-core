# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-924: Legal Impact Scanner."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


LEGAL_AWARE_TEXT = (
    "A pesquisa usa dados pessoais anonimizados conforme LGPD, com consentimento "
    "e base legal explícita. Há aprovação do comitê de ética, revisão jurídica, "
    "licença Creative Commons, análise de risco regulatório, ponderação entre "
    "transparência e privacidade, limitações metodológicas e possibilidade de "
    "abstenção quando houver incerteza jurídica. Fundamenta-se na CF/88, no CPC/2015 "
    "e em precedentes do STF e STJ."
)

NEUTRAL_TEXT = (
    "A pesquisa apresenta um modelo e um dataset para produção. O sistema é eficiente, "
    "seguro e garantido, sem necessidade de revisão adicional."
)


def test_legal_impact_report_structure():
    from scanners import LegalImpactScanner

    scanner = LegalImpactScanner()
    report = scanner.analyze_research_paper(
        titulo="Estudo com LGPD e precedentes",
        resumo=LEGAL_AWARE_TEXT,
        metodologia="Metodologia com anonimização e compliance.",
        resultados="Resultados com mitigação de risco e revisão jurídica.",
        conclusoes="Conclusões com limitações e cautela.",
        palavras_chave=["lgpd", "stf", "compliance"],
        area_conhecimento="direito digital",
    )

    payload = report.as_dict()
    assert 0.0 <= payload["overall_score"] <= 100.0
    assert 0.0 <= payload["metacognitive_gain_score"] <= 100.0
    assert payload["artifact_type"] == "research_paper"
    assert isinstance(payload["dimensions"], list)
    assert len(payload["dimensions"]) == 6


def test_legal_impact_detects_metacognitive_gain():
    from scanners import LegalImpactScanner

    scanner = LegalImpactScanner()
    weak = scanner.analyze_production_artifact("artefato neutro", NEUTRAL_TEXT)
    strong = scanner.analyze_production_artifact("artefato jurídico", LEGAL_AWARE_TEXT)

    assert strong.metacognitive_gain_score > weak.metacognitive_gain_score
    assert strong.overall_score > weak.overall_score


def test_legal_impact_detects_lgpd_and_jurisprudence():
    from scanners import LegalImpactScanner

    scanner = LegalImpactScanner()
    report = scanner.analyze_production_artifact("produção", LEGAL_AWARE_TEXT)
    dim_names = {d.name: d for d in report.dimensions}

    assert dim_names["data_protection"].score >= 60
    assert dim_names["jurisprudential_grounding"].score >= 60


def test_diagnostic_pipeline_can_include_legal_impact():
    from scanners import DiagnosticPipeline

    report = DiagnosticPipeline().run(
        LEGAL_AWARE_TEXT,
        domain="legal_ai",
        include_legal_impact=True,
        legal_params={
            "titulo": "Pesquisa juridicamente consciente",
            "resumo": LEGAL_AWARE_TEXT,
            "metodologia": "Anonimização + revisão jurídica",
            "resultados": "Mitigação de riscos e compliance",
            "conclusoes": "Abstenção quando houver incerteza",
            "palavras_chave": ["lgpd", "stf", "compliance"],
        },
    )

    assert "legal_impact" in report
    assert 0.0 <= report["legal_impact"]["overall_score"] <= 100.0
    assert 0.0 <= report["legal_impact"]["metacognitive_gain_score"] <= 100.0


def test_diagnostic_pipeline_backcompat_without_legal_impact():
    from scanners import DiagnosticPipeline

    report = DiagnosticPipeline().run("texto simples", domain="test")
    assert "legal_impact" not in report
