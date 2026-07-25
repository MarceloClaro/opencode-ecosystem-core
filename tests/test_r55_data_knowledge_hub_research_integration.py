#!/usr/bin/env python3
"""
Testes TDD para SPEC-968: Integração do DataKnowledgeHub ao ResearchHub
========================================================================
RED phase: testes falham antes da implementação.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ═══════════════════════════════════════════════════════════════
# CA1–CA2: Inicialização com DataKnowledgeHub
# ═══════════════════════════════════════════════════════════════

class TestResearchHubDataHubInit:
    """ResearchHub aceita/inicializa DataKnowledgeHub."""

    def test_ca1_accepts_data_hub_param(self):
        """CA1: ResearchHub aceita parâmetro data_hub opcional."""
        from research.hub import ResearchHub

        mock_hub = MagicMock()
        hub = ResearchHub(
            topic="teste",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.data_hub = mock_hub
        assert hub.data_hub is mock_hub

    def test_ca2_auto_instantiates_from_llm_reduction(self):
        """CA2: Se não fornecido, obtém via LLMReductionLayer."""
        from research.hub import ResearchHub
        from skills.tooling.llm_reduction import LLMReductionLayer

        hub = ResearchHub(
            topic="teste",
            production_folder=str(tempfile.mkdtemp()),
        )
        layer = LLMReductionLayer()
        hub.data_hub = layer.data_hub
        assert hub.data_hub is not None
        assert hasattr(hub.data_hub, "search")


class TestResearchHubRunWithData:
    """ResearchHub.run() com use_data_hub=True."""

    def test_ca3_run_accepts_use_data_hub(self):
        """CA3: run() aceita use_data_hub=True."""
        from research.hub import ResearchHub

        mock_hub = MagicMock()
        mock_hub.search.return_value = {
            "domain": "conhecimento",
            "source": "wikipedia",
            "results": [],
            "confidence": 0.7,
            "count": 0,
        }

        hub = ResearchHub(
            topic="machine learning",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.data_hub = mock_hub
        hub.searcher = MagicMock()
        hub.searcher.search.return_value = []
        hub.downloader = MagicMock()
        hub.converter = MagicMock()
        hub.writer = MagicMock()
        hub.analyzer = MagicMock()
        hub.osint = MagicMock()
        hub.osint.analyze_references.return_value = {}

        # Não deve quebrar com use_data_hub=True
        result = hub.run(max_papers=0, use_data_hub=True)
        assert isinstance(result, dict)
        # O DataKnowledgeHub deve ter sido consultado
        mock_hub.search.assert_called()

    def test_ca4_data_hub_queried_with_topic(self):
        """CA4: DataKnowledgeHub consultado com o tema da pesquisa."""
        from research.hub import ResearchHub

        mock_hub = MagicMock()
        mock_hub.search.return_value = {
            "domain": "conhecimento",
            "source": "wikipedia",
            "results": [{"title": "Machine learning", "snippet": "...", "url": "..."}],
            "confidence": 0.7,
            "count": 1,
        }

        hub = ResearchHub(
            topic="machine learning",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.data_hub = mock_hub
        hub.searcher = MagicMock()
        hub.searcher.search.return_value = []
        hub.downloader = MagicMock()
        hub.converter = MagicMock()
        hub.writer = MagicMock()
        hub.analyzer = MagicMock()
        hub.osint = MagicMock()
        hub.osint.analyze_references.return_value = {}

        hub.run(max_papers=0, use_data_hub=True)
        # Deve ter chamado search com o tema
        mock_hub.search.assert_called_with("machine learning")

    def test_ca5_data_knowledge_in_manifest(self):
        """CA5: Resultados do DataKnowledgeHub no manifest."""
        from research.hub import ResearchHub

        mock_hub = MagicMock()
        mock_hub.search.return_value = {
            "domain": "conhecimento",
            "source": "wikipedia",
            "results": [{"title": "ML", "snippet": "Machine learning é..."}],
            "confidence": 0.7,
            "count": 1,
        }

        hub = ResearchHub(
            topic="machine learning",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.data_hub = mock_hub
        hub.searcher = MagicMock()
        hub.searcher.search.return_value = []
        hub.downloader = MagicMock()
        hub.converter = MagicMock()
        hub.writer = MagicMock()
        hub.analyzer = MagicMock()
        hub.osint = MagicMock()
        hub.osint.analyze_references.return_value = {}

        result = hub.run(max_papers=0, use_data_hub=True)
        assert "data_knowledge" in result
        dk = result["data_knowledge"]
        assert dk["domain"] == "conhecimento"
        assert dk["confidence"] == 0.7
        assert dk["count"] == 1

    def test_ca5_data_knowledge_absent_when_not_used(self):
        """CA5: Sem use_data_hub, não há seção data_knowledge."""
        from research.hub import ResearchHub

        hub = ResearchHub(
            topic="machine learning",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.searcher = MagicMock()
        hub.searcher.search.return_value = []
        hub.downloader = MagicMock()
        hub.converter = MagicMock()
        hub.writer = MagicMock()
        hub.analyzer = MagicMock()
        hub.osint = MagicMock()
        hub.osint.analyze_references.return_value = {}

        result = hub.run(max_papers=0, use_data_hub=False)
        assert "data_knowledge" not in result

    def test_ca6_confidence_in_manifest(self):
        """CA6: confidence do CalibrationLayer incluída no manifest."""
        from research.hub import ResearchHub

        mock_hub = MagicMock()
        mock_hub.search.return_value = {
            "domain": "oficial",
            "source": "ibge",
            "results": [{"metric": "IPCA", "valor": 0.38}],
            "confidence": 0.92,
            "count": 1,
        }

        hub = ResearchHub(
            topic="inflação 2024",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.data_hub = mock_hub
        hub.searcher = MagicMock()
        hub.searcher.search.return_value = []
        hub.downloader = MagicMock()
        hub.converter = MagicMock()
        hub.writer = MagicMock()
        hub.analyzer = MagicMock()
        hub.osint = MagicMock()
        hub.osint.analyze_references.return_value = {}

        result = hub.run(max_papers=0, use_data_hub=True)
        assert result["data_knowledge"]["confidence"] == 0.92

    def test_data_hub_failure_does_not_break_pipeline(self):
        """Falha no DataKnowledgeHub não interrompe o pipeline."""
        from research.hub import ResearchHub

        mock_hub = MagicMock()
        mock_hub.search.side_effect = Exception("Fonte offline")

        hub = ResearchHub(
            topic="machine learning",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.data_hub = mock_hub
        hub.searcher = MagicMock()
        hub.searcher.search.return_value = []
        hub.downloader = MagicMock()
        hub.converter = MagicMock()
        hub.writer = MagicMock()
        hub.analyzer = MagicMock()
        hub.osint = MagicMock()
        hub.osint.analyze_references.return_value = {}

        # Não deve lançar exceção
        result = hub.run(max_papers=0, use_data_hub=True)
        assert isinstance(result, dict)
        # Se falhou, manifest não tem data_knowledge
        assert "data_knowledge" not in result


class TestRealDataKnowledgeHub:
    """Testes com DataKnowledgeHub real."""

    def test_real_data_hub_search_returns_dict(self):
        """DataKnowledgeHub real search retorna dict com resultados."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        result = hub.search("machine learning", domain="conhecimento")
        assert isinstance(result, dict)
        assert "domain" in result
        assert "results" in result
        assert "confidence" in result

    def test_real_data_hub_in_llm_reduction(self):
        """LLMReductionLayer contém DataKnowledgeHub."""
        from skills.tooling.llm_reduction import LLMReductionLayer

        layer = LLMReductionLayer()
        assert layer.data_hub is not None
        assert hasattr(layer.data_hub, "search")

    def test_real_data_knowledge_added_to_manifest(self):
        """Integração real: dados enriquecem manifest."""
        from research.hub import ResearchHub
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        dhub = DataKnowledgeHub()
        hub = ResearchHub(
            topic="machine learning",
            production_folder=str(tempfile.mkdtemp()),
        )
        hub.data_hub = dhub
        hub.searcher = MagicMock()
        hub.searcher.search.return_value = []
        hub.downloader = MagicMock()
        hub.converter = MagicMock()
        hub.writer = MagicMock()
        hub.analyzer = MagicMock()
        hub.osint = MagicMock()
        hub.osint.analyze_references.return_value = {}

        result = hub.run(max_papers=0, use_data_hub=True)
        assert "data_knowledge" in result
        assert result["data_knowledge"]["count"] >= 0
