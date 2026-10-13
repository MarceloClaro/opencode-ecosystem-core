# -*- coding: utf-8 -*-
"""R830 — slashing_mechanism: penalidade proporcional fail-closed.

Inspirações: vouch-protocol/vouch (slash configurável), agentcred/agentcred
(faixas 5%/15%/30% por score), TrustMyGit (slash por deadline/disputa).
Corpus keywords: slashing, slash, penalty, slashing_rules, slash_.
Categoria: slashing_mechanism. Nunca remove além do travado.
"""
from __future__ import annotations

def slash(locked: float, amount: float, reason: str = "") -> dict:
    """Aplica slashing_rules: corta até o limite travado, retorna trilha."""
    locked = max(0.0, float(locked))
    amount = max(0.0, float(amount))
    slashed = min(locked, amount)  # slash_ fail-closed
    return {"slashed": slashed, "remaining": locked - slashed,
            "penalty": slashed, "reason": reason or "slashing_mechanism",
            "rules": "slashing_rules: proporcional, teto no travado"}

def slash_by_score(locked: float, score_0_100: float) -> dict:
    """Faixas inspiradas agentcred: 51-100→0%, 21-50→5%, 1-20→15%, 0→30%."""
    s = max(0.0, min(100.0, float(score_0_100)))
    if s >= 51:
        pct = 0.0
    elif s >= 21:
        pct = 0.05
    elif s >= 1:
        pct = 0.15
    else:
        pct = 0.30
    return slash(locked, locked * pct, reason=f"score {s}")
