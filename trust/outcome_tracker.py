# -*- coding: utf-8 -*-
"""R830 — outcome_tracker: registro de outcomes com decaimento.

Inspirações: vouch ReputationEngine (base 50, +1/-2, decay 10%/dia após 7d),
TrustEngine OutcomeTracker/TrackedOutcome, trust score.
Corpus keywords: outcome_tracker, outcome tracker, trust score, OutcomeTracker,
TrackedOutcome. Categoria: outcome_tracker.
"""
from __future__ import annotations
import time
from typing import List, Dict

class OutcomeTracker:
    """outcome_tracker com decaimento temporal toward baseline."""

    def __init__(self, base: float = 0.5, decay_per_day: float = 0.1):
        self.base = base
        self.decay = decay_per_day
        self._outcomes: List[bool] = []
        self._last = time.time()

    def record(self, success: bool) -> None:
        self._outcomes.append(bool(success))
        self._last = time.time()

    def score(self) -> float:
        if not self._outcomes:
            return self.base
        raw = sum(1.0 for o in self._outcomes if o) / len(self._outcomes)
        days = max(0.0, (time.time() - self._last) / 86400.0)
        factor = pow(1.0 - self.decay, days)
        return self.base + (raw - self.base) * factor  # trust score TrackedOutcome

    def stats(self) -> Dict:
        tot = len(self._outcomes)
        ok = sum(1 for o in self._outcomes if o)
        return {"total": tot, "success": ok, "success_rate": (ok / tot) if tot else 0.0,
                "tracker": "OutcomeTracker", "outcome": "TrackedOutcome"}
