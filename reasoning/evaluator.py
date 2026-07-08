# -*- coding: utf-8 -*-
"""
ReasoningEvaluator — Métricas de qualidade para resultados de raciocínio
========================================================================
SPEC-917: calcula métricas leves e auditáveis: coerência, cobertura,
profundidade, confiança e custo temporal.
"""

from __future__ import annotations

from typing import Any, Dict

from reasoning.engines import ReasoningResult


class ReasoningEvaluator:
    """Avaliador heurístico de qualidade de raciocínio."""

    def evaluate(self, result: ReasoningResult) -> Dict[str, float]:
        """Retorna métricas normalizadas [0, 1]."""
        steps = result.steps or []
        conclusion = result.conclusion or ""

        coherence = self._coherence(steps, conclusion)
        coverage = self._coverage(result.query, steps, conclusion)
        depth = min(1.0, len(steps) / 5.0)
        confidence = max(0.0, min(1.0, float(result.confidence)))
        speed = self._speed_score(result.duration_s)

        overall = (
            0.30 * coherence +
            0.25 * coverage +
            0.20 * depth +
            0.15 * confidence +
            0.10 * speed
        )

        return {
            "overall": round(overall, 4),
            "coherence": round(coherence, 4),
            "coverage": round(coverage, 4),
            "depth": round(depth, 4),
            "confidence": round(confidence, 4),
            "speed": round(speed, 4),
        }

    @staticmethod
    def _coherence(steps: Any, conclusion: str) -> float:
        if not steps or not conclusion:
            return 0.2
        joined = " ".join(str(s).lower() for s in steps)
        signals = ["premissa", "inferência", "síntese", "conclusão", "passo", "posterior"]
        hits = sum(1 for signal in signals if signal in joined or signal in conclusion.lower())
        return min(1.0, 0.3 + hits * 0.15)

    @staticmethod
    def _coverage(query: str, steps: Any, conclusion: str) -> float:
        q_words = {w for w in query.lower().split() if len(w) > 3}
        if not q_words:
            return 0.5
        body = (" ".join(str(s) for s in steps) + " " + conclusion).lower()
        covered = sum(1 for word in q_words if word in body)
        return min(1.0, max(0.1, covered / len(q_words)))

    @staticmethod
    def _speed_score(duration_s: float) -> float:
        # 0s→1.0; 1s→~0.5; 5s+→0.1
        if duration_s <= 0:
            return 1.0
        return max(0.1, min(1.0, 1.0 / (1.0 + duration_s)))


reasoning_evaluator = ReasoningEvaluator()
