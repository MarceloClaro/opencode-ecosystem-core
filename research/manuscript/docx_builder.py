# -*- coding: utf-8 -*-
"""Conversor DOCX genérico (SPEC-935-R706, AC3).

Lê QUALQUER workspace do motor: ordem dos módulos via \\input do main.tex,
citações via .aux, referências via .bbl compilado e tabelas via ambientes
tabular — nada de conteúdo codificado.

python-docx é importado sob guarda (erro explícito se ausente).
"""
from __future__ import annotations

import os
import re

from research.manuscript import texparse


def _requer_docx():
    try:
        from docx import Document
        from docx.shared import Pt, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
    except ImportError as exc:
        raise RuntimeError(
            "python-docx ausente: instale python-docx para converter DOCX."
        ) from exc
    return Document, Pt, Cm, WD_ALIGN_PARAGRAPH, WD_TABLE_ALIGNMENT, qn, OxmlElement


def _fonte(run, nome="Times New Roman", tamanho=12, negrito=False, italico=False):
    run.font.name = nome
    run.font.size = tamanho
    run.bold = negrito
    run.italic = italico
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(_qn("w:rFonts"))
    if rfonts is None:
        rfonts = _OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(_qn("w:ascii"), nome)
    rfonts.set(_qn("w:hAnsi"), nome)


_QN = {}
def _qn(tag):
    return _QN["qn"](tag)

def _OxmlElement(tag):
    return _QN["OxmlElement"](tag)


def _runs(p, texto, Pt, tamanho=12):
    for trecho, neg, ita in texparse.runs(texto):
        run = p.add_run(trecho)
        _fonte(run, tamanho=tamanho, negrito=neg, italico=ita)


def _ordem_modulos(diretorio: str) -> list[str]:
    with open(os.path.join(diretorio, "main.tex"), encoding="utf-8") as fh:
        return re.findall(r"\\input\{([^}]+)\}", fh.read())


def build_docx(diretorio: str, saida: str) -> dict:
    """Converte workspace em DOCX ABNT. Retorna {saida, paragrafos, tabelas}."""
    (Document, Pt, Cm, WD_ALIGN_PARAGRAPH, WD_TABLE_ALIGNMENT,
     qn, OxmlElement) = _requer_docx()
    _QN["qn"] = qn
    _QN["OxmlElement"] = OxmlElement

    aux_path = os.path.join(diretorio, "main.aux")
    citas = texparse.Citacoes(
        open(aux_path, encoding="utf-8", errors="ignore").read()
        if os.path.isfile(aux_path) else "")

    def expandir(texto: str) -> str:
        return citas.expandir(texto)

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.paragraph_format.line_spacing = 1.5
    st.paragraph_format.space_after = Pt(0)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.left_margin = Cm(3), Cm(3)
    sec.bottom_margin, sec.right_margin = Cm(2), Cm(2)

    sec_num, sub_num = 0, 0
    n_par, n_tab = 0, 0

    def corpo(texto, recuo=True, central=False):
        nonlocal n_par
        p = doc.add_paragraph()
        p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if central
                       else WD_ALIGN_PARAGRAPH.JUSTIFY)
        pf = p.paragraph_format
        if recuo and not central:
            pf.first_line_indent = Cm(1.25)
        _runs(p, expandir(texto), Pt)
        n_par += 1

    def tabela(legenda, cabec, linhas):
        nonlocal n_tab
        pc = doc.add_paragraph()
        pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = pc.add_run(legenda)
        _fonte(r, tamanho=Pt(12), negrito=True)
        t = doc.add_table(rows=1 + len(linhas), cols=max(1, len(cabec)))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, h in enumerate(cabec):
            cel = t.rows[0].cells[j]
            cel.text = ""
            pr = cel.paragraphs[0]
            rr = pr.add_run(texparse.inline(texparse.deescape(h)))
            _fonte(rr, tamanho=Pt(12), negrito=True)
            pr.paragraph_format.line_spacing = 1.0
        for i, lin in enumerate(linhas, 1):
            for j in range(len(cabec)):
                cel = t.rows[i].cells[j]
                cel.text = ""
                pr = cel.paragraphs[0]
                for trecho, neg, ita in texparse.runs(lin[j] if j < len(lin) else ""):
                    rr = pr.add_run(trecho)
                    _fonte(rr, tamanho=Pt(12), negrito=neg, italico=ita)
                pr.paragraph_format.line_spacing = 1.0
        n_tab += 1

    for modulo in _ordem_modulos(diretorio):
        if "preambulo" in modulo:
            continue
        caminho = os.path.join(diretorio, modulo if modulo.endswith(".tex") else modulo + ".tex")
        if modulo == "modulos/09-referencias" or modulo.endswith("09-referencias"):
            continue  # referências vêm do .bbl ao final
        if not os.path.isfile(caminho):
            continue
        eh_capa = "capa" in os.path.basename(caminho).lower()
        with open(caminho, encoding="utf-8") as fh:
            texto = fh.read()
        for bloco in texparse.iter_blocos(texto):
            kind = bloco[0]
            if kind == "secao":
                sec_num += 1
                sub_num = 0
                p = doc.add_paragraph()
                r = p.add_run(f"{sec_num} {texparse.inline(texparse.deescape(bloco[1])).upper()}")
                _fonte(r, tamanho=Pt(12), negrito=True)
                p.paragraph_format.space_before = Pt(18)
                n_par += 1
            elif kind == "subsecao":
                sub_num += 1
                p = doc.add_paragraph()
                r = p.add_run(f"{sec_num}.{sub_num} {texparse.inline(texparse.deescape(bloco[1]))}")
                _fonte(r, tamanho=Pt(12), negrito=True)
                p.paragraph_format.space_before = Pt(12)
                n_par += 1
            elif kind == "item":
                p = doc.add_paragraph()
                pf = p.paragraph_format
                pf.left_indent = Cm(1.9)
                _runs(p, expandir(bloco[1]), Pt)
                n_par += 1
            elif kind == "centro":
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _runs(p, expandir(bloco[1]), Pt)
                for r in p.runs:
                    r.bold = True
                n_par += 1
            elif kind == "quadro":
                _, legenda, corpo_tab = bloco
                cabec, linhas = texparse.parse_tabular(corpo_tab)
                if cabec:
                    tabela(texparse.inline(texparse.deescape(legenda)), cabec, linhas)
            elif kind == "para":
                if eh_capa:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    _runs(p, expandir(bloco[1]), Pt)
                    n_par += 1
                else:
                    corpo(bloco[1])

    # Referências: do .bbl compilado (fallback honesto sem .bbl)
    p = doc.add_paragraph()
    r = p.add_run("REFERÊNCIAS")
    _fonte(r, tamanho=Pt(12), negrito=True)
    p.paragraph_format.space_before = Pt(18)
    n_par += 1
    bbl_path = os.path.join(diretorio, "main.bbl")
    if os.path.isfile(bbl_path):
        with open(bbl_path, encoding="utf-8", errors="ignore") as fh:
            refs = texparse.parse_bbl(fh.read())
    else:
        refs = ["[Compile o LaTeX (pdflatex + bibtex) para gerar as referências.]"]
    for ref in refs:
        pr = doc.add_paragraph()
        pr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pr.paragraph_format.line_spacing = 1.0
        pr.paragraph_format.space_after = Pt(12)
        for trecho, neg, ita in texparse.runs(ref):
            rr = pr.add_run(trecho)
            _fonte(rr, tamanho=Pt(12), negrito=neg, italico=ita)
        n_par += 1

    doc.save(saida)
    return {"saida": saida, "paragrafos": n_par, "tabelas": n_tab,
            "referencias": len(refs)}
