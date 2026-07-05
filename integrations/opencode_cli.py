# -*- coding: utf-8 -*-
"""
OpenCode CLI Integration — Integração com o OpenCode CLI (opencode.ai)
======================================================================
Gera e mantém a configuração `opencode.json` do repositório para que o
OpenCode CLI reconheça:

1. Os 128+ agentes do catálogo (agents/catalog/*.md) como agentes OpenCode
2. Os agentes essenciais (agents/*.md) com protocolo SDD/TDD/metacognição
3. O servidor MCP Metacognitive Interconnect (mci/mcp_server.py)
4. O servidor MCP Antigravity (integrations/antigravity)
5. Comandos customizados (diagnose, maswos, reason, economy)

Uso:
    python3 -m integrations.opencode_cli            # regenera opencode.json
    python3 -m integrations.opencode_cli --check    # valida configuração
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "opencode.json")


def _catalog_agents() -> Dict[str, Any]:
    """Mapeia o catálogo de agentes para o formato de agentes do OpenCode CLI."""
    sys.path.insert(0, ROOT)
    from marceloclaro.catalog_loader import load_catalog_definitions

    agents: Dict[str, Any] = {}
    for d in load_catalog_definitions():
        agents[d["agent_id"]] = {
            "description": d["description"][:200],
            "mode": "subagent",
            "prompt": "{file:./agents/catalog/" + os.path.basename(d["source_file"]) + "}",
            "tools": {"write": True, "edit": True, "bash": True},
        }
    return agents


def _essential_agents() -> Dict[str, Any]:
    """Agentes essenciais do Core (researcher, coder, reviewer, writer, auditor)."""
    agents: Dict[str, Any] = {}
    agents_dir = os.path.join(ROOT, "agents")
    for name in sorted(os.listdir(agents_dir)):
        if name.endswith(".md"):
            agent_id = os.path.splitext(name)[0]
            agents[agent_id] = {
                "description": f"Agente essencial do Core com protocolo SDD/TDD: {agent_id}",
                "mode": "subagent",
                "prompt": "{file:./agents/" + name + "}",
                "tools": {"write": True, "edit": True, "bash": True},
            }
    return agents


def build_config() -> Dict[str, Any]:
    """Monta o opencode.json completo do ecossistema."""
    agents = _essential_agents()
    agents.update(_catalog_agents())
    # O orquestrador primário prevalece sobre eventuais homônimos do catálogo
    agents.pop("marceloclaro", None)

    return {
        "$schema": "https://opencode.ai/config.json",
        "theme": "opencode",
        "instructions": ["AGENTS.md"],
        "agent": {
            "marceloclaro": {
                "description": (
                    "Orquestrador central metacognitivo do ecossistema: percebe "
                    "(memória global), delega (attention routing + blackboard A2A), "
                    "executa (SDD/TDD) e reflete (Reflexion). Ponto de entrada de "
                    "todas as tarefas."
                ),
                "mode": "primary",
                "prompt": "{file:./marceloclaro/PROMPT.md}",
                "tools": {"write": True, "edit": True, "bash": True},
            },
            **agents,
        },
        "mcp": {
            "metacognitive-interconnect": {
                "type": "local",
                "command": ["python3", "mci/mcp_server.py"],
                "enabled": True,
            },
            "antigravity-bridge": {
                "type": "local",
                "command": ["python3", "integrations/antigravity/antigravity_mcp_server.py"],
                "enabled": True,
            },
        },
        "command": {
            "diagnose": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from scanners import diagnostic_pipeline; import json; print(json.dumps(diagnostic_pipeline.run(open('$ARGUMENTS').read() if '$ARGUMENTS' else 'ecosystem'), ensure_ascii=False, indent=2))\"",
                "description": "Roda o pipeline de diagnóstico (5 scanners) sobre um arquivo",
            },
            "maswos": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from academic import maswos_pipeline; print(maswos_pipeline.run('$ARGUMENTS').summary())\"",
                "description": "Executa o pipeline acadêmico MASWOS Qualis A1 para um tópico",
            },
            "reason": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from reasoning import multi_reasoning; r = multi_reasoning.reason('$ARGUMENTS'); print(r.engine, '->', r.conclusion)\"",
                "description": "Raciocina sobre uma consulta com roteamento automático de motor",
            },
            "economy": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from economy import token_economy; import json; print(json.dumps(token_economy.report(), ensure_ascii=False, indent=2))\"",
                "description": "Relatório da economia de tokens (staking, slashing, fees)",
            },
        },
    }


def write_config(path: str = CONFIG_PATH) -> Dict[str, Any]:
    config = build_config()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return config


def check_config(path: str = CONFIG_PATH) -> bool:
    if not os.path.exists(path):
        print("opencode.json não existe — rode sem --check para gerar")
        return False
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    n_agents = len(config.get("agent", {}))
    n_mcp = len(config.get("mcp", {}))
    n_cmd = len(config.get("command", {}))
    print(f"opencode.json OK: {n_agents} agentes, {n_mcp} MCP servers, {n_cmd} comandos")
    return n_agents > 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check_config() else 1)
    cfg = write_config()
    print(f"opencode.json gerado com {len(cfg['agent'])} agentes, "
          f"{len(cfg['mcp'])} MCP servers e {len(cfg['command'])} comandos.")
