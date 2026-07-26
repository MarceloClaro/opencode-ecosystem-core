# -*- coding: utf-8 -*-
"""
Vectorized Goal Drift Detector — Aceleração Vetorial de Similaridade de Objetivos
===================================================================================
Calcula a similaridade vetorial entre o objetivo da tarefa e o contexto da ação
em tempo constante utilizando n-gramas e produto interno vetorizado.
"""

from __future__ import annotations

import re
import math
from collections import Counter
from typing import Dict, Any, List, Set


class VectorizedGoalDriftDetector:
    """Detector vetorial acelerado de deriva de objetivo."""

    @staticmethod
    def _extract_ngram_vector(text: str, n: int = 3) -> Dict[str, float]:
        """Extrai n-gramas de caracteres e retorna vetor normalizado L2."""
        text = re.sub(r"\s+", " ", text.lower().strip())
        if not text:
            return {}

        ngrams = [text[i:i + n] for i in range(len(text) - n + 1)] if len(text) >= n else [text]
        counts = Counter(ngrams)
        norm = math.sqrt(sum(v * v for v in counts.values()))
        if norm == 0:
            return {}
        return {k: v / norm for k, v in counts.items()}

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula a similaridade de cosseno vetorizada entre dois textos."""
        vec1 = self._extract_ngram_vector(text1)
        vec2 = self._extract_ngram_vector(text2)
        if not vec1 or not vec2:
            return 0.0

        # Dot product dos vetores normalizados L2 = Cosseno
        common_keys = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        return round(min(1.0, max(0.0, dot_product)), 4)

    def check_drift(self, goal: str, context: str, threshold: float = 0.15) -> Dict[str, Any]:
        """Verifica se o contexto da ação derivou do objetivo especificado."""
        similarity = self.calculate_similarity(goal, context)
        drifted = similarity < threshold
        return {
            "goal": goal,
            "context": context,
            "similarity": similarity,
            "threshold": threshold,
            "drifted": drifted,
            "status": "drift_detected" if drifted else "ok",
        }


vectorized_drift_detector = VectorizedGoalDriftDetector()
