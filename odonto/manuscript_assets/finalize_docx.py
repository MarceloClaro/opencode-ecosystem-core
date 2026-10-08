"""Finalise a pandoc draft into the journal-formatted DOCX.

Kept as a function with explicit arguments so that the English submission
manuscript and the author-facing PT-BR translation share one formatter instead
of two copies that can drift apart. Called with no arguments it reproduces the
original English behaviour exactly:

    python3 manuscript_assets/finalize_docx.py

With arguments it formats any other Markdown-derived draft:

    python3 manuscript_assets/finalize_docx.py <draft.docx> <out.docx> <lang>

`lang` selects only the language-dependent literals (article type line, the
ARTICLE INFO / ABSTRACT box headings, the keywords label, and the
Table/Figure caption prefixes). Everything else - page geometry, styles,
column widths - is language independent and comes from the journal template.
"""

import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "manuscript_assets" / "clean_draft.docx"
DEFAULT_EXAMPLE = ROOT / "Journal_of_Dentistry_Example.docx"
DEFAULT_TARGET = ROOT / "Journal_of_Dentistry_Example_OdontoCA.docx"

# Language-dependent literals only.
LANG = {
    "en": {
        "article_type": "Research article · secondary analysis and internal validation",
        "info_heading": "A R T I C L E  I N F O",
        "keywords_label": "Keywords:",
        "abstract_heading": "A B S T R A C T",
        "table_prefixes": ("Table 1.", "Table 2.", "Table 3."),
        "figure_prefixes": ("Figure 1.", "Figure 2.", "Figure 3."),
    },
    "pt": {
        "article_type": "Artigo de pesquisa · análise secundária e validação interna",
        "info_heading": "I N F O R M A Ç Õ E S   D O   A R T I G O",
        "keywords_label": "Palavras-chave:",
        "abstract_heading": "R E S U M O",
        "table_prefixes": ("Tabela 1.", "Tabela 2.", "Tabela 3."),
        "figure_prefixes": ("Figura 1.", "Figura 2.", "Figura 3."),
    },
}


def finalize(source: Path, example: Path, target: Path, lang: str = "en") -> Path:
    if lang not in LANG:
        raise SystemExit(f"unknown lang {lang!r}; expected one of {sorted(LANG)}")
    lit = LANG[lang]

    document = Document(source)
    model = Document(example)
    model_section = model.sections[0]

    for section in document.sections:
        section.page_width = model_section.page_width
        section.page_height = model_section.page_height
        section.left_margin = model_section.left_margin
        section.right_margin = model_section.right_margin
        section.top_margin = model_section.top_margin
        section.bottom_margin = model_section.bottom_margin

    for name in ("Normal", "Body Text", "First Paragraph"):
        style = document.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(10)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_after = Pt(3)
        style.paragraph_format.line_spacing = 1.10

    for name, size, bold, italic in (
        ("Heading 1", 18, False, False),
        ("Heading 2", 10, True, False),
        ("Heading 3", 10, True, True),
    ):
        style = document.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = bold
        style.font.italic = italic
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(7)
        style.paragraph_format.space_after = Pt(4)

    title = document.paragraphs[0]
    abstract_paragraphs = document.paragraphs[2:6]
    abstract_text = [paragraph.text for paragraph in abstract_paragraphs]
    keywords = document.paragraphs[6].text.split(":", 1)[1].strip().rstrip(".")
    to_remove = document.paragraphs[1:7]
    title.paragraph_format.space_after = Pt(8)
    article_type = title.insert_paragraph_before(lit["article_type"])
    article_type.style = document.styles["Normal"]
    article_type.paragraph_format.space_after = Pt(3)

    abstract_table = document.add_table(rows=1, cols=2)
    abstract_table.autofit = False
    abstract_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for column, width in zip(abstract_table.columns, (Inches(1.65), Inches(5.45))):
        column.width = width
    for cell, width in zip(abstract_table.rows[0].cells, (Inches(1.65), Inches(5.45))):
        cell.width = width
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP

    left, right = abstract_table.rows[0].cells
    left.text = ""
    heading = left.paragraphs[0]
    heading.add_run(lit["info_heading"]).bold = True
    heading.paragraph_format.space_after = Pt(7)
    left.add_paragraph(lit["keywords_label"]).runs[0].bold = True
    for term in keywords.split(";"):
        paragraph = left.add_paragraph(term.strip())
        paragraph.paragraph_format.space_after = Pt(1)

    right.text = ""
    heading = right.paragraphs[0]
    heading.add_run(lit["abstract_heading"]).bold = True
    heading.paragraph_format.space_after = Pt(7)
    for text in abstract_text:
        paragraph = right.add_paragraph()
        label, body = text.split(":", 1)
        paragraph.add_run(label + ":").bold = True
        paragraph.add_run(body)
        paragraph.paragraph_format.space_after = Pt(3)
        paragraph.paragraph_format.line_spacing = 1.05

    title._p.addnext(abstract_table._tbl)
    for paragraph in to_remove:
        paragraph._element.getparent().remove(paragraph._element)

    for paragraph in document.paragraphs:
        if paragraph.text.startswith(lit["table_prefixes"]):
            paragraph.paragraph_format.keep_with_next = True
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if paragraph.text.startswith(lit["figure_prefixes"]):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

    table_widths = [
        [Inches(2.03), Inches(0.75), Inches(1.58), Inches(2.84)],
        [Inches(1.80), Inches(1.52), Inches(1.45), Inches(1.45), Inches(0.98)],
        [Inches(2.75), Inches(1.00), Inches(1.15), Inches(1.10), Inches(1.20)],
    ]

    for table, widths in zip(document.tables[1:], table_widths):
        table.autofit = False
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for column, width in zip(table.columns, widths):
            column.width = width
        for row in table.rows:
            properties = row._tr.get_or_add_trPr()
            properties.append(OxmlElement("w:cantSplit"))
            for cell, width in zip(row.cells, widths):
                cell.width = width
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_after = Pt(1)
        table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))

    document.core_properties.author = ""
    document.core_properties.last_modified_by = ""
    document.save(target)
    return target


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(finalize(DEFAULT_SOURCE, DEFAULT_EXAMPLE, DEFAULT_TARGET, "en"))
        return 0
    if len(argv) != 3:
        raise SystemExit("usage: finalize_docx.py [draft.docx out.docx lang]")
    draft, out, lang = argv
    print(finalize(Path(draft), DEFAULT_EXAMPLE, Path(out), lang))
    return 0


if __name__ == "__main__":
    sys.exit(main())
