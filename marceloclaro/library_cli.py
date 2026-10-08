"""Operações locais de biblioteca e integridade de dados, via orquestrador."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
from typing import Any


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _orchestrator(provided: Any) -> Any:
    if provided is not None:
        return provided
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    return MarceloClaroOrchestrator(auto_load_agents=False)


def _emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def run_library_cli(argv: list[str], orchestrator: Any = None) -> int:
    parser = _Parser(prog="biblioteca", description="Consulta local aos livros técnicos.")
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("status")
    sub.add_parser("indexar")
    search = sub.add_parser("buscar")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=5)
    try:
        args = parser.parse_args(argv)
        if args.operation == "buscar":
            if not 1 <= args.top_k <= 10:
                raise ValueError("--top-k deve estar entre 1 e 10.")
            if not args.query.strip() or len(args.query) > 2000:
                raise ValueError("A consulta deve conter de 1 a 2000 caracteres.")
        orch = _orchestrator(orchestrator)
        if args.operation == "status":
            result = orch.library_status()
        elif args.operation == "indexar":
            result = orch.library_index()
        else:
            result = orch.library_query(args.query, top_k=args.top_k)
        _emit(result)
        return 1 if result.get("status") == "error" else 0
    except (ValueError, OSError, ImportError, RuntimeError, sqlite3.Error) as exc:
        _emit({"status": "error", "error": str(exc)})
        return 2


def _load_json(path: str) -> Any:
    source = Path(path)
    if source.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("Arquivo JSON excede o limite de 20 MiB.")
    return json.loads(source.read_text(encoding="utf-8-sig"))


def run_finetuning_cli(argv: list[str], orchestrator: Any = None) -> int:
    parser = _Parser(prog="fine-dados", description="Valida dados e medições sem treinar modelos.")
    sub = parser.add_subparsers(dest="operation", required=True)
    validate = sub.add_parser("validar")
    validate.add_argument("file")
    validate.add_argument("--seed", type=int, default=42)
    evaluate = sub.add_parser("avaliar")
    evaluate.add_argument("file")
    evaluate.add_argument("--min-improvement", type=float, default=0.0)
    try:
        args = parser.parse_args(argv)
        data = _load_json(args.file)
        orch = _orchestrator(orchestrator)
        if args.operation == "validar":
            result = orch.finetuning_prepare_data(data, seed=args.seed)
            # Dados do usuário são devolvidos somente pela API de preparação.
            # O terminal exibe diagnóstico e manifesto, sem perguntas/respostas.
            result = {key: value for key, value in result.items() if key != "splits"}
        else:
            if not isinstance(data, dict) or not {"baseline", "candidate"} <= data.keys():
                raise ValueError("Informe um objeto JSON com baseline e candidate.")
            result = orch.finetuning_evaluate(data["baseline"], data["candidate"],
                                              min_improvement=args.min_improvement)
        _emit(result)
        return 0 if result.get("status") in {"accepted", "passed"} else 1
    except (ValueError, OSError, ImportError, RuntimeError) as exc:
        _emit({"status": "error", "error": str(exc)})
        return 2
