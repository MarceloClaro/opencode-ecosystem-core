# -*- coding: utf-8 -*-
"""Bayesiana conjugada Normal-Normal (SPEC-935-R710, AC4).

Modelo fechado, sem MCMC: dados y_i ~ Normal(θ, σ²) com σ conhecido
(ou estimado da amostra — declarado), prior θ ~ Normal(μ0, τ0²).
Prior sempre registrado; sensibilidade com 2 priors obrigatória.
Sem prior oculto, sem "prova" bayesiana.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _serie(df: pd.DataFrame, coluna: str) -> np.ndarray:
    if coluna not in df.columns:
        raise ValueError(f"Coluna ausente: {coluna!r}.")
    s = pd.to_numeric(df[coluna], errors="coerce").dropna().to_numpy(float)
    if len(s) < 2:
        raise ValueError(f"Coluna {coluna!r} com n insuficiente (<2 válidos).")
    return s


def posterior_normal(y: np.ndarray, mu0: float, tau0: float,
                     sigma: float | None = None) -> dict:
    """Posterior fechada. sigma=None usa dp amostral (declarado na saída)."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    if tau0 <= 0:
        raise ValueError("tau0 (dp do prior) deve ser positivo.")
    sig_usado, estimado = (float(sigma), False) if sigma and sigma > 0 else (float(np.std(y, ddof=1)), True)
    if not np.isfinite(sig_usado) or sig_usado <= 0:
        raise ValueError("sigma inválido ou degenerado.")
    prec_prior, prec_dados = 1.0 / tau0 ** 2, n / sig_usado ** 2
    var_post = 1.0 / (prec_prior + prec_dados)
    mu_post = var_post * (mu0 / tau0 ** 2 + n * float(np.mean(y)) / sig_usado ** 2)
    dp_post = float(np.sqrt(var_post))
    zc = float(stats.norm.ppf(0.975))
    return {"n": int(n), "media_amostral": float(np.mean(y)),
            "sigma_usado": sig_usado, "sigma_estimado": estimado,
            "mu_post": mu_post, "dp_post": dp_post,
            "icr95": [mu_post - zc * dp_post, mu_post + zc * dp_post],
            "p_theta_maior_0": float(1 - stats.norm.cdf((0 - mu_post) / dp_post))}


def atualizar(df: pd.DataFrame, coluna: str, mu0: float, tau0: float,
              sigma: float | None = None,
              prior_alternativo: tuple[float, float] | None = None) -> dict:
    """Atualização + sensibilidade a prior alternativo. Prior registrado."""
    y = _serie(df, coluna)
    princ = posterior_normal(y, float(mu0), float(tau0), sigma)
    princ.update({"prior": {"mu0": float(mu0), "tau0": float(tau0)},
                  "leitura": "crença atualizada sob modelo Normal-Normal; não prova efeito"})
    saida: dict = {"ok": True, "modelo": "Normal-Normal conjugado (sem MCMC)",
                   "principal": princ}
    if prior_alternativo is not None:
        saida["sensibilidade"] = posterior_normal(
            y, float(prior_alternativo[0]), float(prior_alternativo[1]), sigma)
        saida["sensibilidade"]["prior"] = {"mu0": float(prior_alternativo[0]),
                                           "tau0": float(prior_alternativo[1])}
    return saida
