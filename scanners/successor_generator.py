# -*- coding: utf-8 -*-
"""
SuccessorGenerator — Gerador de Sucessores Plausíveis (SPEC-020).

Completa os módulos 2–5 do Potentiality Scanner (Anexos 7 e 8):

    DNA estrutural → combinações de capacidades → hipóteses de
    sucessores → ranking (relevância, viabilidade, aderência, potencial)

Cada capacidade existente no DNA estrutural do ecossistema vira um
"gene". O gerador combina genes em pares e trios, avaliando:

- synergy      : complementaridade de tipos (motor + dados + interface
                 combinam melhor do que três motores redundantes);
- viability    : proporção de componentes já presentes (capacidade
                 emergente com 80% dos insumos prontos é quase gratuita);
- adherence    : aderência ao tema/missão declarada do ecossistema;
- emergence    : potencial de comportamento emergente (novidade da
                 combinação — pares nunca conectados pontuam mais).

successor_score = média ponderada dos quatro fatores.

100% stdlib.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple


# Tipos funcionais de capacidade e a matriz de complementaridade
_TYPE_KEYWORDS = {
    "engine": ("engine", "motor", "solver", "reasoning", "pipeline",
               "transformer", "swarm"),
    "data": ("data", "memory", "memória", "corpus", "dataset", "graph",
             "knowledge", "research", "pesquisa"),
    "interface": ("cli", "api", "mcp", "bridge", "ui", "interface",
                  "integration"),
    "governance": ("trust", "economy", "gate", "audit", "spec", "tdd",
                   "scanner", "validator"),
    "output": ("publishing", "latex", "cover", "illustration", "report",
               "fichamento", "producao"),
}

_COMPLEMENT = {
    frozenset(("engine", "data")): 1.0,
    frozenset(("engine", "interface")): 0.85,
    frozenset(("engine", "output")): 0.9,
    frozenset(("engine", "governance")): 0.8,
    frozenset(("data", "output")): 0.9,
    frozenset(("data", "interface")): 0.75,
    frozenset(("data", "governance")): 0.7,
    frozenset(("interface", "output")): 0.65,
    frozenset(("interface", "governance")): 0.6,
    frozenset(("governance", "output")): 0.7,
}


@dataclass
class SuccessorHypothesis:
    """Hipótese de capacidade sucessora emergente."""
    name: str
    genes: List[str]
    gene_types: List[str]
    synergy: float
    viability: float
    adherence: float
    emergence: float
    successor_score: float
    tier: str                    # imediato | próximo-horizonte | especulativo
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _classify(name: str) -> str:
    low = name.lower()
    for t, kws in _TYPE_KEYWORDS.items():
        if any(k in low for k in kws):
            return t
    return "engine"


class SuccessorGenerator:
    """Gera e ranqueia sucessores plausíveis a partir do DNA estrutural."""

    def __init__(self, mission: str = "pesquisa científica automatizada "
                 "multiagente com metacognição"):
        self.mission = mission.lower()

    # ------------------------------------------------------------------
    def generate(self,
                 dna: Dict[str, Any],
                 existing_links: Optional[Sequence[Tuple[str, str]]] = None,
                 theme: str = "",
                 max_hypotheses: int = 12,
                 ) -> List[SuccessorHypothesis]:
        """Gera hipóteses de sucessores a partir do DNA de capacidades.

        Args:
            dna: saída do PotentialityScanner.extract_dna()
                 (usa 'capabilities'/'components' — lista de nomes ou
                  dicts com 'name' e opcional 'completeness').
            existing_links: pares de capacidades já conectadas (para
                 medir novidade/emergência).
            theme: tema de pesquisa atual (aderência).
            max_hypotheses: corte do ranking.
        """
        genes = self._extract_genes(dna)
        if len(genes) < 2:
            return []
        linked = {frozenset(p) for p in (existing_links or [])}
        theme_words = set((theme or self.mission).lower().split())

        hypotheses: List[SuccessorHypothesis] = []
        combos = list(itertools.combinations(genes.keys(), 2))
        combos += list(itertools.combinations(list(genes.keys())[:8], 3))

        for combo in combos:
            types = [genes[g]["type"] for g in combo]
            synergy = self._synergy(types)
            viability = sum(genes[g]["completeness"] for g in combo) / len(combo)
            adherence = self._adherence(combo, theme_words)
            emergence = 0.9 if frozenset(combo[:2]) not in linked else 0.35
            if len(set(types)) == 1:
                emergence *= 0.6  # combinação homogênea é menos emergente

            score = round(0.30 * synergy + 0.30 * viability
                          + 0.20 * adherence + 0.20 * emergence, 4)
            if score < 0.30:
                continue

            tier = ("imediato" if score >= 0.65 and viability >= 0.7
                    else "próximo-horizonte" if score >= 0.45
                    else "especulativo")
            name = self._name(combo, types)
            rationale = (
                f"Combina {', '.join(combo)} (tipos: {', '.join(types)}). "
                f"Sinergia {synergy:.2f}, viabilidade {viability:.2f} — "
                + ("os componentes já existem e a integração é de baixo custo."
                   if viability >= 0.7 else
                   "requer construção parcial de componentes intermediários."))
            hypotheses.append(SuccessorHypothesis(
                name=name, genes=list(combo), gene_types=types,
                synergy=round(synergy, 3), viability=round(viability, 3),
                adherence=round(adherence, 3), emergence=round(emergence, 3),
                successor_score=score, tier=tier, rationale=rationale))

        hypotheses.sort(key=lambda h: h.successor_score, reverse=True)
        return hypotheses[:max_hypotheses]

    # ------------------------------------------------------------------
    def _extract_genes(self, dna: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        raw = (dna.get("capabilities") or dna.get("components")
               or dna.get("capability_map") or [])
        genes: Dict[str, Dict[str, Any]] = {}
        if isinstance(raw, dict):
            raw = [{"name": k, **(v if isinstance(v, dict) else {})}
                   for k, v in raw.items()]
        for item in raw:
            if isinstance(item, str):
                name, comp = item, 1.0
            elif isinstance(item, dict):
                name = str(item.get("name", item.get("id", "")))
                comp = float(item.get("completeness",
                                      item.get("coverage", 1.0)) or 1.0)
            else:
                name = str(getattr(item, "name", item))
                comp = float(getattr(item, "completeness", 1.0) or 1.0)
            if not name:
                continue
            genes[name] = {"type": _classify(name),
                           "completeness": min(1.0, max(0.0, comp))}
        return genes

    def _synergy(self, types: List[str]) -> float:
        if len(types) < 2:
            return 0.5
        pairs = itertools.combinations(types, 2)
        vals = [_COMPLEMENT.get(frozenset(p), 0.45 if p[0] == p[1] else 0.55)
                for p in pairs]
        return sum(vals) / len(vals)

    def _adherence(self, combo: Sequence[str], theme_words: set) -> float:
        text = " ".join(combo).lower()
        hits = sum(1 for w in theme_words if len(w) > 3 and w in text)
        base = min(1.0, 0.4 + hits * 0.2)
        return base

    def _name(self, combo: Sequence[str], types: List[str]) -> str:
        # nome heurístico: tipo dominante + genes abreviados
        dominant = max(set(types), key=types.count)
        prefix = {"engine": "Motor", "data": "Base", "interface": "Ponte",
                  "governance": "Guarda", "output": "Publicador"}[dominant]
        short = "+".join(c.split("_")[0].split("/")[-1][:12] for c in combo)
        return f"{prefix} Emergente [{short}]"

    # ------------------------------------------------------------------
    def generate_report(self, hypotheses: List[SuccessorHypothesis]) -> str:
        lines = [
            "# Sucessores Plausíveis — DNA Estrutural → Capacidades Emergentes",
            "",
            f"Hipóteses geradas: **{len(hypotheses)}**",
            "",
            "| # | Sucessor | Tier | Score | Sinergia | Viabilidade | "
            "Aderência | Emergência |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for i, h in enumerate(hypotheses, 1):
            lines.append(
                f"| {i} | {h.name} | {h.tier} | {h.successor_score:.3f} "
                f"| {h.synergy:.2f} | {h.viability:.2f} "
                f"| {h.adherence:.2f} | {h.emergence:.2f} |")
        lines.append("")
        lines.append("## Racionais")
        lines.append("")
        for h in hypotheses[:8]:
            lines.append(f"- **{h.name}**: {h.rationale}")
        lines.append("")
        return "\n".join(lines)
