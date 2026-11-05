"""CLI do scientific-data; somente leitura."""

from __future__ import annotations

import argparse
import json

from . import inspect as inspector, policy


def _emit(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok", True) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="scientific-data", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    inspect_cmd = sub.add_parser("inspect")
    inspect_cmd.add_argument("--path", required=True)
    preview = sub.add_parser("preview")
    preview.add_argument("--path", required=True)
    preview.add_argument("--variable")
    preview.add_argument("--selector", help="JSON de índices inteiros por dimensão")
    preview.add_argument("--band", type=int, default=1)
    preview.add_argument("--max-points", type=int, default=2000)
    args = parser.parse_args(argv)
    config = policy.load_config()
    if args.command == "status":
        return _emit(inspector.status())
    if args.command == "inspect":
        try:
            return _emit(inspector.inspect(config, args.path))
        except (policy.ScientificDenied, inspector.InspectError) as exc:
            return _emit({"ok": False, "error": {"code": exc.code, "message": exc.message}})
    try:
        selector = json.loads(args.selector) if args.selector else None
        return _emit(inspector.preview(config, args.path, variable=args.variable,
                                       selector=selector, band=args.band,
                                       max_points=args.max_points))
    except (policy.ScientificDenied, inspector.InspectError, json.JSONDecodeError) as exc:
        code = getattr(exc, "code", "selector_invalid")
        message = getattr(exc, "message", str(exc))
        return _emit({"ok": False, "error": {"code": code, "message": message}})


if __name__ == "__main__":
    raise SystemExit(main())
