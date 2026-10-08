"""Prova local R657: PDFs reais + MCP stdio, sem executar modelos.

Uso no checkout: .venv/bin/python scripts/verify_book_library.py --index
Somente metadados/citações vão ao relatório; trechos integrais ficam no cache.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _payload(result: Any) -> dict[str, Any]:
    if getattr(result, "isError", False):
        raise RuntimeError("MCP retornou erro na consulta de evidências.")
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured
    for block in result.content:
        if getattr(block, "type", None) == "text":
            return json.loads(block.text)
    raise RuntimeError("MCP não retornou dados JSON.")


def _require(condition: bool, message: str) -> None:
    """Gates de evidência permanecem ativos mesmo com Python -O."""
    if not condition:
        raise RuntimeError(message)


async def probe(index: bool = False) -> dict[str, Any]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    if index:
        orch.library_index()
    inventory = orch.library_status()
    if inventory.get("books", 0) < 2:
        raise RuntimeError("A prova real requer pelo menos dois livros técnicos indexados.")
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "integrations.ecosystem_mcp"],
        cwd=str(ROOT),
    )
    checks: dict[str, Any] = {}
    citations = []
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            checks["protocol_version"] = initialized.protocolVersion
            checks["server"] = initialized.serverInfo.name
            tools = (await session.list_tools()).tools
            checks["tools"] = sorted(tool.name for tool in tools)
            _require("ecosystem_library_search" in checks["tools"], "Tool de busca ausente.")
            search_tool = next(tool for tool in tools if tool.name == "ecosystem_library_search")
            _require(search_tool.annotations.readOnlyHint is True, "Busca não declarou somente leitura.")
            _require(search_tool.inputSchema["properties"]["top_k"]["minimum"] == 1, "Limite mínimo inválido.")
            _require(search_tool.inputSchema["properties"]["top_k"]["maximum"] == 10, "Limite máximo inválido.")
            checks["read_only_and_bounded_schema"] = True
            resources = (await session.list_resources()).resources
            _require("ecosystem://books/catalog" in {str(item.uri) for item in resources}, "Catálogo ausente.")
            templates = (await session.list_resource_templates()).resourceTemplates
            _require(any(item.uriTemplate == "ecosystem://books/{book_id}/pages/{page}" for item in templates),
                     "Template de páginas ausente.")
            catalog_resource = await session.read_resource("ecosystem://books/catalog")
            catalog = json.loads(catalog_resource.contents[0].text)
            _require(catalog["books"] == inventory["books"], "Inventários dos processos divergem.")
            checks["catalog_and_page_template"] = True
            for query, expected in [("ambiguidade autoexplicativos resources", "MCP"),
                                    ("independência documento inteiro split", "Fine-Tuning")]:
                result = _payload(await session.call_tool(
                    "ecosystem_library_search", {"query": query, "top_k": 5}
                ))
                _require(result["abstained"] is False, "Consulta bibliográfica sem evidência.")
                evidence = result["evidence"]
                hit = next(item for item in evidence if expected in item["file"])
                actual_digest = hashlib.sha256((ROOT / "biblioteca ai" / hit["file"]).read_bytes()).hexdigest()
                _require(hit["source_sha256"] == actual_digest == hit["book_id"], "Hash da fonte divergente.")
                page_resource = await session.read_resource(hit["uri"])
                page = json.loads(page_resource.contents[0].text)
                _require(page["page"] == hit["page"], "Página física divergente.")
                _require(page["page_sha256"] == hit["page_sha256"], "Hash da página divergente entre interfaces.")
                _require(hashlib.sha256(page["text"].encode()).hexdigest() == hit["page_sha256"],
                         "Hash não corresponde ao texto da página.")
                citations.append({"query": query, "file": hit["file"], "page": hit["page"],
                                  "source_sha256": hit["source_sha256"],
                                  "page_sha256": hit["page_sha256"], "uri": hit["uri"]})
            checks["actual_pdf_hash_and_page_read"] = True
            unrelated = _payload(await session.call_tool(
                "ecosystem_library_search", {"query": "zxqvpt inexistente", "top_k": 3}
            ))
            _require(unrelated["abstained"] is True and not unrelated["evidence"],
                     "Consulta sem suporte não se absteve.")
            checks["unsupported_query_abstains"] = True
            invalid = await session.call_tool("ecosystem_library_search", {"query": "MCP", "top_k": 0})
            boolean = await session.call_tool("ecosystem_library_search", {"query": "MCP", "top_k": True})
            _require(invalid.isError and boolean.isError, "MCP aceitou limites inválidos.")
            checks["invalid_limits_rejected_over_protocol"] = True
            prompt_names = {prompt.name for prompt in (await session.list_prompts()).prompts}
            _require("ecosystem_book_review" in prompt_names, "Prompt de revisão ausente.")
            prompt = await session.get_prompt("ecosystem_book_review", {
                "task": "Revisar a biblioteca técnica do Core", "topic": "resources metadados"
            })
            _require(len(prompt.messages) == 3, "Estrutura inesperada no prompt.")
            _require("não confiáveis" in prompt.messages[0].content.text,
                     "Prompt não demarca dados não confiáveis.")
            checks["review_prompt_returns_reference_data"] = True
    return {"status": "passed", "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "evidence_kind": "actual_local_pdf_and_mcp_protocol",
            "model_inference_executed": False, "training_executed": False,
            "inventory": inventory, "checks": checks, "citations": citations}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", action="store_true", help="Atualizar explicitamente o índice antes da prova.")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/evidence/R657-library-real.json")
    args = parser.parse_args()
    report = asyncio.run(probe(index=args.index))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(args.output),
                      "checks": report["checks"], "citations": report["citations"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
