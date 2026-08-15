# -*- coding: utf-8 -*-
"""Testes R418 — Caso brasileiro em perspectiva comparada (SPEC-935-R418).

Requisitos:
1. Script `scripts/analyze_brasil_comparativo.py` lê os crus WDI
   (data/raw_expandido/), mesma fonte do painel expandido (R412), e persiste
   `outputs/expanded/provenance_r418.json` + `tabela8_brasil_comparado.csv`.
2. Janela 2012-2022 (única em que o WDI reporta matrícula terciária para o
   Brasil); unidades: Brasil, renda média asiática (CHN, IDN, MYS, THA, VNM),
   EUA, Europa Ocidental (DEU, FRA, GBR, ITA, ESP, PRT) e China.
3. Cobertura desbalanceada declarada (EUA/DEU iniciam em 2013; PRT em 2015);
   crescimento médio anual calculado sobre o número real de anos, sem imputação.
4. Seção 4.8 "O caso brasileiro em perspectiva comparada" presente no MD
   canônico e espelhada no LaTeX, com anti-overclaim e números do texto
   ancorados na proveniência (tolerância 0,005).
5. LaTeX compilável (PDF presente); suíte R408–R418 verde.

Estes testes são RED: falham até a implementação existir.
"""

import json
import re
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
OUT = AUDIT / "outputs" / "expanded"
PROV = OUT / "provenance_r418.json"
TABELA = OUT / "tabela8_brasil_comparado.csv"
SCRIPT = AUDIT / "scripts" / "analyze_brasil_comparativo.py"
MD = AUDIT / "ARTIGO_RBEP_SUBMISSAO.md"
LATEX = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.tex"
PDF = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.pdf"

TERMOS_BLOQUEADOS = [
    "Qualis A1", "superhuman", "inédito", "inédita", "efeito causal",
    "causalidade", "causa", "impulsiona", "leva a", "garante",
    "prova que", "assegura que",
]


class TestScriptEProvenance:
    def test_script_existe(self):
        assert SCRIPT.exists(), "scripts/analyze_brasil_comparativo.py ausente"

    def test_provenance_existe(self):
        assert PROV.exists(), "outputs/expanded/provenance_r418.json ausente"

    def test_provenance_janela(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["janela"] == [2012, 2022]

    def test_provenance_tem_brasil_grupos_china(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        for chave in ["brasil", "grupos", "china", "mexico", "argentina"]:
            assert chave in prov, f"proveniência sem '{chave}'"

    def test_provenience_fechada(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["proveniencia_fechada"] is True
        assert "sha256_raw" in prov
        assert len(prov["sha256_raw"]) >= 3


class TestValoresBrasil:
    def test_brasil_matricula_inicio(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["brasil"]["matricula_inicio"] - 43.834) < 0.005

    def test_brasil_matricula_fim(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["brasil"]["matricula_fim"] - 61.000) < 0.005

    def test_brasil_delta_positivo(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["brasil"]["delta_matricula_pp"] > 0

    def test_brasil_cresc_pib(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["brasil"]["crescimento_medio_anual_pct"] + 0.149) < 0.005

    def test_brasil_rho_primeiras_diferencas(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["brasil"]["rho_primeiras_diferencas"] - 0.418) < 0.005
        assert prov["brasil"]["rho_primeiras_diferencas_p"] > 0.05
        assert prov["brasil"]["rho_primeiras_diferencas_n"] >= 9

    def test_brasil_residuo_positivo(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["brasil"]["residuo_ln_terciaria_relacao_global"] > 0


class TestValoresGrupos:
    def test_grupos_presentes(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        for nome in ["renda_media_asiatica", "eua", "europa_ocidental"]:
            assert nome in prov["grupos"], f"grupo '{nome}' ausente"

    def test_renda_media_asiatica_delta(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        g = prov["grupos"]["renda_media_asiatica"]
        assert abs(g["delta_matricula_pp"] - 13.455) < 0.005
        assert g["crescimento_medio_anual_pct"] > 0

    def test_eua_declinio(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        g = prov["grupos"]["eua"]
        assert g["delta_matricula_pp"] < 0, "EUA não registrou declínio"

    def test_europa_delta(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        g = prov["grupos"]["europa_ocidental"]
        assert abs(g["delta_matricula_pp"] - 13.199) < 0.005

    def test_china_crescimento(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert abs(prov["china"]["delta_matricula_pp"] - 42.272) < 0.005
        assert prov["china"]["crescimento_medio_anual_pct"] > 5.0

    def test_cobertura_desbalanceada_declarada(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        assert prov["grupos"]["eua"]["ano_inicio"] >= 2013


class TestValoresVizinhos:
    def test_mexico_na_provenance(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        m = prov["mexico"]
        assert abs(m["matricula_inicio"] - 29.350) < 0.005
        assert abs(m["delta_matricula_pp"] - 17.056) < 0.005
        assert m["crescimento_medio_anual_pct"] > 0

    def test_argentina_na_provenance(self):
        prov = json.loads(PROV.read_text(encoding="utf-8"))
        a = prov["argentina"]
        assert abs(a["matricula_inicio"] - 78.147) < 0.005
        assert abs(a["matricula_fim"] - 107.104) < 0.005
        assert abs(a["delta_matricula_pp"] - 28.957) < 0.005
        assert a["crescimento_medio_anual_pct"] < 0


class TestTabela:
    def test_tabela_existe(self):
        assert TABELA.exists(), "tabela8_brasil_comparado.csv ausente"

    def test_tabela_tem_linhas(self):
        linhas = TABELA.read_text(encoding="utf-8").strip().splitlines()
        assert len(linhas) >= 7, "tabela 8 sem as 7 unidades"


class TestSecaoNoArtigo:
    def test_secao_48_no_md(self):
        texto = MD.read_text(encoding="utf-8")
        assert "### 4.8 O caso brasileiro em perspectiva comparada" in texto, (
            "seção 4.8 ausente no MD"
        )

    def test_secao_48_no_tex(self):
        texto = LATEX.read_text(encoding="utf-8")
        assert "O caso brasileiro em perspectiva comparada" in texto, (
            "seção 4.8 ausente no TeX"
        )

    def test_tabela_8_no_md(self):
        texto = MD.read_text(encoding="utf-8")
        assert "Tabela 8" in texto, "referência à Tabela 8 ausente no MD"

    def test_anti_overclaim(self):
        texto_md = MD.read_text(encoding="utf-8")
        secao = texto_md.split("### 4.8")[1].split("### 4.9")[0]
        for termo in TERMOS_BLOQUEADOS:
            assert termo.lower() not in secao.lower(), (
                f"termo bloqueado na seção 4.8: '{termo}'"
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
        secao = texto_md.split("### 4.8")[1].split("### 4.9")[0]
        for v in re.findall(r"([−-]?\d+[.,]\d+)", secao):
            # "1.462" é separador de milhar (n = 1462), não decimal
            if "." in v and v.count(".") == 1:
                inteiro, frac = v.split(".")
                if len(frac) == 3:
                    v_norm = float(inteiro + frac)
                else:
                    v_norm = float(v.replace(",", ".").replace("−", "-"))
            else:
                v_norm = float(v.replace(",", ".").replace("−", "-"))
            assert any(abs(v_norm - x) < 0.005 for x in candidatos), (
                f"número '{v}' na seção 4.8 sem proveniência r418"
            )

    def test_linguagem_associativa(self):
        texto_md = MD.read_text(encoding="utf-8")
        secao = texto_md.split("### 4.8")[1].split("### 4.9")[0]
        assert "associ" in secao.lower() or "associação" in secao.lower(), (
            "seção 4.8 não usa linguagem associativa"
        )


class TestLatex:
    def test_pdf_existe(self):
        assert PDF.exists(), "latex/ARTIGO_RBEP_SUBMISSAO.pdf ausente"
