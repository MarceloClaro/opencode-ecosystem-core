# -*- coding: utf-8 -*-
"""
Scanners MCP Server — Servidor MCP para o SuperRigorPipeline e Scanners
========================================================================
Expõe as ferramentas dos 8 scanners e auditoria do ecossistema via MCP.
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from scanners.pipeline import super_rigor_pipeline
from scanners.scientific_reasoning_scanner import scientific_reasoning_scanner
from benchmarks.merkle_integrity_guard import merkle_integrity_guard

logger = logging.getLogger("scanners-mcp")


class ScannersMcpServer:
    """Servidor MCP para auditoria de rigor científico e scanners do ecossistema."""

    def get_tools(self) -> Dict[str, Any]:
        """Retorna as ferramentas de auditoria disponíveis via MCP."""
        return {
            "super_rigor_audit": {
                "description": "Executa auditoria completa através dos 8 scanners do ecossistema e calcula o Score de Excelência (EXS)",
                "parameters": {"text": "Texto a ser auditado"},
            },
            "scientific_reasoning_scan": {
                "description": "Avalia o Índice de Rigor Científico (SRI 0-100) e detecta falácias epistemológicas no texto",
                "parameters": {"text": "Texto científico a ser analisado"},
            },
            "merkle_integrity_check": {
                "description": "Verifica a integridade criptográfica SHA-256 do código-fonte através da Árvore de Merkle",
                "parameters": {},
            },
        }

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a ferramenta MCP solicitada."""
        if name == "super_rigor_audit":
            text = args.get("text", "")
            return {"ok": True, "result": super_rigor_pipeline.audit_production(text)}
        elif name == "scientific_reasoning_scan":
            text = args.get("text", "")
            return {"ok": True, "result": scientific_reasoning_scanner.scan_text(text)}
        elif name == "merkle_integrity_check":
            return {"ok": True, "result": merkle_integrity_guard.compute_merkle_root()}
        else:
            return {"ok": False, "error": f"Ferramenta desconhecida: {name}"}


scanners_mcp_server = ScannersMcpServer()
