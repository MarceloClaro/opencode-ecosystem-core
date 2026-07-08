# -*- coding: utf-8 -*-
"""
TDD — SPEC-918 + SPEC-919
=========================

Testa a evolução rumo ao superhuman científico com RAG científico:
- recuperação híbrida com citações;
- abstenção quando não há evidência;
- métricas de grounding;
- suíte conservadora de readiness superhuman.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _sample_documents():
    from rag import ScientificDocument

    return [
        ScientificDocument(
            doc_id="pearl-2009",
            title="Causality",
            authors=["Pearl"],
            year=2009,
            source="book",
            text=(
                "Correlação não implica causalidade. Inferência causal exige "
                "modelo estrutural, controle de confounders e análise contrafactual. "
                "Intervenções do tipo do-calculus distinguem associação de causa."
            ),
        ),
        ScientificDocument(
            doc_id="ioannidis-2005",
            title="Why Most Published Research Findings Are False",
            authors=["Ioannidis"],
            year=2005,
            source="PLOS Medicine",
            text=(
                "Baixo poder estatístico, múltiplas comparações e viés de publicação "
                "aumentam a probabilidade de resultados falsos positivos. "
                "Efeitos significativos em estudos pequenos tendem ao winner's curse."
            ),
        ),
        ScientificDocument(
            doc_id="zadeh-1965",
            title="Fuzzy Sets",
            authors=["Zadeh"],
            year=1965,
            source="Information and Control",
            text=(
                "Lógica difusa representa graus de pertinência entre zero e um, "
                "permitindo raciocínio aproximado com termos linguísticos."
            ),
        ),
    ]


class TestScientificRAG:
    def test_indexes_documents_and_retrieves_citable_evidence(self):
        from rag import ScientificRAG

        rag = ScientificRAG()
        rag.index(_sample_documents())
        evidence = rag.retrieve("como distinguir correlação de causalidade?", top_k=2)

        assert len(evidence) >= 1
        assert evidence[0].doc_id == "pearl-2009"
        assert evidence[0].final_score > 0
        assert "Pearl (2009)" in evidence[0].citation
        assert evidence[0].chunk_id.startswith("pearl-2009#")

    def test_grounded_answer_contains_citations_and_evidence(self):
        from rag import ScientificRAG

        rag = ScientificRAG(min_score=0.05)
        rag.index(_sample_documents())
        answer = rag.answer("baixo poder estatístico gera quais riscos?", top_k=2)

        assert answer["abstained"] is False
        assert answer["evidence_count"] >= 1
        assert "Ioannidis (2005)" in answer["answer"]
        assert answer["groundedness"] > 0.5

    def test_abstains_when_evidence_is_insufficient(self):
        from rag import ScientificRAG

        rag = ScientificRAG(min_score=0.4)
        rag.index(_sample_documents())
        answer = rag.answer("qual é a composição química de uma estrela de nêutrons específica?", top_k=2)

        assert answer["abstained"] is True
        assert answer["groundedness"] == 0.0
        assert "evidência suficiente" in answer["answer"].lower()

    def test_grounding_evaluator_scores_citation_coverage(self):
        from rag import GroundingEvaluator, ScientificRAG

        rag = ScientificRAG(min_score=0.05)
        rag.index(_sample_documents())
        answer = rag.answer("múltiplas comparações e falso positivo", top_k=2)

        score = GroundingEvaluator().evaluate(answer)

        assert 0 <= score["groundedness"] <= 1
        assert score["citation_coverage"] > 0
        assert score["evidence_count"] >= 1


class TestScientificSuperhumanSuite:
    def test_existing_benchmarks_evaluate_pipeline_when_supplied(self):
        from benchmarks.scientific_reasoning.runner import run_all_benchmarks

        def always_wrong(task):
            return "z) resposta incorreta"

        report = run_all_benchmarks(pipeline_fn=always_wrong)

        assert report["total_tasks"] > 0
        assert report["total_passed"] == 0
        assert report["overall_score"] == 0.0

    def test_superhuman_suite_returns_conservative_readiness_report(self):
        from benchmarks.scientific_reasoning.superhuman_suite import run_superhuman_suite
        from rag import ScientificRAG

        rag = ScientificRAG(min_score=0.05)
        rag.index(_sample_documents())
        report = run_superhuman_suite(rag=rag, external_validation=False)

        assert 0 <= report["readiness_score"] <= 100
        assert report["tier"] in {
            "base",
            "research_grade",
            "superhuman_candidate",
            "superhuman_verified",
        }
        assert report["tier"] != "superhuman_verified"
        assert "grounding" in report["evidence"]
        assert "benchmarks" in report["evidence"]

    def test_superhuman_verified_requires_external_validation(self):
        from benchmarks.scientific_reasoning.superhuman_suite import classify_superhuman_tier

        assert classify_superhuman_tier(95.0, external_validation=False) == "superhuman_candidate"
        assert classify_superhuman_tier(95.0, external_validation=True) == "superhuman_verified"
        assert classify_superhuman_tier(75.0, external_validation=True) == "research_grade"

    def test_superhuman_suite_penalizes_absent_grounding(self):
        from benchmarks.scientific_reasoning.superhuman_suite import run_superhuman_suite


        report = run_superhuman_suite(rag=None, external_validation=False)

        assert report["evidence"]["grounding"]["groundedness"] == 0.0
        assert report["readiness_score"] < 90
        assert report["tier"] != "superhuman_verified"
