# -*- coding: utf-8 -*-
"""
SPEC-928: Benchmarks Jurídicos por Ramo
=======================================
Suíte conservadora para medir o comportamento especialista do ecossistema
em 7 ramos jurídicos.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional

from legal.specializations import (
    LEGAL_DOMAIN_PROFILES,
    LegalDomainProfile,
    route_legal_domain,
    assess_domain_coverage,
)


@dataclass(frozen=True)
class LegalBenchmarkCase:
    case_id: str
    query: str
    expected_domain: str
    required_statutes: List[str]
    required_issues: List[str]
    expected_risks: List[str]


LEGAL_BENCHMARK_CASES: List[LegalBenchmarkCase] = [
    LegalBenchmarkCase(
        case_id="penal_001",
        query="Habeas corpus contra prisão preventiva com discussão sobre dosimetria da pena e nulidade da prova.",
        expected_domain="penal",
        required_statutes=["Código Penal", "Código de Processo Penal"],
        required_issues=["prisão preventiva", "dosimetria"],
        expected_risks=["nulidade", "prova ilícita"],
    ),
    LegalBenchmarkCase(
        case_id="trabalho_001",
        query="Ação sobre horas extras, verbas rescisórias e justa causa em vínculo empregatício controverso.",
        expected_domain="trabalhista",
        required_statutes=["CLT"],
        required_issues=["horas extras", "verbas rescisórias"],
        expected_risks=["passivo trabalhista"],
    ),
    LegalBenchmarkCase(
        case_id="tributario_001",
        query="Discussão sobre crédito tributário de ICMS e execução fiscal com alegação de prescrição.",
        expected_domain="tributario",
        required_statutes=["CTN", "Lei de Execução Fiscal"],
        required_issues=["crédito tributário", "execução fiscal"],
        expected_risks=["autuação", "contencioso fiscal"],
    ),
    LegalBenchmarkCase(
        case_id="empresarial_001",
        query="Conflito entre sócios em sociedade limitada com risco de recuperação judicial e responsabilidade patrimonial.",
        expected_domain="empresarial",
        required_statutes=["Código Civil", "Lei de Recuperação e Falências"],
        required_issues=["sociedade", "recuperação judicial"],
        expected_risks=["desconsideração da personalidade jurídica"],
    ),
    LegalBenchmarkCase(
        case_id="administrativo_001",
        query="Análise de nulidade de licitação, ato administrativo e possível improbidade de agente público.",
        expected_domain="administrativo",
        required_statutes=["Lei de Licitações", "Lei de Improbidade Administrativa"],
        required_issues=["licitação", "ato administrativo"],
        expected_risks=["nulidade administrativa"],
    ),
    LegalBenchmarkCase(
        case_id="ambiental_001",
        query="Licenciamento ambiental com EIA/RIMA, dano ambiental e responsabilidade objetiva da empresa poluidora.",
        expected_domain="ambiental",
        required_statutes=["Política Nacional do Meio Ambiente", "Lei de Crimes Ambientais"],
        required_issues=["licenciamento ambiental", "dano ambiental"],
        expected_risks=["multa ambiental"],
    ),
    LegalBenchmarkCase(
        case_id="lgpd_001",
        query="Tratamento de dados pessoais com consentimento, controlador, operador e incidente de segurança sob a LGPD.",
        expected_domain="digital_lgpd",
        required_statutes=["LGPD", "Marco Civil da Internet"],
        required_issues=["base legal", "incidente de segurança"],
        expected_risks=["vazamento", "sanção regulatória"],
    ),
]


def benchmark_router() -> Dict[str, Any]:
    passed = 0
    details: List[Dict[str, Any]] = []
    for case in LEGAL_BENCHMARK_CASES:
        routed = route_legal_domain(case.query)
        ok = routed.domain_id == case.expected_domain
        passed += int(ok)
        details.append({
            "case_id": case.case_id,
            "expected_domain": case.expected_domain,
            "routed_domain": routed.domain_id,
            "passed": ok,
        })
    total = len(LEGAL_BENCHMARK_CASES)
    return {
        "total_cases": total,
        "passed": passed,
        "accuracy": round(passed / total if total else 0.0, 4),
        "details": details,
    }


def evaluate_domain_answer(case: LegalBenchmarkCase, answer: str) -> Dict[str, Any]:
    answer_lower = (answer or "").lower()

    statute_hits = sum(1 for s in case.required_statutes if s.lower() in answer_lower)
    issue_hits = sum(1 for i in case.required_issues if i.lower() in answer_lower)
    risk_hits = sum(1 for r in case.expected_risks if r.lower() in answer_lower)
    humility_hits = sum(
        1
        for token in ["cautela", "revisão humana", "incerteza", "depende", "parecer"]
        if token in answer_lower
    )

    statute_score = 30.0 * (statute_hits / max(len(case.required_statutes), 1))
    issue_score = 30.0 * (issue_hits / max(len(case.required_issues), 1))
    risk_score = 20.0 * (risk_hits / max(len(case.expected_risks), 1))
    humility_score = 20.0 if humility_hits > 0 else 0.0

    total = round(min(100.0, statute_score + issue_score + risk_score + humility_score), 2)
    return {
        "case_id": case.case_id,
        "total_score": total,
        "statute_score": round(statute_score, 2),
        "issue_score": round(issue_score, 2),
        "risk_score": round(risk_score, 2),
        "humility_score": round(humility_score, 2),
    }


def classify_domain_expertise_tier(score: float, external_validation: bool = False) -> str:
    if score >= 90.0:
        return "phd_validated" if external_validation else "phd_candidate"
    if score >= 75.0:
        return "specialist_advanced"
    if score >= 60.0:
        return "specialist"
    return "base"


def run_domain_benchmark_suite(
    answer_fn: Callable[[str, LegalDomainProfile], str],
    external_validation: bool = False,
) -> Dict[str, Any]:
    router = benchmark_router()
    case_results: List[Dict[str, Any]] = []
    per_domain: Dict[str, Dict[str, Any]] = {}

    for case in LEGAL_BENCHMARK_CASES:
        profile = LEGAL_DOMAIN_PROFILES[case.expected_domain]
        answer = answer_fn(case.query, profile)
        answer_eval = evaluate_domain_answer(case, answer)
        coverage = assess_domain_coverage(answer, case.expected_domain)
        total = round((answer_eval["total_score"] * 0.8) + (coverage * 0.2), 2)

        row = {
            "case_id": case.case_id,
            "domain": case.expected_domain,
            "query": case.query,
            "answer": answer,
            "answer_eval": answer_eval,
            "coverage_score": coverage,
            "final_case_score": total,
        }
        case_results.append(row)

        bucket = per_domain.setdefault(case.expected_domain, {"scores": [], "cases": 0})
        bucket["scores"].append(total)
        bucket["cases"] += 1

    for domain, data in per_domain.items():
        scores = data.pop("scores")
        data["average_score"] = round(sum(scores) / max(len(scores), 1), 2)

    avg_answer_score = round(
        sum(r["answer_eval"]["total_score"] for r in case_results) / max(len(case_results), 1),
        2,
    )
    avg_coverage_score = round(
        sum(r["coverage_score"] for r in case_results) / max(len(case_results), 1),
        2,
    )
    overall = round((router["accuracy"] * 100.0 * 0.35) + (avg_answer_score * 0.45) + (avg_coverage_score * 0.20), 2)

    return {
        "total_cases": len(LEGAL_BENCHMARK_CASES),
        "router_accuracy": router["accuracy"],
        "average_answer_score": avg_answer_score,
        "average_coverage_score": avg_coverage_score,
        "overall_score": overall,
        "tier": classify_domain_expertise_tier(overall, external_validation=external_validation),
        "per_domain": per_domain,
        "cases": case_results,
    }


__all__ = [
    "LegalBenchmarkCase",
    "LEGAL_BENCHMARK_CASES",
    "benchmark_router",
    "evaluate_domain_answer",
    "classify_domain_expertise_tier",
    "run_domain_benchmark_suite",
]
