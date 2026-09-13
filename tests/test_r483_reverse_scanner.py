# -*- coding: utf-8 -*-
"""Testes do ReverseScanner (R483) — Scanner Reverso de Trajetórias Evolutivas.

Valida a progressão do usuário (SCANNER ERRO → AUSÊNCIA → OPORTUNIDADE → REVERSO):

  R(F) = fecho regressivo de F no grafo do CrossValidationEngine
  Δ    = R(F) - A                        (gap evolutivo)
  p(g) = α·cascade + β·centrality + γ·novelty − δ·ritual   (em [0,1])

Hermético: sem rede, sem credenciais, sem código de terceiros. A integração
usa o CrossValidationEngine existente com um scan noológico sintético
determinístico.

Subconjunto esperado do grafo (DEPENDENCY_RULES relevantes ao cenário):

  requires: (metodos.Meta-análise → raciocinio.Probabilístico)
            (metodos.Meta-análise → dados."Metadados (revisões)")
            (raciocinio.Probabilístico → raciocinio.Dedutivo)
  enables : (raciocinio.Probabilístico → metodos.Meta-análise)
            (temporalidade."Longitudinal (longo prazo)" → raciocinio.Probabilístico)
            (raciocinio.Probabilístico → raciocinio.Bayesiano)  [Bayesiano fora do grafo]

  R(F) p/ F = {metodos.Meta-análise} =
    {Meta-análise, Probabilístico, Metadados (revisões), Dedutivo, Longitudinal}
  Δ = R(F) - A(covered) = {Meta-análise, Probabilístico, Metadados, Longitudinal}
"""

from __future__ import annotations

import pathlib
import re

import pytest

from scanners.reverse_scanner import ReverseScanReport, ReverseScanner

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "reverse_scanner.py").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def scanner() -> ReverseScanner:
    return ReverseScanner()


@pytest.fixture(scope="module")
def synthetic_scan() -> dict:
    """Scan noológico sintético no formato do NoologicalScanner."""
    return {
        "research_domain": "ecosystem",
        "dimensions": {
            "metodos": {
                "covered": ["Quantitativo experimental", "Revisão sistemática"],
                "absent": ["Meta-análise"],
            },
            "raciocinio": {
                "covered": ["Dedutivo"],
                "absent": ["Probabilístico"],
            },
            "dados": {
                "covered": [],
                "absent": ["Metadados (revisões)"],
            },
            "temporalidade": {
                "covered": [],
                "absent": ["Longitudinal (longo prazo)"],
            },
        },
        "overall_density": 0.3,
    }


# ═══════════════════════════════════════════════════════════════════════
# CA1 — Fecho regressivo transitivo
# ═══════════════════════════════════════════════════════════════════════

class TestReverseClosure:
    def test_transitive_includes_prereqs(self, scanner, synthetic_scan):
        graph = scanner.build_graph(synthetic_scan)
        closure = scanner.reverse_closure(
            graph, ["metodos.Meta-análise"], observed=[]
        )
        assert "raciocinio.Probabilístico" in closure
        assert "raciocinio.Dedutivo" in closure        # prereq de prereq
        assert "dados.Metadados (revisões)" in closure

    def test_transitive_includes_enabler(self, scanner, synthetic_scan):
        graph = scanner.build_graph(synthetic_scan)
        closure = scanner.reverse_closure(
            graph, ["metodos.Meta-análise"], observed=[]
        )
        # enables: Longitudinal habilita Probabilístico => entra na regressão
        assert "temporalidade.Longitudinal (longo prazo)" in closure

    def test_closure_includes_target_itself(self, scanner, synthetic_scan):
        graph = scanner.build_graph(synthetic_scan)
        closure = scanner.reverse_closure(
            graph, ["metodos.Meta-análise"], observed=[]
        )
        assert "metodos.Meta-análise" in closure

    def test_stops_at_observed(self, scanner, synthetic_scan):
        """Poda em A: Dedutivo é observado; seus prereqs não devem ser expandidos."""
        graph = scanner.build_graph(synthetic_scan)
        closure = scanner.reverse_closure(
            graph,
            ["raciocinio.Dedutivo"],
            observed=["raciocinio.Dedutivo"],
        )
        assert closure == ["raciocinio.Dedutivo"]

    def test_empty_target_returns_empty(self, scanner, synthetic_scan):
        graph = scanner.build_graph(synthetic_scan)
        assert scanner.reverse_closure(graph, [], observed=[]) == []

    def test_unknown_target_ignored_with_warning(self, scanner, synthetic_scan):
        graph = scanner.build_graph(synthetic_scan)
        report = scanner.scan(
            synthetic_scan,
            target_state=["nao.existe"],
            observed=[],
        )
        assert report.reverse_closure == []
        assert any("nao.existe" in w for w in report.warnings)

    def test_cycle_tolerance(self, scanner):
        """Grafo cíclico não deve estourar recursão."""
        scan = {
            "dimensions": {
                "a": {"covered": [], "absent": ["X"]},
                "b": {"covered": [], "absent": ["Y"]},
            }
        }
        # Ciclo sintético não existe nas rules; verifica apenas execução sem erro
        # e parada em observado com nós irmãos.
        graph = scanner.build_graph(scan)
        closure = scanner.reverse_closure(graph, ["a.X"], observed=["a.X"])
        assert closure == ["a.X"]


# ═══════════════════════════════════════════════════════════════════════
# CA4 — Gap evolutivo
# ═══════════════════════════════════════════════════════════════════════

class TestEvolutionGap:
    def test_gap_is_closure_minus_observed(self, scanner, synthetic_scan):
        report = scanner.scan(
            synthetic_scan,
            target_state=["metodos.Meta-análise"],
            observed=None,  # default: covered do scan
        )
        assert set(report.evolution_gap) == {
            "metodos.Meta-análise",
            "raciocinio.Probabilístico",
            "dados.Metadados (revisões)",
            "temporalidade.Longitudinal (longo prazo)",
        }

    def test_gap_excludes_observed(self, scanner, synthetic_scan):
        report = scanner.scan(
            synthetic_scan,
            target_state=["metodos.Meta-análise"],
            observed=None,
        )
        assert "metodos.Quantitativo experimental" not in report.evolution_gap
        assert "raciocinio.Dedutivo" not in report.evolution_gap

    def test_gap_empty_when_covered(self, scanner, synthetic_scan):
        observed = [
            "metodos.Meta-análise",
            "raciocinio.Probabilístico",
            'dados."Metadados (revisões)"',
            "temporalidade.Longitudinal (longo prazo)",
        ]
        report = scanner.scan(
            synthetic_scan,
            target_state=["metodos.Meta-análise"],
            observed=observed,
        )
        assert report.evolution_gap == []

    def test_gap_deterministic_order(self, scanner, synthetic_scan):
        a = scanner.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        b = scanner.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert a.evolution_gap == b.evolution_gap
        assert a.evolution_gap == sorted(a.evolution_gap)


# ═══════════════════════════════════════════════════════════════════════
# CA5 — Componentes determinísticos
# ═══════════════════════════════════════════════════════════════════════

class TestComponents:
    def test_ritual_fraction(self, scanner):
        # 0 de 2 exemplares possuem a capacidade => ritual = 1.0
        assert scanner.ritual(
            "cap.X", exemplars=[["cap.A"], ["cap.B"]]
        ) == pytest.approx(1.0)
        # 1 de 2 => 0.5
        assert scanner.ritual(
            "cap.X", exemplars=[["cap.X"], ["cap.B"]]
        ) == pytest.approx(0.5)
        # todos possuem => 0.0
        assert scanner.ritual(
            "cap.X", exemplars=[["cap.X"], ["cap.X", "cap.B"]]
        ) == pytest.approx(0.0)

    def test_ritual_default_neutral_without_exemplars(self, scanner):
        assert scanner.ritual("cap.X", exemplars=None) == pytest.approx(0.0)
        assert scanner.ritual("cap.X", exemplars=[]) == pytest.approx(0.0)

    def test_novelty_overlap(self, scanner):
        assert scanner.novelty(
            "raciocinio.Probabilístico", corpus_terms=["raciocinio"]
        ) == pytest.approx(0.5)
        assert scanner.novelty(
            "raciocinio.Probabilístico",
            corpus_terms=["raciocinio", "probabilístico"],
        ) == pytest.approx(0.0)
        assert scanner.novelty("raciocinio.Probabilístico", corpus_terms=None) == pytest.approx(1.0)

    def test_novelty_no_corpus_is_max(self, scanner):
        assert scanner.novelty("qualquer.capacidade", corpus_terms=[]) == pytest.approx(1.0)


# ═══════════════════════════════════════════════════════════════════════
# CA6 — Potencial decomposto e normalizado
# ═══════════════════════════════════════════════════════════════════════

class TestPotential:
    def test_potential_default_weights_decomposition(self, scanner):
        # cascade_norm=1.0, centrality_norm=1.0, novelty=1.0, ritual=0.0
        # p = 0.40 + 0.25 + 0.20 - 0.00 = 0.85
        p = scanner.potential(
            capability="metodos.Meta-análise",
            cascade_map={"metodos.Meta-análise": 1.8},
            centrality_map={"metodos.Meta-análise": 0.3},
            corpus_terms=None,
            exemplars=None,
        )
        assert p == pytest.approx(0.85)

    def test_potential_ritual_penalty_reduces(self, scanner):
        base = scanner.potential(
            capability="metodos.Meta-análise",
            cascade_map={"metodos.Meta-análise": 1.8},
            centrality_map={"metodos.Meta-análise": 0.3},
            corpus_terms=None,
            exemplars=[["cap.A"]],  # exemplar NÃO possui g => ritual = 1.0
        )
        clean = scanner.potential(
            capability="metodos.Meta-análise",
            cascade_map={"metodos.Meta-análise": 1.8},
            centrality_map={"metodos.Meta-análise": 0.3},
            corpus_terms=None,
            exemplars=[["metodos.Meta-análise"]],  # exemplar possui g => ritual 0
        )
        assert base < clean
        assert base == pytest.approx(0.85 - 0.15)  # penalidade integral δ

    def test_potential_normalized_0_1(self, scanner):
        p = scanner.potential(
            capability="g",
            cascade_map={"g": 999.0},
            centrality_map={"g": 1.0},
            corpus_terms=None,
            exemplars=None,
        )
        assert 0.0 <= p <= 1.0

    def test_potential_zero_when_all_components_zero(self, scanner):
        p = scanner.potential(
            capability="g",
            cascade_map={"g": 0.0},
            centrality_map={"g": 0.0},
            corpus_terms=["g"],  # novelty = 0
            exemplars=[["g"]],   # ritual = 0
        )
        assert p == pytest.approx(0.0)

    def test_tier_classification(self, scanner):
        # ritual >= 0.5 manda para tier "ritual" mesmo com p alto
        assert scanner._tier(1.0, 0.6) == "ritual"
        assert scanner._tier(0.85, 0.0) == "alavanca"
        assert scanner._tier(0.55, 0.0) == "prioritaria"
        assert scanner._tier(0.3, 0.0) == "marginal"


# ═══════════════════════════════════════════════════════════════════════
# CA7 + CA8 — Integração e relatório
# ═══════════════════════════════════════════════════════════════════════

class TestScanReport:
    def test_integration_fields(self, scanner, synthetic_scan):
        report = scanner.scan(
            synthetic_scan,
            target_state=["metodos.Meta-análise"],
            corpus_terms=["Meta-análise", "raciocinio"],
        )
        assert report.target_state == ["metodos.Meta-análise"]
        assert "raciocinio.Dedutivo" in report.observed_capabilities
        assert "metodos.Meta-análise" in report.reverse_closure
        assert set(report.evolution_gap) >= {"raciocinio.Probabilístico"}
        assert report.params["cascade"] == pytest.approx(0.40)
        assert report.params["ritual"] == pytest.approx(0.15)
        assert isinstance(report.opportunities, list)

    def test_opportunity_objects(self, scanner, synthetic_scan):
        report = scanner.scan(
            synthetic_scan,
            target_state=["metodos.Meta-análise"],
        )
        from scanners.reverse_scanner import ReverseOpportunity

        for o in report.opportunities:
            assert isinstance(o, ReverseOpportunity)
            assert 0.0 <= o.potential <= 1.0
            assert 0.0 <= o.cascade <= 1.0
            assert 0.0 <= o.centrality <= 1.0
            assert 0.0 <= o.novelty <= 1.0
            assert 0.0 <= o.ritual <= 1.0
            assert o.tier in {"alavanca", "prioritaria", "marginal", "ritual"}
            assert isinstance(o.possibly_ritual, bool)

    def test_each_gap_has_opportunity(self, scanner, synthetic_scan):
        report = scanner.scan(
            synthetic_scan,
            target_state=["metodos.Meta-análise"],
        )
        gap_kinds = {o.capability for o in report.opportunities}
        assert gap_kinds == set(report.evolution_gap)

    def test_report_warnings_list(self, scanner, synthetic_scan):
        report = scanner.scan(synthetic_scan, target_state=["nao.existe"])
        assert report.warnings
        assert any("nao.existe" in w for w in report.warnings)


# ═══════════════════════════════════════════════════════════════════════
# CA9 — Anti-overclaim
# ═══════════════════════════════════════════════════════════════════════

BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]
NEGATION = ("não ", "sem ", "nunca", "vedado", "proibido", "exceto", "nenhum", "nenhuma")


class TestAntiOverclaim:
    def test_module_source_clean(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_report_string_no_claims(self, scanner, synthetic_scan):
        report = scanner.scan(
            synthetic_scan,
            target_state=["metodos.Meta-análise"],
        )
        text = str(report)
        for pattern in BANNED:
            assert not re.search(pattern, text, re.IGNORECASE), pattern


# ═══════════════════════════════════════════════════════════════════════
# CA10 — Robustez e documentação
# ═══════════════════════════════════════════════════════════════════════

class TestRobustness:
    def test_legacy_dimension_format(self, scanner):
        """Dimensão legada sem covered/absent (ex.: apenas categories) não quebra."""
        scan = {
            "dimensions": {
                "legado": {"categories": ["A", "B"]},
            }
        }
        report = scanner.scan(scan, target_state=["legado.A"], observed=[])
        assert isinstance(report, ReverseScanReport)
        assert report.evolution_gap == []

    def test_scan_without_dimensions(self, scanner):
        report = scanner.scan({}, target_state=["x.y"], observed=[])
        assert report.reverse_closure == []
        assert report.warnings

    def test_scanner_weights_custom(self):
        custom = ReverseScanner(weights={"cascade": 0.5, "centrality": 0.3,
                                          "novelty": 0.1, "ritual": 0.1})
        assert custom.weights["cascade"] == pytest.approx(0.5)
        # pesos não informados mantêm default
        partial = ReverseScanner(weights={"ritual": 0.0})
        assert partial.weights["cascade"] == pytest.approx(0.40)

    def test_no_side_effects_between_scans(self, scanner, synthetic_scan):
        a = scanner.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        b = scanner.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        c = scanner.scan(synthetic_scan, target_state=[])
        assert a == b
        assert c.reverse_closure == []
        # scan com target vazio não polui o scanner
        d = scanner.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert a == d

    def test_algorithm_documented(self):
        assert "R(F)" in MODULE_TEXT
        assert "ritual" in MODULE_TEXT
        assert "feynman-skill" in MODULE_TEXT  # atribuição epistemológica explícita