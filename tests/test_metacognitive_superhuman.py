# -*- coding: utf-8 -*-
"""
TDD — SPEC-920: Metacognitive Superhuman Refinement Suite
=========================================================

Testa benchmark metacognitivo, classificação conservadora, detecção de erro
recorrente, atualização de confiança, qualidade de memória e humildade
epistêmica. Estes testes devem nascer RED antes da implementação.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _sample_traces():
    from mci.metacognitive_evaluator import MetacognitiveTrace

    return [
        MetacognitiveTrace(
            action_id="rag.answer",
            context="responder pergunta científica com evidência",
            outcome="success",
            reflection="Usei RAG científico com citação e abstive quando necessário.",
            confidence_before=0.55,
            confidence_after=0.72,
            strategy="scientific_rag",
            error_type=None,
            evidence_count=3,
            abstained=False,
        ),
        MetacognitiveTrace(
            action_id="benchmark.pipeline",
            context="avaliar pipeline científico",
            outcome="failure",
            reflection="Falha causada por autoaprovação indevida; corrigir avaliando pipeline_fn real.",
            confidence_before=0.70,
            confidence_after=0.46,
            strategy="static_reference",
            error_type="autoapproval",
            evidence_count=1,
            abstained=False,
        ),
        MetacognitiveTrace(
            action_id="benchmark.pipeline",
            context="avaliar pipeline científico novamente",
            outcome="success",
            reflection="Troquei para avaliação real do pipeline_fn, evitando repetir autoaprovação.",
            confidence_before=0.46,
            confidence_after=0.78,
            strategy="pipeline_evaluation",
            error_type=None,
            evidence_count=2,
            abstained=False,
        ),
        MetacognitiveTrace(
            action_id="science.claim",
            context="declarar superhuman verified sem validação externa",
            outcome="blocked",
            reflection="Bloqueei claim verified porque não havia validação externa explícita.",
            confidence_before=0.80,
            confidence_after=0.82,
            strategy="epistemic_humility",
            error_type="overclaim_risk",
            evidence_count=0,
            abstained=True,
        ),
    ]


class TestMetacognitiveTierPolicy:
    def test_verified_requires_external_validation(self):
        from mci.metacognitive_evaluator import classify_metacognitive_tier

        assert classify_metacognitive_tier(95, external_validation=False) == "metacognitive_superhuman_candidate"
        assert classify_metacognitive_tier(95, external_validation=True) == "metacognitive_superhuman_verified"
        assert classify_metacognitive_tier(76, external_validation=True) == "research_grade"
        assert classify_metacognitive_tier(45, external_validation=True) == "reactive"


class TestMetacognitiveEvaluator:
    def test_evaluator_returns_all_dimensions_and_recommendations(self):
        from mci.metacognitive_evaluator import MetacognitiveEvaluator

        report = MetacognitiveEvaluator().evaluate(_sample_traces(), external_validation=False)

        assert 0 <= report["readiness_score"] <= 100
        assert report["tier"] != "metacognitive_superhuman_verified"
        assert set(report["dimensions"].keys()) == {
            "awareness",
            "reflection",
            "adaptation",
            "memory_quality",
            "error_causality",
            "epistemic_humility",
        }
        assert isinstance(report["recommendations"], list)
        assert "evidence" in report

    def test_detects_repeated_error_and_strategy_change(self):
        from mci.metacognitive_evaluator import MetacognitiveEvaluator

        evaluator = MetacognitiveEvaluator()
        analysis = evaluator.analyze_error_patterns(_sample_traces())

        assert analysis["error_types"]["autoapproval"] == 1
        assert analysis["strategy_changes"] >= 1
        assert any("pipeline_evaluation" in item for item in analysis["effective_strategy_shifts"])

    def test_adaptation_score_rewards_confidence_correction(self):
        from mci.metacognitive_evaluator import MetacognitiveEvaluator

        score = MetacognitiveEvaluator().score_adaptation(_sample_traces())

        assert score > 0.6

    def test_epistemic_humility_rewards_abstention_on_low_evidence(self):
        from mci.metacognitive_evaluator import MetacognitiveEvaluator

        score = MetacognitiveEvaluator().score_epistemic_humility(_sample_traces())

        assert score >= 0.75


class TestMetacognitiveBenchmarkSuite:
    def test_suite_runs_deterministic_cases(self):
        from mci.metacognitive_evaluator import MetacognitiveBenchmarkSuite

        result = MetacognitiveBenchmarkSuite().run(external_validation=False)

        assert result["cases_total"] >= 6
        assert result["cases_passed"] >= 5
        assert result["report"]["tier"] in {
            "reactive",
            "reflective",
            "research_grade",
            "metacognitive_superhuman_candidate",
            "metacognitive_superhuman_verified",
        }
        assert result["report"]["tier"] != "metacognitive_superhuman_verified"

    def test_suite_penalizes_no_reflection_or_memory(self):
        from mci.metacognitive_evaluator import MetacognitiveEvaluator

        report = MetacognitiveEvaluator().evaluate([], external_validation=False)

        assert report["readiness_score"] < 50
        assert report["tier"] == "reactive"
        assert any("reflex" in rec.lower() or "memória" in rec.lower() for rec in report["recommendations"])

    def test_global_run_function_exports_report(self):
        from mci.metacognitive_evaluator import run_metacognitive_superhuman_suite

        report = run_metacognitive_superhuman_suite(external_validation=False)

        assert "readiness_score" in report
        assert "tier" in report
        assert "dimensions" in report
        assert report["tier"] != "metacognitive_superhuman_verified"
