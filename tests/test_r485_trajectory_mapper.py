# -*- coding: utf-8 -*-
"""Testes do TrajectoryMapper (R485) — Mapa de Trajetórias Evolutivas.

Progressão: ERRO → AUSÊNCIA → OPORTUNIDADE (R483) → TRAJETÓRIAS (R485).

Enumeras rotas de construção de cada g ∈ Δ até F no grafo de pré-requisitos
(mesma semântica do R483) e agrega lever score (betweenness aproximado).

Hermético: sem rede, sem credenciais, sem código de terceiros.
"""

from __future__ import annotations

import re

import pytest

from scanners.reverse_scanner import ReverseScanner
from scanners.trajectory_mapper import (
    Lever,
    TrajectoryMapper,
    TrajectoryOpportunity,
    TrajectoryMapReport,
)

MODULE_TEXT = (
    __import__("pathlib").Path(__file__).resolve().parent.parent
    / "scanners" / "trajectory_mapper.py"
).read_text(encoding="utf-8")

BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]


@pytest.fixture(scope="module")
def mapper() -> TrajectoryMapper:
    return TrajectoryMapper()


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
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# CA1 — Caminhos
# ═══════════════════════════════════════════════════════════════════════

class TestPaths:
    def test_single_prereq_line(self, mapper, synthetic_scan):
        graph = mapper.build_graph(synthetic_scan)
        # Dedutivo é prereq de Probabilístico (requires) => caminho de construção
        paths = mapper.paths_between(graph, "raciocinio.Dedutivo", ["raciocinio.Probabilístico"], max_depth=4, max_paths=10)
        assert ["raciocinio.Dedutivo", "raciocinio.Probabilístico"] in paths

    def test_succ_direction(self, mapper, synthetic_scan):
        # Meta-análise requer Probabilístico => Prob é construído antes de Meta
        graph = mapper.build_graph(synthetic_scan)
        paths = mapper.paths_between(graph, "raciocinio.Probabilístico", ["metodos.Meta-análise"], max_depth=4, max_paths=10)
        assert ["raciocinio.Probabilístico", "metodos.Meta-análise"] in paths

    def test_multiple_routes(self, mapper, synthetic_scan):
        graph = mapper.build_graph(synthetic_scan)
        # Meta-análise tem 2 prereqs diretos: Probabilístico e Metadados
        paths = mapper.paths_between(graph, "metodos.Meta-análise", ["metodos.Meta-análise"], max_depth=2, max_paths=10)
        # caminho de comprimento 1 (identidade) está presente
        assert ["metodos.Meta-análise"] in paths

    def test_depth_limit_respected(self, mapper, synthetic_scan):
        graph = mapper.build_graph(synthetic_scan)
        paths = mapper.paths_between(graph, "metodos.Meta-análise", ["metodos.Meta-análise"], max_depth=0, max_paths=10)
        # max_depth=0 apenas o próprio nó (identidade)
        assert all(len(p) == 1 for p in paths)
        assert paths == [["metodos.Meta-análise"]]

    def test_no_path_between_disconnected(self, mapper, synthetic_scan):
        graph = mapper.build_graph(synthetic_scan)
        paths = mapper.paths_between(graph, "dados.Metadados (revisões)", ["raciocinio.Dedutivo"], max_depth=4, max_paths=10)
        assert paths == []

    def test_paths_no_cycles_in_path(self, mapper, synthetic_scan):
        graph = mapper.build_graph(synthetic_scan)
        paths = mapper.paths_between(graph, "metodos.Meta-análise", ["metodos.Meta-análise"], max_depth=6, max_paths=100)
        for path in paths:
            assert len(path) == len(set(path)), f"ciclo dentro do caminho: {path}"

    def test_max_paths_cap(self, mapper, synthetic_scan):
        graph = mapper.build_graph(synthetic_scan)
        paths = mapper.paths_between(graph, "metodos.Meta-análise", ["metodos.Meta-análise"], max_depth=6, max_paths=1)
        assert len(paths) <= 1


# ═══════════════════════════════════════════════════════════════════════
# CA5 — Lever score em grafo controlado
# ═══════════════════════════════════════════════════════════════════════

class TestLevers:
    def test_shared_node_is_lever(self, mapper):
        # grafo controlado: dois gaps {X, Y} com caminhos até F ambos passando por HUB
        scan = {
            "dimensions": {
                "a": {"covered": [], "absent": ["X"]},
                "b": {"covered": [], "absent": ["Y"]},
                "h": {"covered": [], "absent": ["HUB"]},
                "f": {"covered": [], "absent": ["F"]},
            }
        }
        # Forçamos arestas via regras reais não disponíveis...
        # Em vez disso, testamos lever com o agregador sobre paths manuais.
        paths = [
            ["a.X", "h.HUB", "f.F"],
            ["b.Y", "h.HUB", "f.F"],
        ]
        levers = mapper.compute_levers(paths)
        hub = next(l for l in levers if l.capability == "h.HUB")
        assert hub.count == 2
        assert hub.lever_score == pytest.approx(1.0)
        # topo da lista = contagem máxima (HUB e F empatam em 2; desempate lexical não é contrato)
        assert levers[0].count == 2

    def test_lever_scores_normalized(self, mapper):
        paths = [
            ["a.X", "h.HUB", "f.F"],
            ["b.Y", "h.HUB", "f.F"],
        ]
        levers = mapper.compute_levers(paths)
        for lever in levers:
            assert 0.0 <= lever.lever_score <= 1.0
        # HUB é o top; score do HUB = 1.0; F também aparece em 2 caminhos
        by_cap = {l.capability: l for l in levers}
        assert by_cap["f.F"].lever_score == pytest.approx(1.0)
        assert by_cap["a.X"].lever_score == pytest.approx(0.5)

    def test_empty_paths_no_levers(self, mapper):
        assert mapper.compute_levers([]) == []


# ═══════════════════════════════════════════════════════════════════════
# CA4/CA6/CA7 — Mapa completo
# ═══════════════════════════════════════════════════════════════════════

class TestMap:
    def test_integration_with_reverse_scanner(self, mapper, synthetic_scan):
        report = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert isinstance(report, TrajectoryMapReport)
        assert report.paths
        assert any("metodos.Meta-análise" in p for p in report.paths)
        # Probabilístico é pré-requisito de Meta-análise: entra em alguma rota
        assert any("raciocinio.Probabilístico" in p for p in report.paths)

    def test_lever_probabilistico_structural(self, mapper, synthetic_scan):
        report = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        levers = {l.capability: l for l in report.levers}
        # Probabilístico habilita Meta-análise e é requisitado por outras rotas
        assert "raciocinio.Probabilístico" in levers
        assert levers["raciocinio.Probabilístico"].lever_score > 0

    def test_opportunities_enriched(self, mapper, synthetic_scan):
        report = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        for opp in report.opportunities:
            assert isinstance(opp, TrajectoryOpportunity)
            assert 0.0 <= opp.potential <= 1.0
            assert 0.0 <= opp.lever_score <= 1.0
            assert opp.combined == pytest.approx(0.70 * opp.potential + 0.30 * opp.lever_score)
            assert opp.tier in {"alavanca estrutural", "alavanca", "prioritaria", "marginal", "ritual"}
            assert isinstance(opp.possibly_ritual, bool)

    def test_one_opportunity_per_gap(self, mapper, synthetic_scan):
        report = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        gap_kinds = {o.capability for o in report.opportunities}
        assert gap_kinds == set(report.evolution_gap)

    def test_determinism(self, mapper, synthetic_scan):
        a = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        b = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert a.paths == b.paths
        assert a.levers == b.levers
        assert a.opportunities == b.opportunities

    def test_params_exposed(self, mapper, synthetic_scan):
        report = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert report.params["max_depth"] == 6
        assert report.params["max_paths"] == 50
        assert report.params["combined_weights"]["potential"] == pytest.approx(0.70)
        assert report.params["combined_weights"]["lever"] == pytest.approx(0.30)


# ═══════════════════════════════════════════════════════════════════════
# CA8/CA9/CA10 — Qualidade
# ═══════════════════════════════════════════════════════════════════════

class TestQuality:
    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_no_anti_overclaim_report(self, mapper, synthetic_scan):
        report = mapper.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        for pattern in BANNED:
            assert not re.search(pattern, str(report), re.IGNORECASE), pattern

    def test_empty_targets(self, mapper, synthetic_scan):
        report = mapper.scan(synthetic_scan, target_state=[])
        assert report.paths == []
        assert report.opportunities == []

    def test_legacy_dimension_format(self, mapper):
        scan = {"dimensions": {"legado": {"categories": ["A"]}}}
        report = mapper.scan(scan, target_state=["legado.A"])
        assert report.paths == []

    def test_algorithm_documented(self):
        assert "lever_score" in MODULE_TEXT
        assert "max_depth" in MODULE_TEXT
        assert "prereqs" in MODULE_TEXT