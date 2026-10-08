#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador DOCX ABNT do relato TDAH — fonte única de verdade: módulos LaTeX.
Formatação: A4; margens sup/esq 3cm, inf/dir 2cm; Times 12; espaço 1,5;
recuo de parágrafo 1,25cm; cabeçalho com página a partir do corpo.
"""
import re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = "/home/marceloclaro/opencode-ecosystem-core/artigos/tdah_brincar_vizinhanca"
OUT = f"{BASE}/RELATO_TDAH_BRINCAR_VIZINHANCA_AUTORAS_5.docx"

# ---------------------------------------------------------------- aux: citações
aux = open(f"{BASE}/main.aux", encoding="utf-8").read()
BIB = dict(re.findall(r"\\bibcite\{([^}]+)\}\{([^}]+)\}", aux))
YEAR = dict(re.findall(r"\\bibciteYEAR\{([^}]+)\}\{([^}]+)\}", aux))

def cite_author(key):
    raw = re.sub(r"[{}]", "", BIB.get(key, key))
    raw = re.sub(r"\s+e\s+", "; ", raw)  # conector de autores: pacote grava "e"
    raw = re.sub(r"\s+\d{4}[a-z]?\.?$", "", raw)  # remove ano do rotulo
    partes = [p.strip() for p in raw.split(";")]
    out = []
    for p in partes:
        low = p.lower()
        if low == "et al.":
            out.append("et al.")
        elif " et al." in low:
            base = p[:low.index(" et al.")]
            out.append(base.upper() + " et al.")
        else:
            out.append(p.upper())
    return "; ".join(out)

def cite_label(key):
    a = cite_author(key)
    ano = YEAR.get(key, "")
    return a + (", " + ano if ano else "")

def expand_cite(m):
    keys = [k.strip() for k in m.group(1).split(",")]
    return "(" + "; ".join(cite_label(k) for k in keys) + ")"

def expand_citeonline(m):
    keys = [k.strip() for k in m.group(1).split(",")]
    autores = "; ".join(cite_author(k) for k in keys)
    anos = "; ".join(YEAR.get(k, "") for k in keys)
    return f"{autores} ({anos})"

# ---------------------------------------------------------------- escapes
ESC = [
    (r"\c{c}", "ç"), (r"\c{C}", "Ç"),
    (r"\~a", "ã"), (r"\~o", "õ"), (r"\~A", "Ã"), (r"\~O", "Õ"),
    (r"\'a", "á"), (r"\'e", "é"), (r"\'i", "í"), (r"\'o", "ó"), (r"\'u", "ú"),
    (r"\'A", "Á"), (r"\'E", "É"), (r"\'I", "Í"), (r"\'O", "Ó"), (r"\'U", "Ú"),
    (r"\^a", "â"), (r"\^e", "ê"), (r"\^o", "ô"), (r"\^A", "Â"), (r"\^E", "Ê"),
    (r"\`a", "à"), (r"\`A", "À"), (r"\%", "%"), (r"\&", "&"),
]
def deescape(s):
    for a, b in ESC:
        s = s.replace(a, b)
    return s

def inline(s):
    s = s.replace("``", '"').replace("''", '"')
    s = re.sub(r"---", "—", s)
    s = re.sub(r"--", "–", s)
    return s

# ---------------------------------------------------------------- runs
BOLD_RE = re.compile(r"\\(textbf|textit)\{((?:[^{}]|\{[^{}]*\})*)\}")

def add_runs(p, text):
    """Adiciona runs ao parágrafo, respeitando \textbf e \textit inline."""
    for m in re.split(r"(\\(?:textbf|textit)\{(?:[^{}]|\{[^{}]*\})*\})", text):
        if not m:
            continue
        mm = BOLD_RE.match(m)
        if mm:
            run = p.add_run(inline(deescape(mm.group(2))))
            run.bold = (mm.group(1) == "textbf")
            run.italic = (mm.group(1) == "textit")
        else:
            run = p.add_run(inline(deescape(m)))
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        rfonts.set(qn("w:ascii"), "Times New Roman")
        rfonts.set(qn("w:hAnsi"), "Times New Roman")

# ---------------------------------------------------------------- documento
doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(12)
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(0)
st.paragraph_format.space_before = Pt(0)

sec1 = doc.sections[0]
sec1.page_width, sec1.page_height = Cm(21), Cm(29.7)
sec1.top_margin, sec1.left_margin = Cm(3), Cm(3)
sec1.bottom_margin, sec1.right_margin = Cm(2), Cm(2)

# ---------------------------------------------------------------- capa
def cp(text, bold=False, size=12, space_after=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    return p

cp("", space_after=18)
cp("RELATO DE EXPERIÊNCIA DA PRÁTICA CLÍNICA EM ABORDAGEM HUMANISTA: DA SALA PARA A RUA – BRINCAR LIVRE NA VIZINHANÇA E ATENUAÇÃO DA INTENSIDADE DE SINTOMAS DE TDAH EM PRÉ-ESCOLAR", bold=True)
cp("", space_after=24)
for a in ["Ana Gessyca de Sousa Fernandes", "Isabelly Rosa Cavalcante",
          "Nadielle Darc Batista Dias", "Winny Ketlyn Sabóia Teixeira",
          "Marta Tainá Silva de Sousa"]:
    cp(a)
cp("", space_after=18)
cp("Discentes do curso de graduação em Psicologia")
cp("[INSTITUIÇÃO DE ENSINO SUPERIOR – A PREENCHER]")
cp("Orientadora: [NOME DA ORIENTADORA – A PREENCHER]")
cp("", space_after=36)
cp("[CIDADE]")
cp("2026")
doc.add_page_break()

# ---------------------------------------------------------------- helpers de parágrafo
def body_para(text, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=1.5,
              left_indent=None):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = spacing
    pf.space_after = Pt(0)
    if indent and left_indent is None:
        pf.first_line_indent = Cm(1.25)
    if left_indent is not None:
        pf.left_indent = Cm(left_indent)
        pf.first_line_indent = Cm(0)
    add_runs(p, text)
    return p

def heading1(num, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f"{num} {inline(deescape(text)).upper()}")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p

def heading2(num, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f"{num} {inline(deescape(text))}")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p

# ---------------------------------------------------------------- tabelas manuais
def quadro(caption, header, rows, widths, fonte):
    cp2 = doc.add_paragraph()
    cp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp2.paragraph_format.space_before = Pt(12)
    cp2.paragraph_format.space_after = Pt(6)
    r = cp2.add_run(caption)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(header):
        cell = t.rows[0].cells[j]
        cell.text = ""
        pr = cell.paragraphs[0]
        run = pr.add_run(h)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        pr.paragraph_format.line_spacing = 1.0
        pr.paragraph_format.space_after = Pt(2)
    for i, row in enumerate(rows, 1):
        for j, val in enumerate(row):
            cell = t.rows[i].cells[j]
            cell.text = ""
            pr = cell.paragraphs[0]
            run = pr.add_run(val)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            pr.paragraph_format.line_spacing = 1.0
            pr.paragraph_format.space_after = Pt(2)
    for j, w in enumerate(widths):
        for row in t.rows:
            row.cells[j].width = Cm(w)
    pf = doc.add_paragraph()
    pf.paragraph_format.space_before = Pt(4)
    pf.paragraph_format.line_spacing = 1.0
    r = pf.add_run(fonte)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

# ---------------------------------------------------------------- conteúdo dos quadros
q1 = quadro1_rows = [
    [cite_label("hood2024"),
     "Revisão sistemática; 458 estudos triados, 7 incluídos",
     "Áreas com mais vegetação e brincadeiras em “árvores grandes e grama” aparecem ligadas a menos diagnósticos e sintomas mais leves, mesmo ajustando renda e fatores pré-natais"],
    [cite_label("kuo2004"),
     "Estudo nacional norte-americano; N = 452 pais; 49 atividades comparadas",
     "A mesma atividade feita em espaço verde alivia mais os sintomas do que em área construída ou fechada (p < 0,001); em crianças hiperativas, só o verde aberto mostrou esse efeito"],
    [cite_label("fabertaylor2009"),
     "Experimento controlado intrasujeito; N = 17; caminhada de 20 minutos",
     "Após caminhar em parque, as crianças pontuaram melhor em testes objetivos de atenção do que após percurso urbano equivalente; cada participante serviu de próprio controle"],
    [cite_label("taylor2011"),
     "Survey nacional; N = 421; local habitual de brincar",
     "Quem brinca com frequência em verde apresenta sintomas mais leves, em todos os sexos e faixas de renda; os autores propõem ensaios de “dose verde” regular"],
    [cite_label("damasceno2025"),
     "Intervenção de 6 meses; grupo intervenção versus controle; SNAP-IV, guias e diários; Nordeste do Brasil",
     "O tipo de TDAH se manteve, mas a intensidade recuou de “demais” para “bastante/pouco”; melhoraram a agitação constante, a espera de turno e a aceitação de regras, com mais calma e abertura social"],
    [cite_label("yang2019"),
     "Transversal; N = 59.754; China; índice de vegetação a 500 m da escola",
     "Cada 0,1 a mais no índice de verde do entorno escolar correspondeu a chance 13% menor de sintomas de TDAH"],
]
q2 = quadro2_rows = [
    ["Atenção sustentada",
     "Não permanecia diante da televisão; levantava e mexia em objetos",
     "Mantém brincadeiras calmas por 10–15 minutos; desenho e jogo",
     "Mãe; diário de campo"],
    ["Hiperatividade",
     "Agitação contínua; “não para”",
     "Corre e brinca, mas volta à calma; intervalos sentada",
     "Mãe; sessões"],
    ["Interação social",
     "Poucos pares; brincar solitário e interno",
     "Brinca todo dia na vizinhança; é chamada pelas colegas",
     "Mãe"],
    ["Sessão terapêutica",
     "Troca rápida de brinquedos; fala acelerada",
     "Permanece mais tempo; espera o turno; pede com palavras",
     "Terapeuta"],
]

# ---------------------------------------------------------------- parser dos módulos
sec_count = 0
sub_count = 0
in_enum = False

def process_module(path):
    global sec_count, sub_count, in_enum
    lines = open(path, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("%"):
            i += 1
            continue
        # comandos de controle LaTeX: ignorar (não escrever no DOCX)
        if re.match(r"\\vspace\{.*\}|\\thispagestyle\{.*\}|\\newpage|\\pagenumbering\{.*\}|\\setcounter\{.*\}|\\renewcommand\{.*\}", line):
            i += 1
            continue
        m = re.match(r"\\section\{(.*)\}\s*$", line)
        if m:
            sec_count += 1
            sub_count = 0
            heading1(sec_count, m.group(1))
            i += 1
            continue
        m = re.match(r"\\subsection\{(.*)\}\s*$", line)
        if m:
            sub_count += 1
            heading2(f"{sec_count}.{sub_count}", m.group(1))
            i += 1
            continue
        if line.startswith(r"\begin{enumerate}"):
            in_enum = True
            i += 1
            continue
        if line.startswith(r"\end{enumerate}"):
            in_enum = False
            i += 1
            continue
        if line.startswith(r"\item"):
            txt = re.sub(r"^\\item\s*", "", line)
            body_para(txt, indent=False, left_indent=1.9)
            i += 1
            continue
        # bloco center (multilinha): acumular até \end{center}
        if line.startswith(r"\begin{center}"):
            i += 1
            inner_parts = []
            while i < len(lines) and not lines[i].strip().startswith(r"\end{center}"):
                t = lines[i].strip()
                if t:
                    inner_parts.append(t)
                i += 1
            i += 1  # pula \end{center}
            txt = " ".join(inner_parts)
            txt = re.sub(r"\{\\bfseries\s*([^}]*)\}", r"\1", txt)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_runs(p, txt)
            for r in p.runs:
                r.bold = True
            continue
        if line.startswith(r"\begin{quadro}"):
            cap = re.match(r"\\begin\{quadro\}\{(.*)\}\s*$", line).group(1)
            # pula até \end{quadro}
            while not lines[i].strip().startswith(r"\end{quadro}"):
                i += 1
            i += 1
            if "Quadro 1" in cap:
                quadro("Quadro 1 – Síntese das referências-âncora (auditoria em 5 out. 2026)",
                       ["Nº", "Referência", "Desenho", "Achado para o caso"],
                       q1, [0.8, 4.2, 4.2, 4.6],
                       "Fonte: dados da revisão; elaborado pelas autoras (2026).")
            else:
                quadro("Quadro 2 – M., 5 anos, antes e depois da mudança de endereço (registro clínico-materno, observacional)",
                       ["Domínio", "Antes (contexto 1)", "Depois (contexto 2; 4–8 semanas)", "Fonte"],
                       q2, [3.4, 4.4, 4.4, 2.2],
                       "Fonte: prontuário e relato materno (2026). Dados observacionais, sem escala padronizada.")
            continue
        # parágrafo: acumular linhas até linha em branco ou comando
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("\\"):
            buf.append(lines[i].strip())
            i += 1
        text = " ".join(b for b in buf if not b.startswith("%"))
        text = re.sub(r"\\citeonline\{([^}]*)\}", expand_citeonline, text)
        text = re.sub(r"\\cite\{([^}]*)\}", expand_cite, text)
        noindent = text.startswith(r"\noindent")
        text = text.replace(r"\noindent", "")
        body_para(text, indent=not noindent)

process_module(f"{BASE}/modulos/02-resumo.tex")
process_module(f"{BASE}/modulos/03-introducao.tex")
process_module(f"{BASE}/modulos/04-objetivos.tex")
process_module(f"{BASE}/modulos/05-metodo.tex")
process_module(f"{BASE}/modulos/06-resultados.tex")
process_module(f"{BASE}/modulos/07-discussao.tex")
process_module(f"{BASE}/modulos/08-conclusao.tex")

# ---------------------------------------------------------------- referências
p = doc.add_paragraph()
r = p.add_run("REFERÊNCIAS")
r.bold = True
r.font.name = "Times New Roman"
r.font.size = Pt(12)
p.paragraph_format.space_before = Pt(18)
p.paragraph_format.space_after = Pt(12)

# (texto, negrito) — NBR 6023: título de livro e nome de periódico em destaque
REFS = [
 [("AMERICAN PSYCHIATRIC ASSOCIATION. ", False),
  ("Manual diagnóstico e estatístico de transtornos mentais: DSM-5-TR.", True),
  (" 5. ed. rev. Porto Alegre: Artmed, 2023.", False)],
 [("AXLINE, V. M. ", False),
  ("Ludoterapia: a dinâmica interior da infância.", True),
  (" São Paulo: Summus, 1984.", False)],
 [("BRONFENBRENNER, U. ", False),
  ("A ecologia do desenvolvimento humano: experimentos naturais e planejados.", True),
  (" Porto Alegre: Artes Médicas, 1996.", False)],
 [("DAMASCENO, M. M. S.; MAZZARINO, J. M.; FIGUEIREDO, A. Crianças com TDAH em contato com a natureza: transformações possíveis. ", False),
  ("Educação & Realidade", True),
  (", Porto Alegre, v. 50, 2025. Disponível em: https://www.scielo.br/j/edreal/a/xJd4QkXcqYnPt5RMLG8GdgG/?lang=pt. Acesso em: 5 out. 2026.", False)],
 [("DAMASCENO, M. M. S.; MAZZARINO, J. M.; FIGUEIREDO, A. Natureza, comportamento biopsicossocial infantil e TDAH. ", False),
  ("Educação", True),
  (", Porto Alegre, v. 48, n. 1, e48180, 2025. Disponível em: https://revistaseletronicas.pucrs.br/faced/article/view/48180. Acesso em: 5 out. 2026.", False)],
 [("FABER TAYLOR, A.; KUO, F. E. Children with attention deficits concentrate better after walk in the park. ", False),
  ("Journal of Attention Disorders", True),
  (", v. 12, n. 5, p. 402-409, 2009.", False)],
 [("FIGUEIREDO, J. S. ", False),
  ("Um estudo de caso a partir da atuação psicopedagógica utilizando estratégias lúdicas com o TDAH.", True),
  (" 2015. Trabalho de Conclusão de Curso (Graduação em Psicopedagogia) – Universidade Federal da Paraíba, João Pessoa, 2015. Disponível em: https://repositorio.ufpb.br/jspui/handle/123456789/2970. Acesso em: 5 out. 2026.", False)],
 [("HOOD, M.; BAUMANN, O. Could nature contribute to the management of ADHD in children? A systematic review. ", False),
  ("International Journal of Environmental Research and Public Health", True),
  (", v. 21, n. 6, p. 736, 2024. Disponível em: https://www.mdpi.com/1660-4601/21/6/736. Acesso em: 5 out. 2026.", False)],
 [("KUO, F. E.; FABER TAYLOR, A. A potential natural treatment for attention-deficit/hyperactivity disorder: evidence from a national study. ", False),
  ("American Journal of Public Health", True),
  (", v. 94, n. 9, p. 1580-1586, 2004.", False)],
 [("LOUV, R. ", False),
  ("Last child in the woods: saving our children from nature-deficit disorder.", True),
  (" 3. ed. Chapel Hill: Algonquin Books, 2015.", False)],
 [("POLANCZYK, G. et al. The worldwide prevalence of ADHD: a systematic review and metaregression analysis. ", False),
  ("American Journal of Psychiatry", True),
  (", v. 164, n. 6, p. 942-948, 2007.", False)],
 [("ROGERS, C. R. ", False),
  ("Terapia centrada no cliente.", True),
  (" São Paulo: Martins Fontes, 2020.", False)],
 [("TAYLOR, A. F.; KUO, F. E. Could exposure to everyday green spaces help treat ADHD? Evidence from children's play settings. ", False),
  ("Applied Psychology: Health and Well-Being", True),
  (", v. 3, n. 3, p. 281-303, 2011.", False)],
 [("WOLRAICH, M. L. et al. Clinical practice guideline for the diagnosis, evaluation, and treatment of attention-deficit/hyperactivity disorder in children and adolescents. ", False),
  ("Pediatrics", True),
  (", v. 144, n. 4, e20192528, 2019.", False)],
 [("YANG, B. et al. Association between greenness surrounding schools and kindergartens and attention-deficit/hyperactivity disorder in children in China. ", False),
  ("JAMA Network Open", True),
  (", v. 2, n. 12, e1917862, 2019.", False)],
]
for parts in REFS:
    pr = doc.add_paragraph()
    pr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pr.paragraph_format.line_spacing = 1.0
    pr.paragraph_format.space_after = Pt(12)
    pr.paragraph_format.first_line_indent = Cm(0)
    for texto, bold in parts:
        run = pr.add_run(texto)
        run.bold = bold
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

# ---------------------------------------------------------------- seção de paginação
sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
sec2.top_margin, sec2.left_margin = Cm(3), Cm(3)
sec2.bottom_margin, sec2.right_margin = Cm(2), Cm(2)
sec2.footer.is_linked_to_previous = False
sec1.header.is_linked_to_previous = False

hdr = sec2.header
hdr.is_linked_to_previous = False
hp = hdr.paragraphs[0]
hp.text = ""
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = hp.add_run()
fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
run.font.name = "Times New Roman"
run.font.size = Pt(12)

doc.save(OUT)
print("SALVO:", OUT)
print("paragrafos:", len(doc.paragraphs), "| tabelas:", len(doc.tables))
