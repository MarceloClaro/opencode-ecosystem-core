# -*- coding: utf-8 -*-
"""Testes R420 — Apêndice A: Glossário de símbolos, códigos e abreviaturas.

Requisitos (SPEC-935-R420):
1. Seção "Apêndice A — Glossário de símbolos, códigos e abreviaturas" no MD
   canônico e espelhada no LaTeX, com subseções A.1 (símbolos estatísticos),
   A.2 (códigos de indicadores WDI/WGI) e A.3 (abreviaturas).
2. Conteúdo mínimo: símbolos ρ, Δ, ln, IC95%, p, p.p.; códigos
   SE.TER.ENRR, NY.GDP.PCAP.KD, NY.GDP.PCAP.KD.ZG, SE.XPD.TOTL.GD.ZS,
   GB.XPD.RSDV.GD.ZS, NV.IND.MANF.ZS, SP.URB.TOTL.IN.ZS; siglas WDI, WGI,
   PIB, LOOCV, FE, RF, ROC, GroupKFold, ML, ISO3, P&D, RBEP.
3. Anti-overclaim mantido no texto inteiro (MD e TeX): sem "AUC",
   "percentil", "validado", "inédito", "efeito causal", "causalidade",
   "impulsiona", "leva a", "16,06", "0,997", "0.997", "condição necessária".
4. LaTeX compilável; PDF presente; 0 Overfull/Underfull no log.
5. Suíte R408–R420 verde.
"""

from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
MD = AUDIT / "ARTIGO_RBEP_SUBMISSAO.md"
LATEX = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.tex"
PDF = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.pdf"

TERMOS_BLOQUEADOS = [
    "AUC", "percentil", "validado", "validada", "inédito", "inédita",
    "efeito causal", "causalidade", "impulsiona", "leva a",
    "16,06", "0,997", "0.997", "condição necessária", "condicao necessaria",
    "Qualis A1", "superhuman",
]

SIMBOLOS = [
    "ρ", "Δ", "ln", "IC95%", "p.p.", "D.P.", "H0", "H1", "WGI_media",
]

CODIGOS = [
    "NY.GDP.PCAP.KD", "NY.GDP.PCAP.KD.ZG", "SE.TER.ENRR",
    "SE.XPD.TOTL.GD.ZS", "GB.XPD.RSDV.GD.ZS", "NV.IND.MANF.ZS",
    "BX.KLT.DINV.WD.GD.ZS", "TX.VAL.TECH.MF.ZS", "SP.URB.TOTL.IN.ZS",
    "SP.DYN.LE00.IN", "SI.POV.GINI",
    "CC.EST", "GE.EST", "PV.EST", "RQ.EST", "RL.EST", "VA.EST",
]

ABREVIATURAS = [
    "WDI", "WGI", "PIB", "P&D", "LOOCV", "FE", "RF", "ROC",
    "GroupKFold", "ML", "ISO3", "RBEP", "IDE", "SHA-256", "UTC",
]


class TestApendiceNoMD:
    def test_apendice_existe(self):
        texto = MD.read_text(encoding="utf-8")
        assert "## Apêndice A — Glossário de símbolos, códigos e abreviaturas" in texto

    def test_subsecoes(self):
        texto = MD.read_text(encoding="utf-8")
        for sub in ["### A.1 Símbolos estatísticos",
                    "### A.2 Códigos de indicadores (WDI/WGI)",
                    "### A.3 Abreviaturas"]:
            assert sub in texto, f"subseção ausente: {sub}"

    def test_apendice_depois_das_referencias(self):
        texto = MD.read_text(encoding="utf-8")
        assert texto.index("## Referências") < texto.index("## Apêndice A")

    def test_simbolos_presentes(self):
        texto = MD.read_text(encoding="utf-8")
        ap = texto.split("## Apêndice A")[1]
        for s in SIMBOLOS:
            assert s in ap, f"símbolo ausente no apêndice: {s}"

    def test_codigos_presentes(self):
        texto = MD.read_text(encoding="utf-8")
        ap = texto.split("## Apêndice A")[1]
        for c in CODIGOS:
            assert c in ap, f"código ausente no apêndice: {c}"

    def test_abreviaturas_presentes(self):
        texto = MD.read_text(encoding="utf-8")
        ap = texto.split("## Apêndice A")[1]
        for a in ABREVIATURAS:
            assert a in ap, f"abreviatura ausente no apêndice: {a}"

    def test_anti_overclaim_md(self):
        texto = MD.read_text(encoding="utf-8")
        for termo in TERMOS_BLOQUEADOS:
            assert termo.lower() not in texto.lower(), (
                f"termo bloqueado presente no MD: '{termo}'"
            )


class TestApendiceNoTeX:
    def test_apendice_existe(self):
        texto = LATEX.read_text(encoding="utf-8")
        assert "Apêndice A" in texto

    def test_subsecoes(self):
        texto = LATEX.read_text(encoding="utf-8")
        for sub in ["A.1 Símbolos estatísticos",
                    "A.2 Códigos de indicadores (WDI/WGI)",
                    "A.3 Abreviaturas"]:
            assert sub in texto, f"subseção ausente no TeX: {sub}"

    def test_apendice_depois_das_referencias(self):
        texto = LATEX.read_text(encoding="utf-8")
        assert texto.index("WORLD BANK.") < texto.index("\\appendix")

    def test_codigos_presentes(self):
        texto = LATEX.read_text(encoding="utf-8")
        ap = texto.split("\\appendix")[1]
        for c in CODIGOS:
            assert c in ap, f"código ausente no apêndice TeX: {c}"

    def test_abreviaturas_presentes(self):
        texto = LATEX.read_text(encoding="utf-8")
        ap = texto.split("\\appendix")[1]
        for a in ABREVIATURAS:
            variante = "P\\&D" if a == "P&D" else a
            assert variante in ap, f"abreviatura ausente no apêndice TeX: {a}"

    def test_anti_overclaim_tex(self):
        texto = LATEX.read_text(encoding="utf-8")
        for termo in TERMOS_BLOQUEADOS:
            assert termo.lower() not in texto.lower(), (
                f"termo bloqueado presente no TeX: '{termo}'"
            )


class TestLatexCompilacao:
    def test_pdf_existe(self):
        assert PDF.exists(), "PDF não compilado"

    def test_latex_sem_overfull(self):
        log = LATEX.parent / "ARTIGO_RBEP_SUBMISSAO.log"
        if not log.exists():
            pytest.skip("log LaTeX indisponível")
        conteudo = log.read_text(encoding="utf-8", errors="replace")
        assert "Overfull" not in conteudo, "LaTeX com Overfull hbox/vbox (tabela fora das margens)"
        assert "Underfull" not in conteudo, "LaTeX com Underfull hbox/vbox"
