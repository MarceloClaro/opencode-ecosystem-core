# -*- coding: utf-8 -*-
"""Manifesto SHA-256 do dossiê de data storytelling (SPEC-935-R1003)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .util import SCHEMA_VERSION, DataStoryError, canonical_json, sha256_bytes, sha256_text

Resolver = Mapping[str, Any] | Callable[[str], Any]


def _to_bytes(value: Any, *, name: str) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    raise DataStoryError(
        "invalid_artifact", f"Artefato {name!r} deve ser str ou bytes."
    )


def build_manifest(
    artifacts: Mapping[str, Any], *, metadata: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Constrói manifesto determinístico (sem relógio) com hash por artefato."""
    if not isinstance(artifacts, Mapping) or not artifacts:
        raise DataStoryError("empty_manifest", "Manifesto exige ao menos um artefato.")
    normalized = {str(key): value for key, value in artifacts.items()}
    items = []
    for name in sorted(normalized):
        payload = _to_bytes(normalized[name], name=name)
        items.append({
            "name": name,
            "sha256": sha256_bytes(payload),
            "bytes": len(payload),
        })
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "data_storytelling_manifest",
        "artifacts": items,
        "metadata": dict(metadata or {}),
    }
    body["manifest_sha256"] = sha256_text(canonical_json(body))
    return body


def verify_manifest(manifest: Mapping[str, Any], resolver: Resolver) -> dict[str, Any]:
    """Confere hashes e presença; não executa nenhum artefato."""
    if not isinstance(manifest, Mapping) or not isinstance(manifest.get("artifacts"), list):
        raise DataStoryError("invalid_manifest", "Manifesto inválido.")
    if not isinstance(resolver, Mapping) and not callable(resolver):
        raise DataStoryError("invalid_resolver", "Resolver deve ser mapeamento ou função.")

    missing: list[str] = []
    mismatches: list[dict[str, Any]] = []
    checked = 0
    for item in manifest["artifacts"]:
        if not isinstance(item, Mapping):
            raise DataStoryError("invalid_manifest", "Item de artefato inválido.")
        name = str(item.get("name"))
        expected = str(item.get("sha256"))
        if isinstance(resolver, Mapping):
            if name not in resolver:
                missing.append(name)
                continue
            value = resolver[name]
        else:
            try:
                value = resolver(name)
            except Exception:  # noqa: BLE001 — ausência é dado de auditoria
                missing.append(name)
                continue
        try:
            actual = sha256_bytes(_to_bytes(value, name=name))
        except DataStoryError:
            mismatches.append({"name": name, "expected": expected, "actual": None})
            continue
        checked += 1
        if actual != expected:
            mismatches.append({"name": name, "expected": expected, "actual": actual})

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "data_storytelling_manifest_verification",
        "ok": not missing and not mismatches,
        "checked": checked,
        "missing": missing,
        "mismatches": mismatches,
        "manifest_sha256": manifest.get("manifest_sha256"),
    }
