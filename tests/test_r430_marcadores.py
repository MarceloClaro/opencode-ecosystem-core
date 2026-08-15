#!/usr/bin/env python3
"""Testes do ciclo R430 — marcadores socioeconômicos não convencionais
(artigo Crateús-IDEB).

Verifica:
- Coleta: 9 municípios × ≥15 marcadores, todos com status "ok", valores
  plausíveis e proveniência (URL/tabela/variavel no manifest).
- Análise: 66 hipóteses (33 marcadores × 2 desfechos), n=9, correção
  FDR/Bonferroni aplicada e reportada, nenhuma sobrevivência (exploratório).
- Perfil Crateús: posições extremas consistentes (sede urbana).
- Manuscrito: subseção §4.8 presente no MD e TeX; termos proibidos (R426)
  ausentes; números R428 intactos no texto.

Executar: pytest tests/test_r430_marcadores.py -v
"""
import json
import re
from pathlib import Path

import pytest

PAPER = Path(__file__).resolve().parent.parent / "academic" / "papers" / "crateus_ideb"
RES = json.loads((PAPER / "outputs" / "expanded" / "resultados_r430.json").read_text(encoding="utf-8"))
PROV = json.loads((PAPER / "outputs" / "expanded" / "provenance_r430.json").read_text(encoding="utf-8"))
DATA = json.loads((PAPER / "data" / "processed" / "indicadores_r430.json").read_text(encoding="utf-8"))
MAN = json.loads((PAPER / "data" / "processed" / "manifest_r430.json").read_text(encoding="utf-8"))
R428 = json.loads((PAPER / "outputs" / "expanded" / "resultados_r428.json").read_text(encoding="utf-8"))
MD = (PAPER / "docs" / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
TEX = (PAPER / "latex" / "ARTIGO_CRATEUS_RBEP.tex").read_text(encoding="utf-8")

PROIBIDOS_R426 = [
    "estudo anterior", "espelh", "padrão nacional", "padrão associativo nacional",
    "reproduz o padrão", "se confirma", "confirmando h", "cratéus", "were null",
]


# ---------------------------------------------------------------- coleta
def test_coleta_n_municipios():
    assert len(DATA) == 9


def test_coleta_n_marcadores_minimo():
    n_ind = len(MAN["etiquetas"])
    assert n_ind >= 15
    assert n_ind == 33


def test_coleta_status_ok():
    for c in MAN["coletas"]:
        assert c["status"].startswith("ok"), f"{c['indicador']}: {c['status']}"


def test_coleta_valores_completos_e_plausiveis():
    for r in DATA:
        assert len([v for v in r.values() if v is not None]) >= 15
    # ordem de grandeza
    for r in DATA:
        assert 40 <= r["mulheres_pct"] <= 60
        assert 0 <= r["pobreza_renda_1sm_pct"] <= 100
        assert 500 <= r["rend_domiciliar_percapita"] <= 3000
        assert 3 <= r["anos_estudo_11mais"] <= 12
        assert 0 <= r["ocup_carteira_pct"] <= 100
        assert 0 <= r["ocup_sem_carteira_pct"] <= 100


def test_coleta_proveniencia():
    for c in MAN["coletas"]:
        assert c["url"].startswith("https://servicodados.ibge.gov.br/api/v3/agregados/")
        assert c["periodo"] == "2022"
        assert c["tabela"] in {9605, 9606, 9928, 9940, 10056, 10061, 10062,
                               10261, 10264, 10266, 10268, 10280, 10295, 10296}


# ---------------------------------------------------------------- análise
def test_analise_66_hipoteses_n9():
    assert RES["resumo"]["n_hipoteses"] == 66
    for r in RES["resultados"]:
        assert r["n"] == 9


def test_analise_ajuste_aplicado():
    for r in RES["resultados"]:
        assert 0 <= r["q_bh"] <= 1
        assert 0 <= r["q_bonferroni"] <= 1
    assert RES["resumo"]["ajuste"].startswith("FDR Benjamini-Hochberg")


def test_analise_exploratorio_sem_sobrevivencia():
    # Anti-overclaim: em n=9 com 66 hipóteses, nada sobrevive ao ajuste.
    assert RES["resumo"]["significativos_bh"] == []
    assert RES["resumo"]["significativos_bonf"] == []


def test_analise_seed_e_bootstrap():
    assert RES["resumo"]["seed"] == 42
    assert RES["resumo"]["b_reamostragens"] == 5000
    for r in RES["resultados"]:
        assert 0 <= r["sinal_estavel_pct"] <= 100


def test_perfil_crateus_sede_urbana():
    p25 = [r for r in RES["resultados"] if r["desfecho"] == "ideb_2025_ai"]
    crateus = {r["indicador"]: r for r in p25}
    # Crateús: máx em renda, estudo, carteira; mín em sem-carteira e pobreza
    assert crateus["rend_domiciliar_percapita"]["crateus_pos"] == 9
    assert crateus["anos_estudo_11mais"]["crateus_pos"] == 9
    assert crateus["ocup_carteira_pct"]["crateus_pos"] == 9
    assert crateus["ocup_sem_carteira_pct"]["crateus_pos"] == 1
    assert crateus["pobreza_renda_1sm_pct"]["crateus_pos"] == 1


def test_provenance():
    assert PROV["ciclo"] == "R430"
    assert "Censo Demográfico 2022" in PROV["fonte_indicadores"]
    assert "INEP" in PROV["fonte_ideb"]
    assert PROV["desenho"] == "transversal, n=9, microrregião Sertão de Crateús"


# ---------------------------------------------------------------- manuscrito
def test_manuscrito_subsecao_48():
    assert "## 4.8" in MD or "### 4.8" in MD or "Marcadores socioeconômicos não convencionais" in MD
    assert "Marcadores socioeconômicos não convencionais" in TEX


def test_manuscrito_sem_termos_proibidos():
    for t in PROIBIDOS_R426:
        assert t.lower() not in MD.lower(), f"termo proibido no MD: {t}"
        assert t.lower() not in TEX.lower(), f"termo proibido no TeX: {t}"


def test_manuscrito_nao_sobrepoe_r428():
    # Números-símbolo do R428 presentes e não alterados
    assert "−0,24" in MD or "-0,24" in MD
    assert "2,61" in MD or "2.61" in MD
    assert "108" in MD


def test_manuscrito_limite_corpo():
    corpo = re.sub(r"[#*\n\s]", "", MD)
    assert 40000 <= len(corpo) <= 70000, f"corpo MD com {len(corpo)} caracteres"
