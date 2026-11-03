# -*- coding: utf-8 -*-
"""R1012 — interface ``marceloclaro federacao``.

Todos os subcomandos são somente leitura, exceto ``apply --apply`` (que grava
``opencode.json`` com backup) e ``sync`` (que grava ``federation/``).
"""

from __future__ import annotations

import argparse
import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .apply import apply_mcp
from .store import federation_root, load_registry, status as registry_status, sync, verify
from .route import route as route_artifacts

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def _items(repo_root: Path) -> List[Dict[str, Any]]:
    return list(load_registry(repo_root).get("items") or ())


def _filter(
    items: List[Dict[str, Any]],
    *,
    ecosystem: Optional[str] = None,
    kind: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    selected = items
    if ecosystem:
        selected = [item for item in selected if item.get("ecosystem") == ecosystem]
    if kind:
        selected = [item for item in selected if item.get("kind") == kind]
    if status:
        selected = [item for item in selected if item.get("status") == status]
    return selected


def _cmd_sync(args: argparse.Namespace) -> int:
    result = sync(Path(args.repo or _REPO_ROOT), home=Path(args.home) if args.home else None,
                  write=not args.no_write)
    _emit(result)
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    _emit(registry_status(Path(args.repo or _REPO_ROOT)))
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    repo = Path(args.repo or _REPO_ROOT)
    items = _filter(_items(repo), ecosystem=args.ecosystem, kind=args.kind, status=args.status)
    total = len(items)
    offset = max(0, int(args.offset or 0))
    limit = max(1, int(args.limit or 50))
    page = items[offset:offset + limit]
    _emit({
        "status": "ok",
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": [{key: item.get(key) for key in
                   ("id", "ecosystem", "kind", "name", "status", "license", "install_mode")}
                  for item in page],
    })
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    repo = Path(args.repo or _REPO_ROOT)
    for item in _items(repo):
        if item.get("id") == args.item_id:
            _emit({"status": "ok", "item": item})
            return 0
    _emit({"status": "not_found", "item_id": args.item_id})
    return 2


def _cmd_candidates(args: argparse.Namespace) -> int:
    repo = Path(args.repo or _REPO_ROOT)
    path = federation_root(repo) / "mcp_candidates.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _emit({"status": "missing", "path": str(path)})
        return 2
    if args.summary:
        _emit({
            "status": "ok",
            "total": len(document.get("servers") or {}),
            "names": sorted(document.get("servers") or {}),
            "registry_digest": document.get("registry_digest"),
        })
        return 0
    _emit(document)
    return 0


def _cmd_apply(args: argparse.Namespace) -> int:
    repo = Path(args.repo or _REPO_ROOT)
    names = [part.strip() for part in (args.ids or "").split(",") if part.strip()] or None
    result = apply_mcp(repo, names=names, dry_run=not args.stage)
    _emit(result)
    return 0


def _cmd_route(args: argparse.Namespace) -> int:
    repo = Path(args.repo or _REPO_ROOT)
    capabilities = [part.strip().lower() for part in (args.capabilities or "").split(",") if part.strip()]
    result = route_artifacts(repo, args.description, capabilities, top_k=args.top,
                             include_non_admitted=args.include_non_admitted)
    _emit(result)
    return 0 if result.get("status") == "ok" else 1


def _cmd_verify(args: argparse.Namespace) -> int:
    result = verify(Path(args.repo or _REPO_ROOT))
    _emit(result)
    return 0 if result.get("ok") else 1


def _names(value: Optional[str]) -> Optional[List[str]]:
    parsed = [part.strip() for part in (value or "").split(",") if part.strip()]
    return parsed or None


def _cmd_probe(args: argparse.Namespace) -> int:
    from .runtime import probe_all

    repo = Path(args.repo or _REPO_ROOT)
    results = probe_all(repo, names=_names(args.ids), timeout=args.timeout)
    summary = {
        name: {
            "ok": bool(result.get("ok")),
            "tools_count": result.get("tools_count"),
            "protocol_version": result.get("protocol_version"),
            "error": result.get("error") or "",
            "duration_ms": result.get("duration_ms"),
        }
        for name, result in results.items()
    }
    _emit({"status": "ok" if all(item["ok"] for item in summary.values()) else "degraded",
           "results": summary, "receipts": str((repo / "federation" / "probes"))})
    return 0 if all(item["ok"] for item in summary.values()) else 1


def _cmd_activate(args: argparse.Namespace) -> int:
    from .runtime import activate

    result = activate(Path(args.repo or _REPO_ROOT), names=_names(args.ids))
    _emit(result)
    return 0 if result.get("status") == "ok" else 1


def _cmd_deactivate(args: argparse.Namespace) -> int:
    from .runtime import deactivate

    result = deactivate(Path(args.repo or _REPO_ROOT), names=_names(args.ids))
    _emit(result)
    return 0 if result.get("status") == "ok" else 1


def _cmd_runtime_doctor(args: argparse.Namespace) -> int:
    from .runtime import doctor

    result = doctor(Path(args.repo or _REPO_ROOT))
    _emit(result)
    return 0 if result.get("status") == "ok" else 1


def _cmd_smoke(args: argparse.Namespace) -> int:
    from .runtime import smoke

    repo = Path(args.repo or _REPO_ROOT)
    results = smoke(repo, names=_names(args.ids), timeout=args.timeout)
    summary = {
        name: {
            "ok": bool(result.get("ok")),
            "tool": result.get("tool"),
            "duration_ms": result.get("duration_ms"),
            "error": result.get("error") or "",
        }
        for name, result in results.items()
    }
    _emit({"status": "ok" if all(item["ok"] for item in summary.values()) else "degraded",
           "results": summary, "receipts": str(repo / "federation" / "probes")})
    return 0 if all(item["ok"] for item in summary.values()) else 1


def _cmd_install(args: argparse.Namespace) -> int:
    import subprocess

    from .runtime import INSTALL_COMMANDS

    repo = Path(args.repo or _REPO_ROOT)
    commands: List[List[str]] = [INSTALL_COMMANDS["node"], *INSTALL_COMMANDS["python"]]
    if not args.execute:
        _emit({"status": "planned", "cwd": str(repo), "commands": commands,
               "note": "Use --execute para instalar. Postinstall de terceiro nunca executa (--ignore-scripts)."})
        return 0
    outcomes = []
    for command in commands:
        process = subprocess.run(command, cwd=str(repo), capture_output=True, text=True, timeout=1800)
        outcomes.append({"command": command, "returncode": process.returncode,
                         "stderr_tail": process.stderr[-400:]})
        if process.returncode != 0:
            break
    _emit({"status": "ok" if all(o["returncode"] == 0 for o in outcomes) else "failed",
           "outcomes": outcomes})
    return 0 if all(o["returncode"] == 0 for o in outcomes) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="marceloclaro federacao")
    parser.add_argument("--repo", default=None, help="Raiz do repositório (padrão: este checkout)")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", default=argparse.SUPPRESS,
                        help="Raiz do repositório (aceito antes ou depois do subcomando)")
    sub = parser.add_subparsers(dest="command", required=True)

    sync_parser = sub.add_parser("sync", parents=[common], help="Coleta e grava o registro federado")
    sync_parser.add_argument("--no-write", action="store_true", help="Somente calcula, sem gravar")
    sync_parser.add_argument("--home", help="HOME alternativo (testes)")
    sync_parser.set_defaults(handler=_cmd_sync)

    status_parser = sub.add_parser("status", parents=[common], help="Estado do registro persistido")
    status_parser.set_defaults(handler=_cmd_status)

    list_parser = sub.add_parser("list", parents=[common], help="Lista artefatos com filtros")
    list_parser.add_argument("--ecosystem", choices=["claude", "chatgpt", "antigravity", "github"])
    list_parser.add_argument("--kind", choices=["plugin", "mcp", "agent", "skill", "command",
                                                "hook", "prompt_pack", "lsp"])
    list_parser.add_argument("--status", choices=["admitted", "quarantined", "degraded", "blocked"])
    list_parser.add_argument("--limit", type=int, default=50)
    list_parser.add_argument("--offset", type=int, default=0)
    list_parser.set_defaults(handler=_cmd_list)

    show_parser = sub.add_parser("show", parents=[common], help="Exibe um artefato pelo ID")
    show_parser.add_argument("item_id")
    show_parser.set_defaults(handler=_cmd_show)

    candidates_parser = sub.add_parser("candidates", parents=[common],
                                       help="Servidores MCP candidatos (desativados)")
    candidates_parser.add_argument("--summary", action="store_true")
    candidates_parser.set_defaults(handler=_cmd_candidates)

    apply_parser = sub.add_parser("apply", parents=[common],
                                  help="Prepara patch MCP (não altera opencode.json)")
    apply_parser.add_argument("--ids", help="Lista separada por vírgula; padrão: todos")
    apply_parser.add_argument("--stage", "--apply", dest="stage", action="store_true",
                              help="Grava federation/mcp_patch.json (dry-run sem esta opção)")
    apply_parser.set_defaults(handler=_cmd_apply)

    route_parser = sub.add_parser("route", parents=[common], help="Ranqueia artefatos para uma tarefa")
    route_parser.add_argument("description")
    route_parser.add_argument("--capabilities", help="Capacidades exigidas, separadas por vírgula")
    route_parser.add_argument("--top", type=int, default=5)
    route_parser.add_argument("--include-non-admitted", action="store_true")
    route_parser.set_defaults(handler=_cmd_route)

    verify_parser = sub.add_parser("verify", parents=[common], help="Reconfere o digest do registro")
    verify_parser.set_defaults(handler=_cmd_verify)

    install_parser = sub.add_parser("install", parents=[common],
                                    help="Mostra (ou executa) a instalação isolada dos MCPs")
    install_parser.add_argument("--execute", action="store_true", help="Executa npm/uv de verdade")
    install_parser.set_defaults(handler=_cmd_install)

    probe_parser = sub.add_parser("probe", parents=[common],
                                  help="Prova initialize + tools/list de cada servidor")
    probe_parser.add_argument("--ids", help="Lista separada por vírgula; padrão: todos")
    probe_parser.add_argument("--timeout", type=int, default=60)
    probe_parser.set_defaults(handler=_cmd_probe)

    activate_parser = sub.add_parser("activate", parents=[common],
                                     help="Ativa perfil padrão com probe + smoke recentes")
    activate_parser.add_argument("--ids", help="Lista separada por vírgula; sem esta opção: perfil padrão seletivo")
    activate_parser.set_defaults(handler=_cmd_activate)

    deactivate_parser = sub.add_parser("deactivate", parents=[common],
                                       help="Remove servidores do activated.json")
    deactivate_parser.add_argument("--ids", help="Lista separada por vírgula; padrão: todos")
    deactivate_parser.set_defaults(handler=_cmd_deactivate)

    runtime_doctor = sub.add_parser("doctor", parents=[common],
                                    help="Confere binário e recibo de cada servidor ativado")
    runtime_doctor.set_defaults(handler=_cmd_runtime_doctor)

    smoke_parser = sub.add_parser("smoke", parents=[common],
                                  help="Chama uma ferramenta real de cada servidor")
    smoke_parser.add_argument("--ids", help="Lista separada por vírgula; padrão: todos")
    smoke_parser.add_argument("--timeout", type=int, default=150)
    smoke_parser.set_defaults(handler=_cmd_smoke)
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        args = parser.parse_args(arguments)
    except SystemExit as exc:  # argparse já imprimiu a mensagem
        return int(exc.code or 2)
    return int(args.handler(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
