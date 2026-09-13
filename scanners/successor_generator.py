#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuccessorGenerator v1.0 — Gerador de Sucessores (R492)

Proposta do usuário (camada Successor Generator): novas capacidades frequentemente
emergem da RECOMBINAÇÃO de capacidades existentes — Motor + Asas + Controle
→ Avião. Nenhum componente é novo: a novidade está na combinação.

    Noological:  "o que não existe?"
    Trajectory:  "como chegar?"
    Potentiality(R491): "o que está prestes a nascer?"
    Successor:   "O QUE PODE SURGIR A PARTIR DISSO?"

Dois mecanismos:
1) SUCCESSOR_BANK — hipóteses CURADAS (exemplos do usuário):
   - Potential Discovery Engine     (gap_detection + trajectory_mapping + self_evolution)
   - Scientific Discovery Engine    (cross_validation + polymathic_reasoning + trajectory_mapping)
   - Cognitive Manifold Mapper      (gap_detection + trajectory_mapping + cross_validation)

2) Geração combinatoria controlada — pares e trios de capabilities de MÓDULOS
   DISTINTOS (recombinação inter-módulo), com heurística:

       score(combo) = 1.0·diversity + 0.5·novelty + 0.3·centrality
       diversity    = nº de módulos distintos no combo
       novelty      = 1 se combo ∉ SUCCESSOR_BANK, 0 caso contrário
       centrality   = nº de capabilities presentes em ≥2 módulos

Sucessores são HIPÓTESES (não implementações): o relatório diz o que SERIA e
que combinação o sustenta. Determinístico, stdlib, anti-overclaim.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any

# ─── Pesos da heurística (documentados na spec R492) ────────────────────
W_DIVERSITY = 1.0
W_NOVELTY = 0.5
W_CENTRALITY = 0.3


@dataclass
class SuccessorHypothesis:
    """Hipótese de sucessor (capacidade emergente por recombinação)."""
    id: str
    name: str
    description: str
    requires: list[str]
    origin: str = "generated"       # bank | generated
    novelty: int = 1
    score: float = 0.0
    function: str = ""


SUCCESSOR_BANK: list[SuccessorHypothesis] = [
    SuccessorHypothesis(
        id="potential-discovery-engine",
        name="Potential Discovery Engine",
        description="Identificar capacidades latentes ainda não modeladas no ecossistema",
        requires=["gap_detection", "trajectory_mapping", "self_evolution"],
        origin="bank",
        function="Análise de potenciais + mapeamento de trajetórias + auto evolução",
    ),
    SuccessorHypothesis(
        id="scientific-discovery-engine",
        name="Scientific Discovery Engine",
        description="Descoberta científica a partir de validação cruzada + convergência + trajetória",
        requires=["cross_validation", "polymathic_reasoning", "trajectory_mapping"],
        origin="bank",
        function="Geração de hipóteses científicas auditáveis",
    ),
    SuccessorHypothesis(
        id="cognitive-manifold-mapper",
        name="Cognitive Manifold Mapper",
        description="Mapear geometria cognitiva dos gaps do ecossistema",
        requires=["gap_detection", "trajectory_mapping", "cross_validation"],
        origin="bank",
        function="Mapa topológico de capacidades e lacunas",
    ),
]


@dataclass
class SuccessorsReport:
    """Catálogo de sucessores: curados (bank) + gerados + ranking."""
    bank: list["SuccessorHypothesis"]
    generated: list["SuccessorHypothesis"]
    ranking: list["SuccessorHypothesis"]
    by_id: dict[str, "SuccessorHypothesis"]
    params: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class SuccessorGenerator:
    """Gera hipóteses de sucessores por recombinação estrutural de capabilities."""

    def __init__(self, modules: dict[str, list[str]]):
        self.modules = modules
        self.cap_to_modules = self._index()
        self.central = self._central()

    def _index(self) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for module, caps in self.modules.items():
            for cap in caps:
                out.setdefault(cap, set()).add(module)
        return out

    def _central(self) -> set[str]:
        seen: set[str] = set()
        dup: set[str] = set()
        for module, caps in self.modules.items():
            for cap in caps:
                if cap in seen:
                    dup.add(cap)
                seen.add(cap)
        return dup

    def _diversity(self, combo: tuple[str, ...]) -> int:
        mods: set[str] = set()
        for cap in combo:
            mods.update(self.cap_to_modules.get(cap, set()))
        return len(mods)

    def _score(self, combo: tuple[str, ...], bank_sets: set[frozenset[str]]) -> float:
        diversity = self._diversity(combo)
        novelty = 0 if frozenset(combo) in bank_sets else 1
        centrality = sum(1 for cap in combo if cap in self.central)
        return round(W_DIVERSITY * diversity + W_NOVELTY * novelty + W_CENTRALITY * centrality, 4)

    def generate(self, max_combos: int = 12) -> list[SuccessorHypothesis]:
        """Pares e trios de capabilities de módulos distintos, ordenados por score."""
        caps = sorted(self.cap_to_modules)
        bank_sets = {frozenset(h.requires) for h in SUCCESSOR_BANK if h.origin == "bank"}
        candidates: list[SuccessorHypothesis] = []
        counter = 0
        for size in (2, 3):
            for combo in itertools.combinations(caps, size):
                if self._diversity(combo) < 2:
                    continue  # recombinação inter-módulo apenas
                if frozenset(combo) in bank_sets:
                    continue
                name = "Hypothesis " + "-".join(combo).replace("_", "-")
                candidates.append(
                    SuccessorHypothesis(
                        id=f"succ-{'-'.join(combo)}",
                        name=name,
                        description="Hipótese combinatoria: " + " + ".join(combo),
                        requires=list(combo),
                        origin="generated",
                        novelty=1,
                        score=self._score(combo, bank_sets),
                    )
                )
        candidates.sort(key=lambda h: (-h.score, h.id))
        return candidates[:max_combos]

    def scan(self, max_combos: int = 12) -> SuccessorsReport:
        """Relatório completo: bank (curado) + gerados + ranking."""
        bank_scored: list[SuccessorHypothesis] = []
        bank_sets = {frozenset(h.requires) for h in SUCCESSOR_BANK if h.origin == "bank"}
        for h in SUCCESSOR_BANK:
            combo = tuple(h.requires)
            score = self._score(combo, bank_sets)
            scored = SuccessorHypothesis(
                id=h.id, name=h.name, description=h.description,
                requires=list(h.requires), origin=h.origin,
                novelty=int(frozenset(combo) not in bank_sets),
                score=score, function=h.function,
            )
            bank_scored.append(scored)
        generated = self.generate(max_combos=max_combos)
        ranking = sorted(bank_scored + generated, key=lambda h: (-h.score, h.id))
        by_id = {h.id: h for h in bank_scored + generated}
        return SuccessorsReport(
            bank=bank_scored,
            generated=generated,
            ranking=ranking,
            by_id=by_id,
            params={
                "bank_entries": len(bank_scored),
                "generated": len(generated),
                "capabilities": len(self.cap_to_modules),
                "max_combos": max_combos,
            },
            warnings=[],
        )