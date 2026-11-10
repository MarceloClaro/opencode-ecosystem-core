# -*- coding: utf-8 -*-
"""CLI da camada de cognição (SPEC-935-R1132).

Uso:
    python3 -m core_cognition.cli map
    python3 -m core_cognition.cli audit
    python3 -m core_cognition.cli risk
    python3 -m core_cognition.cli stop --state state.json
    python3 -m core_cognition.cli ledger --path claims.jsonl
    python3 -m core_cognition.cli ledger --template claims.jsonl
    python3 -m core_cognition.cli contest
    python3 -m core_cognition.cli n-of-1 --template protocol.json
    python3 -m core_cognition.cli n-of-1 --validate protocol.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import claims_ledger, cognitive_function_map, contestability, epistemic_risk, n_of_1, runtime_contract, stop_rules
from .doctor_checks import run_cognition_checks

ROOT = Path(__file__).resolve().parents[1]


def _print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="core_cognition", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("map", help="lista o mapa de funções cognitivas")
    sub.add_parser("audit", help="roda os checks de cognição")
    sub.add_parser("risk", help="audita risco epistêmico do checkout")
    sub.add_parser("contest", help="audita contestabilidade e saída")

    stop_parser = sub.add_parser("stop", help="avalia regras de parada")
    stop_parser.add_argument("--state", required=True, help="JSON com o estado da sessão")

    ledger_parser = sub.add_parser("ledger", help="audita ou cria claims ledger")
    ledger_parser.add_argument("--path", default="claims.jsonl")
    ledger_parser.add_argument("--template", default=None)

    n1_parser = sub.add_parser("n-of-1", help="valida ou cria protocolo N-of-1")
    n1_parser.add_argument("--template", default=None)
    n1_parser.add_argument("--validate", default=None)

    runtime_parser = sub.add_parser("runtime", help="avalia o contrato de runtime")
    runtime_parser.add_argument("--request", required=True, help="JSON com ActionRequest")
    runtime_parser.add_argument("--state", required=True, help="JSON com RuntimeState")

    args = parser.parse_args(argv)

    if args.command == "map":
        _print(cognitive_function_map.to_dicts(cognitive_function_map.load_map()))
        return 0
    if args.command == "audit":
        _print([check.__dict__ for check in run_cognition_checks(ROOT)])
        return 0
    if args.command == "risk":
        _print(epistemic_risk.audit_repository(ROOT))
        return 0
    if args.command == "contest":
        _print(contestability.audit(ROOT).to_dict())
        return 0
    if args.command == "stop":
        decision = stop_rules.StopRules().evaluate(_load_json(args.state))
        _print(decision.to_dict())
        return 0
    if args.command == "ledger":
        if args.template:
            _print({"template": str(claims_ledger.write_template(args.template))})
        else:
            _print(claims_ledger.audit_ledger(args.path))
        return 0
    if args.command == "n-of-1":
        if args.template:
            _print({"template": str(n_of_1.write_template(args.template))})
        elif args.validate:
            _print(n_of_1.validate_protocol(_load_json(args.validate)).to_dict())
        else:
            _print(n_of_1.template())
        return 0
    if args.command == "runtime":
        request = runtime_contract.ActionRequest(**_load_json(args.request))
        state = runtime_contract.RuntimeState(**_load_json(args.state))
        decision = runtime_contract.RuntimeContract().authorize(request, state)
        _print(decision.to_dict())
        return 0

    parser.error("comando desconhecido")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
