# -*- coding: utf-8 -*-
"""
Scientific RAG — Grounding científico auditável.

SPEC-919: módulo canônico de RAG científico leve, sem dependências pesadas.
"""

from rag.scientific import (
    GroundingEvaluator,
    RetrievedEvidence,
    ScientificDocument,
    ScientificRAG,
)

__all__ = [
    "ScientificDocument",
    "RetrievedEvidence",
    "ScientificRAG",
    "GroundingEvaluator",
]
