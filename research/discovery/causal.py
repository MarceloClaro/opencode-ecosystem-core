# -*- coding: utf-8 -*-
"""Inferência causal honesta: DID, IV-2SLS e RDD (SPEC-935-R710, AC1-AC3).

Fórmulas explícitas (numpy/scipy). Cada estimador declara suposições e
diagnósticos; nenhum declara causalidade sozinho. Limites na SPEC.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _col(df: pd.DataFrame, nome: str) -> pd.Series:
    if nome not in df.columns:
        raise ValueError(f"Coluna ausente: {nome!r}.")
    return df[nome]


def did(df: pd.DataFrame, y: str, tempo: str, tratado: str,
        pos: int | float | str = 1, tr: int | float | str = 1,
        n_perm: int = 199, seed: int = 7) -> dict:
    """Dupla diferença + p por permutação de rótulos de tratamento.

    Requer painel longo com 2 períodos. Tendências paralelas NÃO testáveis
    aqui — declarar como suposição (placebo exige 3+ períodos).
    """
    for col in (y, tempo, tratado):
        if col not in df.columns:
            raise ValueError(f"Coluna ausente: {col!r}.")
    yy = pd.to_numeric(df[y], errors="coerce")
    tp = df[tempo].to_numpy()
    trt = (df[tratado].to_numpy() == tr)
    post = (tp == pos)
    mask = yy.notna()
    yy, trt, post = yy[mask].to_numpy(float), trt[mask], post[mask]
    if post.sum() == 0 or (~post).sum() == 0:
        raise ValueError("DID exige dois períodos (pré e pós).")
    if trt.sum() == 0 or (~trt).sum() == 0:
        raise ValueError("DID exige grupo tratado e controle.")

    def _att(a, t, p):
        return (a[t & p].mean() - a[t & ~p].mean()) - (a[~t & p].mean() - a[~t & ~p].mean())

    att = float(_att(yy, trt, post))
    rng = np.random.RandomState(seed)
    cont = 0
    for _ in range(int(n_perm)):
        perm = rng.permutation(trt)
        if abs(_att(yy, perm, post)) >= abs(att):
            cont += 1
    p_perm = (cont + 1) / (int(n_perm) + 1)
    return {"ok": True, "metodo": "DID + permutação", "att": att,
            "p_permutacao": float(p_perm), "n_perm": int(n_perm),
            "n_tratado": int(trt.sum()), "n_controle": int((~trt).sum()),
            "suposicao": "tendências paralelas (não testável com 2 períodos)",
            "leitura": "efeito estimado sob suposição declarada; p por permutação"}


def iv_2sls(df: pd.DataFrame, y_col: str, x_col: str, z_col: str) -> dict:
    """2SLS manual: y ~ X (endógena) com instrumento Z. Sem controles extras."""
    y = pd.to_numeric(df[y_col], errors="coerce").to_numpy(float)
    x = pd.to_numeric(df[x_col], errors="coerce").to_numpy(float)
    z = pd.to_numeric(df[z_col], errors="coerce").to_numpy(float)
    okm = np.isfinite(y) & np.isfinite(x) & np.isfinite(z)
    y, x, z = y[okm], x[okm], z[okm]
    n = len(y)
    if n < 10:
        raise ValueError("2SLS exige n>=10.")
    Um = np.ones(n)
    # primeiro estágio: X ~ 1 + Z
    W = np.column_stack([Um, z])
    b1, res1, *_ = np.linalg.lstsq(W, x, rcond=None)
    xh = W @ b1
    r2_1 = 1 - float(np.sum((x - xh) ** 2) / np.sum((x - x.mean()) ** 2))
    t_z = float(b1[1] / (np.sqrt(float(np.sum((x - xh) ** 2) / (n - 2)) / np.sum((z - z.mean()) ** 2)) or np.nan))
    f1 = float(t_z ** 2)
    if not np.isfinite(f1):
        raise ValueError("Primeiro estágio degenerado (Z sem variação).")
    # segundo estágio: y ~ 1 + Xhat
    Xh = np.column_stack([Um, xh])
    b2, *_ = np.linalg.lstsq(Xh, y, rcond=None)
    resid = y - Xh @ b2
    s2 = float(np.sum(resid ** 2) / (n - 2))
    vcov = s2 * np.linalg.inv(Xh.T @ Xh)
    se = float(np.sqrt(vcov[1, 1]))
    t2 = float(b2[1] / se) if se > 0 else float("nan")
    # OLS para comparação
    X = np.column_stack([Um, x])
    bo, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {"ok": True, "metodo": "IV-2SLS manual (sem controles)",
            "n": int(n), "beta_iv": float(b2[1]), "se_iv": se, "t_iv": t2,
            "beta_ols": float(bo[1]), "primeiro_estagio": {"r2": r2_1, "F": f1},
            "instrumento_forte": bool(f1 >= 10),
            "alerta": ("F<10: instrumento fraco (Staiger-Stock, heurística) — "
                       "NÃO alegar causalidade." if f1 < 10 else
                       "F>=10: relevância mínima atendida; validade (exclusão) segue não testável"),
            "leitura": "causal apenas sob relevância + exclusão + monotonicidade"}


def rdd(df: pd.DataFrame, y_col: str, r_col: str, corte: float,
        banda: float | None = None) -> dict:
    """RDD linear local uniforme: tau = mu+ - mu- em banda h.

    Sem teste de densidade do running (limitação). Sensibilidade h/2, 2h +
    placebos em corte ± h.
    """
    y = pd.to_numeric(df[y_col], errors="coerce").to_numpy(float)
    r = pd.to_numeric(df[r_col], errors="coerce").to_numpy(float)
    okm = np.isfinite(y) & np.isfinite(r)
    y, r = y[okm], r[okm]
    if len(y) < 20:
        raise ValueError("RDD exige n>=20.")
    if banda is None:
        banda = float(np.std(r) * len(r) ** (-1 / 5)) or 1.0
    if banda <= 0:
        raise ValueError("banda deve ser positiva.")

    def _tau(h: float, c: float) -> dict | None:
        d = r - c
        for lado in (1, -1):
            m = (np.abs(d) <= h) & ((d >= 0) if lado > 0 else (d < 0))
            if m.sum() < 5:
                return None
        out = {}
        for lado, chave in ((1, "mu_mais"), (-1, "mu_menos")):
            m = (np.abs(d) <= h) & ((d >= 0) if lado > 0 else (d < 0))
            X = np.column_stack([np.ones(m.sum()), d[m]])
            b, *_ = np.linalg.lstsq(X, y[m], rcond=None)
            out[chave] = float(b[0])
            out[chave + "_n"] = int(m.sum())
        out["tau"] = out["mu_mais"] - out["mu_menos"]
        return out

    princ = _tau(float(banda), float(corte))
    if princ is None:
        raise ValueError("Banda sem observações suficientes de um dos lados.")
    return {"ok": True, "metodo": "RDD linear local (kernel uniforme)",
            "corte": float(corte), "banda": float(banda), **princ,
            "sensibilidade": {"banda_metade": _tau(float(banda) / 2, float(corte)),
                              "banda_dobro": _tau(float(banda) * 2, float(corte))},
            "placebos": {"corte_menos_h": _tau(float(banda), float(corte) - float(banda)),
                         "corte_mais_h": _tau(float(banda), float(corte) + float(banda))},
            "limitacao": "sem teste de densidade do running; placebos nulos fortalecem, não provam",
            "leitura": "efeito local no corte, sob continuidade dos potenciais"}
