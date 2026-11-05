"""R1061 — manifesto determinístico com SHA-256 por arquivo."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import policy

MAX_FILES = 5000
HASH_EXCLUDED = {"manifest_sha256", "created_at", "uploaded_at", "verified",
                 "verification", "purged_at", "purged", "receipt"}


class ManifestError(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sensitive(relpath: str) -> bool:
    return Path(relpath).suffix.casefold() in policy.SENSITIVE_SUFFIXES


def _is_partial(relpath: str) -> bool:
    return Path(relpath).name.casefold().endswith(policy.PARTIAL_SUFFIXES)


def manifest_hash(data: dict) -> str:
    payload = {key: value for key, value in data.items() if key not in HASH_EXCLUDED}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_manifest(config: policy.StorageConfig, root: Path, *, now: float | None = None) -> dict:
    root = policy.validate_root(config, root)
    files: list[dict] = []
    excluded: list[dict] = []
    total_bytes = 0
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d != ".tmp.driveupload"
                   and not (Path(current) / d).is_symlink()]
        for name in sorted(names):
            raw = Path(current) / name
            rel = str(raw.relative_to(root)).replace(os.sep, "/")
            if len(files) + len(excluded) >= MAX_FILES:
                excluded.append({"relpath": rel, "reason": "manifest_limit"})
                continue
            if raw.is_symlink():
                excluded.append({"relpath": rel, "reason": "symlink"})
                continue
            if not raw.is_file():
                continue
            try:
                size = raw.stat().st_size
                mtime = raw.stat().st_mtime
            except OSError:
                excluded.append({"relpath": rel, "reason": "stat_failed"})
                continue
            upload = True
            delete = True
            reason = None
            if rel.casefold().startswith(".tmp.driveupload/"):
                upload = False
                delete = False
                reason = "drive_sync_temp"
            elif name.casefold() in {"desktop.ini", "thumbs.db", ".ds_store"}:
                upload = False
                delete = False
                reason = "system_metadata"
            elif Path(name).suffix.casefold() in {".gdoc", ".gsheet", ".gslides"}:
                upload = False
                delete = False
                reason = "drive_shortcut"
            elif policy.is_excluded(config, rel):
                upload = False
                delete = False
                reason = "excluded_secret"
            elif _is_partial(rel):
                upload = False
                delete = True
                reason = "partial_download"
            elif size > config.max_file_bytes:
                upload = False
                delete = False
                reason = "too_large"
            entry = {
                "relpath": rel, "size": size, "mtime": round(mtime, 3),
                "sha256": sha256_file(raw) if upload else None,
                "sensitive": _sensitive(rel),
                "upload": upload, "delete": delete, "reason": reason,
            }
            files.append(entry)
            if upload:
                total_bytes += size
    folder = policy.remote_folder(root, now=now)
    data: dict[str, Any] = {
        "schema_version": "1.0",
        "root": str(root),
        "remote": config.drive_remote,
        "remote_path": policy.remote_path(config, folder),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "excluded": excluded,
        "totals": {"files": sum(1 for item in files if item["upload"]),
                   "bytes": total_bytes},
        "verified": False,
        "verification": None,
    }
    data["manifest_sha256"] = manifest_hash(data)
    return data


def write_manifest(path: Path, data: dict) -> Path:
    data = dict(data)
    data["manifest_sha256"] = manifest_hash(data)
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_manifest(path: Path) -> dict:
    path = Path(path).expanduser()
    if not path.is_file():
        raise ManifestError("manifest_not_found", "manifesto não encontrado")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError("manifest_invalid", "manifesto inválido") from exc
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise ManifestError("manifest_invalid", "versão de manifesto inválida")
    expected = data.get("manifest_sha256")
    if not isinstance(expected, str) or manifest_hash(data) != expected:
        raise ManifestError("manifest_tampered", "hash do manifesto não confere")
    return data
