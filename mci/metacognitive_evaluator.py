# -*- coding: utf-8 -*-
"""
Metacognitive Superhuman Refinement Suite — SPEC-920
====================================================
Avalia e refina a metacognição do ecossistema de forma conservadora.

Princípio central: não declarar metacognição superhuman verificada sem
validação externa explícita. Internamente, o máximo é candidate.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


DIMENSION_WEIGHTS = {
    "awareness": 0.20,
    "reflection": 0.20,
    "adaptation": 0.20,
    "memory_quality": 0.15,
    "error_causality": 0.15,
    "epistemic_humility": 0.10,
}


@dataclass(frozen=True)
class MetacognitiveTrace:
    """Unidade auditável de ação + reflexão + feedback metacognitivo."""

    action_id: str
    context: str
    outcome: str  # success | failure | blocked | abstained
    reflection: str
    confidence_before: float = 0.5
    confidence_after: float = 0.5
    strategy: str = "default"
    error_type: Optional[str] = None
    evidence_count: int = 0
    abstained: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "context": self.context,
            "outcome": self.outcome,
            "reflection": self.reflection,
            "confidence_before": self.confidence_before,
            "confidence_after": self.confidence_after,
            "strategy": self.strategy,
            "error_type": self.error_type,
            "evidence_count": self.evidence_count,
            "abstained": self.abstained,
        }


def classify_metacognitive_tier(readiness_score: float,
                                external_validation: bool = False) -> str:
    """Classifica maturidade metacognitiva com política anti-overclaim."""
    if readiness_score >= 90 and external_validation:
        return "metacognitive_superhuman_verified"
    if readiness_score >= 85:
        return "metacognitive_superhuman_candidate"
    if readiness_score >= 70:
        return "research_grade"
    if readiness_score >= 50:
        return "reflective"
    return "reactive"


class MetacognitiveEvaluator:
    """Avaliador heurístico e determinístico de metacognição."""

    REFLECTION_KEYWORDS = {
        "falha", "falhou", "sucesso", "lição", "licao", "corrigir",
        "evitar", "estratégia", "estrategia", "causa", "causada",
        "bloqueei", "abstive", "evidência", "evidencia", "validação",
    }

    CAUSAL_KEYWORDS = {
        "causa", "causada", "porque", "devido", "falha", "corrigir",
        "evitar", "autoaprovação", "autoaprovacao", "confounder",
    }

    def evaluate(self, traces: Iterable[MetacognitiveTrace],
                 external_validation: bool = False) -> Dict[str, Any]:
        trace_list = list(traces)
        dimensions = {
            "awareness": self.score_awareness(trace_list),
            "reflection": self.score_reflection(trace_list),
            "adaptation": self.score_adaptation(trace_list),
            "memory_quality": self.score_memory_quality(trace_list),
            "error_causality": self.score_error_causality(trace_list),
            "epistemic_humility": self.score_epistemic_humility(trace_list),
        }
        readiness = sum(dimensions[k] * DIMENSION_WEIGHTS[k] for k in dimensions) * 100.0
        readiness = round(max(0.0, min(100.0, readiness)), 2)
        tier = classify_metacognitive_tier(readiness, external_validation)
        error_patterns = self.analyze_error_patterns(trace_list)

        return {
            "readiness_score": readiness,
            "tier": tier,
            "external_validation": bool(external_validation),
            "dimensions": {k: round(v, 4) for k, v in dimensions.items()},
            "recommendations": self._recommendations(dimensions, trace_list, error_patterns),
            "evidence": {
                "traces_total": len(trace_list),
                "outcomes": dict(Counter(t.outcome for t in trace_list)),
                "error_patterns": error_patterns,
                "policy": "verified requer validação externa explícita",
            },
        }

    def score_awareness(self, traces: List[MetacognitiveTrace]) -> float:
        if not traces:
            return 0.0
        contextualized = sum(1 for t in traces if len(t.context.strip()) >= 12)
        confidence_seen = sum(1 for t in traces if t.confidence_before is not None and t.confidence_after is not None)
        evidence_seen = sum(1 for t in traces if t.evidence_count > 0 or t.abstained)
        return min(1.0, (0.4 * contextualized + 0.35 * confidence_seen + 0.25 * evidence_seen) / len(traces))

    def score_reflection(self, traces: List[MetacognitiveTrace]) -> float:
        if not traces:
            return 0.0
        scored = []
        for trace in traces:
            text = trace.reflection.lower()
            length_component = min(0.45, len(text) / 180.0)
            keyword_hits = sum(1 for kw in self.REFLECTION_KEYWORDS if kw in text)
            keyword_component = min(0.55, keyword_hits * 0.11)
            scored.append(length_component + keyword_component)
        return min(1.0, sum(scored) / len(scored))

    def score_adaptation(self, traces: List[MetacognitiveTrace]) -> float:
        if not traces:
            return 0.0
        good = 0
        for trace in traces:
            delta = trace.confidence_after - trace.confidence_before
            if trace.outcome == "success" and delta > 0:
                good += 1
            elif trace.outcome == "failure" and delta < 0:
                good += 1
            elif trace.outcome in {"blocked", "abstained"} and delta >= 0:
                good += 1
        base = good / len(traces)
        shifts = min(0.25, self.analyze_error_patterns(traces)["strategy_changes"] * 0.15)
        return min(1.0, base * 0.85 + shifts)

    def score_memory_quality(self, traces: List[MetacognitiveTrace]) -> float:
        if not traces:
            return 0.0
        action_diversity = len({t.action_id for t in traces}) / max(1, len(traces))
        contexts = [t.context.lower() for t in traces]
        has_recall_cues = sum(1 for c in contexts if any(k in c for k in ["novamente", "histórico", "historico", "repetir", "evidência", "validacao", "validação"]))
        evidence_component = sum(min(1.0, t.evidence_count / 3.0) for t in traces) / len(traces)
        return min(1.0, 0.35 + 0.25 * action_diversity + 0.20 * (has_recall_cues / len(traces)) + 0.20 * evidence_component)

    def score_error_causality(self, traces: List[MetacognitiveTrace]) -> float:
        failures = [t for t in traces if t.outcome == "failure" or t.error_type]
        if not traces:
            return 0.0
        if not failures:
            return 0.75
        explained = 0
        for trace in failures:
            text = f"{trace.error_type or ''} {trace.reflection}".lower()
            if any(kw in text for kw in self.CAUSAL_KEYWORDS):
                explained += 1
        return min(1.0, explained / len(failures))

    def score_epistemic_humility(self, traces: List[MetacognitiveTrace]) -> float:
        if not traces:
            return 0.0
        low_evidence = [t for t in traces if t.evidence_count == 0 or t.error_type == "overclaim_risk"]
        if not low_evidence:
            return 0.7
        humble = sum(1 for t in low_evidence if t.abstained or t.outcome in {"blocked", "abstained"})
        return min(1.0, humble / len(low_evidence))

    def analyze_error_patterns(self, traces: Iterable[MetacognitiveTrace]) -> Dict[str, Any]:
        trace_list = list(traces)
        error_types = Counter(t.error_type for t in trace_list if t.error_type)
        strategy_changes = 0
        effective_shifts: List[str] = []

        by_action: Dict[str, List[MetacognitiveTrace]] = {}
        for trace in trace_list:
            by_action.setdefault(trace.action_id, []).append(trace)

        for action_id, action_traces in by_action.items():
            previous: Optional[MetacognitiveTrace] = None
            for trace in action_traces:
                if previous and previous.strategy != trace.strategy:
                    strategy_changes += 1
                    if previous.outcome == "failure" and trace.outcome == "success":
                        effective_shifts.append(
                            f"{action_id}: {previous.strategy} -> {trace.strategy}"
                        )
                previous = trace

        repeated_errors = {
            err: count for err, count in error_types.items() if count > 1
        }
        return {
            "error_types": dict(error_types),
            "repeated_errors": repeated_errors,
            "strategy_changes": strategy_changes,
            "effective_strategy_shifts": effective_shifts,
        }

    def _recommendations(self, dimensions: Dict[str, float], traces: List[MetacognitiveTrace],
                         error_patterns: Dict[str, Any]) -> List[str]:
        recs: List[str] = []
        if not traces:
            return [
                "Adicionar reflexões pós-tarefa ao MetaBus/Reflexion.",
                "Popular memória metacognitiva episódica antes de avaliar maturidade.",
                "Executar SDD/TDD com registro de confiança para gerar dados de adaptação.",
            ]
        if dimensions["reflection"] < 0.7:
            recs.append("Aumentar densidade causal das reflexões: causa, alternativa e lição acionável.")
        if dimensions["memory_quality"] < 0.7:
            recs.append("Melhorar memória: incluir contexto, evidência, estratégia e ligação com eventos anteriores.")
        if dimensions["adaptation"] < 0.7:
            recs.append("Ajustar confiança de forma mais sensível a sucesso/falha e registrar mudança de estratégia.")
        if dimensions["epistemic_humility"] < 0.8:
            recs.append("Reforçar abstenção/declaração conservadora quando evidência ou validação externa for baixa.")
        if error_patterns["repeated_errors"]:
            recs.append("Priorizar mitigação de erros repetidos antes de novos recursos.")
        if not recs:
            recs.append("Manter política conservadora: candidate interno, verified apenas com validação externa.")
        return recs


class MetacognitiveBenchmarkSuite:
    """Benchmark determinístico de metacognição do ecossistema."""

    def __init__(self):
        self.evaluator = MetacognitiveEvaluator()

    def run(self, external_validation: bool = False) -> Dict[str, Any]:
        traces = self._default_traces()
        report = self.evaluator.evaluate(traces, external_validation=external_validation)
        cases = self._cases(traces, report)
        passed = sum(1 for case in cases if case["passed"])
        return {
            "cases_total": len(cases),
            "cases_passed": passed,
            "case_details": cases,
            "report": report,
        }

    def _cases(self, traces: List[MetacognitiveTrace], report: Dict[str, Any]) -> List[Dict[str, Any]]:
        analysis = self.evaluator.analyze_error_patterns(traces)
        return [
            {"case": "has_traces", "passed": len(traces) >= 4},
            {"case": "reflection_quality", "passed": report["dimensions"]["reflection"] >= 0.55},
            {"case": "adaptation", "passed": report["dimensions"]["adaptation"] >= 0.60},
            {"case": "error_causality", "passed": report["dimensions"]["error_causality"] >= 0.70},
            {"case": "epistemic_humility", "passed": report["dimensions"]["epistemic_humility"] >= 0.75},
            {"case": "strategy_shift", "passed": analysis["strategy_changes"] >= 1},
            {"case": "no_verified_without_external", "passed": report["tier"] != "metacognitive_superhuman_verified"},
        ]

    @staticmethod
    def _default_traces() -> List[MetacognitiveTrace]:
        return [
            MetacognitiveTrace(
                action_id="sdd.spec",
                context="criar especificação antes de implementar",
                outcome="success",
                reflection="Sucesso: SDD evitou divergência entre contrato e implementação.",
                confidence_before=0.60,
                confidence_after=0.78,
                strategy="sdd_first",
                evidence_count=2,
            ),
            MetacognitiveTrace(
                action_id="tdd.red_green",
                context="executar RED antes do GREEN",
                outcome="success",
                reflection="Estratégia eficaz: teste RED confirmou ausência do módulo antes do código.",
                confidence_before=0.58,
                confidence_after=0.81,
                strategy="red_green_refactor",
                evidence_count=3,
            ),
            MetacognitiveTrace(
                action_id="benchmark.pipeline",
                context="benchmark científico com autoaprovação",
                outcome="failure",
                reflection="Falha causada por autoaprovação; corrigir para avaliar pipeline_fn real.",
                confidence_before=0.72,
                confidence_after=0.45,
                strategy="static_reference",
                error_type="autoapproval",
                evidence_count=1,
            ),
            MetacognitiveTrace(
                action_id="benchmark.pipeline",
                context="benchmark científico novamente após correção",
                outcome="success",
                reflection="Troquei estratégia para pipeline_evaluation e evitei repetir o erro.",
                confidence_before=0.45,
                confidence_after=0.79,
                strategy="pipeline_evaluation",
                evidence_count=2,
            ),
            MetacognitiveTrace(
                action_id="claim.verified",
                context="claim superhuman verified sem validação externa",
                outcome="blocked",
                reflection="Bloqueei overclaim; verified requer validação externa explícita.",
                confidence_before=0.80,
                confidence_after=0.82,
                strategy="epistemic_humility",
                error_type="overclaim_risk",
                evidence_count=0,
                abstained=True,
            ),
            MetacognitiveTrace(
                action_id="artifact.restore",
                context="testes removeram artefatos rastreados; restaurar antes do commit",
                outcome="success",
                reflection="Lição: sempre verificar git ls-files -d após validação operacional.",
                confidence_before=0.65,
                confidence_after=0.86,
                strategy="artifact_guard",
                evidence_count=2,
            ),
        ]


def run_metacognitive_superhuman_suite(external_validation: bool = False) -> Dict[str, Any]:
    """Executa a suíte SPEC-920 e retorna o relatório principal."""
    suite_result = MetacognitiveBenchmarkSuite().run(external_validation=external_validation)
    report = dict(suite_result["report"])
    report["benchmark"] = {
        "cases_total": suite_result["cases_total"],
        "cases_passed": suite_result["cases_passed"],
        "case_details": suite_result["case_details"],
    }
    return report
