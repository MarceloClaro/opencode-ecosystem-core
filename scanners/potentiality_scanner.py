#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PotentialityScanner v1.0 — Scanner de Potenciais Latentes (R491)

Proposta do usuário (camada Potentiality): responder **"o que está prestes a
nascer?"** — capacidades emergentes cujos componentes estruturais já estão
parcialmente presentes no ecossistema. Inspiração: o avião surgiu da
convergência de aerodinâmica, materiais e propulsão — nenhum componente novo,
a novidade foi a combinação.

    Noological/Teleological...: "o que não existe / deveria existir?"
    ReverseScanner (R483):      "o que é necessário?"
    KnowledgeComposition (R490): "do que isso é feito?"
    PotentialityScanner:        "o que pode emergir da estrutura atual?"

Módulos desta revisão:
    1. StructuralDNA — catálogo declarativo módulos → capabilities;
       expõe capabilities, redundant (cap em >1 módulo) e central.
    2. Emergence Scan — para cada candidata (hipótese de latentidade) computa:
       coverage(c)   = |requires(c) ∩ dna.capabilities| / |requires(c)|
       missing(c)    = requires(c) - dna.capabilities
       resistencia(c)= 1 - coverage(c)
       tier(c)       = 'latente-alto' se coverage ≥ 0.66
                       'emergente'    se coverage ≥ 0.34
                       'distante'     caso contrário

Candidatas são hipóteses (curadoria humana ou geradas pelo Successor R492);
o relatório informa o que FALTA para a capacidade emergir. Determinístico,
stdlib, anti-overclaim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Limiares de tiering documentados (não mágicos)
# latente-alto exige ≥ 3/4 dos componentes presentes; emergente ≥ 1/3
TIER_LATENTE_ALTO = 0.75
TIER_EMERGENTE = 0.34


@dataclass
class StructuralDNA:
    """Mapa de capacidades fundamentais do ecossistema (declarativo)."""
    modules: dict[str, list[str]]

    @property
    def capabilities(self) -> set[str]:
        """Todas as capabilities declaradas nos módulos."""
        out: set[str] = set()
        for caps in self.modules.values():
            out.update(caps)
        return out

    @property
    def redundant(self) -> set[str]:
        """Capabilities declaradas em mais de um módulo."""
        seen: set[str] = set()
        dup: set[str] = set()
        for caps in self.modules.values():
            for c in caps:
                if c in seen:
                    dup.add(c)
                seen.add(c)
        return dup

    @property
    def central(self) -> set[str]:
        """Capacidades centrais: presentes em ≥2 módulos."""
        return self.redundant


@dataclass
class PotentialityCandidate:
    """Hipótese de capacidade latente (a avaliar pelo scanner)."""
    id: str
    description: str
    requires: list[str]


@dataclass
class Potentiality:
    """Resultado da avaliação de uma candidata."""
    id: str
    description: str
    requires: list[str]
    coverage: float
    missing: list[str]
    resistencia: float
    tier: str


@dataclass
class PotentialityReport:
    """Relatório de potencialidades latentes."""
    candidates: list["Potentiality"]
    by_id: dict[str, "Potentiality"]
    params: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class PotentialityScanner:
    """Avalia candidatas a capacidade latente contra o DNA estrutural."""

    def __init__(self, modules: dict[str, list[str]]):
        self.dna = StructuralDNA(modules=modules)

    @staticmethod
    def _resolve(candidate: PotentialityCandidate, dna_caps: set[str]) -> Potentiality:
        requires = list(candidate.requires)
        n = len(requires)
        if n == 0:
            coverage, missing = 0.0, []
        else:
            present = [r for r in requires if r in dna_caps]
            coverage = len(present) / n
            missing = [r for r in requires if r not in dna_caps]
        if coverage >= TIER_LATENTE_ALTO:
            tier = "latente-alto"
        elif coverage >= TIER_EMERGENTE:
            tier = "emergente"
        else:
            tier = "distante"
        return Potentiality(
            id=candidate.id,
            description=candidate.description,
            requires=requires,
            coverage=round(coverage, 4),
            missing=missing,
            resistencia=round(1 - coverage, 4),
            tier=tier,
        )

    def scan(self, candidates: list[PotentialityCandidate]) -> PotentialityReport:
        """Avalia todas as candidatas em ordem estável."""
        results: list[Potentiality] = []
        by_id: dict[str, Potentiality] = {}
        dna_caps = self.dna.capabilities
        for cand in candidates:
            p = self._resolve(cand, dna_caps)
            results.append(p)
            by_id[p.id] = p
        return PotentialityReport(
            candidates=results,
            by_id=by_id,
            params={
                "n_candidates": len(candidates),
                "dna_capabilities": len(dna_caps),
            },
            warnings=[],
        )