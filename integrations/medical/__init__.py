# -*- coding: utf-8 -*-
"""
Módulo de Inteligência Médica e Decisão por Teoria dos Jogos
============================================================
Exportações canônicas do motor de suporte à decisão clínica baseada em evidências.
"""

from integrations.medical.evidence_grounding import (
    MedicalEvidence,
    ClinicalEvidenceLibrary,
    VERIFIED_MEDICAL_GUIDELINES,
)
from integrations.medical.clinical_game_theory import (
    DiagnosticHypothesis,
    DiagnosticTest,
    DiagnosticDecisionGraph,
    ShannonEntropyEngine,
    ClinicalGameTheoryEngine,
    ClinicalAnamnesisGenerator,
)
from integrations.medical.clinical_verifier import ClinicalSafetyVerifier
from integrations.medical.clinical_orchestrator_bridge import ClinicalInvestigationPipeline

__all__ = [
    "MedicalEvidence",
    "ClinicalEvidenceLibrary",
    "VERIFIED_MEDICAL_GUIDELINES",
    "DiagnosticHypothesis",
    "DiagnosticTest",
    "DiagnosticDecisionGraph",
    "ShannonEntropyEngine",
    "ClinicalGameTheoryEngine",
    "ClinicalAnamnesisGenerator",
    "ClinicalSafetyVerifier",
    "ClinicalInvestigationPipeline",
]
