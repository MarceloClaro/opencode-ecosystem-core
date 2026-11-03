# -*- coding: utf-8 -*-
"""R1012 — persistência, diff e relatório do registro federado.

Escritas são atômicas (``tmp`` + ``os.replace``) e idempotentes: duas coletas
sem mudança de fonte produzem o mesmo ``digest``. Nada aqui habilita servidor
MCP; a geração de candidatos é sempre ``enabled: false``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any, Dict, Iterable, List, Optional

from .model import FederatedItem, canonical_json, digest_items, sha256_text
from .sources import collect

SCHEMA = "federation-registry/v1"
CANDIDATES_SCHEMA = "federation-mcp-candidates/v1"
REPORT_LIMIT = 40


def federation_root(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / "federation"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# ----------------------------------------------------------------------
# Candidatos MCP
# ----------------------------------------------------------------------
def _server_entry(server: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    entry: Dict[str, Any] = {}
    if server.get("command"):
        entry["type"] = "local"
        entry["command"] = list(server["command"]) + list(server.get("args") or [])
    elif server.get("url"):
        entry["type"] = "remote"
        entry["url"] = server["url"]
    else:
        return None
    entry["enabled"] = False
    return entry


def build_candidates(items: Iterable[FederatedItem]) -> Dict[str, Any]:
    """Servidores MCP admitidos, prontos para registro desativado."""

    servers: Dict[str, Dict[str, Any]] = {}
    provenance: Dict[str, Dict[str, Any]] = {}
    for item in sorted(items, key=lambda i: i.item_id):
        if item.kind != "mcp" or item.status != "admitted":
            continue
        if item.install_mode != "register_disabled":
            continue
        server = (item.metadata or {}).get("server")
        if not isinstance(server, dict):
            continue
        entry = _server_entry(server)
        if not entry:
            continue
        name = item.name
        if name in servers:
            suffix = item.ecosystem
            name = f"{name}-{suffix}"
            counter = 2
            while name in servers:
                name = f"{item.name}-{suffix}-{counter}"
                counter += 1
        servers[name] = entry
        provenance[name] = {
            "item_id": item.item_id,
            "ecosystem": item.ecosystem,
            "license": item.license,
            "source_uri": item.source_uri,
            "content_sha256": item.content_sha256,
            "notes": "Registro desativado. Habilitar exige ato humano (ver R1012-5).",
        }
    return {"servers": servers, "provenance": provenance}


# ----------------------------------------------------------------------
# Diff
# ----------------------------------------------------------------------
def _diff(previous: Optional[Dict[str, Any]], items: List[FederatedItem]) -> Dict[str, Any]:
    old = {}
    if isinstance(previous, dict):
        for entry in previous.get("items") or ():
            if isinstance(entry, dict) and entry.get("id"):
                old[str(entry["id"])] = str(entry.get("content_sha256") or "")
    new = {item.item_id: item.content_sha256 for item in items}
    return {
        "added": sorted(set(new) - set(old)),
        "removed": sorted(set(old) - set(new)),
        "changed": sorted(key for key in set(new) & set(old) if new[key] != old[key]),
    }


# ----------------------------------------------------------------------
# Sync
# ----------------------------------------------------------------------
def sync(
    repo_root: Path,
    *,
    home: Optional[Path] = None,
    write: bool = True,
) -> Dict[str, Any]:
    """Coleta, classifica e (por padrão) grava o registro federado."""

    repo_root = Path(repo_root).resolve()
    root = federation_root(repo_root)
    registry_path = root / "registry.json"
    previous = _load(registry_path)

    items = collect(repo_root, home=home)
    digest = digest_items(items)
    diff = _diff(previous, items)
    counts: Dict[str, Dict[str, int]] = {"ecosystem": {}, "kind": {}, "status": {}}
    for item in items:
        for bucket, key in (("ecosystem", item.ecosystem), ("kind", item.kind), ("status", item.status)):
            counts[bucket][key] = counts[bucket].get(key, 0) + 1
    for bucket in counts:
        counts[bucket] = dict(sorted(counts[bucket].items()))

    candidates = build_candidates(items)
    registry = {
        "schema": SCHEMA,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo": str(repo_root),
        "home": str(Path(home or os.path.expanduser("~")).resolve()),
        "digest": digest,
        "counts": counts,
        "total": len(items),
        "diff": {key: len(value) for key, value in diff.items()},
        "items": [item.to_dict() for item in items],
    }

    result: Dict[str, Any] = {
        "status": "ok",
        "written": bool(write),
        "digest": digest,
        "previous_digest": (previous or {}).get("digest") if isinstance(previous, dict) else None,
        "total": len(items),
        "counts": counts,
        "diff": diff,
        "candidates": len(candidates["servers"]),
        "registry": str(registry_path),
        "path": str(root),
    }
    if not write:
        return result

    _atomic_write(registry_path, json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(
        root / "mcp_candidates.json",
        json.dumps({
            "schema": CANDIDATES_SCHEMA,
            "generated_at": registry["generated_at"],
            "registry_digest": digest,
            "servers": candidates["servers"],
            "provenance": candidates["provenance"],
        }, ensure_ascii=False, indent=2) + "\n",
    )
    _atomic_write(root / "report.md", _report(registry, candidates, diff))
    with open(root / "audit.jsonl", "a", encoding="utf-8") as stream:
        stream.write(canonical_json({
            "ts": registry["generated_at"], "action": "sync", "digest": digest,
            "total": len(items), "counts": counts,
            "diff": {key: len(value) for key, value in diff.items()},
        }) + "\n")
    result["report"] = str(root / "report.md")
    result["candidates_file"] = str(root / "mcp_candidates.json")
    return result


# ----------------------------------------------------------------------
# Relatório
# ----------------------------------------------------------------------
def _table(counter: Dict[str, int]) -> str:
    if not counter:
        return "| — | 0 |\n"
    return "".join(f"| {key} | {value} |\n" for key, value in counter.items())


def _report(registry: Dict[str, Any], candidates: Dict[str, Any], diff: Dict[str, List[str]]) -> str:
    counts = registry["counts"]
    items = registry["items"]
    quarantined = [item for item in items if item["status"] in {"quarantined", "blocked", "degraded"}]
    lines = [
        "# Federação universal de artefatos — relatório R1012",
        "",
        f"Gerado em `{registry['generated_at']}` pelo primário **marceloclaro**.",
        "",
        f"- Digest do registro: `{registry['digest']}`",
        f"- Total de artefatos: **{registry['total']}**",
        f"- Candidatos MCP desativados: **{len(candidates['servers'])}**",
        "",
        "## Por ecossistema",
        "",
        "| Ecossistema | Total |",
        "|---|---|",
        _table(counts.get("ecosystem", {})),
        "## Por tipo",
        "",
        "| Tipo | Total |",
        "|---|---|",
        _table(counts.get("kind", {})),
        "## Por estado",
        "",
        "| Estado | Total |",
        "|---|---|",
        _table(counts.get("status", {})),
        "## Mudanças nesta coleta",
        "",
        f"- Adicionados: {len(diff['added'])}",
        f"- Removidos: {len(diff['removed'])}",
        f"- Alterados: {len(diff['changed'])}",
        "",
        "## Itens que exigem decisão humana",
        "",
        "Nenhum item abaixo foi habilitado. Licença ausente nunca é completada por suposição.",
        "",
        "| ID | Estado | Motivos |",
        "|---|---|---|",
    ]
    for item in quarantined[:REPORT_LIMIT]:
        lines.append(f"| `{item['id']}` | {item['status']} | {', '.join(item['reasons']) or '—'} |")
    if len(quarantined) > REPORT_LIMIT:
        lines.append(f"| … | … | mais {len(quarantined) - REPORT_LIMIT} itens no registro |")
    lines += [
        "",
        "## Como habilitar um MCP",
        "",
        "```bash",
        "python3 -m marceloclaro.cli federacao apply            # dry-run",
        "python3 -m marceloclaro.cli federacao apply --apply    # grava em opencode.json (enabled: false)",
        "```",
        "",
        "Habilitar (`enabled: true`) é ato humano e exige `--enable --yes`;",
        "executar o servidor é etapa distinta e não é comprovada por este relatório.",
        "",
        "> Registro não é execução. Contagem não é certificação. Licença declarada",
        "> no manifesto não substitui parecer jurídico.",
        "",
    ]
    return "\n".join(lines)


# ----------------------------------------------------------------------
# Leitura
# ----------------------------------------------------------------------
def load_registry(repo_root: Path) -> Dict[str, Any]:
    return _load(federation_root(repo_root) / "registry.json") or {}


def load_items(repo_root: Path) -> List[FederatedItem]:
    registry = load_registry(repo_root)
    return [FederatedItem.from_dict(entry) for entry in registry.get("items") or ()]


def status(repo_root: Path) -> Dict[str, Any]:
    registry = load_registry(repo_root)
    root = federation_root(repo_root)
    activated = 0
    activated_path = root / "activated.json"
    if activated_path.is_file():
        try:
            activated = len((json.loads(activated_path.read_text(encoding="utf-8")) or {}).get("servers") or {})
        except (OSError, ValueError):
            activated = 0
    return {
        "status": "ok" if registry else "missing",
        "path": str(root),
        "federated_mcp_activated": activated,
        "generated_at": registry.get("generated_at"),
        "digest": registry.get("digest"),
        "total": registry.get("total", 0),
        "counts": registry.get("counts", {}),
        "candidates_file": str(root / "mcp_candidates.json"),
        "report": str(root / "report.md"),
        "registry": str(root / "registry.json"),
    }


def verify(repo_root: Path) -> Dict[str, Any]:
    """Reconfere o digest do registro contra o conteúdo persistido."""

    registry = load_registry(repo_root)
    if not registry:
        return {"status": "missing", "ok": False}
    items = [FederatedItem.from_dict(entry) for entry in registry.get("items") or ()]
    recomputed = digest_items(items)
    stored = str(registry.get("digest") or "")
    return {
        "status": "ok" if recomputed == stored else "mismatch",
        "ok": recomputed == stored,
        "stored": stored,
        "recomputed": recomputed,
        "total": len(items),
    }
