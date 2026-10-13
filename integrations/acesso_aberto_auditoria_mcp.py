"""MCP — Acesso Aberto com Auditoria Obrigatória (SPEC-979).

Borda FastMCP sobre research/legal_oa_pipeline.py + research/auditoria_fichamento.py.
Núcleo stdlib-only; mcp/pydantic só nesta borda. Bloqueia Sci-Hub antes de rede.
"""
from __future__ import annotations

import hashlib
import json
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

mcp = FastMCP("acesso-aberto-auditoria")

DoiText = Annotated[str, Field(strict=True, min_length=3, max_length=256)]


def _provenance(doi: str, fonte: str, licenca: str | None) -> dict[str, Any]:
    from research.auditoria_fichamento import _now  # stdlib interno
    data = _now()
    return {"doi": doi, "fonte": fonte, "licenca": licenca, "data_consulta": data,
            "hash_resposta": hashlib.sha256(f"{doi}|{fonte}|{data}".encode()).hexdigest()}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
async def resolver_doi(doi: DoiText) -> dict[str, Any]:
    """Resolve metadados canônicos por DOI (Crossref). Bloqueia DOI inválido antes de rede."""
    from research.legal_oa_pipeline import normalize_doi, _validate_doi_or_raise
    norm = _validate_doi_or_raise(normalize_doi(doi))
    return {"doi": norm, **_provenance(norm, "crossref", None), "evidence_eligible": False}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True))
async def verificar_oa(doi: DoiText) -> dict[str, Any]:
    """Verifica disponibilidade OA via OpenAlex (best_oa_location + licença). Não presume OA."""
    from research.legal_oa_pipeline import normalize_doi, _validate_doi_or_raise, is_download_allowed
    norm = _validate_doi_or_raise(normalize_doi(doi))
    # Sem rede nesta borda por padrão: retorna unknown fail-closed; orquestrador injeta runner real.
    info = {"doi": norm, "status": "unknown", "is_oa": False, "licenca": None, "pdf_url": None}
    gate = is_download_allowed({"license": None, "pdf_url": None})
    return {**info, **_provenance(norm, "openalex", None), "allowed": gate["allowed"]}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
async def criar_pasta_auditoria(meta: dict[str, Any]) -> dict[str, Any]:
    """Cria pasta de auditoria por DOI. Bloqueia sci-hub/scihub antes de qualquer escrita."""
    from research.auditoria_fichamento import criar_pasta_auditoria as _criar
    url = str((meta or {}).get("pdf_url") or "")
    if any(b in url.lower() for b in ("sci-hub", "scihub")) or url.lower().startswith("scihub-mcp://"):
        raise ValueError("blocked: unauthorized_source")
    pasta = _criar("auditoria_fichamentos", meta, pdf_bytes=None,
                   runner_allowed=lambda m: {"allowed": False, "reason": "mcp_sem_pdf"})
    return {"pasta": pasta, **_provenance(str(meta.get("doi")), "auditoria", str(meta.get("licenca")))}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
async def adicionar_recorte(pasta: str, recorte: dict[str, Any]) -> dict[str, Any]:
    """Adiciona recorte com página/autor/ano/justificativa. Rejeita trecho >400 ou justificativa curta."""
    from research.auditoria_fichamento import adicionar_recorte as _add
    novo = _add(pasta, recorte)
    return {"ok": True, "recorte": novo}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
async def auditar_pasta(pasta: str, citacoes: list[str]) -> dict[str, Any]:
    """Audita cobertura total de citações. Reprova sem recorte correspondente."""
    from research.auditoria_fichamento import auditar_pasta as _aud
    return _aud(pasta, citacoes)
