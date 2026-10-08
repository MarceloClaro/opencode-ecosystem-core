# -*- coding: utf-8 -*-
"""Análise inferencial e descritiva sobre DataFrame (SPEC-935-R708, AC2).

Toda saída traz n, estatística, p, IC e tamanho de efeito — nunca só p.
Interpretação em linguagem calibrada; conclusão causal é proibida aqui.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _coluna(df: pd.DataFrame, nome: str) -> pd.Series:
    if nome not in df.columns:
        raise ValueError(f"Coluna ausente: {nome!r}.")
    serie = pd.to_numeric(df[nome], errors="coerce").dropna()
    if len(serie) < 2:
        raise ValueError(f"Coluna {nome!r} com n insuficiente (<2 válidos).")
    return serie


def descritiva(df: pd.DataFrame, colunas: list[str]) -> dict:
    """Média, dp, mediana, Q1, Q3, min, max, n por coluna."""
    saida = {}
    for col in colunas:
        s = _coluna(df, col)
        saida[col] = {"n": int(len(s)), "media": float(s.mean()),
                      "dp": float(s.std(ddof=1)) if len(s) > 1 else 0.0,
                      "mediana": float(s.median()),
                      "q1": float(s.quantile(0.25)), "q3": float(s.quantile(0.75)),
                      "min": float(s.min()), "max": float(s.max())}
    return {"ok": True, "descritiva": saida}


def cohen_d(a: pd.Series, b: pd.Series) -> float:
    """d de Cohen com dp combinada (amostras independentes)."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        raise ValueError("Cohen d exige n>=2 por grupo.")
    var = ((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2)
    if var <= 0:
        raise ValueError("Variância combinada nula: d indefinido.")
    return float((a.mean() - b.mean()) / np.sqrt(var))


def _rotulo_d(d: float) -> str:
    a = abs(d)
    if a < 0.2:
        return "desprezível"
    if a < 0.5:
        return "pequeno"
    if a < 0.8:
        return "médio"
    return "grande"


def welch_t(df: pd.DataFrame, coluna: str, grupo_col: str,
            g1: str, g2: str, alfa: float = 0.05) -> dict:
    """t de Welch entre dois grupos + d de Cohen + IC da diferença."""
    if grupo_col not in df.columns:
        raise ValueError(f"Coluna de grupo ausente: {grupo_col!r}.")
    a = _coluna(df.loc[df[grupo_col] == g1], coluna)
    b = _coluna(df.loc[df[grupo_col] == g2], coluna)
    if len(a) < 2 or len(b) < 2:
        raise ValueError("Welch exige n>=2 por grupo.")
    t, p = stats.ttest_ind(a, b, equal_var=False)
    d = cohen_d(a, b)
    dif = float(a.mean() - b.mean())
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    na, nb = len(a), len(b)
    ep = float(np.sqrt(va / na + vb / nb))
    gl = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    margem = float(stats.t.ppf(1 - alfa / 2, gl) * ep)
    return {"ok": True, "teste": "Welch t bicaudal", "n1": int(len(a)), "n2": int(len(b)),
            "t": float(t), "gl": float(gl), "p": float(p), "alfa": alfa,
            "diferenca_medias": dif, "ic95": [dif - margem, dif + margem],
            "cohen_d": d, "magnitude_d": _rotulo_d(d),
            "leitura": ("diferença estatisticamente significativa no nível alfa"
                        if p < alfa else
                        "sem evidência de diferença no nível alfa")}


def pearson(df: pd.DataFrame, x: str, y: str, alfa: float = 0.05) -> dict:
    """Correlação de Pearson + IC via Fisher z."""
    sx, sy = _coluna(df, x), _coluna(df, y)
    idx = sx.index.intersection(sy.index)
    if len(idx) < 3:
        raise ValueError("Pearson exige n>=3 pares válidos.")
    r, p = stats.pearsonr(sx.loc[idx], sy.loc[idx])
    z = float(np.arctanh(np.clip(r, -0.999999, 0.999999)))
    ep = 1.0 / np.sqrt(len(idx) - 3)
    zc = stats.norm.ppf(1 - alfa / 2)
    return {"ok": True, "teste": "Pearson", "n": int(len(idx)), "r": float(r),
            "p": float(p), "alfa": alfa,
            "ic95": [float(np.tanh(z - zc * ep)), float(np.tanh(z + zc * ep))],
            "leitura": "associação linear — correlação não implica causação"}
