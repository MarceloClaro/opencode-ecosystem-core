# -*- coding: utf-8 -*-
"""
Testes TDD — SPEC-923: Integração AUXJURIS no Ecossistema
==========================================================

Cobertura:
  1. 4 agentes jurídicos A2A
  2. Agent Cards compatíveis com Blackboard
  3. Resolvedor heurístico de agentes
  4. Base de conhecimento jurídica (keywords + RAG)
  5. Carga de documentos do Datajud na knowledge base
  6. Sumarizador de documentos jurídicos
  7. Registro dos agentes no catálogo OpenCode
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAuxJurisAgents:
    def test_legal_agents_count_and_ids(self):
        from legal import LEGAL_AGENTS

        ids = {agent.id for agent in LEGAL_AGENTS}
        assert len(LEGAL_AGENTS) == 4
        assert ids == {
            "auxjuris_legal_assistant",
            "auxjuris_document_summarizer",
            "auxjuris_email_drafter",
            "auxjuris_legal_research",
        }

    def test_agent_cards_are_blackboard_compatible(self):
        from legal import get_all_legal_agent_cards

        cards = get_all_legal_agent_cards()
        assert len(cards) == 4
        for card in cards:
            assert isinstance(card["agent_id"], str)
            assert isinstance(card["name"], str)
            assert isinstance(card["description"], str)
            assert isinstance(card["capabilities"], list)
            assert "schema" in card
            assert "system_prompt" in card["schema"]
            assert "legal" in card["capabilities"]

    def test_resolve_legal_agent_heuristics(self):
        from legal import resolve_legal_agent

        assert resolve_legal_agent("resuma esta petição").id == "auxjuris_document_summarizer"
        assert resolve_legal_agent("redija um email ao cliente").id == "auxjuris_email_drafter"
        assert resolve_legal_agent("pesquise jurisprudência do stj").id == "auxjuris_legal_research"
        assert resolve_legal_agent("analise este caso de responsabilidade civil").id == "auxjuris_legal_assistant"

    def test_register_legal_agents_on_blackboard(self):
        from legal import register_legal_agents
        from mci.blackboard import blackboard
        from mci.metabus import metabus

        count = register_legal_agents(metabus)
        assert count == 4
        for agent_id in [
            "auxjuris_legal_assistant",
            "auxjuris_document_summarizer",
            "auxjuris_email_drafter",
            "auxjuris_legal_research",
        ]:
            assert agent_id in blackboard.registry


class TestLegalKnowledgeBase:
    def test_default_documents_loaded(self):
        from legal import LegalKnowledgeBase

        kb = LegalKnowledgeBase()
        assert kb.count() >= 6
        cats = kb.get_categories()
        assert "doutrina" in cats
        assert "legislacao" in cats

    def test_add_and_search_document(self):
        from legal import LegalKnowledgeBase, LegalDocument

        kb = LegalKnowledgeBase()
        kb.add_document(LegalDocument(
            id="doc_teste_auxjuris",
            title="Teste AuxJuris",
            content="Este documento trata de arbitragem societária e cláusula compromissória.",
            keywords=["arbitragem", "societária", "cláusula compromissória"],
            category="doutrina",
        ))

        results = kb.search("cláusula compromissória arbitragem")
        assert len(results) >= 1
        assert results[0][0].id == "doc_teste_auxjuris"
        assert results[0][1] > 0

    def test_rag_context_respects_limit(self):
        from legal import LegalKnowledgeBase

        kb = LegalKnowledgeBase()
        context = kb.rag_context("responsabilidade civil dano moral", max_chars=300)
        assert context.startswith("Contexto de Documentos")
        assert len(context) <= 350
        assert "responsabilidade" in context.lower() or "dano" in context.lower()

    def test_load_from_datajud(self):
        from legal import LegalKnowledgeBase, DatajudClient

        kb = LegalKnowledgeBase()
        client = DatajudClient(offline=True)
        processos = client.search("tjsp")
        added = kb.load_from_datajud(processos)

        assert added >= 1
        assert kb.count() >= 7
        results = kb.search("procedimento comum cível")
        assert len(results) >= 1


class TestLegalSummarizer:
    def test_summarize_extracts_entities(self):
        from legal import LegalDocumentSummarizer

        text = (
            "Autor: João da Silva. Réu: Banco XPTO. Com base no art. 186 do Código Civil "
            "e no art. 927 do CC/2002, requer indenização por dano moral. O STJ no REsp 1234/2020 "
            "já reconheceu a responsabilidade civil em caso análogo. Ao final, pede procedência."
        )
        result = LegalDocumentSummarizer().summarize(text, titulo="Petição Inicial")

        assert result.titulo == "Petição Inicial"
        assert result.resumo != ""
        assert result.compression_ratio >= 0
        assert any("186" in art or "927" in art for art in result.entidades.artigos)
        assert "STJ" in result.entidades.tribunais
        assert len(result.fundamentos) >= 1

    def test_summarize_empty_document(self):
        from legal import LegalDocumentSummarizer

        result = LegalDocumentSummarizer().summarize("   ")
        assert result.resumo == "Documento sem conteúdo."
        assert result.compression_ratio == 0.0


class TestAuxJurisCatalogIntegration:
    def test_catalog_loader_finds_auxjuris_agents(self):
        from marceloclaro.catalog_loader import load_catalog_definitions

        definitions = load_catalog_definitions()
        auxjuris = [d for d in definitions if d["agent_id"].startswith("auxjuris_")]
        ids = {d["agent_id"] for d in auxjuris}

        assert len(auxjuris) == 4
        assert ids == {
            "auxjuris_legal_assistant",
            "auxjuris_document_summarizer",
            "auxjuris_email_drafter",
            "auxjuris_legal_research",
        }
        for definition in auxjuris:
            assert "legal" in definition["capabilities"]
            assert definition["category"] == "legal"
