"""R662: contratos locais de integração e handoff, sem executar artefatos."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

_ARTIFACT_ID = re.compile(r"[A-Za-z0-9._:-]{1,240}\Z")
_FILE_REF = re.compile(r"\{file:([^}]+)\}")


def validate_artifact_id(value: str) -> str:
    if not isinstance(value, str) or ".." in value or not _ARTIFACT_ID.fullmatch(value):
        raise ValueError("Informe um ID de artefato registrado, com até 240 caracteres.")
    return value


class CoreIntegrationService:
    """Lê configuração e metadados. Disponibilidade não comprova execução."""

    def __init__(self, repo_root: str | Path, *, registry: Any = None):
        self.repo_root = Path(repo_root).resolve()
        self._registry = registry

    @property
    def registry(self):
        if self._registry is None:
            from transformer.harness_head import HarnessRegistry
            self._registry = HarnessRegistry(repo_root=str(self.repo_root), kinds=None)
        return self._registry

    def status(self) -> dict[str, Any]:
        issues: list[dict[str, str]] = []

        def issue(code: str, component: str, detail: str, severity: str = "error"):
            issues.append({"code": code, "component": component,
                           "detail": detail, "severity": severity})

        def local_reference(raw: str, component: str, missing_code: str):
            path = (self.repo_root / raw).resolve()
            if not path.is_relative_to(self.repo_root):
                issue("reference_outside_repository", component, "Referência fora do repositório.")
            elif not path.is_file():
                issue(missing_code, component, "Arquivo de entrada ausente: " + raw)

        config: dict[str, Any] = {}
        try:
            config_path = self.repo_root / "opencode.json"
            if config_path.stat().st_size > 5 * 1024 * 1024:
                raise ValueError("Configuração excede 5 MiB.")
            candidate = json.loads(config_path.read_text(encoding="utf-8-sig"))
            if not isinstance(candidate, dict):
                raise ValueError("Configuração deve ser um objeto JSON.")
            config = candidate
        except (OSError, ValueError):
            issue("config_unreadable", "cli", "opencode.json ausente, ilegível ou inválido.")

        sections: dict[str, dict[str, Any]] = {}
        for name, component in (("agent", "agents"), ("command", "cli"), ("mcp", "mcp")):
            section = config.get(name, {})
            if not isinstance(section, dict):
                issue("config_section_invalid", component, "Seção inválida: " + name)
                section = {}
            sections[name] = section
        agents, commands, servers = (sections[key] for key in ("agent", "command", "mcp"))
        primary = config.get("default_agent")
        if not isinstance(primary, str) or primary not in agents or not isinstance(agents.get(primary), dict):
            issue("primary_agent_missing", "agents", "Agente primário não consta da configuração.")
        elif agents[primary].get("mode") != "primary":
            issue("primary_agent_mode", "agents", "O ponto de entrada deve ter mode=primary.")
        instructions = config.get("instructions", [])
        if not isinstance(instructions, list) or any(not isinstance(p, str) for p in instructions):
            issue("instructions_invalid", "cli", "instructions deve ser uma lista de caminhos.")
        else:
            for raw in instructions:
                if not any(char in raw for char in "*?["):
                    local_reference(raw, "cli", "instruction_missing")
        for name, agent in agents.items():
            if not isinstance(agent, dict):
                issue("agent_invalid", "agents", "Registro inválido: " + name)
                continue
            prompt = agent.get("prompt", "")
            if not isinstance(prompt, str):
                issue("agent_prompt_invalid", "agents", "Prompt inválido: " + name)
                continue
            for reference in _FILE_REF.findall(prompt):
                local_reference(reference, "agents", "agent_prompt_missing")
        for name, command in commands.items():
            if not isinstance(command, dict):
                issue("command_invalid", "cli", "Comando inválido: " + name)
                continue
            target = command.get("agent", primary)
            if not isinstance(target, str) or target not in agents:
                issue("command_agent_missing", "agents", "Comando sem agente configurado: " + name)

        mcp_entries = []
        for name, server in servers.items():
            if not isinstance(server, dict):
                issue("mcp_config_invalid", "mcp", "Servidor inválido: " + name)
                continue
            if server.get("enabled", True) is False:
                continue
            if server.get("type") == "remote":
                mcp_entries.append({"name": name, "kind": "remote", "verification": "configuration_only"})
                continue
            command = server.get("command")
            if (server.get("type") != "local" or not isinstance(command, list) or
                    not command or any(not isinstance(arg, str) or not arg for arg in command)):
                issue("mcp_command_invalid", "mcp", "Entrada local inválida: " + name)
                continue
            executable = command[0]
            from integrations.harness_runtime import HarnessRuntime
            executable_path = (str(self.repo_root / executable)
                               if not Path(executable).is_absolute() and ("/" in executable or "\\" in executable)
                               else executable)
            installed = HarnessRuntime(str(self.repo_root)).resolve_cli_path(executable_path) is not None
            if not installed:
                issue("mcp_launcher_unavailable", "mcp", "Iniciador indisponível: " + name, "warning")
            for argument in command[1:]:
                if argument.endswith(".py"):
                    local_reference(argument, "mcp", "mcp_entry_missing")
            mcp_entries.append({"name": name, "kind": "local", "launcher_installed": installed,
                                "verification": "configuration_only"})

        from hooks.engine import EVENTS
        try:
            inventory = self.registry.inventory()
        except (OSError, ValueError, RuntimeError):
            inventory = {}
            issue("artifact_inventory_unavailable", "plugins", "Inventário de artefatos indisponível.")
        by_kind = inventory.get("by_kind", {})
        components = {
            "agents": {"configured_count": len(agents), "primary": primary},
            "hooks": {"events": list(EVENTS), "verification": "contract_only"},
            "mcp": {"configured_count": len(servers), "entries": mcp_entries},
            "cli": {"command_count": len(commands), "verification": "configuration_only"},
            "plugins": {"count": by_kind.get("plugin", 0), "verification": "discovery_only"},
            "skills": {"count": by_kind.get("skill", 0), "verification": "discovery_only"},
        }
        return {"spec_id": "SPEC-935-R662", "orchestrator": "marceloclaro",
                "status": "error" if any(i["severity"] == "error" for i in issues) else "config_checked",
                "executed": False, "execution_verified": False,
                "components": components, "issues": issues,
                "ecosystems_present": inventory.get("ecosystems_present", []),
                "ecosystems_missing": inventory.get("ecosystems_missing", [])}

    def handoff(self, artifact_id: str) -> dict[str, Any]:
        return self.registry.plan_handoff(validate_artifact_id(artifact_id))

    def skill_plan(self, skill_name: str) -> dict[str, Any]:
        from reversa_universal.skill_dispatch import ReversaSkillDispatcher
        decision = ReversaSkillDispatcher(self.repo_root).plan(skill_name).to_dict()
        result = {**decision, "spec_id": "SPEC-935-R662", "status": "instruction_only" if decision["found"] else "not_found",
                  "orchestrator": "marceloclaro", "executed": False, "execution_verified": False}
        if decision["found"]:
            source = Path(decision["skill_path"])
            with source.open("rb") as stream:
                raw = stream.read(128 * 1024 + 1)
            if len(raw) > 128 * 1024:
                return {**result, "status": "refused", "reason": "SKILL.md excede 128 KiB."}
            result.update({"skill_document": raw.decode("utf-8"),
                           "source_file_sha256": hashlib.sha256(raw).hexdigest(),
                           "instruction_root": str(source.parent)})
        return result
