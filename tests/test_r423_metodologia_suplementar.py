# -*- coding: utf-8 -*-
"""Testes R423 — Melhorias metodológicas pós-peer-review (SPEC-935-R423).

Requisitos:
1. Script scripts/analyze_metodologia_suplementar.py gera artefatos novos:
   tabela12_loocv_dispersao.csv, tabela5b_cluster_comparativo.csv,
   tabela13_tost_deteccao.csv, provenance_r423.json.
2. LOOCV: mediana 0,778; DP 0,508; média 0,542; %>0 83%; correlação
   n_obs × |rho_teste| = 0,248 (p = 0,004).
3. FE sem cluster: coef 0,073; SE 0,055; IC [−0,036; 0,182]; p 0,190 —
   números antigos inalterados (0,073; [−0,169; 0,314]; p 0,555).
4. MDES = 0,173; TOST ±0,10 (p = 0,329); TOST ±0,05 (p = 0,644).
5. MD canônico contém subseção 4.10, Tabela 5b e Tabela 13; TeX espelha;
   PDF sem Overfull/Underfull; DOCX regenerado.
"""

import json
from pathlib import Path

import pandas as pd

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
MD = AUDIT / "ARTIGO_RBEP_SUBMISSAO.md"
TEX = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.tex"
LOG = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.log"
SCRIPT = AUDIT / "scripts" / "analyze_metodologia_suplementar.py"
OUT = AUDIT / "outputs" / "expanded"


class TestArtefatos:
    def test_script_existe(self):
        assert SCRIPT.exists()

    def test_artefatos_existem(self):
        for nome in ["tabela12_loocv_dispersao.csv", "tabela5b_cluster_comparativo.csv",
                     "tabela13_tost_deteccao.csv", "provenance_r423.json"]:
            assert (OUT / nome).exists(), nome

    def test_provenance_tem_hash_do_painel(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        assert prov["painel_entrada"]["sha256"]
        assert prov["folds_entrada"]["sha256"]


class TestLoocvDispersao:
    def test_valores_chave(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        d = prov["loocv_dispersao"]
        assert abs(d["rho_teste_media"] - 0.542) < 0.001
        assert abs(d["rho_teste_mediana"] - 0.778) < 0.001
        assert abs(d["rho_teste_dp"] - 0.508) < 0.001
        assert abs(d["rho_teste_pct_positivo"] - 83.0) < 1.0

    def test_instabilidade_n_pequeno(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        d = prov["loocv_dispersao"]
        assert abs(d["corr_n_obs_x_abs_rho_teste"] - 0.248) < 0.01
        assert d["corr_n_obs_x_abs_rho_teste_p"] < 0.01


class TestClusterComparativo:
    def test_valores_chave(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        sem = prov["painel_fe_sem_cluster"]
        assert abs(sem["coef"] - 0.0728) < 0.0005
        assert abs(sem["se"] - 0.0554) < 0.0005
        assert abs(sem["ic_95_inf"] - (-0.036)) < 0.002
        assert abs(sem["ic_95_sup"] - 0.182) < 0.002

    def test_numeros_antigos_inalterados(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        ref = prov["painel_fe_cluster_referencia"]
        assert abs(ref["coef"] - 0.073) < 0.001
        assert abs(ref["ic_95_inf"] - (-0.169)) < 0.002
        assert abs(ref["ic_95_sup"] - 0.314) < 0.002
        assert abs(ref["p_value"] - 0.555) < 0.001

    def test_csv_contem_duas_linhas(self):
        df = pd.read_csv(OUT / "tabela5b_cluster_comparativo.csv")
        assert len(df) == 6


class TestTostDeteccao:
    def test_mdes(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        assert abs(prov["tost_deteccao"]["mdes_poder80_alpha5"] - 0.1725) < 0.002

    def test_tost_010(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        t = prov["tost_deteccao"]["tost_010"]
        assert abs(t["p_tost"] - 0.3291) < 0.005

    def test_tost_005(self):
        prov = json.loads((OUT / "provenance_r423.json").read_text(encoding="utf-8"))
        t = prov["tost_deteccao"]["tost_005"]
        assert abs(t["p_tost"] - 0.6441) < 0.005

    def test_anti_overclaim_tost(self):
        texto_md = MD.read_text(encoding="utf-8")
        assert "não permite declarar equivalência" in texto_md
        assert "não-detecção, não de equivalência" in texto_md


class TestDocumento:
    def test_md_contem_4_10(self):
        texto = MD.read_text(encoding="utf-8")
        assert "### 4.10 Limites de detecção" in texto
        assert "TOST ±0,10 (p) | 0,329" in texto
        assert "tabela12_loocv_dispersao.csv" in texto
        assert "tabela5b_cluster_comparativo.csv" in texto

    def test_tex_espelha(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "subsection{Limites de detecção" in texto
        assert "tab:clustercomp" in texto
        assert "tab:tost" in texto
        assert "tabela12_loocv_dispersao.csv" in texto

    def test_pdf_sem_overfull(self):
        log = LOG.read_text(encoding="utf-8", errors="ignore")
        assert "Overfull" not in log
        assert "Underfull" not in log
