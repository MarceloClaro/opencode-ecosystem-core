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
import math
import copy
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
    confidence: Optional[float] = 0.5  # escore interno; ausente na importação = desconhecido
    timestamp: Optional[float] = field(default_factory=time.time)
    agent: str = ""               # qual agente registrou

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "text_preview": self.text[:200],
            "source": self.source,
            "source_type": self.source_type,
            "confidence": self.confidence,
            "agent": self.agent,
            "timestamp": self.timestamp,
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
    evidence_membership_known: bool = True
    declared_evidence_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type,
            "description": self.description,
            "description_preview": self.description[:200],
            "aliases": list(self.aliases),
            "metadata": copy.deepcopy(self.metadata),
            "evidence": list(self.evidence) if self.evidence_membership_known else None,
            "evidence_count": (len(self.evidence) if self.evidence_membership_known else self.declared_evidence_count),
            "evidence_membership": "known" if self.evidence_membership_known else "unknown",
        }


@dataclass
class Relation:
    """Aresta do grafo de evidencia."""
    id: str = field(default_factory=lambda: f"rel-{uuid.uuid4().hex[:8]}")
    source_id: str = ""
    target_id: str = ""
    relation_type: str = "ASSOCIATED_WITH"
    weight: Optional[float] = 1.0
    evidence: List[str] = field(default_factory=list)
    bidirectional: bool = False
    evidence_membership_known: bool = True
    declared_evidence_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relation_type,
            "weight": self.weight,
            "bidirectional": self.bidirectional,
            "evidence": list(self.evidence) if self.evidence_membership_known else None,
            "evidence_count": (len(self.evidence) if self.evidence_membership_known else self.declared_evidence_count),
            "evidence_membership": "known" if self.evidence_membership_known else "unknown",
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
                existing.weight = weight if existing.weight is None else max(existing.weight, weight)
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

        reference_ids = {
            evidence_id for item in list(nodes.values()) + list(edges.values())
            for evidence_id in item.evidence
        }
        unresolved = sorted(reference_ids - self.evidence_store.keys())
        membership = ("unknown" if any(not item.evidence_membership_known
                        for item in list(nodes.values()) + list(edges.values())) else
                      "partial" if unresolved else "known")
        return {
            "entities": [e.to_dict() for e in nodes.values()],
            "relations": [r.to_dict() for r in edges.values()],
            "total_entities": len(nodes),
            "total_relations": len(edges),
            "evidence": {eid: self.evidence_store[eid].to_dict()
                         for eid in sorted(reference_ids) if eid in self.evidence_store},
            "unresolved_evidence_ids": unresolved,
            "evidence_membership": membership,
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

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "EvidenceGraph":
        """Restaura IDs e registros existentes, sem criar fatos ou evidências.

        Contagens de exportações antigas não permitem inferir vínculos. Nesses
        casos a associação é desconhecida. IDs duplicados conflitantes e pesos
        não finitos são rejeitados em vez de corrigidos silenciosamente.
        """
        if not isinstance(payload, dict):
            raise ValueError("grafo exportado deve ser um objeto")

        def records(value):
            if isinstance(value, dict):
                items = value.items()
            elif isinstance(value, list):
                items = ((None, item) for item in value)
            else:
                raise ValueError("coleção do grafo deve ser lista ou objeto")
            for key, item in items:
                if not isinstance(item, dict):
                    raise ValueError("registro do grafo inválido")
                identifier = item.get("id", key)
                if not isinstance(identifier, str) or not identifier.strip():
                    raise ValueError("registro sem identificador original")
                if key is not None and key != identifier:
                    raise ValueError("identificador difere da chave exportada")
                yield identifier, item

        def text(value, field):
            if not isinstance(value, str):
                raise ValueError(f"{field} deve ser texto")
            return value

        def number(value, field, unit=False):
            if value is None:
                return None
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{field} deve ser número finito")
            if unit and not 0 <= value <= 1:
                raise ValueError(f"{field} fora do intervalo de 0 a 1")
            return value

        def references(item):
            refs = item.get("evidence")
            known = isinstance(refs, list) and item.get("evidence_membership") != "unknown"
            if refs is not None and not isinstance(refs, list):
                raise ValueError("referências de evidência devem ser uma lista")
            if any(not isinstance(ref, str) or not ref.strip() for ref in refs or []):
                raise ValueError("identificador de evidência inválido")
            declared = item.get("evidence_count")
            if declared is not None and (isinstance(declared, bool) or not isinstance(declared, int) or declared < 0):
                raise ValueError("contagem declarada de evidência inválida")
            return list(dict.fromkeys(refs or [])) if known else [], known, declared

        def insert(store, identifier, record):
            if identifier in store and store[identifier] != record:
                raise ValueError(f"identificador duplicado conflitante: {identifier}")
            store[identifier] = record

        graph = cls()
        for identifier, item in records(payload.get("evidence", {})):
            insert(graph.evidence_store, identifier, Evidence(
                id=identifier, text=text(item.get("text", ""), "evidência"),
                source=text(item.get("source", ""), "fonte"),
                source_type=text(item.get("source_type", ""), "tipo de fonte"),
                agent=text(item.get("agent", ""), "agente"),
                confidence=number(item.get("confidence"), "confiança", unit=True),
                timestamp=number(item.get("timestamp"), "instante"),
            ))
        for identifier, item in records(payload.get("entities", payload.get("nodes", {}))):
            refs, known, declared = references(item)
            aliases = item.get("aliases", [])
            metadata = item.get("metadata", {})
            if not isinstance(aliases, list) or any(not isinstance(alias, str) for alias in aliases):
                raise ValueError("aliases devem ser textos")
            if not isinstance(metadata, dict):
                raise ValueError("metadados devem ser um objeto")
            entity = Entity(
                id=identifier, name=text(item.get("name", item.get("label", item.get("title", identifier))), "nome"),
                entity_type=text(item.get("type", item.get("entity_type", item.get("group", "concept"))), "tipo"),
                description=text(item.get("description", ""), "descrição"),
                aliases=list(aliases), metadata=copy.deepcopy(metadata), evidence=refs,
                evidence_membership_known=known, declared_evidence_count=declared,
            )
            insert(graph.entities, identifier, entity)
        for entity in graph.entities.values():
            graph._name_index.setdefault(entity.name.lower().strip(), entity.id)
            graph._type_index.setdefault(entity.entity_type, []).append(entity.id)
            graph._adjacency[entity.id] = []
        for identifier, item in records(payload.get("relations", payload.get("edges", {}))):
            source = item.get("source", item.get("source_id", item.get("from")))
            target = item.get("target", item.get("target_id", item.get("to")))
            if not isinstance(source, str) or not isinstance(target, str) or source not in graph.entities or target not in graph.entities:
                raise ValueError("relação aponta para entidade ausente")
            refs, known, declared = references(item)
            bidirectional = item.get("bidirectional", False)
            if not isinstance(bidirectional, bool):
                raise ValueError("direção da relação inválida")
            relation = Relation(
                id=identifier, source_id=source, target_id=target,
                relation_type=text(item.get("type", item.get("relation_type", item.get("label", "UNKNOWN"))), "tipo de relação"),
                weight=number(item.get("weight", item.get("width")), "peso"),
                evidence=refs, bidirectional=bidirectional,
                evidence_membership_known=known, declared_evidence_count=declared,
            )
            insert(graph.relations, identifier, relation)
        for relation in graph.relations.values():
            graph._adjacency[relation.source_id].append(relation.id)
            if relation.bidirectional:
                graph._adjacency[relation.target_id].append(relation.id)
        return graph

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
