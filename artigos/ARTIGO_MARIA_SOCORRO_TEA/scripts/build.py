#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compila as versões Markdown em DOCX e PDF ABNT via Pandoc + XeLaTeX."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BUILD = BASE / "build"
TEMPLATES = BASE / "templates"


def yaml_quote(texto: str) -> str:
    return "'" + texto.replace("'", "''") + "'"


def preparar_entrada(origem: Path, destino: Path) -> None:
    linhas = origem.read_text(encoding="utf-8").splitlines()
    # Primeiras linhas: título, autor, e-mail (com linhas em branco entre elas).
    nao_vazias = [i for i, l in enumerate(linhas) if l.strip()]
    if len(nao_vazias) < 3:
        raise SystemExit(f"{origem.name}: cabeçalho inesperado")
    i_titulo, i_autor, i_email = nao_vazias[:3]
    titulo = linhas[i_titulo].strip().strip("*")
    autor = linhas[i_autor].strip()
    email = linhas[i_email].strip()
    corpo = "\n".join(linhas[i_email + 1:]).lstrip("\n")
    cabecalho = (
        "---\n"
        f"title: {yaml_quote(titulo)}\n"
        f"author: {yaml_quote(autor + ' (' + email + ')')}\n"
        "lang: pt-BR\n"
        "---\n\n"
    )
    destino.write_text(cabecalho + corpo, encoding="utf-8")


def ajustar_docx(caminho: Path) -> None:
    """Aplica ABNT ao resumo/abstract e às referências no DOCX."""
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt

    doc = Document(str(caminho))
    modo = None
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt == "RESUMO":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
            modo = "resumo"
            continue
        if txt == "ABSTRACT":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
            modo = "resumo"
            continue
        if txt.startswith("Palavras-chave:") or txt.startswith("Keywords:"):
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(12)
            modo = None
            continue
        if txt == "REFERÊNCIAS":
            modo = "refs"
            continue
        if modo == "resumo":
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(0)
        elif modo == "refs":
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(12)
    doc.save(str(caminho))


def rodar(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(BASE), text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"falhou: {cmd[0]}")


def main() -> int:
    BUILD.mkdir(exist_ok=True)
    ref = TEMPLATES / "abnt_reference.docx"
    if not ref.exists():
        raise SystemExit("reference.docx ausente; rode scripts/gerar_reference_docx.py")

    for nome in ("01_ARTIGO_CORRIGIDO_ABNT", "02_ARTIGO_QUALIS_A1"):
        origem = BASE / f"{nome}.md"
        entrada = BUILD / f"{nome}.md"
        preparar_entrada(origem, entrada)

        docx = BASE / f"{nome}.docx"
        rodar([
            "pandoc", str(entrada), "-o", str(docx),
            "--from=markdown+smart",
            "--reference-doc", str(ref),
            "--metadata", "lang=pt-BR",
        ])
        ajustar_docx(docx)

        pdf = BASE / f"{nome}.pdf"
        rodar([
            "pandoc", str(entrada), "-o", str(pdf),
            "--from=markdown+smart",
            "--pdf-engine=xelatex",
            "--pdf-engine-opt=-halt-on-error",
            "--include-in-header", str(TEMPLATES / "abnt_header.tex"),
            "-V", "documentclass=article",
            "-V", "classoption=12pt",
            "-V", "fontsize=12pt",
            "-V", "mainfont=TeX Gyre Termes",
            "-V", "linestretch=1.5",
            "-V", "geometry:a4paper,top=3cm,left=3cm,bottom=2cm,right=2cm",
            "-V", "lang=pt-BR",
            "--metadata", "lang=pt-BR",
        ])

    print("OK: DOCX e PDF gerados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
