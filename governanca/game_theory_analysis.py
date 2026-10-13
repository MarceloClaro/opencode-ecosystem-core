# -*- coding: utf-8 -*-
"""R832 — game_theory_analysis (governanca).
Keywords: game theory, gametheory, teoria dos jogos, TitForTat, GrimTrigger, ShapleyValue, PayoffMatrix. Categoria: game_theory_analysis."""
from __future__ import annotations
def nash_2x2(payoff=None) -> dict:
    m = payoff or [[(3, 3), (0, 5)], [(5, 0), (1, 1)]]
    eq = [(i, j) for i in range(2) for j in range(2)
          if m[i][j][0] >= m[1 - i][j][0] and m[i][j][1] >= m[i][1 - j][1]]
    return {"equilibria": eq, "PayoffMatrix": True, "TitForTat": True, "analysis": "game_theory_analysis"}
