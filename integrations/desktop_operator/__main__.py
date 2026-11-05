"""CLI local do desktop-operator; a aprovação é criada somente aqui."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import approvals, policy, runtime


def _emit(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok", True) else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="desktop-operator", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="saúde e permissões")
    sub.add_parser("list-apps", help="apps GUI visíveis")

    snapshot = sub.add_parser("snapshot", help="árvore de acessibilidade")
    snapshot.add_argument("--app", required=True)
    snapshot.add_argument("--max-depth", type=int, default=6)
    snapshot.add_argument("--timeout-ms", type=int)

    click = sub.add_parser("click", help="ativar ref com aprovação")
    click.add_argument("--app", required=True)
    click.add_argument("--ref", required=True)
    click.add_argument("--approval-token", required=True)
    click.add_argument("--timeout-ms", type=int)

    type_cmd = sub.add_parser("type", help="inserir texto com aprovação")
    type_cmd.add_argument("--app", required=True)
    type_cmd.add_argument("--ref", required=True)
    type_cmd.add_argument("--text", required=True)
    type_cmd.add_argument("--approval-token", required=True)
    type_cmd.add_argument("--timeout-ms", type=int)

    wait = sub.add_parser("wait", help="esperar ref, texto ou intervalo")
    wait.add_argument("--app")
    wait.add_argument("--ref")
    wait.add_argument("--text")
    wait.add_argument("--wait-ms", type=int)
    wait.add_argument("--timeout-ms", type=int, default=5000)

    approve = sub.add_parser("approve", help="criar aprovação humana de uso único")
    approve.add_argument("--command", dest="approved_command", choices=("click", "type"), required=True)
    approve.add_argument("--app", required=True)
    approve.add_argument("--ref", required=True)
    approve.add_argument("--text")
    approve.add_argument("--ttl", type=int)
    approve.add_argument("--confirm", action="store_true", help="confirma a emissão")

    sub.add_parser("config", help="mostrar configuração efetiva sem segredos")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = policy.load_config()
    if args.command == "config":
        return _emit({
            "ok": True,
            "binary": Path(policy.resolve_binary(config)).name if policy.resolve_binary(config) else None,
            "binary_found": bool(policy.resolve_binary(config)),
            "backend": config.backend,
            "allowed_apps": list(config.allowed_apps),
            "state_dir": str(Path(config.state_dir).expanduser()),
            "timeout_ms": config.timeout_ms,
            "max_text_bytes": config.max_text_bytes,
            "max_output_bytes": config.max_output_bytes,
            "approval_ttl_seconds": config.approval_ttl_seconds,
        })
    if args.command == "approve":
        if not args.confirm:
            return _emit({
                "ok": False,
                "error": {"code": "confirm_required", "message": "repita com --confirm após revisar o alvo"},
            })
        try:
            issued = approvals.issue_approval(
                config, args.approved_command, args.app, args.ref,
                text=args.text, ttl_seconds=args.ttl,
            )
        except (approvals.ApprovalError, policy.PolicyDenied) as exc:
            return _emit({"ok": False, "error": {"code": exc.code, "message": exc.reason}})
        return _emit({"ok": True, **issued})

    kwargs = {
        "app": getattr(args, "app", None),
        "ref": getattr(args, "ref", None),
        "text": getattr(args, "text", None),
        "timeout_ms": getattr(args, "timeout_ms", None),
        "max_depth": getattr(args, "max_depth", None),
        "wait_ms": getattr(args, "wait_ms", None),
        "approval_token": getattr(args, "approval_token", None),
    }
    return _emit(runtime.run(args.command, config, **kwargs))


if __name__ == "__main__":
    raise SystemExit(main())
