"""R1061 — relatório de espaço e inventário somente leitura."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from . import policy


def report(config: policy.StorageConfig) -> dict:
    roots = []
    for raw in config.allowed_roots:
        try:
            root = policy.validate_root(config, raw)
            usage = shutil.disk_usage(root)
            roots.append({"root": str(root), "total": usage.total,
                          "used": usage.used, "free": usage.free,
                          "percent": round(usage.used * 100 / usage.total, 1) if usage.total else None})
        except (policy.StorageDenied, OSError) as exc:
            roots.append({"root": str(raw), "error": getattr(exc, "reason", str(exc))})
    return {"ok": True, "roots": roots}


def scan(config: policy.StorageConfig, root: str | Path | None = None) -> dict:
    target = policy.validate_root(config, root or config.allowed_roots[0])
    files = 0
    total = 0
    by_ext: dict[str, int] = {}
    candidates: list[dict] = []
    largest: list[dict] = []
    for current, dirs, names in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if d != ".tmp.driveupload"
                   and not (Path(current) / d).is_symlink()]
        for name in names:
            raw = Path(current) / name
            rel = str(raw.relative_to(target)).replace(os.sep, "/")
            if raw.is_symlink():
                candidates.append({"relpath": rel, "reason": "symlink"})
                continue
            if not raw.is_file():
                continue
            try:
                size = raw.stat().st_size
            except OSError:
                continue
            files += 1
            total += size
            suffix = Path(name).suffix.casefold() or "(sem extensão)"
            by_ext[suffix] = by_ext.get(suffix, 0) + size
            if policy.is_excluded(config, rel):
                candidates.append({"relpath": rel, "size": size, "reason": "excluded_secret"})
            elif Path(name).name.casefold().endswith(policy.PARTIAL_SUFFIXES):
                candidates.append({"relpath": rel, "size": size, "reason": "partial_download"})
            largest.append({"relpath": rel, "size": size})
    largest.sort(key=lambda item: item["size"], reverse=True)
    return {
        "ok": True,
        "root": str(target),
        "totals": {"files": files, "bytes": total},
        "by_extension": dict(sorted(by_ext.items(), key=lambda item: item[1], reverse=True)),
        "candidates": candidates,
        "largest": largest[:20],
    }
