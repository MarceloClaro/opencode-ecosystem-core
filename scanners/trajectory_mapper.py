#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrajectoryMapper v1.0 — Mapa de Trajetórias Evolutivas (R485)

Progressão do usuário:
    ERRO → AUSÊNCIA → OPORTUNIDADE (R483) → **TRAJETÓRIAS** (este módulo) → convergência (R486)

Complementa o ReverseScanner (R483): em vez de apenas listar o gap Δ, enumera
**todas as rotas de construção** de cada lacuna até o estado futuro F no grafo
de pré-requisitos, e agrega **alavancas estruturais** (nós que aparecem em
muitos caminhos → construir primeiro destrava múltiplas rotas).

Formalização (mesma semântica de pré-requisito do R483):

    prereqs(X) = { T : edge(source=X, target=T, relation="requires") }
               ∪ { S : edge(source=S, target=X, relation="enables") }

Caminho: sequência [v1, v2, ..., vk] com v1 ∈ Δ, vk ∈ F, vi prereq de v(i+1),
sem revisitar nós (anti-ciclo), limites max_depth (default 6) e max_paths
(default 50) — anti-explosão — com ordenação lexicográfica (determinismo).

Lever score:

    count(c)     = nº de caminhos (todos os pares g∈Δ → F) que contêm c
    lever_score(c) = count(c) / max_count      (0 se max_count = 0)

Oportunidade enriquecida (para cada g ∈ Δ):

    combined(p, lever) = 0.70·p + 0.30·lever    (pesos default)
    tier: "ritual" (herdado) > "alavanca estrutural" (combined≥0.7 e lever≥0.6)
          > "alavanca" (≥0.7) > "prioritaria" (≥0.4) > "marginal"

100% stdlib, hermético. Não modifica R483/R482.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scanners.cross_validation_engine import CrossValidationEngine
from scanners.reverse_scanner import ReverseScanner

DEFAULT_MAX_DEPTH = 6
DEFAULT_MAX_PATHS = 50
DEFAULT_COMBINED_WEIGHTS = {"potential": 0.70, "lever": 0.30}


@dataclass
class Lever:
    """Alavanca estrutural: capacidade presente em muitos caminhos."""
    capability: str
    count: int
    lever_score: float


@dataclass
class TrajectoryOpportunity:
    """Gap do R483 enriquecido com lever score e tier combinado."""
    capability: str
    domain: str
    potential: float
    lever_score: float
    combined: float
    tier: str
    possibly_ritual: bool = False


@dataclass
class TrajectoryMapReport:
    """Relatório do mapa de trajetórias."""
    target_state: list[str]
    evolution_gap: list[str]
    paths: list[list[str]]
    levers: list["Lever"]
    opportunities: list["TrajectoryOpportunity"]
    params: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


class TrajectoryMapper:
    """Enumerador de rotas de construção e detector de alavancas estruturais."""

    def __init__(self):
        self._cv = CrossValidationEngine()

    # ─── GRAFO ────────────────────────────────────────────────────────────

    def build_graph(self, noological_scan: dict[str, Any]) -> dict[str, Any]:
        return self._cv.build_graph(noological_scan)

    def _prereqs(self, node_key: str) -> list[str]:
        """Pré-requisitos diretos de `node_key` (mesma semântica do R483).

        requires: edge(source=S, target=T) ⇒ S requer T ⇒ T é prereq de S;
        enables : edge(source=S, target=T) ⇒ S habilita T ⇒ S é prereq de T;
        co_occurs: não participa.
        """
        prereqs: list[str] = []
        for e in self._cv.edges:
            if e.relation == "requires" and e.source == node_key:
                prereqs.append(e.target)
            elif e.relation == "enables" and e.target == node_key:
                prereqs.append(e.source)
        seen: set[str] = set()
        ordered: list[str] = []
        for p in prereqs:
            if p not in seen and p in self._cv.nodes:
                seen.add(p)
                ordered.append(p)
        return ordered

    def _succ(self, node_key: str) -> list[str]:
        """Sucessores de construção de `node_key` (inverso dos prereqs).

        Y é sucessor de X se X ∈ prereqs(Y): construir X primeiro destrava Y.
          requires: edge(source=S, target=T) ⇒ S requer T ⇒ S é successor de T;
          enables : edge(source=S, target=T) ⇒ S habilita T ⇒ T é successor de S.
        """
        succ: list[str] = []
        for e in self._cv.edges:
            if e.relation == "requires" and e.target == node_key:
                succ.append(e.source)
            elif e.relation == "enables" and e.source == node_key:
                succ.append(e.target)
        seen: set[str] = set()
        ordered: list[str] = []
        for s in succ:
            if s not in seen and s in self._cv.nodes:
                seen.add(s)
                ordered.append(s)
        return ordered

    # ─── CAMINHOS (CA1-CA3) ──────────────────────────────────────────────

    def paths_between(
        self,
        graph: dict[str, Any],
        start: str,
        targets: list[str],
        max_depth: int = DEFAULT_MAX_DEPTH,
        max_paths: int = DEFAULT_MAX_PATHS,
    ) -> list[list[str]]:
        """Todas as rotas de `start` até qualquer alvo em `targets`.

        DFS determinística (vizinhos ordenados), anti-ciclo, com identidade
        [start] quando start ∈ targets. Caminho termina no primeiro alvo.
        """
        target_set = set(targets)
        paths: list[list[str]] = []

        def dfs(node: str, path: list[str]) -> None:
            if len(paths) >= max_paths:
                return
            if node in target_set:
                paths.append(list(path))
                return
            if len(path) >= max_depth + 1:
                return
            for nxt in sorted(self._succ(node)):
                if nxt not in path:
                    dfs(nxt, path + [nxt])

        dfs(start, [start])
        return sorted(paths)

    # ─── LEVERS (CA5) ────────────────────────────────────────────────────

    @staticmethod
    def compute_levers(paths: list[list[str]]) -> list[Lever]:
        """Contagem de presença por capacidade e lever score normalizado."""
        counts: dict[str, int] = {}
        for path in paths:
            for cap in path:
                counts[cap] = counts.get(cap, 0) + 1
        if not counts:
            return []
        max_count = max(counts.values())
        levers = sorted(
            (
                Lever(
                    capability=cap,
                    count=n,
                    lever_score=round(n / max_count, 4),
                )
                for cap, n in counts.items()
            ),
            key=lambda l: (-l.count, l.capability),
        )
        return levers

    # ─── TIER COMBINADO (CA7) ────────────────────────────────────────────

    @staticmethod
    def _tier(combined: float, lever: float, possibly_ritual: bool) -> str:
        if possibly_ritual:
            return "ritual"
        if combined >= 0.7 and lever >= 0.6:
            return "alavanca estrutural"
        if combined >= 0.7:
            return "alavanca"
        if combined >= 0.4:
            return "prioritaria"
        return "marginal"

    # ─── SCAN ORQUESTRADO (CA4/CA6/CA8-CA10) ─────────────────────────────

    def scan(
        self,
        noological_scan: dict[str, Any],
        target_state: list[str],
        observed: list[str] | None = None,
        corpus_terms: list[str] | None = None,
        exemplars: list[list[str]] | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
        max_paths: int = DEFAULT_MAX_PATHS,
        combined_weights: dict[str, float] | None = None,
    ) -> TrajectoryMapReport:
        """Mapa completo: Δ do R483 → rotas → alavancas → oportunidades."""
        weights = dict(DEFAULT_COMBINED_WEIGHTS)
        if combined_weights:
            weights.update(
                {k: v for k, v in combined_weights.items() if k in DEFAULT_COMBINED_WEIGHTS}
            )

        rs = ReverseScanner()
        base = rs.scan(
            noological_scan,
            target_state=target_state,
            observed=observed,
            corpus_terms=corpus_terms,
            exemplars=exemplars,
        )

        self.build_graph(noological_scan)
        paths: list[list[str]] = []
        for gap in base.evolution_gap:
            paths.extend(
                self.paths_between(
                    self._cv.nodes, gap, target_state,
                    max_depth=max_depth, max_paths=max_paths,
                )
            )
        # determinismo global (paths_between já ordena por start; concatenação
        # na ordem de Δ que é lexicográfica no R483)
        paths = sorted(paths)

        levers = self.compute_levers(paths)
        lever_by_cap = {l.capability: l.lever_score for l in levers}

        opportunities: list[TrajectoryOpportunity] = []
        for opp in base.opportunities:
            lev = lever_by_cap.get(opp.capability, 0.0)
            combined = round(
                weights["potential"] * opp.potential
                + weights["lever"] * lev,
                4,
            )
            opportunities.append(
                TrajectoryOpportunity(
                    capability=opp.capability,
                    domain=opp.domain,
                    potential=opp.potential,
                    lever_score=lev,
                    combined=combined,
                    tier=self._tier(combined, lev, opp.possibly_ritual),
                    possibly_ritual=opp.possibly_ritual,
                )
            )

        return TrajectoryMapReport(
            target_state=list(base.target_state),
            evolution_gap=list(base.evolution_gap),
            paths=paths,
            levers=levers,
            opportunities=opportunities,
            params={
                "max_depth": max_depth,
                "max_paths": max_paths,
                "combined_weights": dict(weights),
            },
            warnings=list(base.warnings),
        )