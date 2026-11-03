#!/usr/bin/env python3
"""MCP Server — OA Resolver (SPEC-935-R1010).

Expõe o pipeline auditado do Core:
  - oa_resolve:       DOI → candidatos legais (sem download)
  - oa_download:      DOI → PDF legal + pasta de auditoria + fichamento + resenha + RAG
  - oa_query_rag:     consulta o índice lexical de uma pasta de auditoria
  - oa_audit_status:  inventário e manifesto de uma pasta
  - oa_list_folders:  pastas de auditoria existentes

Princípios:
  - nenhuma fonte não autorizada é consultada ou baixada;
  - download exige `confirm=true` (dry-run por padrão);
  - pasta confinada a OA_AUDIT_BASE (padrão: <repo>/auditoria_fichamentos);
  - sem tradutor/argumentador, os campos ficam pendentes — nada é inventado;
  - erros viram isError com motivo, nunca silêncio.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research.oa_resolver import openalex_runner, openalex_work, resolve  # noqa: E402
from research.pdf_pipeline import http_fetcher, query_rag, rag_manifest, run  # noqa: E402

from mcp.server import Server  # noqa: E402
from mcp.server.stdio import stdio_server  # noqa: E402
from mcp.types import TextContent, Tool  # noqa: E402

try:
    from mcp.types import CallToolResult
except ImportError:  # pragma: no cover - SDK antigo
    class CallToolResult(list[TextContent]):
        def __init__(self, *, content=None, isError: bool = False, **extra: Any) -> None:
            super().__init__(content or [])
            self.content = list(content or [])
            self.isError = isError
            for key, value in extra.items():
                setattr(self, key, value)


app = Server("oa-resolver")


# ── infraestrutura ──────────────────────────────────────────────────────────


def _base_dir() -> Path:
    raw = os.environ.get("OA_AUDIT_BASE") or str(PROJECT_ROOT / "auditoria_fichamentos")
    base = Path(raw).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def _confine(pasta: str) -> Path:
    base = _base_dir()
    candidate = Path(str(pasta or "")).expanduser()
    target = candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError("pasta fora da base de auditoria") from exc
    if not target.is_dir():
        raise ValueError("pasta de auditoria não encontrada")
    return target


def _ok(payload: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def _mcp_error(message: str) -> CallToolResult:
    return CallToolResult(content=[TextContent(type="text", text=f"ERRO: {message}")], isError=True)


def _runner(mailto: str | None):
    if mailto:
        return lambda doi: openalex_runner(doi, mailto=mailto)
    return openalex_runner


def _meta_from_work(doi: str, work: dict[str, Any]) -> dict[str, Any]:
    source = ((work.get("primary_location") or {}).get("source") or {})
    return {
        "doi": doi,
        "titulo": work.get("title"),
        "autores": [
            a.get("author", {}).get("display_name")
            for a in (work.get("authorships") or [])
            if a.get("author")
        ],
        "ano": work.get("publication_year"),
        "fonte": source.get("display_name"),
    }


# ── funções puras (testáveis sem MCP) ───────────────────────────────────────


def resolve_payload(doi: str, mailto: str | None = None) -> dict[str, Any]:
    return resolve(doi, runners={"openalex": _runner(mailto)})


def download_payload(
    doi: str,
    *,
    confirm: bool = False,
    max_excerpts: int = 8,
    keywords: Iterable[str] = (),
    lang: str = "pt-BR",
    mailto: str | None = None,
) -> dict[str, Any]:
    plan = resolve_payload(doi, mailto)
    if plan.get("status") != "ok" or not plan.get("chosen"):
        return {
            "status": plan.get("status", "no_legal_pdf"),
            "doi": plan.get("doi", doi),
            "requires_confirmation": False,
            "rejected": plan.get("rejected", []),
            "pdf_downloaded": False,
        }

    chosen = plan["chosen"]
    if not confirm:
        return {
            "status": "confirmation_required",
            "requires_confirmation": True,
            "doi": plan["doi"],
            "candidate": {
                key: chosen.get(key)
                for key in ("source", "pdf_url", "license", "host_type", "version")
            },
            "note": "Nenhum download foi feito. Repita com confirm=true após revisar licença e origem.",
        }

    work = openalex_work(doi, mailto=mailto) if mailto else openalex_work(doi)
    meta = _meta_from_work(doi, work)
    return run(
        doi,
        meta,
        base_dir=str(_base_dir()),
        resolver_runners={"openalex": _runner(mailto)},
        fetcher=http_fetcher,
        translator=None,
        argumenter=None,
        max_excerpts=max_excerpts,
        keywords=tuple(keywords),
        target_lang=lang,
    )


def query_payload(pasta: str, query: str, k: int = 5) -> dict[str, Any]:
    target = _confine(pasta)
    hits = query_rag(str(target), query, k=max(1, min(int(k), 20)))
    return {"pasta": str(target), "query": query, "count": len(hits), "hits": hits}


def status_payload(pasta: str) -> dict[str, Any]:
    target = _confine(pasta)
    metadados = {}
    if (target / "metadados.json").is_file():
        metadados = json.loads((target / "metadados.json").read_text(encoding="utf-8"))
    recibo = {}
    if (target / "recibo.json").is_file():
        recibo = json.loads((target / "recibo.json").read_text(encoding="utf-8"))
    rag = rag_manifest(str(target)) if (target / "rag").is_dir() else None
    return {
        "pasta": str(target),
        "arquivos": sorted(p.name for p in target.iterdir()),
        "doi": metadados.get("doi"),
        "titulo": metadados.get("titulo"),
        "licenca": metadados.get("licenca"),
        "pdf_sha256": metadados.get("pdf_sha256"),
        "paginas": recibo.get("pages"),
        "recortes": recibo.get("excerpts"),
        "rag": rag,
    }


def list_payload() -> dict[str, Any]:
    base = _base_dir()
    pastas = []
    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue
        meta_path = item / "metadados.json"
        meta = {}
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
        pastas.append(
            {
                "pasta": item.name,
                "doi": meta.get("doi"),
                "titulo": meta.get("titulo"),
                "licenca": meta.get("licenca"),
            }
        )
    return {"base": str(base), "count": len(pastas), "pastas": pastas}


# ── catálogo MCP ────────────────────────────────────────────────────────────

TOOLS: list[Tool] = [
    Tool(
        name="oa_resolve",
        description=(
            "Resolve um DOI em candidatos de PDF por vias legais (OpenAlex). "
            "Não baixa nada. Recusa fontes não autorizadas e exige licença observada."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {"type": "string", "description": "DOI (aceita DOI:, doi.org ou simples)"},
                "mailto": {"type": "string", "description": "e-mail opcional para o polite pool do OpenAlex"},
            },
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="oa_download",
        description=(
            "Baixa o PDF legal e cria pasta de auditoria com metadados, páginas, "
            "recortes, fichamento ABNT, resenha e índice RAG. Dry-run por padrão: "
            "só baixa com confirm=true. Tradução/argumentação ficam pendentes "
            "(nenhum texto é inventado)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {"type": "string"},
                "confirm": {"type": "boolean", "description": "true autoriza o download"},
                "max_excerpts": {"type": "integer", "minimum": 1, "maximum": 30},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "lang": {"type": "string"},
                "mailto": {"type": "string"},
            },
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="oa_query_rag",
        description=(
            "Consulta o índice lexical (BM25) de uma pasta de auditoria. "
            "Retorna trechos com página, score, hash e citação ABNT. "
            "A pasta precisa estar dentro de OA_AUDIT_BASE."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "pasta": {"type": "string", "description": "nome da pasta ou caminho dentro da base"},
                "query": {"type": "string"},
                "k": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "required": ["pasta", "query"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="oa_audit_status",
        description="Inventário de uma pasta de auditoria: arquivos, DOI, licença, páginas, recortes e manifesto RAG.",
        inputSchema={
            "type": "object",
            "properties": {"pasta": {"type": "string"}},
            "required": ["pasta"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="oa_list_folders",
        description="Lista as pastas de auditoria existentes na base configurada.",
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


async def _handle(name: str, args: dict[str, Any]):
    if name == "oa_resolve":
        return _ok(await asyncio.to_thread(resolve_payload, str(args["doi"]), args.get("mailto")))
    if name == "oa_download":
        return _ok(
            await asyncio.to_thread(
                download_payload,
                str(args["doi"]),
                confirm=bool(args.get("confirm", False)),
                max_excerpts=int(args.get("max_excerpts", 8)),
                keywords=args.get("keywords") or (),
                lang=str(args.get("lang", "pt-BR")),
                mailto=args.get("mailto"),
            )
        )
    if name == "oa_query_rag":
        return _ok(await asyncio.to_thread(query_payload, str(args["pasta"]), str(args["query"]), int(args.get("k", 5))))
    if name == "oa_audit_status":
        return _ok(await asyncio.to_thread(status_payload, str(args["pasta"])))
    if name == "oa_list_folders":
        return _ok(await asyncio.to_thread(list_payload))
    return _mcp_error(f"Ferramenta desconhecida: {name}")


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    try:
        return await _handle(name, arguments or {})
    except KeyError as exc:
        return _mcp_error(f"argumento obrigatório ausente: {exc}")
    except Exception as exc:  # noqa: BLE001 — MCP devolve erro explícito
        return _mcp_error(f"{type(exc).__name__}: {exc}")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
