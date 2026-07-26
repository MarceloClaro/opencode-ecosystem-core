# -*- coding: utf-8 -*-
"""
ScientificReasoningScanner — Auditoria e Aprimoramento do Raciocínio Científico
================================================================================
Avalia manuscritos, hipóteses e inferências com foco em:
  1. Falsificabilidade Popperiana
  2. Rigor Metodológico e Variáveis de Confusão
  3. Detecção de Falácias Epistemológicas (Causalidade vs Correlação, Viés de Confirmação)
  4. Cálculo do Índice de Rigor Científico (SRI 0-100)
"""

from __future__ import annotations

import re
from typing import Dict, List, Any


class ScientificReasoningScanner:
    """Scanner especializado para avaliação e fortalecimento do raciocínio científico."""

    FALSIFIABILITY_KEYWORDS = [
        "hipótese", "se", "então", "falsificável", "invalidação", "teste", "experimento", "métrica"
    ]
    METHODOLOGY_KEYWORDS = [
        "grupo de controle", "amostragem", "p-valor", "intervalo de confiança", "variável independente",
        "variável dependente", "baseline", "cego", "duplo-cego", "reprodutibilidade"
    ]
    FALLACY_TRIGGERS = [
        (r"\bprova que\b", "Afirmação categórica de prova absoluta sem margem de incerteza estatística"),
        (r"\bcorrelação implica\b", "Inclusão indevida de correlação como se fosse causalidade direta"),
        (r"\bsempre funciona\b", "Viés de generalização precipitada sem escopo restrito"),
        (r"\bobviamente\b", "Assunção não justificada sem citação empírica"),
    ]

    def scan_text(self, text: str) -> Dict[str, Any]:
        """Realiza a varredura completa do texto científico e calcula o SRI."""
        text_lower = text.lower()
        
        # 1. Avaliação de Falsificabilidade
        falsifiability_score = sum(1 for kw in self.FALSIFIABILITY_KEYWORDS if kw in text_lower)
        falsifiability_norm = round(min(1.0, falsifiability_score / 4.0) * 100, 2)

        # 2. Avaliação Metodológica
        methodology_score = sum(1 for kw in self.METHODOLOGY_KEYWORDS if kw in text_lower)
        methodology_norm = round(min(1.0, methodology_score / 4.0) * 100, 2)

        # 3. Detecção de Falácias
        detected_fallacies = []
        for pattern, desc in self.FALLACY_TRIGGERS:
            if re.search(pattern, text_lower):
                detected_fallacies.append({"pattern": pattern, "description": desc})

        fallacy_penalty = len(detected_fallacies) * 15.0

        # 4. Cálculo do Scientific Rigor Index (SRI)
        raw_sri = (falsifiability_norm * 0.4) + (methodology_norm * 0.6) - fallacy_penalty
        sri = round(max(0.0, min(100.0, raw_sri)), 2)

        # 5. Recomendações de Aprimoramento
        recommendations = []
        if falsifiability_norm < 50.0:
            recommendations.append("Especifique critérios claros de invalidação empírica (falsificabilidade popperiana).")
        if methodology_norm < 50.0:
            recommendations.append("Inclua detalhes explícitos sobre grupo de controle, amostragem e isolamento de variáveis.")
        if detected_fallacies:
            recommendations.append("Substitua afirmações categóricas ou causalidades precipitadas por justificativas estatísticas.")

        if not recommendations:
            recommendations.append("Raciocínio científico consistente e bem fundamentado.")

        return {
            "sri_score": sri,
            "falsifiability_score": falsifiability_norm,
            "methodology_score": methodology_norm,
            "detected_fallacies": detected_fallacies,
            "recommendations": recommendations,
            "status": "high_rigor" if sri >= 70.0 else ("moderate_rigor" if sri >= 40.0 else "low_rigor"),
        }

    def evaluate_hypothesis(self, hypothesis: str) -> Dict[str, Any]:
        """Avalia individualmente o rigor de uma hipótese científica."""
        scan = self.scan_text(hypothesis)
        has_condition = any(w in hypothesis.lower() for w in ["se", "caso", "quando", "dado que"])
        has_prediction = any(w in hypothesis.lower() for w in ["então", "resulta", "impacta", "aumenta", "reduz"])

        is_testable = has_condition or has_prediction
        return {
            "hypothesis": hypothesis,
            "is_testable": is_testable,
            "rigor_score": scan["sri_score"],
            "status": "valid_hypothesis" if is_testable and scan["sri_score"] >= 20.0 else "needs_refinement",
        }


scientific_reasoning_scanner = ScientificReasoningScanner()
