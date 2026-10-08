# -*- coding: utf-8 -*-
"""Tema e helpers PPTX neutros de conteúdo (SPEC-935-R706, AC6).

Paleta e construtores extraídos de gerar_pptx.py (legado TDAH, intacto):
fundo escuro, cards arredondados, barras proporcionais. Qualquer deck usa
estas primitivas com seu próprio conteúdo.

python-pptx é importado sob guarda (erro explícito se ausente).
"""
from __future__ import annotations


def _requer_pptx():
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from pptx.enum.shapes import MSO_SHAPE
    except ImportError as exc:
        raise RuntimeError(
            "python-pptx ausente: instale python-pptx para montar decks."
        ) from exc
    return Presentation, Inches, Pt, RGBColor, PP_ALIGN, MSO_SHAPE


PALETA = {
    "BG": "0A1F16", "CARD": "14291F", "BORDA": "3F9D71",
    "VERDE": "6FE3A5", "VERDE2": "A8F0C8", "OURO": "F2C46D",
    "TEXTO": "E9F5EE", "MUTED": "9DB8AA", "VERMELHO": "E07A5F",
}
FONTE = "Segoe UI"
LARGURA, ALTURA = 13.333, 7.5


def nova_apresentacao():
    Presentation, Inches, Pt, RGBColor, PP_ALIGN, MSO_SHAPE = _requer_pptx()
    prs = Presentation()
    prs.slide_width = Inches(LARGURA)
    prs.slide_height = Inches(ALTURA)
    return prs


def novo_slide(prs, fundo="BG"):
    from pptx.util import Inches
    from pptx.dml.color import RGBColor
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = RGBColor.from_string(PALETA[fundo])
    return s


def caixa_texto(slide, x, y, w, h, paragrafos, alinhamento="esquerda"):
    """paragrafos: [(texto, tamanho, cor_chave, negrito, italico), ...]."""
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    alvos = {"esquerda": PP_ALIGN.LEFT, "centro": PP_ALIGN.CENTER,
             "direita": PP_ALIGN.RIGHT, "justificado": PP_ALIGN.JUSTIFY}
    primeiro = True
    for texto, tam, cor, neg, ita in paragrafos:
        p = tf.paragraphs[0] if primeiro else tf.add_paragraph()
        primeiro = False
        p.alignment = alvos.get(alinhamento, PP_ALIGN.LEFT)
        r = p.add_run()
        r.text = texto
        r.font.name = FONTE
        r.font.size = Pt(tam)
        r.font.color.rgb = RGBColor.from_string(PALETA[cor])
        r.font.bold = neg
        r.font.italic = ita
    return tb


def cartao(slide, x, y, w, h, titulo=None, corpo=None, selo=None):
    """Card arredondado com selo/título/corpo opcionais. Retorna (shape, ids)."""
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import MSO_ANCHOR
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.07
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(PALETA["CARD"])
    sh.line.color.rgb = RGBColor.from_string(PALETA["BORDA"])
    sh.line.width = Pt(1.2)
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Pt(12)
    tf.margin_top = Pt(10)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    if selo:
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = selo + "  "
        r.font.name = FONTE
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor.from_string(PALETA["VERDE"])
        r.font.bold = True
    if titulo:
        p = tf.paragraphs[0] if (not selo and not tf.paragraphs[0].runs) else tf.add_paragraph()
        r = p.add_run()
        r.text = titulo
        r.font.name = FONTE
        r.font.size = Pt(17)
        r.font.color.rgb = RGBColor.from_string(PALETA["VERDE2"])
        r.font.bold = True
        p.space_after = Pt(4)
    if corpo:
        p = tf.add_paragraph()
        r = p.add_run()
        r.text = corpo
        r.font.name = FONTE
        r.font.size = Pt(12.5)
        r.font.color.rgb = RGBColor.from_string(PALETA["TEXTO"])
        p.line_spacing = 1.15
    return sh


def barra(slide, x, y, largura_max, pct, cor_chave="VERDE"):
    """Retângulo proporcional 0-100. Retorna o shape."""
    from pptx.util import Inches
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    pct = max(0, min(100, pct))
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                                Inches(largura_max * pct / 100.0), Inches(0.22))
    sh.adjustments[0] = 0.5
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(PALETA[cor_chave])
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh
