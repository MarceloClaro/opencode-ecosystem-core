#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colibri MCP Server — Servidor MCP para runtimes Colibri (GLM-5.2 / OLMoE)
=============================================================================
Disponibiliza ferramentas de inferência local via protocolo MCP do OpenCode.

Ferramentas:
  - colibri:chat — Chat multi-turn com GLM-5.2 (requer ./coli serve)
  - colibri:complete — Completion single-turn (GLM-5.2)
  - colibri:olmoe:complete — Inferência OLMoE 1B-7B (binário nativo)
  - colibri:olmoe:validate — Validação contra referência
  - colibri:status — Estado e prontidão dos runtimes
  - colibri:info — Informações dos engines disponíveis

Uso (modo servidor MCP):
    python3 -m integrations.colibri.colibri_mcp_server

Referência: https://github.com/MarceloClaro/colibri
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict

from integrations.colibri.bridge import ColibriBridge, COLI_CAPABILITIES

logging.basicConfig(
    level=logging.INFO,
    format="[colibri-mcp] %(levelname)s %(message)s",
)
logger = logging.getLogger("colibri-mcp")


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Processa uma requisição MCP e despacha para a ferramenta adequada."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", 0)

    bridge = ColibriBridge()

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {
                        "colibri:chat": {
                            "description": "Chat multi-turn com GLM-5.2 (744B MoE) via Colibri (requer ./coli serve)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "messages": {
                                        "type": "array",
                                        "description": "Lista de mensagens [{'role': 'user'|'assistant', 'content': '...'}]",
                                    },
                                    "max_tokens": {"type": "integer", "default": 2048},
                                    "temperature": {"type": "number", "default": 0.7},
                                },
                                "required": ["messages"],
                            },
                        },
                        "colibri:complete": {
                            "description": "Completion single-turn com GLM-5.2 (requer ./coli serve)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string"},
                                    "system": {"type": "string"},
                                    "max_tokens": {"type": "integer", "default": 1024},
                                    "temperature": {"type": "number", "default": 0.7},
                                },
                                "required": ["prompt"],
                            },
                        },
                        "colibri:olmoe:complete": {
                            "description": "Inferência OLMoE 1B-7B MoE via binário nativo (CPU, já convertido)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string", "description": "Texto de entrada"},
                                    "max_tokens": {"type": "integer", "default": 64},
                                    "quant_bits": {"type": "integer", "default": 4, "description": "Bits de quantização (2-8)"},
                                    "cache_size": {"type": "integer", "default": 32},
                                    "pilot": {"type": "integer", "default": 1, "description": "Nível de prefetch (0-3)"},
                                    "hot": {"type": "integer", "default": 4, "description": "Experts fixos por layer"},
                                },
                                "required": ["prompt"],
                            },
                        },
                        "colibri:olmoe:validate": {
                            "description": "Valida engine OLMoE contra referência token-exata",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                            },
                        },
                        "colibri:status": {
                            "description": "Estado e prontidão dos runtimes Colibri (GLM-5.2 + OLMoE)",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                        "colibri:info": {
                            "description": "Informações detalhadas dos engines disponíveis",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                    },
                },
                "serverInfo": {
                    "name": "colibri-mcp",
                    "version": "1.1.0",
                },
            },
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        if tool_name == "colibri:chat":
            messages = tool_args.get("messages", [])
            result = bridge.chat(
                messages=messages,
                max_tokens=tool_args.get("max_tokens", 2048),
                temperature=tool_args.get("temperature", 0.7),
            )
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": result.get("content", str(result))}],
                    "isError": result.get("status") == "error",
                },
            }

        if tool_name == "colibri:complete":
            result = bridge.complete(
                prompt=tool_args.get("prompt", ""),
                system=tool_args.get("system"),
                max_tokens=tool_args.get("max_tokens", 1024),
                temperature=tool_args.get("temperature", 0.7),
            )
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": result.get("content", str(result))}],
                    "isError": result.get("status") == "error",
                },
            }

        if tool_name == "colibri:olmoe:complete":
            result = bridge.olmoe_complete(
                prompt=tool_args.get("prompt", ""),
                max_tokens=tool_args.get("max_tokens", 64),
                quant_bits=tool_args.get("quant_bits", 4),
                cache_size=tool_args.get("cache_size", 32),
                pilot=tool_args.get("pilot", 1),
                hot=tool_args.get("hot", 4),
            )
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": result.get("status") == "error" or result.get("status") == "unavailable",
                },
            }

        if tool_name == "colibri:olmoe:validate":
            result = bridge.olmoe_validate()
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": result.get("status") == "error" or result.get("status") == "unavailable",
                },
            }

        if tool_name == "colibri:status":
            status = {
                "colibri_glm": bridge.check_readiness(),
                "olmoe": {
                    "available": bridge.olmoe_available,
                    "binary": bridge.olmoe_bin,
                    "snapshot": bridge.olmoe_snap,
                },
                "models": list(COLI_MODELS.keys()),
            }
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(status, ensure_ascii=False, indent=2)}],
                },
            }

        if tool_name == "colibri:info":
            info = {
                "colibri_glm": bridge.get_info(),
                "olmoe": {
                    "available": bridge.olmoe_available,
                    "binary": bridge.olmoe_bin,
                    "snapshot": bridge.olmoe_snap,
                },
            }
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(info, ensure_ascii=False, indent=2)}],
                },
            }

        return {
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": f"Ferramenta não encontrada: {tool_name}"},
        }

    if method == "notifications/initialized":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    return {
        "jsonrpc": "2.0", "id": req_id,
        "error": {"code": -32601, "message": f"Método não suportado: {method}"},
    }


def main() -> None:
    """Modo servidor MCP: lê requisições JSON-RPC de stdin, responde em stdout."""
    logger.info("Colibri MCP Server v1.1 iniciado (GLM-5.2 + OLMoE)")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except (json.JSONDecodeError, Exception) as exc:
            error_resp = {
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(error_resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
