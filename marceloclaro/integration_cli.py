"""Interface de diagnóstico e handoff coordenados (R662)."""
from __future__ import annotations

import argparse
import json
from typing import Any


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def run_integration_cli(argv: list[str], orchestrator: Any = None) -> int:
    parser = _Parser(prog="integracoes", description="Diagnóstico e preparação de skills pelo orquestrador.")
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("status")
    sub.add_parser("verificar")
    handoff = sub.add_parser("handoff")
    handoff.add_argument("artifact_id")
    skill = sub.add_parser("skill")
    skill.add_argument("skill_name")
    try:
        args = parser.parse_args(argv or ["status"])
        if orchestrator is None:
            from marceloclaro.orchestrator import MarceloClaroOrchestrator
            orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
        if args.operation in {"status", "verificar"}:
            result = orchestrator.integration_status()
        elif args.operation == "handoff":
            result = orchestrator.integration_handoff(args.artifact_id)
        else:
            result = orchestrator.integration_skill_plan(args.skill_name)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if result.get("status") in {"error", "refused", "not_found"} else 0
    except (ValueError, OSError, ImportError, RuntimeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 2
