# -*- coding: utf-8 -*-
"""Scanner heurístico de temas bohmianos (totalidade, diálogo, fragmentação).

Não avalia verdade, mérito científico ou interpretação correta. Conta marcadores
lexicais e devolve faixas para revisão humana.
"""
from __future__ import annotations

import re
from typing import Any

DIMENSOES = {
    "totalidade": (
        "totalidade", "todo", "inteiro", "interdepend", "relação", "relacao",
        "wholeness", "whole", "não separável", "nao separavel",
    ),
    "dialogo": (
        "diálogo", "dialogo", "suspensão", "suspensao", "suposição", "suposicao",
        "escuta", "dialogo de bohm", "bohm dialogue", "assumption",
    ),
    "fragmentacao": (
        "fragmentação", "fragmentacao", "separação", "separacao", "reducionismo",
        "especialização", "especializacao", "fragmentation", "reductionism",
    ),
    "ordem_implicada": (
        "ordem implicada", "ordem explicada", "holomovimento", "dobramento",
        "implicate order", "explicate order", "holomovement", "enfold",
    ),
    "limites": (
        "limite", "metáfora", "metafora", "interpretação", "interpretacao",
        "não é", "nao e", "não prova", "nao prova", "hipótese", "hipotese",
    ),
}


class BohmScanner:
    """Triagem lexical, sem inferência sobre a qualidade da obra."""

    def scan_text(self, text: str) -> dict[str, Any]:
        texto = (text or "").lower()
        contagens: dict[str, int] = {}
        achados: list[dict[str, Any]] = []
        for dimensao, termos in DIMENSOES.items():
            total = 0
            encontrados = []
            for termo in termos:
                n = len(re.findall(re.escape(termo), texto))
                if n:
                    total += n
                    encontrados.append({"termo": termo, "ocorrencias": n})
            contagens[dimensao] = total
            if encontrados:
                achados.append({"dimensao": dimensao, "termos": encontrados[:8]})
        # Score apenas de presença lexical; não é nota de qualidade.
        cobertura = sum(1 for v in contagens.values() if v > 0) / len(DIMENSOES)
        densidade = min(1.0, sum(contagens.values()) / max(1, len(texto.split())) * 50)
        score = round(100 * (0.6 * cobertura + 0.4 * densidade), 1)
        return {
            "score": score,
            "score_kind": "lexical_heuristic",
            "scientific_quality_assessed": False,
            "dimensoes": contagens,
            "findings": achados,
            "status": "review_context" if score >= 40 else "insufficient_markers",
            "limitations": [
                "Contagem lexical não mede verdade, mérito ou interpretação correta.",
                "Ausência de termos não significa ausência do tema.",
                "Presença de termos não significa que a obra aplica Bohm corretamente.",
            ],
        }


bohm_scanner = BohmScanner()
