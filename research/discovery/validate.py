# -*- coding: utf-8 -*-
"""Validação: múltiplas comparações, normalidade e suposições (SPEC-935-R708, AC3)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def holm_bonferroni(pvalores: list[float], alfa: float = 0.05) -> dict:
    """Correção de Holm (uniformemente mais potente que Bonferroni)."""
    if not pvalores:
        raise ValueError("Lista de p-valores vazia.")
    pv = [float(p) for p in pvalores]
    if any(not 0 <= p <= 1 for p in pv):
        raise ValueError("p-valores devem estar em [0,1].")
    m = len(pv)
    ordem = sorted(range(m), key=lambda i: pv[i])
    rejeitados = [False] * m
    for k, idx in enumerate(ordem, start=1):
        if pv[idx] <= alfa / (m - k + 1):
            rejeitados[idx] = True
        else:
            break
    return {"ok": True, "metodo": "Holm-Bonferroni", "alfa": alfa,
            "rejeitados": rejeitados,
            "p_ajustados": holm_ajustados(pv),
            "n_rejeitados": int(sum(rejeitados))}


def holm_ajustados(pvalores: list[float]) -> list[float]:
    """p-valores ajustados por Holm (monótonos, capados em 1)."""
    pv = [float(p) for p in pvalores]
    m = len(pv)
    ordem = sorted(range(m), key=lambda i: pv[i])
    adj = [0.0] * m
    teto = 0.0
    for k, idx in enumerate(ordem, start=1):
        teto = max(teto, min(1.0, pv[idx] * (m - k + 1)))
        adj[idx] = teto
    return adj


def checar_normalidade(serie: pd.Series) -> dict:
    """Shapiro (n<=5000) ou D'Agostino + assimetria/curtose. Descritivo, não decisório."""
    s = pd.to_numeric(serie, errors="coerce").dropna()
    n = len(s)
    if n < 3:
        raise ValueError("Normalidade exige n>=3.")
    if n <= 5000:
        est, p = stats.shapiro(s)
        metodo = "Shapiro-Wilk"
    else:
        est, p = stats.normaltest(s)
        metodo = "D'Agostino"
    return {"ok": True, "metodo": metodo, "n": int(n),
            "estatistica": float(est), "p": float(p),
            "assimetria": float(s.skew()), "curtose": float(s.kurtosis()),
            "leitura": ("sem desvio relevante da normalidade"
                        if p >= 0.05 else
                        "desvio da normalidade: preferir método robusto ou relatar com cautela")}


def relatar_suposicoes(df: pd.DataFrame, coluna: str, grupo_col: str = "") -> dict:
    """Relatório de suposições por grupo (n, normalidade)."""
    grupos = sorted(df[grupo_col].unique().tolist()) if grupo_col else ["geral"]
    blocos = {}
    for g in grupos:
        sub = df.loc[df[grupo_col] == g, coluna] if grupo_col else df[coluna]
        try:
            blocos[str(g)] = checar_normalidade(sub)
        except ValueError as exc:
            blocos[str(g)] = {"ok": False, "error": str(exc)}
    return {"ok": True, "coluna": coluna, "grupos": blocos}
