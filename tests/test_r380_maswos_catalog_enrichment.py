# -*- coding: utf-8 -*-
"""Testes de regressão — SPEC-935-R380 — Enriquecimento do Catálogo MASWOS.

Ciclo de migração de conteúdo (não de algoritmo novo): 46 agentes MASWOS
tinham description placeholder e corpo apontando para um caminho externo
inexistente; o conteúdo real foi portado de um diretório-fonte confirmado.
Este arquivo prova, de forma reproduzível, que a migração foi aplicada e
que nada quebrou no catálogo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CATALOG_DIR = ROOT / "agents" / "catalog"

MASWOS_46 = [
    "00_editor_chefe_phd", "01_agente_diagnostico_escopo",
    "02_agente_busca_curadoria", "03_agente_evidencias_citacoes",
    "04_agente_estrutura_argumentativa", "05_agente_revisao_literatura_teoria",
    "06_agente_metodologia_reprodutibilidade", "07_agente_estatistica_analise",
    "08_agente_visualizacao_evidencia_grafica", "09_agente_resultados",
    "10_agente_discussao_contribuicao", "11_agente_conclusao_coerencia_final",
    "12_agente_auditoria_bibliografica_abnt", "13_agente_qa_qualis_a1",
    "14_agente_consistencia_interna",
    "15_agente_resumo_abstract_palavras_chave",
    "16_agente_integracao_editorial_docx",
    "17_agente_framework_reprodutivel_ambientes",
    "18_agente_engenharia_dados_datasets_proveniencia",
    "19_agente_auditoria_codigo_documentacao_tecnica",
    "20_agente_estatistica_avancada_inferencia",
    "21_agente_matematica_aplicada_modelagem_formal",
    "22_agente_ml_dl_datamining",
    "23_agente_bioinformatica_omicas",
    "24_agente_quimioinformatica_modelagem_molecular",
    "25_agente_ciencias_sociais_linguistica_computacional",
    "26_agente_visao_computacional_multimodal",
    "27_agente_computacao_quantica_aplicada",
    "28_agente_benchmarking_ablacao_robustez",
    "29_agente_conformidade_internacional",
    "30_agente_traducao_nativa_proofreading",
    "31_agente_blind_peer_review_emulado",
    "32_agente_etica_open_science",
    "33_agente_automacao_multi_norma",
    "34_agente_identificacao_conflitos_similaridade",
    "35_agente_coleta_datasets_reais",
    "36_agente_exportacao_latex_pdf",
    "37_agente_apresentacao_slides_banca",
    "38_agente_montagem_entrega_final",
    "39_agente_metodologia_multi_paradigma",
    "40_agente_marcos_teoricos_interpretacao",
    "41_agente_gis_geoprocessamento_cartografia",
    "42_agente_desenvolvedor_cientista_computacao",
    "43_agente_satelite_bioinformatica_omics",
    "44_agente_correcao_textual_qualis",
    "45_agente_refinamento_argumentacao",
]

_EXTERNAL_MARKERS = (
    "criador-artigo\\agents",
    "references/formulas",
    "templates/TEMPLATE_",
)


@pytest.fixture(scope="module")
def catalog_defs():
    from marceloclaro.catalog_loader import load_catalog_definitions
    return load_catalog_definitions()


class TestMigracaoAplicada:
    def test_46_arquivos_existem(self):
        for agent_id in MASWOS_46:
            assert (CATALOG_DIR / f"{agent_id}.md").exists(), agent_id

    @pytest.mark.parametrize("agent_id", MASWOS_46)
    def test_sem_description_placeholder(self, agent_id, catalog_defs):
        by_id = {d["agent_id"]: d for d in catalog_defs}
        assert agent_id in by_id
        desc = by_id[agent_id]["description"].strip().lower()
        assert not desc.startswith("agente especializado"), agent_id

    @pytest.mark.parametrize("agent_id", MASWOS_46)
    def test_yaml_frontmatter_valido(self, agent_id):
        text = (CATALOG_DIR / f"{agent_id}.md").read_text(encoding="utf-8")
        import re
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        assert m, f"{agent_id}: frontmatter não encontrado"
        yaml.safe_load(m.group(1))  # não deve lançar

    @pytest.mark.parametrize("agent_id", MASWOS_46)
    def test_nota_de_proveniencia_presente(self, agent_id):
        text = (CATALOG_DIR / f"{agent_id}.md").read_text(encoding="utf-8")
        assert "Conteúdo migrado de" in text
        assert "SPEC-935-R380" in text

    @pytest.mark.parametrize("agent_id", MASWOS_46)
    def test_sem_caminho_externo_pendurado(self, agent_id):
        text = (CATALOG_DIR / f"{agent_id}.md").read_text(encoding="utf-8")
        for marker in _EXTERNAL_MARKERS:
            assert marker not in text, f"{agent_id}: ainda referencia {marker!r}"


class TestCatalogoIntacto:
    def test_205_registros_carregam(self, catalog_defs):
        assert len(catalog_defs) == 205

    def test_placeholder_restante_e_o_esperado(self, catalog_defs):
        """53 registros fora do escopo deste ciclo continuam com placeholder
        -- achado documentado, não regressão.

        Era 54 quando esta contagem foi fixada; `contextscout.md` tinha dois
        blocos de frontmatter empilhados (um placeholder genérico primeiro,
        cobrindo o card real e rico com as permissões de segurança logo
        abaixo) -- corrigido removendo o placeholder duplicado (ciclo de
        triagem de 2026-08-03), o que também restaurou a aplicação real das
        negações write/edit desse agente (ver test_r212_opencode_permissions).
        """
        placeholders = [
            d["agent_id"] for d in catalog_defs
            if d["description"].strip().lower().startswith("agente especializado")
        ]
        assert len(placeholders) == 56  # 53 remanescentes + 3 artefatos não-agente
        for agent_id in MASWOS_46:
            assert agent_id not in placeholders
