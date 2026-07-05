# -*- coding: utf-8 -*-
"""
Testes TDD — SPEC-019: Automated Cover Designer + Internal Illustrator.
"""
import json
import os
import shutil
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from publishing.cover_designer import CoverDesigner, PALETTES
from publishing.production import ScientificProduction


@pytest.fixture()
def tmp_out():
    d = tempfile.mkdtemp(prefix="cover_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ── SPEC-019 / REQ-019.1: classificação de estilo ──

def test_estilo_tecnologia(tmp_out):
    designer = CoverDesigner(tmp_out)
    report = designer.design_cover("Manual de Python", "Autor",
                                   "código e algoritmos de software")
    assert report["style"] == "tecnologia"


def test_estilo_academico(tmp_out):
    designer = CoverDesigner(tmp_out)
    report = designer.design_cover("Tese de Doutorado", "Autor",
                                   "pesquisa e teorema com análise")
    assert report["style"] == "academico"


# ── SPEC-019 / INV-019.1: paleta com 5 cores hex ──

def test_paletas_tem_cinco_cores_hex():
    for name, pal in PALETTES.items():
        for key in ("primary", "secondary", "accent", "bg", "text"):
            assert key in pal, f"paleta '{name}' sem '{key}'"
            assert len(pal[key]) == 6, f"cor '{key}' de '{name}' não é hex de 6 dígitos"
            int(pal[key], 16)  # valida hexadecimal


# ── SPEC-019 / REQ-019.2 + INV-019.2: DESIGN_STUDY.md ──

def test_design_study_gerado(tmp_out):
    designer = CoverDesigner(tmp_out)
    report = designer.design_cover("Meu Livro", "Autor", "guia prático didático")
    study = open(report["study_file"], encoding="utf-8").read()
    assert "--ar 2:3" in study
    pal = report["palette"]
    for key in ("primary", "secondary", "accent"):
        assert pal[key] in study


# ── SPEC-019 / REQ-019.3 + INV-019.3: capa.tex e contracapa.tex ──

def test_capa_contracapa_latex(tmp_out):
    designer = CoverDesigner(tmp_out)
    report = designer.design_cover("Livro X", "Autor Y", "história misteriosa")
    capa = open(report["capa_file"], encoding="utf-8").read()
    contra = open(report["contracapa_file"], encoding="utf-8").read()
    assert "\\pagecolor" in capa
    assert report["palette"]["primary"] in capa
    assert "\\pagecolor" in contra
    assert "Sobre o Livro" in contra


# ── SPEC-019 / REQ-019.5 + REQ-019.6: ilustrações internas ──

LONG_PARA = ("A metacognição em sistemas multiagentes representa a capacidade "
             "de cada agente refletir sobre o próprio processo de raciocínio, "
             "ajustando estratégias, corrigindo erros e compartilhando lições "
             "aprendidas com os demais membros do coletivo de forma contínua.")

MD_SAMPLE = f"""# Capítulo 1

{LONG_PARA}

## Seção curta

Texto breve.
"""


def test_illustrate_internals_injeta_prompt(tmp_out):
    designer = CoverDesigner(tmp_out)
    out = designer.illustrate_internals(MD_SAMPLE, "didatico")
    assert "[ILUSTRAÇÃO DIDÁTICA SUGERIDA]" in out
    assert "--ar 16:9" in out
    pal = PALETTES["didatico"]
    assert pal["primary"] in out


def test_illustrate_internals_preserva_linhas_originais(tmp_out):
    designer = CoverDesigner(tmp_out)
    out = designer.illustrate_internals(MD_SAMPLE, "didatico")
    out_lines = out.splitlines()
    for line in MD_SAMPLE.splitlines():
        assert line in out_lines, f"linha original perdida: {line!r}"


def test_illustrate_internals_ignora_headers_listas(tmp_out):
    designer = CoverDesigner(tmp_out)
    md = ("# " + "x" * 200 + "\n"
          "- " + "y" * 200 + "\n"
          "> " + "z" * 200 + "\n")
    out = designer.illustrate_internals(md, "didatico")
    assert "[ILUSTRAÇÃO DIDÁTICA SUGERIDA]" not in out


# ── SPEC-019 / REQ-019.4 + REQ-019.7: integração com o pipeline ──

def test_pipeline_livro_gera_cover_e_ilustrado(tmp_out):
    prod = ScientificProduction(title="Guia Didático de IA",
                                template="livro",
                                author="Prof. Teste",
                                output_root=tmp_out)
    manifest = prod.build(MD_SAMPLE)
    assert manifest["cover_design"] is not None
    cd = manifest["cover_design"]
    assert cd["internal_prompts"] >= 1
    assert os.path.exists(cd["illustrated_manuscript"])
    assert os.path.exists(cd["capa_file"])
    assert os.path.exists(cd["contracapa_file"])
    assert os.path.exists(cd["study_file"])


def test_pipeline_artigo_nao_gera_cover(tmp_out):
    prod = ScientificProduction(title="Artigo Sem Capa",
                                template="artigo",
                                author="Prof. Teste",
                                output_root=tmp_out)
    manifest = prod.build(MD_SAMPLE)
    assert manifest["cover_design"] is None
