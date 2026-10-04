# -*- coding: utf-8 -*-
"""
Ponte MiniZinc MCP Server (SPEC-935-R646) — ferramenta externa orquestrável.

Upstream: r33drichards/minizinc-mcp (MIT): servidor MCP (FastMCP) com tool
única `solve_constraint(model, data?, solver="gecode", all_solutions=false,
timeout?) -> SolveResult`. Requer Python 3.11+, MiniZinc 2.8+ e deps
`mcp`, `pydantic`, `minizinc`.

Esta ponte NÃO executa o protocolo MCP nem resolve modelos; ela expõe
presença/versão, monta payloads no schema ConstraintModel, emite config
stdio/SSE e orienta instalação. A resolução é EXTERNA (servidor do operador
ou SSE hospedado); resultados nunca são "verificados" sem validação (R110).
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

_MINIZINC_BIN = "minizinc"
_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"

UPSTREAM_REPO = "https://github.com/r33drichards/minizinc-mcp"
HOSTED_SSE_URL = "https://minizinc-mcp.up.railway.app/sse"
MINIZINC_DOWNLOAD = "https://www.minizinc.org/software.html"
PYTHON_DEPS = ("mcp", "pydantic", "minizinc")
DEFAULT_SOLVER = "gecode"


def minizinc_available() -> bool:
    """True se o binário `minizinc` (solver) estiver no PATH."""
    return shutil.which(_MINIZINC_BIN) is not None


def minizinc_version(timeout: int = 10) -> Optional[str]:
    """Versão do solver via `minizinc --version` (None se ausente/falha)."""
    if not minizinc_available():
        return None
    try:
        proc = subprocess.run(
            [_MINIZINC_BIN, "--version"], capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        match = re.search(_SEMVER_RE, combined)
        return match.group(1) if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def python_deps_status() -> Dict[str, bool]:
    """Presença das deps Python (`mcp`, `pydantic`, `minizinc`) sem importá-las."""
    status: Dict[str, bool] = {}
    for dep in PYTHON_DEPS:
        try:
            status[dep] = importlib.util.find_spec(dep) is not None
        except (ImportError, ValueError):
            status[dep] = False
    return status


def mcp_available() -> bool:
    """True se as deps Python do servidor estiverem presentes.

    O binário do solver é verificado à parte: o modo SSE hospedado resolve
    sem MiniZinc local.
    """
    return all(python_deps_status().values())


def build_solve_payload(
    model: str,
    data: Optional[Dict[str, Any]] = None,
    solver: str = DEFAULT_SOLVER,
    all_solutions: bool = False,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Monta o payload no schema ConstraintModel do servidor (puro, sem rede).

    Lança ValueError com mensagem em português se o modelo for vazio ou os
    tipos forem inválidos.
    """
    if not isinstance(model, str) or not model.strip():
        raise ValueError("O modelo MiniZinc (model) deve ser uma string não vazia.")
    if data is not None and not isinstance(data, dict):
        raise ValueError("O parâmetro data deve ser um dicionário ou None.")
    if not isinstance(solver, str) or not solver.strip():
        raise ValueError("O solver deve ser uma string não vazia (ex.: 'gecode').")
    if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
        raise ValueError("O timeout deve ser um inteiro positivo em segundos ou None.")
    payload: Dict[str, Any] = {
        "model": model,
        "solver": solver,
        "all_solutions": bool(all_solutions),
    }
    if data:
        payload["data"] = dict(data)
    if timeout is not None:
        payload["timeout"] = timeout
    return payload


def hosted_sse() -> str:
    """URL SSE hospedada do servidor (constante; sem sondagem de rede)."""
    return HOSTED_SSE_URL


def mcp_config(local_cmd: Optional[List[str]] = None) -> Dict[str, object]:
    """Entrada stdio local pronta para a seção `mcp` do `opencode.json`."""
    command = list(local_cmd) if local_cmd else [sys.executable, "main.py"]
    return {
        "type": "local",
        "command": command,
        "enabled": True,
        "timeout": 660000,
    }


def doctor_check() -> Dict[str, str]:
    """DoctorCheck no formato do Core (name/status/detail; nunca fail)."""
    deps = python_deps_status()
    missing_deps = sorted(name for name, ok in deps.items() if not ok)
    has_solver = minizinc_available()
    version = minizinc_version() if has_solver else None
    if not missing_deps and has_solver:
        sufixo = f" (MiniZinc {version})" if version else " (MiniZinc presente)"
        return {
            "name": "minizinc-mcp",
            "status": "pass",
            "detail": f"Ponte MiniZinc MCP pronta{sufixo}; deps Python ok "
            f"({', '.join(PYTHON_DEPS)}). SPEC-935-R646.",
        }
    if not missing_deps:
        return {
            "name": "minizinc-mcp",
            "status": "warn",
            "detail": "Deps Python ok, mas binário `minizinc` ausente — instale o "
            f"MiniZinc 2.8+ em {MINIZINC_DOWNLOAD} ou use o SSE hospedado "
            f"({HOSTED_SSE_URL}). SPEC-935-R646.",
        }
    return {
        "name": "minizinc-mcp",
        "status": "warn",
        "detail": f"Dependências Python ausentes: {', '.join(missing_deps)} "
        "(pip install mcp pydantic minizinc; Python 3.11+). "
        f"Solver minizinc: {'presente' if has_solver else 'ausente'}. SPEC-935-R646.",
    }


def install_instructions() -> str:
    """Instrução oficial de uso do MiniZinc MCP Server."""
    return (
        "MiniZinc MCP Server (r33drichards/minizinc-mcp, MIT) — constraint solving\n"
        "via tool única solve_constraint (4-Queens, knapsack, CSP/COP):\n"
        "\n"
        "Pré-requisitos:\n"
        "  Python 3.11+ e MiniZinc 2.8+ com solver (ex.: gecode):\n"
        f"  {MINIZINC_DOWNLOAD}\n"
        "\n"
        "Opção 1 — SSE hospedado (recomendado, sem instalar):\n"
        f"  {HOSTED_SSE_URL}\n"
        "  Claude: Settings > Connectors > Add Custom Connector (nome 'minizinc mcp')\n"
        "  Claude Code: claude mcp add minizinc -t sse " + HOSTED_SSE_URL + "\n"
        "\n"
        "Opção 2 — local:\n"
        "  git clone " + UPSTREAM_REPO + "\n"
        "  cd minizinc-mcp && pip install -r requirements.txt  # mcp, pydantic, minizinc\n"
        "  python main.py\n"
        "\n"
        "Opção 3 — Docker self-host:\n"
        "  docker build -t minizinc-mcp . && docker run -p 8000:8000 minizinc-mcp\n"
        "\n"
        "Uso no Core:\n"
        "  /minizinc status    # solver + deps Python\n"
        "  /minizinc config    # snippet stdio local\n"
        "  /minizinc payload --model-file modelo.mzn [--solver gecode]\n"
    )


def _format_status() -> str:
    deps = python_deps_status()
    return json.dumps(
        {
            "especificacao": "SPEC-935-R646",
            "solver_presente": minizinc_available(),
            "solver_versao": minizinc_version(),
            "deps_python": deps,
            "ponte_pronta": mcp_available(),
            "sse_hospedado": HOSTED_SSE_URL,
            "solver_padrao": DEFAULT_SOLVER,
            "licenca": "MIT",
            "origem": UPSTREAM_REPO,
        },
        ensure_ascii=False,
        indent=2,
    )


def _parse_payload_argv(tokens: List[str]) -> Dict[str, Any]:
    """Interpreta --model-text/--model-file/--data-json/--solver/--all/--timeout."""
    parsed: Dict[str, Any] = {"solver": DEFAULT_SOLVER}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in ("--model-text", "--model-file", "--data-json", "--solver", "--timeout"):
            if index + 1 >= len(tokens):
                index += 1
                continue
            parsed[token[2:].replace("-", "_")] = tokens[index + 1]
            index += 2
            continue
        if token == "--all":
            parsed["all"] = True
            index += 1
            continue
        if token.startswith("--solver="):
            parsed["solver"] = token.split("=", 1)[1]
            index += 1
            continue
        index += 1
    return parsed


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.minizinc_mcp <status|config|doctor|install|payload|solvers> [args...]\n"
            "  config [--hosted]                 # stdio local ou JSON com URL SSE\n"
            "  payload --model-text '...' | --model-file MZ [--data-json '{...}']\n"
            "          [--solver gecode] [--all] [--timeout SEG]\n"
            "  solvers                           # orienta listagem (requer binário)"
        )
        return 0
    command, *rest = argv
    if command == "status":
        print(_format_status())
        return 0
    if command == "config":
        if "--hosted" in rest:
            print(json.dumps({"minizinc-mcp": {"url": hosted_sse()}},
                             ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"minizinc-mcp": mcp_config()},
                             ensure_ascii=False, indent=2))
        return 0
    if command == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1
    if command == "install":
        print(install_instructions())
        return 0
    if command == "solvers":
        if not minizinc_available():
            print(f"Binário `minizinc` ausente — instale em {MINIZINC_DOWNLOAD}")
            return 1
        try:
            proc = subprocess.run(
                [_MINIZINC_BIN, "--solvers"], capture_output=True, text=True,
                timeout=30, check=False,
            )
            print(proc.stdout or proc.stderr or "")
            return 0 if proc.returncode == 0 else 1
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(str(exc))
            return 1
    if command == "payload":
        opts = _parse_payload_argv(rest)
        model_text = str(opts.get("model_text", "") or "")
        model_file = str(opts.get("model_file", "") or "")
        if model_file and not model_text:
            try:
                with open(model_file, "r", encoding="utf-8") as fh:
                    model_text = fh.read()
            except OSError as exc:
                print(f"Não foi possível ler {model_file}: {exc}")
                return 2
        if not model_text.strip():
            print("Uso: payload --model-text '...' | --model-file MODELO.mzn [--solver NOME]")
            return 2
        data = None
        if opts.get("data_json"):
            try:
                data = json.loads(str(opts["data_json"]))
            except json.JSONDecodeError as exc:
                print(f"data-json inválido: {exc}")
                return 2
        timeout = None
        if opts.get("timeout"):
            try:
                timeout = int(str(opts["timeout"]))
            except ValueError:
                print("timeout deve ser inteiro em segundos.")
                return 2
        try:
            payload = build_solve_payload(
                model_text, data=data, solver=str(opts.get("solver", DEFAULT_SOLVER)),
                all_solutions=bool(opts.get("all", False)), timeout=timeout,
            )
        except ValueError as exc:
            print(str(exc))
            return 2
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
