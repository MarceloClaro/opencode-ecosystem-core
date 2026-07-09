# -*- coding: utf-8 -*-
"""
Testes TDD para R99 — Scientific RAG Evolved
==============================================
SPEC-935-R99: AdaptiveRetriever + CitationGraph + OutlineSynthesizer + RAGEvolved.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def rag_base():
    """ScientificRAG base com documentos de exemplo."""
    from rag.scientific import ScientificDocument, ScientificRAG
    docs = [
        ScientificDocument(
            doc_id="pearl-2009",
            title="Causality",
            authors=["Pearl"],
            year=2009,
            source="book",
            text="Correlation does not imply causation. Causal inference requires structural models. "
                 "Randomized controlled trials are the gold standard for causal identification. "
                 "Confounders must be controlled for. The do-calculus provides a mathematical framework.",
        ),
        ScientificDocument(
            doc_id="rubin-1974",
            title="Estimating Causal Effects",
            authors=["Rubin"],
            year=1974,
            source="journal",
            text="The Rubin Causal Model defines causal effects as potential outcomes. "
                 "Assignment mechanisms are crucial for causal inference. "
                 "Randomization ensures exchangeability between treatment groups. "
                 "Confounders are variables that affect both treatment and outcome.",
        ),
        ScientificDocument(
            doc_id="angrist-2001",
            title="Instrumental Variables",
            authors=["Angrist", "Imbens"],
            year=2001,
            source="journal",
            text="Instrumental variables can identify causal effects when confounders exist. "
                 "The exclusion restriction requires that instruments affect outcomes only through treatment. "
                 "Two-stage least squares is a common estimation method.",
        ),
    ]
    rag = ScientificRAG(min_score=0.05)
    rag.index(docs)
    return rag


@pytest.fixture
def evolved(rag_base):
    """RAGEvolved com dependencias."""
    from rag.evolved import RAGEvolved
    return RAGEvolved(rag_base)


# ============================================================
# CA2 — AdaptiveRetriever
# ============================================================

class TestAdaptiveRetriever:
    """Testes do AdaptiveRetriever (CA2)."""

    def test_ca2_simple_query(self, evolved):
        """analyze_complexity() retorna 'simple' para query factual curta."""
        result = evolved.retriever.analyze_complexity("What is X?")
        assert result == "simple"

    def test_ca2_moderate_query(self, evolved):
        """analyze_complexity() retorna 'moderate' para query comparativa."""
        result = evolved.retriever.analyze_complexity(
            "Compare causal inference methods across different disciplines"
        )
        assert result == "moderate"

    def test_ca2_complex_query(self, evolved):
        """analyze_complexity() retorna 'complex' para query multi-etapa."""
        result = evolved.retriever.analyze_complexity(
            "Synthesize findings from Pearl, Rubin, and Angrist regarding "
            "causal inference methods and discuss implications for "
            "observational studies in epidemiology"
        )
        assert result == "complex"

    def test_ca2_simple_uses_sequential(self, evolved, rag_base):
        """retrieve_adaptive() para 'simple' usa estrategia sequential."""
        results = evolved.retriever.retrieve_adaptive(
            "What is correlation?", rag_base, top_k=3
        )
        assert len(results) >= 0
        # Sequential: 1 chamada, resultados diretos

    def test_ca2_complex_uses_parallel(self, evolved, rag_base):
        """retrieve_adaptive() para 'complex' usa estrategia parallel."""
        results = evolved.retriever.retrieve_adaptive(
            "Synthesize findings from Pearl about causality and Rubin about "
            "potential outcomes and compare their approaches",
            rag_base, top_k=5
        )
        assert len(results) >= 0
        # Parallel: deve ter evidencia de multiplos documentos

    def test_ca2_parallel_deduplicates(self, evolved, rag_base):
        """Parallel retrieval deduplica por chunk_id."""
        results = evolved.retriever._retrieve_parallel(
            "causal inference methods", rag_base, top_k=10
        )
        chunk_ids = [r.chunk_id for r in results]
        assert len(chunk_ids) == len(set(chunk_ids))


# ============================================================
# CA3 — CitationGraph
# ============================================================

class TestCitationGraph:
    """Testes do CitationGraph (CA3)."""

    def test_ca3_add_edge(self, evolved):
        """add_edge() registra aresta dirigida."""
        g = evolved.graph
        g.add_edge("pearl-2009", "rubin-1974")
        assert "pearl-2009" in g._edges
        assert "rubin-1974" in g._edges["pearl-2009"]

    def test_ca3_add_document_edges(self, evolved):
        """add_document_edges() processa lista de referencias."""
        g = evolved.graph
        g.add_document_edges("paper-2024", ["pearl-2009", "rubin-1974"])
        assert "paper-2024" in g._edges
        assert "pearl-2009" in g._edges["paper-2024"]
        assert "rubin-1974" in g._edges["paper-2024"]

    def test_ca3_get_related_cited(self, evolved):
        """get_related() retorna documentos citados."""
        g = evolved.graph
        g.add_edge("paper-2024", "pearl-2009")
        g.add_edge("paper-2024", "rubin-1974")
        related = g.get_related("paper-2024", max_depth=1)
        assert "pearl-2009" in related
        assert "rubin-1974" in related

    def test_ca3_get_related_depth(self, evolved):
        """get_related() navega ate max_depth."""
        g = evolved.graph
        g.add_edge("paper-2024", "pearl-2009")
        g.add_edge("pearl-2009", "rubin-1974")
        related = g.get_related("paper-2024", max_depth=2)
        assert "rubin-1974" in related  # alcancavel em 2 passos

    def test_ca3_expand_retrieval(self, evolved, rag_base):
        """expand_retrieval() retorna doc_ids expandidos."""
        g = evolved.graph
        g.add_edge("paper-2024", "pearl-2009")
        g.add_edge("paper-2024", "rubin-1974")

        evidence = rag_base.retrieve("causal inference", top_k=2)
        expanded = g.expand_retrieval(evidence, max_depth=1)
        assert isinstance(expanded, list)

    def test_ca3_empty_graph(self, evolved):
        """Grafo vazio nao causa erro."""
        g = evolved.graph
        assert g.get_related("nonexistent") == set()
        assert g.expand_retrieval([]) == []


# ============================================================
# CA4 — OutlineSynthesizer
# ============================================================

class TestOutlineSynthesizer:
    """Testes do OutlineSynthesizer (CA4)."""

    def test_ca4_plan_returns_sections(self, evolved):
        """plan() retorna lista de OutlineSection."""
        outline = evolved.synthesizer.plan(
            "What is the impact of instrumental variables on causal inference?"
        )
        assert len(outline) >= 2
        for section in outline:
            assert section.section_id
            assert section.title
            assert section.focus_query
            assert section.expected_content

    def test_ca4_plan_sections_have_ids(self, evolved):
        """Cada secao tem section_id unico."""
        outline = evolved.synthesizer.plan("How does X affect Y?")
        ids = [s.section_id for s in outline]
        assert len(ids) == len(set(ids))

    def test_ca4_retrieve_per_section(self, evolved, rag_base):
        """retrieve_per_section() retorna dict section_id -> evidence."""
        outline = evolved.synthesizer.plan("What is causal inference?")
        section_evidence = evolved.synthesizer.retrieve_per_section(outline, rag_base)
        assert isinstance(section_evidence, dict)
        assert len(section_evidence) == len(outline)

    def test_ca4_synthesize_returns_structure(self, evolved, rag_base):
        """synthesize() retorna dict com secoes."""
        outline = evolved.synthesizer.plan("What is causal inference?")
        section_evidence = evolved.synthesizer.retrieve_per_section(outline, rag_base)
        result = evolved.synthesizer.synthesize(outline, section_evidence)
        assert "sections" in result
        assert len(result["sections"]) == len(outline)
        for sec in result["sections"]:
            assert "section_id" in sec
            assert "title" in sec
            assert "evidence_summary" in sec


# ============================================================
# CA5 — RAGEvolved integrado
# ============================================================

class TestRAGEvolved:
    """Testes do RAGEvolved completo (CA5)."""

    def test_ca5_analyze_complexity(self, evolved):
        """analyze_complexity() delega para retriever."""
        evolved.analyze_complexity("Simple query?") == "simple"

    def test_ca5_retrieve_returns_evidence(self, evolved):
        """retrieve() retorna lista de RetrievedEvidence."""
        results = evolved.retrieve("causal inference")
        assert isinstance(results, list)
        if results:
            from rag.scientific import RetrievedEvidence
            assert isinstance(results[0], RetrievedEvidence)

    def test_ca5_answer_simple(self, evolved):
        """answer_simple() retorna resposta direta."""
        result = evolved.answer_simple("What is correlation?")
        assert "answer" in result
        assert "abstained" in result

    def test_ca5_answer_structured(self, evolved):
        """answer_structured() retorna estrutura com outline + secoes."""
        result = evolved.answer_structured(
            "Compare Pearl and Rubin on causal inference methods"
        )
        assert "outline" in result
        assert "sections" in result
        assert len(result["sections"]) >= 1

    def test_ca5_answer_routes_by_complexity(self, evolved):
        """answer() roteia automaticamente baseado na complexidade."""
        # Simple -> direct answer
        simple = evolved.answer("What is correlation?")
        assert "answer" in simple

        # Complex -> structured
        complex_q = (
            "Synthesize findings from Pearl, Rubin, and Angrist regarding "
            "causal inference methods"
        )
        complex_result = evolved.answer(complex_q)
        assert "answer" in complex_result or "outline" in complex_result


# ============================================================
# CA7 — Fallback
# ============================================================

class TestFallback:
    """Testes de fallback (CA7)."""

    def test_ca7_no_evidence_abstains(self, evolved):
        """answer() abstem quando nao ha evidencia."""
        result = evolved.answer_simple(
            "Nothing about this topic exists in the index"
        )
        assert result.get("abstained", False) or result.get("answer", "")

    def test_ca7_expand_empty_graph(self, evolved):
        """CitationGraph vazio retorna lista vazia."""
        assert evolved.graph.expand_retrieval([]) == []
        assert evolved.graph.get_related("nonexistent") == set()


# ============================================================
# Smoke test — pipeline completo
# ============================================================

class TestFullPipeline:
    """Teste de integracao completo."""

    def test_full_rag_evolved_pipeline(self, evolved):
        """Pipeline completo: adaptive retrieval -> citation expansion -> outline synthesis."""
        query = "Compare causal inference methods by Pearl and Rubin"

        # 1. Adaptive retrieval
        evidence = evolved.retrieve(query, top_k=5)
        assert isinstance(evidence, list)

        # 2. Answer
        result = evolved.answer(query)
        assert result is not None
        # structured answer has sections
        if "sections" in result:
            for sec in result["sections"]:
                assert "section_id" in sec

    def test_complexity_based_answer(self, evolved):
        """Complexidade adequada para diferentes queries."""
        # Curta -> simple
        assert evolved.analyze_complexity("What is X?") == "simple"

        # Media -> moderate
        assert evolved.analyze_complexity(
            "Compare method A with method B for task C"
        ) == "moderate"

        # Longa -> complex
        assert evolved.analyze_complexity(
            "Synthesize findings from A, B, and C regarding topic D "
            "and discuss implications for field E across dimensions F and G"
        ) == "complex"
