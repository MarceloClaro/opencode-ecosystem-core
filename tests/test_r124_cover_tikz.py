# -*- coding: utf-8 -*-
"""
Testes R124 — Capa e Contracapa com Arte Vetorial TikZ Real
=================================================================
Escritos ANTES da implementação (TDD). Elevam o CoverDesigner de
placeholders (bloco de cor + prompt de IA externa) para arte TikZ
compilável no PDF: gradiente, formas geométricas por estilo, lombada
dimensionada pela contagem de páginas e ficha catalográfica (CIP).

Requisitos: SPEC-935-R124. Retrocompatível com SPEC-019
(tests/test_cover_designer.py permanece verde).
"""
import os
import shutil
import tempfile

import pytest

from publishing.cover_designer import CoverDesigner


@pytest.fixture()
def tmp_out():
    d = tempfile.mkdtemp(prefix="cover_r124_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ── CA-1/CA-2: arte TikZ real na capa ─────────────────────────────
def test_capa_tem_arte_tikz(tmp_out):
    designer = CoverDesigner(tmp_out)
    rep = designer.design_cover("Manual de Python", "Autora",
                                "código e algoritmos de software")
    capa = open(rep["capa_file"], encoding="utf-8").read()
    assert "\\begin{tikzpicture}" in capa
    assert "\\end{tikzpicture}" in capa
    assert "\\shade" in capa                     # gradiente
    # retrocompatibilidade: base de cor + cor primária preservadas
    assert "\\pagecolor" in capa
    assert rep["palette"]["primary"] in capa


def test_arte_difere_por_estilo(tmp_out):
    d1 = CoverDesigner(os.path.join(tmp_out, "a"))
    d2 = CoverDesigner(os.path.join(tmp_out, "b"))
    tec = d1.design_cover("Manual de Python", "A", "código algoritmo software")
    # evita a substring "ia" (que o _determine_style do SPEC-019 casa com
    # "tecnologia") — texto de ficção puro para cair em 'ficcao'
    fic = d2.design_cover("A Sombra do Vale", "B", "conto sombrio de suspense e terror")
    assert tec["style"] != fic["style"]
    capa_tec = open(tec["capa_file"], encoding="utf-8").read()
    capa_fic = open(fic["capa_file"], encoding="utf-8").read()
    # o corpo TikZ (entre begin/end) deve diferir entre estilos
    def art(s):
        return s.split("\\begin{tikzpicture}", 1)[1].split("\\end{tikzpicture}", 1)[0]
    assert art(capa_tec) != art(capa_fic)


# ── fix: classificação por palavra inteira (não substring "ia") ───
def test_ficcao_nao_confundida_por_substring_ia(tmp_out):
    # "colônia"/"história" contêm "ia" como substring — não devem
    # classificar um romance como tecnologia (matching por \b agora)
    designer = CoverDesigner(tmp_out)
    rep = designer.design_cover(
        "O Diário da Colônia", "Autor",
        "terror psicológico e drama histórico numa colônia isolada")
    assert rep["style"] == "ficcao"


# ── CA-3: lombada dimensionada pela contagem de páginas ───────────
def test_lombada_gerada(tmp_out):
    designer = CoverDesigner(tmp_out)
    rep = designer.design_cover("Livro X", "Autor Y", "guia prático",
                                page_count=200)
    assert "lombada_file" in rep
    lombada = open(rep["lombada_file"], encoding="utf-8").read()
    assert "Livro X" in lombada
    assert "Autor Y" in lombada


def test_lombada_largura_cresce_com_paginas(tmp_out):
    d_fina = CoverDesigner(os.path.join(tmp_out, "fina"))
    d_grossa = CoverDesigner(os.path.join(tmp_out, "grossa"))
    r100 = d_fina.design_cover("T", "A", "guia", page_count=100)
    r400 = d_grossa.design_cover("T", "A", "guia", page_count=400)
    w100 = r100["spine_mm"]
    w400 = r400["spine_mm"]
    assert w400 > w100
    # a largura em mm deve aparecer no fragmento da lombada
    lom = open(r400["lombada_file"], encoding="utf-8").read()
    assert f"{w400}" in lom


# ── CA-4: ficha catalográfica na contracapa ───────────────────────
def test_contracapa_tem_ficha_catalografica(tmp_out):
    designer = CoverDesigner(tmp_out)
    rep = designer.design_cover("Livro X", "Autor Y", "história misteriosa",
                                isbn="978-65-00-00000-0")
    contra = open(rep["contracapa_file"], encoding="utf-8").read()
    # retrocompat SPEC-019
    assert "\\pagecolor" in contra
    assert "Sobre o Livro" in contra
    # ficha catalográfica CIP
    assert "Catalogação" in contra or "Catalogacao" in contra
    assert "CDD" in contra
    assert "978-65-00-00000-0" in contra


# ── CA-5: preâmbulo dos pacotes necessários ───────────────────────
def test_preambulo_gerado_com_pacotes(tmp_out):
    designer = CoverDesigner(tmp_out)
    rep = designer.design_cover("Livro X", "Autor", "guia")
    assert "preamble_file" in rep
    pre = open(rep["preamble_file"], encoding="utf-8").read()
    assert "\\usepackage{tikz}" in pre
    assert "HTML" in pre and "xcolor" in pre
    # o estudo de design deve explicar como incluir o preâmbulo
    study = open(rep["study_file"], encoding="utf-8").read()
    assert "cover_preamble" in study


# ── CA-6: retrocompatibilidade da assinatura ──────────────────────
def test_chamada_posicional_como_producao(tmp_out):
    # exatamente como production.py chama: (title, author, content_sample[:1000])
    designer = CoverDesigner(tmp_out)
    rep = designer.design_cover("Guia Didático de IA", "Prof. Teste",
                                "conteúdo didático e prático de IA")
    for k in ("style", "palette", "study_file", "capa_file",
              "contracapa_file", "lombada_file", "preamble_file"):
        assert k in rep, f"chave ausente no retorno: {k}"
    for k in ("capa_file", "contracapa_file", "lombada_file",
              "preamble_file", "study_file"):
        assert os.path.exists(rep[k]), f"arquivo não gerado: {k}"


# ── CA-7: integridade estrutural dos fragmentos ───────────────────
def test_tikzpicture_balanceado(tmp_out):
    designer = CoverDesigner(tmp_out)
    rep = designer.design_cover("Livro X", "Autor", "guia prático didático",
                                page_count=150, isbn="978-65-99999-9-9")
    for key in ("capa_file", "lombada_file"):
        txt = open(rep[key], encoding="utf-8").read()
        assert txt.count("\\begin{tikzpicture}") == txt.count("\\end{tikzpicture}")
        assert txt.count("{") == txt.count("}"), f"chaves desbalanceadas em {key}"
