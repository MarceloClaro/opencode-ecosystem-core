# -*- coding: utf-8 -*-
"""ReversaFeynman Bridge — Evidence & Calibration Layer (SPEC-935-R504).

Port Python dos contratos do ReversaFeynman (linha independente derivada do
Reversa original — Macedo & Costa, arXiv:2605.18684):
  - EvidenceGuard (OBSERVED/INFERRED/UNVERIFIED/BLOCKED);
  - FeynmanGates (FEG-01..07, Teach-back humano);
  - OfflinePolicyEvaluator v3 (decide/observe, holdout, Brier/ECE, drift,
    IC95 bootstrap, readiness sem auto-ativação);
  - AuditLedger (hash-chain SHA-256);
  - CalibratedRoutingAdvisor (recomendações shadow para o roteador R500).
"""

from reversa_feynman.evidence_guard import (
    EvidenceGuard, EPISTEMIC_STATES, OBSERVED, INFERRED, UNVERIFIED, BLOCKED,
)
from reversa_feynman.feynman_gates import FeynmanGates, TeachbackResult
from reversa_feynman.offline_eval import (
    OfflinePolicyEvaluator, DecisionRecord, DriftDetector, PromotionReadiness,
)
from reversa_feynman.ledger import AuditLedger
from reversa_feynman.router_calibration import CalibratedRoutingAdvisor

__all__ = [
    "EvidenceGuard", "EPISTEMIC_STATES", "OBSERVED", "INFERRED", "UNVERIFIED",
    "BLOCKED", "FeynmanGates", "TeachbackResult", "OfflinePolicyEvaluator",
    "DecisionRecord", "DriftDetector", "PromotionReadiness", "AuditLedger",
    "CalibratedRoutingAdvisor",
]