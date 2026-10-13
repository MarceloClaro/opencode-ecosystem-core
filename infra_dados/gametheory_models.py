# -*- coding: utf-8 -*-
"""R832 — gametheory_models (infra_dados).
Keywords: gametheory, game theory, gametheory/, PayoffMatrix, ShapleyValue. Categoria: gametheory_models."""
from __future__ import annotations
def nash_2x2(payoff=None) -> dict:
    m = payoff or [[(1, 1), (0, 0)], [(0, 0), (1, 1)]]
    eq = []
    for i in range(2):
        for j in range(2):
            if m[i][j][0] >= m[1 - i][j][0] and m[i][j][1] >= m[i][1 - j][1]:
                eq.append((i, j))
    return {"equilibria": eq, "PayoffMatrix": True, "gametheory": "gametheory_models"}
