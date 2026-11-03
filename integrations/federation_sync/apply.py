# -*- coding: utf-8 -*-
"""R1012/R1013 — patch MCP preparado, nunca ativado automaticamente.

Lição R1013 (observada no host): uma entrada MCP no ``opencode.json`` é uma
*tentativa de inicialização*. Servidor cujo pacote não está instalado aparece
como erro na interface, mesmo com ``"enabled": false``. Portanto esta camada
não escreve no config vivo: ela produz ``federation/mcp_patch.json`` com os
blocos prontos e a proveniência. Ativar é ato humano, depois de instalar o
pacote e confirmar que o comando responde.

Descoberta ≠ instalação ≠ ativação ≠ execução.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import time
from typing import Any, Dict, Iterable, List, Optional

from .store import federation_root

PATCH_SCHEMA = "federation-mcp-patch/v1"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _atomic_write(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _launcher_available(command: List[str]) -> bool:
    """Sonda apenas a existência do launcher; não prova que o pacote existe."""

    if not command:
        return False
    first = str(command[0])
    if os.path.sep in first:
        return Path(first).exists()
    return shutil.which(first) is not None


def build_patch(repo_root: Path, *, names: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    candidates_path = federation_root(repo_root) / "mcp_candidates.json"
    candidates = _load(candidates_path) if candidates_path.is_file() else {}
    servers: Dict[str, Dict[str, Any]] = dict(candidates.get("servers") or {})
    provenance: Dict[str, Dict[str, Any]] = dict(candidates.get("provenance") or {})

    config_path = repo_root / "opencode.json"
    config = _load(config_path) if config_path.is_file() else {}
    current: Dict[str, Any] = dict((config or {}).get("mcp") or {})

    requested = list(names) if names else sorted(servers)
    unknown = [name for name in requested if name not in servers]
    selected = [name for name in requested if name in servers]
    existing = [name for name in selected if name in current]
    stage = [name for name in selected if name not in current]

    entries = {}
    preflight = {}
    for name in stage:
        entry = dict(servers[name])
        entry["enabled"] = False
        entries[name] = entry
        preflight[name] = {
            "launcher": (entry.get("command") or [""])[0],
            "launcher_available": _launcher_available(entry.get("command") or []),
            "package_verified": False,
        }

    return {
        "schema": PATCH_SCHEMA,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "registry_digest": candidates.get("registry_digest"),
        "config": str(config_path),
        "requested": len(requested),
        "unknown": unknown,
        "skipped_existing": existing,
        "servers": entries,
        "provenance": {name: provenance.get(name, {}) for name in entries},
        "preflight": preflight,
        "instructions": (
            "Instale o pacote do servidor, confirme que o comando responde e "
            "cole os blocos desejados em opencode.json. Não há ativação "
            "automática: entrada MCP no config é tentativa de inicialização."
        ),
    }


def apply_mcp(
    repo_root: Path,
    *,
    names: Optional[Iterable[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    ``dry_run=True`` (padrão) apenas relata. ``dry_run=False`` grava o patch
    em ``federation/mcp_patch.json``; o ``opencode.json`` nunca é tocado.
    """

    patch = build_patch(repo_root, names=names)
    report: Dict[str, Any] = {
        "status": "dry_run" if dry_run else "staged",
        "dry_run": bool(dry_run),
        "config_untouched": True,
        "requested": patch["requested"],
        "unknown": patch["unknown"],
        "skipped_existing": patch["skipped_existing"],
        "staged": sorted(patch["servers"]),
        "preflight": patch["preflight"],
        "note": patch["instructions"],
    }
    if dry_run:
        return report

    path = federation_root(Path(repo_root).resolve()) / "mcp_patch.json"
    _atomic_write(path, json.dumps(patch, ensure_ascii=False, indent=2) + "\n")
    report["patch"] = str(path)
    return report
