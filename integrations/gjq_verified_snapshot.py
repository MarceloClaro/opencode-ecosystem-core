"""Snapshot verificado de nomes de backend GJQ (R1106).

O snapshot é proveniência operacional: data, hash do registro, hash do próprio
snapshot e correspondência entre o nome vivo e o ID canônico. Não é prova de
qualidade científica nem de disponibilidade futura.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from integrations.gjq_backend_registry import BACKENDS, resolve_backend

SOURCE = "https://www.tiangongqs.com/cloud/server"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def registry_sha256() -> str:
    return _sha256([backend.to_dict() for backend in BACKENDS])


def _live_name(item: Any) -> str:
    if isinstance(item, dict):
        for key in ("name", "backend_name", "id", "device_name"):
            if item.get(key):
                return str(item[key])
    for attr in ("name", "backend_name", "id"):
        value = getattr(item, attr, None)
        if callable(value):
            try:
                value = value()
            except Exception:
                value = None
        if value:
            return str(value)
    return str(item)


def _normalize_live(live_backends: Iterable[Any]) -> list[str]:
    return [_live_name(item) for item in live_backends]


def build_verified_snapshot(live_backends: Iterable[Any],
                            generated_at: str | None = None) -> dict[str, Any]:
    names = _normalize_live(live_backends)
    entries: list[dict[str, Any]] = []
    missing: list[str] = []
    ambiguous: list[dict[str, Any]] = []
    matched_ids: set[str] = set()
    for name in names:
        matches = resolve_backend(name)
        if not matches:
            missing.append(name)
            continue
        if len(matches) > 1:
            ambiguous.append({"live_name": name, "matches": [m["id"] for m in matches]})
            continue
        row = matches[0]
        entries.append({
            "registry_id": row["id"],
            "live_name": name,
            "api_name": row.get("api_name"),
            "api_name_verified": bool(row.get("api_name_verified")),
            "family": row.get("family"),
            "qubits": row.get("qubits"),
        })
        matched_ids.add(row["id"])
    entries.sort(key=lambda item: item["registry_id"])
    missing_live = sorted(backend.id for backend in BACKENDS if backend.id not in matched_ids)
    payload = {
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source": SOURCE,
        "registry_sha256": registry_sha256(),
        "registry_count": len(BACKENDS),
        "live_count": len(names),
        "entries": entries,
        "missing_in_registry": sorted(missing),
        "missing_live": missing_live,
        "ambiguous": ambiguous,
    }
    payload["snapshot_sha256"] = _sha256(payload)
    return payload


def write_snapshot(path: str | Path, snapshot: dict[str, Any]) -> Path:
    destino = Path(path)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(f".{destino.name}.tmp")
    temporario.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
    os.replace(temporario, destino)
    return destino


def read_snapshot(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "snapshot_sha256" not in data:
        raise ValueError("snapshot inválido: snapshot_sha256 ausente")
    return data


def compare_snapshot(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    prev_entries = {item["registry_id"]: item for item in previous.get("entries", [])}
    curr_entries = {item["registry_id"]: item for item in current.get("entries", [])}
    prev_names = {item["live_name"] for item in prev_entries.values()}
    curr_names = {item["live_name"] for item in curr_entries.values()}
    renamed = [
        {
            "registry_id": rid,
            "before": prev_entries[rid]["live_name"],
            "after": curr_entries[rid]["live_name"],
        }
        for rid in sorted(set(prev_entries) & set(curr_entries))
        if prev_entries[rid]["live_name"] != curr_entries[rid]["live_name"]
    ]
    api_changed = [
        {
            "registry_id": rid,
            "before": prev_entries[rid].get("api_name"),
            "after": curr_entries[rid].get("api_name"),
        }
        for rid in sorted(set(prev_entries) & set(curr_entries))
        if prev_entries[rid].get("api_name") != curr_entries[rid].get("api_name")
    ]
    prev_missing = set(previous.get("missing_in_registry", []))
    curr_missing = set(current.get("missing_in_registry", []))
    result = {
        "added_live": sorted(curr_names - prev_names),
        "removed_live": sorted(prev_names - curr_names),
        "renamed": renamed,
        "api_name_changed": api_changed,
        "missing_added": sorted(curr_missing - prev_missing),
        "missing_removed": sorted(prev_missing - curr_missing),
        "registry_changed": previous.get("registry_sha256") != current.get("registry_sha256"),
    }
    result["changed"] = any(result[key] for key in (
        "added_live", "removed_live", "renamed", "api_name_changed",
        "missing_added", "missing_removed", "registry_changed",
    ))
    return result
