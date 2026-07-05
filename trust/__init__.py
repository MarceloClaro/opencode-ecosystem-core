# -*- coding: utf-8 -*-
"""
Pacote trust — Trust Engine (SPEC-038 / SPEC-007-CORE)
======================================================
Segurança comportamental do ecossistema: TrustScorer, BehavioralGate,
NaturalForgetting (Atkinson-Shiffrin) e OutcomeTracker.

Portado do OpenCode_Ecosystem original (skills/system/academic-audit/trust_engine.py).
"""

from trust.trust_engine import (
    TrustEngine,
    TrustScorer,
    BehavioralGate,
    NaturalForgetting,
    OutcomeTracker,
    GateDecision,
    create_trust_engine,
)

__all__ = [
    "TrustEngine",
    "TrustScorer",
    "BehavioralGate",
    "NaturalForgetting",
    "OutcomeTracker",
    "GateDecision",
    "create_trust_engine",
]
