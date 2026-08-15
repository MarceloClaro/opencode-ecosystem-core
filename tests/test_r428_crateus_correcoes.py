#!/usr/bin/env python3
"""Testes do ciclo R428 — correções da auditoria Qualis A1 (artigo Crateús-IDEB).

Verifica que os resultados corrigidos estão presentes e coerentes:
- between-estimator com IC95% bootstrap por cluster (n=9);
- p-valores cluster-robustos (bootstrap por cluster; CRVE t(G-1); wild cluster);
- H3 corrigida (metas por ano, mesmo ano de referência);
- PIB real deflacionado (IPCA/IPEA Data);
- TOST com SESOI ±0,5 e MDES traduzido por +10% do PIB real;
- LOOCV rotulado como validação INTERNA;
- robustez de defasagem 0-4;
- proveniência (SHA-256 do script e do deflator).

Executar: pytest tests/test_r428_crateus_correcoes.py -v
"""
import hashlib
import json
from pathlib import Path

import pytest

PAPER = Path(__file__).resolve().parent.parent / "academic" / "papers" / "crateus_ideb"
RES = json.loads((PAPER / "outputs" / "expanded" / "resultados_r428.json").read_text(encoding="utf-8"))
PROV = json.loads((PAPER / "outputs" / "expanded" / "provenance_r428.json").read_text(encoding="utf-8"))
IPCA = json.loads((PAPER / "data" / "processed" / "ipca_medias_anuais.json").read_text(encoding="utf-8"))
MICRO = RES["microrregiao_sertao_crateus"]


def test_ciclo_metadados():
    assert RES["metadados"]["ciclo"] == "R428"
    assert RES["metadados"]["seed"] == 42
    assert RES["metadados"]["defasagem_principal"] == 2


def test_between_estimator_n9():
    b = MICRO["between_municipios"]
    assert b["n_municipios"] == 9
    assert b["bootstrap_b"] == 5000
    # r between e IC incluem zero (não discernível)
    assert b["ic95_inf"] < 0 < b["ic95_sup"]
    assert b["p_bootstrap_cluster"] > 0.05
    # jackknife presente para os 9 municípios
    assert len(b["jackknife"]) == 9


def test_pooled_ic_inclui_zero_micro():
    p = MICRO["niveis_pooled"]
    assert p["n"] == 108
    assert p["ic95_inf"] < 0 < p["ic95_sup"]
    assert p["p_bootstrap_cluster"] > 0.05
    assert p["bootstrap_b"] == 5000


def test_primeiras_diferencas():
    pd_ = MICRO["primeiras_diferencas"]
    assert pd_["n"] == 90
    assert pd_["p_valor"] > 0.05


def test_fe_cluster_robusto():
    fe = MICRO["fe"]
    assert fe["especificacao"] == "municipio_x_etapa + ano"
    assert fe["n_clusters"] == 9
    assert fe["n"] == 108
    # se_cluster maior que se (correção de pequena amostra)
    assert fe["se_cluster"] > fe["se"]
    # não significativo sob clusterização
    assert fe["p_valor_cluster_t"] > 0.05
    assert fe["p_wild_cluster_bootstrap"] > 0.05
    assert fe["ic95_cluster_inf"] < 0 < fe["ic95_cluster_sup"]
    assert fe["wild_b"] == 9999


def test_mdes_traduzido_e_tost_substantivo():
    mt = RES["mdes_tost_micro"]
    assert mt["mdes_cluster"] > 5.0  # detectaria apenas efeitos incomuns
    assert 0.3 < mt["mdes_por_10pct_pib_real"] < 1.0  # ~0,57 ponto por +10%
    # TOST com margem substantiva ±0,5 não significativo (precisão insuficiente)
    assert mt["tost"]["0.5"]["p_tost"] > 0.05
    # margem ±0,10 mantida como transparência
    assert mt["tost"]["0.1"]["p_tost"] > 0.05
    assert "não-detecção" in mt["leitura_mdes"].lower() or "precisão" in mt["leitura_tost"].lower()


def test_h3_metas_mesmo_ano():
    h = RES["h3_metas_por_ano"]
    assert h["n_comparacoes"] == 108
    assert h["pct_atingiu_geral"] > 95.0  # 99,1%
    # anos cobertos: 2011..2021
    assert set(h["por_ano"].keys()) == {"2011", "2013", "2015", "2017", "2019", "2021"}
    # Crateús anos iniciais 2021: observado 6,5 >= meta 5,2
    cr = [d for d in h["ai_2021_detalhe"] if d["nome"] == "Crateús" and d["etapa"] == "anos_iniciais"]
    assert cr and cr[0]["ideb_observado"] == 6.5 and cr[0]["meta_inep"] == 5.2 and cr[0]["atingiu"]
    # proposição separada ganho×renda com n=9
    g = h["correlacao_ganho_renda_ai"]
    assert g["n"] == 9 and g["p_valor"] > 0.05


def test_loocv_rotulado_interno():
    l = RES["loocv_interno"]
    assert l["n_folds"] == 9
    assert "Validação INTERNA" in l["nota"]
    assert "não constitui validação externa" in l["nota"]
    assert "co-tendência" in l["nota"]
    assert l["pct_positivos"] == 100.0


def test_robustez_lags():
    perfil = RES["robustez_lags"]["perfil_lags"]
    assert [p["lag"] for p in perfil] == [0, 1, 2, 3, 4]
    assert RES["robustez_lags"]["defasagem_principal"] == 2


def test_deflator_ipca_registrado():
    assert IPCA["serie"] == "PRECOS12_IPCA12"
    assert IPCA["base_ano"] == 2021
    # fator deflator para 2021 é 1,0
    assert IPCA["fator_deflator_para_2021"]["2021"] == 1.0
    assert IPCA["n_registros"] > 1000


def test_proveniencia_sha256():
    prov_script = PROV["sha256_scripts"]["analise_crateus_r428.py"]
    real = hashlib.sha256((PAPER / "scripts" / "analise_crateus_r428.py").read_bytes()).hexdigest()
    assert prov_script == real
    prov_ipca = PROV["ipca"]["sha256_json"]
    real_ipca = hashlib.sha256((PAPER / "data" / "processed" / "ipca_medias_anuais.json").read_bytes()).hexdigest()
    assert prov_ipca == real_ipca


def test_missingness_reportada():
    m = MICRO["missingness"]
    assert m["escala"] == "microrregiao_sertao_crateus"
    assert m["n_municipios"] == 9
    assert "pct_missing_ideb" in m


def test_ceara_brasil_presentes():
    for escala in ["ceara", "brasil"]:
        b = RES[escala]
        assert b["between_municipios"]["n_municipios"] > 50
        assert b["fe"]["n_clusters"] == b["between_municipios"]["n_municipios"]


def test_tabela4_reproduz_ai_2021_detalhe():
    """A Tabela 4 do manuscrito (IDEB 2021 anos iniciais) DEVE reproduzir ai_2021_detalhe."""
    detalhe = {d["nome"]: d for d in RES["h3_metas_por_ano"]["ai_2021_detalhe"]}
    esperado = {
        "Ararendá": (5.3, 9.5), "Crateús": (5.2, 6.5), "Independência": (5.2, 8.7),
        "Ipaporanga": (6.1, 6.6), "Monsenhor Tabosa": (4.4, 6.3), "Nova Russas": (5.1, 7.2),
        "Novo Oriente": (5.6, 8.9), "Quiterianópolis": (5.9, 5.9), "Tamboril": (4.4, 6.6),
    }
    for nome, (meta, obs) in esperado.items():
        d = detalhe[nome]
        assert d["meta_inep"] == meta, nome
        assert d["ideb_observado"] == obs, nome
    assert len(esperado) == len(detalhe) == 9


def test_manuscrito_sem_termos_proibidos():
    md = (PAPER / "docs" / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    for proibido in ["padrão nacional", "estudo anterior", "espelh", "se confirma",
                     "primeiras diferenças foram nulas", "were null"]:
        assert proibido not in md.lower(), proibido
    assert "Cratéus" not in md


def test_manuscrito_missingness_reportada():
    md = (PAPER / "docs" / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    assert "0,5%" in md and "26,2%" in md and "1 de 198" in md


def test_manuscrito_atingiu_ou_superou():
    md = (PAPER / "docs" / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    assert "atingiram ou superaram" in md
    assert "no único desvio, um município, em 2013, não atingiu a meta" in md


def test_manuscrito_figuras_1_6_referenciadas():
    md = (PAPER / "docs" / "ARTIGO_CRATEUS_RBEP.md").read_text(encoding="utf-8")
    for i in range(1, 7):
        assert f"Figura {i}" in md


def test_json_leitura_mdes_atualizada():
    mt = RES["mdes_tost_micro"]
    assert "6,01" in mt["leitura_mdes"] and "0,57" in mt["leitura_mdes"]
    assert "5,71" not in mt["leitura_mdes"]


def test_linguagem_sem_overclaim_no_json():
    # o próprio JSON não deve conter vocabulário de confirmação de nulidade
    texto = json.dumps(RES, ensure_ascii=False).lower()
    for proibido in ["se confirma", "confirmando h", "foi nula", "foram nulas"]:
        assert proibido not in texto
