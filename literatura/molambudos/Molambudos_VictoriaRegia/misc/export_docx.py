#!/usr/bin/env python3
"""Export Molambudos LaTeX fragments to DOCX via Markdown.

Reads main.tex for fragment order, converts each .tex fragment
to clean Markdown, and outputs a .docx via Pandoc.
"""

import re
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MISC = BASE / "misc"
MD_OUT = MISC / "main_export.md"
DOCX_OUT = BASE / "main.docx"

# ── Fragment input order (parsed from main.tex) ──────────────────────────

def parse_fragment_order(main_tex: Path) -> list[tuple[str, str, str]]:
    """Return list of (part_label, fragment_id, file_path)."""
    order = []
    current_part = ""
    frag_pattern = re.compile(
        r'\\hypertarget\{(\w+-\d+)\}\{\}.*?\\input\{([^}]+)\}'
    )
    part_pattern = re.compile(r'\\part\*\{(.+?)\}')
    
    with open(main_tex, encoding="utf-8") as f:
        for line in f:
            pm = part_pattern.search(line)
            if pm:
                current_part = pm.group(1)
            fm = frag_pattern.search(line)
            if fm:
                order.append((current_part, fm.group(1), fm.group(2)))
    return order


# ── LaTeX → Markdown conversion ─────────────────────────────────────────

def strip_latex_markup(text: str) -> str:
    """Convert a fragment .tex content to clean Markdown."""
    # Save section headers before processing
    # section*{\textbf{ID} --- Title}
    text = re.sub(
        r'\\section\*\{\\textbf\{([^}]+)\}\s*---\s*([^}]+)\}',
        r'## \1 — \2',
        text
    )
    # section*{Title}
    text = re.sub(
        r'\\section\*\{([^}]+)\}',
        r'## \1',
        text
    )
    # subsubsection*{Title}
    text = re.sub(
        r'\\subsubsection\*\{([^}]+)\}',
        r'### \1',
        text
    )
    
    # Remove \markboth
    text = re.sub(r'\\markboth\{[^}]*\}\{[^}]*\}', '', text)
    
    # Remove \noindent
    text = re.sub(r'\\noindent', '', text)
    
    # \textbf{...} → **...**
    text = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', text)
    
    # \textit{...} → *...* (only if not already inside formatting)
    text = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', text)
    
    # \texttt{...} → `...`
    text = re.sub(r'\\texttt\{([^}]*)\}', r'`\1`', text)
    
    # \textquotedbl{} → "
    text = re.sub(r'\\textquotedbl\{\}', '"', text)
    text = re.sub(r'\{\\textquotedbl\}', '"', text)
    text = re.sub(r"\\textquoteleft\{\}", "'", text)
    text = re.sub(r"\\textquoteright\{\}", "'", text)
    
    # \textcolor{color}{text} → text
    text = re.sub(r'\\textcolor\{[^}]*\}\{([^}]*)\}', r'\1', text)
    
    # \hyperlink{id}{text} → text (or markdown link)
    text = re.sub(r'\\hyperlink\{[^}]*\}\{([^}]*)\}', r'\1', text)
    
    # \rule{w}{h} → ---
    text = re.sub(r'\\rule\{[^}]*\}\{[^}]*\}', '---', text)
    
    # Remove \fragicon{type} (ícone por grupo de fragmento)
    text = re.sub(r'\\fragicon\{[^}]*\}', '', text)
    
    # Remove \vspace, \hspace, \vfill
    text = re.sub(r'\\vspace\*?\{[^}]*\}', '', text)
    text = re.sub(r'\\hspace\*?\{[^}]*\}', '', text)
    text = re.sub(r'\\vfill', '', text)
    text = re.sub(r'\\vspace\*?\{\\fill\}', '', text)
    
    # Remove \includegraphics
    text = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}', '', text)
    
    # Remove \fbox{...} — handle balanced braces version
    def balanced_sub(s, prefix, rfunc):
        """Apply rfunc to content after prefix with balanced brace matching."""
        result = []
        i = 0
        while i < len(s):
            if s[i:i+len(prefix)] == prefix:
                depth = 1
                j = i + len(prefix)
                while j < len(s) and depth > 0:
                    if s[j] == '{': depth += 1
                    elif s[j] == '}': depth -= 1
                    j += 1
                result.append(rfunc(s[i+len(prefix):j-1]))
                i = j
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)
    
    def unwrap_fbox_content(inner):
        inner = re.sub(r'\\begin\{minipage\}\{[^}]*\}', '', inner)
        inner = re.sub(r'\\end\{minipage\}', '', inner)
        inner = re.sub(r'\\begin\{center\}', '', inner)
        inner = re.sub(r'\\end\{center\}', '', inner)
        return inner.strip()
    
    text = balanced_sub(text, '\\fbox{', unwrap_fbox_content)
    # Remove standalone minipage environments (non-nested)
    text = re.sub(r'\\begin\{minipage\}\{[^}]*\}(.*?)\\end\{minipage\}', r'\1', text, flags=re.DOTALL)
    
    # Remove \begin{titlepage}...\end{titlepage}
    text = re.sub(r'\\begin\{titlepage\}.*?\\end\{titlepage\}', '', text, flags=re.DOTALL)
    
    # Convert itemize
    text = re.sub(r'\\begin\{itemize\}', '', text)
    text = re.sub(r'\\end\{itemize\}', '', text)
    text = re.sub(r'\\item\b', '-', text)
    
    # Convert quote environment to blockquote
    text = re.sub(r'\\begin\{quote\}', '', text)
    text = re.sub(r'\\end\{quote\}', '', text)
    text = re.sub(r'\\raggedright', '', text)
    
    # Convert center environment
    text = re.sub(r'\\begin\{center\}', '', text)
    text = re.sub(r'\\end\{center\}', '', text)
    
    # Remove \newpage, \cleardoublepage, \null
    text = re.sub(r'\\newpage', '\n\n', text)
    text = re.sub(r'\\cleardoublepage', '\n\n', text)
    text = re.sub(r'\\null', '', text)
    text = re.sub(r'\\thispagestyle\{[^}]*\}', '', text)
    text = re.sub(r'\\pagestyle\{[^}]*\}', '', text)
    
    # Remove stray \begin/\end environments (minipage, center, etc.)
    text = re.sub(r'\\begin\{minipage\}\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{minipage\}', '', text)
    
    # Remove \addcontentsline
    text = re.sub(r'\\addcontentsline\{[^}]*\}\{[^}]*\}\{[^}]*\}', '', text)
    
    # Convert \lettrine to DROP_CAP marker BEFORE brace removal
    # \lettrine{E}{ste} → ☙DCE❧ste (uses safe Unicode markers, no braces, no %)
    LDC = '\u2619'  # ☙ (rotated floral heart bullet, harmless marker)
    RDC = '\u2767'  # ❧ (rotated floral heart bullet, harmless marker)
    text = re.sub(
        r'\\lettrine\{([^}])\}\{([^}]*)\}',
        LDC + r'DC\1' + RDC + r'\2',
        text
    )
    
    # Substitute LaTeX variables BEFORE brace removal
    text = re.sub(r'\\editionyear\{\}', '2026', text)
    text = re.sub(r'\\authorname\{\}', 'Marcelo Dias de Carvalho', text)
    text = re.sub(r'\\coauthorname\{\}', 'Marcelo Claro', text)
    text = re.sub(r'\\booktitle\{\}', 'Molambundos --- O Diário do Paciente 1.260', text)
    text = re.sub(r'\\subtitle\{\}', 'Uma narrativa em fragmentos', text)
    text = re.sub(r'\\publisher\{\}', 'OpenCode Books', text)
    text = re.sub(r'\\publishercity\{\}', 'Crateús', text)
    text = re.sub(r'\\isbn\{\}', 'ISBN em processo de registro', text)
    
    # Handle \copyright before brace removal
    text = re.sub(r'\\copyright\s*\\\{\}', '©', text)  # \copyright\ {}
    text = re.sub(r'\\copyright\{\}', '©', text)       # \copyright{}
    
    # Remove stray braces and ~ 
    text = re.sub(r'(?<!\w)~(?!\w)', '', text)  # lone ~
    text = re.sub(r'[\{\}]', '', text)  # remove all braces
    
    # Clean up multiple blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    # Clean up comment-only lines
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('%') or stripped.startswith(r'\begin{tikzpicture') or stripped.startswith(r'\end{tikzpicture}'):
            continue
        if re.match(r'\\begin\{scope\}', stripped) or re.match(r'\\end\{scope\}', stripped):
            continue
        if re.match(r'\\pgfmathset', stripped) or re.match(r'\\newlength', stripped):
            continue
        if re.match(r'\\setlength', stripped) or re.match(r'\\tikzset', stripped):
            continue
        if re.match(r'\\tikzmath', stripped) or re.match(r'\\foreach', stripped):
            continue
        if re.match(r'\\shade', stripped) or re.match(r'\\fill', stripped):
            continue
        if re.match(r'\\node', stripped) or re.match(r'\\coordinate', stripped):
            continue
        if re.match(r'\\draw', stripped) or re.match(r'\\path', stripped):
            continue
        if re.match(r'\\def\\', stripped):
            continue
        # Remove lines that are only LaTeX comments after processing
        if re.match(r'^%', stripped):
            continue
        cleaned.append(line)
    text = '\n'.join(cleaned)
    
    # Clean multiple blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    # Remove leading/trailing whitespace per line
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    
    return text.strip()


def convert_file(filepath: str) -> str:
    """Read a .tex file and return clean Markdown."""
    # \input in LaTeX adds .tex automatically
    tex_path = filepath if filepath.endswith('.tex') else filepath + '.tex'
    path = BASE / tex_path
    if not path.exists():
        print(f"  ⚠ Fragment not found: {path}", file=sys.stderr)
        return f"*[Fragment {path.name} não encontrado]*\n\n"
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return strip_latex_markup(content)


def convert_frontmatter_simple(filepath: str) -> str:
    """Convert frontmatter .tex files to plain text."""
    tex_path = filepath if filepath.endswith('.tex') else filepath + '.tex'
    path = BASE / tex_path
    if not path.exists():
        return ""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return strip_latex_markup(content)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    print("📄 Exportando Molambundos para DOCX...")
    
    # Parse order
    order = parse_fragment_order(BASE / "main.tex")
    print(f"   {len(order)} fragmentos encontrados")
    
    # Build markdown
    md_parts = []
    
    # ── Title page ──
    md_parts.append("""---
title: "Molambudos — O Diário do Paciente 1.260"
author: "Marcelo Dias de Carvalho, Marcelo Claro"
subtitle: "Uma narrativa em fragmentos"
---
""")
    
    # ── Copyright page ──
    md_parts.append("# Direitos\n\n*Esta é uma obra de ficção. Qualquer semelhança com pessoas vivas ou mortas é coincidência.*\n\n")
    md_parts.append(convert_frontmatter_simple("frontmatter/copyrightpage.tex"))
    md_parts.append("\n\n---\n\n")
    
    # ── Ficha catalográfica ──
    md_parts.append("## Ficha Catalográfica\n\n")
    md_parts.append(convert_frontmatter_simple("frontmatter/ficha_catalografica.tex"))
    md_parts.append("\n\n---\n\n")
    
    # ── Preface ──
    preface = convert_frontmatter_simple("frontmatter/preface.tex")
    if preface:
        md_parts.append(preface)
        md_parts.append("\n\n---\n\n")
    
    # ── Fragments ──
    current_part = ""
    for part_label, frag_id, filepath in order:
        # Part header
        if part_label and part_label != current_part:
            current_part = part_label
            md_parts.append(f"\n\n# {part_label}\n\n")
        
        # Fragment
        print(f"   → {frag_id} ({filepath})")
        content = convert_file(filepath)
        if content:
            md_parts.append(content)
            md_parts.append("\n\n---\n\n")
    
    # ── Epilogue ──
    md_parts.append("""# Epílogo

*O ciclo recomeça a cada leitor.*

*Ao final, você é o Paciente 1.263.*

*Bem-vindo ao arquivo.*

---

*Se você está lendo isto, você já é o 1.263.*
*O cheiro já começou?*

— Lúcia Menezes, Paciente 1.262

---

*Este livro contém 73 fragmentos e 180 rotas de leitura.*
*Se você leu todos, o ciclo está completo em você.*
*Seu percurso é único: o padrão formado pela sua rota é sua assinatura no arquivo.*

---

*Aquilo agora está aqui.*
*Na página em branco.*
*Esperando o próximo leitor.*

**1260**

*---*

*FIM DA NARRATIVA*

*---*

*Se você chegou até aqui, feche o livro.*
*Conte 62 segundos.*
*Abra na página 62.*
*A primeira linha que você leu mudou.*
*O cheiro está diferente.*
*Você é o Paciente 1.263.*

*Bem-vindo ao arquivo.*
*A entidade agradece sua visita.*

*Agora passe o livro para outra pessoa.*
""")
    
    # Write markdown
    full_md = "\n".join(md_parts)
    # Clean excessive --- separators
    full_md = re.sub(r'\n\n---\n\n---\n\n', '\n\n---\n\n', full_md)
    
    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"\n✅ Markdown escrito: {MD_OUT}")
    
    # ── Convert to DOCX via Pandoc ──
    print("\n🔄 Convertendo para DOCX via Pandoc...")
    cmd = [
        "pandoc",
        str(MD_OUT),
        "-o", str(DOCX_OUT),
        "--from", "markdown+smart",
        "--to", "docx",
        "--toc",
        "--toc-depth", "3",
        "--metadata", "title=Molambundos — O Diário do Paciente 1.260",
        "--metadata", "author=Marcelo Dias de Carvalho, Marcelo Claro",
        "--metadata", "lang=pt-BR",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Pandoc error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    size = os.path.getsize(DOCX_OUT)
    print(f"✅ DOCX gerado: {DOCX_OUT} ({size/1024:.1f} KB)")
    
    # Keep intermediate markdown for inspection/post-processing
    print(f"   (markdown intermediário: {MD_OUT})")


if __name__ == "__main__":
    main()
