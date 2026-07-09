# -*- coding: utf-8 -*-
"""
opencode-peer-review — Agentic Peer Review (R103)
==================================================
Agentic Peer Review with Rubric Engine, Review Ledger, and AuditGraph.

Componentes:
  - RubricEngine: 8 meta-dimensoes de qualidade
  - ReviewLedger: Claim-Evidence-Risk ledger
  - AuditGraph: Grafo de auditoria integrado com EvidenceGraph (R102)
  - MultiCriticReviewer: 4 especialistas (Methodology, Results, Literature, Ethics)
  - OrchestratorReviewer: Pipeline drafting->grounding->synthesis
"""

from .review_agent import (
    RubricEngine, ReviewLedger, AuditGraph,
    MultiCriticReviewer, OrchestratorReviewer
)

__all__ = [
    "RubricEngine", "ReviewLedger", "AuditGraph",
    "MultiCriticReviewer", "OrchestratorReviewer",
]
