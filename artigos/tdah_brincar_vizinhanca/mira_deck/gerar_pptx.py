#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador PPTX do deck MIRA — formatação espelhada do deck HTML + animações
nativas do PowerPoint (entrada Fade escalonada por shape + transição Fade).

Limite honesto: animações CSS customizadas (contadores numéricos, barras
crescendo, seta desenhando) não existem 1:1 no PPTX — são substituídas por
efeitos de entrada nativos equivalentes. O deck HTML continua sendo a versão
totalmente animada.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml

# ---------------------------------------------------------------- paleta
BG      = RGBColor.from_string("0A1F16")
CARD    = RGBColor.from_string("14291F")
CARD2   = RGBColor.from_string("1A352A")
BORDA   = RGBColor.from_string("3F9D71")
VERDE   = RGBColor.from_string("6FE3A5")
VERDE2  = RGBColor.from_string("A8F0C8")
OURO    = RGBColor.from_string("F2C46D")
TEXTO   = RGBColor.from_string("E9F5EE")
MUTED   = RGBColor.from_string("9DB8AA")
VERMELHO= RGBColor.from_string("E07A5F")
FONT    = "Segoe UI"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

# ---------------------------------------------------------------- helpers
def add_slide():
    s = prs.slides.add_slide(blank)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    return s

def txbox(s, x, y, w, h):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Pt(4)
    tf.margin_top = tf.margin_bottom = Pt(2)
    return tb, tf

def run(p, text, size, color, bold=False, italic=False):
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.italic = italic
    return r

def kicker(s, text):
    tb, tf = txbox(s, 0.9, 0.55, 11.5, 0.45)
    p = tf.paragraphs[0]
    run(p, text.upper(), 13, OURO, bold=True)

def titulo(s, text, y=1.05):
    tb, tf = txbox(s, 0.9, y, 11.5, 0.95)
    p = tf.paragraphs[0]
    run(p, text, 30, VERDE, bold=True)
    return tb

def card(s, x, y, w, h, num=None, head=None, body=None):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.07
    sh.fill.solid(); sh.fill.fore_color.rgb = CARD
    sh.line.color.rgb = BORDA; sh.line.width = Pt(1.2)
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Pt(12)
    tf.margin_top = Pt(10); tf.margin_bottom = Pt(8)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    first = True
    if num:
        p = tf.paragraphs[0]; first = False
        run(p, num + "  ", 13, VERDE, bold=True)
    if head:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        run(p, head, 17, VERDE2, bold=True)
        p.space_after = Pt(4)
    if body:
        p = tf.add_paragraph() if not first else tf.paragraphs[0]
        run(p, body, 12.5, TEXTO)
        p.line_spacing = 1.15
    return sh

def aviso(s, text, y=6.15):
    tb, tf = txbox(s, 0.9, y, 11.5, 0.95)
    p = tf.paragraphs[0]
    run(p, "⚠ " + text, 12.5, OURO)
    p.line_spacing = 1.1
    return tb

def relogio(s, tempo):
    tb, tf = txbox(s, 11.3, 7.0, 1.75, 0.4)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    run(p, "⏱ " + tempo + " sugeridos", 11, OURO)

# ---------------------------------------------------------------- animações
_id = [100]
def _nid():
    _id[0] += 1
    return _id[0]

NS_P = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'

def fade_entrance(slide, spids_delays):
    """Entrada Fade (presetID 10) com delays; XML de timing nativo do PPT."""
    if not spids_delays:
        return
    sld = slide._element
    # remove timing existente
    for t in sld.findall(qn('p:timing')):
        sld.remove(t)
    parts = []
    for spid, delay in spids_delays:
        c1 = _nid(); c2 = _nid(); c3 = _nid(); c4 = _nid()
        parts.append(
            '<p:par><p:cTn id="{c1}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
            '<p:childTnLst><p:par><p:cTn id="{c2}" fill="hold"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
            '<p:childTnLst><p:par><p:cTn id="{c3}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" nodeType="clickEffect">'
            '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            '<p:set><p:cBhvr><p:cTn id="{c4}" dur="400" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            '<p:to><p:strVal val="visible"/></p:to></p:set>'
            '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
            '</p:childTnLst></p:cTn></p:par>'.format(c1=c1, c2=c2, c3=c3, c4=c4, spid=spid, delay=delay)
        )
    seq_id = _nid(); root_id = _nid()
    timing = (
        '<p:timing {ns}><p:tnLst><p:par><p:cTn id="{root}" dur="indefinite" restart="never" nodeType="tmRoot">'
        '<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="{seq}" dur="indefinite" nodeType="mainSeq">'
        '<p:childTnLst>{parts}</p:childTnLst></p:cTn>'
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
    ).format(ns=NS_P, root=root_id, seq=seq_id, parts="".join(parts))
    sld.append(parse_xml(timing))

def fade_transition(slide):
    sld = slide._element
    for t in sld.findall(qn('p:transition')):
        sld.remove(t)
    trans = parse_xml('<p:transition %s spd="med"><p:fade/></p:transition>' % NS_P)
    cm = sld.find(qn('p:clrMapOvr'))
    if cm is not None:
        cm.addnext(trans)
    else:
        sld.insert(0, trans)

# ================================================================ SLIDE 1 - CAPA
s = add_slide()
sh1 = []
tb, tf = txbox(s, 1.0, 1.3, 11.3, 1.1)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "DEFESA ACADÊMICA · RELATO DE EXPERIÊNCIA CLÍNICA", 14, OURO, bold=True)
sh1.append(tb.shape_id)
tb, tf = txbox(s, 0.7, 1.95, 11.9, 2.0)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "DA SALA PARA A RUA", 44, TEXTO, bold=True)
p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
run(p2, "Brincar livre na vizinhança e atenuação da intensidade de sintomas de TDAH em pré-escolar", 24, VERDE, bold=True)
sh1.append(tb.shape_id)
tb, tf = txbox(s, 1.0, 4.05, 11.3, 0.7)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "Uma leitura humanista de um caso clínico à luz da literatura sobre natureza, pares e autorregulação", 15, MUTED)
sh1.append(tb.shape_id)
tb, tf = txbox(s, 1.0, 5.0, 11.3, 1.1)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "Ana Gessyca de Sousa Fernandes · Isabelly Rosa Cavalcante · Nadielle Darc Batista Dias", 14, MUTED)
p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
run(p2, "Winny Ketlyn Sabóia Teixeira · Marta Tainá Silva de Sousa", 14, MUTED)
sh1.append(tb.shape_id)
tb, tf = txbox(s, 1.0, 6.35, 11.3, 0.6)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "Discentes do curso de graduação em Psicologia · Orientadora: [A PREENCHER] · 2026", 13, MUTED)
sh1.append(tb.shape_id)
fade_entrance(s, [(sp, 150 + i * 160) for i, sp in enumerate(sh1)]); fade_transition(s)

# ================================================================ SLIDE 2 - ROTEIRO
s = add_slide(); kicker(s, "Roteiro"); titulo(s, "O que vamos apresentar (18 min + arguição)")
itens = [
    "1. O caso que disparou tudo — a vinheta clínica (2 min)",
    "2. Pergunta, lacuna e objetivos (2 min)",
    "3. Método: revisão integrativa, ética e critérios de invalidação (3 min)",
    "4. Evidências: seis âncoras em três eixos (4 min)",
    "5. O caso à luz da literatura — o que dá para afirmar (3 min)",
    "6. Limitações, agenda e implicações práticas (2 min)",
    "7. Conclusão e abertura para a banca (2 min)",
]
shapes = []
for i, it in enumerate(itens):
    tb, tf = txbox(s, 1.2, 2.05 + i * 0.68, 11.0, 0.6)
    p = tf.paragraphs[0]
    run(p, it.split(" — ")[0] + " — ", 16, VERDE2, bold=True) if "—" in it else run(p, it, 16, TEXTO)
    if "—" in it:
        run(p, it.split(" — ", 1)[1], 16, TEXTO)
    shapes.append(tb.shape_id)
fade_entrance(s, [(sp, 150 + i * 150) for i, sp in enumerate(shapes)]); fade_transition(s)

# ================================================================ SLIDE 3 - VINHETA
s = add_slide(); kicker(s, "Ponto de partida"); titulo(s, "Um caso que a escuta clínica não ignorou")
c1 = card(s, 0.9, 1.95, 5.6, 1.7, head="Antes da mudança",
          body="M., 5 anos, laudo de TDAH misto. Hiperatividade grave: não conseguia permanecer nem diante da televisão. Em sessão: trocas rápidas de brinquedos, fala acelerada, poucos pares.")
c2 = card(s, 6.85, 1.95, 5.6, 1.7, head="Depois da mudança",
          body="A família mudou de endereço. A criança passou a brincar todos os dias na vizinhança com crianças de idade próxima. Mãe e terapeuta passaram a notá-la bem mais tranquila — inclusive nas sessões.")
tb, tf = txbox(s, 0.9, 3.85, 11.5, 0.5)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "[ TV sem conseguir parar ]   ────▶   [ Sol + crianças pulando: brincar diário na vizinhança ]", 15, MUTED)
a = aviso(s, "Ética: nome fictício (M.), anonimização completa, TCLE do responsável e assentimento lúdico [A ANEXAR]. Uso de medicação: NÃO DECLARADO pela família até o fechamento — registrado literalmente, sem presumir ausência.", y=4.6)
fade_entrance(s, [(c1.shape_id, 200), (c2.shape_id, 450), (tb.shape_id, 750), (a.shape_id, 1100)]); fade_transition(s)

# ================================================================ SLIDE 4 - PERGUNTA + LACUNAS
s = add_slide(); kicker(s, "Problema de pesquisa"); titulo(s, "O que a literatura já sabe sobre o que aconteceu com M.?")
tb, tf = txbox(s, 0.9, 2.0, 11.5, 1.3)
p = tf.paragraphs[0]
run(p, "O que a literatura nacional e internacional, de 2004 a 2026, descreve sobre a relação entre brincar livre em espaços externos ou na vizinhança e a atenuação da intensidade de sintomas de TDAH em pré-escolares — e como isso dialoga com a clínica humanista?", 16, TEXTO)
p.line_spacing = 1.2
l1 = card(s, 0.9, 3.55, 3.7, 2.2, num="LACUNA 1", head="Faixa etária", body="Quase todos os estudos cobrem escolares de 7–12 anos. Pouquíssimos com 5 anos.")
l2 = card(s, 4.85, 3.55, 3.7, 2.2, num="LACUNA 2", head="Cenário", body="Pesquisas usam parques e programas planejados; o brincar cotidiano de rua/vizinhança é raro na literatura.")
l3 = card(s, 8.8, 3.55, 3.7, 2.2, num="LACUNA 3", head="Olhar", body="Nenhum estudo identificado sob a ótica humanista brasileira (Abordagem Centrada na Pessoa).")
fade_entrance(s, [(tb.shape_id, 200), (l1.shape_id, 500), (l2.shape_id, 650), (l3.shape_id, 800)]); fade_transition(s)

# ================================================================ SLIDE 5 - OBJETIVOS
s = add_slide(); kicker(s, "Objetivos"); titulo(s, "O que este trabalho se propõe")
og = card(s, 0.9, 1.95, 11.55, 1.15, head="Objetivo geral",
          body="Sintetizar evidências e lacunas sobre ambiente, brincar social e TDAH pré-escolar, tornando inteligível a mudança observada no caso índice.")
o1 = card(s, 0.9, 3.35, 3.7, 2.5, num="a", head="Verde e gravidade", body="Mapear evidências sobre natureza, espaço verde e intensidade de sintomas de TDAH.")
o2 = card(s, 4.85, 3.35, 3.7, 2.5, num="b", head="Pares e autorregulação", body="Mapear evidências sobre brincar livre entre pares na faixa de 3 a 6 anos.")
o3 = card(s, 8.8, 3.35, 3.7, 2.5, num="c", head="Clínica humanista", body="Articular os fundamentos de Rogers e Axline que ajudam a explicar a tranquilização também em sessão.")
fade_entrance(s, [(og.shape_id, 200), (o1.shape_id, 500), (o2.shape_id, 650), (o3.shape_id, 800)]); fade_transition(s)

# ================================================================ SLIDE 6 - METODO
s = add_slide(); kicker(s, "Método"); titulo(s, "Revisão integrativa narrativa com vinheta clínica")
m1 = card(s, 0.9, 1.95, 5.6, 1.95, head="Bases e período", body="SciELO · BVS/PEPSIC · Portal CAPES · PubMed · PsycINFO — 2004 a 2026, em português, inglês e espanhol. Descritores DeCS/MeSH: TDAH; pré-escolar; brincar; meio ambiente; terapia centrada no cliente.")
m2 = card(s, 6.85, 1.95, 5.6, 1.95, head="Critérios", body="Inclusão: 3–12 anos, laudo ou traços de TDAH, contexto externo/vizinhança/natureza, desfecho comportamental. Exclusão: só adultos, farmacologia sem ambiente, resumo sem texto completo, duplicatas.")
m3 = card(s, 0.9, 4.05, 5.6, 1.95, head="Desenho — com honestidade", body="Estudo descritivo-hermenêutico de caso único: gera hipóteses, não as confirma. Por isso dispensa, deliberadamente, grupo de controle e isolamento de variáveis.")
m4 = card(s, 6.85, 4.05, 5.6, 1.95, head="Critérios de invalidação", body="A hipótese do “tempo verde-social” cai se: (a) SNAP-IV piorar/estabilizar em 3 meses; (b) melhora persistir sem brincar; (c) surgir psicofármaco no período; (d) mãe e professora discordarem; (e) grupo-irmão sem exposição melhorar igual.")
fade_entrance(s, [(m1.shape_id, 200), (m2.shape_id, 400), (m3.shape_id, 600), (m4.shape_id, 800)]); fade_transition(s)

# ================================================================ SLIDE 7 - EVIDENCIAS
s = add_slide(); kicker(s, "Evidências"); titulo(s, "Seis referências-âncora auditadas")
evs = [
    ("1", "Hood & Baumann (2024)", "Revisão sistemática: 458 estudos → 7 incluídos. Verde denso e brincar em “árvores grandes e grama” ligam-se a menos sintomas, controlando renda e fatores pré-natais."),
    ("2", "Kuo & Faber Taylor (2004)", "452 pais. A mesma atividade em verde alivia mais (p < 0,001); em hiperativos, só o verde aberto funciona."),
    ("3", "Faber Taylor & Kuo (2009)", "Experimento controlado intrasujeito (17 crianças): atenção objetivamente melhor após caminhada em parque do que em percurso urbano."),
    ("4", "Taylor & Kuo (2011)", "421 famílias. Brincar regular em verde = sintomas mais leves, em todos os sexos e rendas. Propõem “dose verde” regular."),
    ("5", "Damasceno et al. (2025)", "Intervenção brasileira de 6 meses (GI × GC, SNAP-IV): o tipo de TDAH permanece, a intensidade recua de “demais” para “bastante/pouco”."),
    ("6", "Yang et al. (2019)", "59.754 crianças, China. Cada +0,1 no índice de verde do entorno escolar = chance 13% menor de sintomas."),
]
shapes = []
for i, (n, h, b) in enumerate(evs):
    col, lin = i % 3, i // 3
    c = card(s, 0.9 + col * 3.95, 1.95 + lin * 2.45, 3.7, 2.25, num=n, head=h, body=b)
    shapes.append(c.shape_id)
fade_entrance(s, [(sp, 150 + i * 130) for i, sp in enumerate(shapes)]); fade_transition(s)

# ================================================================ SLIDE 8 - EIXOS
s = add_slide(); kicker(s, "Síntese"); titulo(s, "Três eixos que conversam com o caso")
e1 = card(s, 0.9, 1.95, 3.7, 2.4, num="EIXO 1", head="Verde e restauração atencional", body="A natureza captura a atenção sem esforço e descansa o sistema atencional sobrecarregado no TDAH (Teoria da Restauração da Atenção).")
e2 = card(s, 4.85, 1.95, 3.7, 2.4, num="EIXO 2", head="Brincar entre pares como regulador", body="Laboratório de convivência: pertencimento, frustração, espera, regras negociadas, corpo em movimento, menos telas.")
e3 = card(s, 8.8, 1.95, 3.7, 2.4, num="EIXO 3", head="Clínica humanista como facilitador", body="Relação viva, não técnica sobre a criança: acolhida na rua e na sessão, a criança integra em vez de só descarregar.")
tb, tf = txbox(s, 0.9, 4.75, 11.5, 0.8)
p = tf.paragraphs[0]
run(p, "O padrão de M. replica Damasceno: a intensidade diminui, o tipo permanece. E inverte o “déficit de natureza” descrito por Louv (2015).", 16, VERDE2, bold=True)
fade_entrance(s, [(e1.shape_id, 200), (e2.shape_id, 350), (e3.shape_id, 500), (tb.shape_id, 800)]); fade_transition(s)

# ================================================================ SLIDE 9 - QUADRO 2 (barras)
s = add_slide(); kicker(s, "Registro clínico-materno"); titulo(s, "M., 5 anos — intensidade da dificuldade por domínio")
tb, tf = txbox(s, 0.9, 1.85, 11.5, 0.4)
p = tf.paragraphs[0]
run(p, "Escala única de 0 a 100 · ilustrativa, não é medida padronizada · Fontes: prontuário e relato materno (2026)", 12, MUTED)
dom = [
    ("Atenção sustentada", 88, 42, "não permanecia diante da TV", "mantém brincadeiras calmas por 10–15 min"),
    ("Hiperatividade", 92, 46, "agitação contínua, “não para”", "corre e brinca, mas volta à calma"),
    ("Dificuldade de interação social", 70, 28, "poucos pares, brincar solitário", "brinca todo dia, é chamada pelas colegas"),
    ("Sessão terapêutica", 85, 40, "trocas rápidas de brinquedo, fala acelerada", "permanece, espera o turno, pede com palavras"),
]
shapes = []
for i, (h, va, vd, da, dd) in enumerate(dom):
    col, lin = i % 2, i // 2
    x, y = 0.9 + col * 5.95, 2.35 + lin * 2.15
    c = card(s, x, y, 5.6, 2.0, head=h)
    shapes.append(c.shape_id)
    # barra antes
    tb, tf = txbox(s, x + 0.2, y + 0.62, 0.75, 0.3); run(tf.paragraphs[0], "Antes", 11, MUTED)
    bar = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + 0.95), Inches(y + 0.60), Inches(3.9 * va / 100), Inches(0.22))
    bar.adjustments[0] = 0.5; bar.fill.solid(); bar.fill.fore_color.rgb = VERMELHO; bar.line.fill.background(); bar.shadow.inherit = False
    shapes.append(bar.shape_id)
    tb, tf = txbox(s, x + 4.0, y + 0.58, 0.7, 0.3); run(tf.paragraphs[0], str(va), 11, OURO, bold=True)
    tb, tf = txbox(s, x + 1.15, y + 0.84, 4.3, 0.3); run(tf.paragraphs[0], da, 10.5, MUTED)
    # barra depois
    tb, tf = txbox(s, x + 0.2, y + 1.18, 0.75, 0.3); run(tf.paragraphs[0], "Depois", 11, MUTED)
    bar2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + 0.95), Inches(y + 1.16), Inches(3.9 * vd / 100), Inches(0.22))
    bar2.adjustments[0] = 0.5; bar2.fill.solid(); bar2.fill.fore_color.rgb = VERDE; bar2.line.fill.background(); bar2.shadow.inherit = False
    shapes.append(bar2.shape_id)
    tb, tf = txbox(s, x + 4.0, y + 1.14, 0.7, 0.3); run(tf.paragraphs[0], str(vd), 11, OURO, bold=True)
    tb, tf = txbox(s, x + 1.15, y + 1.40, 4.3, 0.3); run(tf.paragraphs[0], dd, 10.5, MUTED)
tb, tf = txbox(s, 0.9, 6.75, 11.5, 0.4)
run(tf.paragraphs[0], "Leitura: barra vermelha (antes) sempre maior que a verde (depois) — a dificuldade caiu nos quatro domínios. Valores ilustram o relato, não são escores.", 11.5, MUTED)
shapes.append(tb.shape_id)
fade_entrance(s, [(sp, 150 + i * 90) for i, sp in enumerate(shapes)]); fade_transition(s)

# ================================================================ SLIDE 10 - DISCUSSAO
s = add_slide(); kicker(s, "Discussão"); titulo(s, "O que dá para afirmar — e o que não dá")
d1 = card(s, 0.9, 1.95, 5.6, 2.0, head="Afirmamos", body="O percurso de M. é coerente com a literatura (Damasceno; Kuo; Hood). A mudança de endereço não “tratou” a criança — ampliou seu campo relacional, liberando a tendência atualizante (Rogers, 2020).")
d2 = card(s, 6.85, 1.95, 5.6, 2.0, head="Não afirmamos", body="Nenhuma eficácia, causalidade ou remissão. Sem SNAP-IV basal, sem dose medida de brincar/telas e sem dado farmacológico, concluímos apenas coerência teórica e agenda.")
a = aviso(s, "Oito explicações alternativas: maturação (5,0–5,5 anos) · sono/rotina/escola · estresse familiar · aliança terapêutica · viés de expectativa materna · sazonalidade · redução de telas não mensurada · MEDICAÇÃO NÃO DECLARADA (se houve início/ajuste/suspensão, a leitura ambiental perde sustentação).", y=4.4)
fade_entrance(s, [(d1.shape_id, 200), (d2.shape_id, 450), (a.shape_id, 800)]); fade_transition(s)

# ================================================================ SLIDE 11 - CONCLUSAO
s = add_slide(); kicker(s, "Conclusão"); titulo(s, "A ecologia do brincar entra na formulação clínica")
tb, tf = txbox(s, 0.9, 1.95, 11.5, 1.0)
p = tf.paragraphs[0]
run(p, "Em pré-escolares com TDAH misto, a formulação deve incluir onde, com quem e por quanto tempo a criança brinca ao ar livre — ao lado de sintomas, família e escola (Bronfenbrenner, 1996).", 16, TEXTO)
p.line_spacing = 1.2
i1 = card(s, 0.9, 3.15, 5.6, 2.4, head="4 implicações práticas",
          body="• Registrar a dose diária de brincar externo social\n• Priorizar verdes e abertos no predomínio hiperativo\n• Envolver a escola no mapeamento do recreio\n• Usar o registro como instrumento dialógico nas sessões")
i2 = card(s, 6.85, 3.15, 5.6, 2.4, head="Contribuição",
          body="Documentar, em português e sob ótica humanista, um fenômeno quase ausente da literatura: o brincar de vizinhança não estruturado aos 5 anos — com categorias replicáveis para outros clínicos.")
fade_entrance(s, [(tb.shape_id, 200), (i1.shape_id, 500), (i2.shape_id, 650)]); fade_transition(s)

# ================================================================ SLIDE 12 - AGENDA
s = add_slide(); kicker(s, "Próximos passos"); titulo(s, "Agenda de continuidade")
ags = [
    "1. Aplicar SNAP-IV com pais e professores agora e em 3 meses (linha de base + seguimento)",
    "2. Diário de 2 semanas: hora de rua, com quem, onde, hora de tela, hora de dormir",
    "3. 8–12 sessões com protocolo axlineano registrado em vinhetas",
    "4. Entrevista semiestruturada com a mãe",
    "5. Submissão a Comitê de Ética em Pesquisa, se a pesquisa for institucional",
]
shapes = []
for i, it in enumerate(ags):
    tb, tf = txbox(s, 1.2, 1.95 + i * 0.62, 11.0, 0.55)
    run(tf.paragraphs[0], "✔  " + it, 15.5, TEXTO)
    shapes.append(tb.shape_id)
a = aviso(s, "Limitações assumidas: caso único · sem grupo controle · sem escala padronizada · dose não medida · medicação e sono sem informação · possível viés no relato materno.", y=5.6)
shapes.append(a.shape_id)
fade_entrance(s, [(sp, 200 + i * 200) for i, sp in enumerate(shapes)]); fade_transition(s)

# ================================================================ SLIDE 13 - REFERENCIAS
s = add_slide(); kicker(s, "Fundamentação"); titulo(s, "Referências centrais (15 no manuscrito)")
refs = [
    "1. HOOD, M.; BAUMANN, O. Could nature contribute to the management of ADHD in children? A systematic review. Int. J. Environ. Res. Public Health, v. 21, n. 6, p. 736, 2024.",
    "2. KUO, F. E.; FABER TAYLOR, A. A potential natural treatment for attention-deficit/hyperactivity disorder. Am. J. Public Health, v. 94, n. 9, p. 1580-1586, 2004.",
    "3. FABER TAYLOR, A.; KUO, F. E. Children with attention deficits concentrate better after walk in the park. J. Atten. Disord., v. 12, n. 5, p. 402-409, 2009.",
    "4. DAMASCENO, M. M. S. et al. Crianças com TDAH em contato com a natureza: transformações possíveis. Educação & Realidade, v. 50, 2025.",
    "5. ROGERS, C. R. Terapia centrada no cliente. São Paulo: Martins Fontes, 2020. · AXLINE, V. M. Ludoterapia. São Paulo: Summus, 1984. · BRONFENBRENNER, U. A ecologia do desenvolvimento humano. Porto Alegre: Artes Médicas, 1996.",
]
shapes = []
for i, r in enumerate(refs):
    tb, tf = txbox(s, 0.9, 1.95 + i * 0.9, 11.5, 0.85)
    p = tf.paragraphs[0]; p.line_spacing = 1.1
    run(p, r, 12.5, TEXTO)
    shapes.append(tb.shape_id)
fade_entrance(s, [(sp, 200 + i * 180) for i, sp in enumerate(shapes)]); fade_transition(s)

# ================================================================ SLIDE 14 - ENCERRAMENTO
s = add_slide()
sh14 = []
tb, tf = txbox(s, 1.0, 1.6, 11.3, 0.5)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "ENCERRAMENTO", 14, OURO, bold=True)
sh14.append(tb.shape_id)
tb, tf = txbox(s, 0.7, 2.2, 11.9, 2.0)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "Obrigada.", 54, TEXTO, bold=True)
p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
run(p2, "Estamos à disposição da banca.", 30, VERDE, bold=True)
sh14.append(tb.shape_id)
tb, tf = txbox(s, 1.0, 4.5, 11.3, 0.8)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "“O corpo que precisava interromper para existir passou a correr, negociar e descansar.”", 17, MUTED, italic=True)
sh14.append(tb.shape_id)
tb, tf = txbox(s, 1.0, 6.0, 11.3, 0.5)
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run(p, "Relato de experiência — Clínica humanista · 2026", 13, MUTED)
sh14.append(tb.shape_id)
fade_entrance(s, [(sp, 150 + i * 170) for i, sp in enumerate(sh14)]); fade_transition(s)

OUT = "/home/marceloclaro/opencode-ecosystem-core/artigos/tdah_brincar_vizinhanca/mira_deck/deck_tdah_mira.pptx"
prs.save(OUT)
print("SALVO:", OUT)
print("slides:", len(prs.slides.__iter__.__self__._sldIdLst))
