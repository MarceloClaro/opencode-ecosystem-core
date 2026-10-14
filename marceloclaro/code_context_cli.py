"""CLI de contexto de código local sob o primário (R887)."""
from __future__ import annotations

import argparse
import json


def run_code_context_cli(argv, orchestrator_factory) -> int:
    parser = argparse.ArgumentParser(prog="marceloclaro code-context")
    parser.add_argument("operation", choices=("setup", "index", "status", "query"))
    parser.add_argument("--tool", help="Ferramenta de consulta permitida")
    parser.add_argument("--arguments", default="{}", help="Objeto JSON dos parâmetros da consulta")
    parser.add_argument("--timeout", type=float, default=30.0)
    try:
        args = parser.parse_args(argv)
        arguments = json.loads(args.arguments)
        if not isinstance(arguments, dict):
            raise TypeError("arguments deve ser um objeto JSON.")
        config = {"operation": args.operation, "timeout_seconds": args.timeout}
        if args.operation == "query":
            if args.tool is None:
                raise ValueError("query exige --tool.")
            config.update(tool=args.tool, arguments=arguments)
        elif args.tool is not None or arguments:
            raise ValueError("tool/arguments somente se aplicam a query.")
        report = orchestrator_factory(auto_load_agents=False).code_context_action(config)
    except SystemExit as exc:
        return int(exc.code)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"success": False, "status": "invalid", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("success") is True else 1


if __name__ == "__main__":
    import sys

    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    raise SystemExit(run_code_context_cli(sys.argv[1:], MarceloClaroOrchestrator))
