#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compila as 1000 laudas pixel em HTML e PDF navegável."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SECOES = RAIZ / "secoes"
PARTES = RAIZ / "partes"

MD = RAIZ / "LIVRO_1000_LAUDAS.md"
HTML = RAIZ / "LIVRO_1000_LAUDAS.html"
PDF = RAIZ / "LIVRO_1000_LAUDAS.pdf"


def _secoes_parte(parte: int) -> list[Path]:
    inicio = (parte - 1) * 100 + 1
    fim = parte * 100
    arquivos = []
    for n in range(inicio, fim + 1):
        achados = sorted(SECOES.glob(f"{n:04d}_*.md"))
        if len(achados) != 1:
            raise FileNotFoundError(f"lauda {n}: encontrados {len(achados)} arquivos")
        arquivos.append(achados[0])
    return arquivos


def montar(limite: int | None = None) -> str:
    partes = [ (RAIZ / "abertura.md").read_text(encoding="utf-8") ]
    partes.append((RAIZ / "MAPA.md").read_text(encoding="utf-8"))

    total = 0
    for parte in range(1, 11):
        partes.append((PARTES / f"parte_{parte:02d}.md").read_text(encoding="utf-8"))
        for arq in _secoes_parte(parte):
            if limite is not None and total >= limite:
                break
            partes.append(arq.read_text(encoding="utf-8"))
            total += 1
        if limite is not None and total >= limite:
            break

    fecho = RAIZ / "fecho.md"
    if fecho.exists() and limite is None:
        partes.append(fecho.read_text(encoding="utf-8"))

    return "\n\n".join(partes) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="compilar apenas N laudas (amostra)")
    args = ap.parse_args()

    texto = montar(args.limit)
    MD.write_text(texto, encoding="utf-8")
    print(f"Markdown: {MD} ({len(texto):,} caracteres)")

    pandoc = shutil.which("pandoc")
    weasyprint = shutil.which("weasyprint")
    if not pandoc or not weasyprint:
        print("pandoc/weasyprint ausente", file=sys.stderr)
        return 2

    subprocess.run([
        pandoc, MD.name,
        "-f", "markdown+fenced_divs+pipe_tables+raw_html",
        "-t", "html5", "-s",
        "--css", "estilo_pixel.css",
        "--metadata", "lang=pt-BR",
        "--metadata", "title=1000 Laudas de Física Quântica",
        "--metadata", "author=OpenCode Ecosystem Core",
        "-o", HTML.name,
    ], cwd=RAIZ, check=True)

    subprocess.run([weasyprint, HTML.name, PDF.name], cwd=RAIZ, check=True)
    print(f"PDF: {PDF} ({PDF.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())