#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Minds and Machines submission DOCX files from Markdown."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT / "reference-custom.docx"

FILES = [
    ("MANUSCRIPT_MINDS_MACHINES.md", "MANUSCRIPT_MINDS_MACHINES.docx"),
    ("TITLE_PAGE.md", "TITLE_PAGE.docx"),
    ("COVER_LETTER.md", "COVER_LETTER.docx"),
    ("SUPPLEMENTARY_MATERIAL.md", "SUPPLEMENTARY_MATERIAL.docx"),
    ("LEITURA_PT.md", "LEITURA_PT.docx"),
    ("ARTIGO_PT.md", "ARTIGO_PT.docx"),
]


def convert() -> None:
    for source, target in FILES:
        subprocess.run(
            [
                "pandoc",
                str(ROOT / source),
                "-o",
                str(ROOT / target),
                f"--reference-doc={REFERENCE}",
            ],
            check=True,
        )


def set_properties() -> None:
    properties = {
        "MANUSCRIPT_MINDS_MACHINES.docx": (
            "",
            "",
            "The house that helps to think",
        ),
        "SUPPLEMENTARY_MATERIAL.docx": ("", "", "Supplementary Material"),
        "TITLE_PAGE.docx": (
            "Marcelo Claro Laranjeira",
            "Marcelo Claro Laranjeira",
            "Title Page",
        ),
        "COVER_LETTER.docx": (
            "Marcelo Claro Laranjeira",
            "Marcelo Claro Laranjeira",
            "Cover Letter",
        ),
        "LEITURA_PT.docx": (
            "Marcelo Claro Laranjeira",
            "Marcelo Claro Laranjeira",
            "Leitura em português — A casa que ajuda a pensar",
        ),
        "ARTIGO_PT.docx": (
            "Marcelo Claro Laranjeira",
            "Marcelo Claro Laranjeira",
            "A casa que ajuda a pensar",
        ),
    }
    for filename, (author, last_modified_by, title) in properties.items():
        doc = Document(ROOT / filename)
        doc.core_properties.author = author
        doc.core_properties.last_modified_by = last_modified_by
        doc.core_properties.title = title
        doc.core_properties.comments = ""
        doc.save(ROOT / filename)


def format_tables(path: Path) -> None:
    doc = Document(path)
    for table in doc.tables:
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        ncols = len(table.columns)
        header = table.rows[0].cells[0].text.strip().lower() if table.rows else ""
        if ncols == 4:
            if header == "mark":
                widths = [2.5, 5.0, 4.5, 4.0]
            else:
                widths = [3.6, 4.2, 5.0, 3.2]
        elif ncols == 5:
            if header == "move":
                widths = [2.3, 2.8, 3.6, 4.8, 2.5]
            else:
                widths = [2.9, 3.1, 3.5, 3.5, 3.0]
        else:
            widths = [16.0 / ncols] * ncols

        for i, column in enumerate(table.columns):
            column.width = Cm(widths[i])

        for row_index, row in enumerate(table.rows):
            tr_pr = row._tr.get_or_add_trPr()
            if tr_pr.find(qn("w:cantSplit")) is None:
                tr_pr.append(OxmlElement("w:cantSplit"))
            for i, cell in enumerate(row.cells):
                cell.width = Cm(widths[i])
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_after = Pt(2)
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        if row_index == 0:
                            run.font.bold = True

        tbl_pr = table._tbl.tblPr
        for old in tbl_pr.findall(qn("w:tblBorders")):
            tbl_pr.remove(old)
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            element = OxmlElement(f"w:{edge}")
            if edge in ("top", "bottom"):
                element.set(qn("w:val"), "single")
                element.set(qn("w:sz"), "6")
                element.set(qn("w:color"), "000000")
            elif edge == "insideH":
                element.set(qn("w:val"), "single")
                element.set(qn("w:sz"), "2")
                element.set(qn("w:color"), "BFBFBF")
            else:
                element.set(qn("w:val"), "nil")
            element.set(qn("w:space"), "0")
            borders.append(element)
        tbl_pr.append(borders)
    doc.save(path)


def add_bullets(path: Path, markdown_path: Path) -> None:
    markdown = markdown_path.read_text(encoding="utf-8")
    items = []
    for line in markdown.splitlines():
        if line.startswith("- "):
            items.append(line[2:].strip().replace("**", ""))

    doc = Document(path)
    paragraphs = list(doc.paragraphs)
    used: set[int] = set()

    for item in items:
        key = item[:50].lower()
        found = None
        for index, paragraph in enumerate(paragraphs):
            if index in used:
                continue
            if paragraph.text.lower().startswith(key[:35]):
                found = (index, paragraph)
                break
        if found is None:
            for index, paragraph in enumerate(paragraphs):
                if index in used:
                    continue
                if key[:25] in paragraph.text.lower():
                    found = (index, paragraph)
                    break
        if found is None:
            continue
        index, paragraph = found
        used.add(index)
        run = paragraph.add_run("• ")
        run.bold = False
        run.font.size = Pt(12)
        paragraph._p.insert(0, run._r)
        paragraph.paragraph_format.left_indent = Cm(0.75)
        paragraph.paragraph_format.first_line_indent = Cm(-0.5)
        paragraph.paragraph_format.space_after = Pt(3)

    doc.save(path)


def add_page_breaks(path: Path) -> None:
    doc = Document(path)
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text in {"Statements and Declarations", "References", "Referências"}:
            paragraph.paragraph_format.page_break_before = True
        if text.startswith(("Table ", "Tabela ")):
            paragraph.paragraph_format.keep_with_next = True
    doc.save(path)


def main() -> None:
    convert()
    set_properties()
    format_tables(ROOT / "MANUSCRIPT_MINDS_MACHINES.docx")
    format_tables(ROOT / "SUPPLEMENTARY_MATERIAL.docx")
    add_bullets(
        ROOT / "MANUSCRIPT_MINDS_MACHINES.docx",
        ROOT / "MANUSCRIPT_MINDS_MACHINES.md",
    )
    add_bullets(ROOT / "LEITURA_PT.docx", ROOT / "LEITURA_PT.md")
    add_bullets(ROOT / "ARTIGO_PT.docx", ROOT / "ARTIGO_PT.md")
    add_page_breaks(ROOT / "MANUSCRIPT_MINDS_MACHINES.docx")
    add_page_breaks(ROOT / "LEITURA_PT.docx")
    add_page_breaks(ROOT / "ARTIGO_PT.docx")
    format_tables(ROOT / "LEITURA_PT.docx")
    format_tables(ROOT / "ARTIGO_PT.docx")
    print("DOCX files built in", ROOT)


if __name__ == "__main__":
    main()
