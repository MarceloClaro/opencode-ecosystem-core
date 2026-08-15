"""Testes do ciclo R427 — diagnóstico de indicadores correlacionados com o IDEB (foco Crateús).

Valida: SPEC-935-R427-crateus-diagnostico.md, coleta SIDRA, análise com bootstrap,
ranking, perfil de Crateús, nota técnica e figuras.
"""
import json
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parent.parent
PAPER = RAIZ / "academic" / "papers" / "crateus_ideb"
PROC = PAPER / "data" / "processed"
OUT = PAPER / "outputs" / "expanded"
FIG = PAPER / "outputs" / "figuras_r427"
DOCS = PAPER / "docs"
SCRIPTS = PAPER / "scripts"

MUNICIPIOS_MICRO = [
    2301257, 2304103, 2305605, 2305654, 2308609,
    2309300, 2309409, 2311264, 2313203,
]
CRATEUS = 2304103

INDICADORES = [
    "taxa_alfabetizacao_15_pct", "agua_rede_geral_pct", "esgoto_rede_pct",
    "lixo_coletado_pct", "internet_domicilios_pct", "banheiro_exclusivo_pct",
    "renda_responsavel", "pib_per_capita",
]


# ---------- coleta SIDRA ----------

def test_coleta_indicadores_9_municipios():
    d = json.loads((PROC / "indicadores_sidra.json").read_text())
    assert len(d) == 9
    assert {int(x["cod_mun"]) for x in d} == set(MUNICIPIOS_MICRO)


def test_coleta_indicadores_sem_na():
    d = pd.DataFrame(json.loads((PROC / "indicadores_sidra.json").read_text()))
    cols = [c for c in d.columns if c != "cod_mun"]
    assert len(cols) >= 6
    assert not d[cols].isna().any().any()


def test_manifest_sidra():
    m = json.loads((PROC / "manifest_sidra.json").read_text())
    assert m["ciclo"] == "R427"
    assert len(m["coleta"]["tabelas"]) >= 6
    assert len(m["sha256_json"]) == 64


# ---------- análise ----------

def test_resultados_r427_estrutura():
    r = json.loads((OUT / "resultados_r427.json").read_text())
    for chave in ["ranking_pearson", "ranking_spearman", "ranking_agregado",
                  "perfil_crateus", "matriz_prioridade", "alavancas", "nao_alavancas"]:
        assert chave in r, chave


def test_ranking_agregado_8_indicadores():
    r = json.loads((OUT / "resultados_r427.json").read_text())
    assert len(r["ranking_agregado"]) == 8
    nomes = [x["indicador"] for x in r["ranking_agregado"]]
    assert set(nomes) == set(INDICADORES)


def test_saneamento_no_topo_do_ranking():
    r = json.loads((OUT / "resultados_r427.json").read_text())
    top3 = [x["indicador"] for x in r["ranking_agregado"][:3]]
    # banheiro, água e lixo devem estar entre os 3 primeiros por |r| médio
    assert "banheiro_exclusivo_pct" in top3
    assert "agua_rede_geral_pct" in top3


def test_renda_nao_alavanca():
    r = json.loads((OUT / "resultados_r427.json").read_text())
    nao = [x["indicador"] for x in r["nao_alavancas"]]
    assert "renda_responsavel" in nao
    assert "pib_per_capita" in nao


def test_bootstrap_valores_validos():
    r = json.loads((OUT / "resultados_r427.json").read_text())
    for k, v in r["correlacoes"].items():
        assert -1.0 <= v["pearson"] <= 1.0
        assert -1.0 <= v["spearman"] <= 1.0
        lo, hi = v["pearson_ic95"]
        assert lo <= v["pearson"] <= hi
        assert 0 <= v["sinal_estavel_pct"] <= 100


def test_perfil_crateus_completo():
    r = json.loads((OUT / "resultados_r427.json").read_text())
    perfil = r["perfil_crateus"]
    assert len(perfil) == 8
    # Crateús é líder em esgoto, internet, alfabetização, renda e PIB
    for ind in ["esgoto_rede_pct", "internet_domicilios_pct",
                "taxa_alfabetizacao_15_pct", "renda_responsavel", "pib_per_capita"]:
        assert perfil[ind]["melhor_micro"] == perfil[ind]["valor_crateus"], ind


def test_matriz_prioridade_agua_e_lixo():
    r = json.loads((OUT / "resultados_r427.json").read_text())
    prio = [p["indicador"] for p in r["matriz_prioridade"]]
    assert prio[0] == "agua_rede_geral_pct"
    assert "lixo_coletado_pct" in prio


def test_provenance_r427():
    p = json.loads((OUT / "provenance_r427.json").read_text())
    assert p["ciclo"] == "R427"
    assert p["bootstrap"]["seed"] == 42
    assert len(p["sha256_script"]) == 64


# ---------- figuras ----------

def test_figuras_r427_geradas():
    esperadas = ["heatmap_correlacoes.png",
                 "scatter_top1_banheiro_exclusivo_pct.png",
                 "scatter_top2_agua_rede_geral_pct.png",
                 "scatter_top3_lixo_coletado_pct.png"]
    for f in esperadas:
        assert (FIG / f).exists(), f


# ---------- nota técnica ----------

def test_nota_tecnica_existe():
    nt = DOCS / "NOTA_TECNICA_CRATEUS_INDICADORES.md"
    assert nt.exists()
    texto = nt.read_text(encoding="utf-8")
    assert "Crateús" in texto
    assert "R427" in texto


def test_nota_tecnica_anti_overclaim():
    nt = (DOCS / "NOTA_TECNICA_CRATEUS_INDICADORES.md").read_text(encoding="utf-8")
    for termo in ["prova", "provar que", "causa o", "efeito causal", "superhuman", "Qualis A1"]:
        assert termo.lower() not in nt.lower(), termo
    # usos legítimos: negativa explícita de causalidade
    assert "causalidade" in nt
    assert "≠ causalidade" in nt or "não é causalidade" in nt or "nunca\ncausalidade" in nt
    assert "n=9" in nt
    assert "IC95" in nt


def test_nota_tecnica_ranking_top_bottom():
    nt = (DOCS / "NOTA_TECNICA_CRATEUS_INDICADORES.md").read_text(encoding="utf-8")
    # mais correlacionados: saneamento; menos: renda/PIB
    assert "banheiro" in nt and "água" in nt
    assert "renda" in nt and "PIB" in nt


# ---------- scripts ----------

def test_scripts_r427_existem():
    assert (SCRIPTS / "baixar_indicadores.py").exists()
    assert (SCRIPTS / "analise_indicadores_crateus.py").exists()
