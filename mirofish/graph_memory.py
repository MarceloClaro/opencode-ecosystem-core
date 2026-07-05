# -*- coding: utf-8 -*-
"""
GraphMemory — Memória de Grafo para o enxame MiroFish
=====================================================
Inspirado no MiroFish-Offline (Neo4j + Ollama): simula um grafo de
conhecimento em memória (stdlib puro, sem Neo4j) para que o enxame
rastreie as relações lógicas entre argumentos durante o debate Delphi.

Nós: argumentos, agentes, evidências, conclusões
Arestas tipadas: SUPPORTS, CONTRADICTS, REFINES, CITES, PROPOSED_BY

Consultas típicas:
- Quais argumentos sustentam a conclusão X?
- Há contradições não resolvidas no debate?
- Qual o argumento mais central (grau ponderado)?
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

EDGE_TYPES = {"SUPPORTS", "CONTRADICTS", "REFINES", "CITES", "PROPOSED_BY"}


@dataclass
class GraphNode:
    node_id: str
    kind: str                      # argument | agent | evidence | conclusion
    label: str
    weight: float = 1.0
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class GraphEdge:
    source: str
    target: str
    edge_type: str
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)


class GraphMemory:
    """Grafo de conhecimento em memória para debates do enxame."""

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    # ── construção ──
    def add_node(self, node_id: str, kind: str, label: str,
                 weight: float = 1.0, **meta) -> GraphNode:
        node = GraphNode(node_id=node_id, kind=kind, label=label,
                         weight=weight, meta=meta)
        self.nodes[node_id] = node
        return node

    def add_edge(self, source: str, target: str, edge_type: str,
                 weight: float = 1.0) -> GraphEdge:
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"edge_type inválido: {edge_type}. "
                             f"Use um de {sorted(EDGE_TYPES)}")
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("source e target devem existir no grafo")
        edge = GraphEdge(source=source, target=target,
                         edge_type=edge_type, weight=weight)
        self.edges.append(edge)
        return edge

    # ── consultas ──
    def supporters_of(self, node_id: str) -> List[GraphNode]:
        """Argumentos que sustentam (SUPPORTS) o nó dado."""
        return [self.nodes[e.source] for e in self.edges
                if e.target == node_id and e.edge_type == "SUPPORTS"
                and e.source in self.nodes]

    def contradictions(self) -> List[Tuple[GraphNode, GraphNode]]:
        """Pares de nós em contradição (CONTRADICTS)."""
        return [(self.nodes[e.source], self.nodes[e.target])
                for e in self.edges if e.edge_type == "CONTRADICTS"
                and e.source in self.nodes and e.target in self.nodes]

    def degree(self, node_id: str) -> float:
        """Grau ponderado (soma dos pesos das arestas incidentes)."""
        return sum(e.weight for e in self.edges
                   if e.source == node_id or e.target == node_id)

    def most_central(self, kind: Optional[str] = None,
                     top_n: int = 3) -> List[Tuple[GraphNode, float]]:
        """Nós mais centrais por grau ponderado."""
        candidates = [n for n in self.nodes.values()
                      if kind is None or n.kind == kind]
        ranked = sorted(((n, self.degree(n.node_id)) for n in candidates),
                        key=lambda t: t[1], reverse=True)
        return ranked[:top_n]

    def consensus_score(self) -> float:
        """
        Score de consenso do debate ∈ [0, 1]:
        proporção de arestas de suporte/refinamento vs contradições.
        """
        if not self.edges:
            return 0.0
        positive = sum(1 for e in self.edges
                       if e.edge_type in ("SUPPORTS", "REFINES"))
        negative = sum(1 for e in self.edges
                       if e.edge_type == "CONTRADICTS")
        total = positive + negative
        return round(positive / total, 4) if total else 0.0

    # ── ingestão a partir de um debate do enxame ──
    def ingest_debate(self, topic: str,
                      opinions: List[Dict[str, Any]]) -> str:
        """
        Ingere as opiniões de uma rodada Delphi como subgrafo.

        opinions: [{"agent": str, "position": float, "argument": str}, ...]
        Retorna o node_id da conclusão criada.
        """
        conclusion_id = f"conclusion::{abs(hash(topic)) % 10**8}"
        self.add_node(conclusion_id, "conclusion", topic)

        prev_position: Optional[float] = None
        prev_arg_id: Optional[str] = None
        for i, op in enumerate(opinions):
            agent_id = f"agent::{op.get('agent', f'anon{i}')}"
            if agent_id not in self.nodes:
                self.add_node(agent_id, "agent", op.get("agent", f"anon{i}"))
            arg_id = f"arg::{abs(hash(op.get('argument', str(i)))) % 10**10}"
            self.add_node(arg_id, "argument",
                          (op.get("argument") or "")[:200],
                          weight=abs(op.get("position", 0.5)))
            self.add_edge(arg_id, conclusion_id, "SUPPORTS"
                          if op.get("position", 0.5) >= 0.5 else "CONTRADICTS",
                          weight=abs(op.get("position", 0.5)))
            self.add_edge(agent_id, arg_id, "PROPOSED_BY")
            # relação com o argumento anterior (refina ou contradiz)
            if prev_arg_id is not None and prev_position is not None:
                same_side = ((op.get("position", 0.5) >= 0.5)
                             == (prev_position >= 0.5))
                self.add_edge(arg_id, prev_arg_id,
                              "REFINES" if same_side else "CONTRADICTS",
                              weight=0.5)
            prev_arg_id, prev_position = arg_id, op.get("position", 0.5)
        return conclusion_id

    # ── serialização ──
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [asdict(n) for n in self.nodes.values()],
            "edges": [asdict(e) for e in self.edges],
            "consensus_score": self.consensus_score(),
        }

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "GraphMemory":
        gm = cls()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for n in data.get("nodes", []):
            gm.nodes[n["node_id"]] = GraphNode(**{
                k: v for k, v in n.items()
                if k in GraphNode.__dataclass_fields__})
        for e in data.get("edges", []):
            gm.edges.append(GraphEdge(**{
                k: v for k, v in e.items()
                if k in GraphEdge.__dataclass_fields__}))
        return gm
