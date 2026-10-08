# -*- coding: utf-8 -*-
"""
CliEcosystemBridge — Gerenciador Unificado de CLIs (Antigravity, Claude Code, Codex/OpenCode)
========================================================================================
Ponte multilateral que harmoniza agentes, skills, comandos slash e especificações formais
entre Antigravity CLI (agy), Claude Code CLI e OpenAI Codex / OpenCode CLI.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import os
import sys
import logging
from typing import Dict, Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agents.lazy_catalog import lazy_agent_catalog
from integrations.harness_runtime import HarnessRuntime
from sdd.spec_engine import spec_registry

logger = logging.getLogger("cli-ecosystem-bridge")


class CliEcosystemBridge:
    """Ponte de integração entre Antigravity CLI, Claude Code CLI e Codex / OpenCode CLI."""

    def __init__(self, repo_root: str = REPO_ROOT):
        self.repo_root = repo_root

    def discover_cli_capabilities(self) -> Dict[str, Any]:
        """Inventaria binários e instruções sem confundir instalação e execução."""
        opencode_json = os.path.join(self.repo_root, "opencode.json")
        claude_md = os.path.join(self.repo_root, "CLAUDE.md")
        agents_md = os.path.join(self.repo_root, "AGENTS.md")
        codex_config = os.path.join(self.repo_root, ".codex", "config.toml")
        executors = HarnessRuntime(self.repo_root).status()["executors"]

        agents_count = len(lazy_agent_catalog.list_agents())
        specs_count = len(spec_registry.specs)

        def inventory(ecosystem: str, label: str, config_path: str, config_kind: str) -> Dict[str, Any]:
            state = executors.get(ecosystem, {})
            installed = bool(state.get("installed"))
            return {
                "active": installed,  # Campo legado: inventário de instalação.
                "installed": installed,
                "available": bool(state.get("available")),
                "availability_scope": "external_read_only_executor",
                "availability_reason": state.get("reason"),
                "cli": state.get("cli", ecosystem),
                "cli_path": state.get("path"),
                "label": label,
                "config_path": config_path,
                "config_present": os.path.isfile(config_path),
                "config_kind": config_kind,
                "verification": "installation_only",
                "execution_verified": False,
            }

        return {
            "opencode_codex": {
                **inventory("opencode", "OpenCode CLI (chave legada opencode_codex)", opencode_json, "runtime_configuration"),
                "agents_count": agents_count,
            },
            "claude_code": {
                **inventory("claude", "Claude Code CLI", claude_md, "repository_instructions"),
                "specs_available": specs_count,
                "specs_integrated": 0,  # Nenhuma exportação realizada por este inventário.
            },
            "antigravity_cli": {
                **inventory("antigravity", "Antigravity CLI (agy)", agents_md, "repository_instructions"),
            },
            "codex_cli": {
                **inventory("codex", "OpenAI Codex CLI", codex_config, "repository_configuration"),
                "instructions_path": agents_md,
                "instructions_present": os.path.isfile(agents_md),
            },
        }

    def export_agent_cards_to_claude(self) -> Dict[str, Any]:
        """Produz um preview das cartas; não copia arquivos para o Claude Code."""
        agent_ids = lazy_agent_catalog.list_agents()
        preview = []
        for agent_id in sorted(agent_ids)[:20]:
            preview.append({
                "name": agent_id,
                "role": f"Subagente do ecossistema {agent_id}",
                "mode": "subagent",
            })
        return {
            "status": "preview_only",
            "executed": False,
            "written_count": 0,
            "total_exported": 0,
            "preview_count": len(preview),
            "agents_preview": preview,
        }

    def export_skills_to_antigravity(self) -> Dict[str, Any]:
        """Inventaria skills locais; não instala sidecars nem sincroniza a CLI."""
        skills_dir = os.path.join(self.repo_root, ".opencode", "skills")
        has_skills_dir = os.path.isdir(skills_dir)
        from pathlib import Path
        skill_files = sorted(str(path.relative_to(skills_dir)) for path in Path(skills_dir).rglob("SKILL.md")) if has_skills_dir else []

        return {
            "status": "inventory_only",
            "executed": False,
            "written_count": 0,
            "skills_dir": skills_dir if has_skills_dir else None,
            "inventory_count": len(skill_files),
            "skills_preview": skill_files[:20],
        }

    def get_unified_status(self) -> Dict[str, Any]:
        """Relata instalação das quatro CLIs, sem afirmar execução ou sincronização."""
        caps = self.discover_cli_capabilities()
        claude_sync = self.export_agent_cards_to_claude()
        agy_sync = self.export_skills_to_antigravity()

        missing = [name for name, info in caps.items() if not info["active"]]

        return {
            "unified_status": "installed_unverified" if not missing else "partially_installed",
            "missing": missing,
            "execution_verified": False,
            "verification": "installation_only",
            "network_mcp_path": os.path.join(self.repo_root, "integrations", "ecosystem_mcp.py"),
            "network_mcp_present": os.path.isfile(os.path.join(self.repo_root, "integrations", "ecosystem_mcp.py")),
            "ecosystems": caps,
            "claude_integration": claude_sync,
            "antigravity_integration": agy_sync,
            "total_specs": len(spec_registry.specs),
        }


cli_ecosystem_bridge = CliEcosystemBridge()
