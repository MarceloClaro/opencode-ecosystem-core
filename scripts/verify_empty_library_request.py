"""R677: guarda Python real, MCP em processo novo e contraprovas em memória.

Não modifica fontes, não indexa livros e não executa modelos. Os mutantes são
carregados em memória; o relatório distingue contraprovas de operações reais.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def empty_receipt(library_class, directory: Path) -> dict:
    library = library_class(directory / "absent-books", directory / "absent.sqlite3")

    def forbidden_snapshot():
        raise RuntimeError("Consulta vazia tentou acessar inventário/fontes.")

    library._snapshot = forbidden_snapshot
    result = library.query("")
    require(result.get("status") == "invalid_request", "Consulta vazia apresentada como válida.")
    require(result.get("reason_code") == "empty_query", "Motivo de abstenção ausente.")
    require(result.get("abstained") is True and result.get("evidence") == []
            and result.get("evidence_count") == 0, "Evidência fabricada para entrada vazia.")
    for flag in ("retrieval_executed", "model_inference_executed", "training_executed"):
        require(result.get(flag) is False, "Estado de execução incorreto: " + flag)
    require("index_status" not in result, "Inventário apresentado sem leitura.")
    require(not library.source_dir.exists() and not library.index_path.exists(), "Arquivos criados.")
    return result


async def protocol_receipts() -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.shared.exceptions import McpError

    parameters = StdioServerParameters(command=sys.executable,
        args=["-m", "integrations.ecosystem_mcp"], cwd=str(ROOT))
    cases = []
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            for name, arguments in [
                ("prompt_blank", {"task": "", "topic": ""}),
                ("prompt_whitespace", {"task": " \t", "topic": "MCP"}),
                ("prompt_missing_task", {"topic": "MCP"}),
                ("prompt_missing_topic", {"task": "Revisar"}),
                ("prompt_missing_both", {}),
            ]:
                rejected = False
                try:
                    await session.get_prompt("ecosystem_book_review", arguments)
                except McpError:
                    rejected = True
                require(rejected, "MCP aceitou " + name)
                cases.append({"case": name, "rejected": rejected})
            for name, arguments in [
                ("search_blank", {"query": ""}),
                ("search_whitespace", {"query": " \t"}),
                ("search_missing", {}),
            ]:
                result = await session.call_tool("ecosystem_library_search", arguments)
                require(result.isError, "MCP aceitou " + name)
                cases.append({"case": name, "rejected": result.isError})
    return {"server": initialized.serverInfo.name,
            "protocol_version": initialized.protocolVersion, "cases": cases}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/evidence/R677_RUNTIME.json")
    args = parser.parse_args()
    from rag.book_library import LocalBookLibrary

    source = ROOT / "rag/book_library.py"
    original = source.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    mutants = [
        ("removed_empty_guard", "if not query.strip():", "if False:"),
        ("empty_request_marked_ready", '"status": "invalid_request", "reason_code": "empty_query"',
         '"status": "ready", "reason_code": "empty_query"'),
    ]
    mutation_results = []
    with tempfile.TemporaryDirectory(prefix="r677-") as temporary:
        directory = Path(temporary)
        receipt = empty_receipt(LocalBookLibrary, directory)
        for name, before, after in mutants:
            require(original.count(before) == 1, "Alvo de mutação ambíguo: " + name)
            module = types.ModuleType("r677_mutant_" + name)
            module.__file__ = str(source)
            exec(compile(original.replace(before, after, 1), str(source), "exec"), module.__dict__)
            killed = False
            reason = ""
            try:
                empty_receipt(module.LocalBookLibrary, directory)
            except RuntimeError as exc:
                killed, reason = True, str(exc)
            require(killed, "Mutante sobrevivente: " + name)
            mutation_results.append({"name": name, "killed": killed, "reason": reason,
                                     "evidence_kind": "synthetic_in_memory_mutation"})
    protocol = asyncio.run(protocol_receipts())
    require(hashlib.sha256(source.read_bytes()).hexdigest() == digest, "Fonte mudou durante a prova.")
    report = {"status": "passed", "executed_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_sha256": digest, "source_unchanged": True,
              "empty_query_actual_python_result": receipt,
              "fresh_actual_mcp": protocol, "mutants": mutation_results,
              "model_inference_executed": False, "training_executed": False,
              "externally_validated": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(args.output),
                      "invalid_mcp_requests_rejected": len(protocol["cases"]),
                      "targeted_mutants_killed": len(mutation_results)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
