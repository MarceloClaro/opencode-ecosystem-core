# -*- coding: utf-8 -*-
"""Testes da Composição Unitária do Conhecimento (R490).

Proposta do usuário (camada Composição Unitária): cada capacidade futura é
como uma atividade de obra — possui composição de insumos (conceitos, métodos,
bases, ferramentas, domínios, validações). Este módulo decompõe cada lacuna
do ReverseScanner nesses insumos, com bank curado + fallback lexical.

Hermético: stdlib apenas; sem rede/credenciais. Anti-overclaim: composição é
heurística (origem explícita), sem veredictos absolutos.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from scanners.knowledge_composition import (
    CompositionInsight,
    CompositionReport,
    KnowledgeComposition,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "knowledge_composition.py").read_text(encoding="utf-8")
BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]


@pytest.fixture(scope="module")
def kc() -> KnowledgeComposition:
    return KnowledgeComposition()


@pytest.fixture(scope="module")
def synthetic_scan() -> dict:
    return {
        "dimensions": {
            "metodos": {
                "covered": ["Quantitativo experimental", "Revisão sistemática"],
                "absent": ["Meta-análise"],
            },
            "raciocinio": {
                "covered": ["Dedutivo"],
                "absent": ["Prova geométrica"],
            },
            "dados": {
                "covered": [],
                "absent": ["Metadados (revisões)"],
            },
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# CA1-CA2 — bank curado
# ═══════════════════════════════════════════════════════════════════════

class TestBank:
    def test_meta_analysis_curated(self, kc):
        ins = kc.compose("metodos.Meta-análise")
        assert ins.origem == "bank"
        assert ins.conceitos and "efeito de tamanho" in ins.conceitos
        assert "forest plot" in ins.conceitos or "heterogeneidade" in ins.conceitos

    def test_meta_analysis_all_six_classes(self, kc):
        ins = kc.compose("metodos.Meta-análise")
        assert ins.metodos and ins.bases and ins.ferramentas
        assert ins.dominios and ins.validacoes

    def test_geometric_proof_curated(self, kc):
        ins = kc.compose("raciocinio.Prova geométrica")
        assert ins.origem == "bank"
        assert "axioma" in ins.conceitos
        assert ins.validacoes  # verificação formal deve estar presente

    def test_every_insight_has_source_tag(self, kc):
        for cap in ("metodos.Meta-análise", "raciocinio.Prova geométrica"):
            ins = kc.compose(cap)
            assert ins.fonte_conceitos.startswith("bank") or ins.fonte_conceitos == ""


# ═══════════════════════════════════════════════════════════════════════
# CA3 — fallback lexical
# ═══════════════════════════════════════════════════════════════════════

class TestLexical:
    def test_unknown_capability_falls_back(self, kc):
        ins = kc.compose("musica.Harmonia modal aplicada")
        assert ins.origem == "lexical"
        assert ins.warning

    def test_lexical_has_six_keys(self, kc):
        ins = kc.compose("dados.Proveniência auditável")
        for attr in ("conceitos", "metodos", "bases", "ferramentas", "dominios", "validacoes"):
            assert hasattr(ins, attr)

    def test_lexical_derives_from_tokens(self, kc):
        ins = kc.compose("musica.Harmonia modal")
        assert any("harmonia" in c.lower() or "musica" in c.lower() for c in ins.conceitos)


# ═══════════════════════════════════════════════════════════════════════
# CA4-CA6 — scan integrado
# ═══════════════════════════════════════════════════════════════════════

class TestScan:
    def test_scan_integrates_reverse_scanner(self, kc, synthetic_scan):
        report = kc.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert isinstance(report, CompositionReport)
        assert report.evolution_gap
        assert "metodos.Meta-análise" in report.by_capability

    def test_scan_by_gap(self, kc, synthetic_scan):
        report = kc.scan(synthetic_scan, target_state=["raciocinio.Prova geométrica"])
        assert report.by_capability["raciocinio.Prova geométrica"].origem == "bank"

    def test_determinism(self, kc, synthetic_scan):
        a = kc.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        b = kc.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert a.by_capability == b.by_capability

    def test_no_targets(self, kc):
        report = kc.scan({}, target_state=[])
        assert report.matches == []
        assert report.evolution_gap == []


# ═══════════════════════════════════════════════════════════════════════
# CA7-CA9 — qualidade
# ═══════════════════════════════════════════════════════════════════════

class TestQuality:
    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_no_anti_overclaim_report(self, kc, synthetic_scan):
        report = kc.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        for pattern in BANNED:
            assert not re.search(pattern, str(report), re.IGNORECASE), pattern

    def test_algorithm_documented(self):
        assert "COMPOSITION_BANK" in MODULE_TEXT
        assert "bank" in MODULE_TEXT and "lexical" in MODULE_TEXT
        assert "conceitos" in MODULE_TEXT and "validacoes" in MODULE_TEXT

    def test_result_objects_typed(self):
        ins = CompositionInsight(capability="x.y", conceitos=[], metodos=[], bases=[],
                                 ferramentas=[], dominios=[], validacoes=[],
                                 origem="lexical", warning="")
        assert ins.capability == "x.y"