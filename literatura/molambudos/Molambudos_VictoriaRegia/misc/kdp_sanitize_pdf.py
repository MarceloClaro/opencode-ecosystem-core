#!/usr/bin/env python3
"""Sanitização de PDFs para Amazon/KDP.

Remove anotações clicáveis e marcações não imprimíveis do PDF, com opção de
extrair intervalo de páginas. Usado para gerar miolos físicos sem hyperlinks.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject


CATALOG_KEYS_TO_REMOVE = (
    "/OpenAction",
    "/Names",
    "/Outlines",
    "/PageMode",
    "/AA",
)


def _strip_page_annotations(page) -> None:
    obj = page.get_object()
    obj.pop(NameObject("/Annots"), None)
    obj.pop(NameObject("/AA"), None)


def _strip_catalog_markup(writer: PdfWriter) -> None:
    root = writer._root_object  # pypdf public API does not expose a safer mutator here.
    for key in CATALOG_KEYS_TO_REMOVE:
        root.pop(NameObject(key), None)


def sanitize_pdf(input_pdf: Path, output_pdf: Path, start_page: int | None, end_page: int | None) -> None:
    reader = PdfReader(str(input_pdf))
    if reader.is_encrypted:
        raise SystemExit(f"PDF criptografado não suportado: {input_pdf}")

    total = len(reader.pages)
    start = 1 if start_page is None else start_page
    end = total if end_page is None else end_page
    if start < 1 or end > total or start > end:
        raise SystemExit(f"Intervalo inválido {start}-{end}; PDF possui {total} página(s)")

    writer = PdfWriter()
    for idx in range(start - 1, end):
        page = reader.pages[idx]
        _strip_page_annotations(page)
        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata({k: str(v) for k, v in reader.metadata.items() if v is not None})
    _strip_catalog_markup(writer)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as fh:
        writer.write(fh)


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove links/anotações e opcionalmente extrai páginas de PDF.")
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--start-page", type=int, default=None, help="Página inicial 1-indexada")
    parser.add_argument("--end-page", type=int, default=None, help="Página final 1-indexada, inclusiva")
    args = parser.parse_args()
    sanitize_pdf(args.input_pdf, args.output_pdf, args.start_page, args.end_page)


if __name__ == "__main__":
    main()
