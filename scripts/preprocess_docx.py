#!/usr/bin/env python3
"""Pré-processa banca_mestrado_educacao_campo.tex -> Markdown para pandoc (DOCX).
Converte ambientes abntex2 (quadro/siglas/citacao/resumo), resolve \\ref e
normaliza \\cite* para citeproc (\\citet/\\citep)."""
import re, sys

src = open('banca_mestrado_educacao_campo.tex', encoding='utf-8').read()

# 1) Corpo (entre begin/end document)
body = src.split(r'\begin{document}', 1)[1].split(r'\end{document}', 1)[0]

# 2) Captura comandos institucionais para gerar capa/folha manual
def grab_cmd_balanced(name):
    """Captura \\name{...} lidando com chaves aninhadas."""
    m = re.search(r'\\' + name + r'\{', body)
    if not m:
        return ''
    i = m.end()
    depth = 1
    start = i
    while i < len(body) and depth > 0:
        if body[i] == '{':
            depth += 1
        elif body[i] == '}':
            depth -= 1
        i += 1
    return body[start:i-1]

titulo   = grab_cmd_balanced('titulo')
titulo_e = grab_cmd_balanced('tituloestrangeiro')
autor    = grab_cmd_balanced('autor')
local    = grab_cmd_balanced('local')
data     = grab_cmd_balanced('data')
orient   = grab_cmd_balanced('orientador')
preambulo = grab_cmd_balanced('preambulo')

# limpa \thanks{...} (emails)
emails_m = re.findall(r'\\thanks\{([^}]*)\}', autor)
autor_clean = re.sub(r'\\thanks\{[^}]*\}', '', autor).replace('\\\\', ' e ')
inst = '[Instituição de Ensino Superior]'

# Remove comandos institucionais do corpo (estão em linhas próprias no .tex)
for cmd in ['tituloestrangeiro', 'titulo', 'autor', 'local', 'data',
            'orientador', 'preambulo', 'instituicao']:
    body = re.sub(r'^\\' + cmd + r'\{.*\}.*$', '', body, flags=re.M)

# 3) Remove comandos de capa/folha de rosto (serão gerados manualmente)
body = re.sub(r'\\imprimircapa\s*', '', body)
body = re.sub(r'\\imprimirfolhaderosto\s*', '', body)
body = re.sub(r'\\imprimirpreambulo\s*', '', body)

# 4) Folha de aprovação -> texto
def aprova(m):
    inner = m.group(1)
    inner = inner.replace(r'\imprimirautor', autor_clean)
    inner = inner.replace(r'\imprimirtitulo', titulo)
    inner = inner.replace(r'\imprimirlocal', local)
    inner = inner.replace(r'\imprimirdata', data)
    # assinaturas
    inner = re.sub(r'\\assinatura\{([^}]*)\}', r'\n\n________________________________________\n\n\1', inner)
    for c in [r'\begin{center}', r'\end{center}', r'\vspace*{\fill}', r'\vfill',
              r'\begin{minipage}{.5\textwidth}', r'\end{minipage}',
              r'\hspace{.45\textwidth}', r'\par', '\\textbf{', '}']:
        inner = inner.replace(c, '')
    inner = inner.replace('{', '')  # remove agrupamentos órfãos
    inner = inner.replace('%', '')  # remove comentários residuais
    # remove indentação de linhas (evita code block no pandoc)
    inner = '\n'.join(ln.lstrip() for ln in inner.split('\n'))
    return '# Folha de Aprovação\n\n' + inner.strip()
body = re.sub(r'\\begin\{folhadeaprovacao\}(.*?)\\end\{folhadeaprovacao\}', aprova, body, flags=re.S)

# 5) Resumo / Abstract
def resumo(m):
    try:
        title = m.group(1).strip() or 'Resumo'
        inner = m.group(2)
    except IndexError:
        title = 'Resumo'
        inner = m.group(1)
    # remove otherlanguage* com {english} ou {french}...
    inner = re.sub(r'\\begin\{otherlanguage\*\}\{[^}]*\}', '', inner)
    inner = re.sub(r'\\end\{otherlanguage\*\}', '', inner)
    inner = inner.replace(r'\noindent', '').replace(r'\vspace{\onelineskip}', '')
    inner = re.sub(r'\\textbf\{Palavras-chave\}', '**Palavras-chave**', inner)
    inner = re.sub(r'\\textbf\{Keywords\}', '**Keywords**', inner)
    return f"# {title}\n\n{inner.strip()}"
body = re.sub(r'\\begin\{resumo\}\s*\[([^]]*)\]\s*(.*?)\\end\{resumo\}', lambda m: resumo(m), body, flags=re.S)
body = re.sub(r'\\begin\{resumo\}(.*?)\\end\{resumo\}', lambda m: resumo(m), body, flags=re.S)

# 6) Siglas
def siglas(m):
    items = re.findall(r'\\item\[([^\]]*)\]\s*([^\n]*)', m.group(1))
    out = ['# Lista de Abreviaturas e Siglas', '']
    for k, v in items:
        out.append(f'* **{k}** — {v.strip()}')
    return '\n'.join(out)
body = re.sub(r'\\begin\{siglas\}(.*?)\\end\{siglas\}', siglas, body, flags=re.S)

# 7) Quadro -> tabela markdown + legenda + fonte
def tabular_to_md(tab):
    tab = re.sub(r'\\begin\{tabularx?\}.*?\}', '', tab, count=1)
    tab = re.sub(r'\\end\{tabularx?\}', '', tab)
    # Processa linha a linha (separador \\ é fim de linha do LaTeX)
    rows = []
    pending = ''
    for raw in tab.split('\n'):
        ln = raw.strip()
        if not ln:
            continue
        # descarta linha de especificador de colunas {>{\RaggedRight...X}
        if 'arraybackslash' in ln and '&' not in ln:
            pending = ''
            continue
        # remove especificador residual do início da linha
        ln = re.sub(r'^\{>.*?\}\s*', '', ln)
        ln = ln.replace(r'\hline', '').strip()
        if not ln:
            pending = ''
            continue
        # se não termina em \\, acumula (célula multilinha); senão fecha a linha
        if ln.endswith(r'\\'):
            cell_src = pending + ' ' + ln[:-2] if pending else ln[:-2]
            # fallback: se a linha contém &, trata como linha pronta
            row = cell_src if '&' in cell_src else ln[:-2] if '&' in ln else None
            if row is not None:
                row = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', row)
                cells = [c.strip() for c in row.split('&')]
                rows.append(cells)
            pending = ''
        else:
            pending = (pending + ' ' + ln).strip()
    if not rows:
        return ''
    lines = ['| ' + ' | '.join(rows[0]) + ' |']
    lines.append('|' + '|'.join([' --- '] * len(rows[0])) + '|')
    for r in rows[1:]:
        lines.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(lines)

qcount = [0]
def quadro(m):
    inner = m.group(1)
    cap = re.search(r'\\caption\{([^}]*)\}', inner)
    cap = cap.group(1) if cap else 'Quadro'
    qcount[0] += 1
    fonte = re.search(r'\\fonte\{([^}]*)\}', inner)
    fonte = fonte.group(1) if fonte else ''
    tab = re.search(r'\\begin\{tabularx\}.*?\\end\{tabularx\}', inner, flags=re.S)
    if not tab:
        tab = re.search(r'\\begin\{tabular\}.*?\\end\{tabular\}', inner, flags=re.S)
    md = tabular_to_md(tab.group(0)) if tab else ''
    out = [f'**Quadro {qcount[0]} – {cap}**', '', md, '']
    if fonte:
        out.append(f'Fonte: {fonte}')
    out.append('')
    return '\n'.join(out)
body = re.sub(r'\\begin\{quadro\}(.*?)\\end\{quadro\}', quadro, body, flags=re.S)

# 8) Citações longas -> blockquote (com optional [default] e \cite[p.x]{k})
def citacao(m):
    inner = m.group(1)
    # \cite[p.~8]{x} -> (AUTOR, p. 8) já via citeproc; aqui mantemos como citação
    inner = re.sub(r'\\cite(\[[^\]]*\])?\{[^}]*\}', '', inner)
    inner = re.sub(r'``|"', '"', inner)
    inner = re.sub(r'^\[default\]\s*', '', inner)
    inner = re.sub(r'\n{2,}', '\n', inner.strip())
    return '\n> ' + inner.replace('\n', '\n> ')
body = re.sub(r'\\begin\{citacao\}(.*?)\\end\{citacao\}', citacao, body, flags=re.S)

# 9) Citações: \citeonline{a,b} -> \citet{a,b}; \cite -> \citep (citeproc)
body = re.sub(r'\\citeonline(\[[^\]]*\])?\{([^}]*)\}', r'\\citet\1{\2}', body)
# \citep com optional e sem
body = re.sub(r'(?<!\\citet)\\[Cc]ite(\[[^\]]*\])?\{([^}]*)\}', r'\\citep\1{\2}', body)

# 9b) Citações -> sintaxe citeproc do pandoc
# \citet[p. 19]{a} -> @a [p. 19]   ; \citet{a,b} -> @a; @b   (textual: Autor (ano))
def citet_to_pandoc(m):
    loc = m.group(1)
    keys = '; '.join('@' + k.strip() for k in m.group(2).split(','))
    if loc:
        return f'{keys} [{loc.strip("[]")}]'
    return keys
body = re.sub(r'\\citet(\[[^\]]*\])?\{([^}]*)\}', citet_to_pandoc, body)
# \citep[p. 19]{a} -> [@a, p. 19]   ; \citep{a,b} -> [@a; @b]
def citep_to_pandoc(m):
    loc = m.group(1)
    keys = '; '.join('@' + k.strip() for k in m.group(2).split(','))
    if loc:
        loc_clean = loc.strip('[]')
        return f'[{keys}, {loc_clean}]'
    return f'[{keys}]'
body = re.sub(r'\\citep(\[[^\]]*\])?\{([^}]*)\}', citep_to_pandoc, body)

# 10) References de quadros -> números
body = body.replace(r'\ref{qua:quadro1}', '1').replace(r'\ref{qua:coletadocumental}', '2')

# 10b) \section / \subsection -> headings markdown
body = re.sub(r'\\section\{([^}]*)\}', r'# \1', body)
body = re.sub(r'\\subsection\{([^}]*)\}', r'## \1', body)

# 11) Remover comandos LaTeX restantes irrelevantes
drop = [r'\\setlength\{[^}]*\}\{[^}]*\}', r'\\pdfbookmark\[[^\]]*\]\{[^}]*\}\{[^}]*\}',
        r'\\tableofcontents\*?', r'\\listofquadros\*?', r'\\cleardoublepage',
        r'\\textual', r'\\pretextual', r'\\postextual',
        r'\\renewcommand\{[^}]*\}\{[^}]*\}', r'\\small', r'\\vspace\{[^}]*\}',
        r'\\begin\{center\}', r'\\end\{center\}', r'\\noindent', r'\\par',
        r'\\itemsep', r'\\absparsep', r'\\onehalfspacing',
        r'^%.*$']  # comentários LaTeX
for pat in drop:
    body = re.sub(pat, '', body, flags=re.M)
keep = [ (r'\\textit\{([^}]*)\}', r'\1'), (r'\\emph\{([^}]*)\}', r'\1'),
         (r'\\url\{([^}]*)\}', r'\1'), (r'\\textbf\{([^}]*)\}', r'\1') ]
for pat, rep in keep:
    body = re.sub(pat, rep, body)

# 11b) Normalizações de texto: travessão e ~ (espaço inquebrável)
body = body.replace(' -- ', ' – ')
body = body.replace('~', ' ')

# 12) Capa e folha de rosto em markdown
sh = '#' * 80
capa = f"""# {titulo}

{autor_clean}

_E-mails: {'; '.join(emails_m)}_ (não constam na versão impressa)

{local} – {data}
"""
# preâmbulo vira epígrafe da folha de rosto
flr = f"""# Folha de Rosto

*{preambulo}*

{local} – {data}
"""
body = capa + '\n' + flr + '\n' + body

# 13) Sumário automático (pandoc --toc)
full = body.strip()
open('banca_mestrado_educacao_campo_body.md', 'w', encoding='utf-8').write(full)
print('OK -> banca_mestrado_educacao_campo_body.md')
print('Questões convertidas:', qcount[0])