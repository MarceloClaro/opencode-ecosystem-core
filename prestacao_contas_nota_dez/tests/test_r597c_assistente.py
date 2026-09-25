# -*- coding: utf-8 -*-
"""
R597c — Assistente de preenchimento da minuta (sugestões revisadas por humano)
==============================================================================
Cobre: classificação por tema, sugestão com excerto do manual-2019-ocr,
relatório anti-overclaim e aplicação segura (marcador [SUGESTÃO – REVISAR])
na minuta.
"""
from pathlib import Path

import pytest

from prestacao_contas_nota_dez.src.assistente import (
    classificar_item,
    gerar_relatorio_sugestoes,
    gerar_sugestoes,
)
from prestacao_contas_nota_dez.src.auditor import auditar_diligencia
from prestacao_contas_nota_dez.src.diligencia import parse_diligencia
from prestacao_contas_nota_dez.src.executor import gerar_minuta

DILIGENCIA = """GOVERNO DO ESTADO DO CEARÁ
Secretaria da Educação
13º CREDE

UNIDADE EXECUTORA: CONSELHO ESCOLAR DA ESCOLA DE CIDADANIA AIRAM VERAS
MUNICÍPIO: CRATEUS CNPJ: 03.191.642/0001-03
RECURSOS: FECOP-10 R$ 24.500,00 NE: 18109 ANO:2016

DILIGÊNCIA

COMUM A TODAS AS LICITAÇÕES/OBJETO

DEMANDAS:

* AUSÊNCIA DA DATA DO ATESTO NA NOTA FISCAL (PAG. 25) DO GESTOR DE COMPRAS
* AUSÊNCIA NO MAPA COMPARATIVO DE PREÇO, DA ASSINATURA DO ORDENADOR DE DESPESA (PAG. 27)
* AUSÊNCIA DA CONCILIAÇÃO BANCÁRIA (ANEXO VI)
* FALTA DE COMPROVANTE DE DEPÓSITO NA CONTA ESCOLAR (PAG. 2)
"""


@pytest.fixture(scope="module")
def doc():
    return parse_diligencia(DILIGENCIA, fonte="fixture")


@pytest.fixture(scope="module")
def checklist(doc):
    return auditar_diligencia(doc)


class TestClassificacao:
    def test_atesto_vira_tema_fiscal(self):
        cls = classificar_item("AUSÊNCIA DA DATA DO ATESTO NA NOTA FISCAL DAS COMPRAS")
        assert "Atesto" in cls["tema"]
        assert cls["pagina_manual"] == 31

    def test_mapa_comparativo(self):
        cls = classificar_item("REFAZER MAPA COMPARATIVO DE PREÇO SEGUNDO O MANUAL")
        assert "Mapa" in cls["tema"]
        assert cls["pagina_manual"] == 27

    def test_concilia_bancaria(self):
        cls = classificar_item("AUSÊNCIA DA CONCILIAÇÃO BANCÁRIA - ANEXO VI")
        assert "Conciliação" in cls["tema"]
        assert cls["pagina_manual"] == 30

    def test_fallback_generico(self):
        cls = classificar_item("ASSUNTO FORA DO CATÁLOGO DE TEMAS")
        assert cls["tema"] == "Outro"
        assert cls["pagina_manual"] is None
        assert cls["providencia_base"] == ""


class TestSugestoes:
    def test_gera_para_todos_os_itens(self, doc, checklist):
        sugestoes = gerar_sugestoes(checklist)
        assert len(sugestoes) == len(checklist)
        for s in sugestoes:
            assert s["id"]
            assert s["tema"]
            assert s["revisar"] is True

    def test_excerto_do_manual_quando_tem_pagina(self, checklist):
        sugestoes = gerar_sugestoes(checklist)
        com_pagina = [s for s in sugestoes if s["pagina_manual"]]
        assert com_pagina, "deveria haver ao menos um tema com página do manual"
        assert all(s["excerto_manual"] for s in com_pagina)

    def test_relatorio_anti_overclaim(self, doc, checklist):
        sugestoes = gerar_sugestoes(checklist)
        rel = gerar_relatorio_sugestoes(doc, sugestoes)
        assert "PARA REVISÃO HUMANA" in rel
        assert "imagem prevalece" in rel
        assert "não regularizam o processo" in rel
        assert "não fabrique documentos" in rel


class TestMinutaAssistida:
    def test_aplica_sugestao_com_marcador(self, doc, checklist):
        sugestoes = gerar_sugestoes(checklist)
        minuta = gerar_minuta(doc, checklist, sugestoes=sugestoes)
        assert "[SUGESTÃO – REVISAR]" in minuta
        # todos os ids continuam presentes
        for item in checklist:
            assert item["id"] in minuta

    def test_celula_vazia_sem_sugestao(self, doc, checklist):
        from prestacao_contas_nota_dez.src.assistente import gerar_sugestoes

        sugestoes = gerar_sugestoes(checklist)
        # remove a sugestão do 1o item para simular item sem proposta
        s = list(sugestoes)
        s[0]["providencia_sugerida"] = ""
        minuta = gerar_minuta(doc, checklist, sugestoes=s)
        assert "[SUGESTÃO – REVISAR]" in minuta  # demais itens mantêm
        assert "________________________" in minuta  # 1o item segue em branco

    def test_arquivo_sugestoes(self, doc, checklist, tmp_path: Path):
        from prestacao_contas_nota_dez.src.assistente import gerar_sugestoes_arquivo

        sugestoes = gerar_sugestoes(checklist)
        destino = tmp_path / "sugestoes.md"
        gerar_sugestoes_arquivo(doc, sugestoes, destino)
        texto = destino.read_text(encoding="utf-8")
        assert "SUGESTÕES" in texto.upper()
        assert sugestoes[0]["id"] in texto