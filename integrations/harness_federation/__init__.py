# -*- coding: utf-8 -*-
"""
Federação de artefatos multi-harness (SPEC-935-R621)
===================================================
Ingestão, normalização e portabilidade dos artefatos de agente produzidos nos
ecossistemas **Claude Code**, **Codex (OpenAI)**, **Antigravity (Google)** e
**ChatGPT** para o OpenCode Ecosystem Core.

Fluxo:

    harvester.discover()          # varredura real do disco
      -> [HarnessArtifact]        # modelo canônico, fail-closed
    emitter.emit_all(artifacts)    # portabilidade para .opencode/ + Codex/ChatGPT
    HarnessAttentionHead          # artefato vira candidato do Transformer

O relatório distingue sempre ``discovered`` de ``emitted`` e nunca afirma
sincronização completa havendo artefatos degradados ou raízes ausentes.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .artifact import (
    ECOSYSTEMS,
    KINDS,
    HarnessArtifact,
    build_artifact,
    parse_frontmatter,
    parse_hook_manifest,
    sha256_of,
    slugify,
)
from .emit import HarnessEmitter
from .harvest import HarnessHarvester, REPO_ROOT

__all__ = [
    "ECOSYSTEMS",
    "KINDS",
    "HarnessArtifact",
    "HarnessEmitter",
    "HarnessHarvester",
    "REPO_ROOT",
    "build_artifact",
    "parse_frontmatter",
    "parse_hook_manifest",
    "sha256_of",
    "slugify",
    "harness_inventory",
    "harness_emit",
    "harness_emit_all",
]

__version__ = "1.0.0"


def harness_inventory(repo_root: str = REPO_ROOT, *, home: Optional[str] = None) -> Dict[str, Any]:
    """Atalho: inventário real dos quatro ecossistemas."""

    return HarnessHarvester(repo_root=repo_root, home=home).inventory()


def harness_emit(artifact: HarnessArtifact, repo_root: str = REPO_ROOT, *, dry_run: bool = False) -> Dict[str, Any]:
    """Atalho: emite um único artefato no destino correspondente ao seu ``kind``."""

    emitter = HarnessEmitter(repo_root=repo_root, dry_run=dry_run)
    if artifact.kind == "skill":
        return emitter.emit_skill(artifact)
    if artifact.kind == "agent":
        return emitter.emit_agent(artifact)
    if artifact.kind == "hook":
        return emitter.emit_hooks(artifact)
    if artifact.kind == "plugin":
        return emitter.export_codex_plugin(artifact)
    if artifact.kind == "prompt_pack":
        return emitter.export_chatgpt_instructions(artifact)
    return {"status": "skipped", "artifact_id": artifact.artifact_id,
            "reason": f"sem emissor para kind={artifact.kind}"}


def harness_emit_all(
    repo_root: str = REPO_ROOT,
    *,
    kinds: Optional[Sequence[str]] = None,
    dry_run: bool = False,
    require_license: bool = False,
    home: Optional[str] = None,
) -> Dict[str, Any]:
    """Atalho: descoberta seguida de emissão em lote, com relatório consolidado."""

    harvester = HarnessHarvester(repo_root=repo_root, home=home)
    artifacts: List[HarnessArtifact] = harvester.discover()
    emitter = HarnessEmitter(repo_root=repo_root, dry_run=dry_run)
    report = emitter.emit_all(
        artifacts,
        kinds=tuple(kinds) if kinds else None,
        require_license=require_license,
    )
    report["roots_scanned"] = harvester._scanned_roots  # noqa: SLF001 - relatório da mesma classe
    report["roots_missing"] = harvester._missing_roots  # noqa: SLF001
    return report
