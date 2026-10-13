# -*- coding: utf-8 -*-
"""R830 — fee_market: mercado de taxas por prioridade.

Inspiração: economy/token_economy FeeQuote + FeeMarket, prstake slots.
Corpus keywords: fee market, fee_market, gas, tax, FeeMarket, FeeQuote.
Categoria: fee_market.
"""
from __future__ import annotations

BASE_FEE = 1.0
MULT = {"low": 0.5, "normal": 1.0, "high": 2.0, "critical": 4.0}

def quote(task_id: str, priority: str = "normal", congestion: float = 1.0) -> dict:
    """fee_market quote: base_fee * multiplicador * congestão (gas/tax)."""
    mult = MULT.get(priority, 1.0)
    total = BASE_FEE * mult * max(0.1, float(congestion))
    return {"task_id": task_id, "priority": priority, "base_fee": BASE_FEE,
            "congestion_multiplier": float(congestion), "total_fee": total,
            "market": "FeeMarket", "quote": "FeeQuote"}
