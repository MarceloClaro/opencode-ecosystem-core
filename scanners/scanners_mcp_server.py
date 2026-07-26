# -*- coding: utf-8 -*-
"""
Scanners MCP Server — Servidor MCP para o SuperRigorPipeline e Scanners
========================================================================
Expõe as ferramentas dos 8 scanners e auditoria do ecossistema via MCP.

Ferramentas:
  - super_rigor_audit:          Executa auditoria completa através dos 8 scanners
  - scientific_reasoning_scan:   Avalia o Índice de Rigor Científico (SRI 0-100)
  - merkle_integrity_check:     Verifica a integridade SHA-256 via Árvore de Merkle

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import os
import sys
import json
import asyncio
import logging
from typing import Any, Mapping, Dict

# Adiciona a raiz do projeto ao sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scanners.pipeline import super_rigor_pipeline
from scanners.scientific_reasoning_scanner import scientific_reasoning_scanner
from benchmarks.merkle_integrity_guard import merkle_integrity_guard

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

try:
    from mcp.types import CallToolResult
except ImportError:
    class CallToolResult(list[TextContent]):
        def __init__(
            self, *, content: list[TextContent], isError: bool = False, **extra_data: Any,
        ) -> None:
            super().__init__(content)
            self.content = list(content)
            self.isError = isError
            for key, value in extra_data.items():
                setattr(self, key, value)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("scanners-mcp")


def _text_content(text: str) -> list[TextContent]:
    return [TextContent(type="text", text=text)]


def _mcp_error(message: str) -> CallToolResult:
    return CallToolResult(content=_text_content(message), isError=True)


def _call_tool_result(data: dict) -> CallToolResult:
    return CallToolResult(
        content=_text_content(json.dumps(data, indent=2, ensure_ascii=False)),
    )


# ── MCP Server ────────────────────────────────────────────────────

app = Server("scanners-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="super_rigor_audit",
            description="Executa auditoria completa através dos 8 scanners do ecossistema e calcula o Score de Excelência (EXS)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto a ser auditado",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="scientific_reasoning_scan",
            description="Avalia o Índice de Rigor Científico (SRI 0-100) e detecta falácias epistemológicas no texto",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto científico a ser analisado",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="merkle_integrity_check",
            description="Verifica a integridade criptográfica SHA-256 do código-fonte através da Árvore de Merkle",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult | list[TextContent]:
    supported_tools = {"super_rigor_audit", "scientific_reasoning_scan", "merkle_integrity_check"}
    if not isinstance(name, str) or name not in supported_tools:
        return _mcp_error(f"Ferramenta desconhecida: {name}")
    if not isinstance(arguments, Mapping):
        return _mcp_error("Payload inválido: argumentos devem ser um objeto.")

    if name == "super_rigor_audit":
        text = arguments.get("text", "")
        if not isinstance(text, str):
            return _mcp_error("Payload inválido: 'text' deve ser uma string.")
        try:
            result = super_rigor_pipeline.audit_production(text)
            return _call_tool_result({"ok": True, "result": result})
        except Exception as exc:
            logger.debug("Falha no super_rigor_audit: %s", exc, exc_info=True)
            return _mcp_error(f"Falha na auditoria: {type(exc).__name__}.")

    if name == "scientific_reasoning_scan":
        text = arguments.get("text", "")
        if not isinstance(text, str):
            return _mcp_error("Payload inválido: 'text' deve ser uma string.")
        try:
            result = scientific_reasoning_scanner.scan_text(text)
            return _call_tool_result({"ok": True, "result": result})
        except Exception as exc:
            logger.debug("Falha no scientific_reasoning_scan: %s", exc, exc_info=True)
            return _mcp_error(f"Falha no scan: {type(exc).__name__}.")

    if name == "merkle_integrity_check":
        try:
            result = merkle_integrity_guard.compute_merkle_root()
            return _call_tool_result({"ok": True, "result": result})
        except Exception as exc:
            logger.debug("Falha no merkle_integrity_check: %s", exc, exc_info=True)
            return _mcp_error(f"Falha no check: {type(exc).__name__}.")

    return _mcp_error(f"Ferramenta desconhecida: {name}")


class ScannersMcpServer:
    """Classe Wrapper para testes internos e chamadas síncronas do ecossistema."""

    def get_tools(self) -> Dict[str, Any]:
        return {
            "super_rigor_audit": {
                "description": "Executa auditoria completa através dos 8 scanners do ecossistema",
                "parameters": {"text": "Texto a ser auditado"},
            },
            "scientific_reasoning_scan": {
                "description": "Avalia o Índice de Rigor Científico (SRI 0-100)",
                "parameters": {"text": "Texto científico a ser analisado"},
            },
            "merkle_integrity_check": {
                "description": "Verifica a integridade criptográfica SHA-256 do código-fonte",
                "parameters": {},
            },
        }

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
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


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
