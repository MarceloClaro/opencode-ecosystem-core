#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReverseScanner v1.0 — Scanner Reverso de Trajetórias Evolutivas (R483)

Direção de inferência oposta ao Scanner Noológico:

    noológico   : presente  → incompletude           (indução sobre o presente)
    reverso     : desejado  → pré-requisitos mínimos (dedução regressiva a partir do futuro)

Formalização sobre o grafo de capacidades do CrossValidationEngine:

    G = (C, D)   grafo (nós = capacidades; arestas dirigidas)
    A            capacidades observadas (covered do scan noológico)
    F            estado futuro desejado (target_state)
    R(F)         fecho regressivo de F em G  (pré-requisitos transitivos)
    Δ = R(F) - A gap evolutivo

Potencial de cada g ∈ Δ (componentes normalizados em [0, 1]):

    p(g) = α·cascade_norm(g) + β·centrality_norm(g) + γ·novelty(g) − δ·ritual(g)
    α=0.40  β=0.25  γ=0.20  δ=0.15    (default; α+β+γ+δ = 1)

    cascade_norm   impacto em cascata (CrossValidationEngine.cascade_impact),
                   normalizado pelo máximo de Δ (0 se máximo = 0)
    centrality_norm influence_score do nó (bottleneck do build_graph),
                   normalizado pelo máximo de Δ
    novelty        1 − overlap(tokens(capacidade), corpus_terms);
                   sem corpus → 1.0 (capacidade não indexada = máxima novidade;
                   caso documentado, não oculto)
    ritual         fração de exemplares bem-sucedidos que NÃO possuem g
                   (teste anti-cargo-cult inspirado no feynman-skill: distinguir
                   lacuna genuína de lacuna ritual); sem exemplares → 0.0
                   (neutro: sem dados não se pune)

Tiering:  ritual ≥ 0.5 → "ritual";  p ≥ 0.70 → "alavanca";
          0.40 ≤ p < 0.70 → "prioritaria";  p < 0.40 → "marginal".

100% stdlib, hermético (sem rede, sem credenciais, sem código de terceiros).
Atribuições epistemológicas: feynman-skill (MIT) — anti-cargo-cult;
feynman (MIT) — execução futura de pesquisa; bernstein (Apache-2.0) —
execução futura do roadmap. Nenhum código desses projetos foi copiado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from scanners.cross_validation_engine import CrossValidationEngine

DEFAULT_WEIGHTS: dict[str, float] = {
    "cascade": 0.40,
    "centrality": 0.25,
    "novelty": 0.20,
    "ritual": 0.15,
}

_TOKEN_RE = re.compile(r"[a-zà-ÿ0-9]+", re.IGNORECASE)


@dataclass
class ReverseOpportunity:
    """Uma capacidade do gap evolutivo com pontuação completa."""
    capability: str
    domain: str
    potential: float
    cascade: float
    centrality: float
    novelty: float
    ritual: float
    tier: str
    possibly_ritual: bool = False


@dataclass
class ReverseScanReport:
    """Relatório auditável do fecho reverso e do gap evolutivo."""
    target_state: list[str]
    observed_capabilities: list[str]
    reverse_closure: list[str]
    evolution_gap: list[str]
    opportunities: list["ReverseOpportunity"]
    params: dict[str, float]
    warnings: list[str] = field(default_factory=list)


class ReverseScanner:
    """Planejador estrutural do futuro: do estado desejado aos pré-requisitos mínimos.

    Reutiliza o CrossValidationEngine (grafo de dependências) e o formato de
    scan do NoologicalScanner (dimensões com `covered`/`absent`).
    """

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights: dict[str, float] = dict(DEFAULT_WEIGHTS)
        if weights:
            self.weights.update({k: v for k, v in weights.items() if k in DEFAULT_WEIGHTS})
        self._cv = CrossValidationEngine()

    # ─── GRAFO ────────────────────────────────────────────────────────────

    def build_graph(self, noological_scan: dict[str, Any]) -> dict[str, Any]:
        """Constrói (ou reconstrói) o grafo de capacidades do scan."""
        return self._cv.build_graph(noological_scan)

    # ─── FECHO REGRESSIVO (CA1-CA3) ───────────────────────────────────────

    def _prereqs(self, node_key: str) -> list[str]:
        """Pré-requisitos diretos de `node_key` no grafo atual.

        Semântica do CrossValidationEngine:
          requires: edge(source=S, target=T) ⇒ S requer T ⇒ T é prereq de S;
          enables : edge(source=S, target=T) ⇒ S habilita T ⇒ S é prereq de T;
          co_occurs: não participa da regressão.
        """
        prereqs: list[str] = []
        for e in self._cv.edges:
            if e.relation == "requires" and e.source == node_key:
                prereqs.append(e.target)
            elif e.relation == "enables" and e.target == node_key:
                prereqs.append(e.source)
        # deduplicar preservando ordem
        seen: set[str] = set()
        ordered: list[str] = []
        for p in prereqs:
            if p not in seen and p in self._cv.nodes:
                seen.add(p)
                ordered.append(p)
        return ordered

    def reverse_closure(
        self,
        graph: dict[str, Any],
        target_state: list[str],
        observed: list[str] | None = None,
    ) -> list[str]:
        """Fecho regressivo R(F) restrito ao grafo.

        Percorre prereqs transitivamente, **parando em capacidades observadas**
        (poda em A: não se planeja o que já se tem). Tolerante a ciclos
        (visita única) e a chaves fora do grafo (ignoradas).
        """
        observed_set = set(observed or [])
        stack = list(target_state)
        closure: list[str] = []
        visited: set[str] = set()

        while stack:
            key = stack.pop()
            if key in visited or key not in self._cv.nodes:
                continue
            visited.add(key)
            closure.append(key)
            if key in observed_set:
                continue  # poda: capacidade já observada, não retrocede
            for prereq in self._prereqs(key):
                if prereq not in visited:
                    stack.append(prereq)
        return sorted(closure)

    # ─── GAP EVOLUTIVO (CA4) ──────────────────────────────────────────────

    @staticmethod
    def evolution_gap(
        reverse_closure: list[str],
        observed: list[str] | None = None,
    ) -> list[str]:
        """Δ = R(F) - A, ordenado lexicograficamente (determinismo)."""
        observed_set = set(observed or [])
        return sorted(c for c in reverse_closure if c not in observed_set)

    # ─── COMPONENTES (CA5) ────────────────────────────────────────────────

    @staticmethod
    def ritual(capability: str, exemplars: list[list[str]] | None = None) -> float:
        """Fração de exemplares bem-sucedidos que NÃO possuem `capability`.

        Anti-cargo-cult (feynman-skill): se vários sistemas que atingiram F não
        tinham a capacidade, ela pode ser lacuna ritual. Sem exemplares → 0.0
        (neutro: sem dados não se pune).
        """
        if not exemplars:
            return 0.0
        missing = sum(1 for ex in exemplars if capability not in ex)
        return round(missing / len(exemplars), 4)

    @staticmethod
    def novelty(capability: str, corpus_terms: list[str] | None = None) -> float:
        """1 − overlap(tokens(capacidade), corpus_terms).

        Sem corpus → 1.0 (capacidade não indexada = máxima novidade).
        """
        tokens = set(_TOKEN_RE.findall(capability.lower()))
        if not corpus_terms or not tokens:
            return 1.0
        corpus = {t.lower() for t in corpus_terms}
        overlap = len(tokens & corpus) / len(tokens)
        return round(1.0 - overlap, 4)

    # ─── POTENCIAL (CA6) ──────────────────────────────────────────────────

    def potential(
        self,
        capability: str,
        cascade_map: dict[str, float],
        centrality_map: dict[str, float],
        corpus_terms: list[str] | None = None,
        exemplars: list[list[str]] | None = None,
    ) -> float:
        """p(g) = α·cascade_norm + β·centrality_norm + γ·novelty − δ·ritual, clamp [0,1]."""
        gap_keys = [k for k in cascade_map if k in centrality_map] or [capability]
        max_cascade = max((cascade_map.get(k, 0.0) for k in gap_keys), default=0.0)
        max_centrality = max((centrality_map.get(k, 0.0) for k in gap_keys), default=0.0)

        c_norm = (cascade_map.get(capability, 0.0) / max_cascade) if max_cascade > 0 else 0.0
        b_norm = (centrality_map.get(capability, 0.0) / max_centrality) if max_centrality > 0 else 0.0
        n_val = self.novelty(capability, corpus_terms)
        r_val = self.ritual(capability, exemplars)

        p = (
            self.weights["cascade"] * c_norm
            + self.weights["centrality"] * b_norm
            + self.weights["novelty"] * n_val
            - self.weights["ritual"] * r_val
        )
        return round(max(0.0, min(1.0, p)), 4)

    @staticmethod
    def _tier(potential: float, ritual_val: float) -> str:
        if ritual_val >= 0.5:
            return "ritual"
        if potential >= 0.70:
            return "alavanca"
        if potential >= 0.40:
            return "prioritaria"
        return "marginal"

    # ─── SCAN ORQUESTRADO (CA7-CA10) ──────────────────────────────────────

    def scan(
        self,
        noological_scan: dict[str, Any],
        target_state: list[str],
        observed: list[str] | None = None,
        corpus_terms: list[str] | None = None,
        exemplars: list[list[str]] | None = None,
    ) -> ReverseScanReport:
        """Executa o pipeline completo: grafo → R(F) → Δ → potenciais → relatório."""
        warnings: list[str] = []

        dims = noological_scan.get("dimensions", {}) or {}
        observed_capabilities = list(observed or [])
        if observed is None:
            for dim_key, dim_data in dims.items():
                for cat in (dim_data or {}).get("covered", []):
                    observed_capabilities.append(f"{dim_key}.{cat}")

        # Chaves de F fora do grafo viram aviso (e são ignoradas).
        self.build_graph(noological_scan)
        for t in target_state:
            if t not in self._cv.nodes:
                warnings.append(f"target_state '{t}' fora do grafo — ignorado")

        closure = self.reverse_closure(
            self._cv.nodes, target_state, observed=observed_capabilities
        )
        gap = self.evolution_gap(closure, observed=observed_capabilities)

        unnormalized_gap = gap or closure
        cascade_raw = self._cv.cascade_impact(noological_scan)
        max_cascade = max((cascade_raw.get(k, 0.0) for k in unnormalized_gap), default=0.0)
        max_centr = max(
            (self._cv.nodes.get(k).influence_score for k in unnormalized_gap),
            default=0.0,
        )

        opportunities: list[ReverseOpportunity] = []
        for g in gap:
            c_norm = (cascade_raw.get(g, 0.0) / max_cascade) if max_cascade > 0 else 0.0
            b_norm = (
                (self._cv.nodes[g].influence_score / max_centr) if max_centr > 0 else 0.0
            )
            n_val = self.novelty(g, corpus_terms)
            r_val = self.ritual(g, exemplars)
            p = self.potential(g, {g: c_norm + 1e-9}, {g: b_norm + 1e-9}, corpus_terms, exemplars)

            domain = g.split(".", 1)[0] if "." in g else "raiz"
            opportunities.append(
                ReverseOpportunity(
                    capability=g,
                    domain=domain,
                    potential=p,
                    cascade=round(c_norm, 4),
                    centrality=round(b_norm, 4),
                    novelty=n_val,
                    ritual=r_val,
                    tier=self._tier(p, r_val),
                    possibly_ritual=(r_val >= 0.5),
                )
            )

        return ReverseScanReport(
            target_state=list(target_state),
            observed_capabilities=sorted(observed_capabilities),
            reverse_closure=closure,
            evolution_gap=gap,
            opportunities=opportunities,
            params=dict(self.weights),
            warnings=warnings,
        )