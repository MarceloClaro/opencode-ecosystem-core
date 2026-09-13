#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuccessorGenerator v1.1 — Gerador de Sucessores (R492 + SPEC-020)

API unificada (R492-fix): mantém os dois contratos sem quebra:

A) SPEC-020 (legado, usado por DiagnosticPipeline e /diagnose):
   - SuccessorGenerator(mission=...)   # sem argumentos obrigatórios
   - generate(dna, existing_links=None, theme="", max_hypotheses=12)
       -> List[SuccessorHypothesis] com successor_score em [0,1],
          genes derivados do DNA, tier (imediato/proximo_horizonte/especulativo)
   - generate_report(hypotheses) -> str (Markdown)

B) R492 (proposta do usuário — recombinação estrutural):
   - SuccessorGenerator(modules=...) | sem argumentos (usa DEFAULT_MODULES)
   - scan(max_combos=12) -> SuccessorsReport com SUCCESSOR_BANK (curado)
     + combinações inter-módulo (diversity/novelty/centrality)

    Noological:  "o que não existe?"
    Trajectory:  "como chegar?"
    Potentiality(R491): "o que está prestes a nascer?"
    Successor:   "O QUE PODE SURGIR A PARTIR DISSO?"

Sucessores são HIPÓTESES (não implementações): o relatório diz o que SERIA e
que combinação o sustenta. Determinístico, stdlib, anti-overclaim.
"""

from __future__ import annotations

import itertools
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ─── Pesos da heurística R492 (documentados na spec R492) ───────────────
W_DIVERSITY = 1.0
W_NOVELTY = 0.5
W_CENTRALITY = 0.3

# ─── DNA declarativo padrão (SPEC-020 compat: pipeline instancia sem args)
DEFAULT_MODULES: dict[str, list[str]] = {
    "noological_scanner": ["gap_detection"],
    "teleological_scanner": ["target_definition"],
    "reverse_scanner": ["capacity_decomposition"],
    "trajectory_mapper": ["dependency_mapping", "trajectory_mapping"],
    "cross_validation_engine": ["cross_validation"],
    "polymathic_convergence": ["polymathic_reasoning", "cross_reference"],
    "knowledge_composition": ["input_decomposition"],
    "auto_evolve": ["self_evolution"],
    "mci_blackboard": ["multi_agent_coordination"],
    "trust_engine": ["evaluation"],
    "metabus": ["shared_memory"],
}


@dataclass
class SuccessorHypothesis:
    """Hipótese de capacidade sucessora emergente.

    Campos legados (SPEC-020): name, genes, gene_types, synergy, viability,
    adherence, emergence, successor_score, tier, rationale, to_dict().
    Campos R492: id, description, requires, origin, novelty, score, function.
    """
    # SPEC-020
    name: str = ""
    genes: List[str] = field(default_factory=list)
    gene_types: List[str] = field(default_factory=list)
    synergy: float = 0.0
    viability: float = 0.0
    adherence: float = 0.0
    emergence: float = 0.0
    successor_score: float = 0.0
    tier: str = "especulativo"
    rationale: str = ""
    # R492
    id: str = ""
    description: str = ""
    requires: List[str] = field(default_factory=list)
    origin: str = "generated"
    novelty: int = 1
    score: float = 0.0
    function: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─── Tipos funcionais e matriz de complementaridade (SPEC-020) ──────────
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


def _classify(name: str) -> str:
    low = name.lower()
    for t, kws in _TYPE_KEYWORDS.items():
        if any(k in low for k in kws):
            return t
    return "engine"


# ─── SUCCESSOR_BANK (R492) — hipóteses curadas (exemplos do usuário) ─────
SUCCESSOR_BANK: List[SuccessorHypothesis] = [
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
    """Catálogo de sucessores R492: curados (bank) + gerados + ranking."""
    bank: List["SuccessorHypothesis"]
    generated: List["SuccessorHypothesis"]
    ranking: List["SuccessorHypothesis"]
    by_id: Dict[str, "SuccessorHypothesis"]
    params: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class SuccessorGenerator:
    """Gera e ranqueia sucessores plausíveis a partir do DNA estrutural.

    API legada (SPEC-020): mission opcional; generate(dna, ...).
    API R492: modules opcional; scan(max_combos).
    """

    def __init__(self, mission: str = "pesquisa científica automatizada "
                 "multiagente com metacognição",
                 modules: Optional[Dict[str, List[str]]] = None):
        self.mission = mission.lower()
        self.modules = modules if modules is not None else DEFAULT_MODULES

    # ═══════════════════════ API SPEC-020 (legada) ═══════════════════════
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
                    else "proximo_horizonte" if score >= 0.45
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

    # ═══════════════════════ API R492 (recombinação) ═════════════════════
    def _index(self) -> Dict[str, set]:
        out: Dict[str, set] = {}
        for module, caps in self.modules.items():
            for cap in caps:
                out.setdefault(cap, set()).add(module)
        return out

    def _central(self) -> set:
        seen: set = set()
        dup: set = set()
        for module, caps in self.modules.items():
            for cap in caps:
                if cap in seen:
                    dup.add(cap)
                seen.add(cap)
        return dup

    def _diversity(self, combo: Tuple[str, ...]) -> int:
        mods: set = set()
        for cap in combo:
            mods.update(self.cap_to_modules.get(cap, set()))
        return len(mods)

    def _score(self, combo: Tuple[str, ...],
               bank_sets: set) -> float:
        diversity = self._diversity(combo)
        novelty = 0 if frozenset(combo) in bank_sets else 1
        centrality = sum(1 for cap in combo if cap in self.central)
        return round(W_DIVERSITY * diversity + W_NOVELTY * novelty
                     + W_CENTRALITY * centrality, 4)

    def _generate_combos(self, max_combos: int = 12) -> List[SuccessorHypothesis]:
        """Pares e trios de capabilities de módulos distintos, por score."""
        caps = sorted(self.cap_to_modules)
        bank_sets = {frozenset(h.requires)
                     for h in SUCCESSOR_BANK if h.origin == "bank"}
        candidates: List[SuccessorHypothesis] = []
        for size in (2, 3):
            for combo in itertools.combinations(caps, size):
                if self._diversity(combo) < 2:
                    continue  # recombinação inter-módulo apenas
                if frozenset(combo) in bank_sets:
                    continue
                candidates.append(SuccessorHypothesis(
                    id=f"succ-{'-'.join(combo)}",
                    name="Hypothesis " + "-".join(combo).replace("_", "-"),
                    description="Hipótese combinatoria: " + " + ".join(combo),
                    requires=list(combo),
                    origin="generated",
                    novelty=1,
                    score=self._score(combo, bank_sets),
                ))
        candidates.sort(key=lambda h: (-h.score, h.id))
        return candidates[:max_combos]

    def scan(self, max_combos: int = 12) -> SuccessorsReport:
        """Relatório completo R492: bank (curado) + gerados + ranking."""
        self.cap_to_modules = self._index()
        self.central = self._central()
        bank_scored: List[SuccessorHypothesis] = []
        bank_sets = {frozenset(h.requires)
                     for h in SUCCESSOR_BANK if h.origin == "bank"}
        for h in SUCCESSOR_BANK:
            combo = tuple(h.requires)
            scored = SuccessorHypothesis(
                id=h.id, name=h.name, description=h.description,
                requires=list(h.requires), origin=h.origin,
                novelty=int(frozenset(combo) not in bank_sets),
                score=self._score(combo, bank_sets), function=h.function,
            )
            bank_scored.append(scored)
        generated = self._generate_combos(max_combos=max_combos)
        ranking = sorted(bank_scored + generated,
                         key=lambda h: (-h.score, h.id))
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