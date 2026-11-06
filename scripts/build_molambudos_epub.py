#!/usr/bin/env python3
"""Gera o EPUB3 de leitura do Molambudos a partir dos fragmentos canônicos.

Fonte: `main.tex` (ordem canônica) + `fragmentos/` + `frontmatter/`.
O EPUB é uma edição de leitura; não substitui o PDF KDP 160×230 mm.

Uso:
    python3 scripts/build_molambudos_epub.py \
      --project literatura/molambudos/Molambudos_VictoriaRegia \
      --output literatura/molambudos/release/2026-11-05/epub/Molambudos_PT.epub \
      --report reports/r1074/epub_manifest.json
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from marceloclaro.bookstudio.epub import patch_accessibility_summary

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = ROOT / "literatura/molambudos/Molambudos_VictoriaRegia"
DEFAULT_OUTPUT = ROOT / "literatura/molambudos/release/2026-11-05/epub/Molambudos_PT.epub"
DEFAULT_REPORT = ROOT / "reports/r1074/epub_manifest.json"

PART_TITLES = [
    "Sertão (1914–1917)",
    "Colônia (1917–1979)",
    "Diário de Oliveira e Laudos (1979)",
    "Investigação Lúcia (2026)",
    "Contaminação (Você)",
]

PART_NOTES = {
    3: (
        "Nota do Arquivista: a partir deste ponto, a voz principal deixa de ser "
        "a de Joaquim e passa a ser a de quem o estudou. Os documentos a seguir "
        "foram escritos por médicos, peritos e arquivistas. A linguagem muda. "
        "O olhar muda. Mas o diário é o mesmo."
    ),
    4: (
        "Nota do Arquivista: os fragmentos desta parte foram organizados por "
        "Dra. Lúcia Mendes durante sua pesquisa em 2026. As anotações dela "
        "estão em itálico nas margens dos documentos originais. O documento "
        "mais antigo do arquivo — de 1853 — foi encontrado por ela e anexado "
        "ao processo."
    ),
}

TABLE_SPECS = {
    "moltabletwo": "ll",
    "moltablethree": "lll",
    "moltablefour": "llll",
    "moltablefive": "lllll",
    "moltablesix": "llllll",
}

ACCESSIBILITY_SUMMARY = (
    "Edição em português com estrutura navegável, texto alternativo nas imagens, "
    "ordem de leitura definida e sumário. A obra é uma ficção documental; as "
    "imagens são reconstituições ficcionais, não documentos históricos."
)

CSS = """\
body { font-family: serif; line-height: 1.55; margin: 0 1.2em; }
h1, h2, h3, h4 { font-family: sans-serif; line-height: 1.2; }
h1 { page-break-before: always; margin-top: 2em; }
h2 { margin-top: 1.6em; }
p { margin: 0 0 0.65em 0; text-align: justify; }
blockquote { margin: 1em 1.6em; font-style: italic; }
hr { border: 0; border-top: 1px solid #999; margin: 1.4em 0; }
img { max-width: 100%; height: auto; }
.center { text-align: center; }
.smallcaps { font-variant: small-caps; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.92em; }
th, td { border: 1px solid #999; padding: 0.25em 0.35em; vertical-align: top; }
.code-mem { color: #8A3B1F; font-weight: bold; }
.code-doc { color: #1F5C57; font-weight: bold; }
.code-luc { color: #552A7A; font-weight: bold; }
.code-cont { color: #9B1B1B; font-weight: bold; }
figure { margin: 1.2em 0; text-align: center; }
figcaption { font-size: 0.9em; font-style: italic; color: #2B2117; }
"""


def run(cmd: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"comando falhou: {' '.join(cmd)}\n{proc.stderr[:4000]}")
    return proc.stdout


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_braced(text: str, pos: int) -> tuple[str, int]:
    if pos >= len(text) or text[pos] != "{":
        raise ValueError(f"esperava '{{' em {pos}: {text[pos:pos+40]!r}")
    depth = 0
    for i in range(pos, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[pos + 1:i], i + 1
    raise ValueError("chaves não balanceadas")


def parse_fragtitle(tex_text: str) -> list[str] | None:
    j = tex_text.find("\\fragtitle{")
    if j < 0:
        return None
    pos = j + len("\\fragtitle")
    args: list[str] = []
    try:
        for _ in range(5):
            pos = tex_text.index("{", pos)
            arg, pos = parse_braced(tex_text, pos)
            args.append(arg)
    except ValueError:
        return None
    return args


def replace_fragtitle(text: str) -> str:
    out: list[str] = []
    i = 0
    needle = "\\fragtitle{"
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        pos = j + len("\\fragtitle")
        args: list[str] = []
        try:
            for _ in range(5):
                pos = text.index("{", pos)
                arg, pos = parse_braced(text, pos)
                args.append(arg)
        except ValueError:
            out.append(text[j:pos])
            i = pos
            continue
        out.append(f"\\section*{{\\textbf{{{args[2]}-{args[3]}}} --- {args[4]}}}")
        i = pos
    return "".join(out)


def extract_args(line: str, command: str, count: int) -> list[str]:
    pos = line.index(command) + len(command)
    args = []
    for _ in range(count):
        pos = line.index("{", pos)
        arg, pos = parse_braced(line, pos)
        args.append(arg)
    return args


def clean_inline(text: str) -> str:
    text = re.sub(r"\\text(?:it|bf|sc|tt|rm|sf)\{([^{}]*)\}", r"\1", text)
    text = text.replace("---", "—").replace("--", "–")
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = text.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", text).strip()


def parse_main(project: Path) -> tuple[list[dict], Path, Path]:
    main = (project / "main.tex").read_text(encoding="utf-8")
    lines = main.splitlines()
    parts: list[dict] = []
    current: dict | None = None
    for line in lines:
        if re.match(r"^\s*\\partopener\{", line):
            args = extract_args(line, "\\partopener", 3)
            title = clean_inline(args[1])
            if current is None or current["title"] != title:
                current = {"title": title, "fragments": []}
                parts.append(current)
        m = re.search(r"\\fragdef\{([^}]*)\}\\input\{([^}]*)\}", line)
        if m and current is not None:
            current["fragments"].append((m.group(1), m.group(2)))
    if len(parts) != 5:
        raise SystemExit(f"esperava 5 partes em main.tex, encontrei {len(parts)}")
    total = sum(len(p["fragments"]) for p in parts)
    if total != 84:
        raise SystemExit(f"esperava 84 fragmentos, encontrei {total}")
    return parts, project / "main.tex", project / "fragmentos"


def replace_braced(text: str, command: str, func) -> str:
    out = []
    i = 0
    needle = command + "{"
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        arg, end = parse_braced(text, j + len(command))
        out.append(func(arg))
        i = end
    return "".join(out)


def preprocess_latex(text: str, project: Path) -> str:
    # Comentários de linha inteira
    text = re.sub(r"(?m)^\s*%.*$\n?", "", text)
    # Cabeçalho visual R1076 -> heading LaTeX compreensível pelo Pandoc
    text = replace_fragtitle(text)
    # Ambientes de tabela -> tabular
    def table_begin(m: re.Match) -> str:
        env = m.group(1)
        return "\\begin{tabular}{%s}" % TABLE_SPECS.get(env, "ll")
    text = re.sub(r"\\begin\{(moltable\w+)\}(\[[^\]]*\])?", table_begin, text)
    text = re.sub(r"\\end\{(moltable\w+)\}", r"\\end{tabular}", text)
    text = re.sub(r"\\begin\{itemize\}\[[^\]]*\]", r"\\begin{itemize}", text)
    text = text.replace(r"\item[$\square$]", r"\item [ ]")
    # Rotas e notas
    text = re.sub(r"\\rota\{([^}]*)\}", r"**\1**", text)
    text = text.replace(r"\rotasep", "·")
    text = replace_braced(text, r"\NE", lambda a: r"\footnote{[N.E.] " + a + "}")
    def marg(a: str) -> str:
        a = a.replace("\\\\", "; ").replace(r"\páginas", "páginas")
        a = a.replace(r"\folhas", "folhas").replace(r"\viradas", "viradas")
        a = a.replace(r"\Quem", "Quem").replace(r"\virando", "virando")
        return r"\footnote{" + a + "}"
    text = replace_braced(text, r"\margnota", marg)
    text = text.replace(r"\{}", "").replace(r"\{", "{").replace(r"\}", "}")
    text = text.replace(r"\%", "%").replace(r"\&", "&").replace(r"\_", "_")
    text = text.replace(r"\#", "#").replace(r"\$", "$")
    # Quebras de linha LaTeX com espaçamento opcional: \\[1.2em]
    text = re.sub(r"\\\\\[[^\]]*\]", " ", text)
    text = re.sub(r"\\setlength\{[^{}]*\}\{[^{}]*\}", "", text)
    text = text.replace(r"\begingroup", "").replace(r"\endgroup", "")
    text = re.sub(r"\\color\{[^{}]*\}", "", text)
    text = re.sub(r"\\itemsep[0-9.]+em", "", text)
    # Cores: mantém o conteúdo
    text = replace_braced(text, r"\textcolor", lambda a: a)
    # Comandos de layout removidos
    for cmd in (r"\vspace", r"\hspace*", r"\label", r"\index", r"\thispagestyle",
                r"\pagestyle", r"\cleardoublepage", r"\noindent", r"\centering",
                r"\small", r"\footnotesize", r"\normalsize", r"\large", r"\Large",
                r"\LARGE", r"\Huge", r"\huge", r"\scshape", r"\itshape",
                r"\bfseries", r"\raggedright", r"\par", r"\null", r"\vfill",
                r"\hfill", r"\selectfont", r"\relax"):
        text = replace_braced(text, cmd, lambda a: "")
    text = re.sub(r"\\(vspace|hspace\*?|label|index|thispagestyle|pagestyle|cleardoublepage|noindent|centering|small|footnotesize|normalsize|large|Large|LARGE|Huge|huge|scshape|itshape|bfseries|raggedright|par|null|vfill|hfill|selectfont|relax)\*?", "", text)
    # Regras horizontais e preenchimentos
    text = re.sub(r"\\rule\{[^{}]*\}\{[^{}]*\}", "", text)
    text = re.sub(r"\\markboth\{[^{}]*\}\{[^{}]*\}", "", text)
    text = text.replace(r"\makebox[2in]{\hrulefill}", "________")
    text = text.replace(r"\hrulefill", "________")
    text = text.replace(r"\dotfill", "______")
    text = text.replace(r"\qquad", "    ").replace(r"\quad", " ")
    # Imagens: resolve figures/
    def img(m: re.Match) -> str:
        opt = m.group(1) or ""
        path = m.group(2)
        if not path.startswith(("figures/", "frontmatter/")) and (project / "figures" / path).is_file():
            path = "figures/" + path
        return f"\\includegraphics{opt}{{{path}}}"
    text = re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}", img, text)
    # Símbolos e pontuação
    text = text.replace(r"\ldots", "...").replace(r"\dots", "...")
    text = text.replace(r"\textemdash", "—").replace(r"\textendash", "–")
    text = text.replace(r"\textbullet", "•").replace(r"\checkmark", "✓")
    text = text.replace(r"\square", "☐").replace(r"\blacktriangleright", "▶")
    text = text.replace(r"\hookrightarrow", "↪").replace(r"\rightarrow", "→")
    text = text.replace(r"\leftarrow", "←").replace(r"\to", "→")
    text = text.replace(r"\heartsuit", "♥").replace(r"\bigstar", "★")
    text = text.replace(r"\circ", "°").replace(r"\texttimes", "×")
    text = text.replace(r"\cdot", "·").replace(r"\times", "×")
    text = text.replace(r"\textbackslash{}", "")
    text = text.replace(r"\slash", "/").replace(r"\textbackslash", "\\")
    text = text.replace("$\\rightarrow$", "→").replace("$\\to$", "→")
    text = text.replace("$\\square$", "☐").replace("$\\checkmark$", "✓")
    text = text.replace("$\\times$", "×")
    text = text.replace(r"\...", "...")
    # Traços e escapes
    text = re.sub(r"\\\[", "[", text)
    text = re.sub(r"\\\]", "]", text)
    text = text.replace(r"\,", " ").replace(r"\;", " ").replace(r"\:", " ")
    text = text.replace(r"\!", "")
    text = text.replace("---", "—").replace("--", "–")
    text = text.replace(r"\{}", "")
    return text


def pandoc_tex_to_md(tex_text: str, workdir: Path, project: Path, name: str) -> str:
    if "\\documentclass" not in tex_text:
        tex_text = "\\documentclass{book}\n\\begin{document}\n" + tex_text + "\n\\end{document}\n"
    elif "\\end{document}" not in tex_text:
        tex_text += "\n\\end{document}\n"
    src = workdir / f"{name}.tex"
    src.write_text(tex_text, encoding="utf-8")
    out = run([
        "pandoc", str(src), "-f", "latex", "-t", "markdown",
        "--wrap=none", "--resource-path", str(project),
    ], cwd=project)
    return out


def fragment_title(tex_text: str, fid: str) -> str:
    args = parse_fragtitle(tex_text)
    if args:
        return clean_inline(args[4])
    m = re.search(r"\\section\*\{\\textbf\{([^}]*)\}\s*---\s*(.+?)\}", tex_text, re.S)
    if not m:
        return fid
    return clean_inline(m.group(2))


def drop_first_heading(md: str) -> str:
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return "\n".join(lines[i + 1:]).lstrip()
        if line.strip():
            return md
    return md


def normalize_md(md: str) -> str:
    md = md.replace("\r\n", "\n")

    def route_repl(m: re.Match) -> str:
        rest = m.group(1).replace("\\*\\*", "**").replace("\\*", "*")
        return "> **↪ Rotas:** " + rest

    md = re.sub(r"(?m)^\*{0,3}↪ Rotas:\*{0,3}\s*(.*)$", route_repl, md)
    md = re.sub(r"(?m)^-{3,}\s*\n(> \*\*↪ Rotas:)", r"\1", md)
    md = re.sub(r"\n+(> \*\*↪ Rotas:)", r"\n\n\1", md)
    md = re.sub(r"(> \*\*↪ Rotas:[^\n]*)\n(?=#)", r"\1\n\n", md)
    md = re.sub(r"(?m)^-{3,}\s*$", "---", md)
    md = re.sub(r"(?m)^\\\s*$", "", md)
    md = md.replace(r"\[N.E.\]", "[N.E.]").replace(r"\[ilegível\]", "[ilegível]")
    md = md.replace(r"\[lacuna\]", "[lacuna]").replace(r"\[sic\]", "[sic]")
    md = md.replace(r"\[/ 10\]", "[/ 10]")
    md = re.sub(r"\[\s*~?\s*\]", "[ ]", md)
    md = re.sub(r"\(p\.\s*\)", "(ver Nota Histórica)", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def build_markdown(project: Path, workdir: Path) -> tuple[str, dict]:
    parts, _, _ = parse_main(project)
    chunks: list[str] = []
    chunks.append("""---
title: "Molambudos — O Diário do Paciente 1.260"
subtitle: "Uma narrativa em fragmentos"
author:
  - "Marcelo Dias de Carvalho Filho"
  - "Marcelo Claro"
lang: pt-BR
publisher: "OpenCode Books"
date: "2026"
identifier: "ISBN 9798189170492"
rights: "© 2026 Marcelo Dias de Carvalho Filho e Marcelo Claro. Todos os direitos reservados."
description: "Romance em fragmentos. Edição digital de leitura derivada da edição canônica KDP PT-BR."
---""")

    def add_frontmatter(name: str, title: str | None, tex_file: Path | None = None, text: str | None = None, preamble: str = ""):
        if text is None:
            raw = tex_file.read_text(encoding="utf-8")
            text = preamble + preprocess_latex(raw, project)
        md = normalize_md(pandoc_tex_to_md(text, workdir, project, name))
        if title:
            chunks.append(f"# {title}")
        chunks.append(md)

    add_frontmatter("aviso", "Aviso ao Leitor", project / "frontmatter/aviso_ao_leitor.tex")
    add_frontmatter("epigrafe", "Epígrafe", project / "frontmatter/epigrafe.tex")

    chunks.append("# Cuidado")
    chunks.append(
        "> **CUIDADO**\n>\n"
        "> Este livro contém um ciclo de contaminação narrativa.\n>\n"
        "> Ao ler, você se torna o **Paciente 1.263**.\n>\n"
        "> Ao final, não haverá como devolver o livro à estante como se você não o tivesse aberto.\n>\n"
        "> Se um zumbido surgir durante a leitura, não pare. Já é tarde demais para parar."
    )

    preamble = (
        "\\documentclass{book}\n"
        "\\newcommand{\\authorname}{Marcelo Dias de Carvalho Filho}\n"
        "\\newcommand{\\coauthorname}{Marcelo Claro}\n"
        "\\newcommand{\\booktitle}{Molambudos --- O Diário do Paciente 1.260}\n"
        "\\newcommand{\\publisher}{OpenCode Books}\n"
        "\\newcommand{\\publishercity}{Crateús}\n"
        "\\newcommand{\\editionyear}{2026}\n"
        "\\newcommand{\\isbn}{9798189170492}\n"
        "\\begin{document}\n"
    )
    add_frontmatter("copyright", "Copyright", project / "frontmatter/copyrightpage.tex", preamble=preamble)

    chunks.append("# Ficha Catalográfica")
    chunks.append(
        "**Dados Internacionais de Catalogação na Publicação (CIP)**\n\n"
        "Carvalho Filho, Marcelo Dias de.\n"
        "*Molambudos — O Diário do Paciente 1.260* / Marcelo Dias de Carvalho Filho, Marcelo Claro. — 1. ed. — Crateús: OpenCode Books, 2026.\n\n"
        "ISBN 9798189170492.\n\n"
        "1. Ficção brasileira. 2. Horror psicológico. 3. Narrativa fragmentária. "
        "4. Literatura contemporânea. 5. Memória e trauma. I. Carvalho Filho, Marcelo Dias de. "
        "II. Claro, Marcelo. III. Título.\n\n"
        "CDD: 869.93 — CDU: 821.134.3(81)-3\n\n"
        "Índice para catálogo sistemático: 1. Ficção brasileira: 869.93"
    )

    add_frontmatter("nota_arquivista", None, project / "frontmatter/nota_arquivista.tex")
    add_frontmatter("como_ler", None, project / "frontmatter/como_ler.tex")

    chunks.append("# Legenda dos Códigos")
    chunks.append(
        "Cada fragmento pertence a uma família. A cor e a capitular de abertura "
        "indicam essa família antes de o leitor começar a ler.\n\n"
        '**<span class="code-mem">MEM</span> Memória.** A voz de Joaquim: sertão, fome, colônia, o diário.\n\n'
        '**<span class="code-doc">DOC</span> Documento.** Laudos, prontuários, cartas, registros e provas.\n\n'
        '**<span class="code-luc">LUC</span> Lucidez.** A investigação de Lúcia Mendes em 2026.\n\n'
        '**<span class="code-cont">CONT</span> Contaminação.** A segunda pessoa, o leitor, o ciclo.'
    )

    for idx, part in enumerate(parts, start=1):
        chunks.append(f"# Parte {idx} — {PART_TITLES[idx-1]}")
        if idx in PART_NOTES:
            chunks.append(f"> *{PART_NOTES[idx]}*")
        for fid, rel in part["fragments"]:
            tex_path = project / rel
            if not tex_path.is_file():
                tex_path = tex_path.with_suffix(".tex")
            raw = tex_path.read_text(encoding="utf-8")
            title = fragment_title(raw, fid)
            pre = preprocess_latex(raw, project)
            md = normalize_md(pandoc_tex_to_md(pre, workdir, project, f"frag_{fid.replace('-', '_')}"))
            md = drop_first_heading(md)
            md = "\n".join(("#" + line) if line.startswith("#") else line for line in md.splitlines())
            code = fid.split("-", 1)[0].lower()
            chunks.append(f'## <span class="code-{code}">{fid}</span> — {title}')
            chunks.append(md)

    # Epílogo: bloco entre \fragdef{EPI-01} e o apêndice editorial
    main_lines = (project / "main.tex").read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(main_lines) if line.startswith("\\fragdef{EPI-01}"))
    end = next(i for i, line in enumerate(main_lines) if line.startswith("\\input{frontmatter/nota_editorial}"))
    epi = "\n".join(main_lines[start:end])
    epi = "\\documentclass{book}\n\\begin{document}\n" + preprocess_latex(epi, project) + "\n\\end{document}\n"
    epi_md = normalize_md(pandoc_tex_to_md(epi, workdir, project, "epilogo"))
    epi_md = drop_first_heading(epi_md)
    chunks.append("# Epílogo")
    chunks.append(epi_md)

    add_frontmatter("nota_editorial", None, project / "frontmatter/nota_editorial.tex")

    chunks.append("# Caderno de Provas Iconográficas")
    chunks.append(
        "*As imagens deste caderno pertencem à ficção documental do romance. "
        "Não são reproduções de documentos históricos, nem provas de arquivo. "
        "Foram compostas para este volume; o horror real de Barbacena e da seca "
        "não é reconstituído aqui.*"
    )
    for placa, caption in [
        ("placa_00", "Paciente 1.260. Retrato de arquivo. Reconstituição ficcional."),
        ("placa_01", "Registro de admissão. Colônia de Barbacena, 1917. Reconstituição ficcional."),
        ("placa_02", "Dr. Heitor Oliveira. Arquivo pessoal, 1979. Reconstituição ficcional."),
        ("placa_03", "O homem do pano preto. Imagem não catalogada. Reconstituição ficcional."),
        ("placa_04", "Dra. Lúcia Mendes. Rodoviária de Barbacena, 2026. Reconstituição ficcional."),
        ("placa_05", "Fotografia 5. Arquivo pessoal de Lúcia Mendes, 2026. Reconstituição ficcional."),
    ]:
        chunks.append(f"![](figures/immersao/{placa}.png)\n\n*{caption}*")

    add_frontmatter("glossario", None, project / "frontmatter/glossario_historico.tex")
    add_frontmatter("nota_historica", None, project / "frontmatter/nota_historica.tex")
    add_frontmatter("ficha_beta", None, project / "frontmatter/ficha_beta_diegetica.tex")

    chunks.append("# Sobre esta edição digital")
    chunks.append(
        "Esta edição digital de leitura foi derivada dos **84 fragmentos canônicos** "
        "e do epílogo, na ordem de `main.tex` da edição KDP PT-BR 160×230 mm. "
        "O texto é o mesmo da edição impressa; o layout, as folhas e os folios não "
        "são reproduzidos. As imagens disponíveis no projeto foram incluídas quando "
        "referenciadas pelo texto.\n\n"
        "Gerada com Pandoc 3.7 em 2026-11-05. Não passou por EPUBCheck, revisão "
        "humana de galerada ou validação editorial externa. O PDF canônico permanece "
        "a referência de impressão."
    )

    md = "\n\n".join(chunk for chunk in chunks if chunk is not None)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    stats = {
        "parts": len(parts),
        "fragments": sum(len(p["fragments"]) for p in parts),
        "part_titles": [p["title"] for p in parts],
    }
    return md, stats


def validate_epub(epub: Path, canonical_words: int) -> dict:
    result: dict = {
        "zip_ok": False,
        "opf_ok": False,
        "nav_ok": False,
        "spine_items": 0,
        "manifest_items": 0,
        "xhtml_items": 0,
        "images": 0,
        "fragment_headings": 0,
        "fragment_links": 0,
        "sections": 0,
        "low_sections": [],
        "nav_links": 0,
        "nav_broken": [],
        "word_count": 0,
        "canonical_word_count": canonical_words,
        "word_ratio": None,
        "raw_latex": [],
        "missing_images": [],
        "unresolved_refs": [],
        "metadata": {},
        "epubcheck": "não instalado; validação estrutural local",
    }
    if not epub.is_file():
        result["error"] = "EPUB ausente"
        return result
    try:
        with zipfile.ZipFile(epub) as z:
            bad = z.testzip()
            result["zip_ok"] = bad is None
            names = set(z.namelist())
            container = ET.fromstring(z.read("META-INF/container.xml"))
            rootfile = container.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
            if rootfile is None:
                result["error"] = "container.xml sem rootfile"
                return result
            opf_path = rootfile.get("full-path")
            opf = ET.fromstring(z.read(opf_path))
            ns = {
                "opf": "http://www.idpf.org/2007/opf",
                "dc": "http://purl.org/dc/elements/1.1/",
            }
            result["opf_ok"] = True
            result["accessibility_summary"] = "schema:accessibilitySummary" in z.read(opf_path).decode("utf-8", "replace")
            result["metadata"] = {
                "title": (opf.findtext(".//dc:title", namespaces=ns) or "").strip(),
                "creator": [e.text.strip() for e in opf.findall(".//dc:creator", ns) if e.text],
                "language": (opf.findtext(".//dc:language", namespaces=ns) or "").strip(),
                "identifier": (opf.findtext(".//dc:identifier", namespaces=ns) or "").strip(),
                "publisher": (opf.findtext(".//dc:publisher", namespaces=ns) or "").strip(),
            }
            manifest = opf.findall(".//opf:item", ns)
            spine = opf.findall(".//opf:itemref", ns)
            result["manifest_items"] = len(manifest)
            result["spine_items"] = len(spine)
            by_id = {item.get("id"): item for item in manifest}
            xhtml_paths = [item.get("href") for item in manifest if item.get("media-type") == "application/xhtml+xml"]
            result["xhtml_items"] = len(xhtml_paths)
            nav_item = next((item for item in manifest if "nav" in (item.get("properties") or "")), None)
            fragment_ids: set[str] = set()
            words = 0
            for href in xhtml_paths:
                path = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), href))
                if path not in names:
                    continue
                data = z.read(path).decode("utf-8", errors="replace")
                try:
                    root = ET.fromstring(data)
                except ET.ParseError:
                    continue
                text = "".join(root.itertext())
                words += len(text.split())
                for m in re.finditer(r"\b(MEM|DOC|LUC|CONT)-[0-9A-Za-z-]+", text):
                    fragment_ids.add(m.group(0))
                for sec in root.iter("{http://www.w3.org/1999/xhtml}section"):
                    h = sec.find("{http://www.w3.org/1999/xhtml}h2")
                    if h is None:
                        continue
                    result["sections"] += 1
                    sec_text = "".join(sec.itertext())
                    wc = len(sec_text.split())
                    if wc < 80:
                        result["low_sections"].append({"path": path, "id": h.get("id"), "words": wc})
                for m in re.finditer(r"\\[a-zA-Z]+", text):
                    result["raw_latex"].append({"path": path, "token": m.group(0)})
                for token in ("\\pageref", "\\ref", "p.~", "(p. )"):
                    if token in text:
                        result["unresolved_refs"].append({"path": path, "token": token})
                for img in root.iter():
                    src = None
                    if img.tag.endswith("}img"):
                        src = img.get("src")
                    elif img.tag.endswith("}image"):
                        src = img.get("{http://www.w3.org/1999/xlink}href")
                    if not src:
                        continue
                    result["images"] += 1
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(path), src))
                    if target not in names:
                        result["missing_images"].append({"path": path, "src": src, "resolved": target})
            result["fragment_headings"] = len(fragment_ids)
            result["word_count"] = words
            if canonical_words:
                result["word_ratio"] = round(words / canonical_words, 3)
            if nav_item is not None:
                nav_path = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), nav_item.get("href")))
                if nav_path in names:
                    nav = ET.fromstring(z.read(nav_path))
                    base = posixpath.dirname(nav_path)
                    for a in nav.findall(".//{http://www.w3.org/1999/xhtml}a"):
                        href = a.get("href")
                        if not href:
                            continue
                        result["nav_links"] += 1
                        label = "".join(a.itertext()).strip()
                        if re.match(r"^(MEM|DOC|LUC|CONT)-", label):
                            result["fragment_links"] += 1
                        if href.startswith(("http://", "https://")):
                            continue
                        path_part, _, frag = href.partition("#")
                        target = posixpath.normpath(posixpath.join(base, path_part)) if path_part else nav_path
                        if target not in names:
                            result["nav_broken"].append({"href": href, "reason": "file"})
                            continue
                        if frag:
                            data = z.read(target).decode("utf-8", errors="replace")
                            if f'id="{frag}"' not in data:
                                result["nav_broken"].append({"href": href, "reason": "id"})
                    result["nav_ok"] = result["nav_links"] > 0 and not result["nav_broken"]
    except (zipfile.BadZipFile, ET.ParseError) as exc:
        result["error"] = str(exc)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--workdir", type=Path, default=Path("/tmp/opencode/molambudos_epub"))
    args = ap.parse_args()

    project = args.project.resolve()
    output = args.output.resolve()
    report_path = args.report.resolve()
    workdir = args.workdir.resolve()
    if not (project / "main.tex").is_file():
        raise SystemExit(f"projeto inválido: {project}")
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    md, stats = build_markdown(project, workdir)
    md_path = workdir / "Molambudos_PT.md"
    md_path.write_text(md, encoding="utf-8")
    css_path = workdir / "epub.css"
    css_path.write_text(CSS, encoding="utf-8")

    cover = project / "frontmatter/capa.png"
    run([
        "pandoc", str(md_path), "-f", "markdown", "-t", "epub3",
        "--toc", "--toc-depth=2", "--split-level=1",
        "--epub-cover-image", str(cover),
        "--css", str(css_path),
        "--resource-path", str(project),
        "--output", str(output),
    ], cwd=project)
    patch_accessibility_summary(output, ACCESSIBILITY_SUMMARY)

    pdf = project / "main_kdp_pt_160x230mm.pdf"
    canonical_words = 0
    if pdf.is_file():
        txt = run(["pdftotext", str(pdf), "-"])
        canonical_words = len(txt.split())

    validation = validate_epub(output, canonical_words)
    status = "completed"
    problems = []
    if not validation.get("zip_ok"):
        problems.append("zip inválido")
    if not validation.get("opf_ok"):
        problems.append("OPF inválido")
    if not validation.get("nav_ok"):
        problems.append("nav ausente")
    if not validation.get("accessibility_summary"):
        problems.append("schema:accessibilitySummary ausente")
    if validation.get("raw_latex"):
        problems.append(f"{len(validation['raw_latex'])} comandos LaTeX crus")
    if validation.get("missing_images"):
        problems.append(f"{len(validation['missing_images'])} imagens ausentes")
    if validation.get("unresolved_refs"):
        problems.append(f"{len(validation['unresolved_refs'])} referências não resolvidas")
    if validation.get("fragment_headings") != 84:
        problems.append(f"fragmentos no EPUB: {validation.get('fragment_headings')} (esperado 84)")
    if validation.get("fragment_links") != 84:
        problems.append(f"links de fragmento no TOC: {validation.get('fragment_links')} (esperado 84)")
    if validation.get("sections") != 84:
        problems.append(f"seções de fragmento: {validation.get('sections')} (esperado 84)")
    if validation.get("low_sections"):
        problems.append(f"{len(validation['low_sections'])} seções com menos de 80 palavras")
    if validation.get("nav_broken"):
        problems.append(f"{len(validation['nav_broken'])} links quebrados no TOC")
    if canonical_words and not (0.80 <= (validation.get("word_ratio") or 0) <= 1.20):
        problems.append(f"razão de palavras fora da faixa: {validation.get('word_ratio')}")
    if problems:
        status = "failed"

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source_project": str(project.relative_to(ROOT)) if project.is_relative_to(ROOT) else str(project),
        "source_order": "main.tex",
        "parts": stats["parts"],
        "fragments": stats["fragments"],
        "part_titles": stats["part_titles"],
        "epub": {
            "path": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
            "bytes": output.stat().st_size if output.is_file() else None,
            "sha256": sha256_file(output) if output.is_file() else None,
        },
        "validation": validation,
        "problems": problems,
        "limits": [
            "Edição de leitura derivada da canônica; não substitui o PDF KDP.",
            "Validação estrutural local; EPUBCheck/Ace são executados como ferramentas externas.",
            "Sem revisão humana de galerada ou validação editorial externa.",
        ],
    }
    report_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "epub": manifest["epub"], "problems": problems,
                      "validation": {k: validation.get(k) for k in ("fragment_headings", "word_count", "word_ratio", "images")}},
                     ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
