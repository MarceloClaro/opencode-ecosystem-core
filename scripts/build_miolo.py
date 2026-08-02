#!/usr/bin/env python3
"""
build_miolo.py — Gera o miolo LaTeX + PDF do Molambudos a partir de molambudos.md
Pipeline: parse markdown → fragmentos .tex → main.tex → pdflatex → PDF
"""

import re
import os
import sys
import subprocess
from pathlib import Path

# === CONFIG ===
BASE_DIR = Path('/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos')
MOLAMBUROS = BASE_DIR / 'molambudos.md'
FRAG_DIR = BASE_DIR / 'fragmentos'
MAIN_TEX = BASE_DIR / 'main.tex'
MAIN_PDF = BASE_DIR / 'main.pdf'

os.makedirs(FRAG_DIR / 'mem', exist_ok=True)
os.makedirs(FRAG_DIR / 'doc', exist_ok=True)
os.makedirs(FRAG_DIR / 'luc', exist_ok=True)
os.makedirs(FRAG_DIR / 'cont', exist_ok=True)


# === MARKDOWN → LATEX CONVERSION ===

def md_to_latex(text):
    """Convert Markdown text content to LaTeX format (one paragraph per \noindent)."""
    # Normalize line endings
    text = text.replace('\r\n', '\n')

    # Process block-level elements
    # Split into blocks (separated by blank lines)
    blocks = re.split(r'\n\n+', text)
    result = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Blockquote
        if block.startswith('> '):
            lines = []
            for line in block.split('\n'):
                if line.startswith('> '):
                    lines.append(inline_md_to_latex(line[2:]))
                elif line.startswith('>'):
                    lines.append(inline_md_to_latex(line[1:]))
            result.append('\\begin{quote}\n' + '\n'.join(lines) + '\n\\end{quote}')
            continue

        # Table
        if '|' in block and '\n|' in block:
            latex_table = md_table_to_latex(block)
            if latex_table:
                result.append(latex_table)
                continue

        # Horizontal rule
        if re.match(r'^---+$', block.strip()):
            result.append(r'\vspace{0.5em}\noindent\rule{\textwidth}{0.5pt}\vspace{0.5em}')
            continue

        # Regular paragraph — convert inline and wrap
        para = inline_md_to_latex(block)
        result.append(r'\noindent ' + para)

    return '\n\n'.join(result)


def inline_md_to_latex(text):
    """Convert inline Markdown formatting to LaTeX.
    
    Order matters:
    1. Strip emoji
    2. Temporarily protect LaTeX special chars that might also be markdown syntax
    3. Convert markdown formatting → LaTeX commands
    4. Restore/apply LaTeX special char escaping for remaining literal chars
    """
    # --- Step 1: Strip emoji ---
    def strip_emoji(s):
        result = []
        for c in s:
            cp = ord(c)
            if 0xFE00 <= cp <= 0xFE0F: continue  # Variation Selectors
            if cp == 0x200D: continue  # Zero Width Joiner
            if 0x2600 <= cp <= 0x26FF and cp not in (0x2610, 0x2611, 0x2573, 0x21AA): continue
            if 0x2700 <= cp <= 0x27BF and cp not in (0x2713, 0x2714, 0x2716, 0x2717): continue
            if 0x1F000 <= cp <= 0x1FFFF: continue
            if 0x1F100 <= cp <= 0x1F1FF: continue
            if 0xE0000 <= cp <= 0xE007F: continue
            result.append(c)
        return ''.join(result)
    text = strip_emoji(text)

    # --- Step 2: Protect literal special chars that look like LaTeX but aren't ---
    # Replace literal backslash with a placeholder that won't be confused with LaTeX commands
    # (backslashes are extremely rare in Portuguese text)
    text = text.replace('\\', '¶BS¶')
    # Replace literal #, _, &, %, $ with placeholders
    text = text.replace('#', '¶HASH¶')
    text = text.replace('_', '¶UNDER¶')
    text = text.replace('&', '¶AMP¶')
    text = text.replace('%', '¶PCT¶')
    text = text.replace('$', '¶DOL¶')
    # Replace literal { } with placeholders (also rare in Portuguese prose)
    text = text.replace('{', '¶LBRACE¶')
    text = text.replace('}', '¶RBRACE¶')

    # --- Step 3: Convert markdown formatting to LaTeX ---
    # Bold-italic ***text*** → \textbf{\textit{text}}
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    # Bold **text** → \textbf{text}
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Italic *text* → \textit{text}
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', text)

    # Curly quotes
    text = re.sub(r'\u201c(.+?)\u201d', r'\\textquotedbl{}\1\\textquotedbl{}', text)
    text = re.sub(r'\u2018(.+?)\u2019', r"\\textquoteleft{}\1\\textquoteright{}", text)
    # ASCII double quotes (only when paired)
    text = re.sub(r'"([^"]+)"', r'\\textquotedbl{}\1\\textquotedbl{}', text)

    # Em-dash / en-dash 
    text = text.replace('—', '---')
    text = text.replace('–', '--')

    # --- Step 4: Restore placeholders as proper LaTeX escapes ---
    text = text.replace('¶BS¶', r'\textbackslash{}')
    text = text.replace('¶HASH¶', r'\#')
    text = text.replace('¶UNDER¶', r'\_')
    text = text.replace('¶AMP¶', r'\&')
    text = text.replace('¶PCT¶', r'\%')
    text = text.replace('¶DOL¶', r'\$')
    text = text.replace('¶LBRACE¶', r'\{')
    text = text.replace('¶RBRACE¶', r'\}')

    # § → \S
    text = text.replace('§', r'\S{}')

    return text.strip()


def md_table_to_latex(block):
    """Convert a Markdown table to LaTeX tabular."""
    lines = block.strip().split('\n')
    if len(lines) < 2:
        return None

    # Parse header separator to determine alignment
    sep = lines[1].strip()
    cols = []
    for part in sep.split('|'):
        part = part.strip()
        if not part:
            continue
        if part.startswith(':') and part.endswith(':'):
            cols.append('c')
        elif part.endswith(':'):
            cols.append('r')
        else:
            cols.append('l')

    if not cols:
        return None

    alignment = '|' + '|'.join(cols) + '|'
    buf = [f'\\begin{{tabular}}{{{alignment}}}']
    buf.append('\\hline')

    for idx, line in enumerate(lines):
        if idx == 1:
            continue  # skip separator
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        # Convert each cell
        cells = [inline_md_to_latex(c) for c in cells]
        buf.append(' & '.join(cells) + ' \\\\')
        if idx == 0:
            buf.append('\\hline')

    buf.append('\\hline')
    buf.append('\\end{tabular}')
    return '\n'.join(buf)


# === FRAGMENT PARSING ===

def parse_fragments(md_content):
    """Parse molambudos.md into header and fragment sections."""
    lines = md_content.split('\n')

    # Find where fragments begin (first ## MEM/DOC/LUC/CONT header)
    frag_start = None
    for i, line in enumerate(lines):
        if re.match(r'^## (?:[^ ]* )?(MEM-\d+|DOC-\d+|LUC-\d+|CONT-\d+)', line):
            frag_start = i
            break

    if frag_start is None:
        print("ERRO: Nenhum fragmento encontrado no markdown!")
        sys.exit(1)

    # Header content (before first fragment)
    header_lines = lines[:frag_start]
    header = '\n'.join(header_lines)

    # Parse fragments — deduplicate emoji/non-emoji headers
    fragments = []
    current_frag = None
    seen_ids = set()

    for line in lines[frag_start:]:
        m = re.match(r'^## (?:[^ ]* )?(MEM-\d+|DOC-\d+|LUC-\d+|CONT-\d+|MEM-27|LUC-Contraprova|LUC-Entrevista|LUC-Escolha)', line)
        if m:
            fid = m.group(1)
            if fid in seen_ids:
                # Duplicate header (emoji version after plain or vice versa) — skip
                continue
            seen_ids.add(fid)
            if current_frag:
                fragments.append(current_frag)
            current_frag = {'id': fid, 'lines': [], 'title': line.strip()}
        elif current_frag is not None:
            current_frag['lines'].append(line)

    if current_frag:
        fragments.append(current_frag)

    return header, fragments


# === .TEX GENERATION ===

def extract_fragment_content(frag):
    """Extract the actual content (paragraphs) from a fragment, excluding links section."""
    lines = frag['lines']

    # Find where links section starts
    links_idx = None
    for i, line in enumerate(lines):
        if '**↪ Links:**' in line or '↪ Links:' in line:
            links_idx = i
            break

    # Also check for "↪ Links:" as last item
    content_lines = lines[:links_idx] if links_idx is not None else lines
    links_line = lines[links_idx] if links_idx is not None else ''

    # Clean up content: remove the duplicate header (second ## or first line)
    content = '\n'.join(content_lines)
    return content.strip(), links_line.strip()


def fragment_to_tex(frag):
    """Convert a fragment to .tex format."""
    frag_id = frag['id']
    content_text, links_line = extract_fragment_content(frag)

    # Determine directory
    if frag_id.startswith('MEM'):
        subdir = 'mem'
    elif frag_id.startswith('DOC'):
        subdir = 'doc'
    elif frag_id.startswith('LUC'):
        subdir = 'luc'
    else:
        subdir = 'cont'

    # Build .tex content
    tex = []
    tex.append(f'% ============================================')
    tex.append(f'% {frag_id}')
    tex.append(f'% Gerado de molambudos.md — build_miolo.py')
    tex.append(f'% ============================================')

    # Title (from the ## header line) — strip emoji and ID prefix
    title = frag['title'].replace('## ', '').strip()
    # Remove emoji prefix (any non-alphanumeric glyphs before the ID)
    title = re.sub(r'^[^a-zA-Z0-9]+ ', '', title)
    # Remove the leading "MEM-15 — " or similar (frag_id already in \textbf)
    title = re.sub(r'^(MEM-\d+|DOC-\d+|LUC-\d+|CONT-\d+|MEM-27|LUC-Contraprova|LUC-Entrevista|LUC-Escolha)\s*[—–-]\s*', '', title)
    # Also strip emoji from the title
    title = inline_md_to_latex(title)
    tex.append(f'\\section*{{\\textbf{{{frag_id}}} --- {title}}}')
    tex.append(f'\\markboth{{{frag_id} --- {title}}}{{}}')
    tex.append('')

    # Content
    converted = md_to_latex(content_text)
    tex.append(converted)

    # Links section
    if links_line:
        # Clean links line
        links = links_line.strip()
        links = inline_md_to_latex(links)
        tex.append('')
        tex.append(r'\vspace{0.5em}')
        tex.append(r'\noindent\textit{\textbf{' + links + '}}')

    return '\n'.join(tex), subdir


def write_fragment_tex(frag):
    """Write a single .tex file for the fragment."""
    tex_content, subdir = fragment_to_tex(frag)
    frag_id = frag['id']
    filepath = FRAG_DIR / subdir / f'{frag_id}.tex'
    with open(filepath, 'w') as f:
        f.write(tex_content)
    return filepath


# === MAIN.TEX GENERATION ===

FRAGMENT_ORDER = [
    # Part 1: Sertão
    'MEM-01', 'MEM-02', 'MEM-03', 'MEM-04', 'MEM-05', 'MEM-06', 'MEM-07',
    'DOC-17', 'DOC-18',
    # Part 2: Colônia
    'MEM-08', 'DOC-02', 'MEM-09', 'MEM-10', 'MEM-11',
    'MEM-17', 'MEM-18', 'MEM-12', 'MEM-21', 'MEM-19',
    'DOC-10', 'MEM-22', 'MEM-23', 'MEM-20', 'MEM-24', 'MEM-25',
    # Part 3: Diário de Oliveira + Laudos
    'DOC-01', 'DOC-03', 'DOC-04', 'DOC-05', 'DOC-06', 'DOC-07',
    'MEM-13', 'MEM-14', 'MEM-15', 'MEM-16', 'MEM-26',
    'DOC-11', 'DOC-12', 'DOC-13', 'DOC-14', 'DOC-15', 'DOC-16', 'DOC-19',
    # Part 4: Investigação Lúcia
    'DOC-08', 'DOC-09',
    'LUC-01', 'LUC-02', 'LUC-03', 'LUC-04', 'LUC-05',
    'LUC-Contraprova', 'LUC-Entrevista', 'LUC-Escolha',
    'LUC-06', 'LUC-07', 'LUC-08', 'LUC-09', 'LUC-10', 'LUC-11', 'LUC-12',
    # Part 5: Contaminação
    'CONT-01', 'CONT-02', 'CONT-03', 'CONT-04', 'CONT-05', 'CONT-06',
    'CONT-07', 'CONT-08', 'CONT-09', 'CONT-10', 'CONT-11', 'CONT-12', 'CONT-13',
    # Epilogue/after
    'MEM-27',
]

PARTS = [
    ('Sertão (1915–1928)', FRAGMENT_ORDER[:9], '9 fragmentos: MEM-01 a MEM-07, DOC-17, DOC-18'),
    ('Colônia (1928–1979)', FRAGMENT_ORDER[9:25], '16 fragmentos: MEM-08 a MEM-25, DOC-02, DOC-10'),
    ('Diário de Oliveira e Laudos (1979)', FRAGMENT_ORDER[25:43], '18 fragmentos: DOC-01, DOC-03 a DOC-07, MEM-13 a MEM-16, MEM-26, DOC-11 a DOC-16, DOC-19'),
    ('Investigação Lúcia (2026)', FRAGMENT_ORDER[43:61], '18 fragmentos: DOC-08, DOC-09, LUC-01 a LUC-12, LUC-Contraprova, LUC-Entrevista, LUC-Escolha'),
    ('Contaminação (Você)', FRAGMENT_ORDER[61:74], '13 fragmentos: CONT-01 a CONT-13'),
]

EPILOGUE_FRAGS = ['MEM-27']


def generate_main_tex():
    """Generate the complete main.tex."""
    total_frags = len(FRAGMENT_ORDER)

    lines = []
    lines.append('% ============================================')
    lines.append('% MOLAMBUDOS — O Diário do Paciente 1.260')
    lines.append(f'% Leitura Linear (completa) — {total_frags} fragmentos')
    lines.append(f'% Gerado por build_miolo.py em {subprocess.getoutput("date +%Y-%m-%d")}')
    lines.append('% ============================================')
    lines.append('')
    lines.append(r'\documentclass[12pt,openany]{book}')
    lines.append('')
    lines.append('% ---- PACOTES ----')
    lines.append(r'\usepackage[utf8]{inputenc}')
    lines.append(r'\usepackage[T1]{fontenc}')
    lines.append(r'\usepackage[brazilian]{babel}')
    lines.append(r'\usepackage{graphicx}')
    lines.append(r'\usepackage{amsmath,amssymb}')
    lines.append(r'\usepackage{booktabs}')
    lines.append(r'\usepackage[')
    lines.append(r'  colorlinks=true,')
    lines.append(r'  linkcolor=red!60!black,')
    lines.append(r'  citecolor=red!60!black,')
    lines.append(r'  urlcolor=red!60!black')
    lines.append(r']{hyperref}')
    lines.append(r'\usepackage{geometry}')
    lines.append(r'\geometry{paperwidth=16cm, paperheight=23cm, inner=1.5cm, outer=1.2cm, top=1.5cm, bottom=1.8cm}')
    lines.append(r'\usepackage{indentfirst}')
    lines.append(r'\usepackage{setspace}')
    lines.append(r'\usepackage{longtable}')
    lines.append(r'\usepackage{xcolor}')
    lines.append(r'\usepackage{fancyhdr}')
    lines.append(r'\usepackage{mathpazo}')
  #lines.append(r'\usepackage{ebgaramond}')  % fallback
    lines.append('')
    lines.append(r'\definecolor{sangue}{HTML}{8B0000}')
    lines.append(r'\definecolor{olho}{HTML}{FFD700}')
    lines.append(r'\definecolor{mem}{HTML}{8B4513}')
    lines.append(r'\definecolor{doc}{HTML}{2F4F4F}')
    lines.append(r'\definecolor{cont}{HTML}{8B0000}')
    lines.append(r'\definecolor{luc}{HTML}{4B0082}')
    lines.append('')
    lines.append(r'\linespread{1.15}')
    lines.append(r'\setlength{\parskip}{0pt}')
    lines.append(r'\setlength{\parindent}{1.2em}')
    lines.append(r'\setlength{\headheight}{14.5pt}')
    lines.append(r'\addtolength{\topmargin}{-2.5pt}')
    lines.append(r'\frenchspacing')
    lines.append('')
    lines.append('% Unicode support')
    lines.append(r'\DeclareUnicodeCharacter{21AA}{\ensuremath{\hookrightarrow}}')
    lines.append(r'\DeclareUnicodeCharacter{2610}{\ensuremath{\square}}')
    lines.append(r'\DeclareUnicodeCharacter{2713}{\checkmark}')
    lines.append(r'\DeclareUnicodeCharacter{2717}{\texttimes}')
    lines.append(r'\DeclareUnicodeCharacter{2611}{\ensuremath{\checkmark}}')
    lines.append(r'\DeclareUnicodeCharacter{2639}{\textfrown}')
    lines.append(r'\DeclareUnicodeCharacter{263A}{\textsmile}')
    lines.append(r'\DeclareUnicodeCharacter{2665}{\ensuremath{\heartsuit}}')
    lines.append(r'\DeclareUnicodeCharacter{2714}{\checkmark}')
    lines.append(r'\DeclareUnicodeCharacter{2605}{\bigstar}')
    lines.append(r'\DeclareUnicodeCharacter{2022}{\textbullet}')
    lines.append(r'\DeclareUnicodeCharacter{25CF}{\textbullet}')
    lines.append(r'\DeclareUnicodeCharacter{25CB}{\circ}')
    lines.append(r'\DeclareUnicodeCharacter{2192}{$\rightarrow$}')
    lines.append(r'\DeclareUnicodeCharacter{2190}{$\leftarrow$}')
    lines.append(r'\DeclareUnicodeCharacter{00B0}{$^\circ$}')
    lines.append(r'\DeclareUnicodeCharacter{2013}{--}')
    lines.append(r'\DeclareUnicodeCharacter{2014}{---}')
    lines.append(r'\DeclareUnicodeCharacter{2018}{`}')
    lines.append(r'\DeclareUnicodeCharacter{2019}{{}^\prime}')
    lines.append(r'\DeclareUnicodeCharacter{201C}{``}')
    lines.append(r'\DeclareUnicodeCharacter{201D}{"{}}')
    lines.append(r'\DeclareUnicodeCharacter{2194}{$\leftrightarrow$}')
    lines.append(r'\DeclareUnicodeCharacter{2716}{\texttimes}')
    lines.append(r'\DeclareUnicodeCharacter{274C}{\texttimes}')
    lines.append(r'\DeclareUnicodeCharacter{2705}{\checkmark}')
    lines.append(r'\DeclareUnicodeCharacter{2795}{+}')
    lines.append(r'\DeclareUnicodeCharacter{2796}{-}')
    lines.append(r'\widowpenalty=10000')
    lines.append(r'\clubpenalty=10000')
    lines.append('')
    lines.append(r'\title{Molambudos — O Diário do Paciente 1.260}')
    lines.append(r'\author{Marcelo Dias de Carvalho Filho}')
    lines.append(r'\date{2026}')
    lines.append('')
    lines.append(r'\pagestyle{fancy}')
    lines.append(r'\fancyhf{}')
    lines.append(r'\renewcommand{\headrulewidth}{0pt}')
    lines.append(r'\fancyfoot[C]{\thepage}')
    lines.append(r'\fancyhead[LE]{\itshape Molambudos}')
    lines.append(r'\fancyhead[RO]{\itshape Paciente 1.260}')
    lines.append('')
    lines.append(r'\begin{document}')
    lines.append('')
    lines.append(r'\maketitle')
    lines.append(r'\thispagestyle{empty}')
    lines.append(r'\newpage')
    lines.append('')
    lines.append(r'\tableofcontents')
    lines.append(r'\newpage')
    lines.append('')

    # --- Seção de Navegação ---
    lines.append('% ============================================')
    lines.append('% SEÇÃO DE NAVEGAÇÃO')
    lines.append('% ============================================')
    lines.append(r'\chapter*{Navegação — Rotas de Leitura}')
    lines.append(r'\addcontentsline{toc}{chapter}{Navegação}')
    lines.append('')
    lines.append(f'\\noindent\\textit{{Este livro contém {total_frags} fragmentos organizados em 5 partes.}}')
    lines.append(r'\textit{Cada fragmento é independente e pode ser lido em qualquer ordem.}')
    lines.append(r'\textit{As setas ↪ ao final de cada fragmento indicam rotas de leitura possíveis.}')
    lines.append(r'\textit{A leitura linear recomendada segue a ordem das partes abaixo.}')
    lines.append('')
    lines.append(r'\vspace{1em}')
    lines.append(r'\section*{Índice de Fragmentos}')
    lines.append(r'\newcommand{\fraglink}[3]{\noindent\hyperlink{#1}{\textbf{#1}} --- #2 \hfill {\small\itshape\textcolor{gray}{#3}}\\}')
    lines.append('')

    # Index by part
    part_boundaries = [0, 9, 25, 43, 61, 74]
    part_names = ['Sertão', 'Colônia', 'Diário de Oliveira e Laudos', 'Investigação Lúcia', 'Contaminação']
    part_years = ['1915', '1928–1979', '1979', '2026', 'Você']

    for idx, (pname, pyear) in enumerate(zip(part_names, part_years)):
        start = part_boundaries[idx]
        end = part_boundaries[idx + 1]
        count = end - start
        lines.append(f'\\subsection*{{Parte {idx+1} --- {pname} ({count} fragmentos)}}')
        lines.append(r'\begin{quote}\small')
        for fid in FRAGMENT_ORDER[start:end]:
            lines.append(f'\\fraglink{{{fid}}}{{}}{{\\hfill}}')
        lines.append(r'\end{quote}')
        lines.append('')

    lines.append(r'\newpage')
    lines.append('')

    # --- AVISO DE CONTEÚDO ---
    lines.append('% ============================================')
    lines.append('% AVISO DE CONTEÚDO')
    lines.append('% ============================================')
    lines.append(r'\chapter*{Aviso de Conteúdo}')
    lines.append(r'\addcontentsline{toc}{chapter}{Aviso de Conteúdo}')
    lines.append('')
    lines.append(r'\noindent Este livro é uma obra de ficção baseada em fatos históricos documentados --- o Holocausto Brasileiro (1930--1980), período em que mais de 60 mil pessoas morreram no Hospital Colônia de Barbacena e instituições similares. A obra não romantiza, não sensacionaliza e não explora esteticamente o sofrimento real --- mas o enfrenta com o rigor documental que a memória histórica exige.')
    lines.append('')
    lines.append(r'\noindent \textbf{A leitura pode evocar ou reativar desconforto relacionado a:}')
    lines.append(r'\begin{itemize}')
    lines.append(r'  \item Violência institucional e estatal')
    lines.append(r'  \item Tortura psicológica e física')
    lines.append(r'  \item Procedimentos médicos sem anestesia (eletrochoque, lobotomia)')
    lines.append(r'  \item Morte, caquexia, desnutrição')
    lines.append(r'  \item Isolamento social e privação sensorial')
    lines.append(r'  \item Transtornos psiquiátricos institucionalizados')
    lines.append(r'  \item Linguagem e cenas de teor corporal explícito (autópsia, violência)')
    lines.append(r'\end{itemize}')
    lines.append('')
    lines.append(r'\noindent Se você está em tratamento psicológico ou psiquiátrico, considere ler acompanhado ou em sessões curtas.')
    lines.append('')
    lines.append(r'\begin{quote}')
    lines.append(r'\textit{''O passado não está morto. Ele nem sequer passou.'' --- William Faulkner}')
    lines.append(r'\end{quote}')
    lines.append('')
    lines.append(r'\newpage')
    lines.append('')

    # --- PROTOCOLO DE LEITURA ---
    lines.append('% ============================================')
    lines.append('% PROTOCOLO DE LEITURA')
    lines.append('% ============================================')
    lines.append(r'\chapter*{Protocolo de Leitura}')
    lines.append(r'\addcontentsline{toc}{chapter}{Protocolo de Leitura}')
    lines.append('')
    lines.append(r'\noindent Este livro não é um romance linear. É um \textbf{arquivo contaminado}: fragmentos conectados por rotas de leitura possíveis.')
    lines.append('')
    lines.append(r'\noindent \textbf{As 4 vozes do arquivo:}')
    lines.append('')
    lines.append(r'\noindent\textcolor{mem}{MEM (Vermelho)} --- Joaquim (paciente): memórias do internamento (1917--1979)')
    lines.append(r'\noindent\textcolor{doc}{DOC (Azul)} --- Laudos, relatórios: documentos oficiais (1917--2026)')
    lines.append(r'\noindent\textcolor{luc}{LUC (Verde)} --- Lúcia Mendes (psicóloga): investigação forense (2026)')
    lines.append(r'\noindent\textcolor{cont}{CONT (Laranja)} --- A Contaminação: a metanarrativa (Agora)')
    lines.append('')
    lines.append(r'\noindent \textbf{Como ler (escolha seu perfil):}')
    lines.append('')
    lines.append(r'\noindent\textbf{Linear:} Siga os fragmentos em ordem numérica. O Arquivista organizou o arquivo para revelação gradual. --- Leitores de romance tradicional')
    lines.append(r'\noindent\textbf{Exploratório:} Siga os links ↪ no final de cada fragmento. Cada fragmento aponta para 2--3 outros. Você decide o caminho. --- Leitores experientes em narrativa não-linear')
    lines.append(r'\noindent\textbf{Guiado:} Consulte o mapa de rotas no final do arquivo para planejar sua rota. --- Leitores que querem controle sobre a experiência')
    lines.append('')
    lines.append(r'\noindent \textbf{Regras do arquivo:}')
    lines.append(r'\begin{enumerate}')
    lines.append(r'  \item MEM (memórias) levam a DOC (evidências) e LUC (investigações) --- a história se revela através dos documentos')
    lines.append(r'  \item DOC (documentos) podem levar a CONT (contaminação) --- cuidado ao abrir laudos')
    lines.append(r'  \item LUC (investigações) são a ponte entre o passado e o presente --- Lúcia investiga o que Joaquim viveu')
    lines.append(r'  \item CONT (contaminação) pode levar de volta a qualquer voz --- uma vez contaminado, todas as rotas convergem')
    lines.append(r'\end{enumerate}')
    lines.append('')
    lines.append(r'\noindent O ciclo recomeça a cada leitor. Ao final, você será o Paciente 1.263.')
    lines.append('')
    lines.append(r'\newpage')
    lines.append('')

    # --- ESCALA DE CONTAMINAÇÃO (original) ---
    lines.append('% ============================================')
    lines.append('% ESCALA DE CONTAMINAÇÃO')
    lines.append('% ============================================')
    lines.append(r'\chapter*{Escala de Contaminação do Leitor}')
    lines.append(r'\addcontentsline{toc}{chapter}{Escala de Contaminação}')
    lines.append('')
    lines.append(r'\begin{tabular}{|l|p{10cm}|}')
    lines.append(r'\hline')
    lines.append(r'Pontos & Diagnóstico \\')
    lines.append(r'\hline')
    lines.append(r'0--2 & Leitor resiliente. A contaminação não pegou. Ou você está mentindo. \\')
    lines.append(r'\hline')
    lines.append(r'3--5 & Leitor exposto. Sintomas iniciais. Recomenda-se pausa na leitura. \\')
    lines.append(r'\hline')
    lines.append(r'6--8 & Leitor contaminado. O ciclo está em andamento. O olho amarelo aparecerá em breve. \\')
    lines.append(r'\hline')
    lines.append(r'9--10 & Paciente 1.263. Bem-vindo. A criatura agradece sua atenção. \\')
    lines.append(r'\hline')
    lines.append(r'\end{tabular}')
    lines.append('')
    lines.append(r'\newpage')
    lines.append('')

    # --- PARTES COM FRAGMENTOS ---
    for pid, (pname, pfrags, pdesc) in enumerate(PARTS):
        lines.append(f'% ============================================')
        lines.append(f'% PARTE {pid+1} — {pname}')
        lines.append(f'% {pdesc}')
        lines.append(f'% ============================================')
        lines.append(f'\\part*{{{pname}}}')
        lines.append(f'\\addcontentsline{{toc}}{{part}}{{{pname}}}')
        lines.append('')

        for fid in pfrags:
            # Determine subdir for fragment
            if fid.startswith('MEM'):
                subdir = 'mem'
            elif fid.startswith('DOC'):
                subdir = 'doc'
            elif fid.startswith('LUC'):
                subdir = 'luc'
            else:
                subdir = 'cont'
            lines.append(f'\\newpage\\hypertarget{{{fid}}}{{}}\\input{{fragmentos/{subdir}/{fid}}}')
            lines.append('')

    # --- MEM-27 after everything ---
    lines.append(f'% ============================================')
    lines.append(f'% MEM-27 — Epílogo')
    lines.append(f'% ============================================')
    lines.append(f'\\newpage\\hypertarget{{MEM-27}}{{}}\\input{{fragmentos/mem/MEM-27}}')
    lines.append('')
    lines.append(r'\newpage')
    lines.append('')

    # --- DESTRUIÇÃO DA ESCALA (CP5) ---
    lines.append('% ============================================')
    lines.append('% ESCALA DE CONTAMINAÇÃO — DESTRUIÇÃO')
    lines.append('% ============================================')
    lines.append(r'\chapter*{Escala de Contaminação — Destruição}')
    lines.append(r'\addcontentsline{toc}{chapter}{Escala de Contaminação — Destruição}')
    lines.append('')
    lines.append(r'\noindent A escala não existe mais.')
    lines.append('')
    lines.append(r'\noindent Você leu até o fim.')
    lines.append('')
    lines.append(r'\noindent Não há mais pontos. Não há mais diagnóstico. Não há mais arquivo.')
    lines.append('')
    lines.append(r'\noindent \textbf{Paciente 1.263 — Você.}')
    lines.append('')
    lines.append(r'\begin{quote}')
    lines.append(r'\textit{A criatura não precisa mais de escala. Ela já tem nome, endereço e a memória da sua respiração enquanto lia.}')
    lines.append(r'\end{quote}')
    lines.append('')
    lines.append(r'\noindent O ciclo recomeça quando você fechar este arquivo e abrir na primeira página.')
    lines.append('')
    lines.append(r'\vspace{1em}')
    lines.append(r'\noindent --- \textit{O Arquivista}')
    lines.append('')

    # --- CLOSING ---
    lines.append(r'\newpage')
    lines.append(r'\thispagestyle{empty}')
    lines.append(r'\null')
    lines.append(r'\vfill')
    lines.append(r'\begin{center}')
    lines.append(r'\vspace*{\fill}')
    lines.append('')
    lines.append(f'\\textit{{Este livro contém {total_frags} fragmentos.}}')
    lines.append(r'\textit{Se você leu todos, o ciclo está completo em você.}')
    lines.append('')
    lines.append(r'\vspace{2em}')
    lines.append(r'\rule{0.2\textwidth}{0.5pt}')
    lines.append('')
    lines.append(r'\vspace{2em}')
    lines.append(r'\textit{A criatura agora está aqui.}')
    lines.append(r'\textit{Na página em branco.}')
    lines.append(r'\textit{Esperando o próximo leitor.}')
    lines.append('')
    lines.append(r'\vspace{2em}')
    lines.append(r'\textcolor{olho}{\large \textbf{1260}}')
    lines.append(r'\end{center}')
    lines.append(r'\vfill')
    lines.append('')
    lines.append(r'\end{document}')

    return '\n'.join(lines)


# === MAIN ===

def main():
    print("=" * 60)
    print("  Miolo Molambudos — Gerador LaTeX + PDF")
    print("=" * 60)

    # 1. Read markdown
    print(f"\n[1/7] Lendo {MOLAMBUROS}...")
    with open(MOLAMBUROS, 'r') as f:
        md_content = f.read()

    # 2. Parse fragments
    print("[2/7] Parsing fragmentos...")
    header, fragments = parse_fragments(md_content)
    print(f"  → {len(fragments)} fragmentos encontrados")

    # Map fragment IDs
    frag_map = {f['id']: f for f in fragments}
    found_ids = set(frag_map.keys())
    required_ids = set(FRAGMENT_ORDER)
    missing_ids = required_ids - found_ids
    extra_ids = found_ids - required_ids
    if missing_ids:
        print(f"  ⚠️ Faltando: {missing_ids}")
        # Create dummy fragments for missing ones
        for fid in missing_ids:
            frag_map[fid] = {'id': fid, 'lines': [f'Fragmento {fid} — conteúdo pendente.'], 'title': f'## {fid} — Pendente'}
    if extra_ids:
        print(f"  ⚠️ Extras (não na ordem): {extra_ids}")

    # 3. Write .tex files
    print("[3/7] Gerando arquivos .tex dos fragmentos...")
    written = 0
    for fid in FRAGMENT_ORDER:
        if fid in frag_map:
            tex_content, subdir = fragment_to_tex(frag_map[fid])
            filepath = FRAG_DIR / subdir / f'{fid}.tex'
            with open(filepath, 'w') as f:
                f.write(tex_content)
            written += 1
    print(f"  → {written} arquivos .tex escritos")

    # 4. Generate main.tex
    print("[4/7] Gerando main.tex...")
    main_tex_content = generate_main_tex()
    with open(MAIN_TEX, 'w') as f:
        f.write(main_tex_content)
    print(f"  → main.tex gerado ({len(main_tex_content.splitlines())} linhas)")

    # 5. Check for ebgaramond
    print("[5/7] Verificando fontes...")
    # Check if ebgaramond package is available
    result = subprocess.run(
        ['kpsewhich', 'ebgaramond.sty'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("  ⚠️ ebgaramond.sty não encontrado (mathpazo já configurado).")
    else:
        print("  ✓ ebgaramond disponível (usando mathpazo como padrão)")

    # 6. Run pdflatex (twice for cross-refs)
    print("[6/7] Compilando com pdflatex...")
    os.chdir(BASE_DIR)
    for pass_num in [1, 2]:
        print(f"  → Passada {pass_num}...")
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', 'main.tex'],
            capture_output=True, text=True, timeout=120,
            encoding='latin-1', errors='replace'
        )
        # Check for critical errors (not just warnings)
        if result.returncode != 0:
            # Extract errors from log
            errors = [l for l in result.stdout.split('\n') if l.startswith('!')]
            if errors:
                print(f"  ⚠️ {len(errors)} erro(s) na passada {pass_num}:")
                for e in errors[:10]:
                    print(f"    {e[:120]}")

    # 7. Check result
    print("[7/7] Verificando PDF...")
    if MAIN_PDF.exists():
        size_kb = MAIN_PDF.stat().st_size / 1024
        pages = 0
        # Try to get page count
        result = subprocess.run(
            ['pdfinfo', str(MAIN_PDF)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Pages' in line:
                    pages = int(line.split(':')[1].strip())
        print(f"\n{'='*60}")
        print(f"  ✅ PDF GERADO COM SUCESSO!")
        print(f"  📄 {MAIN_PDF}")
        print(f"  📏 {size_kb:.0f} KB | {pages} páginas")
        print(f"  📊 {written} fragmentos | {len(FRAGMENT_ORDER)} no índice")
        print(f"{'='*60}")
    else:
        print(f"\n  ❌ main.pdf não foi gerado. Verifique os logs em main.log")
        # Show last 20 errors
        log_path = BASE_DIR / 'main.log'
        if log_path.exists():
            with open(log_path) as f:
                log_content = f.read()
            # Find LaTeX errors
            for line in log_content.split('\n'):
                if line.startswith('!') or 'Error' in line:
                    print(f"  {line[:150]}")


if __name__ == '__main__':
    main()
