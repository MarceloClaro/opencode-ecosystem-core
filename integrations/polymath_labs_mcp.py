# -*- coding: utf-8 -*-
"""Polymath Labs MCP — Superfície MCP da allowlist R711 (SPEC-935-R712).

Ferramentas sobre `integrations/github_polymath_labs.py`, sem rede/subprocesso/LLM
no núcleo. Orquestração pertence ao orquestrador; MCP é ferramenta/contexto.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, Mapping

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from integrations import github_polymath_labs as labs  # noqa: E402
from integrations.mcp_validation import validate_arguments  # noqa: E402

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    try:
        from mcp.types import CallToolResult
    except ImportError:
        class CallToolResult(list[TextContent]):  # compat
            def __init__(self, *, content, isError=False, **extra):
                super().__init__(content)
                self.content = list(content)
                self.isError = isError
    _MCP_DISPONIVEL = True
except ImportError:
    _MCP_DISPONIVEL = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("polymath-labs-mcp")

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "listar_labs": {"type": "object", "properties": {}, "additionalProperties": False},
    "validar_lab": {
        "type": "object",
        "properties": {"url": {"type": "string", "description": "URL https://github.com/org/repo da allowlist R711"}},
        "required": ["url"],
    },
    "manifesto_labs": {
        "type": "object",
        "properties": {"destino_dir": {"type": "string", "description": "Diretório que recebe labs_manifest.json"}},
        "required": ["destino_dir"],
    },
    "auditar_clones": {
        "type": "object",
        "properties": {"base_dir": {"type": "string", "description": "Diretório base com clones org__repo"}},
        "required": ["base_dir"],
    },
    "rotulo_polimata": {"type": "object", "properties": {}, "additionalProperties": False},
    "pinar_lab": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL https://github.com/org/repo da allowlist R711"},
            "consentimento": {"type": "boolean", "description": "Consentimento explícito do operador para rede (obrigatório true)"}
        },
        "required": ["url", "consentimento"],
    },
    "revalidar_federacao": {
        "type": "object",
        "properties": {
            "consentimento": {"type": "boolean", "description": "Consentimento explícito do operador para rede (obrigatório true)"},
            "dias": {"type": "integer", "description": "Janela de manutenção em dias (padrão 90)"}
        },
        "required": ["consentimento"],
    },
    "propor_federacao": {
        "type": "object",
        "properties": {
            "consentimento": {"type": "boolean", "description": "Consentimento explícito do operador (obrigatório true)"}
        },
        "required": ["consentimento"],
    },
}

TOOL_DESCRIPTIONS = {
    "listar_labs": "Lista a allowlist R711 de laboratórios por tipo de raciocínio, com licença e uso polímata. Candidatos a inspeção, sem autoridade epistêmica.",
    "validar_lab": "Valida URL contra a allowlist R711 (fail-closed HTTPS GitHub org/repo). Fora da allowlist é rejeitada.",
    "manifesto_labs": "Emite labs_manifest.json auditável em diretório explícito, sem rede nem clone.",
    "auditar_clones": "Audita clones locais por leitura de .git/HEAD e hash de README, sem subprocesso. Ausente não é erro fatal.",
    "rotulo_polimata": "Retorna rótulo candidato_a_inspecao com exigência de validação externa; nunca aprova.",
    "pinar_lab": "Extensão R713: orienta pinagem viva de um lab; exige consentimento=true, sem executar rede no gate.",
    "revalidar_federacao": "Extensão R713: orienta revalidação 90d de toda a allowlist; exige consentimento=true, sem executar rede no gate.",
    "propor_federacao": "Extensão R715: orienta proposta por classe com override auditado; exige consentimento=true, nada federado automaticamente.",
}


def _tool_listar_labs() -> Dict[str, Any]:
    try:
        itens = labs.listar_labs()
        return {"ok": True, "total": len(itens), "labs": itens, "rotulo": "candidato_a_inspecao"}
    except Exception as exc:
        return {"ok": False, "error": f"Falha ao listar: {type(exc).__name__}."}


def _tool_validar_lab(url: str) -> Dict[str, Any]:
    if not isinstance(url, str) or not url.strip():
        return {"ok": False, "error": "Payload inválido: 'url' deve ser string não vazia."}
    try:
        canonica = labs.validar_url(url)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    for item in labs.listar_labs():
        if item["url"].lower() == canonica.lower():
            return {"ok": True, "id": item["id"], "url": item["url"], "tipo_raciocinio": item["tipo_raciocinio"]}
    return {"ok": False, "error": f"Fora da allowlist R711: {url!r}."}


def _tool_manifesto_labs(destino_dir: str) -> Dict[str, Any]:
    if not isinstance(destino_dir, str) or not destino_dir.strip():
        return {"ok": False, "error": "Payload inválido: 'destino_dir' deve ser string não vazia."}
    try:
        return labs.gerar_manifesto(destino_dir)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "error": f"Falha no manifesto: {type(exc).__name__}."}


def _tool_auditar_clones(base_dir: str) -> Dict[str, Any]:
    if not isinstance(base_dir, str) or not base_dir.strip():
        return {"ok": False, "error": "Payload inválido: 'base_dir' deve ser string não vazia."}
    try:
        rel = labs.verificar_clones(base_dir)
        return {"ok": True, **rel}
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "error": f"Falha na auditoria: {type(exc).__name__}."}


def _tool_rotulo_polimata() -> Dict[str, Any]:
    base = labs.rotulo_epistemico()
    return {"rotulo": base["rotulo"], "exige_validacao_externa": True, "nota": base.get("nota", "")}


def _tool_pinar_lab(url: str, consentimento: bool) -> Dict[str, Any]:
    if consentimento is not True:
        return {"ok": False, "error": "Pinagem viva exige consentimento=true explícito do operador (R713)."}
    try:
        labs.validar_url(url)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": "Rotina viva fora do gate: operador deve executar integrations.polymath_pinagem.pinar_lab com fetcher vivo (GET api.github.com + git ls-remote).", "rotulo": "candidato_a_inspecao"}


def _tool_revalidar_federacao(consentimento: bool, dias: int = 90) -> Dict[str, Any]:
    if consentimento is not True:
        return {"ok": False, "error": "Revalidação exige consentimento=true explícito do operador (R713)."}
    return {"ok": False, "error": f"Rotina viva fora do gate: operador deve executar revalidar_todos + emitir_pins com janela {int(dias) if isinstance(dias, int) else 90}d.", "rotulo": "candidato_a_inspecao"}


def _tool_propor_federacao(consentimento: bool) -> Dict[str, Any]:
    if consentimento is not True:
        return {"ok": False, "error": "Proposta exige consentimento=true explícito (R715)."}
    return {"ok": False, "error": "Fora do gate: operador deve executar polymath_federacao.propor + emitir_proposta com overrides auditados; nada federado automaticamente.", "rotulo": "candidato_a_inspecao"}


def _text_content(text: str):
    from mcp.types import TextContent as TC
    return [TC(type="text", text=text)]


if _MCP_DISPONIVEL:
    app = Server("polymath-labs-mcp")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(name=n, description=TOOL_DESCRIPTIONS[n], inputSchema=s) for n, s in TOOL_SCHEMAS.items()]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name not in TOOL_SCHEMAS:
            return _text_content(json.dumps({"ok": False, "error": f"Ferramenta desconhecida: {name}"}, ensure_ascii=False))
        if not isinstance(arguments, Mapping):
            return _text_content(json.dumps({"ok": False, "error": "Payload inválido."}, ensure_ascii=False))
        val = validate_arguments(name, dict(arguments), TOOL_SCHEMAS[name])
        if not val["valid"]:
            return _text_content(json.dumps({"ok": False, "error": "Payload inválido: " + "; ".join(val["errors"])}, ensure_ascii=False))
        try:
            if name == "listar_labs":
                return _text_content(json.dumps(_tool_listar_labs(), ensure_ascii=False, indent=2))
            if name == "validar_lab":
                return _text_content(json.dumps(_tool_validar_lab(arguments.get("url", "")), ensure_ascii=False, indent=2))
            if name == "manifesto_labs":
                return _text_content(json.dumps(_tool_manifesto_labs(arguments.get("destino_dir", "")), ensure_ascii=False, indent=2))
            if name == "auditar_clones":
                return _text_content(json.dumps(_tool_auditar_clones(arguments.get("base_dir", "")), ensure_ascii=False, indent=2))
            if name == "rotulo_polimata":
                return _text_content(json.dumps(_tool_rotulo_polimata(), ensure_ascii=False, indent=2))
            if name == "pinar_lab":
                return _text_content(json.dumps(_tool_pinar_lab(arguments.get("url", ""), arguments.get("consentimento", False)), ensure_ascii=False, indent=2))
            if name == "revalidar_federacao":
                return _text_content(json.dumps(_tool_revalidar_federacao(arguments.get("consentimento", False), arguments.get("dias", 90)), ensure_ascii=False, indent=2))
            if name == "propor_federacao":
                return _text_content(json.dumps(_tool_propor_federacao(arguments.get("consentimento", False)), ensure_ascii=False, indent=2))
        except Exception as exc:
            logger.debug("Falha em %s: %s", name, exc, exc_info=True)
            return _text_content(json.dumps({"ok": False, "error": f"Falha: {type(exc).__name__}."}, ensure_ascii=False))
        return _text_content(json.dumps({"ok": False, "error": "Ferramenta desconhecida."}, ensure_ascii=False))

    async def main():
        async with stdio_server() as (rs, ws):
            await app.run(rs, ws, app.create_initialization_options())

    if __name__ == "__main__":
        asyncio.run(main())
