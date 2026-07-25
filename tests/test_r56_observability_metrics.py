#!/usr/bin/env python3
"""
Testes TDD para SPEC-969: Observabilidade — Métricas e Endpoints de Saúde
==========================================================================
RED phase: testes falham antes da implementação completa.
"""

import json
import os
import sys
from unittest.mock import MagicMock, PropertyMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestMetricsCollector:
    """CA1–CA3: Coleta de métricas dos componentes."""

    def test_ca1_collects_llm_reduction_stats(self):
        """CA1: MetricsCollector coleta stats de LLMReductionLayer."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        mock_layer = MagicMock()
        mock_layer.stats = {
            "total_llm_calls_saved": 42,
            "route_calls": 30,
            "search_calls": 10,
            "classify_calls": 2,
            "gametheory_calls": 0,
            "template_calls": 5,
            "data_queries": 0,
        }

        collector.collect_from_layer(mock_layer)
        snap = collector._snapshots.get("llm_reduction")
        assert snap is not None
        assert snap.data["total_llm_calls_saved"] == 42
        assert snap.data["route_calls"] == 30

    def test_ca2_collects_data_knowledge_hub_stats(self):
        """CA2: MetricsCollector coleta stats de DataKnowledgeHub."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        mock_hub = MagicMock()
        mock_hub.get_stats.return_value = {
            "total_queries": 100,
            "cache_hits": 60,
            "cache_misses": 40,
            "cache_hit_rate": 60.0,
            "online": 80,
            "online_rate": 80.0,
        }

        collector.collect_from_hub(mock_hub)
        snap = collector._snapshots.get("data_knowledge_hub")
        assert snap is not None
        assert snap.data["total_queries"] == 100
        assert snap.data["cache_hit_rate"] == 60.0

    def test_ca3_collects_orchestrator_stats(self):
        """CA3: MetricsCollector coleta stats do Orquestrador."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        mock_orch = MagicMock()
        mock_orch.id = "marceloclaro"
        mock_orch._llm_calls_saved = 15
        mock_orch.get_reduction_stats.return_value = {
            "total_llm_calls_saved": 15,
            "route_calls": 10,
            "search_calls": 3,
            "classify_calls": 2,
            "_llm_calls_saved": 15,
        }

        collector.collect_from_orchestrator(mock_orch)
        snap = collector._snapshots.get("orchestrator")
        assert snap is not None
        assert snap.data["llm_calls_saved"] == 15
        assert snap.data["reduction"]["total_llm_calls_saved"] == 15

    def test_collects_multiple_components(self):
        """Pode coletar de múltiplos componentes."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.collect_from_layer(MagicMock(stats={}))
        collector.collect_from_hub(MagicMock())
        collector.collect_from_orchestrator(MagicMock(
            id="test", _llm_calls_saved=0,
            get_reduction_stats=lambda: {},
        ))
        assert len(collector._snapshots) == 3


class TestMetricsRender:
    """CA4–CA5: Renderização de métricas."""

    def test_ca4_render_returns_string(self):
        """CA4: render() retorna string formatada."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.collect_from_layer(MagicMock(stats={"total_llm_calls_saved": 5}))
        output = collector.render()
        assert isinstance(output, str)
        assert "MÉTRICAS DO ECOSSISTEMA" in output

    def test_ca4_render_empty(self):
        """render() sem dados retorna mensagem."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        output = collector.render()
        assert "Nenhuma métrica" in output

    def test_ca5_to_dict_returns_dict(self):
        """CA5: to_dict() retorna dict aninhado."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.collect_from_layer(MagicMock(stats={"total_llm_calls_saved": 5}))
        d = collector.to_dict()
        assert isinstance(d, dict)
        assert "llm_reduction" in d
        assert d["llm_reduction"]["data"]["total_llm_calls_saved"] == 5

    def test_to_dict_structure(self):
        """to_dict() tem estrutura esperada."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.collect_from_layer(MagicMock(stats={"a": 1}))
        d = collector.to_dict()
        snap = d["llm_reduction"]
        assert "component" in snap
        assert "timestamp" in snap
        assert "data" in snap
        assert snap["component"] == "llm_reduction"


class TestMetricsHealth:
    """CA6: Endpoint de saúde."""

    def test_render_health_returns_dict(self):
        """render_health() retorna dict com status."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        health = collector.render_health()
        assert isinstance(health, dict)
        assert "status" in health
        assert "components" in health

    def test_render_health_healthy(self):
        """render_health() sem erros = healthy."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.collect_from_layer(MagicMock(stats={"a": 1}))
        health = collector.render_health()
        assert health["status"] == "healthy"


class TestMetricsHTTPServer:
    """Servidor HTTP leve."""

    def test_server_handles_health(self):
        """Servidor responde /health com JSON."""
        from marceloclaro.metrics import MetricsCollector, MetricsHTTPServer

        collector = MetricsCollector()
        server = MetricsHTTPServer(collector)

        response = server._handle_request("GET /health HTTP/1.1")
        assert isinstance(response, bytes)
        body = json.loads(response.decode("utf-8").split("\r\n\r\n")[1])
        assert "status" in body

    def test_server_handles_metrics(self):
        """Servidor responde /metrics com JSON."""
        from marceloclaro.metrics import MetricsCollector, MetricsHTTPServer

        collector = MetricsCollector()
        collector.collect_from_layer(MagicMock(stats={"test": 1}))
        server = MetricsHTTPServer(collector)

        response = server._handle_request("GET /metrics HTTP/1.1")
        assert isinstance(response, bytes)
        body = json.loads(response.decode("utf-8").split("\r\n\r\n")[1])
        assert "llm_reduction" in body

    def test_server_404(self):
        """Rota desconhecida retorna 404."""
        from marceloclaro.metrics import MetricsCollector, MetricsHTTPServer

        collector = MetricsCollector()
        server = MetricsHTTPServer(collector)

        response = server._handle_request("GET /unknown HTTP/1.1")
        assert b"404" in response

    def test_server_root(self):
        """Rota / retorna texto."""
        from marceloclaro.metrics import MetricsCollector, MetricsHTTPServer

        collector = MetricsCollector()
        server = MetricsHTTPServer(collector)

        response = server._handle_request("GET / HTTP/1.1")
        assert isinstance(response, bytes)
        body = response.decode("utf-8").split("\r\n\r\n")[1]
        assert len(body) > 0

    def test_server_start_stop(self):
        """Servidor inicia e para sem erros."""
        from marceloclaro.metrics import MetricsCollector, MetricsHTTPServer

        collector = MetricsCollector()
        server = MetricsHTTPServer(collector, port=9099)
        server.start(daemon=True)
        assert server._server is not None
        server.stop()
        # Servidor foi parado com sucesso (não lançou exceção)


class TestMetricsToJSON:
    """Serialização JSON."""

    def test_to_json(self):
        """to_json() retorna string JSON."""
        from marceloclaro.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.collect_from_layer(MagicMock(stats={"total_llm_calls_saved": 3}))
        j = collector.to_json()
        parsed = json.loads(j)
        assert "llm_reduction" in parsed


class TestIntegration:
    """Testes de integração com componentes reais."""

    def test_collect_from_real_orchestrator(self):
        """Coleta de orquestrador real."""
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from marceloclaro.metrics import MetricsCollector

        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        collector = MetricsCollector()
        collector.collect_from_orchestrator(orch)

        snap = collector._snapshots.get("orchestrator")
        assert snap is not None
        assert snap.data["orchestrator_id"] == "marceloclaro"
        assert "reduction" in snap.data

    def test_collect_from_real_data_hub(self):
        """Coleta de DataKnowledgeHub real."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub
        from marceloclaro.metrics import MetricsCollector

        hub = DataKnowledgeHub()
        collector = MetricsCollector()
        collector.collect_from_hub(hub)

        snap = collector._snapshots.get("data_knowledge_hub")
        assert snap is not None
        assert "total_queries" in snap.data

    def test_collect_from_real_layer(self):
        """Coleta de LLMReductionLayer real."""
        from skills.tooling.llm_reduction import LLMReductionLayer
        from marceloclaro.metrics import MetricsCollector

        layer = LLMReductionLayer()
        collector = MetricsCollector()
        collector.collect_from_layer(layer)

        snap = collector._snapshots.get("llm_reduction")
        assert snap is not None
        assert "total_llm_calls_saved" in snap.data

    def test_integration_with_doctor(self):
        """Doctor inclui métricas de forma não destrutiva."""
        from marceloclaro.doctor import run_doctor

        report = run_doctor()
        assert isinstance(report, dict)
        # Doctor ainda funciona, e não quebra com métricas
        assert "overall" in report
