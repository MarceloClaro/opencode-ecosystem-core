# -*- coding: utf-8 -*-
"""Descoberta científica auditável: dados → inferência → manuscrito.

SPEC-935-R708. Elo quantitativo do Core: desenho (PICO, hipóteses,
poder), análise (descritiva, Welch, Pearson, Cohen, IC), validação
(Holm, normalidade, suposições) e relato calibrado + pacote de replicação.

Estatística corrobora, não prova. Nenhuma função deste pacote declara
causalidade, eficácia ou cura.
"""
from research.discovery import design, analysis, validate, report
from research.discovery import causal, bayes, mistos

__all__ = ["design", "analysis", "validate", "report",
           "causal", "bayes", "mistos"]
