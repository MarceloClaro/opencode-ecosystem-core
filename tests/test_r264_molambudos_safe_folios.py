# -*- coding: utf-8 -*-
"""Teste de regressão — SPEC-935-R264 (Molambudos 160x230mm, folios seguros).

A spec R264 originalmente registrava apenas "validação inline pypdf+PyMuPDF"
sem arquivo de teste — o que quebrava o registro SDD (test_file inexistente).
Este teste torna a validação repetível: verifica no PDF entregue o que a spec
prometeu (formato 160x230mm e ausência de hyperlinks/anotações clicáveis).

Se o artefato tiver sido arquivado fora do repositório, o teste é pulado —
sem fabricar aprovação.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PDF = (
    ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
    / "_archive" / "pdf_old"
    / "main_miolo_amazon_kdp_160x230mm_COM-FOLIOS_SEM-LINKS_SAFE-MARGINS.pdf"
)

MM_PER_PT = 25.4 / 72.0


@pytest.fixture(scope="module")
def reader():
    if not PDF.exists():
        pytest.skip(f"artefato R264 não presente no checkout: {PDF.name}")
    pypdf = pytest.importorskip("pypdf")
    return pypdf.PdfReader(str(PDF))


def test_formato_160x230mm(reader):
    box = reader.pages[0].mediabox
    width_mm = float(box.width) * MM_PER_PT
    height_mm = float(box.height) * MM_PER_PT
    assert abs(width_mm - 160.0) < 1.5, f"largura {width_mm:.1f}mm != 160mm"
    assert abs(height_mm - 230.0) < 1.5, f"altura {height_mm:.1f}mm != 230mm"


def test_sem_hyperlinks_clicaveis(reader):
    # Amostra determinística de páginas (documento grande; leitura preguiçosa)
    total = len(reader.pages)
    sample = sorted(set([0, 1, total // 4, total // 2, (3 * total) // 4, total - 1]))
    links = 0
    for index in sample:
        page = reader.pages[index]
        annots = page.get("/Annots") or []
        for ref in annots:
            annot = ref.get_object()
            if annot.get("/Subtype") == "/Link":
                links += 1
    assert links == 0, f"{links} anotação(ões) /Link na amostra de páginas {sample}"


def test_documento_tem_paginas(reader):
    assert len(reader.pages) > 100
