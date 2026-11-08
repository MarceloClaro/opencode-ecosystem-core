# -*- coding: utf-8 -*-
"""Contratos da edição de curso (R1103) e do audiolivro piloto.

A edição de curso é uma seleção de 60 conceitos da obra de referência. O
audiolivro é uma seleção de leitura, não a narração integral das 600 laudas.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

from pypdf import PdfReader

RAIZ = Path(__file__).resolve().parents[2]
LIVRO = RAIZ / "educacao_quantica_bohm" / "livro_pixel"
CURSO_PDF = LIVRO / "EDICAO_CURSO_600.pdf"
CURSO_EPUB = LIVRO / "EDICAO_CURSO_600.epub"
CURSO_HTML = LIVRO / "EDICAO_CURSO_600.html"
AUDIO = LIVRO / "AUDIOLIVRO_CURSO"
MANIFEST = AUDIO / "manifest.json"


def test_curso_pdf_dentro_da_faixa_de_paginas() -> None:
    assert CURSO_PDF.is_file(), "PDF da edição de curso ausente"
    paginas = len(PdfReader(CURSO_PDF).pages)
    assert 600 <= paginas <= 800, f"páginas fora da faixa: {paginas}"
    assert CURSO_PDF.stat().st_size > 1_000_000


def test_curso_html_tem_60_conceitos_e_exclui_gabarito() -> None:
    html = CURSO_HTML.read_text(encoding="utf-8")
    assert html.count('class="lauda ') == 600
    assert html.count('class="modulo"') == 12
    assert html.count("modulo-fig") == 12
    assert 'href="#g-' not in html
    assert 'href="#f-' not in html
    assert 'id="gabarito"' not in html
    assert "NOTAS AO PROFESSOR" in html or "Notas ao professor" in html
    assert "Aprofundamento quântico" in html


def test_curso_epub_integro() -> None:
    assert CURSO_EPUB.is_file(), "EPUB da edição de curso ausente"
    with zipfile.ZipFile(CURSO_EPUB) as z:
        assert z.testzip() is None
        xhtml = [n for n in z.namelist() if n.endswith(".xhtml")]
    assert len(xhtml) >= 30


def test_build_curso_declara_12_modulos_e_60_selecoes() -> None:
    texto = (LIVRO / "build_curso.py").read_text(encoding="utf-8")
    assert "MÓDULOS" in texto or "MODULOS" in texto
    assert "12 MÓDULOS · 600 LAUDAS" in texto
    # 12 módulos, cada um com uma lista de 5 pares (nível, conceito).
    selecoes = re.findall(r"\[\(0, \d+\).*?\)\]", texto)
    assert len(selecoes) == 12
    for selecao in selecoes:
        assert len(re.findall(r"\(\d+, \d+\)", selecao)) == 5


def test_audiolivro_manifest_e_arquivos() -> None:
    assert MANIFEST.is_file(), "manifest.json do audiolivro ausente"
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["synthetic_voice"] is True
    assert manifest["voice_cloning"] is False
    assert manifest["voice"] == "pt-BR-FranciscaNeural"
    assert len(manifest["chapters"]) == 13
    total = 0.0
    for cap in manifest["chapters"]:
        arquivo = AUDIO / cap["file"]
        assert arquivo.is_file(), cap["file"]
        assert arquivo.stat().st_size > 1_000
        assert hashlib.sha256(arquivo.read_bytes()).hexdigest() == cap["sha256"]
        total += cap["duration_seconds"]
    assert abs(total - manifest["total_seconds"]) < 1.0
    completo = AUDIO / manifest["full_file"]
    assert completo.is_file()
    assert hashlib.sha256(completo.read_bytes()).hexdigest() == manifest["full_sha256"]
    assert completo.stat().st_size > 1_000_000


def test_audiolivro_duracao_total_e_selecao_declarada() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["total_seconds"] > 60
    assert "não é a narração integral" in manifest["note"]
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(AUDIO / manifest["full_file"])],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert abs(float(saida) - manifest["total_seconds"]) < 3.0
