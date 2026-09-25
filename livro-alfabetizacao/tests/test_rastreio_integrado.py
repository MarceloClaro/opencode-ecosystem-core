#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do rastreio_integrado.py — SPEC-935-R211."""

from pathlib import Path

import pytest

import rastreio_integrado as ri

FIXTURES = Path(__file__).parent / "fixtures" / "rastreio"

DUMMY_CP = ri.Checkpoint(
    arquivo="rastreio-teste",
    rotulo="Rastreio Integrado Teste",
    quando="após a unidade teste",
    dominio="Consciência Fonológica",
    fichas="Ficha 1 (Dislexia)",
    itens_auto=["Item um", "Item dois", "Item tres", "Item quatro"],
    indicadores=["Ind A", "Ind B", "Ind C", "Ind D", "Ind E"],
    encaminhamento="Encaminhar ao profissional habilitado.",
)


def test_gera_latex_valido():
    tex = DUMMY_CP.to_latex()
    assert "\\begin{rastreio}[" in tex
    assert "Rastreio Integrado Teste" in tex
    assert "Ficha 1 (Dislexia)" in tex
    assert "Item um" in tex and "Ind E" in tex
    assert "não diagnostica" in tex
    # Sem loops LaTeX: tabular e itemize já vêm expandidos
    assert "\\foreach" not in tex
    assert "\\item Item um (\\textbf{SIM}) (\\textbf{NÃO})" in tex


def test_classe_tem_aviso_e_ambiente_rastreio():
    """A classe alfabetizar.cls deve expor o ambiente rastreio e o aviso ético."""
    cls = ri.VOLUME1 / "alfabetizar.cls"
    if not cls.exists():
        pytest.skip("alfabetizar.cls não presente neste checkout")
    texto = cls.read_text(encoding="utf-8")
    assert "\\newtcolorbox{rastreio}" in texto
    assert "não diagnostica" not in texto  # aviso fica no conteúdo gerado


def test_itens_e_indicadores_na_lista():
    tex = DUMMY_CP.to_latex()
    # O corpo deve conter cada item/indicador expandido explicitamente
    for it in DUMMY_CP.itens_auto:
        assert f"\\item {it} (\\textbf{{SIM}}) (\\textbf{{NÃO}})" in tex
    for ob in DUMMY_CP.indicadores:
        assert f"{ob} & & & & \\\\" in tex


def test_mapeamento_v1_tem_6_checkpoints():
    assert len(ri.CHECKPOINTS_V1) == 6
    nomes = [cp.arquivo for cp in ri.CHECKPOINTS_V1]
    assert nomes == ["rastreio-u1", "rastreio-u2", "rastreio-u3",
                     "rastreio-u4", "rastreio-u5", "rastreio-u6"]


def test_gerar_checkpoints_cria_arquivos(tmp_path):
    criados = ri.gerar_checkpoints(destino=tmp_path, cps=[DUMMY_CP])
    assert len(criados) == 1
    arquivo = tmp_path / "rastreio-teste.tex"
    assert arquivo.exists()
    conteudo = arquivo.read_text(encoding="utf-8")
    assert "\\begin{rastreio}[" in conteudo


def test_injecao_idempotente(tmp_path):
    # Monta um parte2 simulado com duas âncoras
    parte2 = tmp_path / "parte2-simulado.tex"
    parte2.write_text(
        "Unidade 1\n"
        "\\chapter{Unidade 2 --- Consonantes do Bloco 1}\n"
        "\\chapter{Unidade 3 --- Silabas Diretas}\n"
        "%% FIM DA PARTE II -- SEQUENCIA DIDATICA\n",
        encoding="utf-8",
    )
    ancoras = [
        (r"\\chapter\{Unidade 2 --- Consonantes do Bloco 1\}", "rastreio-u1"),
        (r"\\chapter\{Unidade 3 --- Silabas Diretas\}", "rastreio-u2"),
        (r"%% FIM DA PARTE II -- SEQUENCIA DIDATICA", "rastreio-u6"),
    ]
    acoes1 = ri.injetar(parte2, ancoras=[])  # lista vazia explícita: nenhuma ação
    assert acoes1 == []
    # Chamada 1
    acoes = ri.injetar(parte2, ancoras=ancoras, dry_run=True)
    assert len(acoes) == 3
    assert all(a.startswith("INJETADO") for a in acoes)
    # Chamada 2 (aplicação real) deve marcar como já presentes
    ri.injetar(parte2, ancoras=ancoras)
    acoes2 = ri.injetar(parte2, ancoras=ancoras)
    assert all(a.startswith("OK (já presente)") for a in acoes2)
    # Conteúdo final: inputs presentes e sem duplicação
    texto = parte2.read_text(encoding="utf-8")
    assert texto.count("\\input{checkpoints/rastreio-u1}") == 1
    assert texto.count("\\input{checkpoints/rastreio-u2}") == 1
    assert texto.count("\\input{checkpoints/rastreio-u6}") == 1


def test_ancoras_do_volume1_existem_no_arquivo_real():
    """Guarda contra drift: as âncoras do Volume 1 devem continuar no .tex real."""
    if not ri.SEQUENCIA.exists():
        pytest.skip("Volume 1 não presente neste checkout")
    texto = ri.SEQUENCIA.read_text(encoding="utf-8")
    for padrao, _nome in ri.ANCLAS_V1:
        assert padrao.strip("\\^${}[]()*+?.") or True  # apenas sanity
        import re as _re
        assert _re.search(padrao, texto), f"âncora ausente: {padrao}"