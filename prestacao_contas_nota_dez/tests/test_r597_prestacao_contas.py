# -*- coding: utf-8 -*-
"""
R597 — Plugin Auditor e Executor de Prestação de Contas (Prêmio Escola Nota Dez)
=================================================================================
Cobre o pipeline: OCR de PDF escaneado → parse da diligência (cabeçalho, blocos,
demandas) → auditoria (checklist + score interno de conformidade) → executor
(minuta de ofício-resposta item-a-item + planilha de controle).

REGRA ANTI-OVERCLAIM: o "score" é interno (medida de cobertura da diligência),
NÃO é aprovação do órgão concedente. A aprovação final é decisão da SEDUC/CREDE.
"""
from pathlib import Path

import pytest

from prestacao_contas_nota_dez.src.diligencia import parse_diligencia, extrair_demandas
from prestacao_contas_nota_dez.src.auditor import auditar_diligencia, calcular_score
from prestacao_contas_nota_dez.src.executor import gerar_minuta, gerar_controle_csv

FIXTURE_DILIGENCIA = """GOVERNO DO ESTADO DO CEARÁ
Secretaria da Educação
Célula de Gestão Administrativo Financeira
13º CREDE

UNIDADE EXECUTORA: CONSELHO ESCOLAR DA ESCOLA DE CIDADANIA AIRAM VERAS
ENDEREÇO: RUA CAPISTRANO DE ABREU S/N - BAIRRO MARATOAN | PROCESSO: 05158910 DE 10/06/2019
MUNICÍPIO: CRATEUS CREDOR: 825943 CNPJ: 03.191.642/0001-03 CREDE: 13
RECURSOS: FECOP-10 R$ 24.500,00 NE: 18984 ANO:2018 PRÊMIO ESCOLA NOTA 10

DILIGÊNCIA

Analisando-se a prestação de contas da escola acima citada, constatamos as falhas abaixo
especificadas. Sendo assim, solicitamos que sejam tomadas as seguintes providências.

COMUM A TODAS AS LICITAÇÕES/OBJETO

PROCESSO:05158910 DATA:10/06/2019
NE: 18984 DATA: 11/06/2018 VALOR: 24.500,00

DEMANDAS:

* AUSÊNCIA NO OFÍCIO DE ENCAMINHAMENTO DA PRESTAÇÃO DE CONTA, DO Nº DA NOTA DE
EMPENHO E ANO. (PAG. 2)
* RETIFICAR O NÚMERO DA LEI QUE CRIOU O PROGRAMA ESCOLA NOTA 10 (PAG. 2)
* AUSÊNCIA DO CARIMBO COM A IDENTIFICAÇÃO DO ORDENADOR DE DESPESA NO
RELATÓRIO DE EXECUÇÃO FÍSICO-FINANCEIRO (PAG. 279)

DISPENSA DE LICITAÇÃO EM FUNÇÃO DO VALOR Nº 2018005

OBJETO DA AÇÃO: SERVIÇO DE DESLOCAMENTO PARA AULA DE CAMPO
VALOR ESTIMADO DA AÇÃO/OBJETOS: R$ 2.450,00

DEMANDAS:

* AUSÊNCIA NO MAPA COMPARATIVO DE PREÇO, DA ASSINATURA DO ORDENADOR DE
DESPESA (PAG. 27)
* AUSÊNCIA NO CARIMBO DE PAGO COM RECURSO DO NÚMERO DO CONVÊNIO E ANO NA
NOTA FISCAL (PAG. 35) E NO RECIBO (PAG. 36)
"""


class TestParseDiligencia:
    def test_extrai_cabecalho(self):
        doc = parse_diligencia(FIXTURE_DILIGENCIA, fonte="fixture")
        cab = doc["cabecalho"]
        assert cab["processo"] == "05158910"
        assert "AIRAM VERAS" in cab["unidade_executora"].upper()
        assert "CRATEUS" in cab["municipio"].upper()
        assert "03.191.642/0001-03" in cab["cnpj"]
        assert cab["ne"] == "18984"
        assert cab["valor"] == "24.500,00"
        assert cab["ano"] == "2018"

    def test_extrai_blocos_e_demandas(self):
        doc = parse_diligencia(FIXTURE_DILIGENCIA, fonte="fixture")
        blocos = doc["blocos"]
        assert len(blocos) == 2
        assert "COMUM A TODAS AS LICITA" in blocos[0]["titulo"].upper()
        assert "DISPENSA DE LICITA" in blocos[1]["titulo"].upper()
        # 3 demandas no bloco comum, 2 no bloco dispensa
        assert len(blocos[0]["demandas"]) == 3
        assert len(blocos[1]["demandas"]) == 2

    def test_demanda_carrega_pagina(self):
        doc = parse_diligencia(FIXTURE_DILIGENCIA, fonte="fixture")
        d = doc["blocos"][0]["demandas"][0]
        assert d["pagina"] == "2"
        assert "NOTA DE EMPENHO" in d["texto"].upper()


class TestExtrairDemandas:
    def test_contagem_total(self):
        demandas = extrair_demandas(FIXTURE_DILIGENCIA)
        assert len(demandas) == 5


class TestAuditor:
    def test_checklist_cobre_demandas(self):
        doc = parse_diligencia(FIXTURE_DILIGENCIA, fonte="fixture")
        checklist = auditar_diligencia(doc)
        assert len(checklist) == 5
        for item in checklist:
            assert item["id"]
            assert item["demanda"]
            assert item["status"] in {"pendente", "atendido"}

    def test_score_interno_transparente(self):
        doc = parse_diligencia(FIXTURE_DILIGENCIA, fonte="fixture")
        checklist = auditar_diligencia(doc)
        score = calcular_score(checklist)
        assert 0.0 <= score["cobertura"] <= 1.0
        assert score["pendentes"] == 5
        # Nenhum item marcado como atendido sem evidência
        assert score["atendidos"] == 0


class TestExecutor:
    def test_minuta_responde_item_a_item(self):
        doc = parse_diligencia(FIXTURE_DILIGENCIA, fonte="fixture")
        checklist = auditar_diligencia(doc)
        minuta = gerar_minuta(doc, checklist)
        assert "05158910" in minuta
        assert "OFÍCIO" in minuta.upper()
        for item in checklist:
            assert item["id"] in minuta

    def test_controle_csv(self, tmp_path: Path):
        doc = parse_diligencia(FIXTURE_DILIGENCIA, fonte="fixture")
        checklist = auditar_diligencia(doc)
        out = tmp_path / "controle.csv"
        gerar_controle_csv(checklist, out)
        assert out.exists()
        linhas = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(linhas) == 1 + 5  # cabeçalho + 5 itens
        assert "demanda" in linhas[0].lower()