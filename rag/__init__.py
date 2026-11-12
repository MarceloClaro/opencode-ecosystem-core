# -*- coding: utf-8 -*-
"""
Scientific RAG — Grounding científico auditável.

SPEC-919: módulo canônico de RAG científico leve, sem dependências pesadas.
"""

from rag.evidence_ledger import (
    EmbeddingModelMismatch,
    QuestionRecord,
    assert_embedding_compatible,
    collection_metadata,
    join_documents_questions,
    question_record_to_document,
    stable_document_id,
)
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
    "EmbeddingModelMismatch",
    "QuestionRecord",
    "assert_embedding_compatible",
    "collection_metadata",
    "join_documents_questions",
    "question_record_to_document",
    "stable_document_id",
]
