# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R267: scanners literários rigorosos."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdd.spec_engine import spec_registry


RICH_LITERARY_TEXT = """
Nota do Arquivista: este romance-arquivo reúne memórias, laudos, cartas,
prontuários e fragmentos. Joaquim deseja sair da vala, mas a fome fala por ele.
Lúcia investiga o diário em 2026 e descobre que o leitor também entra no ciclo.
O olho amarelo, o cheiro adocicado, a coruja e a página rasgada retornam como
símbolos. Há cinco partes, rotas de leitura, passaporte do leitor, epílogo e
contaminação narrativa. A obra dialoga com arquivo, trauma, metaficção,
literatura ergódica, horror social e ética da representação. A nota histórica
adverte que a ficção não substitui testemunho real nem reparação.
"""

WEAK_TEXT = """Um texto simples informa que alguém saiu, voltou e terminou."""


EXPECTED_SCANNERS = {
    "narrative_architecture",
    "character_psychology",
    "style_voice",
    "symbolic_imagery",
    "intertextual_theory",
    "reader_response",
    "ethical_representation",
    "literary_innovation",
}


def test_spec_r267_registered():
    spec = spec_registry.get("SPEC-935-R267")
    assert spec is not None
    assert spec.status in {"red", "green", "verified"}


def test_literary_suite_exports_eight_scanners():
    from scanners.literary_scanners import LITERARY_SCANNER_CLASSES

    assert len(LITERARY_SCANNER_CLASSES) == 8
    assert {cls.scanner_id for cls in LITERARY_SCANNER_CLASSES} == EXPECTED_SCANNERS


def test_each_scanner_returns_serializable_contract():
    from scanners.literary_scanners import LITERARY_SCANNER_CLASSES

    for scanner_cls in LITERARY_SCANNER_CLASSES:
        result = scanner_cls().scan(RICH_LITERARY_TEXT)
        assert result["scanner_id"] == scanner_cls.scanner_id
        assert 0.0 <= result["score"] <= 100.0
        assert result["grade"] in {"insuficiente", "emergente", "consistente", "forte", "excelente"}
        assert isinstance(result["evidence"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["dimensions"], dict)
        assert len(result["dimensions"]) >= 3
        json.dumps(result, ensure_ascii=False)


def test_literary_suite_aggregation_and_overclaim_guard():
    from scanners.literary_scanners import run_literary_scanner_suite

    result = run_literary_scanner_suite(RICH_LITERARY_TEXT, metadata={"genre": "romance-arquivo"})
    assert result["domain"] == "literary"
    assert result["scanner_count"] == 8
    assert set(result["results"].keys()) == EXPECTED_SCANNERS
    assert 0.0 <= result["literary_excellence_score"] <= 100.0
    assert "não substitui crítica literária humana" in result["overclaim_guard"].lower()
    assert result["metadata"]["genre"] == "romance-arquivo"


def test_rich_literary_text_scores_above_weak_text():
    from scanners.literary_scanners import run_literary_scanner_suite

    rich = run_literary_scanner_suite(RICH_LITERARY_TEXT)
    weak = run_literary_scanner_suite(WEAK_TEXT)
    assert rich["literary_excellence_score"] > weak["literary_excellence_score"]
    assert rich["results"]["reader_response"]["score"] > weak["results"]["reader_response"]["score"]
    assert rich["results"]["symbolic_imagery"]["score"] > weak["results"]["symbolic_imagery"]["score"]


def test_empty_text_is_safe_and_actionable():
    from scanners.literary_scanners import run_literary_scanner_suite

    result = run_literary_scanner_suite("")
    assert result["scanner_count"] == 8
    assert result["literary_excellence_score"] == 0.0
    for scanner_result in result["results"].values():
        assert scanner_result["score"] == 0.0
        assert scanner_result["warnings"]
        assert scanner_result["recommendations"]


def test_scanners_exported_from_package_root():
    from scanners import LiteraryInnovationScanner, run_literary_scanner_suite

    result = LiteraryInnovationScanner().scan(RICH_LITERARY_TEXT)
    assert result["scanner_id"] == "literary_innovation"
    assert run_literary_scanner_suite(RICH_LITERARY_TEXT)["scanner_count"] == 8


def test_diagnostic_pipeline_auto_includes_literary_for_literary_domain():
    from scanners import DiagnosticPipeline

    report = DiagnosticPipeline().run(RICH_LITERARY_TEXT, domain="literary")
    assert "literary" in report
    assert report["literary"]["scanner_count"] == 8
    assert report["literary"]["domain"] == "literary"
