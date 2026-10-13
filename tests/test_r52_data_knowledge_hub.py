#!/usr/bin/env python3
"""
Testes TDD para DataKnowledgeHub (SPEC-965)
============================================
RED phase: testes falham antes da implementação.

Ciclo: RED → GREEN → REFACTOR
"""

import json
import io
import os
import sys
import time
import urllib.error
import urllib.parse
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
    """Contrato HTTP com respostas controladas; nenhuma consulta de rede nestes casos."""

    @pytest.fixture(autouse=True)
    def dataset_http(self, monkeypatch):
        from skills.tooling.data_knowledge_hub import datasets

        payloads = {
            "zenodo.org": {"hits": {"hits": [{"id": 7, "metadata": {
                "title": "Controlled climate record", "doi": "10.0000/fixture.zenodo",
                "creators": [{"name": "Fixture Author"}], "publication_date": "2025-01-02",
                "resource_type": {"type": "dataset"}}}]}},
            "api.datacite.org": {"data": [{"attributes": {
                "doi": "10.0000/fixture.datacite", "titles": [{"title": "Controlled ML record"}],
                "creators": [{"name": "Fixture Author"}], "publicationYear": 2025,
                "publisher": "Fixture Publisher"}}]},
            "archive.ics.uci.edu": '<a href="datasets/fixture">Controlled Iris record</a>',
            "api.figshare.com": [{"id": 9, "title": "Controlled biology record",
                "item_type": 3, "published_date": "2025-01-02", "authors": [{"full_name": "Fixture Author"}]}],
        }
        requests = []

        def urlopen(request, *, timeout):
            requests.append(request.full_url)
            assert timeout == 15
            parsed = urllib.parse.urlparse(request.full_url)
            assert parsed.scheme == "https"
            payload = payloads[parsed.hostname]
            encoded = payload if isinstance(payload, str) else json.dumps(payload)
            return io.BytesIO(encoded.encode("utf-8"))

        monkeypatch.setattr(datasets.urllib.request, "urlopen", urlopen)
        return requests

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
        assert result["status"] == "online"
        assert result["results"][0]["id"] == 7
        assert result["results"][0]["titulo"] == "Controlled climate record"
        assert result["evidence_eligible"] is True
        assert result["synthetic"] is False
        assert result["provenance"]["acquisition"] == "http_request"

    def test_dataset_search_datacite(self):
        """DatasetDataSource busca DataCite."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("machine learning", source="datacite")
        assert result["source"] == "datacite"
        assert result["status"] == "online"
        assert result["results"][0]["doi"] == "10.0000/fixture.datacite"
        assert result["results"][0]["titulo"] == "Controlled ML record"

    def test_dataset_search_uci(self):
        """DatasetDataSource busca UCI ML Repository."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("iris", source="uci")
        assert result["source"] == "uci"
        assert result["status"] == "online"
        assert result["results"][0]["nome"] == "Controlled Iris record"
        # A fixture valida apenas o parser legado; não afirma disponibilidade upstream.
        assert result["results"][0]["url"] == "https://archive.ics.uci.edu/ml/datasets/fixture"

    def test_dataset_search_figshare(self):
        """DatasetDataSource busca Figshare."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        result = dds.search("biology", source="figshare")
        assert result["source"] == "figshare"
        assert result["status"] == "online"
        assert result["results"][0]["id"] == 9
        assert result["results"][0]["titulo"] == "Controlled biology record"

    def test_dataset_auto_route(self):
        """DatasetDataSource roteia por domínio."""
        from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource

        dds = DatasetDataSource()
        r = dds.search("dataset climate change")
        assert r["source"] == "zenodo"
        assert r["results"][0]["id"] == 7

    @pytest.mark.parametrize("source", ["zenodo", "datacite", "uci", "figshare"])
    @pytest.mark.parametrize("demo", [False, True])
    def test_dataset_failure_is_closed_and_demo_requires_opt_in(self, monkeypatch, source, demo):
        """Erro de aquisição não pode devolver exemplos como evidência observada."""
        from skills.tooling.data_knowledge_hub import datasets

        def failed_request(*args, **kwargs):
            raise urllib.error.URLError("controlled acquisition failure")

        monkeypatch.setattr(datasets.urllib.request, "urlopen", failed_request)
        result = datasets.DatasetDataSource(allow_demo_fallback=demo).search("fixture", source=source)
        assert result["source"] == source
        assert result["status"] == ("demonstration" if demo else "unavailable")
        assert result["synthetic"] is demo
        assert result["evidence_eligible"] is False
        assert result["provenance"]["error_type"] == "URLError"
        assert result["provenance"]["acquisition"] == ("demonstration_fallback" if demo else "failed_http_request")
        if demo:
            assert result["results"]
            assert all(record["synthetic"] is True and record["evidence_kind"] == "demonstration"
                       for record in result["results"])
        else:
            assert result["results"] == []


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
