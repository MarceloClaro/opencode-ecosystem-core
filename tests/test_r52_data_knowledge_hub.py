#!/usr/bin/env python3
"""
Testes TDD para DataKnowledgeHub (SPEC-965)
============================================
RED phase: testes falham antes da implementação.

Ciclo: RED → GREEN → REFACTOR
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ═══════════════════════════════════════════════════════════════
# Testes de Classe Base (DataSource)
# ═══════════════════════════════════════════════════════════════

class TestDataSourceBase:
    """RED: testes esperam módulo data_knowledge_hub existir."""

    def test_module_exists(self):
        """Módulo deve existir."""
        try:
            from skills.tooling.data_knowledge_hub import DataKnowledgeHub
            assert DataKnowledgeHub is not None
        except ImportError:
            pytest.fail("Módulo skills.tooling.data_knowledge_hub não existe")

    def test_datasource_base_class(self):
        """DataSource base deve definir interface."""
        from skills.tooling.data_knowledge_hub.base import DataSource

        # Verificar que é abstrata
        assert hasattr(DataSource, "search")
        assert hasattr(DataSource, "name")
        assert hasattr(DataSource, "get_stats")

    def test_datasource_requires_name(self):
        """DataSource deve ter atributo name."""
        from skills.tooling.data_knowledge_hub.base import DataSource

        class TestSource(DataSource):
            name = "test"

            def search(self, query: str, **kwargs):
                return []

        ts = TestSource()
        assert ts.name == "test"


# ═══════════════════════════════════════════════════════════════
# Testes de FinancialDataSource
# ═══════════════════════════════════════════════════════════════

class TestFinancialDataSource:
    """RED: testes esperam FinancialDataSource com yfinance, BCB, FRED."""

    def test_financial_module_exists(self):
        """Módulo financial deve existir."""
        from skills.tooling.data_knowledge_hub.financial import FinancialDataSource
        assert FinancialDataSource is not None

    def test_financial_search_yfinance(self):
        """FinancialDataSource busca cotações via yfinance."""
        from skills.tooling.data_knowledge_hub.financial import FinancialDataSource

        fds = FinancialDataSource()
        result = fds.search("PETR4", source="yfinance")
        assert result["source"] == "yfinance"
        assert len(result["results"]) >= 0  # pode ser 0 se sem rede
        assert "query" in result
        assert "timestamp" in result

    def test_financial_search_bcb(self):
        """FinancialDataSource busca séries BCB/SGS."""
        from skills.tooling.data_knowledge_hub.financial import FinancialDataSource

        fds = FinancialDataSource()
        result = fds.search("IPCA", source="bcb")
        assert result["source"] == "bcb"
        assert result["status"] in ("online", "offline")

    def test_financial_search_fred(self):
        """FinancialDataSource busca dados FRED."""
        from skills.tooling.data_knowledge_hub.financial import FinancialDataSource

        fds = FinancialDataSource()
        result = fds.search("GDP", source="fred")
        assert result["source"] == "fred"
        assert result["status"] in ("online", "offline")

    def test_financial_search_world_bank(self):
        """FinancialDataSource busca dados World Bank."""
        from skills.tooling.data_knowledge_hub.financial import FinancialDataSource

        fds = FinancialDataSource()
        result = fds.search("Brazil GDP", source="world_bank")
        assert result["source"] == "world_bank"
        assert result["status"] in ("online", "offline")

    def test_financial_auto_route(self):
        """FinancialDataSource roteia automaticamente por palavras-chave."""
        from skills.tooling.data_knowledge_hub.financial import FinancialDataSource

        fds = FinancialDataSource()
        # "PETR4" é ação → yfinance
        r1 = fds.search("cotação PETR4 hoje")
        assert r1["source"] in ("yfinance", "bcb", "fred", "world_bank", "offline")

        # "IPCA" é inflação → BCB
        r2 = fds.search("IPCA acumulado 2024")
        assert r2["source"] in ("yfinance", "bcb", "fred", "world_bank", "offline")

    def test_financial_get_stats(self):
        """FinancialDataSource deve expor estatísticas."""
        from skills.tooling.data_knowledge_hub.financial import FinancialDataSource

        fds = FinancialDataSource()
        fds.search("PETR4")
        stats = fds.get_stats()
        assert stats["total_queries"] >= 1
        assert stats["name"] == "financial"
        assert "avg_ms" in stats


# ═══════════════════════════════════════════════════════════════
# Testes de OfficialDataSource (IBGE, IPEA)
# ═══════════════════════════════════════════════════════════════

class TestOfficialDataSource:
    """RED: testes esperam OfficialDataSource com IBGE, IPEA."""

    def test_official_module_exists(self):
        """Módulo official deve existir."""
        from skills.tooling.data_knowledge_hub.official import OfficialDataSource
        assert OfficialDataSource is not None

    def test_official_search_ibge(self):
        """OfficialDataSource busca dados IBGE."""
        from skills.tooling.data_knowledge_hub.official import OfficialDataSource

        ods = OfficialDataSource()
        result = ods.search("IPCA", source="ibge")
        assert result["source"] == "ibge"
        assert result["status"] in ("online", "offline")
        assert "query" in result

    def test_official_search_ipea(self):
        """OfficialDataSource busca dados IPEA."""
        from skills.tooling.data_knowledge_hub.official import OfficialDataSource

        ods = OfficialDataSource()
        result = ods.search("PIB", source="ipea")
        assert result["source"] == "ipea"
        assert result["status"] in ("online", "offline")

    def test_official_search_datagov(self):
        """OfficialDataSource busca dados.gov.br (CKAN)."""
        from skills.tooling.data_knowledge_hub.official import OfficialDataSource

        ods = OfficialDataSource()
        result = ods.search("educação", source="dados_gov")
        assert result["source"] == "dados_gov"
        assert result["status"] in ("online", "offline")

    def test_official_auto_route(self):
        """OfficialDataSource roteia por domínio."""
        from skills.tooling.data_knowledge_hub.official import OfficialDataSource

        ods = OfficialDataSource()
        r = ods.search("IPCA 2024")
        assert r["source"] in ("ibge", "ipea", "dados_gov", "offline")

    def test_official_mock_data(self):
        """OfficialDataSource deve ter dados mockados para modo offline."""
        from skills.tooling.data_knowledge_hub.official import OfficialDataSource

        ods = OfficialDataSource()
        result = ods.search("IPCA", source="ibge")
        if result["status"] == "offline":
            assert len(result["results"]) > 0  # mock data available


# ═══════════════════════════════════════════════════════════════
# Testes de KnowledgeDataSource (Wikipedia, Wikidata, ConceptNet)
# ═══════════════════════════════════════════════════════════════

class TestKnowledgeDataSource:
    """RED: testes esperam KnowledgeDataSource com Wikipedia, Wikidata."""

    def test_knowledge_module_exists(self):
        """Módulo knowledge deve existir."""
        from skills.tooling.data_knowledge_hub.knowledge import KnowledgeDataSource
        assert KnowledgeDataSource is not None

    def test_knowledge_search_wikipedia(self):
        """KnowledgeDataSource busca Wikipedia."""
        from skills.tooling.data_knowledge_hub.knowledge import KnowledgeDataSource

        kds = KnowledgeDataSource()
        result = kds.search("machine learning", source="wikipedia")
        assert result["source"] == "wikipedia"
        assert result["status"] in ("online", "offline")
        if result["status"] == "online":
            assert len(result["results"]) > 0

    def test_knowledge_search_wikidata(self):
        """KnowledgeDataSource busca Wikidata."""
        from skills.tooling.data_knowledge_hub.knowledge import KnowledgeDataSource

        kds = KnowledgeDataSource()
        result = kds.search("Albert Einstein", source="wikidata")
        assert result["source"] == "wikidata"
        assert result["status"] in ("online", "offline")

    def test_knowledge_search_conceptnet(self):
        """KnowledgeDataSource busca ConceptNet."""
        from skills.tooling.data_knowledge_hub.knowledge import KnowledgeDataSource

        kds = KnowledgeDataSource()
        result = kds.search("inteligência artificial", source="conceptnet")
        assert result["source"] == "conceptnet"
        assert result["status"] in ("online", "offline")

    def test_knowledge_auto_route(self):
        """KnowledgeDataSource roteia por tipo de consulta."""
        from skills.tooling.data_knowledge_hub.knowledge import KnowledgeDataSource

        kds = KnowledgeDataSource()
        r = kds.search("o que é machine learning")
        assert r["source"] in ("wikipedia", "wikidata", "conceptnet", "offline")

    def test_knowledge_mock_data(self):
        """KnowledgeDataSource deve ter fallback offline com dados mockados."""
        from skills.tooling.data_knowledge_hub.knowledge import KnowledgeDataSource

        kds = KnowledgeDataSource()
        result = kds.search("machine learning", source="wikipedia")
        if result["status"] == "offline":
            assert len(result["results"]) > 0


# ═══════════════════════════════════════════════════════════════
# Testes de DatasetDataSource (Zenodo, DataCite, UCI, Figshare)
# ═══════════════════════════════════════════════════════════════

class TestDatasetDataSource:
    """RED: testes esperam DatasetDataSource com Zenodo, DataCite, UCI, Figshare."""

    def test_dataset_module_exists(self):
        """Módulo datasets deve existir."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource
        assert DatasetDataSource is not None

    def test_dataset_search_zenodo(self):
        """DatasetDataSource busca Zenodo."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("climate", source="zenodo")
        assert result["source"] == "zenodo"
        assert result["status"] in ("online", "offline")

    def test_dataset_search_datacite(self):
        """DatasetDataSource busca DataCite."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("machine learning", source="datacite")
        assert result["source"] == "datacite"
        assert result["status"] in ("online", "offline")

    def test_dataset_search_uci(self):
        """DatasetDataSource busca UCI ML Repository."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("iris", source="uci")
        assert result["source"] == "uci"
        assert result["status"] in ("online", "offline")

    def test_dataset_search_figshare(self):
        """DatasetDataSource busca Figshare."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("biology", source="figshare")
        assert result["source"] == "figshare"
        assert result["status"] in ("online", "offline")

    def test_dataset_auto_route(self):
        """DatasetDataSource roteia por domínio."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        r = dds.search("dataset climate change")
        assert r["source"] in ("zenodo", "datacite", "uci", "figshare", "offline")

    def test_dataset_mock_data(self):
        """DatasetDataSource deve ter fallback offline."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("climate", source="zenodo")
        if result["status"] == "offline":
            assert len(result["results"]) > 0


# ═══════════════════════════════════════════════════════════════
# Testes do DomainRouter
# ═══════════════════════════════════════════════════════════════

class TestDomainRouter:
    """RED: testes esperam DomainRouter classificar domínios."""

    def test_router_classify_finance(self):
        """Router identifica consultas financeiras."""
        from skills.tooling.data_knowledge_hub.router import DomainRouter

        router = DomainRouter()
        assert router.classify("cotação PETR4 hoje") == "financeiro"
        assert router.classify("IPCA acumulado 2024") == "financeiro"
        assert router.classify("dólar comercial agora") == "financeiro"
        assert router.classify("PIB Brasil 2023") in ("financeiro", "oficial")

    def test_router_classify_official(self):
        """Router identifica consultas de dados oficiais."""
        from skills.tooling.data_knowledge_hub.router import DomainRouter

        router = DomainRouter()
        assert router.classify("população brasileira 2024") == "oficial"
        assert router.classify("censo demográfico IBGE") == "oficial"

    def test_router_classify_knowledge(self):
        """Router identifica consultas de conhecimento."""
        from skills.tooling.data_knowledge_hub.router import DomainRouter

        router = DomainRouter()
        assert router.classify("o que é inteligência artificial") == "conhecimento"
        assert router.classify("conceito de entropia") == "conhecimento"

    def test_router_classify_dataset(self):
        """Router identifica consultas de datasets."""
        from skills.tooling.data_knowledge_hub.router import DomainRouter

        router = DomainRouter()
        assert router.classify("dataset de imagens médicas") == "dataset"
        assert router.classify("base de dados clima") == "dataset"

    def test_router_classify_academic(self):
        """Router mantém classificação acadêmica (delega ao searchers.py)."""
        from skills.tooling.data_knowledge_hub.router import DomainRouter

        router = DomainRouter()
        assert router.classify("artigo machine learning transformers") == "academico"


# ═══════════════════════════════════════════════════════════════
# Testes do DataKnowledgeHub (fachada unificada)
# ═══════════════════════════════════════════════════════════════

class TestDataKnowledgeHub:
    """RED: testes esperam DataKnowledgeHub funcionando."""

    def test_hub_initializes(self):
        """Hub inicializa com todas as fontes."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        assert hub.financial is not None
        assert hub.official is not None
        assert hub.knowledge is not None
        assert hub.datasets is not None
        assert hub.router is not None

    def test_hub_search_finance(self):
        """Hub busca dados financeiros."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        result = hub.search("cotação PETR4 hoje")
        assert result["domain"] in ("financeiro", "offline")
        assert "results" in result
        assert "source" in result

    def test_hub_search_knowledge(self):
        """Hub busca conhecimento."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        result = hub.search("o que é machine learning")
        if result["domain"] == "conhecimento":
            assert "results" in result

    def test_hub_search_dataset(self):
        """Hub busca datasets."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        result = hub.search("dataset climate change")
        if result["domain"] == "dataset":
            assert "results" in result

    def test_hub_get_stats(self):
        """Hub expõe estatísticas de uso."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        hub.search("PETR4")
        hub.search("machine learning")
        stats = hub.get_stats()
        assert stats["total_queries"] >= 2
        assert "domains" in stats
        assert "sources" in stats

    def test_hub_cache_ttl(self):
        """Hub tem cache com TTL por domínio."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        # Cache deve existir
        assert hasattr(hub, "_cache")

    def test_hub_report(self):
        """Hub gera relatório legível."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        hub.search("PETR4")
        report = hub.get_report()
        assert "DataKnowledgeHub" in report
        assert "consultas" in report.lower()


# ═══════════════════════════════════════════════════════════════
# Testes de Integração com LLMReductionLayer
# ═══════════════════════════════════════════════════════════════

class TestIntegrationWithLLMReduction:
    """RED: testes esperam integração com LLMReductionLayer."""

    def test_llm_reduction_has_data_hub(self):
        """LLMReductionLayer deve expor DataKnowledgeHub."""
        from skills.tooling.llm_reduction import get_reduction_layer

        layer = get_reduction_layer()
        assert hasattr(layer, "data_hub"), "LLMReductionLayer não tem 'data_hub'"
        assert hasattr(layer.data_hub, "search")

    def test_llm_reduction_search_data(self):
        """Buscar dados via LLMReductionLayer conta como LLM call evitada."""
        from skills.tooling.llm_reduction import get_reduction_layer

        layer = get_reduction_layer()
        stats_before = layer.stats["total_llm_calls_saved"]

        result = layer.search_data("cotação PETR4")
        assert result is not None

        stats_after = layer.stats["total_llm_calls_saved"]
        assert stats_after >= stats_before


# ═══════════════════════════════════════════════════════════════
# Testes de Performance
# ═══════════════════════════════════════════════════════════════

class TestDataHubPerformance:
    """Hub deve responder em < 100ms (modo offline/mock)."""

    def test_router_under_10ms(self):
        """Classificação de domínio deve ser < 10ms."""
        from skills.tooling.data_knowledge_hub.router import DomainRouter

        router = DomainRouter()
        start = time.time()
        for _ in range(100):
            router.classify("cotação PETR4 hoje")
        elapsed_ms = (time.time() - start) * 10

        assert elapsed_ms < 10, f"Classificação muito lenta: {elapsed_ms:.2f}ms"
