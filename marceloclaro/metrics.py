# -*- coding: utf-8 -*-
"""
MetricsCollector — Observabilidade do Ecossistema (SPEC-969)
=============================================================
Coleta e expõe métricas de todos os componentes do ecossistema
em formato amigável para terminal e para API HTTP.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional

logger = logging.getLogger("marceloclaro.metrics")


@dataclass
class MetricsSnapshot:
    """Snapshot de métricas de um componente."""

    component: str
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"component": self.component, "timestamp": self.timestamp, "data": dict(self.data)}


class MetricsCollector:
    """Coletor central de métricas do ecossistema.

    Agrega dados da LLMReductionLayer, DataKnowledgeHub,
    Orquestrador e outros componentes.
    """

    def __init__(self):
        self._snapshots: Dict[str, MetricsSnapshot] = {}

    def collect_from_orchestrator(self, orch) -> None:
        """Coleta métricas do orquestrador."""
        data: Dict[str, Any] = {"orchestrator_id": orch.id}

        # LLM Reduction stats
        try:
            reduction_stats = orch.get_reduction_stats()
            data["reduction"] = reduction_stats
            data["llm_calls_saved"] = getattr(orch, "_llm_calls_saved", 0)
        except Exception as exc:
            data["reduction"] = {"error": str(exc)}

        # Trust Engine (resumo)
        try:
            trust = orch.trust
            if hasattr(trust, "get_confidence"):
                data["trust_tier"] = trust.get_confidence("marceloclaro")
            if hasattr(trust, "get_stats"):
                data["trust_stats"] = trust.get_stats()
        except Exception:
            pass

        # Token Economy (resumo)
        try:
            economy = getattr(orch, "economy", None)
            if economy and hasattr(economy, "get_balance"):
                data["economy_balance"] = economy.get_balance("marceloclaro")
        except Exception:
            pass

        self._snapshots["orchestrator"] = MetricsSnapshot(
            component="orchestrator", data=data
        )

    def collect_from_hub(self, hub) -> None:
        """Coleta métricas do DataKnowledgeHub."""
        data: Dict[str, Any] = {}
        try:
            if hasattr(hub, "get_stats"):
                data = hub.get_stats()
            elif hasattr(hub, "_stats"):
                data = dict(hub._stats)
        except Exception as exc:
            data = {"error": str(exc)}

        self._snapshots["data_knowledge_hub"] = MetricsSnapshot(
            component="data_knowledge_hub", data=data
        )

    def collect_from_layer(self, layer) -> None:
        """Coleta métricas da LLMReductionLayer."""
        data: Dict[str, Any] = {}
        try:
            if hasattr(layer, "stats"):
                data = dict(layer.stats)
            if hasattr(layer, "get_stats"):
                extra = layer.get_stats()
                if isinstance(extra, dict):
                    data.update(extra)
            if hasattr(layer, "search") and hasattr(layer, "whoosh"):
                data["whoosh_available"] = True
        except Exception as exc:
            data = {"error": str(exc)}

        self._snapshots["llm_reduction"] = MetricsSnapshot(
            component="llm_reduction", data=data
        )

    def to_dict(self) -> Dict[str, Any]:
        """Retorna todas as métricas como dict aninhado."""
        return {
            name: snap.to_dict() for name, snap in self._snapshots.items()
        }

    def render(self) -> str:
        """Renderiza métricas em formato legível para terminal."""
        if not self._snapshots:
            return "Nenhuma métrica coletada ainda."

        lines = [
            "=" * 60,
            "  MÉTRICAS DO ECOSSISTEMA — OpenCode Core",
            "=" * 60,
            "",
        ]

        for name, snap in sorted(self._snapshots.items()):
            lines.append(f"[{name}]")
            lines.append(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snap.timestamp))}")

            # Extrair dados principais
            data = snap.data

            # LLM Reduction específico
            if "llm_calls_saved" in data:
                lines.append(f"  LLM calls saved: {data['llm_calls_saved']}")
            if "reduction" in data and isinstance(data["reduction"], dict):
                r = data["reduction"]
                lines.append(f"  Total LLM calls saved: {r.get('total_llm_calls_saved', '?')}")
                lines.append(f"  Route calls: {r.get('route_calls', '?')}")
                lines.append(f"  Search calls: {r.get('search_calls', '?')}")
                lines.append(f"  Classify calls: {r.get('classify_calls', '?')}")
                lines.append(f"  Template calls: {r.get('template_calls', '?')}")

            # DataKnowledgeHub específico
            if "total_queries" in data:
                lines.append(f"  Total queries: {data['total_queries']}")
                lines.append(f"  Cache hit rate: {data.get('cache_hit_rate', 0)}%")
                lines.append(f"  Online rate: {data.get('online_rate', 0)}%")

            # Trust stats
            if "trust_tier" in data:
                lines.append(f"  Trust tier: {data['trust_tier']}")
            if "economy_balance" in data:
                lines.append(f"  Economy balance: {data['economy_balance']}")

            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def render_health(self) -> Dict[str, Any]:
        """Retorna status de saúde simplificado."""
        status = "healthy"
        details = []

        for name, snap in self._snapshots.items():
            data = snap.data
            if "error" in data:
                status = "degraded"
                details.append(f"{name}: error — {data['error']}")

        return {
            "status": status,
            "timestamp": time.time(),
            "components": len(self._snapshots),
            "details": details,
        }

    def to_json(self, indent: int = 2) -> str:
        """Retorna métricas como JSON formatado."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ─── Servidor HTTP Leve (SPEC-969) ────────────────────────────

class MetricsHTTPServer:
    """Servidor HTTP leve para /health e /metrics.

    Usa socket nativo (sem dependência externa).
    Inicia em modo daemon, escuta em porta configurável.
    """

    def __init__(self, collector: MetricsCollector, host: str = "127.0.0.1",
                 port: int = 9090):
        self.collector = collector
        self.host = host
        self.port = port
        self._server = None

    def _handle_request(self, request_line: str) -> bytes:
        """Processa request HTTP e retorna resposta."""
        method, path, _ = request_line.split(" ", 2) if " " in request_line else ("GET", "/", "")

        if path == "/health":
            health = self.collector.render_health()
            body = json.dumps(health, indent=2, ensure_ascii=False)
            status = "200 OK"
            ctype = "application/json"
        elif path == "/metrics":
            body = self.collector.to_json()
            status = "200 OK"
            ctype = "application/json"
        elif path == "/":
            body = self.collector.render()
            status = "200 OK"
            ctype = "text/plain; charset=utf-8"
        else:
            body = json.dumps({"error": "not_found"})
            status = "404 Not Found"
            ctype = "application/json"

        response = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: {ctype}\r\n"
            f"Content-Length: {len(body.encode('utf-8'))}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{body}"
        )
        return response.encode("utf-8")

    def start(self, daemon: bool = True) -> None:
        """Inicia servidor HTTP em thread separada."""
        import socketserver
        import threading

        class Handler(socketserver.BaseRequestHandler):
            def handle(inner_self):
                try:
                    data = inner_self.request.recv(4096).decode("utf-8", errors="replace")
                    request_line = data.split("\r\n")[0] if data else "GET / HTTP/1.1"
                    response = self._handle_request(request_line)
                    inner_self.request.sendall(response)
                except Exception:
                    pass
                finally:
                    inner_self.request.close()

        self._server = socketserver.TCPServer((self.host, self.port), Handler)
        thread = threading.Thread(target=self._server.serve_forever, daemon=daemon)
        thread.start()
        logger.info(
            "Metrics HTTP server listening on http://%s:%d",
            self.host, self.port,
        )

    def stop(self) -> None:
        """Para o servidor HTTP."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            logger.info("Metrics HTTP server stopped.")


# Singleton
_default_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    global _default_collector
    if _default_collector is None:
        _default_collector = MetricsCollector()
    return _default_collector
