#!/usr/bin/env python3
"""
DataSource — Classe Base Abstrata para Fontes de Dados
========================================================
Define a interface que todas as fontes de dados devem implementar.

Uso:
    from skills.tooling.data_knowledge_hub.base import DataSource

    class MeuDataSource(DataSource):
        name = "meu_data_source"

        def search(self, query, **kwargs):
            ...
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class DataSource(ABC):
    """
    Classe base abstrata para todas as fontes de dados.

    Atributos:
        name (str): Nome único da fonte (ex: "yfinance", "ibge", "wikipedia")
    """

    name: str = ""

    def __init__(self):
        self._stats = {
            "total_queries": 0,
            "total_elapsed_ms": 0.0,
            "successful": 0,
            "failed": 0,
            "offline": 0,
        }

    @abstractmethod
    def search(
        self, query: str, source: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Busca dados na fonte.

        Args:
            query: termo de busca
            source: fonte específica (opcional — se None, usa roteamento automático)
            **kwargs: argumentos adicionais específicos da fonte

        Returns:
            Dict com resultados padronizados:
                - query: termo buscado
                - source: fonte usada
                - status: "online" | "offline"
                - results: lista de resultados
                - timestamp: ISO datetime
                - elapsed_ms: tempo de resposta
        """
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso da fonte."""
        total = self._stats["total_queries"]
        return {
            **self._stats,
            "name": self.name,
            "avg_ms": round(
                self._stats["total_elapsed_ms"] / total, 2
            ) if total > 0 else 0.0,
        }

    def _record_query(
        self, elapsed_ms: float, success: bool, offline: bool = False
    ):
        """Registra estatísticas de uma consulta."""
        self._stats["total_queries"] += 1
        self._stats["total_elapsed_ms"] += elapsed_ms
        if success:
            self._stats["successful"] += 1
        else:
            self._stats["failed"] += 1
        if offline:
            self._stats["offline"] += 1

    def _make_result(
        self,
        query: str,
        source: str,
        results: List[Dict[str, Any]],
        status: str = "online",
        elapsed_ms: float = 0.0,
    ) -> Dict[str, Any]:
        """Cria dict de resultado padronizado."""
        return {
            "query": query,
            "source": source,
            "status": status,
            "results": results,
            "count": len(results),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_ms": round(elapsed_ms, 2),
        }
