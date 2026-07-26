#!/usr/bin/env python3
"""
PyPI Search MCP Server v1.1.0
==============================
Servidor MCP que expõe capacidades de busca, recomendação e descoberta de
bibliotecas Python no PyPI como ferramentas utilizáveis pelo ecossistema
OpenCode.

Protocolo: MCP stdio (JSON-RPC 2.0)
Versão do protocolo: ecoa a versão solicitada pelo cliente (default 2024-11-05)

Ferramentas expostas:
  - pypi_search           Busca pacotes no PyPI por termo
  - pypi_exact_lookup     Detalhes exatos de um pacote específico
  - pypi_recommend        Recomenda bibliotecas para um tipo de tarefa
  - pypi_index_status     Status do índice local

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import logging
import sys
import time
import traceback
from pathlib import Path
from typing import Any

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.tooling.pypi_search import (
    search as pypi_search_func,
    recommend_for_task,
    CATEGORY_KEYWORDS,
    TASK_LIBRARIES,
    format_output,
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PyPI-MCP] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("pypi-mcp")


# ============================================================
# Implementação do Protocolo MCP (stdio-based)
# ============================================================

class PyPiMCPServer:
    """
    Servidor MCP minimalista via stdio.
    Implementa o protocolo JSON-RPC 2.0 compatível com MCP.
    """

    def __init__(self):
        self.request_id = 0
        self.capabilities = {
            "tools": [
                {
                    "name": "pypi_search",
                    "description": "Busca pacotes no PyPI por termo de busca. "
                                   "Retorna tabela comparativa com scores de 0-10 "
                                   "nos critérios: saúde, popularidade, qualidade técnica, "
                                   "compatibilidade e afinidade com o ecossistema.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Termo de busca (ex: 'scihub paper download', 'async http')",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Máximo de resultados (1-25, padrão 10)",
                                "default": 10,
                            },
                            "category": {
                                "type": "string",
                                "description": "Categoria para refinar busca: "
                                               f"{list(CATEGORY_KEYWORDS.keys())}",
                                "default": "",
                            },
                            "no_enrich": {
                                "type": "boolean",
                                "description": "Se true, não enriquece com JSON API (mais rápido)",
                                "default": False,
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "pypi_exact_lookup",
                    "description": "Obtém detalhes completos de um pacote PyPI específico "
                                   "pelo nome exato. Inclui versão, licença, dependências, "
                                   "classificadores e score.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "package": {
                                "type": "string",
                                "description": "Nome exato do pacote (ex: 'scihub-cli', 'requests')",
                            },
                        },
                        "required": ["package"],
                    },
                },
                {
                    "name": "pypi_recommend",
                    "description": "Recomenda as melhores bibliotecas Python para um tipo "
                                   "específico de tarefa. Opções: download_papers, web_scraping, "
                                   "data_analysis, cli_tools, pdf_generation.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_type": {
                                "type": "string",
                                "description": "Tipo de tarefa",
                                "enum": list(TASK_LIBRARIES.keys()),
                            },
                        },
                        "required": ["task_type"],
                    },
                },
                {
                    "name": "pypi_index_status",
                    "description": "Retorna o status do índice local de pacotes PyPI: "
                                   "quantos pacotes indexados, idade do cache, etc.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                    },
                },
            ],
        }

    def handle_request(self, request: dict) -> dict | None:
        """Processa uma requisição JSON-RPC e retorna a resposta."""
        method = request.get("method", "")
        params = request.get("params", {}) or {}
        req_id = request.get("id")

        logger.info("Requisição: %s %s", method, params)

        try:
            if method == "initialize":
                return self._handle_initialize(params, req_id)
            elif method == "ping":
                return self._make_response(req_id, {})
            elif method == "tools/list":
                return self._make_response(
                    req_id, {"tools": self.capabilities["tools"]}
                )
            elif method == "tools/call":
                return self._handle_call_tool(params, req_id)
            elif method == "shutdown":
                logger.info("Shutdown solicitado")
                return self._make_response(req_id, {"status": "shutting_down"})
            elif method in ("notifications/initialized",):
                return None  # No response needed for notifications
            else:
                return self._make_error_response(
                    req_id, -32601, f"Método não encontrado: {method}"
                )
        except Exception as exc:
            logger.error("Erro no método %s: %s", method, exc)
            logger.error(traceback.format_exc())
            return self._make_error_response(req_id, -32603, str(exc))

    # Versão padrão do protocolo MCP (ecoada de volta ao cliente)
    MCP_PROTOCOL_VERSION = "2024-11-05"

    def _handle_initialize(self, params: dict, req_id: int | None) -> dict:
        """Lida com initialize handshake.

        Ecore a versão do protocolo solicitada pelo cliente para garantir
        compatibilidade com diferentes versões do protocolo MCP.
        """
        protocol_version = params.get("protocolVersion", self.MCP_PROTOCOL_VERSION)
        return self._make_response(req_id, {
            "protocolVersion": protocol_version,
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "pypi-search-mcp",
                "version": "1.1.0",
            },
        })

    def _handle_call_tool(self, params: dict, req_id: int | None) -> dict:
        """Executa uma ferramenta e retorna o resultado.

        Segue o formato MCP tools/call:
          - Sucesso: {content: [{type: "text", text: ...}]}
          - Erro:    {content: [...], isError: true}
        """
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        if not tool_name:
            return self._tool_error_result(req_id, "Nome da ferramenta é obrigatório")

        if tool_name == "pypi_search":
            return self._tool_search(tool_args, req_id)
        elif tool_name == "pypi_exact_lookup":
            return self._tool_exact_lookup(tool_args, req_id)
        elif tool_name == "pypi_recommend":
            return self._tool_recommend(tool_args, req_id)
        elif tool_name == "pypi_index_status":
            return self._tool_index_status(tool_args, req_id)
        else:
            return self._tool_error_result(
                req_id, f"Ferramenta desconhecida: {tool_name}"
            )

    def _tool_result(self, req_id: int | None, data: Any) -> dict:
        """Constrói resultado de tool no formato MCP padrão."""
        return self._make_response(req_id, {
            "content": [
                {"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}
            ]
        })

    def _tool_error_result(self, req_id: int | None, message: str) -> dict:
        """Constrói resultado de erro de tool com isError=true."""
        return self._make_response(req_id, {
            "isError": True,
            "content": [
                {"type": "text", "text": message}
            ]
        })

    def _tool_search(self, args: dict, req_id: int | None) -> dict:
        """Executa busca no PyPI."""
        query = args.get("query", "")
        limit = min(int(args.get("limit", 10)), 25)
        category = args.get("category", "")
        no_enrich = args.get("no_enrich", False)

        if not query:
            return self._tool_error_result(req_id, "Parâmetro 'query' é obrigatório")

        result = pypi_search_func(
            query=query,
            limit=limit,
            enrich=not no_enrich,
            use_cache=True,
            category=category,
        )

        packages_data = [
            {
                "name": p.name,
                "version": p.version,
                "summary": p.summary[:300] if p.summary else "",
                "score": round(p.score, 2),
                "scores": {k: round(v, 1) for k, v in p.scores.items()},
                "license": p.license,
                "requires_python": p.requires_python,
                "last_upload": p.last_upload,
                "release_url": p.release_url,
            }
            for p in result.packages
        ]

        return self._tool_result(req_id, {
            "query": result.query,
            "total_found": result.total_found,
            "displayed": len(result.packages),
            "elapsed_ms": result.elapsed_ms,
            "source": result.source,
            "error": result.error,
            "packages": packages_data,
            "markdown": format_output(result),
        })

    def _tool_exact_lookup(self, args: dict, req_id: int | None) -> dict:
        """Busca detalhes exatos de um pacote."""
        package = args.get("package", "")

        if not package:
            return self._tool_error_result(req_id, "Parâmetro 'package' é obrigatório")

        result = pypi_search_func(
            query=package,
            limit=1,
            enrich=True,
            exact=True,
        )

        if not result.packages:
            return self._tool_result(req_id, {
                "found": False,
                "package": package,
                "error": f"Pacote '{package}' não encontrado",
            })

        pkg = result.packages[0]
        return self._tool_result(req_id, {
            "found": True,
            "name": pkg.name,
            "version": pkg.version,
            "summary": pkg.summary,
            "description": pkg.description[:500],
            "author": pkg.author,
            "author_email": pkg.author_email,
            "license": pkg.license,
            "home_page": pkg.home_page,
            "project_urls": pkg.project_urls,
            "requires_python": pkg.requires_python,
            "requires_dist": pkg.requires_dist,
            "classifiers": pkg.classifiers,
            "keywords": pkg.keywords,
            "last_upload": pkg.last_upload,
            "release_url": pkg.release_url,
            "score": round(pkg.score, 2),
            "scores": {k: round(v, 1) for k, v in pkg.scores.items()},
            "install_command": f"pip install {pkg.name}",
        })

    def _tool_recommend(self, args: dict, req_id: int | None) -> dict:
        """Recomenda bibliotecas para um tipo de tarefa."""
        task_type = args.get("task_type", "")

        if not task_type:
            return self._tool_error_result(
                req_id,
                f"Parâmetro 'task_type' é obrigatório. Opções: {list(TASK_LIBRARIES.keys())}"
            )

        recs = recommend_for_task(task_type)

        if not recs.get("found"):
            return self._tool_error_result(req_id, recs.get("message", ""))

        recommendations = []
        for r in recs.get("recommendations", []):
            recommendations.append({
                "name": r["name"],
                "version": r.get("version", ""),
                "summary": r.get("summary", "")[:200],
                "score": r["score"],
                "install_command": r["install"],
                "url": r["url"],
            })

        return self._tool_result(req_id, {
            "task_type": task_type,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
        })

    def _tool_index_status(self, args: dict, req_id: int | None) -> dict:
        """Status do índice PyPI local."""
        from skills.tooling.pypi_search import PACKAGE_INDEX_CACHE, INDEX_TTL_SECONDS

        status = {
            "index_exists": PACKAGE_INDEX_CACHE.exists(),
        }
        if PACKAGE_INDEX_CACHE.exists():
            import gzip
            mtime = PACKAGE_INDEX_CACHE.stat().st_mtime
            age = time.time() - mtime
            status["age_seconds"] = int(age)
            status["age_days"] = round(age / 86400, 1)
            status["ttl_seconds"] = INDEX_TTL_SECONDS
            status["expired"] = age > INDEX_TTL_SECONDS
            try:
                with gzip.open(PACKAGE_INDEX_CACHE, "rt", encoding="utf-8") as f:
                    index = json.load(f)
                status["total_packages"] = len(index)
            except Exception:
                status["total_packages"] = "unknown (corrupted?)"
        else:
            status["total_packages"] = 0
            status["age_seconds"] = 0
            status["age_days"] = 0
            status["expired"] = True

        return self._tool_result(req_id, status)

    def _make_response(self, req_id: int | None, result: Any) -> dict:
        """Constrói resposta JSON-RPC de sucesso."""
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def _make_error_response(self, req_id: int | None, code: int, message: str) -> dict:
        """Constrói resposta JSON-RPC de erro."""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }

    def run(self):
        """Loop principal: lê requisições do stdin, escreve respostas no stdout."""
        logger.info("PyPI MCP Server iniciado (stdio)")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError as exc:
                logger.error("JSON inválido: %s", exc)
                error_resp = self._make_error_response(None, -32700, f"Parse error: {exc}")
                sys.stdout.write(json.dumps(error_resp) + "\n")
                sys.stdout.flush()
            except KeyboardInterrupt:
                break
            except Exception as exc:
                logger.error("Erro fatal: %s", exc)
                logger.error(traceback.format_exc())
                error_resp = self._make_error_response(None, -32603, f"Internal error: {exc}")
                try:
                    sys.stdout.write(json.dumps(error_resp) + "\n")
                    sys.stdout.flush()
                except Exception:
                    pass


def main():
    server = PyPiMCPServer()
    server.run()


if __name__ == "__main__":
    main()
