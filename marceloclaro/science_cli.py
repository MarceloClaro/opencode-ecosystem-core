"""CLI científica central: planejamento ou execução delimitada por configuração."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from marceloclaro.knowledge_evolution import validate_plan_config, validate_science_config


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Campo JSON duplicado: {key}")
        result[key] = value
    return result


def run_science_cli(argv: list[str], orchestrator: Any = None) -> int:
    parser = _Parser(prog="ciencia", description="Evolução do conhecimento e pesquisa reproduzível.")
    sub = parser.add_subparsers(dest="operation", required=True)
    for operation in ("planejar", "executar", "runtime", "dataset", "personalizar", "plugins", "notebook"):
        command = sub.add_parser(operation)
        command.add_argument("--config")
        if operation == "planejar":
            command.add_argument("--problema")
            command.add_argument("--objetivo", action="append")
    try:
        args = parser.parse_args(argv)
        if args.config:
            if args.operation == "planejar" and (args.problema or args.objetivo):
                raise ValueError("Use --config ou --problema/--objetivo.")
            path = Path(args.config)
            if path.stat().st_size > 131072:
                raise ValueError("Configuração excede 128 KiB.")
            with path.open("rb") as stream:
                raw = stream.read(131073)
            if len(raw) > 131072:
                raise ValueError("Configuração excede 128 KiB.")
            config = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
        elif args.operation == "planejar":
            config = {"problem": args.problema, "target_state": args.objetivo}
        else:
            raise ValueError("executar exige --config.")
        from marceloclaro.runtime_actions import METHODS, validate_action
        if args.operation in METHODS:
            config = validate_action(args.operation, config)
        else:
            validator = validate_plan_config if args.operation == "planejar" else validate_science_config
            config = validator(config)
        if orchestrator is None:
            from marceloclaro.orchestrator import MarceloClaroOrchestrator
            orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
        if args.operation in METHODS:
            method = getattr(orchestrator, METHODS[args.operation])
        else:
            method = orchestrator.knowledge_evolution_plan if args.operation == "planejar" else orchestrator.scientific_reproducible_run
        result = method(**config)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if result.get("status") in {"blocked", "error", "failed", "partial", "lost"} else 0
    except (ValueError, OSError, ImportError, RuntimeError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 2
