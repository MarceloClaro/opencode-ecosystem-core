"""Grafo de Conhecimento da Universidade Sintética — SPEC-935.

Mapeia conceitos, faculdades, correlações e teses em um grafo navegável
para consulta e visualização.
"""

from __future__ import annotations
import json
import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Nó no grafo de conhecimento da universidade."""
    node_id: str
    label: str
    node_type: str  # "faculty", "concept", "correlation", "thesis", "combination"
    faculty_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Aresta no grafo de conhecimento."""
    source_id: str
    target_id: str
    edge_type: str  # "contains", "correlates", "generates", "relates_to"
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class UniversityKnowledgeGraph:
    """Grafo de conhecimento completo da universidade sintética.
    
    Nós: faculdades, conceitos, correlações, teses, combinações.
    Arestas: contém, correlaciona, gera, relaciona-se.
    """
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        
        # Índices
        self._nodes_by_type: Dict[str, List[str]] = defaultdict(list)
        self._edges_by_source: Dict[str, List[GraphEdge]] = defaultdict(list)
        self._edges_by_target: Dict[str, List[GraphEdge]] = defaultdict(list)
    
    def add_faculty(self, faculty_id: str, label: str, metadata: Dict = None) -> GraphNode:
        """Adiciona nó de faculdade."""
        return self._add_node(
            f"faculty:{faculty_id}", label, "faculty",
            faculty_id=faculty_id, metadata=metadata or {}
        )
    
    def add_concept(self, concept: str, faculty_id: str) -> GraphNode:
        """Adiciona nó de conceito vinculado a uma faculdade."""
        node_id = f"concept:{concept.lower().replace(' ', '_')[:40]}"
        return self._add_node(
            node_id, concept, "concept",
            faculty_id=faculty_id
        )
    
    def add_correlation(self, corr_id: str, label: str, metadata: Dict = None) -> GraphNode:
        """Adiciona nó de correlação."""
        return self._add_node(
            f"correlation:{corr_id}", label, "correlation",
            metadata=metadata or {}
        )
    
    def add_thesis(self, thesis_id: str, label: str, metadata: Dict = None) -> GraphNode:
        """Adiciona nó de tese."""
        return self._add_node(
            f"thesis:{thesis_id}", label, "thesis",
            metadata=metadata or {}
        )
    
    def add_combination(self, comb_id: str, label: str, metadata: Dict = None) -> GraphNode:
        """Adiciona nó de combinação."""
        return self._add_node(
            f"combination:{comb_id}", label, "combination",
            metadata=metadata or {}
        )
    
    def _add_node(
        self, node_id: str, label: str, node_type: str,
        faculty_id: Optional[str] = None,
        metadata: Dict = None,
    ) -> GraphNode:
        if node_id not in self.nodes:
            node = GraphNode(
                node_id=node_id,
                label=label,
                node_type=node_type,
                faculty_id=faculty_id,
                metadata=metadata or {},
            )
            self.nodes[node_id] = node
            self._nodes_by_type[node_type].append(node_id)
        return self.nodes[node_id]
    
    def add_edge(
        self, source_id: str, target_id: str,
        edge_type: str, weight: float = 1.0,
        metadata: Dict = None,
    ) -> GraphEdge:
        """Adiciona aresta entre dois nós."""
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            metadata=metadata or {},
        )
        self.edges.append(edge)
        self._edges_by_source[source_id].append(edge)
        self._edges_by_target[target_id].append(edge)
        return edge
    
    def connect_faculty_to_concept(self, faculty_id: str, concept: str) -> GraphEdge:
        """Conecta faculdade → conceito."""
        fac_node_id = f"faculty:{faculty_id}"
        conc_node_id = f"concept:{concept.lower().replace(' ', '_')[:40]}"
        return self.add_edge(fac_node_id, conc_node_id, "contains")
    
    def connect_concept_to_correlation(
        self, concept: str, corr_id: str, weight: float = 1.0
    ) -> GraphEdge:
        """Conecta conceito → correlação."""
        conc_node_id = f"concept:{concept.lower().replace(' ', '_')[:40]}"
        corr_node_id = f"correlation:{corr_id}"
        return self.add_edge(conc_node_id, corr_node_id, "correlates", weight=weight)
    
    def connect_combination_to_thesis(
        self, comb_id: str, thesis_id: str, weight: float = 1.0
    ) -> GraphEdge:
        """Conecta combinação → tese."""
        comb_node_id = f"combination:{comb_id}"
        thesis_node_id = f"thesis:{thesis_id}"
        return self.add_edge(comb_node_id, thesis_node_id, "generates", weight=weight)
    
    def build_from_faculties(self, faculties: List) -> int:
        """Popula o grafo com todas as faculdades e conceitos."""
        count = 0
        for fac in faculties:
            self.add_faculty(fac.id, fac.nome)
            for concept in fac.conceitos[:50]:  # limite para não explodir
                self.add_concept(concept, fac.id)
                self.connect_faculty_to_concept(fac.id, concept)
                count += 1
        logger.info(f"Grafo populado: {count} conceitos de {len(faculties)} faculdades")
        return count
    
    def build_from_combinations(
        self, combinations: List
    ) -> int:
        """Adiciona combinações ao grafo."""
        count = 0
        for comb in combinations:
            label = " × ".join(list(comb.concepts)[:3])
            self.add_combination(comb.combination_id, label, {
                "composite": comb.composite_score,
                "pattern": comb.discovered_pattern,
            })
            # Conectar conceitos à combinação
            for concept in comb.concepts:
                conc_id = f"concept:{concept.lower().replace(' ', '_')[:40]}"
                if conc_id in self.nodes:
                    self.add_edge(conc_id, f"combination:{comb.combination_id}", "relates_to")
            count += 1
        return count
    
    def build_from_correlations(self, correlations: List) -> int:
        """Adiciona correlações ao grafo."""
        count = 0
        for corr in correlations:
            label = f"{corr.correlation_type.value}: {' × '.join(list(corr.concepts)[:3])}"
            self.add_correlation(corr.correlation_id, label, {
                "type": corr.correlation_type.value,
                "strength": corr.strength,
                "significance": corr.significance,
            })
            # Conectar conceitos à correlação
            for concept in corr.concepts:
                self.connect_concept_to_correlation(concept, corr.correlation_id, corr.strength)
            count += 1
        return count
    
    def build_from_theses(self, theses: List) -> int:
        """Adiciona teses ao grafo."""
        count = 0
        for thesis in theses:
            self.add_thesis(thesis.thesis_id, thesis.title[:80], {
                "level": thesis.academic_level.value,
                "score": thesis.composite_score,
            })
            for comb_id in thesis.source_combinations:
                self.connect_combination_to_thesis(comb_id, thesis.thesis_id)
            count += 1
        return count
    
    def query_by_type(self, node_type: str) -> List[GraphNode]:
        """Consulta nós por tipo."""
        return [self.nodes[nid] for nid in self._nodes_by_type.get(node_type, [])]
    
    def query_by_faculty(self, faculty_id: str) -> List[GraphNode]:
        """Consulta nós por faculdade."""
        return [n for n in self.nodes.values() if n.faculty_id == faculty_id]
    
    def query_neighbors(self, node_id: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Retorna vizinhos de um nó."""
        neighbors = []
        edges = []
        for e in self._edges_by_source.get(node_id, []):
            if e.target_id in self.nodes:
                neighbors.append(self.nodes[e.target_id])
                edges.append(e)
        for e in self._edges_by_target.get(node_id, []):
            if e.source_id in self.nodes:
                neighbors.append(self.nodes[e.source_id])
                edges.append(e)
        return neighbors, edges
    
    def get_statistics(self) -> Dict:
        """Estatísticas do grafo."""
        return {
            "total_nodes": len(self.nodes),
            "nodes_by_type": {t: len(ids) for t, ids in self._nodes_by_type.items()},
            "total_edges": len(self.edges),
            "faculties": len(self._nodes_by_type.get("faculty", [])),
            "concepts": len(self._nodes_by_type.get("concept", [])),
            "correlations": len(self._nodes_by_type.get("correlation", [])),
            "theses": len(self._nodes_by_type.get("thesis", [])),
            "combinations": len(self._nodes_by_type.get("combination", [])),
        }
    
    def to_dict(self) -> Dict:
        """Serializa o grafo para dict."""
        return {
            "nodes": [
                {
                    "id": n.node_id,
                    "label": n.label,
                    "type": n.node_type,
                    "faculty": n.faculty_id,
                    "metadata": n.metadata,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type,
                    "weight": e.weight,
                }
                for e in self.edges
            ],
            "stats": self.get_statistics(),
        }
    
    def export_json(self, filepath: str):
        """Exporta grafo para arquivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Grafo exportado para {filepath}")
