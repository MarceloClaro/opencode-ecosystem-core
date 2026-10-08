"""Testes RED/GREEN da SPEC-935-R708 — Descoberta científica auditável.

Suíte hermética: dados sintéticos com sementes fixas (numpy RandomState),
sem rede/subprocesso/LLM; nenhum código do repositório é modificado.
"""
import numpy as np
import pandas as pd
import pytest

from research.discovery import design, analysis, validate, report


def _df_grupos(seed=7, n=40, desloc=1.2):
    rng = np.random.RandomState(seed)
    return pd.DataFrame({
        "escore": np.concatenate([rng.normal(50, 8, n), rng.normal(50 + desloc * 8, 8, n)]),
        "grupo": ["controle"] * n + ["intervencao"] * n,
    })


# ---------------------------------------------------------------- AC1: desenho
def test_hipotese_exige_falsificacao():
    with pytest.raises(ValueError):
        design.Hipotese(rotulo="H1", h0="Sem diferença.", h1="Há diferença.", falsificacao="  ")


def test_desenho_exige_pergunta_e_hipotese():
    h = design.Hipotese(rotulo="H1", h0="Sem diferença.", h1="Há diferença.",
                        falsificacao="p>=0,05 em SNAP-IV pré/pós.")
    with pytest.raises(ValueError):
        design.Desenho(pergunta=" ", populacao="crianças", intervencao_ou_exposicao="brincar",
                       comparador="rotina", desfecho="SNAP-IV", hipotese_list=[h])
    with pytest.raises(ValueError):
        design.Desenho(pergunta="P?", populacao="crianças", intervencao_ou_exposicao="brincar",
                       comparador="rotina", desfecho="SNAP-IV", hipotese_list=[])


def test_poder_monotonico_e_amostra_sensata():
    assert design.poder_t2(0.8, 30) > design.poder_t2(0.8, 10)
    assert design.poder_t2(0.2, 30) < design.poder_t2(0.8, 30)
    n = design.tamanho_amostra(0.8, poder_alvo=0.8)
    assert 20 <= n <= 40
    with pytest.raises(ValueError):
        design.poder_t2(-0.5, 30)


# ---------------------------------------------------------------- AC2: análise
def test_welch_detecta_grupos_separados():
    df = _df_grupos()
    r = analysis.welch_t(df, "escore", "grupo", "controle", "intervencao")
    assert r["p"] < 0.05 and r["cohen_d"] < -0.8
    for chave in ("n1", "n2", "t", "gl", "p", "ic95", "cohen_d", "magnitude_d"):
        assert chave in r


def test_welch_nao_detecta_grupos_identicos():
    rng = np.random.RandomState(11)
    base = rng.normal(50, 8, 40)
    df = pd.DataFrame({"escore": np.concatenate([base, base + rng.normal(0, 0.5, 40)]),
                       "grupo": ["a"] * 40 + ["b"] * 40})
    r = analysis.welch_t(df, "escore", "grupo", "a", "b")
    assert r["p"] > 0.05


def test_welch_falha_fechada():
    df = _df_grupos()
    with pytest.raises(ValueError):
        analysis.welch_t(df, "coluna_ausente", "grupo", "controle", "intervencao")
    with pytest.raises(ValueError):
        analysis.welch_t(df, "escore", "grupo", "controle", "grupo_fantasma")


def test_pearson_e_descritiva():
    rng = np.random.RandomState(5)
    x = rng.normal(0, 1, 60)
    df = pd.DataFrame({"x": x, "y": 2 * x + rng.normal(0, 0.3, 60)})
    r = analysis.pearson(df, "x", "y")
    assert r["r"] > 0.9 and r["p"] < 0.001 and r["ic95"][0] > 0.9
    d = analysis.descritiva(df, ["x"])
    assert d["descritiva"]["x"]["n"] == 60


# ---------------------------------------------------------------- AC3: validação
def test_holm_rejeita_o_esperado():
    r = validate.holm_bonferroni([0.001, 0.01, 0.3, 0.6])
    assert r["rejeitados"] == [True, True, False, False]
    assert r["n_rejeitados"] == 2
    with pytest.raises(ValueError):
        validate.holm_bonferroni([1.5])


def test_normalidade_descritiva():
    rng = np.random.RandomState(3)
    r = validate.checar_normalidade(pd.Series(rng.normal(0, 1, 100)))
    assert r["ok"] is True and r["p"] > 0.05
    with pytest.raises(ValueError):
        validate.checar_normalidade(pd.Series([1.0]))


# ---------------------------------------------------------------- AC4/AC5: relato
def test_secao_resultados_exige_limitacoes():
    with pytest.raises(ValueError):
        report.secao_resultados("T", [{"teste": "x"}], [])
    md = report.secao_resultados("T", [{"teste": "Welch", "p": 0.01}],
                                 ["Amostra de conveniência."])
    assert "[RESULTADO]" in md and "[OBRIGATÓRIO]" in md


def test_pacote_replicacao(tmp_path):
    dados = tmp_path / "dados.csv"
    dados.write_text("a,b\n1,2\n", encoding="utf-8")
    r = report.pacote_replicacao(str(tmp_path), metodos={"teste": "Welch"},
                                 resultados={"p": 0.01})
    assert r["ok"] is True and len(r["sha256_dados"]) == 64
    with pytest.raises(FileNotFoundError):
        report.pacote_replicacao(str(tmp_path), dados_nome="ausente.csv")
