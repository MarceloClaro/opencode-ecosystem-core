# -*- coding: utf-8 -*-
"""Testes R419 — Estatística da hipótese, amostragem e confiabilidade.

Requisitos (SPEC-935-R419):
1. Script `scripts/analyze_hipotese_confiabilidade.py` lê os crus WDI
   (data/raw_expandido/) e persiste `outputs/expanded/provenance_r419.json`
   + tabela9_hipotese.csv, tabela10_amostragem.csv, tabela11_confiabilidade.csv.
2. Teste formal da hipótese central por bootstrap por país (500 replicações,
   seed fixa): Δ = ρ_níveis − ρ_1ªdif com IC95% percentil e p-valor.
3. Amostragem formal: população (217 países oficiais WDI), critério de
   elegibilidade (≥ 20 obs), motivos de exclusão e cobertura temporal.
4. Confiabilidade: IC95% bootstrap dos ρ centrais e robustez de semente.
5. Seção 4.9 no MD canônico e espelhada no LaTeX, com anti-overclaim,
   números do texto ancorados na proveniência (tolerância 0,005) e
   tabelas 9/10/11 dentro das margens (0 Overfull no log do LaTeX).
"""

import json
import re
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
OUT = AUDIT / "outputs" / "expanded"
PROV = OUT / "provenance_r419.json"
TAB9 = OUT / "tabela9_hipotese.csv"
TAB10 = OUT / "tabela10_amostragem.csv"
TAB11 = OUT / "tabela11_confiabilidade.csv"
SCRIPT = AUDIT / "scripts" / "analyze_hipotese_confiabilidade.py"
MD = AUDIT / "ARTIGO_RBEP_SUBMISSAO.md"
LATEX = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.tex"
PDF = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.pdf"

TERMOS_BLOQUEADOS = [
    "Qualis A1", "superhuman", "inédito", "inédita", "efeito causal",
    "causalidade", "causa", "impulsiona", "leva a", "garante",
    "prova que", "assegura que",
]


def secao_49(texto: str) -> str:
    assert "### 4.9" in texto or "\\subsection{Estatística da hipótese" in texto
    if "### 4.9" in texto:
        return texto.split("### 4.9")[1].split("### 4.10")[0]
    return texto.split("\\subsection{Estatística da hipótese")[1].split("\\section{Discussão}")[0]


class TestScriptEProvenance:
    def test_script_existe(self):
        assert SCRIPT.exists(), "scripts/analyze_hipotese_confiabilidade.py ausente"

    def test_provenance_existe(self):
        assert PROV.exists(), "outputs/expanded/provenance_r419.json ausente"

    def test_proveniencia_fechada(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["proveniencia_fechada"] is True
        assert "sha256_raw" in prov
        assert len(prov["sha256_raw"]) >= 3
        assert "sha256_countries_meta" in prov

    def test_blocos_principais(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        for chave in ["hipotese", "amostragem", "confiabilidade"]:
            assert chave in prov, f"proveniência sem bloco '{chave}'"


class TestHipotese:
    def test_delta_obs(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["hipotese"]["delta_obs"] - 0.604) < 0.005

    def test_rho_niveis_obs(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["hipotese"]["rho_niveis_obs"] - 0.751) < 0.005

    def test_rho_diferencas_obs(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["hipotese"]["rho_diferencas_obs"] - 0.146) < 0.005

    def test_ic95_delta_positivo(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        h = prov["hipotese"]
        assert h["delta_ic95_inf"] > 0, "IC95% do Δ contém zero"

    def test_p_valor(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["hipotese"]["p_valor_delta_positivo"] < 0.05

    def test_ics_nao_sobrepoem(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        h = prov["hipotese"]
        assert h["rho_niveis_ic95_inf"] > h["rho_diferencas_ic95_sup"], (
            "IC95% dos ρ se sobrepõem"
        )

    def test_n_boot(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["hipotese"]["n_boot"] == 500
        assert prov["hipotese"]["n_replicacoes_validas"] == 500


class TestAmostragem:
    def test_populacao(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["amostragem"]["populacao"]["n_paises_oficiais_wdi"] == 217

    def test_elegiveis_e_amostra(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["amostragem"]["elegiveis"] == 135
        assert prov["amostragem"]["amostra_final"] == 135

    def test_exclusoes_total(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["amostragem"]["exclusoes"]["total_paises_excluidos"] == 82

    def test_exclusoes_por_motivo(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        motivo = prov["amostragem"]["exclusoes"]["por_motivo"]
        assert motivo["sem_matricula"] == 13
        assert motivo["sem_pib"] == 2
        assert motivo["sem_matricula_e_sem_pib"] == 2
        assert motivo["menos_de_20_obs"] == 65

    def test_cobertura_decadas(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        dec = prov["amostragem"]["cobertura_decadas"]
        assert dec["1960s"]["n_pais_ano"] == 1350
        assert dec["2020s"]["n_pais_ano"] == 540


class TestConfiabilidade:
    def test_quatro_sementes(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        seeds = prov["confiabilidade"]["sementes"]
        assert len(seeds) == 4
        assert [s["seed"] for s in seeds] == [42, 7, 2024, 123]

    def test_delta_estavel_entre_sementes(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        seeds = prov["confiabilidade"]["sementes"]
        deltas = {s["delta_obs"] for s in seeds}
        assert len(deltas) == 1, "Δ observado varia entre sementes"

    def test_p_valor_estavel(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        seeds = prov["confiabilidade"]["sementes"]
        assert all(s["p_valor_delta_positivo"] < 0.05 for s in seeds)

    def test_ic_estavel_entre_sementes(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        seeds = prov["confiabilidade"]["sementes"]
        infs = [s["delta_ic95_inf"] for s in seeds]
        sups = [s["delta_ic95_sup"] for s in seeds]
        assert (max(infs) - min(infs)) < 0.01
        assert (max(sups) - min(sups)) < 0.01


class TestTabelas:
    def test_tabela9(self):
        assert TAB9.exists()
        linhas = TAB9.read_text(encoding="utf-8").strip().splitlines()
        assert len(linhas) >= 4
        assert "0,604" in TAB9.read_text(encoding="utf-8")

    def test_tabela10(self):
        assert TAB10.exists()
        linhas = TAB10.read_text(encoding="utf-8").strip().splitlines()
        assert len(linhas) >= 8
        assert "217;135" in TAB10.read_text(encoding="utf-8")

    def test_tabela11(self):
        assert TAB11.exists()
        linhas = TAB11.read_text(encoding="utf-8").strip().splitlines()
        assert len(linhas) >= 5
        assert "2024" in TAB11.read_text(encoding="utf-8")


class TestSecaoNoArtigo:
    def test_secao_49_no_md(self):
        texto = MD.read_text(encoding="utf-8")
        assert "### 4.9 Estatística da hipótese, amostragem e confiabilidade" in texto

    def test_secao_49_no_tex(self):
        texto = LATEX.read_text(encoding="utf-8")
        assert "\\subsection{Estatística da hipótese, amostragem e confiabilidade}" in texto

    def test_tabelas_9_10_11_no_md(self):
        texto = MD.read_text(encoding="utf-8")
        secao = texto.split("### 4.9")[1].split("### 4.10")[0]
        for ref in ["Tabela 9", "Tabela 10", "Tabela 11"]:
            assert ref in secao

    def test_ancora_31(self):
        texto = MD.read_text(encoding="utf-8")
        secao = texto.split("### 3.1")[1].split("### 3.2")[0]
        assert "subseção 4.9" in secao

    def test_ancora_42(self):
        texto = MD.read_text(encoding="utf-8")
        secao = texto.split("### 4.2")[1].split("### 4.3")[0]
        assert "subseção 4.9" in secao
        assert "0,604" in secao

    def test_anti_overclaim(self):
        texto_md = MD.read_text(encoding="utf-8")
        secao = secao_49(texto_md)
        for termo in TERMOS_BLOQUEADOS:
            assert termo.lower() not in secao.lower(), (
                f"termo bloqueado na seção 4.9: '{termo}'"
            )

    def test_numeros_da_secao_na_provenance(self):
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
        texto_md = MD.read_text(encoding="utf-8")
        secao = secao_49(texto_md)
        for v in re.findall(r"([−-]?\d+[.,]\d+)", secao):
            if "." in v and v.count(".") == 1:
                inteiro, frac = v.split(".")
                if len(frac) == 3:
                    v_norm = float(inteiro + frac)
                else:
                    v_norm = float(v.replace(",", ".").replace("−", "-"))
            else:
                v_norm = float(v.replace(",", ".").replace("−", "-"))
            assert any(abs(v_norm - x) < 0.005 for x in candidatos), (
                f"número '{v}' na seção 4.9 sem proveniência r419"
            )

    def test_linguagem_associativa(self):
        texto_md = MD.read_text(encoding="utf-8")
        secao = secao_49(texto_md)
        assert "associ" in secao.lower() or "associação" in secao.lower()


class TestLatex:
    def test_pdf_existe(self):
        assert PDF.exists(), "PDF não compilado"

    def test_latex_sem_overfull(self):
        log = LATEX.parent / "ARTIGO_RBEP_SUBMISSAO.log"
        if not log.exists():
            pytest.skip("log LaTeX indisponível")
        conteudo = log.read_text(encoding="utf-8", errors="replace")
        assert "Overfull" not in conteudo, "LaTeX com Overfull hbox/vbox (tabela fora das margens)"
