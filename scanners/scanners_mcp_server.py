# -*- coding: utf-8 -*-
"""
Scanners MCP Server — Servidor MCP para o SuperRigorPipeline e Scanners
========================================================================
Expõe triagens heurísticas e diagnóstico do ecossistema via MCP.

Ferramentas:
  - super_rigor_audit:          Combina diagnóstico heurístico e triagem lexical
  - scientific_reasoning_scan:   Triagem lexical PT/EN, sem avaliação científica
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

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Adiciona a raiz do projeto ao sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Imports locais após o bootstrap permitem executar este arquivo standalone.
from scanners.pipeline import super_rigor_pipeline  # noqa: E402
from scanners.scientific_reasoning_scanner import scientific_reasoning_scanner  # noqa: E402
from scanners.literary_scanners import run_literary_scanner_suite  # noqa: E402
from scanners.literary_research_scanners import run_literary_research_scanner_suite  # noqa: E402
from benchmarks.merkle_integrity_guard import merkle_integrity_guard  # noqa: E402
from integrations.mcp_validation import validate_arguments  # noqa: E402

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

# Limite de caracteres Unicode, anunciado no schema e validado antes de qualquer
# scanner tanto no servidor assíncrono quanto no wrapper síncrono (R815).
MAX_SCIENTIFIC_TEXT_CHARS = 1_000_000

TOOL_SCHEMAS = {
    "super_rigor_audit": {
        "type": "object", "properties": {"text": {"type": "string", "maxLength": MAX_SCIENTIFIC_TEXT_CHARS}},
        "required": ["text"], "additionalProperties": False,
    },
    "scientific_reasoning_scan": {
        "type": "object", "properties": {"text": {"type": "string", "maxLength": MAX_SCIENTIFIC_TEXT_CHARS}},
        "required": ["text"], "additionalProperties": False,
    },
    "merkle_integrity_check": {"type": "object", "properties": {}, "additionalProperties": False},
    "literary_scanner_suite": {
        "type": "object", "properties": {"text": {"type": "string"}, "metadata": {"type": "object"}},
        "required": ["text"], "additionalProperties": False,
    },
    "literary_research_scanner_suite": {
        "type": "object", "properties": {"text": {"type": "string"}, "metadata": {"type": "object"}},
        "required": ["text"], "additionalProperties": False,
    },
}

TOOL_DESCRIPTIONS = {
    "super_rigor_audit": (
        "Combina diagnósticos heurísticos do ecossistema e triagem lexical científica. "
        "Preserva scores e status legados; não avalia qualidade científica, "
        "validade clínica ou risco de viés. Entrada limitada a 1.000.000 caracteres Unicode."
    ),
    "scientific_reasoning_scan": (
        "Realiza triagem lexical PT/EN de conceitos e gatilhos categóricos. "
        "Não avalia qualidade científica, validade clínica ou risco de viés; "
        "os scores e rótulos legados são indicadores heurísticos. Entrada limitada a 1.000.000 caracteres Unicode."
    ),
    "merkle_integrity_check": "Verifica a integridade criptográfica SHA-256 do código-fonte através da Árvore de Merkle",
    "literary_scanner_suite": "Realiza triagem heurística literária: narrativa, personagem, estilo, símbolos, teoria, leitor, ética e inovação",
    "literary_research_scanner_suite": "Realiza triagem heurística de pesquisa literária: bibliografia, corpus comparativo, teoria e estrutura de relato",
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="super_rigor_audit",
            description=TOOL_DESCRIPTIONS["super_rigor_audit"],
            inputSchema=TOOL_SCHEMAS["super_rigor_audit"],
        ),
        Tool(
            name="scientific_reasoning_scan",
            description=TOOL_DESCRIPTIONS["scientific_reasoning_scan"],
            inputSchema=TOOL_SCHEMAS["scientific_reasoning_scan"],
        ),
        Tool(
            name="merkle_integrity_check",
            description=TOOL_DESCRIPTIONS["merkle_integrity_check"],
            inputSchema=TOOL_SCHEMAS["merkle_integrity_check"],
        ),
        Tool(
            name="literary_scanner_suite",
            description=TOOL_DESCRIPTIONS["literary_scanner_suite"],
            inputSchema=TOOL_SCHEMAS["literary_scanner_suite"],
        ),
        Tool(
            name="literary_research_scanner_suite",
            description=TOOL_DESCRIPTIONS["literary_research_scanner_suite"],
            inputSchema=TOOL_SCHEMAS["literary_research_scanner_suite"],
        ),
    ]


# O SDK usa ValidationError.message e ecoaria a entrada rejeitada inteira.
# O handler abaixo aplica o mesmo schema com diagnósticos de regra/caminho,
# sem valores, antes de executar qualquer scanner.
@app.call_tool(validate_input=False)
async def call_tool(name: str, arguments: dict) -> CallToolResult | list[TextContent]:
    supported_tools = {"super_rigor_audit", "scientific_reasoning_scan", "merkle_integrity_check", "literary_scanner_suite", "literary_research_scanner_suite"}
    if not isinstance(name, str) or name not in supported_tools:
        return _mcp_error(f"Ferramenta desconhecida: {name}")
    if not isinstance(arguments, Mapping):
        return _mcp_error("Payload inválido: argumentos devem ser um objeto.")
    validation = validate_arguments(name, dict(arguments), TOOL_SCHEMAS[name])
    if not validation["valid"]:
        return _mcp_error("Payload inválido: " + "; ".join(validation["errors"]))

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

    if name == "literary_scanner_suite":
        text = arguments.get("text", "")
        metadata = arguments.get("metadata", {})
        if not isinstance(text, str):
            return _mcp_error("Payload inválido: 'text' deve ser uma string.")
        if not isinstance(metadata, Mapping):
            return _mcp_error("Payload inválido: 'metadata' deve ser um objeto.")
        try:
            result = run_literary_scanner_suite(text, metadata=metadata)
            return _call_tool_result({"ok": True, "result": result})
        except Exception as exc:
            logger.debug("Falha no literary_scanner_suite: %s", exc, exc_info=True)
            return _mcp_error(f"Falha no scan literário: {type(exc).__name__}.")

    if name == "literary_research_scanner_suite":
        text = arguments.get("text", "")
        metadata = arguments.get("metadata", {})
        if not isinstance(text, str):
            return _mcp_error("Payload inválido: 'text' deve ser uma string.")
        if not isinstance(metadata, Mapping):
            return _mcp_error("Payload inválido: 'metadata' deve ser um objeto.")
        try:
            result = run_literary_research_scanner_suite(text, metadata=metadata)
            return _call_tool_result({"ok": True, "result": result})
        except Exception as exc:
            logger.debug("Falha no literary_research_scanner_suite: %s", exc, exc_info=True)
            return _mcp_error(f"Falha no scan de pesquisa literária: {type(exc).__name__}.")

    return _mcp_error(f"Ferramenta desconhecida: {name}")


class ScannersMcpServer:
    """Classe Wrapper para testes internos e chamadas síncronas do ecossistema."""

    def get_tools(self) -> Dict[str, Any]:
        return {
            "super_rigor_audit": {
                "description": TOOL_DESCRIPTIONS["super_rigor_audit"],
                "parameters": {"text": "Texto a ser auditado"},
            },
            "scientific_reasoning_scan": {
                "description": TOOL_DESCRIPTIONS["scientific_reasoning_scan"],
                "parameters": {"text": "Texto científico a ser analisado"},
            },
            "merkle_integrity_check": {
                "description": TOOL_DESCRIPTIONS["merkle_integrity_check"],
                "parameters": {},
            },
            "literary_scanner_suite": {
                "description": TOOL_DESCRIPTIONS["literary_scanner_suite"],
                "parameters": {"text": "Texto literário", "metadata": "Metadados opcionais"},
            },
            "literary_research_scanner_suite": {
                "description": TOOL_DESCRIPTIONS["literary_research_scanner_suite"],
                "parameters": {"text": "Pesquisa literária", "metadata": "Metadados opcionais"},
            },
        }

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(name, str) or name not in TOOL_SCHEMAS:
            return {"ok": False, "error": f"Ferramenta desconhecida: {name}"}
        validation = validate_arguments(name, args, TOOL_SCHEMAS[name])
        if not validation["valid"]:
            return {"ok": False, "error": "Payload inválido: " + "; ".join(validation["errors"])}
        if name == "super_rigor_audit":
            text = args.get("text", "")
            return {"ok": True, "result": super_rigor_pipeline.audit_production(text)}
        elif name == "scientific_reasoning_scan":
            text = args.get("text", "")
            return {"ok": True, "result": scientific_reasoning_scanner.scan_text(text)}
        elif name == "merkle_integrity_check":
            return {"ok": True, "result": merkle_integrity_guard.compute_merkle_root()}
        elif name == "literary_scanner_suite":
            text = args.get("text", "")
            metadata = args.get("metadata", {})
            return {"ok": True, "result": run_literary_scanner_suite(text, metadata=metadata)}
        elif name == "literary_research_scanner_suite":
            text = args.get("text", "")
            metadata = args.get("metadata", {})
            return {"ok": True, "result": run_literary_research_scanner_suite(text, metadata=metadata)}
        else:
            return {"ok": False, "error": f"Ferramenta desconhecida: {name}"}


scanners_mcp_server = ScannersMcpServer()


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
