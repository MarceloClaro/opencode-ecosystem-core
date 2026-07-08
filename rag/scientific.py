# -*- coding: utf-8 -*-
"""
Scientific RAG — recuperação científica com grounding e citações.
=================================================================
Implementa a SPEC-919 com componentes determinísticos e leves:

- indexação de documentos científicos com metadados;
- chunking citável;
- busca híbrida lexical + semantic-lite;
- reranking científico;
- resposta grounded com abstenção;
- métricas de groundedness e cobertura de citações.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from mci.metabus import metabus


@dataclass(frozen=True)
class ScientificDocument:
    """Documento científico indexável."""

    doc_id: str
    title: str
    authors: List[str]
    year: int
    source: str
    text: str


@dataclass(frozen=True)
class RetrievedEvidence:
    """Evidência recuperada e citável."""

    doc_id: str
    chunk_id: str
    title: str
    authors: List[str]
    year: int
    source: str
    text: str
    lexical_score: float
    semantic_score: float
    final_score: float
    citation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "source": self.source,
            "text": self.text,
            "lexical_score": round(self.lexical_score, 4),
            "semantic_score": round(self.semantic_score, 4),
            "final_score": round(self.final_score, 4),
            "citation": self.citation,
        }


@dataclass(frozen=True)
class _Chunk:
    doc: ScientificDocument
    chunk_id: str
    text: str
    tokens: Tuple[str, ...]
    expanded_tokens: Tuple[str, ...]


class ScientificRAG:
    """RAG científico determinístico com busca híbrida e abstenção.

    Args:
        min_score: score mínimo para aceitar evidência.
        chunk_sentences: número de frases por chunk.
    """

    SCIENCE_TERMS = {
        "randomizacao", "randomização", "pvalor", "p-valor", "p", "confounder",
        "confounders", "causalidade", "causal", "correlacao", "correlação",
        "power", "poder", "replicacao", "replicação", "intervalo", "confianca",
        "confiança", "viés", "vies", "bias", "estatistico", "estatístico",
        "contrafactual", "intervencao", "intervenção", "hipotese", "hipótese",
        "evidencia", "evidência",
    }

    SYNONYMS = {
        "causa": {"causal", "causalidade", "efeito", "intervencao", "contrafactual"},
        "causalidade": {"causal", "causa", "confounder", "contrafactual"},
        "correlacao": {"associacao", "associação", "causalidade", "causa"},
        "correlação": {"associacao", "associação", "causalidade", "causa"},
        "poder": {"power", "amostral", "amostra", "falso", "negativo"},
        "power": {"poder", "amostral", "amostra"},
        "falso": {"positivo", "negativo", "erro"},
        "positivo": {"falso", "erro", "significativo"},
        "vies": {"bias", "publicacao", "seleção", "selecao"},
        "viés": {"bias", "publicacao", "seleção", "selecao"},
        "difusa": {"fuzzy", "pertinencia", "aproximado"},
        "fuzzy": {"difusa", "pertinencia", "aproximado"},
    }

    STOPWORDS = {
        "a", "o", "os", "as", "um", "uma", "de", "da", "do", "das", "dos",
        "e", "ou", "em", "no", "na", "nos", "nas", "para", "por", "com",
        "como", "qual", "quais", "que", "se", "é", "ser", "ao", "aos", "à",
        "sobre", "entre", "quando", "onde", "especifica", "especifico",
    }

    def __init__(self, min_score: float = 0.08, chunk_sentences: int = 2):
        self.min_score = min_score
        self.chunk_sentences = max(1, chunk_sentences)
        self._chunks: List[_Chunk] = []

    # ── Indexação ────────────────────────────────────────────────────────

    def index(self, documents: Sequence[ScientificDocument]) -> None:
        """Indexa documentos científicos."""
        self._chunks.clear()
        for doc in documents:
            for idx, chunk_text in enumerate(self._chunk_text(doc.text), start=1):
                tokens = tuple(self._tokenize(chunk_text))
                expanded = tuple(sorted(self._expand_tokens(tokens)))
                self._chunks.append(_Chunk(
                    doc=doc,
                    chunk_id=f"{doc.doc_id}#{idx}",
                    text=chunk_text,
                    tokens=tokens,
                    expanded_tokens=expanded,
                ))
        metabus.publish_subsystem_event(
            "rag",
            "index.updated",
            {"documents": len(documents), "chunks": len(self._chunks)},
            source_agent="scientific_rag",
        )
        metabus.memory.upsert_semantic_topic(
            "rag.scientific",
            lesson=f"ScientificRAG indexado com {len(documents)} documentos e {len(self._chunks)} chunks.",
            metadata={"documents": len(documents), "chunks": len(self._chunks)},
        )

    @property
    def size(self) -> int:
        return len(self._chunks)

    # ── Recuperação ──────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedEvidence]:
        """Recupera top-k evidências citáveis para uma consulta."""
        q_tokens = tuple(self._tokenize(query))
        q_expanded = self._expand_tokens(q_tokens)
        scored: List[RetrievedEvidence] = []

        for chunk in self._chunks:
            lexical = self._overlap_score(set(q_tokens), set(chunk.tokens))
            semantic = self._overlap_score(q_expanded, set(chunk.expanded_tokens))
            method_bonus = self._scientific_bonus(set(q_tokens), set(chunk.tokens))
            metadata_bonus = 0.02 if chunk.doc.authors and chunk.doc.year else 0.0
            directness_bonus = self._directness_bonus(q_tokens, chunk.tokens)
            final = min(1.0, 0.55 * lexical + 0.35 * semantic + method_bonus + metadata_bonus + directness_bonus)

            if final > 0:
                scored.append(RetrievedEvidence(
                    doc_id=chunk.doc.doc_id,
                    chunk_id=chunk.chunk_id,
                    title=chunk.doc.title,
                    authors=chunk.doc.authors,
                    year=chunk.doc.year,
                    source=chunk.doc.source,
                    text=chunk.text,
                    lexical_score=lexical,
                    semantic_score=semantic,
                    final_score=round(final, 6),
                    citation=self._citation(chunk.doc, chunk.chunk_id),
                ))

        scored.sort(key=lambda ev: ev.final_score, reverse=True)
        return scored[:top_k]

    def answer(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Gera resposta grounded ou abstém se evidência for insuficiente."""
        evidence = [ev for ev in self.retrieve(query, top_k=top_k)
                    if ev.final_score >= self.min_score]

        if not evidence:
            result = {
                "query": query,
                "answer": "Não há evidência suficiente no índice RAG para responder com grounding.",
                "abstained": True,
                "evidence": [],
                "evidence_count": 0,
                "groundedness": 0.0,
                "citation_coverage": 0.0,
            }
            metabus.publish_subsystem_event(
                "rag",
                "answer.generated",
                {"query": query, "abstained": True, "evidence_count": 0, "groundedness": 0.0},
                source_agent="scientific_rag",
            )
            metabus.memory.update_topic_confidence("rag.scientific", 0.2)
            return result

        evidence_fragments = []
        for ev in evidence:
            evidence_fragments.append(
                f"[{ev.citation}] {self._shorten(ev.text, 220)}"
            )
        answer_text = (
            "Resposta ancorada em evidências recuperadas: "
            + " ".join(evidence_fragments)
        )
        grounding = GroundingEvaluator().evaluate({
            "query": query,
            "answer": answer_text,
            "abstained": False,
            "evidence": [ev.to_dict() for ev in evidence],
        })

        result = {
            "query": query,
            "answer": answer_text,
            "abstained": False,
            "evidence": [ev.to_dict() for ev in evidence],
            "evidence_count": len(evidence),
            "groundedness": grounding["groundedness"],
            "citation_coverage": grounding["citation_coverage"],
        }
        metabus.publish_subsystem_event(
            "rag",
            "answer.generated",
            {
                "query": query,
                "abstained": False,
                "evidence_count": len(evidence),
                "groundedness": grounding["groundedness"],
            },
            source_agent="scientific_rag",
        )
        metabus.memory.upsert_semantic_topic(
            "rag.answers",
            lesson=f"RAG respondeu consulta '{query[:80]}' com {len(evidence)} evidências.",
            metadata={"last_groundedness": grounding["groundedness"]},
        )
        metabus.memory.update_topic_confidence("rag.scientific", grounding["groundedness"])
        return result

    # ── Scoring ──────────────────────────────────────────────────────────

    def _chunk_text(self, text: str) -> List[str]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        if not sentences:
            return []
        chunks = []
        for i in range(0, len(sentences), self.chunk_sentences):
            chunks.append(" ".join(sentences[i:i + self.chunk_sentences]))
        return chunks

    @classmethod
    def _tokenize(cls, text: str) -> List[str]:
        text = cls._normalize(text)
        raw = re.findall(r"[a-z0-9][a-z0-9\-']*", text)
        tokens = []
        for token in raw:
            token = token.strip("-'")
            if not token or token in cls.STOPWORDS or len(token) <= 2:
                continue
            tokens.append(cls._stem(token))
        return tokens

    @staticmethod
    def _normalize(text: str) -> str:
        text = unicodedata.normalize("NFKD", str(text))
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return text.lower()

    @staticmethod
    def _stem(token: str) -> str:
        for suffix in ("coes", "ções", "cao", "ção", "mente", "s"):
            if token.endswith(suffix) and len(token) > len(suffix) + 3:
                return token[: -len(suffix)]
        return token

    @classmethod
    def _expand_tokens(cls, tokens: Iterable[str]) -> set:
        expanded = set(tokens)
        for token in list(expanded):
            expanded.update(cls.SYNONYMS.get(token, set()))
        return expanded

    @staticmethod
    def _overlap_score(query_tokens: set, doc_tokens: set) -> float:
        if not query_tokens or not doc_tokens:
            return 0.0
        overlap = query_tokens & doc_tokens
        # normaliza pelo tamanho da query para favorecer cobertura da pergunta
        return len(overlap) / max(1, len(query_tokens))

    @classmethod
    def _scientific_bonus(cls, q_tokens: set, d_tokens: set) -> float:
        science_overlap = (q_tokens & d_tokens) & cls.SCIENCE_TERMS
        return min(0.08, 0.03 * len(science_overlap))

    @staticmethod
    def _directness_bonus(q_tokens: Sequence[str], d_tokens: Sequence[str]) -> float:
        q = list(q_tokens)
        d = list(d_tokens)
        if not q or not d:
            return 0.0
        bigrams_q = set(zip(q, q[1:]))
        bigrams_d = set(zip(d, d[1:]))
        return min(0.05, 0.025 * len(bigrams_q & bigrams_d))

    @staticmethod
    def _citation(doc: ScientificDocument, chunk_id: str) -> str:
        author = doc.authors[0] if doc.authors else "Autor desconhecido"
        return f"{author} ({doc.year}), {chunk_id}"

    @staticmethod
    def _shorten(text: str, limit: int) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


class GroundingEvaluator:
    """Avalia grounding de respostas RAG."""

    def evaluate(self, answer: Dict[str, Any]) -> Dict[str, Any]:
        evidence = answer.get("evidence", []) or []
        abstained = bool(answer.get("abstained", False))
        evidence_count = len(evidence)

        if abstained or evidence_count == 0:
            return {
                "groundedness": 0.0,
                "citation_coverage": 0.0,
                "evidence_count": 0,
                "abstention": 1.0 if abstained else 0.0,
            }

        citations = [ev.get("citation", "") for ev in evidence if isinstance(ev, dict)]
        cited = sum(1 for c in citations if c and re.search(r"\(\d{4}\)", c))
        citation_coverage = cited / evidence_count if evidence_count else 0.0
        avg_score = sum(float(ev.get("final_score", 0.0)) for ev in evidence) / evidence_count
        grounding = min(1.0, 0.45 + 0.35 * citation_coverage + 0.20 * min(1.0, avg_score * 2))

        return {
            "groundedness": round(grounding, 4),
            "citation_coverage": round(citation_coverage, 4),
            "evidence_count": evidence_count,
            "abstention": 0.0,
        }
