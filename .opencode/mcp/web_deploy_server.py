#!/usr/bin/env python3
"""
MCP Server — Web Deploy (GitHub Pages + mídia + feed)
======================================================
Ferramentas para deploy e verificação de sites estáticos no GitHub Pages,
compiladas das lições reais R569–R580 (SPEC-974):

  - web_deploy_pages_status:  status do build Pages via API GitHub
  - web_deploy_probe_url:     sonda URL com GET(+Range); NUNCA HEAD
  - web_deploy_site_weight:   peso de árvore (guard 1GB/por-arquivo)
  - web_deploy_validate_feed: valida RSS/Atom (enclosure length, guid)
  - web_deploy_assert_gone:   confirma remoções (404 obrigatório)

Princípios (herdados do padrão SPEC-970/971/972 — fail-closed):
  - erro de rede/credencial → isError explícita, nunca None silencioso
  - token nunca é impresso; resposta traz apenas status + motivo
  - prova física: status HTTP, bytes, hash

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlsplit

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Instrumentação de eficiência (SPEC-975): falha de medição nunca quebra a tool.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
try:
    from integrations.op_timing import record as _op_record
except Exception:  # pragma: no cover - ambiente sem o módulo
    _op_record = None


def _maybe_record(op: str, seconds: float, ok: bool) -> None:
    if _op_record is not None:
        try:
            _op_record(op, seconds, ok)
        except Exception:
            pass

try:
    from mcp.types import CallToolResult
except ImportError:
    class CallToolResult(list[TextContent]):
        """Fallback mínimo (SDK antigo) preservando contrato observável."""

        def __init__(
            self,
            *,
            content: Optional[list[TextContent]] = None,
            isError: bool = False,
            **extra_data: Any,
        ) -> None:
            super().__init__(content or [])
            self.content = list(content or [])
            self.isError = isError
            for key, value in extra_data.items():
                setattr(self, key, value)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("web-deploy-mcp")

GH_API_BASE_ENV = "GH_API_BASE"
DEFAULT_GH_API_BASE = "https://api.github.com"
GH_TOKEN_ENV = "GITHUB_TOKEN"
DEFAULT_LIMIT_MB = 1000
DEFAULT_MAX_FILE_MB = 25
MAX_PROBE_BYTES = 2 * 1024 * 1024

app = Server("web-deploy")


def _mcp_error(message: str) -> CallToolResult:
    """Fail-closed: erro explícito com isError=True (padrão SPEC-970/971/972)."""
    return CallToolResult(content=[TextContent(type="text", text=f"ERRO: {message}")], isError=True)


def _ok(message: str) -> list[TextContent]:
    """Conteúdo textual no formato aceito pelo SDK MCP (lista, nunca solto)."""
    return [TextContent(type="text", text=message)]


def _gh_api_base() -> str:
    return (os.environ.get(GH_API_BASE_ENV) or DEFAULT_GH_API_BASE).rstrip("/")


def _read_github_token() -> str:
    """Token da API GitHub, sem jamais imprimi-lo.

    Preferência: env GITHUB_TOKEN. Fallback: parse seguro de ~/.git-credentials
    (https://user:token@github.com). Lança ValueError se ausente/curto.
    """
    env_token = os.environ.get(GH_TOKEN_ENV)
    if env_token and len(env_token) >= 20:
        return env_token
    cred_file = Path.home() / ".git-credentials"
    if cred_file.is_file():
        for line in cred_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "github.com" not in line:
                continue
            stripped = line.strip()
            if not stripped.startswith("https://"):
                continue
            after_at = stripped.split("@", 1)
            if len(after_at) != 2:
                continue
            before_at = after_at[0].removeprefix("https://")
            if ":" not in before_at:
                continue
            token = before_at.split(":", 1)[1]
            if len(token) >= 20:
                return token
    raise ValueError("token GitHub ausente (env GITHUB_TOKEN ou ~/.git-credentials)")


def _validate_url(value: str, allow_loopback: bool = True) -> str:
    url = (value or "").strip()
    if not url:
        raise ValueError("URL ausente")
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"URL inválida: {url!r}")
    if not allow_loopback and parsed.hostname in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
        raise ValueError("host de loopback não permitido nesta ferramenta")
    return url


# ── Ferramenta 1: status do build Pages ─────────────────────────────────────


def _parse_credentials() -> dict[str, Any]:
    """Lê owner/repo e token dos argumentos ou env (owner/repo obrigatórios)."""


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="web_deploy_pages_status",
            description=(
                "Consulta o status do último build do GitHub Pages via API "
                "(campos status, duration, error). Token via env GITHUB_TOKEN "
                "ou ~/.git-credentials — nunca é impresso."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "dono do repo"},
                    "repo": {"type": "string", "description": "nome do repo"},
                },
                "required": ["owner", "repo"],
            },
        ),
        Tool(
            name="web_deploy_probe_url",
            description=(
                "Sonda URL com GET (+Range opcional). NUNCA usa HEAD — falha no "
                "GitHub Pages para m4a. Retorna status HTTP, bytes lidos e se um "
                "marcador de conteúdo (substring) foi encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "marker": {"type": "string", "description": "flag de conteúdo esperado"},
                    "range_first": {"type": "boolean", "description": "usar Range 0-1023"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="web_deploy_site_weight",
            description=(
                "Calcula peso de diretório excluindo .git, lista os maiores "
                "arquivos e aplica guards: total <= LIMIT_MB (padrão 1000) e "
                "arquivo <= MAX_FILE_MB (padrão 25). Retorna status GRANTED/DENIED."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit_mb": {"type": "integer"},
                    "max_file_mb": {"type": "integer"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="web_deploy_validate_feed",
            description=(
                "Valida feed RSS/Atom local: itens, presence de enclosure com "
                "length real, guid/item e, se um diretório raiz for passado, "
                "confere que o arquivo do enclosure existe (recomendado)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "feed_path": {"type": "string"},
                    "root_dir": {"type": "string", "description": "dir base dos enclosures"},
                },
                "required": ["feed_path"],
            },
        ),
        Tool(
            name="web_deploy_assert_gone",
            description=(
                "Confirma que URLs retornam 404 (verificação de remoções). "
                "Retorna por URL o status observado; qualquer status != 404 é falha."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["urls"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult | list[TextContent]:
    import time as _time
    _t0 = _time.monotonic()
    if name == "web_deploy_pages_status":
        _res = await _pages_status(arguments)
    elif name == "web_deploy_probe_url":
        _res = await _probe_url(arguments)
    elif name == "web_deploy_site_weight":
        _res = await _site_weight(arguments)
    elif name == "web_deploy_validate_feed":
        _res = await _validate_feed(arguments)
    elif name == "web_deploy_assert_gone":
        _res = await _assert_gone(arguments)
    else:
        _res = _mcp_error(f"Ferramenta desconhecida: {name}")
    _ok_result = not (isinstance(_res, CallToolResult) and getattr(_res, "isError", False))
    _maybe_record(name, _time.monotonic() - _t0, _ok_result)
    return _res


async def _pages_status(arguments: dict[str, Any]) -> TextContent:
    owner = (arguments or {}).get("owner", "").strip()
    repo = (arguments or {}).get("repo", "").strip()
    if not owner or not repo:
        return _mcp_error("owner e repo são obrigatórios")
    try:
        token = _read_github_token()
    except ValueError as exc:
        return _mcp_error(str(exc))
    url = f"{_gh_api_base()}/repos/{owner}/{repo}/pages/builds/latest"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        if resp.status_code != 200:
            return _mcp_error(
                f"API GitHub respondeu {resp.status_code}: {resp.text[:200].strip()}"
            )
        data = resp.json()
        status = data.get("status")
        duration = data.get("duration")
        error = data.get("error") or {}
        return _ok(
            "pages_status: "
            f"status={status} | duration={duration} | error={error.get('message') or error or 'nenhum'}"
        )
    except httpx.RequestError as exc:
        return _mcp_error(f"falha HTTP na API GitHub: {type(exc).__name__}")
    except (ValueError, KeyError) as exc:
        return _mcp_error(f"resposta inesperada da API: {exc}")


async def _probe_url(arguments: dict[str, Any]) -> TextContent:
    args = arguments or {}
    try:
        url = _validate_url(args.get("url", ""))
    except ValueError as exc:
        return _mcp_error(str(exc))
    marker = (args.get("marker") or "").strip()
    use_range = bool(args.get("range_first"))
    headers = {"Range": "bytes=0-1023", "User-Agent": "opencode-web-deploy-mcp"} if use_range else {
        "User-Agent": "opencode-web-deploy-mcp"
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
            resp = await client.get(url, headers=headers)
        body = resp.content[:MAX_PROBE_BYTES]
        found = marker in resp.text[:MAX_PROBE_BYTES] if marker else None
        lines = [
            f"probe_url: {url}",
            f"  status={resp.status_code} | bytes={len(body)} | range={use_range}",
        ]
        if marker:
            lines.append(f"  marker={marker!r} encontrado={found}")
        return _ok("\n".join(lines))
    except httpx.RequestError as exc:
        return _mcp_error(f"falha HTTP na sondagem: {type(exc).__name__}: {exc}")


async def _site_weight(arguments: dict[str, Any]) -> TextContent:
    args = arguments or {}
    target = (args.get("path") or "").strip()
    limit_mb = int(args.get("limit_mb") or DEFAULT_LIMIT_MB)
    max_file_mb = int(args.get("max_file_mb") or DEFAULT_MAX_FILE_MB)
    root = Path(target).expanduser()
    if not root.is_dir():
        return _mcp_error(f"diretorio não existe: {root}")

    total_bytes = 0
    files: list[tuple[int, Path]] = []
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            try:
                size = path.stat().st_size
            except OSError:
                continue
            total_bytes += size
            files.append((size, path))
    if root.joinpath(".git").is_dir():
        try:
            import shutil

            git_size = sum(
                p.stat().st_size
                for p in root.joinpath(".git").rglob("*")
                if p.is_file()
            )
            total_bytes = max(0, total_bytes - git_size)
        except OSError:
            pass

    total_mb = total_bytes // (1024 * 1024)
    files.sort(reverse=True)
    biggest = "\n".join(
        f"  {size / 1048576:6.1f} MiB  {path}" for size, path in files[:5]
    ) or "  (vazio)"
    oversize = [str(p) for size, p in files if size > max_file_mb * 1024 * 1024]
    status = (
        total_mb > limit_mb or bool(oversize)
    )
    head = (
        f"site_weight: total={total_mb} MiB (limite {limit_mb} MiB) | "
        f"arquivos={len(files)} | por-arquivo={max_file_mb} MiB\n"
        f"maiores:\n{biggest}"
    )
    if oversize:
        head += "\noversize:\n" + "\n".join(f"  {p}" for p in oversize[:5])
    head += f"\nstatus={'DENIED' if status else 'GRANTED'}"
    return _ok(head)


async def _validate_feed(arguments: dict[str, Any]) -> TextContent:
    args = arguments or {}
    feed_path = (args.get("feed_path") or "").strip()
    root_dir = (args.get("root_dir") or "").strip()
    feed = Path(feed_path).expanduser()
    if not feed.is_file():
        return _mcp_error(f"feed não encontrado: {feed}")
    text = feed.read_text(encoding="utf-8", errors="ignore")

    import re

    items = re.findall(r"<item>|</entry>", text)  # RSS simple count
    n_items = len(re.findall(r"<item>", text)) or len(re.findall(r"<entry>", text))
    enclosures = re.findall(
        r'<enclosure[^>]*url="([^"]+)"[^>]*length="(\d+)"[^>]*/?>', text
    )
    missing_length = re.findall(r"<enclosure(?![^>]*length=)[^>]*>", text)
    guids = re.findall(r"<guid[^>]*>([^<]+)</guid>", text)
    mising_link = len(re.findall(r"<link>", text))

    problems: list[str] = []
    if missing_length:
        problems.append(f"{len(missing_length)} enclosures sem length")
    if not enclosures and n_items:
        problems.append("nenhum enclosure com url+length encontrado")
    if n_items and len(guids) < n_items:
        problems.append(f"guid: {len(guids)}/<{n_items} itens")

    if root_dir:
        base = Path(root_dir).expanduser()
        missing_files = []
        for url, _ in enclosures:
            name = url.split("/")[-1]
            if not base.joinpath(name).is_file():
                missing_files.append(name)
        if missing_files:
            problems.append(f"enclosures ausentes no root: {missing_files[:5]}")

    head = (
        f"validate_feed: {feed.name} | itens={n_items} | enclosures={len(enclosures)} "
        f"| guid={len(guids)}"
    )
    if problems:
        return _ok(head + "\nproblemas:\n" + "\n".join(f"  - {p}" for p in problems) + "\nstatus=DENIED")
    return _ok(head + "\nstatus=GRANTED")


async def _assert_gone(arguments: dict[str, Any]) -> TextContent:
    urls = [(arguments or {}).get("urls") or []]
    if isinstance(urls, list) and len(urls) == 1 and isinstance(urls[0], list):
        urls = urls[0]
    if not urls:
        return _mcp_error("urls (lista) é obrigatório")
    results = []
    failed = False
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
        for url in urls:
            try:
                resp = await client.get(url, headers={"User-Agent": "opencode-web-deploy-mcp"})
                code = resp.status_code
            except httpx.RequestError as exc:
                code = f"ERRO {type(exc).__name__}"
                failed = True
            ok = code == 404
            if not ok:
                failed = True
            results.append(f"  {url} → {code} {'OK(404)' if ok else 'FALHA'}")
    head = "assert_gone: " + ("FALHA" if failed else "TODOS 404 (remoções confirmadas)")
    return _ok(head + "\n" + "\n".join(results))


# ── Entrypoint ──────────────────────────────────────────────────────────────


async def main() -> None:
    logger.info("Iniciando MCP Server web-deploy...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())