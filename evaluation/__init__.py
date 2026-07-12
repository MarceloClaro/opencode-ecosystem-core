# -*- coding: utf-8 -*-
"""
evaluation — capacidades de avaliação honesta do ecossistema.

Exporta o Honest Evaluation Engine (SPEC-935-R142): a disciplina
antioverclaim como funções reutilizáveis. Cobertura ≠ qualidade;
nota de topo exige validação externa.
"""

from evaluation.honest_reviewer import (  # noqa: F401
    INTERNAL_QUALITY_CEILING,
    classify_claim,
    detect_inflation,
    honest_score_band,
    review,
)

__all__ = [
    "INTERNAL_QUALITY_CEILING",
    "classify_claim",
    "detect_inflation",
    "honest_score_band",
    "review",
]
