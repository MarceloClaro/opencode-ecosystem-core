#!/usr/bin/env python3
"""
Pre-processa o LaTeX do Molambudos para conversão ePub via pandoc.
Abordagem robusta: resolve includes, remove comandos customizados,
e gera Markdown intermediário reflowable para ePub.
"""

import re
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return ""

def resolve_includes(content, depth=0, max_depth=20, processed=None):
    if processed is None:
        processed = set()
    if depth > max_depth:
        return content
    
    def replace_include(match):
        name = match.group(1) or match.group(2)
        candidates = [
            os.path.join(BASE_DIR, name + '.tex'),
            os.path.join(BASE_DIR, name),
        ]
        if '/' in name:
            candidates.insert(0, os.path.join(BASE_DIR, name + '.tex'))
        
        for cand in candidates:
            norm = os.path.normpath(cand)
            if norm in processed:
                return ""
            if os.path.isfile(norm):
                processed.add(norm)
                sub = read_file(norm)
                sub = resolve_includes(sub, depth+1, max_depth, processed)
                return f"\n% --- {name} ---\n{sub}\n% --- end {name} ---\n"
        
        print(f"  AVISO: include/input {{{name}}} não encontrado")
        return ""
    
    content = re.sub(
        r'\\(?:include|input)\{([^}]+)\}',
        replace_include,
        content
    )
    return content

def extract_body(content):
    """Extrai conteúdo entre \\begin{document} e \\end{document}."""
    m = re.search(r'\\begin{document}\n?(.*)\\end{document}', content, re.DOTALL)
    if m:
        return m.group(1)
    return content

def convert_to_epub_markdown(content):
    """
    Converte LaTeX complexo para Markdown que pandoc entende.
    Remove comandos customizados, converte os especiais.
    """
    lines = content.split('\n')
    out = []
    skip_custom_macro = False
    
    for line in lines:
        # Remover definições multilineares de macros do passaporte.
        # Elas não devem aparecer no ePub; apenas as chamadas das macros.
        if skip_custom_macro:
            if 'vspace' in line and '}}' in line:
                skip_custom_macro = False
            continue
        if re.match(r'^\s*\\newcommand\{\\(?:passaporte|passaportecont|passaporteluc|passaportedoc)\}', line):
            skip_custom_macro = True
            continue

        # --- REMOÇÕES GLOBAIS ---
        
        # Remover comentários inteiros
        if re.match(r'^\s*%', line):
            continue
        
        # Remover linhas de tikzpicture e afins
        if any(x in line for x in ['tikzpicture', '\\fill[', '\\node', '\\pgfornament']):
            continue
        
        # Remover comandos de página/estilo
        line = re.sub(r'\\thispagestyle\{[^}]*\}', '', line)
        line = re.sub(r'\\addcontentsline\{[^}]*\}\{[^}]*\}\{[^}]*\}', '', line)
        line = re.sub(r'\\markboth\{[^}]*\}\{[^}]*\}', '', line)
        
        # Converter ambientes simples antes de remover comandos
        line = re.sub(r'\\subsubsection\*\{([^}]*)\}', r'#### \1', line)
        line = re.sub(r'\\begin\{itemize\}', '', line)
        line = re.sub(r'\\end\{itemize\}', '', line)
        line = re.sub(r'\\begin\{enumerate\}', '', line)
        line = re.sub(r'\\end\{enumerate\}', '', line)
        line = re.sub(r'\\begin\{center\}', '', line)
        line = re.sub(r'\\end\{center\}', '', line)
        line = re.sub(r'\\begin\{minipage\}\{[^}]*\}', '', line)
        line = re.sub(r'\\end\{minipage\}', '', line)
        line = re.sub(r'\\item\s*', '- ', line)
        line = re.sub(r'\\texttt\{([^}]*)\}', r'`\1`', line)

        # Remover espaçamento vertical/horizontal
        line = re.sub(r'\\[vh]space\*?\{[^}]*\}', '', line)
        line = re.sub(r'\\hfill', ' ', line)
        line = re.sub(r'\\dotfill', '...', line)

        # Converter quebra de linha LaTeX (\\ ou \\[...]) em espaço textual
        line = re.sub(r'\\\\(?:\[[^\]]*\])?', ' ', line)
        
        # Remover \rule
        line = re.sub(r'\\rule(?:\[[^\]]*\])?\{[^}]*\}\{[^}]*\}', '', line)
        
        # Remover \noindent
        line = re.sub(r'\\noindent', '', line)
        
        # Remover labels, refs, pageref
        line = re.sub(r'\\label\{[^}]*\}', '', line)
        line = re.sub(r'\\ref\{[^}]*\}', '', line)
        line = re.sub(r'\\pageref\{[^}]*\}', '', line)
        
        # Remover \setlength, \renewcommand
        line = re.sub(r'\\setlength\{[^}]*\}\{[^}]*\}', '', line)
        line = re.sub(r'\\renewcommand\{[^}]*\}(?:\[[^\]]*\])?\{[^}]*\}', '', line)
        
        # Remover \newcommand
        line = re.sub(r'\\newcommand\{[^}]*\}(?:\[[^\]]*\])?\{[^}]*\}', '', line)
        
        # Remover \fbox, \rotatebox, \includegraphics avulsos
        line = re.sub(r'\\fbox\{', '', line)
        line = re.sub(r'\\rotatebox\{[^}]*\}\{', '', line)
        
        # --- CONVERSÕES ---
        
        # \textcolor{color}{text} → text
        line = re.sub(r'\\textcolor\{[^}]*\}\{([^}]*)\}', r'\1', line)

        # \lettrine[opts]{A}{bc} → Abc
        # Após remover \textcolor, o argumento inicial fica simples.
        line = re.sub(r'\\lettrine(?:\[[^\]]*\])?\{([^}]*)\}\{([^}]*)\}', r'\1\2', line)
        
        # \fragicon{x} → remove
        line = re.sub(r'\\fragicon\{[^}]*\}', '', line)
        
        # \partopener{a}{b}{c} → ## a
        line = re.sub(r'\\partopener\{([^}]*)\}\{[^}]*\}\{[^}]*\}', r'# \1', line)
        
        # \section*{x} → ## x
        line = re.sub(r'\\section\*\{([^}]*)\}', r'## \1', line)
        
        # \subsection*{x} → ### x
        line = re.sub(r'\\subsection\*\{([^}]*)\}', r'### \1', line)
        
        # \textbf{text} → **text**
        line = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', line)
        
        # \textit{text} → *text*
        line = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', line)
        
        # \emph{text} → *text*
        line = re.sub(r'\\emph\{([^}]*)\}', r'*\1*', line)
        
        # \textquotedbl → "
        line = line.replace('\\textquotedbl{}', '"')
        line = line.replace('\\textquotedbl', '"')
        
        # \textquoteleft → '
        line = line.replace('\\textquoteleft{}', "'")
        line = line.replace('\\textquoteleft', "'")
        
        # \textquoteright → '
        line = line.replace('\\textquoteright{}', "'")
        line = line.replace('\\textquoteright', "'")
        
        # \textendash → --
        line = line.replace('\\textendash{}', '--')
        line = line.replace('\\textendash', '--')
        
        # \textemdash → ---
        line = line.replace('\\textemdash{}', '---')
        line = line.replace('\\textemdash', '---')
        
        # --- Comandos do livro para texto simples ---
        
        # \rota{ID} → ID
        line = re.sub(r'\\rota\{([^}]*)\}', r'\1', line)
        
        # \rotasep → •
        line = line.replace('\\rotasep', ' • ')
        
        # \rotaphantom → remove
        line = re.sub(r'\\rotaphantom\{[^}]*\}', '', line)
        
        # \hyperlink{x}{text} → text
        line = re.sub(r'\\hyperlink\{[^}]*\}\{([^}]*)\}', r'\1', line)
        
        # \hypertarget{x}{text} → text
        line = re.sub(r'\\hypertarget\{[^}]*\}\{([^}]*)\}', r'\1', line)
        
        # \url{url} → url
        line = re.sub(r'\\url\{([^}]*)\}', r'\1', line)
        
        # \includegraphics[opts]{file} → ![image](file)
        line = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}', r'![](\1)', line)
        
        # \newpage, \cleardoublepage, \clearpage → ---
        if re.match(r'^\s*\\(?:newpage|cleardoublepage|clearpage)\s*$', line):
            out.append('')
            out.append('---')
            out.append('')
            continue
        
        # --- REMOVER CHAVES DE AGRUPAMENTO DESNECESSÁRIAS ---
        # Remover { } ao redor de comandos quando não afetam sentido
        
        # \small\textbf{...} → **...**  (comando \small removido)
        line = re.sub(r'\\small', '', line)
        line = re.sub(r'\\footnotesize', '', line)
        line = re.sub(r'\\large', '', line)
        line = re.sub(r'\\Large', '', line)
        line = re.sub(r'\\LARGE', '', line)
        line = re.sub(r'\\huge', '', line)
        line = re.sub(r'\\Huge', '', line)
        line = re.sub(r'\\normalfont', '', line)
        line = re.sub(r'\\itshape', '', line)
        line = re.sub(r'\\scshape', '', line)
        line = re.sub(r'\\bfseries', '', line)
        line = re.sub(r'\\centering', '', line)
        
        # \textquotedbl → "
        line = line.replace('\\textquotedbl{}', '"')
        
        # \& → &
        line = line.replace('\\&', '&')
        
        # \% → %
        line = line.replace('\\%', '%')
        
        # \_ → _
        line = line.replace('\\_', '_')
        
        # \vfill → remove
        line = re.sub(r'\\vfill', '', line)
        
        # \color{x} → remove
        line = re.sub(r'\\color\{[^}]*\}', '', line)
        
        # Custom metadata commands (definidos no preâmbulo, agora removido)
        line = line.replace('\\authorname', 'Marcelo Dias de Carvalho Filho')
        line = line.replace('\\coauthorname', '')
        line = line.replace('\\booktitle', 'Molambundos — O Diário do Paciente 1.260')
        line = line.replace('\\publisher', 'Selo Molambundos')
        line = line.replace('\\publishercity', '')
        line = line.replace('\\editionyear', '2026')
        line = line.replace('\\subtitle', '')
        line = line.replace('\\thepage', '')
        
        # --- passaporte macros → texto plano ---
        line = re.sub(r'\\passaporte\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', r'✦ \1 \2 (\3)', line)
        line = re.sub(r'\\passaportecont\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', r'● \1 \2', line)
        line = re.sub(r'\\passaporteluc\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', r'★ \1 \2 (\3)', line)
        line = re.sub(r'\\passaportedoc\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', r'◆ \1 \2 (\3)', line)
        
        # Remover $...$ (matemática inline) que pode confundir
        # (cuidado: algumas podem ser intencionais)
        # line = re.sub(r'\$[^$]*\$', '', line)
        
        # Remover ambientes remanescentes que não fazem sentido no ePub
        line = re.sub(r'\\begin\{[^}]*\}', '', line)
        line = re.sub(r'\\end\{[^}]*\}', '', line)

        # Remover comandos LaTeX simples remanescentes, preservando texto após
        # quebras LaTeX já convertidas. Ex.: \copyright -> copyright.
        line = re.sub(r'\\copyright', '©', line)
        line = re.sub(r'\\bigstar', '★', line)
        line = re.sub(r'\\cdot', '·', line)
        line = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?', '', line)

        # Remover chaves LaTeX órfãs restantes.
        line = line.replace('{', '').replace('}', '')

        # Limpar espaços múltiplos
        line = re.sub(r'  +', ' ', line)
        
        # Limpar espaços no início da linha
        line = line.lstrip()
        
        out.append(line)
    
    # Pós-processamento: juntar linhas
    result = '\n'.join(out)
    
    # Remover linhas que são só espaços ou pontuação
    result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
    
    return result

def main():
    main_path = os.path.join(BASE_DIR, 'main.tex')
    output_path = os.path.join(BASE_DIR, 'main.epub.md')
    
    print(f"1. Lendo {main_path}...")
    content = read_file(main_path)
    if not content:
        print("ERRO: main.tex vazio!")
        sys.exit(1)
    
    print(f"2. Resolvendo includes/inputs...")
    flat = resolve_includes(content)
    
    print(f"3. Extraindo body (pós \\\\begin{{document}})...")
    body = extract_body(flat)
    
    print(f"4. Convertendo para Markdown ePub-safe...")
    pandoc_ready = convert_to_epub_markdown(body)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pandoc_ready)
    
    lines = pandoc_ready.count('\n')
    chars = len(pandoc_ready)
    
    print(f"\n✅ Arquivo gerado: {output_path}")
    print(f"   {lines} linhas, {chars} caracteres")
    
    # Verificar comandos LaTeX remanescentes
    remaining = set(re.findall(r'\\[a-zA-Z]+', pandoc_ready))
    # Filtrar comandos padrão que pandoc entende
    known = {'begin', 'end', 'textbf', 'textit', 'emph', 'chapter', 'section', 'subsection',
             'subsubsection', 'paragraph', 'item', 'enumerate', 'itemize', 'description',
             'ref', 'label', 'cite', 'footnote', 'em', 'textsc', 'texttt', 'textsf',
             'textsl', 'texttt', 'textmd', 'textnormal', 'textrm', 'textup'}
    unknown = [c for c in remaining if c[1:] not in known]
    if unknown:
        print(f"\n⚠️  {len(unknown)} comandos desconhecidos remanescentes:")
        for c in sorted(unknown)[:20]:
            print(f"    {c}")
        if len(unknown) > 20:
            print(f"    ... e mais {len(unknown)-20}")
    else:
        print("\n✅ Nenhum comando desconhecido remanescente!")

if __name__ == '__main__':
    main()
