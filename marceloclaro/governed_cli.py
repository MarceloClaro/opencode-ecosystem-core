"""Entradas pequenas para o primário: agentes governados e CI local."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_ci_config(config):
    if not isinstance(config, dict):
        raise ValueError("Configuração CI deve ser objeto")
    operation = config.get("operation")
    optional = {"start": {"profile"}, "status": {"run_id"}, "runs": {"limit"}, "cancel": {"run_id"}}
    if operation not in optional or set(config) - {"operation", *optional[operation]}:
        raise ValueError("Operação CI ou campos desconhecidos")
    if "profile" in config and config["profile"] != "scientific":
        raise ValueError("Perfil CI não autorizado")
    if "limit" in config and (type(config["limit"]) is not int or not 1 <= config["limit"] <= 100):
        raise ValueError("Limite CI inválido")
    if operation == "cancel" and "run_id" not in config:
        raise ValueError("Cancelamento exige run_id")
    if "run_id" in config:
        import re
        if not isinstance(config["run_id"], str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", config["run_id"]):
            raise ValueError("run_id CI inválido")
    return dict(config)


def run_governed_cli(kind, argv, orchestrator_factory):
    profile_path = None
    parser = argparse.ArgumentParser(prog="marceloclaro " + kind)
    if kind == "agentes":
        parser.add_argument("action", choices=("inventory", "validar", "registrar", "ativar", "criar"))
        parser.add_argument("agent_id", nargs="?")
        parser.add_argument("--task")
        parser.add_argument("--config")
        args = parser.parse_args(argv)
        operations = {"inventory": "inventory", "validar": "validate", "registrar": "register", "ativar": "activate", "criar": "create"}
        config = {"operation": operations[args.action]}
        if args.agent_id:
            config["agent_id"] = args.agent_id
        if args.task:
            config["task"] = args.task
        if args.config:
            profile_path = Path(args.config)
        from agents.lifecycle import validate_lifecycle_request
        validator, method = validate_lifecycle_request, "agent_profile_action"
    else:
        parser.add_argument("action", choices=("iniciar", "status", "listar", "cancelar"))
        parser.add_argument("--run-id")
        parser.add_argument("--profile", default=None)
        parser.add_argument("--limit", type=int)
        args = parser.parse_args(argv)
        config = {"operation": {"iniciar": "start", "status": "status", "listar": "runs", "cancelar": "cancel"}[args.action]}
        for name in ("run_id", "profile", "limit"):
            if getattr(args, name) is not None:
                config[name] = getattr(args, name)
        validator, method = validate_ci_config, "local_ci_action"
    try:
        if profile_path is not None:
            with profile_path.open("rb") as stream:
                raw = stream.read(128 * 1024 + 1)
            if len(raw) > 128 * 1024:
                raise ValueError("Configuração de perfil excessiva")
            config["profile"] = json.loads(raw)
        config = validator(config)
        result = getattr(orchestrator_factory(auto_load_agents=False), method)(config)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "executed": False}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") in {"blocked", "busy", "failed", "error", "invalid_request"} else 0
