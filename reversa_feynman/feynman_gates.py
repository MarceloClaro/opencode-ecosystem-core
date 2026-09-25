# -*- coding: utf-8 -*-
"""FeynmanGates — FEG-01..07 (SPEC-935-R504).

FEG-01: o mecanismo pode ser explicado sem depender apenas do nome?
FEG-02: a afirmação forte possui evidência/proveniência?
FEG-03: observação e inferência estão separadas?
FEG-04: existe teste/oracle capaz de refutar?
FEG-05: a solução resolve necessidade demonstrada ou é cargo cult?
FEG-06: qual menor experimento reduz a incerteza?
FEG-07: a fonte humana explica mecanismo e transfere para cenário variante?

Score base FEG-01..06: 0..12 (2 pontos por gate). FEG-07 (Teach-back) é
somente humano e fica FORA do score base.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class TeachbackResult:
    status: str  # HUMAN-VALIDATED | HUMAN-PARTIAL | HUMAN-CONFLICT
    note: str = ""


class FeynmanGates:
    def score(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia FEG-01..06. Claim sem evidência → score 0 (anti-cargo-cult)."""
        evidence = claim.get("evidence") or []
        if not evidence:
            return {
                "feg_01_06_score": 0,
                "feg": {"FEG-01": 0, "FEG-02": 0, "FEG-03": 0,
                        "FEG-04": 0, "FEG-05": 0, "FEG-06": 0},
                "reason": "sem evidencia/proveniencia",
            }

        feg = {
            "FEG-01": 2 if (claim.get("mechanism") or "").strip() else 0,
            "FEG-02": 2 if (claim.get("evidence") or []) else 0,
            "FEG-03": 2 if claim.get("observed_inferred_separated") else 0,
            "FEG-04": 2 if (claim.get("test_oracle") or "").strip() else 0,
            "FEG-05": 2 if claim.get("need_demonstrated") else 0,
            "FEG-06": 2 if (claim.get("min_experiment") or "").strip() else 0,
        }
        return {
            "feg_01_06_score": sum(feg.values()),
            "feg": feg,
            "reason": None,
        }

    def teachback(self, human_text: str, transfer: str) -> TeachbackResult:
        """FEG-07 — somente humano. Não entra no score automático."""
        if not (human_text or "").strip():
            return TeachbackResult(status="HUMAN-CONFLICT",
                                   note="sem explicação humana registrada")
        if not (transfer or "").strip():
            return TeachbackResult(status="HUMAN-PARTIAL",
                                   note="explica mecanismo mas sem transferência variante")
        return TeachbackResult(status="HUMAN-VALIDATED",
                               note="mecanismo explicado e transferido a variante")