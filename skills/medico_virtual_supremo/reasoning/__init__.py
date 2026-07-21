# -*- coding: utf-8 -*-
"""
Motor de Raciocínio Científico — Médico Virtual Supremo
===========================================================
Implementa raciocínio baseado em evidências (EBM), diagnóstico diferencial
bayesiano e análise terapêutica com NNT/NNH.
"""
from skills.medico_virtual_supremo.reasoning.evidence_based_reasoning import (
    EvidenceBasedReasoning,
    GradeClassification,
    PICOQuery,
    SOAPNote,
    ForcaRecomendacao,
)
from skills.medico_virtual_supremo.reasoning.diagnostic_reasoning import (
    DiagnosticReasoning,
    BayesianResult,
    LikelihoodRatio,
)
