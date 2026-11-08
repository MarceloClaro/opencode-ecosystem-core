#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o livro Bohm/black: Markdown -> HTML -> PDF.

As fórmulas são renderizadas em SVG com cor clara, para o fundo preto.
"""
from __future__ import annotations

import hashlib
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

from matplotlib.figure import Figure

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro"
FIGURAS = LIVRO / "figuras_geradas"
MATEMATICA = FIGURAS / "math"
COR_MATEMATICA = "#E8F0FF"

PARTES = [
    "parte_00_abertura.md",
    "parte_01_cap1_3.md",
    "parte_02_cap4_5.md",
    "parte_03_cap6_9.md",
    "parte_04_cap10_12.md",
    "parte_05_cap13_15.md",
    "parte_06_glossario.md",
]

MD_FINAL = LIVRO / "LIVRO_BOHM_BLACK.md"
HTML_FINAL = LIVRO / "LIVRO_BOHM_BLACK.html"
PDF_FINAL = LIVRO / "LIVRO_BOHM_BLACK.pdf"


def concatenar() -> str:
    partes = []
    for nome in PARTES:
        caminho = LIVRO / nome
        if not caminho.exists():
            raise FileNotFoundError(f"Parte ausente: {caminho}")
        partes.append(caminho.read_text(encoding="utf-8").strip())
    return "\n\n".join(partes) + "\n"


def _slug(latex: str, display: bool) -> str:
    base = ("D" if display else "I") + latex
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def _render(latex: str, destino: Path, display: bool) -> None:
    tamanho = 11.6 if display else 10.6
    fig = Figure(figsize=(6.0, 1.2))
    fig.patch.set_alpha(0)
    fig.text(0.01, 0.5, f"${latex}$", fontsize=tamanho, va="center",
             color=COR_MATEMATICA)
    fig.savefig(
        destino,
        format="svg",
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.015,
        transparent=True,
    )


def substituir_matematica(texto: str) -> tuple[str, int, int]:
    MATEMATICA.mkdir(parents=True, exist_ok=True)

    def display(match: re.Match) -> str:
        latex = " ".join(match.group(1).split())
        nome = _slug(latex, True)
        destino = MATEMATICA / f"{nome}.svg"
        if not destino.exists():
            _render(latex, destino, True)
        alt = html.escape(latex, quote=True)
        return f'<div class="math-display"><img src="figuras_geradas/math/{nome}.svg" alt="{alt}"></div>'

    def inline(match: re.Match) -> str:
        latex = " ".join(match.group(1).split())
        nome = _slug(latex, False)
        destino = MATEMATICA / f"{nome}.svg"
        if not destino.exists():
            _render(latex, destino, False)
        alt = html.escape(latex, quote=True)
        return f'<img class="math-inline" src="figuras_geradas/math/{nome}.svg" alt="{alt}">'

    texto, n_disp = re.subn(r"\\\[(.*?)\\\]", display, texto, flags=re.S)
    texto, n_inl = re.subn(r"\\\((.*?)\\\)", inline, texto, flags=re.S)
    return texto, n_disp, n_inl


def validar_figuras(texto: str) -> None:
    referenciadas = set(re.findall(r"figuras_geradas/([A-Za-z0-9_\-]+\.(?:png|svg))", texto))
    existentes = {p.name for p in FIGURAS.glob("*.*") if p.suffix in {".png", ".svg"}}
    faltantes = referenciadas - existentes
    if faltantes:
        raise FileNotFoundError(f"Figuras ausentes: {sorted(faltantes)}")
    nao_usadas = existentes - referenciadas - {"capa_bohm.png"}
    if nao_usadas:
        print(f"[aviso] figuras não referenciadas: {sorted(nao_usadas)}")


def rodar(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=LIVRO, check=True)


def main() -> int:
    texto = concatenar()
    texto, n_disp, n_inl = substituir_matematica(texto)
    validar_figuras(texto)

    MD_FINAL.write_text(texto, encoding="utf-8")
    print(f"Markdown: {MD_FINAL} ({len(texto):,} caracteres)")
    print(f"Fórmulas: {n_disp} em bloco, {n_inl} em linha")

    pandoc = shutil.which("pandoc")
    weasyprint = shutil.which("weasyprint")
    if not pandoc or not weasyprint:
        print("pandoc/weasyprint ausente", file=sys.stderr)
        return 2

    rodar([
        pandoc, MD_FINAL.name,
        "-f", "markdown+fenced_divs+pipe_tables+raw_html",
        "-t", "html5", "-s",
        "--css", "estilo_black.css",
        "--metadata", "lang=pt-BR",
        "--metadata", "title=Bohm na Escola — Edição Black",
        "--metadata", "author=OpenCode Ecosystem Core",
        "-o", HTML_FINAL.name,
    ])
    rodar([weasyprint, HTML_FINAL.name, PDF_FINAL.name])

    if PDF_FINAL.exists():
        print(f"PDF: {PDF_FINAL} ({PDF_FINAL.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())