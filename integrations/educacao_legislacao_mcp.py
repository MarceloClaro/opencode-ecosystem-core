"""MCP de consulta on-demand a um catálogo restrito de fontes legais oficiais.

O servidor aceita apenas identificadores predefinidos, faz GET sem gravar
conteúdo e não infere vigência, revogação ou sucessão a partir do HTTP status.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


MAX_BYTES = 2_000_000
MAX_CHARS = 12_000
MAX_TIMEOUT_SECONDS = 15
ALLOWED_HOSTS = frozenset({"www.planalto.gov.br", "planalto.gov.br", "www2.al.ce.gov.br"})


def _checked_integer(value: int, name: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} deve estar entre {minimum} e {maximum}.")
    return value

LAW_SOURCES: dict[str, dict[str, Any]] = {
    "eca": {
        "title": "Estatuto da Criança e do Adolescente",
        "citation": "Lei nº 8.069/1990",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/leis/l8069.htm",
        "current_validity": "not_assessed",
    },
    "ldb": {
        "title": "Lei de Diretrizes e Bases da Educação Nacional",
        "citation": "Lei nº 9.394/1996",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/leis/l9394.htm",
        "current_validity": "not_assessed",
    },
    "lbi": {
        "title": "Lei Brasileira de Inclusão da Pessoa com Deficiência",
        "citation": "Lei nº 13.146/2015",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm",
        "current_validity": "not_assessed",
    },
    "pne_2014": {
        "title": "Plano Nacional de Educação (texto-base histórico)",
        "citation": "Lei nº 13.005/2014",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l13005.htm",
        "declared_period": "2014–2024",
        "status_note": "Extensão/sucessor precisa de verificação oficial.",
        "current_validity": "not_verified",
    },
    "pee_ce_2016": {
        "title": "Plano Estadual de Educação do Ceará (texto-base histórico)",
        "citation": "Lei estadual nº 16.025/2016",
        "jurisdiction": "Ceará",
        "url": "https://www2.al.ce.gov.br/legislativo/legislacao5/leis2016/16025.htm",
        "declared_period": "2016–2024",
        "status_note": "Extensão/sucessor precisa de verificação oficial.",
        "current_validity": "not_verified",
    },
    "libras_2002": {
        "title": "Língua Brasileira de Sinais (Libras)",
        "citation": "Lei nº 10.436/2002",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm",
        "current_validity": "not_assessed",
    },
    "acessibilidade_2000": {
        "title": "Acessibilidade",
        "citation": "Lei nº 10.098/2000",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/leis/l10098.htm",
        "current_validity": "not_assessed",
    },
    "autismo_2012": {
        "title": "Política Nacional de Proteção dos Direitos da Pessoa com TEA",
        "citation": "Lei nº 12.764/2012",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12764.htm",
        "current_validity": "not_assessed",
    },
    "convencao_deficiencia_2009": {
        "title": "Convenção sobre os Direitos das Pessoas com Deficiência",
        "citation": "Decreto nº 6.949/2009",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/decreto/d6949.htm",
        "current_validity": "not_assessed",
    },
    "educacao_bilingue_2021": {
        "title": "Educação bilíngue de surdos (alteração da LDB)",
        "citation": "Lei nº 14.191/2021",
        "jurisdiction": "federal",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14191.htm",
        "current_validity": "not_assessed",
    },
}


class _TextExtractor(HTMLParser):
    _BLOCKED = {"script", "style", "noscript", "svg"}
    _BLOCKS = {"p", "div", "section", "article", "h1", "h2", "h3", "li", "br", "tr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._BLOCKED:
            self._skip_depth += 1
        elif self._skip_depth == 0 and tag in self._BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._BLOCKED and self._skip_depth:
            self._skip_depth -= 1
        elif self._skip_depth == 0 and tag in self._BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self.parts.append(data)

    def text(self) -> str:
        return "\n".join(line.strip() for line in "".join(self.parts).splitlines() if line.strip())


class _AllowlistedRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError("Redirecionamento fora da allowlist oficial bloqueado.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch_official(url: str, *, max_bytes: int, timeout_seconds: int) -> dict[str, Any]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("URL não pertence à allowlist de fontes oficiais.")
    opener = build_opener(_AllowlistedRedirects())
    request = Request(url, method="GET", headers={"User-Agent": "OpenCode-Education-Law-MCP/1.0", "Accept": "text/html"})
    try:
        response = opener.open(request, timeout=timeout_seconds)
    except HTTPError as exc:
        body = exc.read(max_bytes + 1)
        return {"status_code": exc.code, "final_url": exc.geturl(), "body": body[:max_bytes], "truncated": len(body) > max_bytes}
    except (URLError, TimeoutError, OSError) as exc:
        return {"status_code": 0, "final_url": url, "body": b"", "truncated": False, "transport_error": type(exc).__name__}

    with response:
        final_url = response.geturl()
        final = urlsplit(final_url)
        if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("URL final fora da allowlist oficial.")
        body = response.read(max_bytes + 1)
        return {"status_code": response.getcode(), "final_url": final_url,
                "body": body[:max_bytes], "truncated": len(body) > max_bytes}


class LawSourceRegistry:
    """Catálogo seed e GET sob demanda, sempre por ID fixo e origem oficial."""

    @staticmethod
    def list_sources() -> dict[str, Any]:
        sources = [dict(law_id=law_id, **metadata) for law_id, metadata in LAW_SOURCES.items()]
        return {
            "status": "partial",
            "scope_complete": False,
            "scope_note": "Catálogo inicial não exaustivo; inclui normas indicadas pelo usuário e referências diretamente relacionadas.",
            "sources": sources,
            "current_validity_is_assessed": False,
        }

    def fetch_source(
        self,
        law_id: str,
        *,
        start: int = 0,
        max_chars: int = MAX_CHARS,
        fetcher=None,
    ) -> dict[str, Any]:
        if not isinstance(law_id, str) or law_id not in LAW_SOURCES:
            raise ValueError("law_id não pertence ao catálogo fechado.")
        start = _checked_integer(start, "start", minimum=0, maximum=1_000_000)
        max_chars = _checked_integer(max_chars, "max_chars", minimum=100, maximum=MAX_CHARS)
        source = LAW_SOURCES[law_id]
        transport = fetcher or _fetch_official
        response = transport(source["url"], max_bytes=MAX_BYTES, timeout_seconds=MAX_TIMEOUT_SECONDS)
        final_url = response.get("final_url", "")
        final = urlsplit(final_url)
        if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("URL final fora da allowlist oficial.")
        body = response.get("body", b"")
        if not isinstance(body, bytes):
            raise ValueError("Resposta de fonte oficial inválida.")
        body_sha256 = sha256(body).hexdigest()
        status_code = response.get("status_code", 0)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        if not 200 <= status_code < 300:
            return {
                "status": "source_unavailable",
                "law_id": law_id,
                "title": source["title"],
                "citation": source["citation"],
                "source_url": source["url"],
                "final_url": final_url,
                "http_status": status_code,
                "retrieved_at": retrieved_at,
                "content_sha256": body_sha256,
                "current_validity": "not_verified",
                "legal_interpretation_performed": False,
                "transport_error": response.get("transport_error"),
            }
        parser = _TextExtractor()
        parser.feed(body.decode("utf-8", errors="replace"))
        text = parser.text()
        excerpt = text[start:start + max_chars]
        return {
            "status": "retrieved",
            "law_id": law_id,
            "title": source["title"],
            "citation": source["citation"],
            "source_url": source["url"],
            "final_url": final_url,
            "http_status": status_code,
            "retrieved_at": retrieved_at,
            "content_sha256": body_sha256,
            "text": excerpt,
            "start": start,
            "total_characters": len(text),
            "truncated": bool(response.get("truncated")) or start + len(excerpt) < len(text),
            "current_validity": "not_determined_by_fetch",
            "legal_interpretation_performed": False,
        }


def create_server(registry: LawSourceRegistry | None = None) -> FastMCP:
    registry = registry or LawSourceRegistry()
    server = FastMCP("educacao-legislacao")
    local_read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    official_get = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True)

    @server.tool(name="list_sources", annotations=local_read)
    def list_sources() -> dict:
        """Lista o catálogo seed de normas; não declara sua exaustividade ou vigência."""
        return registry.list_sources()

    @server.tool(name="fetch_source", annotations=official_get)
    def fetch_source(law_id: str, start: int = 0, max_chars: int = MAX_CHARS) -> dict:
        """Faz GET sob demanda de um ID allowlisted; não baixa arquivo nem decide vigência."""
        return registry.fetch_source(law_id, start=start, max_chars=max_chars)

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
