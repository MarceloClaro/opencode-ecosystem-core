# -*- coding: utf-8 -*-
"""RAG Evidence Ledger — proveniência leve para RAG (SPEC-935-R1114).

Padrões portados do `renumics-rag` (MIT) sem adotar LangChain, ChromaDB,
Streamlit ou o monkeypatch global de ``sqlite3``:

- identidade do modelo de embeddings na metadata da coleção;
- identificador estável de documento por metadata;
- registro de pergunta/resposta com fontes;
- junção documentos x perguntas para medir uso observado.

A contagem de uso mede **uso observado**, não relevância, qualidade ou
causalidade. Nenhuma função aqui executa rede, modelo ou banco.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

__all__ = [
    "EmbeddingModelMismatch",
    "QuestionRecord",
    "assert_embedding_compatible",
    "collection_metadata",
    "join_documents_questions",
    "question_record_to_document",
    "stable_document_id",
]

_OPENAI_AZURE = frozenset({"openai", "azure"})


class EmbeddingModelMismatch(RuntimeError):
    """A coleção foi indexada por um modelo de embeddings incompatível."""


def collection_metadata(model_name: str, model_type: str) -> dict[str, str]:
    """Metadata mínima que identifica o modelo de embeddings de uma coleção."""
    if not isinstance(model_name, str) or not model_name.strip():
        raise ValueError("model_name deve ser uma string não vazia")
    if not isinstance(model_type, str) or not model_type.strip():
        raise ValueError("model_type deve ser uma string não vazia")
    return {"model_name": model_name, "model_type": model_type}


def assert_embedding_compatible(
    metadata: Mapping[str, Any] | None,
    model_name: str,
    model_type: str,
    *,
    allow_openai_azure_equivalence: bool = True,
) -> None:
    """Recusa consultar uma coleção indexada por outro modelo de embeddings.

    Metadata ausente ou incompleta não bloqueia: coleções antigas seguem
    legíveis. Quando a metadata existe, nome e tipo precisam coincidir. Por
    padrão, ``openai`` e ``azure`` com o mesmo nome são equivalentes.
    """
    if not metadata:
        return

    stored_name = metadata.get("model_name")
    stored_type = metadata.get("model_type")
    if stored_name is None or stored_type is None:
        return

    if stored_name != model_name:
        raise EmbeddingModelMismatch(
            f"coleção indexada por '{stored_name}', mas o modelo consultado é "
            f"'{model_name}'"
        )

    if stored_type == model_type:
        return

    if allow_openai_azure_equivalence and {stored_type, model_type} == _OPENAI_AZURE:
        return

    raise EmbeddingModelMismatch(
        f"coleção indexada por tipo '{stored_type}', mas o modelo consultado é "
        f"do tipo '{model_type}'"
    )


def stable_document_id(metadata: Mapping[str, Any]) -> str:
    """SHA-1 determinístico da metadata ordenada.

    A ordem das chaves não altera o resultado. O ID é adequado para
    indexação idempotente, não para segurança criptográfica.
    """
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata deve ser um Mapping")
    payload = json.dumps(
        dict(metadata), sort_keys=True, ensure_ascii=False, default=str
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class QuestionRecord:
    """Pergunta respondida e as fontes efetivamente usadas na resposta."""

    question: str
    answer: str
    sources: Sequence[str] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.question, str) or not isinstance(self.answer, str):
            raise TypeError("question e answer devem ser strings")
        if isinstance(self.sources, str):
            normalized: tuple[str, ...] = (self.sources,)
        else:
            normalized = tuple(str(source) for source in self.sources)
        object.__setattr__(self, "sources", normalized)


def question_record_to_document(record: QuestionRecord) -> dict[str, Any]:
    """Serializa um registro no formato documento + metadata do RAG."""
    return {
        "page_content": record.question,
        "metadata": {
            "answer": record.answer,
            "sources": ",".join(record.sources),
        },
    }


def _normalize_sources(raw: Any) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        return tuple(part.strip() for part in raw.split(",") if part.strip())
    if isinstance(raw, Sequence):
        return tuple(str(part) for part in raw)
    return (str(raw),)


def join_documents_questions(
    documents: Iterable[Mapping[str, Any]],
    questions: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Junta documentos e perguntas por ID de fonte.

    Cada documento recebe ``used_by_questions`` (IDs das perguntas que o
    usaram) e ``used_by_num_questions`` (contagem inteira). Documentos sem uso
    são preservados com lista vazia e contagem zero. Perguntas sem ``id``
    recebem o índice como identificador.
    """
    usage: dict[str, list[str]] = {}
    for index, question in enumerate(questions):
        question_id = str(question.get("id", index))
        for source in _normalize_sources(question.get("sources")):
            usage.setdefault(source, []).append(question_id)

    joined: list[dict[str, Any]] = []
    for document in documents:
        row = dict(document)
        document_id = row.get("id")
        used = usage.get(document_id, []) if document_id is not None else []
        row["used_by_questions"] = list(used)
        row["used_by_num_questions"] = len(used)
        joined.append(row)
    return joined
