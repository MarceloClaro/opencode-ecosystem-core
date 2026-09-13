#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InertiaVectorAnalyzer v1.0 — Inércia Vetorial Analyzer (R493)

Proposta do usuário ("o que está impedindo isso de emergir?"): mesmo com
elevado potencial, relevância e aderência, uma capacidade pode não emergir —
toda evolução compete contra mecanismos de estabilidade do próprio sistema.

    PotentialityScanner (R491): "quão próximo isso está de emergir?" (coverage)
    SuccessorGenerator (R492):  "o que pode emergir?" (recombinação)
    InertiaVectorAnalyzer:      "O QUE ESTÁ IMPEDINDO ISSO DE EMERGIR?"

QIV = Potencial − Inércia, onde Inércia é a soma ponderada de 4 forças:
    complexidade  (0.30) — quanta mudança estrutural a arquitetura precisará
    dependencias  (0.30) — fração dos componentes requeridos que não existem
    custo         (0.20) — esforço estimado de materialização
    acoplamentos  (0.20) — impacto sobre módulos existentes (toque múltiplo)

Faixas (proposta do usuário):
    QIV > 0.70          → quebra-imediata    (reorganização alta)
    0.40 ≤ QIV ≤ 0.70   → quebra-moderada    (reorganização moderada)
    QIV < 0.40          → inercia-dominante  (reorganização baixa)

Tudo é HIPÓTESE (estimativa heurística determinística), nunca previsão
garantida. Pesos documentados; entrada pode vir do PotentialityReport (R491)
ou de dicts. Hermético, stdlib, anti-overclaim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scanners.potentiality_scanner import DEFAULT_MODULES

# ─── Pesos documentados (SPEC-935-R493) ─────────────────────────────────
W_COMPLEXITY = 0.30
W_DEPENDENCIES = 0.30
W_COST = 0.20
W_COUPLING = 0.20
# Fração de pesquisa/incerteza embutida no custo (constante documentada)
COST_RESEARCH_CONSTANT = 0.4
# Complexidade satura em 5 componentes (documentado: >5 = máxima)
COMPLEXITY_SATURATION = 5.0

QIV_QUEBRA_IMEDIATA = 0.70
QIV_QUEBRA_MODERADA = 0.40


@dataclass
class InertiaAssessment:
    """Avaliação de inércia vetorial para uma capacidade candidata."""
    id: str
    description: str
    requires: list[str]
    potential: float                  # latent potential score (0-1)
    complexity: float                 # 0.30 — mudança arquitetural necessária
    dependencies: float               # 0.30 — fração de bases ausentes
    cost: float                       # 0.20 — esforço estimado
    coupling: float                   # 0.20 — impacto sobre módulos existentes
    inertia: float                    # soma ponderada das 4 forças
    qiv: float                        # clamp(potencial − inércia, 0, 1)
    tier: str                         # quebra-imediata | moderada | dominante
    reorg_prediction: str             # alta | moderada | baixa (hipótese)
    critical_dependencies: list[str]  # requires ausentes do DNA
    barriers: dict[str, float]        # ranking das 4 forças (nome → valor)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "requires": list(self.requires),
            "potential": self.potential,
            "complexity": self.complexity,
            "dependencies": self.dependencies,
            "cost": self.cost,
            "coupling": self.coupling,
            "inertia": self.inertia,
            "qiv": self.qiv,
            "tier": self.tier,
            "reorg_prediction": self.reorg_prediction,
            "critical_dependencies": list(self.critical_dependencies),
            "barriers": dict(self.barriers),
        }


@dataclass
class InertiaReport:
    """Relatório de inércia vetorial."""
    assessments: list["InertiaAssessment"]
    ranking: list["InertiaAssessment"]     # por inércia desc (barreiras)
    by_id: dict[str, "InertiaAssessment"]
    params: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class InertiaVectorAnalyzer:
    """Mensura a resistência estrutural à emergência de capacidades."""

    def __init__(self, modules: dict[str, list[str]] | None = None):
        self.modules = modules if modules is not None else DEFAULT_MODULES
        self.cap_to_modules: dict[str, set[str]] = {}
        for module, caps in self.modules.items():
            for cap in caps:
                self.cap_to_modules.setdefault(cap, set()).add(module)
        self._n_modules = max(1, len(self.modules))

    # ── faixas (proposta do usuário) ────────────────────────────────────
    @staticmethod
    def _tier(qiv: float) -> str:
        if qiv > QIV_QUEBRA_IMEDIATA:
            return "quebra-imediata"
        if qiv >= QIV_QUEBRA_MODERADA:
            return "quebra-moderada"
        return "inercia-dominante"

    @staticmethod
    def _reorg_prediction(tier: str) -> str:
        return {"quebra-imediata": "alta",
                "quebra-moderada": "moderada",
                "inercia-dominante": "baixa"}[tier]

    # ── forças ──────────────────────────────────────────────────────────
    def _complexity(self, requires: list[str]) -> float:
        # mais componentes requeridos → mais mudança arquitetural (satura em 5)
        return min(1.0, len(requires) / COMPLEXITY_SATURATION)

    def _dependencies(self, requires: list[str]) -> tuple[float, list[str]]:
        if not requires:
            return 0.0, []
        missing = [r for r in requires if r not in self.cap_to_modules]
        return len(missing) / len(requires), missing

    def _coupling(self, requires: list[str]) -> float:
        # médio sobre requires: presente em k módulos → (k−1)/(n−1)
        # capability inexistente não toca módulos existentes (0)
        values: list[float] = []
        for req in requires:
            k = len(self.cap_to_modules.get(req, set()))
            if k <= 1:
                values.append(0.0)
            else:
                values.append((k - 1) / max(1, self._n_modules - 1))
        if not values:
            return 0.0
        return sum(values) / len(values)

    # ── avaliação ───────────────────────────────────────────────────────
    def evaluate(self, id: str, description: str, requires: list[str],
                 potential: float) -> InertiaAssessment:
        complexity = self._complexity(requires)
        dependencies, missing = self._dependencies(requires)
        coupling = self._coupling(requires)
        cost = (0.5 * dependencies + 0.3 * complexity
                + 0.2 * COST_RESEARCH_CONSTANT)
        inertia = (W_COMPLEXITY * complexity + W_DEPENDENCIES * dependencies
                   + W_COST * cost + W_COUPLING * coupling)
        qiv = min(1.0, max(0.0, potential - inertia))
        tier = self._tier(qiv)
        barriers = {
            "complexidade": round(complexity, 4),
            "dependencias": round(dependencies, 4),
            "custo": round(cost, 4),
            "acoplamentos": round(coupling, 4),
        }
        return InertiaAssessment(
            id=id,
            description=description,
            requires=list(requires),
            potential=round(potential, 4),
            complexity=round(complexity, 4),
            dependencies=round(dependencies, 4),
            cost=round(cost, 4),
            coupling=round(coupling, 4),
            inertia=round(inertia, 4),
            qiv=round(qiv, 4),
            tier=tier,
            reorg_prediction=self._reorg_prediction(tier),
            critical_dependencies=missing,
            barriers=barriers,
        )

    def scan(self, candidates: list[dict[str, Any]]) -> InertiaReport:
        """Avalia candidatas: dicts com id/description/requires/potential."""
        assessments = [
            self.evaluate(
                id=c.get("id", ""),
                description=c.get("description", ""),
                requires=list(c.get("requires", [])),
                potential=float(c.get("potential", 0.0)),
            )
            for c in candidates
        ]
        ranking = sorted(assessments,
                         key=lambda a: (a.inertia, -a.qiv, a.id),
                         reverse=True)
        return InertiaReport(
            assessments=assessments,
            ranking=ranking,
            by_id={a.id: a for a in assessments},
            params={
                "n_candidates": len(candidates),
                "n_modules": self._n_modules,
            },
            warnings=[],
        )

    def analyze(self, potentiality_report) -> InertiaReport:
        """Consome PotentialityReport (R491): potential = coverage."""
        candidates = [
            {
                "id": p.id,
                "description": p.description,
                "requires": p.requires,
                "potential": p.coverage,  # latent potential score
            }
            for p in getattr(potentiality_report, "candidates", [])
        ]
        return self.scan(candidates)