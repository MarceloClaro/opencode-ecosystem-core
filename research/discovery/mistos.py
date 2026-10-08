# -*- coding: utf-8 -*-
"""Modelos mistos leves: ICC + erros-padrão robustos a cluster (SPEC-935-R710, AC5).

ICC por ANOVA de efeitos aleatórios (via única). EP cluster-robustos (CR0,
sanduíche) para coeficientes OLS. Fail-closed em grupo unitário ou posto
incompleto. Sem efeitos aleatórios em inclinação (fora de escopo, SPEC).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def icc(df: pd.DataFrame, coluna: str, grupo_col: str) -> dict:
    """Coeficiente de correlação intraclasse (ANOVA, efeitos aleatórios)."""
    if coluna not in df.columns or grupo_col not in df.columns:
        raise ValueError("Coluna de medida ou de grupo ausente.")
    dado = df[[coluna, grupo_col]].copy()
    dado[coluna] = pd.to_numeric(dado[coluna], errors="coerce")
    dado = dado.dropna()
    grupos = dado[grupo_col].unique()
    g = len(grupos)
    if g < 2:
        raise ValueError("ICC exige ao menos 2 grupos.")
    n_total = len(dado)
    tamanhos = dado.groupby(grupo_col)[coluna].count().to_numpy(float)
    if (tamanhos < 1).any():
        raise ValueError("Grupo vazio após limpeza.")
    media_geral = float(dado[coluna].mean())
    ssb = float(sum(n * (dado.loc[dado[grupo_col] == gr, coluna].mean() - media_geral) ** 2
                    for gr, n in zip(grupos, tamanhos)))
    ssw = float(sum(((dado.loc[dado[grupo_col] == gr, coluna]
                      - dado.loc[dado[grupo_col] == gr, coluna].mean()) ** 2).sum()
                    for gr in grupos))
    glb, glw = g - 1, n_total - g
    if glw <= 0:
        raise ValueError("Sem graus de liberdade intra-grupo.")
    msb, msw = ssb / glb, ssw / glw
    k0 = (n_total - float(np.sum(tamanhos ** 2)) / n_total) / glb
    if k0 <= 0:
        raise ValueError("k0 degenerado (grupos unitários demais).")
    valor = max(0.0, (msb - msw) / (msb + (k0 - 1) * msw)) if (msb + (k0 - 1) * msw) > 0 else 0.0
    return {"ok": True, "metodo": "ICC ANOVA efeitos aleatórios (via única)",
            "icc": float(valor), "grupos": int(g), "n": int(n_total),
            "k_medio": float(n_total / g),
            "leitura": ("alta similaridade intra-grupo: modelar hierarquia" if valor >= 0.1
                        else "baixa similaridade intra-grupo: OLS simples pode bastar")}


def ep_cluster_robusto(df: pd.DataFrame, y_col: str, x_cols: list[str],
                       grupo_col: str, com_intercepto: bool = True) -> dict:
    """EP sanduíche CR0 para OLS. Retorna betas, EPs e t por coeficiente."""
    for col in [y_col, grupo_col, *x_cols]:
        if col not in df.columns:
            raise ValueError(f"Coluna ausente: {col!r}.")
    base = df[[y_col, grupo_col, *x_cols]].copy()
    for col in [y_col, *x_cols]:
        base[col] = pd.to_numeric(base[col], errors="coerce")
    base = base.dropna()
    if base.empty:
        raise ValueError("Sem linhas válidas após limpeza.")
    y = base[y_col].to_numpy(float)
    X = base[x_cols].to_numpy(float)
    if com_intercepto:
        X = np.column_stack([np.ones(len(y)), X])
        nomes = ["intercepto", *x_cols]
    else:
        nomes = list(x_cols)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    grupos = base[grupo_col].unique()
    if len(grupos) < 2:
        raise ValueError("EP cluster-robusto exige ao menos 2 clusters.")
    carne = np.zeros((X.shape[1], X.shape[1]))
    for gr in grupos:
        m = (base[grupo_col].to_numpy() == gr)
        Xg, eg = X[m], resid[m]
        s = Xg.T @ eg
        carne += np.outer(s, s)
    vcov = XtX_inv @ carne @ XtX_inv
    eps = [float(np.sqrt(max(vcov[i, i], 0.0))) for i in range(len(nomes))]
    return {"ok": True, "metodo": "OLS + EP sanduíche CR0 por cluster",
            "n": int(len(y)), "clusters": int(len(grupos)),
            "coeficientes": [{"nome": nm, "beta": float(b), "ep_cluster": e,
                              "t": float(b / e) if e > 0 else None}
                             for nm, b, e in zip(nomes, beta, eps)]}
