# -*- coding: utf-8 -*-
"""Testes R413 — Canais associativos da educação terciária (SPEC-935-R413).

Requisitos:
1. Script `scripts/analyze_channels.py` reusa o painel expandido (R412) e
   persiste `outputs/channels/provenance_r413.json` + tabelas CSV.
2. Matriz de correlações parciais (ctrl PIB) com IC bootstrap por país;
   análise em etapas do par matrícula×PIB (queda ao adicionar saúde);
   canais saúde/desigualdade/inovação com painel FE clusterizado;
   moderação institucional (interações matrícula×WGI, matrícula×P&D).
3. LOOCV ≥ 20 folds das parciais centrais.
4. NOTA_CANAIS_ASSOCIATIVOS.md: anti-overclaim, resumo trilíngue, números
   do resumo com proveniência em provenance_r413.json.
5. LaTeX + PDF compilável; suíte R408–R413 verde.

Estes testes são RED: falham até a implementação existir.
"""

import json
import re
from pathlib import Path

import pandas as pd
import pytest

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
OUT_CH = AUDIT / "outputs" / "channels"
PROV = OUT_CH / "provenance_r413.json"
NOTA = AUDIT / "NOTA_CANAIS_ASSOCIATIVOS.md"
LATEX = AUDIT / "latex" / "NOTA_CANAIS_ASSOCIATIVOS.tex"
PDF = AUDIT / "latex" / "NOTA_CANAIS_ASSOCIATIVOS.pdf"

TERMOS_BLOQUEADOS = [
    "Qualis A1", "superhuman", "inédito", "inédita", "efeito causal",
    "causalidade", "causa", "impulsiona", "leva a", "garante",
    "prova que", "assegura que",
]


class TestScriptEProvenance:
    def test_script_existe(self):
        script = AUDIT / "scripts" / "analyze_channels.py"
        assert script.exists(), "scripts/analyze_channels.py ausente"

    def test_provenance_existe(self):
        assert PROV.exists(), "outputs/channels/provenance_r413.json ausente"

    def test_provenance_cobre_requisitos(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        for chave in ["parciais", "etapas", "canais", "interacoes",
                      "loocv_folds", "seed", "n_bootstrap"]:
            assert chave in prov, f"proveniência sem '{chave}'"

    def test_painel_fonte_declarado(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert "painel_fonte" in prov
        assert "panel_wdi_expandido" in prov["painel_fonte"]


class TestMatrizParciais:
    def test_tabela_parciais_existe(self):
        tabela = OUT_CH / "tabela_parciais.csv"
        assert tabela.exists(), "tabela_parciais.csv ausente"

    def test_parciais_tem_ic_bootstrap(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        parciais = prov["parciais"]
        assert parciais, "matriz de parciais vazia"
        primeira = parciais[0]
        for chave in ["x", "y", "rho_parcial", "n", "ic_boot_inf",
                      "ic_boot_sup"]:
            assert chave in primeira, f"parcial sem '{chave}'"

    def test_parcial_saude_na_matriz(self):
        """Canal saúde: matrícula terciária × expectativa de vida (ctrl PIB)."""
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        alvo = None
        for p in prov["parciais"]:
            if ("ln_tertiaria" in {p["x"], p["y"]}
                    and "SP_DYN_LE00_IN" in {p["x"], p["y"]}):
                alvo = p
        assert alvo, "parcial matrícula×expectativa de vida ausente"
        assert alvo["rho_parcial"] > 0.3, (
            f"parcial saúde fraca/negativa: {alvo['rho_parcial']:.3f}"
        )

    def test_parcial_gini_na_matriz(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        alvo = None
        for p in prov["parciais"]:
            if ("ln_tertiaria" in {p["x"], p["y"]}
                    and "SI_POV_GINI" in {p["x"], p["y"]}):
                alvo = p
        assert alvo, "parcial matrícula×Gini ausente"

    def test_parcial_inovacao_na_matriz(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        alvo = None
        for p in prov["parciais"]:
            if ("GB_XPD_RSDV_GD_ZS" in {p["x"], p["y"]}
                    and "TX_VAL_TECH_MF_ZS" in {p["x"], p["y"]}):
                alvo = p
        assert alvo, "parcial P&D×alta tecnologia ausente"


class TestAnaliseEmEtapas:
    def test_tabela_etapas_existe(self):
        tabela = OUT_CH / "tabela_etapas.csv"
        assert tabela.exists(), "tabela_etapas.csv ausente"

    def test_etapas_documentam_queda(self):
        """Mediação descritiva: rho inicial > rho final (controle saúde)."""
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        etapas = prov["etapas"]
        assert len(etapas) >= 3, "menos de 3 etapas documentadas"
        rho_inicial = None
        rho_final = None
        for e in etapas:
            if e.get("etapa") == "inicial" or e.get("ordem") == 0:
                rho_inicial = e["rho"]
            if e.get("etapa") == "saude" or e.get("controle") == "saude":
                rho_final = e["rho"]
        assert rho_inicial is not None and rho_final is not None, (
            "etapas inicial/final não identificáveis"
        )
        assert rho_final < rho_inicial, (
            f"queda não documentada: {rho_inicial:.3f} → {rho_final:.3f}"
        )

    def test_etapas_tem_ic_bootstrap(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        for e in prov["etapas"]:
            assert "ic_boot_inf" in e and "ic_boot_sup" in e, (
                "etapa sem IC bootstrap"
            )
            assert "n" in e


class TestCanais:
    def test_canal_saude_painel_fe(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        canal = prov["canais"].get("saude")
        assert canal, "canal saúde ausente"
        assert canal["cluster"] == "por_pais"
        assert canal["n_clusters"] >= 20
        assert canal["coef"] > 0, f"coef FE saúde não positivo: {canal['coef']}"

    def test_canal_desigualdade_painel_fe(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        canal = prov["canais"].get("desigualdade")
        assert canal, "canal desigualdade ausente"
        assert canal["cluster"] == "por_pais"
        assert canal["n_clusters"] >= 20

    def test_canal_inovacao_painel_fe(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        canal = prov["canais"].get("inovacao")
        assert canal, "canal inovação ausente"
        assert canal["cluster"] == "por_pais"
        assert canal["n_clusters"] >= 20
        assert canal["coef"] > 0, f"coef FE inovação não positivo: {canal['coef']}"


class TestModeracaoInstitucional:
    def test_interacoes_exploratorias(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        inter = prov["interacoes"]
        assert inter, "interações ausentes"
        chaves = {i.get("termo") for i in inter}
        assert any("WGI" in c for c in chaves), "interação matrícula×WGI ausente"
        assert any("RSDV" in c for c in chaves), "interação matrícula×P&D ausente"
        for i in inter:
            assert i.get("exploratorio") is True, (
                "interação deve ser marcada como exploratória"
            )
            assert "coef" in i and "p_value" in i


class TestValidacao:
    def test_loocv_20_folds(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["loocv_folds"] >= 20, (
            f"apenas {prov['loocv_folds']} folds LOOCV"
        )
        folds = OUT_CH / "loocv_folds_channels.json"
        assert folds.exists()
        data = json.loads(folds.read_text(encoding="utf-8"))
        assert len(data["folds"]) >= 20

    def test_bootstrap_500(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["n_bootstrap"] >= 500
        assert prov["seed"] == 42

    def test_reprodutibilidade_seed_fixa(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert "seed" in prov


class TestNota:
    def test_nota_existe(self):
        assert NOTA.exists(), "NOTA_CANAIS_ASSOCIATIVOS.md ausente"

    def test_anti_overclaim(self):
        texto = NOTA.read_text(encoding="utf-8")
        for termo in TERMOS_BLOQUEADOS:
            assert termo.lower() not in texto.lower(), (
                f"termo bloqueado na nota: '{termo}'"
            )
        # Bloqueia o verbo "determinar" flexionado (alegação causal), mas
        # permite "determinantes" (substantivo técnico da literatura).
        for verbo in [r"\bdetermina\b", r"\bdeterminam\b", r"\bdeterminar\b",
                      r"\bdeterminado\b", r"\bdeterminada\b"]:
            assert not re.search(verbo, texto, re.IGNORECASE), (
                f"verbo causal na nota: '{verbo}'"
            )
        assert "associativ" in texto.lower() or "associação" in texto.lower(), (
            "nota não usa linguagem associativa"
        )

    def test_resumo_trilingue(self):
        texto = NOTA.read_text(encoding="utf-8")
        for secao in ["Resumo", "Abstract", "Resumen"]:
            assert secao in texto, f"seção '{secao}' ausente"

    def test_numeros_do_resumo_na_provenance(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))

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
        texto = NOTA.read_text(encoding="utf-8")
        resumo = texto.split("Abstract")[0]
        for v in re.findall(r"([−-]?\d+[.,]\d+)", resumo):
            v_norm = float(v.replace(",", ".").replace("−", "-"))
            assert any(abs(v_norm - x) < 0.005 for x in candidatos), (
                f"número '{v}' no resumo sem proveniência r413"
            )

    def test_proveniencia_fechada(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert "proveniencia_fechada" in prov and prov["proveniencia_fechada"]
        assert "sha256_painel" in prov


class TestLatex:
    def test_tex_existe(self):
        assert LATEX.exists(), "NOTA_CANAIS_ASSOCIATIVOS.tex ausente"

    def test_pdf_existe(self):
        assert PDF.exists(), "NOTA_CANAIS_ASSOCIATIVOS.pdf ausente"
