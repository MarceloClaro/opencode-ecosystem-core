# -*- coding: utf-8 -*-
"""
Evidence Graph — R102
=====================
Grafo incremental de evidencia que acumula conhecimento entre rodadas
de pesquisa profunda. Inspirado no Evidence Graph do DeepEvidence
(Wang et al., Nature Machine Intelligence 2026).

Entidades (nos): genes, doenças, drogas, papers, conceitos.
Relacoes (arestas): TREATS, CAUSES, ASSOCIATED_WITH, CITES, etc.

SPEC-935-R102.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Tipos de entidade e relacao
# ============================================================

ENTITY_TYPES = [
    "gene", "disease", "drug", "paper", "pathway",
    "clinical_trial", "concept", "author", "method",
]

RELATION_TYPES = [
    "TREATS", "CAUSES", "ASSOCIATED_WITH", "CITES",
    "TARGETS", "IN_PATHWAY", "DIAGNOSES", "CONTRADICTS",
    "EVIDENCE_FOR", "EVIDENCE_AGAINST", "MENTIONS",
]


@dataclass
class Evidence:
    """Fragmento de evidencia com proveniencia."""
    id: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:8]}")
    text: str = ""
    source: str = ""              # DOI, PMID, URL
    source_type: str = ""         # pubmed, clinical_trial, kg, web
    confidence: float = 0.5       # 0.0 a 1.0
    timestamp: float = field(default_factory=time.time)
    agent: str = ""               # qual agente registrou

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text[:200],
            "source": self.source,
            "source_type": self.source_type,
            "confidence": self.confidence,
            "agent": self.agent,
        }


@dataclass
class Entity:
    """No do grafo de evidencia."""
    id: str = field(default_factory=lambda: f"ent-{uuid.uuid4().hex[:8]}")
    name: str = ""
    entity_type: str = "concept"
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)  # Evidence ids

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type,
            "description": self.description[:200],
            "aliases": self.aliases[:3],
            "evidence_count": len(self.evidence),
        }


@dataclass
class Relation:
    """Aresta do grafo de evidencia."""
    id: str = field(default_factory=lambda: f"rel-{uuid.uuid4().hex[:8]}")
    source_id: str = ""
    target_id: str = ""
    relation_type: str = "ASSOCIATED_WITH"
    weight: float = 1.0
    evidence: List[str] = field(default_factory=list)
    bidirectional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relation_type,
            "weight": self.weight,
            "evidence_count": len(self.evidence),
        }


# ============================================================
# EvidenceGraph
# ============================================================

class EvidenceGraph:
    """Grafo incremental de evidencia.

    Acumula conhecimento entre rodadas de pesquisa.
    Suporta expansao, consulta, path-finding e exportacao.
    """

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.evidence_store: Dict[str, Evidence] = {}
        # Indices
        self._type_index: Dict[str, List[str]] = {
            t: [] for t in ENTITY_TYPES
        }
        self._name_index: Dict[str, str] = {}  # name.lower() -> entity_id
        self._adjacency: Dict[str, List[str]] = {}  # entity_id -> [relation_id]

    # ---- Entidades ----

    def add_entity(
        self,
        name: str,
        entity_type: str = "concept",
        description: str = "",
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        evidence_text: str = "",
        source: str = "",
        source_type: str = "",
    ) -> Entity:
        """Adiciona ou recupera entidade."""
        # Verificar se ja existe pelo nome
        name_lower = name.lower().strip()
        if name_lower in self._name_index:
            eid = self._name_index[name_lower]
            entity = self.entities[eid]
            # Atualizar metadados se vazio
            if not entity.description and description:
                entity.description = description
            if evidence_text:
                ev = self._add_evidence(
                    evidence_text, source, source_type, "evidence_graph"
                )
                if ev.id not in entity.evidence:
                    entity.evidence.append(ev.id)
            return entity

        entity = Entity(
            name=name,
            entity_type=entity_type if entity_type in ENTITY_TYPES else "concept",
            description=description,
            aliases=aliases or [],
            metadata=metadata or {},
        )
        self.entities[entity.id] = entity
        self._name_index[name_lower] = entity.id
        if entity.entity_type in self._type_index:
            self._type_index[entity.entity_type].append(entity.id)
        else:
            self._type_index["concept"].append(entity.id)
        self._adjacency[entity.id] = []

        if evidence_text:
            ev = self._add_evidence(
                evidence_text, source, source_type, "evidence_graph"
            )
            entity.evidence.append(ev.id)

        return entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Recupera entidade por ID."""
        return self.entities.get(entity_id)

    def find_entity_by_name(self, name: str) -> Optional[Entity]:
        """Busca entidade por nome (case-insensitive)."""
        eid = self._name_index.get(name.lower().strip())
        return self.entities.get(eid) if eid else None

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Recupera entidades por tipo."""
        ids = self._type_index.get(entity_type, [])
        return [self.entities[eid] for eid in ids if eid in self.entities]

    # ---- Relacoes ----

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str = "ASSOCIATED_WITH",
        weight: float = 1.0,
        evidence_text: str = "",
        source: str = "",
        bidirectional: bool = False,
    ) -> Optional[Relation]:
        """Adiciona relacao entre entidades."""
        if source_id not in self.entities:
            logger.warning(f"Source entity {source_id} not found")
            return None
        if target_id not in self.entities:
            logger.warning(f"Target entity {target_id} not found")
            return None

        # Verificar duplicata
        for rid in self._adjacency.get(source_id, []):
            existing = self.relations.get(rid)
            if (existing and existing.source_id == source_id
                    and existing.target_id == target_id
                    and existing.relation_type == relation_type):
                existing.weight = max(existing.weight, weight)
                return existing

        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type
            if relation_type in RELATION_TYPES else "ASSOCIATED_WITH",
            weight=weight,
            bidirectional=bidirectional,
        )
        self.relations[relation.id] = relation
        self._adjacency.setdefault(source_id, []).append(relation.id)
        if bidirectional:
            self._adjacency.setdefault(target_id, []).append(relation.id)

        if evidence_text:
            ev = self._add_evidence(
                evidence_text, source, "kg", "evidence_graph"
            )
            relation.evidence.append(ev.id)

        return relation

    def get_relations(
        self,
        entity_id: str,
        relation_type: Optional[str] = None,
        direction: str = "both",
    ) -> List[Relation]:
        """Recupera relacoes de uma entidade.

        Args:
            entity_id: ID da entidade.
            relation_type: Filtrar por tipo de relacao.
            direction: 'outgoing', 'incoming', ou 'both'.
        """
        result = []
        for rid, rel in self.relations.items():
            # Verificar se a entidade participa
            is_source = rel.source_id == entity_id
            is_target = rel.target_id == entity_id
            if not (is_source or is_target):
                continue
            if direction == "outgoing" and not is_source:
                continue
            if direction == "incoming" and not is_target:
                continue
            if relation_type and rel.relation_type != relation_type:
                continue
            result.append(rel)
        return result

    # ---- Evidencia ----

    def _add_evidence(
        self,
        text: str,
        source: str = "",
        source_type: str = "",
        agent: str = "",
    ) -> Evidence:
        """Adiciona evidencia ao store."""
        ev = Evidence(
            text=text,
            source=source,
            source_type=source_type,
            agent=agent,
        )
        self.evidence_store[ev.id] = ev
        return ev

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """Recupera evidencia por ID."""
        return self.evidence_store.get(evidence_id)

    # ---- Consultas ----

    def find_paths(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 3,
    ) -> List[List[Relation]]:
        """Encontra caminhos entre duas entidades (BFS)."""
        if source_id not in self.entities or target_id not in self.entities:
            return []

        visited: Set[str] = {source_id}
        queue: List[Tuple[str, List[Relation]]] = [(source_id, [])]

        while queue:
            current, path = queue.pop(0)
            if current == target_id:
                return [path]

            if len(path) >= max_depth:
                continue

            for rel in self.get_relations(current):
                neighbor = (
                    rel.target_id if rel.source_id == current
                    else rel.source_id
                )
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [rel]))

        return []

    def subgraph_query(
        self,
        seed_ids: List[str],
        max_depth: int = 2,
        max_nodes: int = 50,
    ) -> Dict[str, Any]:
        """Extrai subgrafo ao redor de entidades semente."""
        nodes: Dict[str, Entity] = {}
        edges: Dict[str, Relation] = {}
        frontier: List[Tuple[str, int]] = [
            (sid, 0) for sid in seed_ids if sid in self.entities
        ]
        visited: Set[str] = set()

        while frontier and len(nodes) < max_nodes:
            eid, depth = frontier.pop(0)
            if eid in visited:
                continue
            visited.add(eid)

            if eid in self.entities:
                nodes[eid] = self.entities[eid]

            if depth < max_depth:
                for rel in self.get_relations(eid):
                    edges[rel.id] = rel
                    neighbor = (
                        rel.target_id if rel.source_id == eid
                        else rel.source_id
                    )
                    if neighbor not in visited:
                        frontier.append((neighbor, depth + 1))

        return {
            "entities": [e.to_dict() for e in nodes.values()],
            "relations": [r.to_dict() for r in edges.values()],
            "total_entities": len(nodes),
            "total_relations": len(edges),
        }

    # ---- Estatisticas ----

    def stats(self) -> Dict[str, Any]:
        """Estatisticas do grafo."""
        return {
            "entities": len(self.entities),
            "relations": len(self.relations),
            "evidence_pieces": len(self.evidence_store),
            "entity_types": {
                t: len(ids) for t, ids in self._type_index.items()
            },
            "relation_types": self._count_relation_types(),
            "avg_degree": self._avg_degree(),
        }

    def _count_relation_types(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for rel in self.relations.values():
            counts[rel.relation_type] = counts.get(rel.relation_type, 0) + 1
        return counts

    def _avg_degree(self) -> float:
        if not self.entities:
            return 0.0
        total = sum(len(rels) for rels in self._adjacency.values())
        return round(total / len(self.entities), 2)

    # ---- Exportacao ----

    def to_dict(self) -> Dict[str, Any]:
        """Exporta grafo completo."""
        return {
            "entities": {
                eid: e.to_dict() for eid, e in self.entities.items()
            },
            "relations": {
                rid: r.to_dict() for rid, r in self.relations.items()
            },
            "evidence": {
                eid: e.to_dict() for eid, e in self.evidence_store.items()
            },
            "stats": self.stats(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Exporta como JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    def export_visualization(self) -> Dict[str, Any]:
        """Exporta para visualizacao (formato compatível com D3/vis.js)."""
        nodes = []
        for eid, entity in self.entities.items():
            nodes.append({
                "id": eid,
                "label": entity.name,
                "group": entity.entity_type,
                "size": len(entity.evidence) + 1,
            })

        edges = []
        for rid, rel in self.relations.items():
            edges.append({
                "id": rid,
                "from": rel.source_id,
                "to": rel.target_id,
                "label": rel.relation_type,
                "width": rel.weight,
            })

        return {"nodes": nodes, "edges": edges}
