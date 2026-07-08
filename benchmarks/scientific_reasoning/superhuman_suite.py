# -*- coding: utf-8 -*-
"""
Scientific Superhuman Benchmark Suite — SPEC-918
================================================
Camada conservadora de readiness científico superhuman.

Importante: este módulo NÃO declara superhuman verificado sem validação
externa explícita. Ele classifica o ecossistema como base, research-grade,
superhuman-candidate ou superhuman-verified conforme thresholds auditáveis.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from benchmarks.scientific_reasoning.runner import run_all_benchmarks
from mci.metabus import metabus


def classify_superhuman_tier(readiness_score: float,
                             external_validation: bool = False) -> str:
    """Classifica tier científico de forma conservadora."""
    if readiness_score >= 90 and external_validation:
        return "superhuman_verified"
    if readiness_score >= 85:
        return "superhuman_candidate"
    if readiness_score >= 60:
        return "research_grade"
    return "base"


def run_superhuman_suite(rag: Optional[Any] = None,
                         external_validation: bool = False,
                         pipeline_fn=None,
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Executa avaliação de readiness científico superhuman.

    Args:
        rag: objeto compatível com `ScientificRAG` (método `.answer`).
        external_validation: validação externa independente; necessário para
            `superhuman_verified`.
        pipeline_fn: pipeline científico opcional para benchmarks existentes.
    """
    benchmarks = run_all_benchmarks(pipeline_fn=pipeline_fn, verbose=False)
    benchmark_score = float(benchmarks.get("overall_score", 0.0)) * 100.0

    grounding = _evaluate_grounding(rag)
    grounding_score = float(grounding.get("groundedness", 0.0)) * 100.0

    robustness = _robustness_score(benchmarks)
    calibration = _calibration_score(benchmarks, grounding)
    reproducibility = _reproducibility_score(benchmarks, grounding)

    readiness = (
        0.35 * benchmark_score
        + 0.20 * grounding_score
        + 0.15 * robustness
        + 0.15 * calibration
        + 0.15 * reproducibility
    )
    readiness = round(min(100.0, max(0.0, readiness)), 2)
    tier = classify_superhuman_tier(readiness, external_validation=external_validation)
    report = {
        "readiness_score": readiness,
        "tier": tier,
        "external_validation": bool(external_validation),
        "claim_policy": (
            "verified only with external validation"
            if tier != "superhuman_verified"
            else "external validation supplied"
        ),
        "evidence": {
            "benchmarks": benchmarks,
            "grounding": grounding,
            "robustness": {"score": round(robustness, 2), "basis": "causal+bias+statistical tasks"},
            "calibration": {"score": round(calibration, 2), "basis": "confidence constrained by grounding"},
            "reproducibility": {"score": round(reproducibility, 2), "basis": "benchmark details + RAG evidence trace"},
        },
    }
    ctx = context or {}
    metabus.publish_subsystem_event(
        "superhuman",
        "suite.completed",
        {
            "readiness_score": readiness,
            "tier": tier,
            "external_validation": bool(external_validation),
            "marker": ctx.get("marker"),
        },
        source_agent="superhuman_suite",
    )
    metabus.memory.upsert_semantic_topic(
        "superhuman.readiness",
        lesson=f"Superhuman suite finalizada com readiness {readiness} e tier {tier}.",
        metadata={"last_readiness": readiness, "last_tier": tier},
    )
    metabus.memory.update_topic_confidence("superhuman", readiness / 100.0)
    return report


def _evaluate_grounding(rag: Optional[Any]) -> Dict[str, Any]:
    if rag is None:
        return {
            "groundedness": 0.0,
            "citation_coverage": 0.0,
            "evidence_count": 0,
            "abstention": 1.0,
            "queries": [],
        }

    queries = [
        "como distinguir correlação de causalidade?",
        "baixo poder estatístico gera quais riscos?",
        "múltiplas comparações e falso positivo",
    ]
    answers = []
    for query in queries:
        try:
            answers.append(rag.answer(query, top_k=2))
        except Exception as exc:
            answers.append({
                "query": query,
                "abstained": True,
                "groundedness": 0.0,
                "citation_coverage": 0.0,
                "evidence_count": 0,
                "error": str(exc),
            })

    n = len(answers) or 1
    avg_grounding = sum(float(a.get("groundedness", 0.0)) for a in answers) / n
    avg_citations = sum(float(a.get("citation_coverage", 0.0)) for a in answers) / n
    evidence_count = sum(int(a.get("evidence_count", 0)) for a in answers)
    abstentions = sum(1 for a in answers if a.get("abstained"))

    return {
        "groundedness": round(avg_grounding, 4),
        "citation_coverage": round(avg_citations, 4),
        "evidence_count": evidence_count,
        "abstention": round(abstentions / n, 4),
        "queries": [
            {
                "query": a.get("query"),
                "groundedness": a.get("groundedness", 0.0),
                "citation_coverage": a.get("citation_coverage", 0.0),
                "evidence_count": a.get("evidence_count", 0),
                "abstained": a.get("abstained", False),
            }
            for a in answers
        ],
    }


def _robustness_score(benchmarks: Dict[str, Any]) -> float:
    names = {b.get("benchmark", "") for b in benchmarks.get("benchmarks", [])}
    score = 60.0
    if "Causal Inference" in names:
        score += 10.0
    if "Bias Detection" in names:
        score += 10.0
    if "Statistical Interpretation" in names:
        score += 7.5
    if "Power Analysis" in names:
        score += 5.0
    return min(100.0, score)


def _calibration_score(benchmarks: Dict[str, Any], grounding: Dict[str, Any]) -> float:
    benchmark_component = float(benchmarks.get("overall_score", 0.0)) * 70.0
    grounding_component = float(grounding.get("groundedness", 0.0)) * 30.0
    # Penaliza abstenção total ou grounding ausente
    abstention_penalty = float(grounding.get("abstention", 0.0)) * 15.0
    return max(0.0, min(100.0, benchmark_component + grounding_component - abstention_penalty))


def _reproducibility_score(benchmarks: Dict[str, Any], grounding: Dict[str, Any]) -> float:
    details_count = sum(len(b.get("details", [])) for b in benchmarks.get("benchmarks", []))
    trace_component = min(60.0, details_count * 4.0)
    grounding_component = min(40.0, float(grounding.get("evidence_count", 0)) * 8.0)
    return min(100.0, trace_component + grounding_component)
