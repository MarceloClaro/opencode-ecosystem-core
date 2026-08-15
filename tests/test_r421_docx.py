# -*- coding: utf-8 -*-
"""Testes R421 — Exportação DOCX do artigo RBEP (SPEC-935-R421).

Requisitos:
1. `scripts/export_docx_rbep.py` gera `outputs/docx/ARTIGO_RBEP_SUBMISSAO.docx`
   a partir do MD canônico via pandoc, com reference ABNT e MANIFEST.json.
2. DOCX com margens ABNT (esq/sup 3 cm; dir/inf 2 cm), página A4,
   fonte Times New Roman, 14+ tabelas com bordas, espaçamento 1,5.
3. Conteúdo crítico do manuscrito presente (incluindo Apêndice A).
4. Suíte R408–R421 verde.
"""

import json
import hashlib
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
DOCX = AUDIT / "outputs" / "docx" / "ARTIGO_RBEP_SUBMISSAO.docx"
MANIFEST = AUDIT / "outputs" / "docx" / "MANIFEST.json"
SCRIPT = AUDIT / "scripts" / "export_docx_rbep.py"
MD = AUDIT / "ARTIGO_RBEP_SUBMISSAO.md"

docx = pytest.importorskip("docx")


class TestArtefatos:
    def test_script_existe(self):
        assert SCRIPT.exists()

    def test_docx_existe(self):
        assert DOCX.exists(), "outputs/docx/ARTIGO_RBEP_SUBMISSAO.docx ausente"

    def test_manifest_existe(self):
        assert MANIFEST.exists()

    def test_manifest_sha256_bate(self):
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        h = hashlib.sha256(DOCX.read_bytes()).hexdigest()
        assert m["docx"]["sha256"] == h


class TestEstrutura:
    def test_margens_abnt(self):
        doc = docx.Document(str(DOCX))
        sec = doc.sections[0]
        assert abs(sec.left_margin.cm - 3.0) < 0.05
        assert abs(sec.top_margin.cm - 3.0) < 0.05
        assert abs(sec.right_margin.cm - 2.0) < 0.05
        assert abs(sec.bottom_margin.cm - 2.0) < 0.05

    def test_pagina_a4(self):
        doc = docx.Document(str(DOCX))
        sec = doc.sections[0]
        assert abs(sec.page_width.cm - 21.0) < 0.05
        assert abs(sec.page_height.cm - 29.7) < 0.05

    def test_tabelas_suficientes(self):
        doc = docx.Document(str(DOCX))
        assert len(doc.tables) >= 14, f"esperava 14+ tabelas, há {len(doc.tables)}"

    def test_tabela_8_brasil(self):
        doc = docx.Document(str(DOCX))
        t = doc.tables[7]
        assert len(t.rows) == 8
        assert "Brasil" in t.rows[1].cells[0].text

    def test_tabelas_glossario(self):
        doc = docx.Document(str(DOCX))
        texto_tabs = " ".join(
            t.rows[0].cells[0].text for t in doc.tables[-3:]
        )
        assert "Símbolo" in texto_tabs
        assert "Código" in texto_tabs
        assert "Sigla" in texto_tabs


class TestConteudo:
    def test_conteudo_critico(self):
        doc = docx.Document(str(DOCX))
        texto = "\n".join(p.text for p in doc.paragraphs)
        for termo in ["Apêndice A", "SE.TER.ENRR", "NY.GDP.PCAP.KD",
                      "0,751", "0,146", "0,604", "LOOCV", "GroupKFold"]:
            assert termo in texto, f"termo ausente no DOCX: {termo}"

    def test_apendice_depois_referencias(self):
        doc = docx.Document(str(DOCX))
        textos = [p.text for p in doc.paragraphs]
        idx_refs = next(i for i, t in enumerate(textos) if t.strip() == "Referências")
        idx_ap = next(i for i, t in enumerate(textos) if "Apêndice A" in t)
        assert idx_refs < idx_ap
