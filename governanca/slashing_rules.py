# -*- coding: utf-8 -*-
"""R832 — slashing_rules (governanca).
Keywords: slashing, slash, penalty, slashing_rules, slash_. Categoria: slashing_rules (governança)."""
from __future__ import annotations
def rules() -> dict:
    return {"tiers": {"51-100": "0%", "21-50": "5%", "1-20": "15%", "0": "30%"},
            "slashing_rules": True, "slash_": True, "penalty": "slashing"}
