# -*- coding: utf-8 -*-
"""R828 — Trust Engine mínimo fail-closed.

Roteamento pondera trust; trust <0.3 exige supervisão.
Operação local, sem inferência externa.
"""

def route(candidates):
    """Roteia para maior trust; fail-closed com supervisão."""
    if not isinstance(candidates, list) or len(candidates) == 0:
        return {"selected": None, "requires_supervision": True, "reason": "sem_candidatos"}
    def _trust(c):
        try:
            t = float(c.get("trust", 0.0))
        except Exception:
            t = 0.0
        return t
    best = max(candidates, key=_trust)
    t = _trust(best)
    return {
        "selected": best,
        "trust": t,
        "requires_supervision": bool(t < 0.3),
        "reason": "r828_ok" if t >= 0.3 else "trust_baixo_exige_supervisao",
    }
