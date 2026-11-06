"""CLI local do storage-operator; aprovação só é emitida aqui."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import approvals, drive, inventory, manifest, policy


def _emit(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok", True) else 1


def _plan(config: policy.StorageConfig, root: str | None) -> dict:
    target = policy.validate_root(config, root or config.allowed_roots[0])
    data = manifest.build_manifest(config, target)
    state = Path(config.state_dir).expanduser() / "manifests"
    state.mkdir(parents=True, exist_ok=True)
    path = state / f"{data['manifest_sha256']}.json"
    manifest.write_manifest(path, data)
    return {"ok": True, "manifest_path": str(path),
            "manifest_sha256": data["manifest_sha256"], "root": data["root"],
            "remote_path": data["remote_path"], "totals": data["totals"],
            "files": [{"relpath": f["relpath"], "size": f["size"], "upload": f["upload"],
                       "delete": f["delete"], "sensitive": f["sensitive"], "reason": f["reason"]}
                      for f in data["files"]],
            "excluded": data["excluded"]}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="storage-operator", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("report")
    scan = sub.add_parser("scan")
    scan.add_argument("--root")
    plan = sub.add_parser("plan")
    plan.add_argument("--root")
    upload = sub.add_parser("upload")
    upload.add_argument("--manifest", required=True)
    upload.add_argument("--approval-token", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--manifest", required=True)
    purge = sub.add_parser("purge")
    purge.add_argument("--manifest", required=True)
    purge.add_argument("--approval-token", required=True)
    approve = sub.add_parser("approve")
    approve.add_argument("--command", dest="approved_command", choices=("upload", "purge"), required=True)
    approve.add_argument("--manifest", required=True)
    approve.add_argument("--ttl", type=int)
    approve.add_argument("--confirm", action="store_true")
    sub.add_parser("config")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = policy.load_config()
    if args.command == "config":
        return _emit({"ok": True, "allowed_roots": list(config.allowed_roots),
                      "drive_remote": config.drive_remote,
                      "drive_parent": config.drive_parent,
                      "state_dir": str(Path(config.state_dir).expanduser()),
                      "rclone": __import__("shutil").which("rclone"),
                      "external_validation": False})
    if args.command == "status":
        return _emit({"ok": True, "roots": list(config.allowed_roots),
                      "rclone": bool(__import__("shutil").which("rclone")),
                      "drive_remote": config.drive_remote})
    if args.command == "report":
        return _emit({"ok": True, **inventory.report(config)})
    if args.command == "scan":
        return _emit(inventory.scan(config, args.root))
    if args.command == "plan":
        return _emit(_plan(config, args.root))
    if args.command == "approve":
        if not args.confirm:
            return _emit({"ok": False, "error": {"code": "confirm_required",
                                                 "message": "repita com --confirm após revisar o manifesto"}})
        try:
            data = manifest.load_manifest(Path(args.manifest))
            issued = approvals.issue_approval(config, args.approved_command,
                                              data["manifest_sha256"], ttl_seconds=args.ttl)
        except (approvals.ApprovalError, manifest.ManifestError) as exc:
            return _emit({"ok": False, "error": {"code": exc.code, "message": exc.reason}})
        return _emit({"ok": True, **issued})
    try:
        if args.command == "upload":
            return _emit(drive.upload(config, args.manifest, args.approval_token))
        if args.command == "verify":
            return _emit(drive.verify(config, args.manifest))
        if args.command == "purge":
            return _emit(drive.purge(config, args.manifest, args.approval_token))
    except (approvals.ApprovalError, manifest.ManifestError, policy.StorageDenied, drive.PurgeError) as exc:
        return _emit({"ok": False, "error": {"code": exc.code, "message": exc.reason}})
    return _emit({"ok": False, "error": {"code": "unknown", "message": "comando desconhecido"}})


if __name__ == "__main__":
    raise SystemExit(main())
