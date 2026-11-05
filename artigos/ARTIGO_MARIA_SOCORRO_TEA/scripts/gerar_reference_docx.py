#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera templates/abnt_reference.docx a partir do reference.docx do Pandoc."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "templates" / "base.docx"
DST = BASE / "templates" / "abnt_reference.docx"


def fonte(style, tamanho=12, negrito=None, italico=None):
    style.font.name = "Times New Roman"
    style.font.size = Pt(tamanho)
    if negrito is not None:
        style.font.bold = negrito
    if italico is not None:
        style.font.italic = italico
    # Garante a fonte para caracteres latinos acentuados.
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
    if rfonts is not None:
        for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
            rfonts.set(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}" + attr,
                "Times New Roman",
            )


def paragrafo(style, *, alinhamento=None, recuo=None, espacamento=None,
              antes=0, depois=0, manter=False):
    pf = style.paragraph_format
    if alinhamento is not None:
        pf.alignment = alinhamento
    if recuo is not None:
        pf.first_line_indent = recuo
    if espacamento is not None:
        pf.line_spacing = espacamento
    pf.space_before = Pt(antes)
    pf.space_after = Pt(depois)
    if manter:
        pf.keep_with_next = True


doc = Document(str(SRC))

# Página A4 e margens ABNT: 3 cm superior/esquerda, 2 cm inferior/direita.
sec = doc.sections[0]
sec.page_width = Cm(21)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(3)
sec.left_margin = Cm(3)
sec.bottom_margin = Cm(2)
sec.right_margin = Cm(2)

# Corpo.
for nome in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if nome in doc.styles:
        st = doc.styles[nome]
        fonte(st, 12)
        paragrafo(st, alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY, recuo=Cm(1.25),
                  espacamento=1.5)

# Título e autoria.
if "Title" in doc.styles:
    st = doc.styles["Title"]
    fonte(st, 12, negrito=True)
    paragrafo(st, alinhamento=WD_ALIGN_PARAGRAPH.CENTER, recuo=Cm(0),
              espacamento=1.5, depois=12)
if "Author" in doc.styles:
    st = doc.styles["Author"]
    fonte(st, 12)
    paragrafo(st, alinhamento=WD_ALIGN_PARAGRAPH.CENTER, recuo=Cm(0),
              espacamento=1.5, depois=18)

# Seções.
if "Heading 1" in doc.styles:
    st = doc.styles["Heading 1"]
    fonte(st, 12, negrito=True)
    paragrafo(st, alinhamento=WD_ALIGN_PARAGRAPH.LEFT, recuo=Cm(0),
              espacamento=1.5, antes=18, depois=12, manter=True)
if "Heading 2" in doc.styles:
    st = doc.styles["Heading 2"]
    fonte(st, 12, negrito=True)
    paragrafo(st, alinhamento=WD_ALIGN_PARAGRAPH.LEFT, recuo=Cm(0),
              espacamento=1.5, antes=12, depois=6, manter=True)

# Citação longa: recuo de 4 cm, 10 pt, espaço simples.
for nome in ("Quote", "Block Text"):
    if nome in doc.styles:
        st = doc.styles[nome]
        fonte(st, 10)
        pf = st.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.left_indent = Cm(4)
        pf.right_indent = Cm(0)
        pf.first_line_indent = Cm(0)
        pf.line_spacing = 1.0
        pf.space_before = Pt(6)
        pf.space_after = Pt(6)

doc.save(str(DST))
print(f"OK: {DST}")
