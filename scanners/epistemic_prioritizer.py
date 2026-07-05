# -*- coding: utf-8 -*-
"""
EpistemicPrioritizer — Estimador de Potencial Epistemológico (SPEC-020).

Completa a progressão proposta pelo usuário:

    ERRO → AUSÊNCIA → OPORTUNIDADE (priorizada)

O Scanner Noológico responde "o que está ausente?".
Este módulo responde "quais ausências valem mais o esforço científico?".

Cada ausência (gap/blind spot) recebe um EpistemicScore composto por
quatro fatores, todos normalizados em [0, 1]:

- centrality      : impacto em cascata — quantas outras dimensões dependem
                    desta (proxy: peso da dimensão e severidade do gap);
- rarity          : quão inexplorada é a região (1 - densidade observada);
- interdisciplinarity : conectividade com domínios externos (analogias
                    polimáticas disponíveis sugerem transferência possível);
- feasibility     : inverso do custo de construção estimado pela
                    Composição Unitária do Conhecimento (menos insumos
                    faltantes ⇒ mais viável).

potential = w1*centrality + w2*rarity + w3*interdisciplinarity
opportunity = potential * feasibility     (valor ajustado pelo custo)

Saída: ranking de oportunidades com classificação qualitativa
(breakthrough / promissora / marginal) e hipóteses de exploração.

100% stdlib.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class EpistemicOpportunity:
    """Uma ausência priorizada como oportunidade de pesquisa."""
    dimension: str
    description: str
    centrality: float
    rarity: float
    interdisciplinarity: float
    feasibility: float
    potential: float
    opportunity_score: float
    tier: str                      # breakthrough | promissora | marginal
    exploration_hypothesis: str
    related_domains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EpistemicPrioritizer:
    """Transforma ausências detectadas em oportunidades priorizadas.

    Pesos padrão calibrados para privilegiar centralidade (efeito
    cascata) sem ignorar a raridade epistêmica.
    """

    def __init__(self, w_centrality: float = 0.4, w_rarity: float = 0.35,
                 w_interdisc: float = 0.25):
        total = w_centrality + w_rarity + w_interdisc
        self.w_centrality = w_centrality / total
        self.w_rarity = w_rarity / total
        self.w_interdisc = w_interdisc / total

    # ------------------------------------------------------------------
    def prioritize(self,
                   noological_report: Dict[str, Any],
                   analogies: Optional[List[Any]] = None,
                   capability_units: Optional[List[Any]] = None,
                   ) -> List[EpistemicOpportunity]:
        """Gera o ranking de oportunidades epistemológicas.

        Args:
            noological_report: saída do NoologicalScanner.scan()
                (usa 'dimensions' com blind_spot_score/density/weight
                 e/ou a lista 'gaps').
            analogies: analogias polimáticas (PolymathicConvergence),
                usadas como proxy de interdisciplinaridade.
            capability_units: composições unitárias (SPEC-033) usadas
                como proxy de custo/viabilidade.
        """
        analogies = analogies or []
        capability_units = capability_units or []

        # Índice de analogias por domínio/dimensão
        analogy_index: Dict[str, List[str]] = {}
        for a in analogies:
            key = str(getattr(a, "target_domain", None)
                      or getattr(a, "dimension", None)
                      or getattr(a, "domain", "")).lower()
            src = str(getattr(a, "source_domain", None)
                      or getattr(a, "source", "externo"))
            analogy_index.setdefault(key, []).append(src)

        # Índice de custo por capacidade (composição unitária)
        cost_index: Dict[str, float] = {}
        max_cost = 1.0
        for u in capability_units:
            cid = str(getattr(u, "capability_id", getattr(u, "id", ""))).lower()
            inputs = getattr(u, "all_inputs", None) or []
            cost = float(getattr(u, "construction_cost", len(inputs)) or len(inputs))
            cost_index[cid] = cost
            max_cost = max(max_cost, cost)

        opportunities: List[EpistemicOpportunity] = []
        dims = noological_report.get("dimensions", {}) or {}
        gaps = noological_report.get("gaps", []) or []

        # Fonte primária: dimensões com blind_spot_score
        seen = set()
        for dim_key, data in dims.items():
            if not isinstance(data, dict):
                continue
            density = float(data.get("density", data.get("coverage", 0.0)) or 0.0)
            weight = float(data.get("weight", 1.0) or 1.0)
            blind = float(data.get("blind_spot_score", 0.0) or 0.0)
            if blind <= 0 and density >= 0.2:
                continue  # dimensão razoavelmente coberta
            seen.add(str(dim_key).lower())
            opportunities.append(self._score(
                dimension=str(dim_key),
                description=str(data.get("description", f"Dimensão '{dim_key}' com baixa densidade")),
                density=density, weight=weight,
                blind=blind, analogy_index=analogy_index,
                cost_index=cost_index, max_cost=max_cost))

        # Fonte secundária: gaps textuais não mapeados em dimensões
        for g in gaps:
            name = str(g.get("dimension", g.get("name", "")) if isinstance(g, dict)
                       else getattr(g, "dimension", str(g)))
            if name.lower() in seen or not name:
                continue
            desc = str(g.get("description", name) if isinstance(g, dict)
                       else getattr(g, "description", name))
            sev = str(g.get("severity", "moderate") if isinstance(g, dict)
                      else getattr(g, "severity", "moderate"))
            sev_map = {"critical": 0.9, "high": 0.7, "moderate": 0.5, "low": 0.3}
            opportunities.append(self._score(
                dimension=name, description=desc,
                density=0.1, weight=sev_map.get(sev, 0.5) * 2,
                blind=sev_map.get(sev, 0.5) * 0.25,
                analogy_index=analogy_index,
                cost_index=cost_index, max_cost=max_cost))
            seen.add(name.lower())

        opportunities.sort(key=lambda o: o.opportunity_score, reverse=True)
        return opportunities

    # ------------------------------------------------------------------
    def _score(self, dimension: str, description: str, density: float,
               weight: float, blind: float,
               analogy_index: Dict[str, List[str]],
               cost_index: Dict[str, float], max_cost: float,
               ) -> EpistemicOpportunity:
        centrality = min(1.0, weight / 2.0)          # peso 2.0 ⇒ central
        rarity = min(1.0, max(0.0, 1.0 - density))
        related = analogy_index.get(dimension.lower(), [])
        interdisc = min(1.0, len(related) / 3.0)     # 3+ domínios ⇒ máx.
        cost = cost_index.get(dimension.lower(), max_cost * 0.5)
        feasibility = min(1.0, max(0.1, 1.0 - (cost / (max_cost or 1.0)) * 0.9))

        potential = (self.w_centrality * centrality
                     + self.w_rarity * rarity
                     + self.w_interdisc * interdisc)
        score = round(potential * feasibility, 4)

        if score >= 0.45 or (potential >= 0.7 and interdisc >= 0.6):
            tier = "breakthrough"
            hypo = (f"A ausência em '{dimension}' cruza {max(1, len(related))} "
                    f"domínio(s) e possui alta centralidade — investigá-la pode "
                    f"abrir uma linha de pesquisa inédita com efeito cascata.")
        elif score >= 0.25:
            tier = "promissora"
            hypo = (f"Explorar '{dimension}' tende a fechar lacunas estruturais "
                    f"com bom retorno; recomenda-se estudo exploratório dirigido.")
        else:
            tier = "marginal"
            hypo = (f"'{dimension}' representa complementação incremental; "
                    f"tratar de forma oportunista, sem prioridade de agenda.")

        return EpistemicOpportunity(
            dimension=dimension, description=description,
            centrality=round(centrality, 3), rarity=round(rarity, 3),
            interdisciplinarity=round(interdisc, 3),
            feasibility=round(feasibility, 3),
            potential=round(potential, 4), opportunity_score=score,
            tier=tier, exploration_hypothesis=hypo,
            related_domains=related)

    # ------------------------------------------------------------------
    def generate_report(self, opportunities: List[EpistemicOpportunity]) -> str:
        """Relatório Markdown da priorização epistemológica."""
        lines = [
            "# Priorização Epistemológica — Erro → Ausência → Oportunidade",
            "",
            f"Oportunidades analisadas: **{len(opportunities)}**",
            "",
            "| # | Dimensão | Tier | Score | Centralidade | Raridade | "
            "Interdisc. | Viabilidade |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for i, o in enumerate(opportunities, 1):
            lines.append(
                f"| {i} | {o.dimension} | {o.tier} | {o.opportunity_score:.3f} "
                f"| {o.centrality:.2f} | {o.rarity:.2f} "
                f"| {o.interdisciplinarity:.2f} | {o.feasibility:.2f} |")
        lines.append("")
        lines.append("## Hipóteses de exploração")
        lines.append("")
        for o in opportunities[:10]:
            lines.append(f"- **{o.dimension}** ({o.tier}): "
                         f"{o.exploration_hypothesis}")
        lines.append("")
        return "\n".join(lines)
