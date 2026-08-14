# -*- coding: utf-8 -*-
"""Testes R412 — Expansão da pesquisa para eliminar limitações reais.

Requisitos (SPEC-935-R412):
1. Download auditável (data/raw_expandido/ + manifest_expandido.json, SHA-256).
2. Painel expandido ≥ 20 países (data/processed/panel_wdi_expandido_*.csv),
   com controles WGI e estruturais; sem imputação.
3. Análise expandida (outputs/expanded/): correlações, LOOCV ≥ 20 folds,
   subperíodos, painel FE com erros clusterizados por país, ML agrupado,
   proveniência completa.
4. Manuscrito atualizado (MD): menciona WGI e cluster; números do resumo
   com proveniência na provenance_expanded.json; anti-overclaim mantido.
"""

import json
import re
from pathlib import Path

import pandas as pd
import pytest

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
RAW_EXP = AUDIT / "data" / "raw_expandido"
MANIFEST_EXP = RAW_EXP / "manifest_expandido.json"
PAINEL_EXP = AUDIT / "data" / "processed" / "panel_wdi_expandido_1960_2023.csv"
OUT_EXP = AUDIT / "outputs" / "expanded"
PROV_EXP = OUT_EXP / "provenance_expanded.json"
ARTIGO = AUDIT / "ARTIGO_RBEP_SUBMISSAO.md"

CONTROLES_WGI = ["WGI_CC", "WGI_GE", "WGI_PV", "WGI_RQ", "WGI_RL", "WGI_VA"]
CONTROLES_ESTRUTURAIS = [
    "NV_IND_MANF_ZS", "TX_VAL_TECH_MF_ZS", "SP_DYN_LE00_IN", "BX_KLT_DINV_WD_GD_ZS",
]

TERMOS_BLOQUEADOS = [
    "Qualis A1", "superhuman", "inédito", "inédita",
    "0,997", "0.997", "AUC", "percentil", "efeito causal",
    "causalidade", "impulsiona", "leva a",
]


class TestDownloadAuditavel:
    def test_manifest_expandido_existe(self):
        assert MANIFEST_EXP.exists(), "manifest_expandido.json ausente"

    def test_manifest_tem_requests_com_hash(self):
        manifest = json.loads(MANIFEST_EXP.read_text(encoding="utf-8"))
        reqs = manifest["requests"]
        assert len(reqs) >= 12, f"apenas {len(reqs)} indicadores baixados"
        for req in reqs:
            assert req["sha256"], "request sem sha256"
            assert req["status_http"] == 200
            assert (RAW_EXP / req["cache_file"]).exists(), (
                f"cache_file ausente: {req['cache_file']}"
            )

    def test_wgi_no_manifest(self):
        manifest = json.loads(MANIFEST_EXP.read_text(encoding="utf-8"))
        indicadores = {r["indicator"] for r in manifest["requests"]}
        for wgi in ["CC.EST", "GE.EST", "RL.EST"]:
            assert wgi in indicadores, f"WGI {wgi} ausente do manifest"


class TestPainelExpandido:
    def test_painel_existe(self):
        assert PAINEL_EXP.exists(), "painel expandido ausente"

    def test_pelo_menos_20_paises(self):
        df = pd.read_csv(PAINEL_EXP)
        paises = df["iso3"].nunique()
        assert paises >= 20, f"apenas {paises} países (esperado ≥ 20)"

    def test_grade_pais_ano(self):
        df = pd.read_csv(PAINEL_EXP)
        cols = set(df.columns)
        assert {"iso3", "year"}.issubset(cols)
        assert not df.duplicated(subset=["iso3", "year"]).any(), (
            "duplicatas iso3-year"
        )

    def test_controles_wgi_presentes(self):
        df = pd.read_csv(PAINEL_EXP)
        cols = set(df.columns)
        for c in CONTROLES_WGI:
            assert c in cols, f"controle WGI {c} ausente do painel"
            assert df[c].notna().any(), f"{c} totalmente ausente (sem dados)"

    def test_controles_estruturais_presentes(self):
        df = pd.read_csv(PAINEL_EXP)
        cols = set(df.columns)
        for c in CONTROLES_ESTRUTURAIS:
            assert c in cols, f"controle estrutural {c} ausente do painel"

    def test_sem_imputacao_de_zero(self):
        """Ausências devem ser NaN, nunca zero preenchido."""
        df = pd.read_csv(PAINEL_EXP)
        assert df.isna().any().any(), "painel sem nenhum NaN (suspeito de imputação)"
        # variáveis econômicas não podem ter zero artificial
        for c in ["NY_GDP_PCAP_KD", "SE_TER_ENRR"]:
            assert (df[c].fillna(0) == 0).sum() < df[c].notna().sum(), (
                f"{c}: mais zeros que dados (imputação de zero?)"
            )


class TestAnaliseExpandida:
    def test_outputs_expandidos_existem(self):
        assert OUT_EXP.exists()
        assert PROV_EXP.exists(), "provenance_expanded.json ausente"

    def test_loocv_com_20_folds(self):
        prov = json.loads(PROV_EXP.read_text(encoding="utf-8"))
        assert prov["n_paises"] >= 20
        folds = OUT_EXP / "loocv_folds_expanded.json"
        assert folds.exists()
        data = json.loads(folds.read_text(encoding="utf-8"))
        assert len(data["folds"]) >= 20, (
            f"apenas {len(data['folds'])} folds LOOCV (esperado ≥ 20)"
        )

    def test_painel_fixe_efeitos_com_cluster(self):
        prov = json.loads(PROV_EXP.read_text(encoding="utf-8"))
        assert "efeito_fixo_cluster_coef" in prov
        assert "efeito_fixo_cluster_ic_inf" in prov
        assert "efeito_fixo_cluster_ic_sup" in prov
        assert prov.get("cluster_tipo") == "por_pais", (
            "cluster não é por país"
        )
        assert prov["n_clusters"] >= 20

    def test_controle_wgi_no_painel_fixe(self):
        prov = json.loads(PROV_EXP.read_text(encoding="utf-8"))
        assert prov.get("usou_controle_wgi") is True, (
            "painel FE sem controle WGI declarado"
        )

    def test_ml_agrupado_presente(self):
        prov = json.loads(PROV_EXP.read_text(encoding="utf-8"))
        assert "ml_auc_linha" in prov and "ml_auc_agrupado" in prov

    def test_proveniencia_cobre_numeros(self):
        prov = json.loads(PROV_EXP.read_text(encoding="utf-8"))
        for chave in ["rho_niveis_terciaria", "rho_diferencas_terciaria",
                      "n_paises", "n_pais_ano"]:
            assert chave in prov, f"proveniência sem '{chave}'"


class TestManuscritoAtualizado:
    def test_artigo_mentiona_wgi(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert "WGI" in texto or "governança" in texto, (
            "artigo não menciona controles WGI"
        )

    def test_artigo_mentiona_cluster(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert "cluster" in texto.lower(), (
            "artigo não menciona erros padrão clusterizados"
        )

    def test_artigo_mentiona_paises_expandidos(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert re.search(r"\b\d{2,3}\s+países\b", texto, re.IGNORECASE), (
            "artigo não menciona painel expandido (≥ 20 países)"
        )

    def test_numeros_do_resumo_na_provenance(self):
        prov = json.loads(PROV_EXP.read_text(encoding="utf-8"))

        def iter_numeros(obj):
            if isinstance(obj, (int, float)):
                yield obj
            elif isinstance(obj, list):
                for item in obj:
                    yield from iter_numeros(item)
            elif isinstance(obj, dict):
                for item in obj.values():
                    yield from iter_numeros(item)

        candidatos = list(iter_numeros(prov))
        texto = ARTIGO.read_text(encoding="utf-8")
        resumo = texto.split("Abstract")[0]
        for v in re.findall(r"([−-]?\d+[.,]\d+)", resumo):
            v_norm = float(v.replace(",", ".").replace("−", "-"))
            assert any(abs(v_norm - x) < 0.005 for x in candidatos), (
                f"número '{v}' no resumo sem proveniência expandida"
            )

    def test_anti_overclaim_mantido(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        for termo in TERMOS_BLOQUEADOS:
            assert termo not in texto, f"termo bloqueado: '{termo}'"
        for causal in ["determina", "garante", "assegura que", "prova que"]:
            assert causal not in texto.lower()
        # Refinamento R414 (alinhado ao gate R413): "causa"/"prova" como
        # palavra são alegações; formas adjetivais em contexto não assertivo
        # ("causais", "provavelmente") são aceitáveis.
        assert not re.search(r"\bcausa\b", texto, re.IGNORECASE), (
            "uso não-negado de 'causa' no artigo"
        )

    def test_trilinguismo_mantido(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        for secao in ["Resumo", "Abstract", "Resumen", "Título en español",
                      "Palavras-chave", "Keywords", "Palabras clave"]:
            assert secao in texto, f"seção '{secao}' ausente"
