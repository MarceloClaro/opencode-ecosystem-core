"""SPEC-935-R816: operações do Core recebem dados JSON, nunca código shell.

Este módulo é a fronteira local da ferramenta core_command. O parser textual
de comandos do OpenCode é uma fronteira upstream distinta.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROCESS_TIMEOUT = 120
MAX_INPUT_BYTES = 1024 * 1024
MODULE_COMMANDS = {
    "efficiency": ("integrations.op_timing", ("report",)),
    "goose": ("integrations.goose_cli", ()),
    "gemini": ("integrations.gemini_cli", ()),
    "plandex": ("integrations.plandex_cli", ()),
    "reasonix": ("integrations.reasonix_cli", ()),
    "colab": ("integrations.colab_cli", ()),
    "colab-mcp": ("integrations.colab_mcp", ()),
    "minizinc": ("integrations.minizinc_mcp", ()),
    "claude-sdk": ("integrations.claude_agent_sdk", ()),
    "opencode-sdk": ("integrations.opencode_agent_sdk", ()),
    "kaggle": ("integrations.kaggle_cli", ()),
    "agy": ("integrations.antigravity_cli", ()),
}
COMMAND_NAMES = (
    "diagnose", "maswos", "reason", "economy", "models", "route", "sdd", "tdd", "pypi",
    *MODULE_COMMANDS,
)


def _admit(payload: Any) -> tuple[str, str, list[str]]:
    if not isinstance(payload, dict) or set(payload) - {"command", "arguments", "argv"}:
        raise ValueError("O pedido deve conter apenas command, arguments e argv.")
    name = payload.get("command")
    if not isinstance(name, str) or name not in COMMAND_NAMES:
        raise ValueError("Comando fora da lista explícita de operações do Core.")
    arguments = payload.get("arguments", "")
    argv = payload.get("argv", [])
    if not isinstance(arguments, str) or "\0" in arguments:
        raise ValueError("arguments deve ser texto sem NUL.")
    if not isinstance(argv, list) or any(not isinstance(arg, str) or "\0" in arg for arg in argv):
        raise ValueError("argv deve ser uma lista explícita de textos sem NUL.")
    if name not in MODULE_COMMANDS and argv:
        raise ValueError("Esta operação recebe arguments, não opções de processo.")
    if name in {"economy", "models", "sdd"} and arguments.strip():
        raise ValueError("Esta operação não recebe argumentos.")
    if name in MODULE_COMMANDS and arguments.strip() and "argv" not in payload:
        raise ValueError("CLIs requerem argv explícito; o texto não será interpretado por shell.")
    return name, arguments, argv


def _orchestrator():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    return MarceloClaroOrchestrator()


def execute_request(payload: Any) -> dict[str, Any]:
    """Executa somente operações fixas e retorna o resultado real da operação."""
    name, arguments, argv = _admit(payload)
    success = True
    limitations: list[str] = []
    if name in MODULE_COMMANDS:
        module, prefix = MODULE_COMMANDS[name]
        process = subprocess.run(
            [sys.executable, "-m", module, *prefix, *argv], cwd=ROOT,
            capture_output=True, text=True, shell=False, timeout=PROCESS_TIMEOUT,
        )
        result = {"returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr}
        success = process.returncode == 0
        limitations.append("Disponibilidade, autenticação e inferência dependem da CLI chamada e de seu resultado.")
    elif name == "reason":
        result = _orchestrator().reason(arguments)
        success = not bool(result.get("error"))
        limitations.append("Motor de raciocínio local; não prova inferência externa.")
    elif name == "diagnose":
        corpus = "ecosystem"
        if arguments:
            target = Path(arguments)
            if not target.is_absolute():
                target = ROOT / target
            corpus = target.read_text(encoding="utf-8")
        result = _orchestrator().diagnose(corpus, deep=True)
        success = not any(isinstance(section, dict) and section.get("error") for section in result.values())
        limitations.append("O arquivo é lido como texto; os scanners fornecem diagnóstico local.")
    elif name == "maswos":
        result = _orchestrator().academic_pipeline(arguments)
        limitations.append("MASWOS executa estágios internos via Blackboard; a pontuação não certifica manuscrito, inferência LLM ou Qualis.")
    elif name == "route":
        from integrations.model_router import model_router
        route = model_router.route(arguments or "coding")
        result = {"provider": route.provider_id, "model": route.model_id, "reason": route.reason,
                  "alternatives": [f"{provider}/{model}" for provider, model in route.alternatives]}
        limitations.append("Seleção de modelo; não executa inferência.")
    elif name == "economy":
        from economy import token_economy
        result = token_economy.report()
    elif name == "models":
        from integrations.model_router import model_router
        result = model_router.list_all_models()
        limitations.append("Catálogo de modelos; disponibilidade de executor não foi sondada.")
    elif name == "sdd":
        from sdd.spec_engine import spec_registry
        result = spec_registry.coverage_report()
    elif name == "tdd":
        from sdd.tdd_runner import run_pytest
        result = run_pytest(arguments or "tests/", timeout=PROCESS_TIMEOUT)
        success = result.get("all_passed") is True
    else:  # pypi, único nome restante da lista admitida
        from skills.tooling.pypi_search import search, format_output
        query = arguments.strip()
        json_output = query == "--json" or query.endswith(" --json")
        if json_output:
            query = query[:-6].rstrip()
        if not query:
            result = {"rendered": "Uso: /pypi <termo de busca> [--json]  (ex.: /pypi requests)", "query": query}
        else:
            found = search(query, limit=10)
            result = {"query": query, "rendered": format_output(found, json_output=json_output), "error": found.error}
            success = not bool(found.error)
        limitations.append("Busca de pacotes; não instala nem executa o conteúdo encontrado.")
    return {"success": success, "status": "completed" if success else "failed", "command": name,
            "coordinator": "marceloclaro", "input": {"arguments": arguments, "argv": argv},
            "result": result, "verification": "local_operation", "limitations": limitations}


def main() -> int:
    # Imports/motores legados podem emitir mensagens. Somente o envelope JSON
    # é enviado ao stdout; diagnósticos ficam no stderr.
    captured = io.StringIO()
    try:
        encoded = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(encoded) > MAX_INPUT_BYTES:
            raise ValueError("Pedido JSON excede o limite de entrada.")
        payload = json.loads(encoded)
        with redirect_stdout(captured):
            report = execute_request(payload)
    except Exception as exc:
        report = {"success": False, "status": "failed", "coordinator": "marceloclaro",
                  "error": type(exc).__name__, "message": str(exc)}
    if captured.getvalue():
        print(captured.getvalue(), file=sys.stderr, end="")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["success"] is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
