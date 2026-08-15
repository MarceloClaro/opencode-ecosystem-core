"""Testes do ciclo R426 — estudo Crateús-IDEB (Sertão de Cratéus).

Valida: SPEC-935-R426-crateus-ideb.md, dados/scripts/resultados/mapas/figuras/manuscrito.
"""
import json
import hashlib
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parent.parent
PAPER = RAIZ / "academic" / "papers" / "crateus_ideb"
PROC = PAPER / "data" / "processed"
OUT = PAPER / "outputs" / "expanded"
MAPAS = PAPER / "outputs" / "mapas"
FIGURAS = PAPER / "outputs" / "figuras"
SCRIPTS = PAPER / "scripts"
DOCS = PAPER / "docs"

MUNICIPIOS_MICRO = [
    2301257, 2304103, 2305605, 2305654, 2308609,
    2309300, 2309409, 2311264, 2313203,
]


# ---------- dados ----------

def test_dados_processados_existem():
    for nome in ["ideb_br.json", "ideb_ce.json", "pib_br.json", "pib_ce.json",
                 "renda_br.json", "renda_ce.json", "ideb_microrregiao.json"]:
        assert (PROC / nome).exists(), nome


def test_ideb_etapas_separadas():
    ideb = pd.read_json(PROC / "ideb_br.json", orient="records")
    etapas = set(ideb["etapa"].unique())
    assert {"anos_iniciais", "anos_finais"} <= etapas


def test_ideb_contem_metas():
    ideb = pd.read_json(PROC / "ideb_ce.json", orient="records")
    assert "proj_2021" in ideb.columns


def test_renda_convertida_numero():
    renda = pd.read_json(PROC / "renda_ce.json", orient="records")
    crateus = renda[renda["cod_mun"] == 2304103]
    assert not crateus.empty
    assert pd.api.types.is_float_dtype(renda["renda_media_resp"])
    assert crateus["renda_media_resp"].iloc[0] > 1000


def test_microrregiao_nove_municipios():
    renda = pd.read_json(PROC / "renda_microrregiao.json", orient="records")
    assert set(renda["cod_mun"].astype(int)) == set(MUNICIPIOS_MICRO)


def test_manifest_fontes():
    m = json.loads((PAPER / "data" / "raw" / "SOURCE_MANIFEST.json").read_text())
    assert len(m["fontes"]) >= 4
    for f in m["fontes"]:
        assert f["url"].startswith("http")
        assert len(f["sha256"]) == 64


# ---------- resultados ----------

def test_resultados_gerados():
    r = json.loads((OUT / "resultados_r426.json").read_text())
    for chave in ["microrregiao", "ceara", "brasil", "loocv_microrregiao",
                  "mdes_tost_micro", "h3_estagnacao"]:
        assert chave in r


def test_h1_niveis_positivo_micro():
    r = json.loads((OUT / "resultados_r426.json").read_text())
    n = r["microrregiao"]["niveis"]
    assert n["r"] >= 0.3
    assert n["ic95_inf"] > 0
    assert n["n_clusters"] == 9


def test_h2_dentro_nula_micro():
    r = json.loads((OUT / "resultados_r426.json").read_text())
    fe = r["microrregiao"]["fe"]
    # SE clusterizado presente e IC95% cluster contém zero (não-detecção)
    assert "se_cluster" in fe and "ic95_cluster_inf" in fe
    assert fe["ic95_cluster_inf"] < 0 < fe["ic95_cluster_sup"]
    assert fe["n_clusters"] == 9
    d1 = r["microrregiao"]["primeiras_diferencas"]
    assert abs(d1["r"]) < 0.2


def test_loocv_9_folds_positivos():
    r = json.loads((OUT / "resultados_r426.json").read_text())
    lo = r["loocv_microrregiao"]
    assert lo["n_folds"] == 9
    assert lo["pct_positivos"] == 100.0


def test_mdes_e_tost_declarados():
    r = json.loads((OUT / "resultados_r426.json").read_text())
    m = r["mdes_tost_micro"]
    assert m["mdes"] > 1
    assert m["p_tost"] > 0.05  # não-equivalência/não-detecção
    assert "não-detecção" in m["leitura"]


def test_h3_metas_atingidas_micro():
    r = json.loads((OUT / "resultados_r426.json").read_text())
    detalhe = [d for d in r["h3_estagnacao"]["detalhe"]
               if d["cod_mun"] in MUNICIPIOS_MICRO and d["etapa"] == "anos_iniciais"]
    assert len(detalhe) == 9
    assert all(d["atingiu_meta"] for d in detalhe)


def test_provenance_r426():
    p = json.loads((OUT / "provenance_r426.json").read_text())
    assert p["ciclo"] == "R426"
    assert "sha256_scripts" in p
    assert (SCRIPTS / "analise_crateus.py").read_bytes()


# ---------- mapas ----------

def test_mapas_gerados():
    assert (MAPAS / "mapa_renda_responsavel_censo2022.png").exists()
    assert (MAPAS / "mapa_pib_per_capita_2021.png").exists()
    assert (MAPAS / "mapas_manifest.json").exists()


# ---------- manuscrito ----------

def test_manuscrito_anti_overclaim():
    texto = (DOCS / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    for termo in ["provar que", "efeito causal", "causa o", "superhuman", "Qualis A1"]:
        assert termo.lower() not in texto.lower(), termo
    # usos legítimos de "prova" só no sentido de não-detecção
    assert "não uma prova de ausência" in texto
    assert "não-detecção" in texto
    assert "evidência associativa" in texto or "associativa" in texto


def test_manuscrito_dois_resumos_e_autor():
    texto = (DOCS / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    assert "## Resumo" in texto and "## Abstract" in texto
    assert "Marcelo Claro Laranjeira" in texto
    assert "https://orcid.org/0000-0001-8996-2887" in texto


def test_manuscrito_referencias_com_doi():
    texto = (DOCS / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    # todas as referências DOI listadas devem estar no texto
    dofs = ["10.1590/S0101-73302012000200008", "10.1590/S0100-15742012000300010",
            "10.1016/j.econedurev.2021.102219", "10.1086/693981",
            "10.1186/s40536-026-00302-0", "10.3102/0162373715571437",
            "10.21723/riaee.v17iesp.3.16719", "10.1590/S2176-66812013000200002",
            "10.7551/mitpress/9780262029179.001.0001",
            "10.1590/S1413-24782019240002", "10.21814/rpe.4295",
            "10.18222/eae.v35.10549", "10.1590/S0101-73302013000300013"]
    for doi in dofs:
        assert doi in texto, doi


# ---------- pesquisa original (sem estudo anterior; RQ explícita) ----------

def test_manuscrito_sem_referencia_estudo_anterior():
    texto = (DOCS / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    for termo in ["estudo anterior", "espelho", "espelhando", "espelhado",
                  "padrão nacional", "padrão associativo nacional", "reproduz o padrão"]:
        assert termo.lower() not in texto.lower(), termo
    # "padrão associativo" pode aparecer como conceito (sem nacional/anterior); verificar que
    # nenhuma menção remete a estudo prévio
    assert "estudo anterior" not in texto.lower()
    assert "ARM" not in texto


def test_manuscrito_pergunta_de_pesquisa():
    texto = (DOCS / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    assert "Pergunta de pesquisa" in texto or "RQ" in texto
    assert "transversal" in texto and "temporal" in texto


def test_manuscrito_figuras_referenciadas():
    texto = (DOCS / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    for i in range(1, 7):
        assert f"Figura {i} —" in texto, i
    # gráficos e mapas presentes no markdown
    assert "outputs/figuras/fig_scatter_niveis_micro.png" in texto
    assert "outputs/figuras/fig_serie_ideb_micro.png" in texto
    assert "outputs/figuras/fig_loocv_r_teste.png" in texto
    assert "outputs/figuras/fig_scatter_ganho_renda.png" in texto
    assert "outputs/mapas/mapa_renda_responsavel_censo2022.png" in texto
    assert "outputs/mapas/mapa_pib_per_capita_2021.png" in texto


def test_manuscrito_quatro_tabelas():
    texto = (DOCS / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    for i in range(1, 5):
        assert f"**Tabela {i} —" in texto or f"**Tabela {i} —" in texto, i


# ---------- figuras geradas (gráficos) ----------

def test_figuras_geradas():
    for f in ["fig_scatter_niveis_micro.png", "fig_serie_ideb_micro.png",
              "fig_loocv_r_teste.png", "fig_scatter_ganho_renda.png"]:
        p = FIGURAS / f
        assert p.exists() and p.stat().st_size > 10_000, f
    m = json.loads((FIGURAS / "figuras_manifest.json").read_text(encoding="utf-8"))
    assert len(m["figuras"]) == 4


def test_script_graficos_existe():
    assert (SCRIPTS / "graficos_crateus.py").exists()
