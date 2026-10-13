# -*- coding: utf-8 -*-
"""R830 — behavioral_gate: pré-execução por trust comportamental.

Inspirações: TrustGate (sinal comportamental para roteamento/gating, decisão
no app), trust_engine BehavioralGate/GateDecision, vouch tiers.
Corpus keywords: behavioral_gate, behavioral gate, behavioral, BehavioralGate,
GateDecision. Categoria: behavioral_gate.
"""
from __future__ import annotations

TIERS = [(0.8, "platinum"), (0.6, "gold"), (0.4, "silver"), (0.1, "bronze"), (0.0, "unverified")]

def tier_of(trust: float) -> str:
    for th, name in TIERS:
        if trust >= th:
            return name
    return "unverified"

def allow(action_id: str, trust: float, threshold: float = 0.5) -> dict:
    """behavioral gate: só executa se trust >= threshold. Retorna GateDecision."""
    t = max(0.0, min(1.0, float(trust)))
    allowed = bool(t >= float(threshold))
    risk = "safe" if t >= 0.8 else "moderate" if t >= 0.5 else "risky" if t >= 0.3 else "blocked"
    return {"action_id": action_id, "allowed": allowed, "trust_score": t,
            "threshold": float(threshold), "tier": tier_of(t),
            "reason": "behavioral_gate R830", "risk_level": risk,
            "gate": "BehavioralGate", "decision": "GateDecision"}
