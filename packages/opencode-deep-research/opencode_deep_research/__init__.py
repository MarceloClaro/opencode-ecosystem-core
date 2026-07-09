# -*- coding: utf-8 -*-
"""
opencode-deep-research — Deep Research Agent (R102)
====================================================
DeepEvidence-style hierarchical orchestration with evidence graphs.

Componentes:
  - EvidenceGraph: Entity-Relation-Evidence knowledge graph
  - BFRSAgent: Broad-First Research Search (varredura ampla)
  - DFRSAgent: Deep-First Research Search (mergulho profundo)
  - KnowledgeBaseRegistry: Gerenciamento de fontes
  - Orchestrator: Coordenacao BFRS+DFRS
"""

from .evidence_graph import EvidenceGraph, Entity, Relation, Evidence
from .deep_research import BFRSAgent, DFRSAgent, KnowledgeBaseRegistry, OrchestratorAgent

__all__ = [
    "EvidenceGraph", "Entity", "Relation", "Evidence",
    "BFRSAgent", "DFRSAgent", "KnowledgeBaseRegistry", "Orchestrator",
]
