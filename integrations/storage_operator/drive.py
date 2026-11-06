"""R1061 — upload e verificação via rclone; purge por arquivo do manifesto."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import approvals, manifest, policy


class PurgeError(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


def _env() -> dict[str, str]:
    env = {key: os.environ[key] for key in ("PATH", "HOME", "XDG_CONFIG_HOME", "RCLONE_CONFIG") if key in os.environ}
    env["NO_COLOR"] = "1"
    return env


def _run(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    options = {"capture_output": True, "text": True, "timeout": 7200,
               "env": _env(), "shell": False, "check": False}
    options.update(kwargs)
    return subprocess.run(argv, **options)


def _rclone() -> str:
    return os.environ.get("STORAGE_OPERATOR_RCLONE", "rclone")


def _files_from(config: policy.StorageConfig, data: dict) -> Path:
    state = Path(config.state_dir).expanduser() / "lists"
    state.mkdir(parents=True, exist_ok=True)
    target = state / f"{data['manifest_sha256']}.txt"
    lines = [item["relpath"] for item in data["files"] if item["upload"]]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def _copy_argv(config: policy.StorageConfig, data: dict, list_path: Path) -> list[str]:
    return [
        _rclone(), "copy", data["root"], data["remote_path"],
        "--files-from", str(list_path), "--checksum",
        "--transfers", str(config.transfers), "--checkers", str(config.transfers),
        "--bwlimit", config.bandwidth, "--no-traverse",
        "--stats-one-line", "--log-level", "ERROR",
    ]


def _check_argv(data: dict, list_path: Path) -> list[str]:
    return [_rclone(), "check", data["root"], data["remote_path"],
            "--files-from", str(list_path), "--checksum", "--one-way"]


def upload(config: policy.StorageConfig, manifest_path: str | Path, token: str) -> dict:
    data = manifest.load_manifest(Path(manifest_path))
    approvals.verify_approval(config, token, "upload", data["manifest_sha256"])
    files = [item for item in data["files"] if item["upload"]]
    if not files:
        return {"ok": False, "error": {"code": "NO_FILES", "message": "manifesto sem arquivos para upload"}}
    list_path = _files_from(config, data)
    result = _run(_copy_argv(config, data, list_path), shell=False)
    if result.returncode != 0:
        return {"ok": False, "error": {"code": "RCLONE_COPY_FAILED",
                                       "message": (result.stderr or result.stdout or "")[-2000:]}}
    check = _run(_check_argv(data, list_path), shell=False)
    if check.returncode != 0:
        return {"ok": False, "partial": True,
                "error": {"code": "RCLONE_CHECK_FAILED",
                          "message": (check.stderr or check.stdout or "")[-2000:]}}
    data["uploaded_at"] = datetime.now(timezone.utc).isoformat()
    data["verified"] = True
    data["verification"] = {"ok": True, "method": "rclone check --checksum --one-way",
                            "at": datetime.now(timezone.utc).isoformat()}
    manifest.write_manifest(Path(manifest_path), data)
    return {"ok": True, "manifest_sha256": data["manifest_sha256"],
            "remote_path": data["remote_path"], "files": len(files),
            "bytes": data["totals"]["bytes"], "verified": True}


def verify(config: policy.StorageConfig, manifest_path: str | Path) -> dict:
    data = manifest.load_manifest(Path(manifest_path))
    list_path = _files_from(config, data)
    result = _run(_check_argv(data, list_path), shell=False)
    ok = result.returncode == 0
    data["verified"] = ok
    data["verification"] = {"ok": ok, "method": "rclone check --checksum --one-way",
                            "at": datetime.now(timezone.utc).isoformat(),
                            "detail": (result.stderr or result.stdout or "")[-1000:] if not ok else None}
    manifest.write_manifest(Path(manifest_path), data)
    return {"ok": ok, "manifest_sha256": data["manifest_sha256"],
            "verified": ok, "detail": data["verification"]["detail"]}


def purge(config: policy.StorageConfig, manifest_path: str | Path, token: str) -> dict:
    data = manifest.load_manifest(Path(manifest_path))
    if not data.get("verified") or not (data.get("verification") or {}).get("ok"):
        raise PurgeError("not_verified", "manifesto sem verificação remota válida")
    approvals.verify_approval(config, token, "purge", data["manifest_sha256"])
    root = policy.validate_root(config, data["root"])
    deleted = []
    for item in data["files"]:
        if not item.get("delete"):
            continue
        target = policy.validate_file(config, root, item["relpath"])
        if item.get("sha256"):
            current = manifest.sha256_file(target)
            if current != item["sha256"]:
                raise PurgeError("file_changed", f"arquivo alterado: {item['relpath']}")
        target.unlink()
        deleted.append({"relpath": item["relpath"], "bytes": item.get("size", 0)})
    data["purged_at"] = datetime.now(timezone.utc).isoformat()
    data["purged"] = deleted
    manifest.write_manifest(Path(manifest_path), data)
    return {"ok": True, "deleted": len(deleted),
            "bytes": sum(item["bytes"] for item in deleted),
            "manifest_sha256": data["manifest_sha256"]}
