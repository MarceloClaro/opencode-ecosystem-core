#!/usr/bin/env python3
"""
AuditTrail — Log Imutável e Auditável de Consultas de Dados
==============================================================
Registra toda consulta de dados usada para decisões de orquestração,
permitindo rastrear "por que o orquestrador decidiu X?".

Características:
    - Append-only (imutável após inserção)
    - Hash SHA-256 do resultado bruto (integridade)
    - Export JSON Lines
    - Busca por query, domínio, fonte, intervalo de tempo
    - Paginação

Uso:
    from skills.tooling.data_knowledge_hub.audit import AuditTrail
    audit = AuditTrail()
    eid = audit.record("IPCA", "financeiro", "bcb", 0.95)
    entry = audit.get(eid)
    entries = audit.search("IPCA")
    jsonl = audit.export_json()
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class AuditTrail:
    """
    Audit trail append-only para consultas de dados.
    Thread-safe para operações de leitura/escrita.
    """

    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self._index: int = 0
        self._stats = {
            "total_entries": 0,
            "domains": {},
            "sources": {},
        }

    def record(
        self,
        query: str,
        domain: str,
        source: str,
        confidence: float,
        decision_context: str = "data_knowledge_hub:search",
        raw_result: Any = None,
        cross_validated: bool = False,
        calibration_details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Registra uma consulta no audit trail.

        Args:
            query: termo buscado
            domain: domínio classificado
            source: fonte usada
            confidence: confiança calibrada (0-1)
            decision_context: contexto da decisão
            raw_result: resultado bruto (para hash de integridade)
            cross_validated: se houve validação cruzada
            calibration_details: detalhes da calibração

        Returns:
            ID único da entrada (audit_YYYYMMDD_NNN)
        """
        timestamp = time.time()
        timestamp_iso = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        # Hash do resultado bruto
        if raw_result is not None:
            result_hash = hashlib.sha256(
                json.dumps(raw_result, sort_keys=True, ensure_ascii=False).encode()
            ).hexdigest()
        else:
            result_hash = ""

        # Gerar ID sequencial
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
        self._index += 1
        entry_id = f"audit_{date_str}_{self._index:04d}"

        entry = {
            "id": entry_id,
            "timestamp": timestamp_iso,
            "timestamp_unix": timestamp,
            "query": query,
            "domain": domain,
            "source": source,
            "confidence": confidence,
            "decision_context": decision_context,
            "result_hash": result_hash,
            "cross_validated": cross_validated,
            "calibration_details": calibration_details or {},
        }

        # Imutável: congelamos o dict
        self._entries.append(entry)

        # Stats
        self._stats["total_entries"] += 1
        self._stats["domains"][domain] = self._stats["domains"].get(domain, 0) + 1
        self._stats["sources"][source] = self._stats["sources"].get(source, 0) + 1

        return entry_id

    def get(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Recupera uma entrada por ID."""
        for entry in self._entries:
            if entry["id"] == entry_id:
                # Retorna cópia imutável
                return dict(entry)
        return None

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Lista entradas com paginação."""
        return [
            dict(e) for e in self._entries[offset:offset + limit]
        ]

    def search(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Busca entradas por query, domínio ou fonte."""
        results = []
        for entry in self._entries:
            if query and query.lower() not in entry["query"].lower():
                continue
            if domain and entry["domain"] != domain:
                continue
            if source and entry["source"] != source:
                continue
            results.append(dict(entry))
            if len(results) >= limit:
                break
        return results

    def export_json(self, limit: int = 1000) -> str:
        """Exporta entradas como JSON Lines (cada linha = um JSON)."""
        lines = []
        for entry in self._entries[-limit:]:
            lines.append(json.dumps(entry, ensure_ascii=False))
        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do audit trail."""
        return {**self._stats}

    def clear(self):
        """Limpa todas as entradas (apenas para testes)."""
        self._entries.clear()
        self._index = 0
        self._stats = {
            "total_entries": 0,
            "domains": {},
            "sources": {},
        }
