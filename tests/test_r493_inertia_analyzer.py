# -*- coding: utf-8 -*-
"""Testes do Inércia Vetorial Analyzer (R493).

Proposta do usuário: mesmo com alto potencial e forte aderência, uma capacidade
pode não emergir porque toda evolução compete contra mecanismos de estabilidade.
O IVA responde "o que está impedindo isso de emergir?" via QIV = Potencial −
Inércia, onde Inércia = Complexidade + Dependências Faltantes + Custo +
Acoplamentos. Hermético, stdlib, anti-overclaim.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from scanners.inertia_analyzer import (
    InertiaAssessment,
    InertiaReport,
    InertiaVectorAnalyzer,
)
from scanners.potentiality_scanner import DEFAULT_MODULES, Potentiality, PotentialityScanner

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "inertia_analyzer.py").read_text(encoding="utf-8")
BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]


@pytest.fixture(scope="module")
def dna() -> dict:
    return DEFAULT_MODULES


@pytest.fixture(scope="module")
def analyzer(dna) -> InertiaVectorAnalyzer:
    return InertiaVectorAnalyzer(modules=dna)


# ═══════════════════════════════════════════════════════════════════════
# CA1-CA3 — exemplo conceitual do usuário e decomposição da inércia
# ═══════════════════════════════════════════════════════════════════════

class TestExemploConceitual:
    def test_qiv_from_user_example(self, analyzer):
        """Potencial 0.82, inércia 0.27 → QIV = 0.55 → Quebra Moderada."""
        a = analyzer.evaluate(
            id="potential-discovery-engine",
            description="Potential Discovery Engine",
            requires=["gap_detection", "trajectory_mapping", "self_evolution"],
            potential=0.82,
        )
        assert a.qiv == pytest.approx(0.82 - a.inertia, abs=1e-4)
        assert a.qiv == pytest.approx(0.55, abs=0.06)  # exemplo conceitual aprox.

    def test_tiers(self, analyzer):
        """CA2: faixas do usuário."""
        assert analyzer._tier(0.75) == "quebra-imediata"
        assert analyzer._tier(0.55) == "quebra-moderada"
        assert analyzer._tier(0.30) == "inercia-dominante"
        assert analyzer._tier(0.70) == "quebra-moderada"   # faixa inclusiva
        assert analyzer._tier(0.40) == "quebra-moderada"

    def test_components_in_unit_interval(self, analyzer):
        """CA3: componentes e ponderados 0.30/0.30/0.20/0.20."""
        a = analyzer.evaluate(
            id="x", description="x",
            requires=["gap_detection", "trajectory_mapping", "self_evolution"],
            potential=0.8,
        )
        for v in (a.complexity, a.dependencies, a.cost, a.coupling):
            assert 0.0 <= v <= 1.0
        expected = (0.30 * a.complexity + 0.30 * a.dependencies
                    + 0.20 * a.cost + 0.20 * a.coupling)
        assert a.inertia == pytest.approx(expected, abs=1e-4)


# ═══════════════════════════════════════════════════════════════════════
# CA4-CA6 — modelo e determinismo
# ═══════════════════════════════════════════════════════════════════════

class TestModelo:
    def test_dependencies_from_missing(self, analyzer):
        """CA4: dependências = fração dos requires ausentes do DNA."""
        a = analyzer.evaluate(
            id="c", description="c",
            requires=["gap_detection", "inexistente_a", "inexistente_b"],
            potential=0.5,
        )
        assert a.dependencies == pytest.approx(2 / 3, abs=1e-4)
        assert sorted(a.critical_dependencies) == ["inexistente_a", "inexistente_b"]

    def test_qiv_clamped(self, analyzer):
        """CA5: QIV ∈ [0,1] mesmo com potencial 1.0 e inércia 0."""
        a = analyzer.evaluate(id="c", description="c", requires=[], potential=1.0)
        assert 0.0 <= a.qiv <= 1.0
        b = analyzer.evaluate(id="d", description="d", requires=["z_nao_existe"],
                              potential=0.0)
        assert 0.0 <= b.qiv <= 1.0

    def test_determinism_and_barrier_ranking(self, analyzer):
        """CA6: mesmo resultado entre execuções; ranking por inércia desc."""
        cands = [
            {"id": "a", "description": "a", "requires": ["gap_detection"], "potential": 0.9},
            {"id": "b", "description": "b", "requires": ["z1", "z2", "z3"], "potential": 0.5},
        ]
        r1 = analyzer.scan(cands)
        r2 = analyzer.scan(cands)
        assert [a.id for a in r1.ranking] == [a.id for a in r2.ranking]
        assert r1.ranking[0].inertia >= r1.ranking[-1].inertia


# ═══════════════════════════════════════════════════════════════════════
# CA7-CA10 — qualidade
# ═══════════════════════════════════════════════════════════════════════

class TestQualidade:
    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_algorithm_documented(self):
        for term in ("0.30", "0.20", "dependencias", "complexidade",
                     "acoplamentos", "custo", "clamp"):
            assert term in MODULE_TEXT.lower(), term

    def test_reorg_prediction(self, analyzer):
        """CA9: previsão de reorganização mapeada às faixas."""
        assert analyzer._tier(0.75) == "quebra-imediata"
        pred = analyzer._reorg_prediction("quebra-imediata")
        assert pred == "alta"
        pred2 = analyzer._reorg_prediction("inercia-dominante")
        assert pred2 == "baixa"

    def test_no_requires_explicit(self, analyzer):
        """CA10: candidata sem requires → inércia documentada, sem crash."""
        a = analyzer.evaluate(id="n", description="n", requires=[], potential=0.5)
        assert a.dependencies == 0.0
        assert a.critical_dependencies == []
        assert a.inertia >= 0.0
        assert a.qiv == pytest.approx(a.potential - a.inertia, abs=1e-4)


# ═══════════════════════════════════════════════════════════════════════
# CA11-CA12 — integração
# ═══════════════════════════════════════════════════════════════════════

class TestIntegracao:
    def test_consumes_potentiality_report(self, dna):
        """CA11: consome Potentiality (R491)."""
        scanner = PotentialityScanner(modules=dna)
        from scanners.potentiality_scanner import PotentialityCandidate, TIER_LATENTE_ALTO
        cands = [
            PotentialityCandidate(
                id="cognitive-manifold-mapper",
                description="Mapa cognitivo",
                requires=["gap_detection", "trajectory_mapping",
                          "cross_validation", "nao_existe"],
            ),
            PotentialityCandidate(
                id="simple",
                description="Simples",
                requires=["gap_detection"],
            ),
        ]
        rep = scanner.scan(cands)
        analyzer = InertiaVectorAnalyzer(modules=dna)
        out = analyzer.analyze(rep)
        assert len(out.assessments) == 2
        for a in out.assessments:
            # potencial = coverage do Potentiality (latent potential score)
            assert a.potential == pytest.approx(
                rep.by_id[a.id].coverage, abs=1e-4)
            assert a.qiv <= 1.0

    def test_empty_report(self, analyzer):
        """CA12: sem candidatas → relatório vazio sem erro."""
        out = analyzer.scan([])
        assert out.assessments == []
        assert out.ranking == []
        assert out.params["n_candidates"] == 0