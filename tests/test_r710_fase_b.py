"""Testes RED/GREEN da SPEC-935-R710 — Fase B (DID/IV/RDD, Bayes, mistos).

Suíte hermética: dados sintéticos com sementes fixas (RandomState), sem
rede/subprocesso/LLM; nenhum código do repositório é modificado.
"""
import numpy as np
import pandas as pd
import pytest

from research.discovery import causal, bayes, mistos


def _did_df(seed=21, efeito=5.0, n=60):
    rng = np.random.RandomState(seed)
    base = rng.normal(50, 6, n)
    tratado = np.array([0] * n + [1] * n)
    tempo = np.array([0] * (n // 2) + [1] * (n // 2) + [0] * (n // 2) + [1] * (n // 2))
    y = np.concatenate([base, base]) + tratado * tempo * efeito + rng.normal(0, 1, 2 * n)
    return pd.DataFrame({"y": y, "tempo": tempo, "tratado": tratado})


# ---------------------------------------------------------------- AC1: DID
def test_did_recupera_efeito():
    df = _did_df()
    r = causal.did(df, "y", "tempo", "tratado", n_perm=199, seed=7)
    assert r["ok"] is True
    assert abs(r["att"] - 5.0) < 1.0
    assert r["p_permutacao"] < 0.05


def test_did_nulo_centrado_em_zero():
    df = _did_df(efeito=0.0)
    r = causal.did(df, "y", "tempo", "tratado", n_perm=199, seed=7)
    assert abs(r["att"]) < 1.5
    assert r["p_permutacao"] > 0.05


def test_did_falha_fechada():
    df = _did_df()
    with pytest.raises(ValueError):
        causal.did(df, "coluna_ausente", "tempo", "tratado")
    with pytest.raises(ValueError):
        causal.did(df, "y", "tempo", "tratado", pos=99)


# ---------------------------------------------------------------- AC2: IV
def _iv_df(seed=33, forca=1.0, n=400):
    rng = np.random.RandomState(seed)
    z = rng.normal(0, 1, n)
    u = rng.normal(0, 1, n)
    x = forca * z + 0.8 * u + rng.normal(0, 0.5, n)
    y = 2.0 * x + u
    return pd.DataFrame({"y": y, "x": x, "z": z})


def test_iv_valido_recupera_e_acusa_forte():
    df = _iv_df()
    r = causal.iv_2sls(df, "y", "x", "z")
    assert r["ok"] is True
    assert abs(r["beta_iv"] - 2.0) < 0.3
    assert r["instrumento_forte"] is True
    assert r["primeiro_estagio"]["F"] >= 10


def test_iv_fraco_acusa_f_menor_10():
    df = _iv_df(forca=0.05)
    r = causal.iv_2sls(df, "y", "x", "z")
    assert r["instrumento_forte"] is False
    assert "NÃO alegar" in r["alerta"]
    with pytest.raises(ValueError):
        causal.iv_2sls(df.head(5), "y", "x", "z")


# ---------------------------------------------------------------- AC3: RDD
def _rdd_df(seed=44, salto=4.0, n=600):
    rng = np.random.RandomState(seed)
    r = rng.uniform(-3, 3, n)
    y = 1.5 * r + (r >= 0) * salto + rng.normal(0, 1, n)
    return pd.DataFrame({"y": y, "r": r})


def test_rdd_recupera_salto():
    df = _rdd_df()
    r = causal.rdd(df, "y", "r", corte=0.0, banda=1.0)
    assert r["ok"] is True
    assert abs(r["tau"] - 4.0) < 0.8
    assert r["sensibilidade"]["banda_metade"] is not None
    with pytest.raises(ValueError):
        causal.rdd(df.head(10), "y", "r", corte=0.0)


# ---------------------------------------------------------------- AC4: Bayes
def test_bayes_entre_prior_e_dados():
    rng = np.random.RandomState(55)
    df = pd.DataFrame({"y": rng.normal(2.0, 1.0, 50)})
    r = bayes.atualizar(df, "y", mu0=0.0, tau0=1.0, sigma=1.0,
                        prior_alternativo=(0.0, 10.0))
    assert r["ok"] is True
    assert 0.0 < r["principal"]["mu_post"] < 2.0
    assert r["principal"]["p_theta_maior_0"] > 0.9
    assert "sensibilidade" in r
    with pytest.raises(ValueError):
        bayes.atualizar(df, "coluna_ausente", mu0=0.0, tau0=1.0)


# ---------------------------------------------------------------- AC5: mistos
def _cluster_df(seed=66, rho_alta=True, g=20, k=10):
    rng = np.random.RandomState(seed)
    ys, gs = [], []
    for j in range(g):
        efeito = rng.normal(0, 3.0 if rho_alta else 0.2)
        for _ in range(k):
            ys.append(50 + efeito + rng.normal(0, 1.0))
            gs.append(f"g{j}")
    return pd.DataFrame({"y": ys, "grupo": gs, "x": rng.normal(0, 1, g * k)})


def test_icc_alto_em_clusters_coesos():
    r = mistos.icc(_cluster_df(rho_alta=True), "y", "grupo")
    assert r["ok"] is True and r["icc"] > 0.5
    r2 = mistos.icc(_cluster_df(rho_alta=False), "y", "grupo")
    assert r2["icc"] < r["icc"]
    with pytest.raises(ValueError):
        mistos.icc(_cluster_df().head(3), "y", "grupo")


def test_ep_cluster_robusto():
    df = _cluster_df()
    r = mistos.ep_cluster_robusto(df, "y", ["x"], "grupo")
    assert r["ok"] is True and r["clusters"] == 20
    assert all(c["ep_cluster"] > 0 for c in r["coeficientes"])
    with pytest.raises(ValueError):
        mistos.ep_cluster_robusto(df, "y", ["x"], "grupo_ausente")
