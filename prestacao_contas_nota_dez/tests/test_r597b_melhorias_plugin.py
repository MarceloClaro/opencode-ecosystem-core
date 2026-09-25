# -*- coding: utf-8 -*-
"""
R597b — Melhorias do plugin a partir das referências contas-escolares-airam-veras
=================================================================================
Cobre: estados documentais/de tramitação (modelo do plugin Codex), verificação
documental base (checklist-base.csv C01–C40), minuta em formato administrativo
(tabela Item | Exigência | Resposta | Anexo | Pendência) e relatório de
conferência com anti-overclaim explícito.
"""
from pathlib import Path

import pytest

from prestacao_contas_nota_dez.src.auditor import auditar_diligencia, calcular_score, consolidar_estados
from prestacao_contas_nota_dez.src.diligencia import parse_diligencia
from prestacao_contas_nota_dez.src.executor import gerar_minuta
from prestacao_contas_nota_dez.src.relatorio import gerar_relatorio
from prestacao_contas_nota_dez.src.verificacao import (
    carregar_checklist_base,
    gerar_tabela_base,
    grupos_disponiveis,
)

DILIGENCIA = """GOVERNO DO ESTADO DO CEARÁ
Secretaria da Educação
13º CREDE

UNIDADE EXECUTORA: CONSELHO ESCOLAR DA ESCOLA DE CIDADANIA AIRAM VERAS
MUNICÍPIO: CRATEUS CNPJ: 03.191.642/0001-03
RECURSOS: FECOP-10 R$ 24.500,00 NE: 18109 ANO:2016

DILIGÊNCIA

COMUM A TODAS AS LICITAÇÕES/OBJETO

DEMANDAS:

* AUSÊNCIA DO REPRESENTANTE DOS ALUNOS NA ATA (PAG. 5)

DISPENSA DE LICITAÇÃO EM FUNÇÃO DO VALOR Nº 2018005

DEMANDAS:

* AUSÊNCIA DO CARIMBO DE PAGO NA NOTA FISCAL (PAG. 35)
"""


@pytest.fixture(scope="module")
def doc():
    return parse_diligencia(DILIGENCIA, fonte="fixture")


class TestVerificacaoBase:
    def test_carrega_checklist_base(self):
        itens = carregar_checklist_base()
        assert len(itens) >= 35
        primeiro = itens[0]
        assert primeiro["id"].startswith("C0")
        assert {"id", "grupo", "verificacao", "condicao", "referencia_historica"} <= set(primeiro)

    def test_grupos_e_tabela(self):
        itens = carregar_checklist_base()
        grupos = grupos_disponiveis(itens)
        assert "Financeiro" in grupos
        assert "Contratacao" in grupos
        tabela = gerar_tabela_base(itens)
        assert "| ID |" in tabela and "C40" in tabela


class TestEstados:
    def test_estados_iniciais(self, doc):
        checklist = auditar_diligencia(doc)
        for item in checklist:
            assert item["estado_documental"] == "não examinado"
            assert item["estado_tramitacao"] == "identificado"

    def test_consolidar_estados(self, doc):
        checklist = auditar_diligencia(doc)
        estados = consolidar_estados(checklist)
        assert estados["documental"]["não examinado"] == len(checklist)
        assert estados["tramitacao"]["identificado"] == len(checklist)


class TestMinutaAdministrativa:
    def test_formato_tabela_e_cabecalho(self, doc):
        checklist = auditar_diligencia(doc)
        minuta = gerar_minuta(doc, checklist)
        assert "MINUTA PARA REVISÃO E ASSINATURA" in minuta
        assert "Ofício nº [PENDENTE: número]" in minuta
        assert "| Item | Exigência e origem |" in minuta
        assert "Pendência remanescente" in minuta
        assert "Índice de anexos" in minuta
        for item in checklist:
            assert item["id"] in minuta

    def test_minuta_nao_declara_aprovacao(self, doc):
        checklist = auditar_diligencia(doc)
        minuta = gerar_minuta(doc, checklist)
        assert "decisão exclusiva da SEDUC" in minuta


class TestRelatorio:
    def test_relatorio_anti_overclaim(self, doc):
        checklist = auditar_diligencia(doc)
        score = calcular_score(checklist)
        rel = gerar_relatorio(doc, checklist, score, fonte="fixture")
        assert "Relatório de conferência" in rel
        assert "é probabilidade de aprovação" in rel
        assert "não certifica regularidade" in rel
        assert "não declara aprovação" in rel
        # não pode conter afirmação de aprovação do órgão
        assert "aprovado pela SEDUC" not in rel
        assert "aceite comprovado pelo órgão: 0" in rel

    def test_relatorio_arquivo(self, doc, tmp_path: Path):
        from prestacao_contas_nota_dez.src.relatorio import gerar_relatorio_arquivo

        checklist = auditar_diligencia(doc)
        score = calcular_score(checklist)
        destino = tmp_path / "relatorio.md"
        gerar_relatorio_arquivo(doc, checklist, score, destino)
        assert destino.exists()
        assert "Relatório de conferência" in destino.read_text(encoding="utf-8")