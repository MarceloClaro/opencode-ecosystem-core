# -*- coding: utf-8 -*-
"""Testes do RAG Evidence Ledger (SPEC-935-R1114).

Ciclo TDD: este arquivo é escrito antes de rag/evidence_ledger.py.
"""

from __future__ import annotations

import pytest

from rag.evidence_ledger import (
    EmbeddingModelMismatch,
    QuestionRecord,
    assert_embedding_compatible,
    collection_metadata,
    join_documents_questions,
    question_record_to_document,
    stable_document_id,
)


def test_collection_metadata_roundtrip() -> None:
    metadata = collection_metadata("text-embedding-3-large", "openai")
    assert metadata == {
        "model_name": "text-embedding-3-large",
        "model_type": "openai",
    }


def test_compatible_same_model_passes() -> None:
    metadata = collection_metadata("text-embedding-3-large", "openai")
    assert_embedding_compatible(metadata, "text-embedding-3-large", "openai")


def test_mismatch_model_name_raises() -> None:
    metadata = collection_metadata("text-embedding-3-large", "openai")
    with pytest.raises(EmbeddingModelMismatch):
        assert_embedding_compatible(metadata, "text-embedding-ada-002", "openai")


def test_mismatch_model_type_raises() -> None:
    metadata = collection_metadata("gte-base", "hf")
    with pytest.raises(EmbeddingModelMismatch):
        assert_embedding_compatible(metadata, "gte-base", "openai")


def test_openai_azure_equivalence() -> None:
    metadata = collection_metadata("text-embedding-3-large", "azure")
    assert_embedding_compatible(metadata, "text-embedding-3-large", "openai")


def test_openai_azure_equivalence_requires_same_name() -> None:
    metadata = collection_metadata("text-embedding-3-large", "azure")
    with pytest.raises(EmbeddingModelMismatch):
        assert_embedding_compatible(metadata, "text-embedding-ada-002", "openai")


def test_missing_metadata_is_noop() -> None:
    assert_embedding_compatible({}, "any-model", "hf")
    assert_embedding_compatible(None, "any-model", "hf")


def test_stable_document_id_is_deterministic_and_order_insensitive() -> None:
    first = stable_document_id({"source": "a.html", "page": 1, "start_index": 0})
    second = stable_document_id({"start_index": 0, "page": 1, "source": "a.html"})
    assert first == second
    assert len(first) == 40
    assert first.isalnum()


def test_stable_document_id_differs_for_distinct_metadata() -> None:
    first = stable_document_id({"source": "a.html", "page": 1})
    second = stable_document_id({"source": "a.html", "page": 2})
    assert first != second


def test_stable_document_id_rejects_non_mapping() -> None:
    with pytest.raises(TypeError):
        stable_document_id(["not", "a", "mapping"])  # type: ignore[arg-type]


def test_question_record_to_document_preserves_sources() -> None:
    record = QuestionRecord(
        question="Quem construiu o Nürburgring?",
        answer="Foi construído em 1925.",
        sources=("doc-1", "doc-2"),
    )
    document = question_record_to_document(record)
    assert document["page_content"] == record.question
    assert document["metadata"]["answer"] == record.answer
    assert document["metadata"]["sources"] == "doc-1,doc-2"


def test_question_record_normalizes_string_sources() -> None:
    record = QuestionRecord(question="q", answer="a", sources="doc-1")  # type: ignore[arg-type]
    document = question_record_to_document(record)
    assert document["metadata"]["sources"] == "doc-1"


def test_join_counts_usage() -> None:
    documents = [
        {"id": "doc-1", "source": "a.html"},
        {"id": "doc-2", "source": "b.html"},
    ]
    questions = [
        {"id": "q-1", "sources": ["doc-1"]},
        {"id": "q-2", "sources": ["doc-1", "doc-2"]},
    ]
    joined = join_documents_questions(documents, questions)
    by_id = {row["id"]: row for row in joined}
    assert by_id["doc-1"]["used_by_questions"] == ["q-1", "q-2"]
    assert by_id["doc-1"]["used_by_num_questions"] == 2
    assert by_id["doc-2"]["used_by_questions"] == ["q-2"]
    assert by_id["doc-2"]["used_by_num_questions"] == 1


def test_join_handles_empty_and_unknown_sources() -> None:
    documents = [{"id": "doc-1"}]
    questions = [{"id": "q-1", "sources": ["doc-unknown"]}]
    joined = join_documents_questions(documents, questions)
    assert joined[0]["used_by_questions"] == []
    assert joined[0]["used_by_num_questions"] == 0
    assert join_documents_questions([], []) == []


def test_join_accepts_comma_separated_sources() -> None:
    documents = [{"id": "doc-1"}, {"id": "doc-2"}]
    questions = [{"id": "q-1", "sources": "doc-1,doc-2"}]
    joined = join_documents_questions(documents, questions)
    assert [row["used_by_num_questions"] for row in joined] == [1, 1]
