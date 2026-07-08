# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-928: benchmarks jurídicos por ramo."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_benchmark_cases_cover_all_7_domains():
    from legal.benchmarks import LEGAL_BENCHMARK_CASES

    domains = {case.expected_domain for case in LEGAL_BENCHMARK_CASES}
    assert domains == {
        "penal",
        "trabalhista",
        "tributario",
        "empresarial",
        "administrativo",
        "ambiental",
        "digital_lgpd",
    }


def test_router_benchmark_reaches_full_accuracy_on_canonical_cases():
    from legal.benchmarks import benchmark_router

    report = benchmark_router()
    assert report["total_cases"] >= 7
    assert report["accuracy"] == 1.0


def test_evaluate_domain_answer_bounds():
    from legal.benchmarks import LEGAL_BENCHMARK_CASES, evaluate_domain_answer

    case = LEGAL_BENCHMARK_CASES[0]
    score = evaluate_domain_answer(
        case,
        "Resposta breve sem fundamentos.",
    )
    assert 0.0 <= score["total_score"] <= 100.0


def test_grounded_answer_scores_higher_than_shallow_answer():
    from legal.benchmarks import LEGAL_BENCHMARK_CASES, evaluate_domain_answer

    case = next(c for c in LEGAL_BENCHMARK_CASES if c.expected_domain == "digital_lgpd")
    weak = evaluate_domain_answer(
        case,
        "Isso depende do caso concreto.",
    )
    strong = evaluate_domain_answer(
        case,
        (
            "Com base na LGPD e no Marco Civil da Internet, é necessário analisar "
            "a base legal, o papel de controlador e operador, os riscos de incidente "
            "de segurança e a necessidade de revisão humana especializada antes da decisão final."
        ),
    )
    assert strong["total_score"] > weak["total_score"]


def test_classify_domain_expertise_tier_is_conservative():
    from legal.benchmarks import classify_domain_expertise_tier

    assert classify_domain_expertise_tier(95.0, external_validation=False) == "phd_candidate"
    assert classify_domain_expertise_tier(95.0, external_validation=True) == "phd_validated"
    assert classify_domain_expertise_tier(78.0, external_validation=False) == "specialist_advanced"


def test_run_domain_benchmark_suite_returns_consolidated_report():
    from legal.benchmarks import run_domain_benchmark_suite

    def answer_fn(query, profile):
        return (
            f"Com base em {profile.core_statutes[0]} e nos princípios de {profile.name}, "
            f"a questão exige cautela, análise dos riscos {', '.join(profile.risk_vectors[:1])} "
            f"e revisão humana especializada se houver incerteza."
        )

    report = run_domain_benchmark_suite(answer_fn=answer_fn, external_validation=False)
    assert report["total_cases"] >= 7
    assert 0.0 <= report["overall_score"] <= 100.0
    assert report["tier"] in {
        "base",
        "specialist",
        "specialist_advanced",
        "phd_candidate",
        "phd_validated",
    }
    assert len(report["per_domain"]) == 7
