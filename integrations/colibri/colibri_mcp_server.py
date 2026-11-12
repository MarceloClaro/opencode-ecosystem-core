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

from integrations.colibri.bridge import ColibriBridge, COLI_MODELS

logging.basicConfig(
    level=logging.INFO,
    format="[colibri-mcp] %(levelname)s %(message)s",
)
logger = logging.getLogger("colibri-mcp")


def _tool_schemas() -> Dict[str, Any]:
    """Catálogo estático: consultar ferramentas não inicializa inferência."""
    return {
        "colibri:chat": {
            "description": "Chat multi-turn com GLM-5.2 via Colibri (requer ./coli serve)",
            "inputSchema": {"type": "object", "properties": {
                "messages": {"type": "array", "items": {"type": "object"}},
                "max_tokens": {"type": "integer", "default": 2048},
                "temperature": {"type": "number", "default": 0.7},
            }, "required": ["messages"]},
        },
        "colibri:complete": {
            "description": "Completion single-turn com GLM-5.2 (requer ./coli serve)",
            "inputSchema": {"type": "object", "properties": {
                "prompt": {"type": "string"}, "system": {"type": "string"},
                "max_tokens": {"type": "integer", "default": 1024},
                "temperature": {"type": "number", "default": 0.7},
            }, "required": ["prompt"]},
        },
        "colibri:olmoe:complete": {
            "description": "Inferência OLMoE via binário nativo e snapshot local (se instalados)",
            "inputSchema": {"type": "object", "properties": {
                "prompt": {"type": "string"},
                "max_tokens": {"type": "integer", "default": 64},
                "quant_bits": {"type": "integer", "default": 4},
                "cache_size": {"type": "integer", "default": 32},
                "pilot": {"type": "integer", "default": 1},
                "hot": {"type": "integer", "default": 4},
            }, "required": ["prompt"]},
        },
        "colibri:olmoe:validate": {
            "description": "Valida engine OLMoE contra referência token-exata, se instalada",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "colibri:status": {
            "description": "Estado e prontidão dos runtimes Colibri (GLM-5.2 e OLMoE)",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "colibri:info": {
            "description": "Informações dos engines disponíveis",
            "inputSchema": {"type": "object", "properties": {}},
        },
    }


def _invalid_params(message: str, req_id: Any) -> Dict[str, Any]:
    """Erro JSON-RPC de parâmetros, sempre antes de tocar o provedor."""
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32602, "message": message}}


def _positive_int(value: Any, *, default: int, field: str,
                  req_id: Any) -> Dict[str, Any] | int:
    """Valida inteiro positivo sem aceitar bool, float implícito ou zero."""
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return _invalid_params(f"{field} deve ser inteiro positivo", req_id)
    return value


def _temperature(value: Any, *, default: float, req_id: Any) -> Dict[str, Any] | float:
    """Valida temperatura numérica finita em [0, 2]."""
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return _invalid_params("temperature deve ser numérica", req_id)
    if not (0 <= float(value) <= 2):
        return _invalid_params("temperature deve estar entre 0 e 2", req_id)
    return float(value)


def _validate_tool_arguments(tool_name: str, arguments: Dict[str, Any],
                             req_id: Any) -> Dict[str, Any] | None:
    """Valida o subconjunto de ferramentas que dispara inferência."""
    if tool_name == "colibri:complete":
        prompt = arguments.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return _invalid_params("prompt deve ser texto não vazio", req_id)
        max_tokens = _positive_int(arguments.get("max_tokens"), default=1024,
                                   field="max_tokens", req_id=req_id)
        if isinstance(max_tokens, dict):
            return max_tokens
        temperature = _temperature(arguments.get("temperature"), default=0.7,
                                   req_id=req_id)
        if isinstance(temperature, dict):
            return temperature
        arguments["max_tokens"] = max_tokens
        arguments["temperature"] = temperature
        return None

    if tool_name == "colibri:chat":
        messages = arguments.get("messages")
        if not isinstance(messages, list) or not messages:
            return _invalid_params("messages deve ser lista não vazia", req_id)
        if any(not isinstance(item, dict) for item in messages):
            return _invalid_params("cada mensagem deve ser objeto", req_id)
        max_tokens = _positive_int(arguments.get("max_tokens"), default=2048,
                                   field="max_tokens", req_id=req_id)
        if isinstance(max_tokens, dict):
            return max_tokens
        temperature = _temperature(arguments.get("temperature"), default=0.7,
                                   req_id=req_id)
        if isinstance(temperature, dict):
            return temperature
        arguments["max_tokens"] = max_tokens
        arguments["temperature"] = temperature
        return None

    if tool_name == "colibri:olmoe:complete":
        prompt = arguments.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return _invalid_params("prompt deve ser texto não vazio", req_id)
        for field, default in (("max_tokens", 64), ("cache_size", 32)):
            value = _positive_int(arguments.get(field), default=default,
                                  field=field, req_id=req_id)
            if isinstance(value, dict):
                return value
            arguments[field] = value
        for field in ("quant_bits", "pilot", "hot"):
            value = arguments.get(field)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return _invalid_params(f"{field} deve ser inteiro não negativo", req_id)
        return None

    return None


def handle_request(request: Dict[str, Any]) -> Dict[str, Any] | None:
    """Processa uma requisição MCP e despacha para a ferramenta adequada."""
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
        return {"jsonrpc": "2.0", "id": None,
                "error": {"code": -32600, "message": "Requisição JSON-RPC inválida"}}
    # JSON-RPC proíbe responder notificações, inclusive initialized/cancelled.
    if "id" not in request:
        return None
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request["id"]
    if not isinstance(params, dict):
        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32602, "message": "params deve ser objeto"}}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": (params.get("protocolVersion")
                                    if params.get("protocolVersion") in ("2024-11-05", "2025-03-26")
                                    else "2025-03-26"),
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "colibri-mcp",
                    "version": "1.1.0",
                },
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {
            "tools": [{"name": name, **schema} for name, schema in _tool_schemas().items()]}}

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        if not isinstance(tool_name, str) or not isinstance(tool_args, dict):
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602, "message": "name deve ser texto e arguments objeto"}}
        invalid = _validate_tool_arguments(tool_name, tool_args, req_id)
        if invalid is not None:
            return invalid
        bridge = ColibriBridge()

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
                    "isError": result.get("status") in ("error", "unavailable"),
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
                    "isError": result.get("status") in ("error", "unavailable"),
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
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "JSON inválido"},
            }
        else:
            try:
                response = handle_request(request)
            except Exception:
                logger.exception("Falha ao processar requisição MCP")
                response = {"jsonrpc": "2.0", "id": request.get("id"),
                            "error": {"code": -32603, "message": "Erro interno do servidor"}}
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
