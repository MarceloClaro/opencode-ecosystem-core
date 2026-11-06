#!/usr/bin/env python3
"""Pós-processamento do DOCX para regras cultas da escrita PT-BR.

Aplica:
  1. Indentação de primeira linha (1,25 cm) em parágrafos do corpo
  2. Letra capitular no primeiro parágrafo do prefácio
  3. Ajustes tipográficos finos
"""

import re
import sys
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, Twips
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

BASE = Path(__file__).resolve().parent.parent
DOCX_PATH = BASE / "main.docx"
MD_PATH = BASE / "misc" / "main_export.md"

FIRST_LINE_INDENT = Cm(1.25)
DROP_CAP_LINES = 3  # altura da capitular em linhas
CAPITULAR_FONT_SIZE = Pt(28)  # tamanho da letra capitular


def find_preface_para_index(doc: Document) -> int:
    """Find the paragraph index of the preface first paragraph.
    
    Looks for 'Nota do Autor' heading, then returns the next paragraph.
    Falls back to searching for the DROP_CAP marker.
    """
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        # Find DROP_CAP marker
        if '{DROP_CAP:' in text:
            return i
    return -1


def find_dropcap_paragraphs(doc: Document) -> list[tuple[int, str]]:
    """Find all paragraphs with DROP_CAP markers (using ☙DC<X>❧).
    
    Returns list of (paragraph_index, character) tuples.
    """
    LDC = '\u2619'  # ☙
    RDC = '\u2767'  # ❧
    results = []
    for i, para in enumerate(doc.paragraphs):
        text = para.text
        # Look for ☙DC<X>❧ pattern
        m = re.search(LDC + r'DC([A-Za-zÀ-ÿ])' + RDC, text)
        if m:
            results.append((i, m.group(1)))
    return results


def add_drop_cap(paragraph, drop_char: str):
    """Add a proper drop cap to a paragraph using XML manipulation.
    
    This creates a Word VML/textbox-based drop cap that wraps text around it.
    """
    # Get current paragraph text
    full_text = paragraph.text
    
    # Find and remove the DROP_CAP marker
    LDC = '\u2619'  # ☙
    RDC = '\u2767'  # ❧
    clean_text = re.sub(LDC + r'DC[A-Za-zÀ-ÿ]' + RDC, '', full_text)
    
    # Clear paragraph
    p = paragraph._element
    for r in p.findall(qn('w:r')):
        p.remove(r)
    
    # Clear paragraph properties to rebuild
    pPr = p.find(qn('w:pPr'))
    
    # Create drop cap frame in paragraph properties
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        p.insert(0, pPr)
    
    # Add frame for drop cap
    frame = OxmlElement('w:frame')
    frame.set(qn('w:dropCap'), 'drop')      # Drop cap style
    frame.set(qn('w:lines'), str(DROP_CAP_LINES))  # Height in lines
    frame.set(qn('w:w'), '0')               # Let Word auto-calculate width
    frame.set(qn('w:h'), '0')               # Auto height
    frame.set(qn('w:hSpace'), '72')         # 0.05in = ~3.6pt space to right
    frame.set(qn('w:vSpace'), '0')          # Vertical space
    frame.set(qn('w:wrap'), 'around')       # Text wraps around
    frame.set(qn('w:vanchor'), 'paragraph') # Anchor to paragraph
    frame.set(qn('w:halign'), 'left')       # Left alignment
    pPr.append(frame)
    
    # Add the drop cap character as the first run (large font)
    drop_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    # Set font size for drop cap
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(CAPITULAR_FONT_SIZE.pt * 2)))  # half-points
    rPr.append(sz)
    
    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), str(int(CAPITULAR_FONT_SIZE.pt * 2)))
    rPr.append(szCs)
    
    # Set bold
    b = OxmlElement('w:b')
    rPr.append(b)
    
    drop_run.append(rPr)
    drop_text = OxmlElement('w:t')
    drop_text.set(qn('xml:space'), 'preserve')
    drop_text.text = drop_char
    drop_run.append(drop_text)
    
    # Find where to insert the drop run
    first_run = p.find(qn('w:r'))
    if first_run is not None:
        p.insert(p.index(first_run), drop_run)
    else:
        p.append(drop_run)
    
    # Re-add the rest of the paragraph text (may need to handle first run content)
    # The remaining text should be added after the drop cap
    # Split where the drop char appears in the original
    rest_text = clean_text
    
    if rest_text:
        rest_run = OxmlElement('w:r')
        rest_text_elem = OxmlElement('w:t')
        rest_text_elem.set(qn('xml:space'), 'preserve')
        rest_text_elem.text = rest_text
        rest_run.append(rest_text_elem)
        p.append(rest_run)


def apply_first_line_indent(doc: Document):
    """Apply first-line indent to body paragraphs.
    
    Skips:
      - Headings (Heading 1-4)
      - Title page
      - TOC entries
      - Empty paragraphs
      - Table of Contents
      - List items
    """
    # Styles that should not be indented
    heading_styles = ['Heading 1', 'Heading 2', 'Heading 3', 'Heading 4',
                      'heading 1', 'heading 2', 'heading 3']
    skip_style_prefixes = ['heading', 'toc', 'titl', 'subtitl', 'abstract',
                          'quote', 'blockquote']
    
    # Count of indented paragraphs
    indented = 0
    skipped = 0
    
    for para in doc.paragraphs:
        style_name = para.style.name.lower() if para.style else ''
        text = para.text.strip()
        
        # Skip conditions
        if not text:
            skipped += 1
            continue
        if any(style_name.startswith(p) for p in skip_style_prefixes):
            skipped += 1
            continue
        if para.style.name in heading_styles:
            skipped += 1
            continue
        
        # Skip if style is a heading variant or TOC
        if 'heading' in style_name or 'toc' in style_name:
            skipped += 1
            continue
        
        # Skip paragraphs that are part of lists
        numPr = para._element.find(qn('w:pPr'))
        if numPr is not None and numPr.find(qn('w:numPr')) is not None:
            skipped += 1
            continue
        
        # Check if paragraph is a center-aligned section (epilogue, separators)
        if para.alignment is not None and para.alignment.name == 'CENTER':
            skipped += 1
            continue
        
        # Skip horizontal rule paragraphs (contains only ---)
        if text == '---' or text.startswith('---'):
            skipped += 1
            continue
        
        # Skip TOC entries (lines that look like "Fragment-XX ... 3")
        if re.match(r'^[A-Z]+-\d+\s', text):
            skipped += 1
            continue
        
        # Apply first-line indent
        para.paragraph_format.first_line_indent = FIRST_LINE_INDENT
        indented += 1
    
    return indented, skipped


def cleanup_docx(doc: Document):
    """Clean up common DOCX issues."""
    # Remove empty paragraphs at document start
    while doc.paragraphs and not doc.paragraphs[0].text.strip():
        p = doc.paragraphs[0]._element
        p.getparent().remove(p)
    
    # Set default paragraph spacing
    for para in doc.paragraphs:
        if para.text.strip():
            # Ensure spacing is reasonable
            if para.paragraph_format.space_before is None:
                para.paragraph_format.space_before = Pt(0)
            if para.paragraph_format.space_after is None:
                para.paragraph_format.space_after = Pt(4)


def main():
    print("📝 Pós-processando DOCX...")
    
    if not DOCX_PATH.exists():
        print(f"❌ DOCX não encontrado: {DOCX_PATH}")
        print("   Execute primeiro: python3 misc/export_docx.py")
        sys.exit(1)
    
    doc = Document(str(DOCX_PATH))
    
    # ── Step 1: Apply first-line indent ──
    print("   Aplicando indentação de primeira linha (1,25 cm)...")
    indented, skipped = apply_first_line_indent(doc)
    print(f"   → {indented} parágrafos indentados, {skipped} ignorados")
    
    # ── Step 2: Add drop cap ──
    print("   Adicionando letra capitular no prefácio...")
    drop_paras = find_dropcap_paragraphs(doc)
    if drop_paras:
        for idx, char in drop_paras:
            para = doc.paragraphs[idx]
            # Remove indent from drop cap paragraph
            para.paragraph_format.first_line_indent = Cm(0)
            add_drop_cap(para, char)
            print(f"   → Capitular '{char}' no parágrafo {idx}")
    else:
        print("   ⚠ Nenhum marcador DROP_CAP encontrado. Verificar Nota do Autor.")
    
    # ── Step 3: Cleanup ──
    cleanup_docx(doc)
    
    # ── Save ──
    doc.save(str(DOCX_PATH))
    size = DOCX_PATH.stat().st_size
    print(f"\n✅ DOCX atualizado: {DOCX_PATH} ({size/1024:.1f} KB)")


if __name__ == '__main__':
    main()
