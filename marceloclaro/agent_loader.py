# -*- coding: utf-8 -*-
"""
Agent Loader
============
Carrega definições de agentes a partir de arquivos Markdown com frontmatter YAML
(`agents/*.md`) e os registra no Blackboard como Agent Cards (padrão A2A).

Formato esperado do frontmatter:
---
id: researcher
name: Researcher
description: Agente de pesquisa e síntese de literatura.
capabilities: [search, summarize, cite]
---
(corpo do arquivo = system prompt do agente)

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
import re
import glob
import logging
from typing import Dict, List, Any

logger = logging.getLogger("marceloclaro-loader")
logger.setLevel(logging.INFO)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(REPO_ROOT, "agents")


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    """Parser simples de frontmatter YAML (sem dependências externas)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {"meta": {}, "body": content}

    meta: Dict[str, Any] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Listas inline: [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
            meta[key] = items
        else:
            meta[key] = value.strip("'\"")

    return {"meta": meta, "body": match.group(2).strip()}


def load_agent_definitions(agents_dir: str = AGENTS_DIR) -> List[Dict[str, Any]]:
    """Lê todos os agents/*.md e retorna as definições estruturadas."""
    definitions = []
    for path in sorted(glob.glob(os.path.join(agents_dir, "*.md"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                parsed = _parse_frontmatter(f.read())
            meta = parsed["meta"]
            if not meta.get("id"):
                logger.warning(f"Arquivo sem frontmatter válido ignorado: {path}")
                continue
            definitions.append({
                "agent_id": meta.get("id"),
                "name": meta.get("name", meta.get("id")),
                "description": meta.get("description", ""),
                "capabilities": meta.get("capabilities", []),
                "system_prompt": parsed["body"],
                "source_file": os.path.basename(path),
            })
        except Exception as e:
            logger.error(f"Erro ao carregar {path}: {e}")
    return definitions


def register_all_agents(metabus) -> int:
    """Registra todos os agentes definidos em agents/ no Blackboard via MetaBus."""
    count = 0
    for definition in load_agent_definitions():
        metabus.publish("agent.register", {
            "agent_id": definition["agent_id"],
            "name": definition["name"],
            "description": definition["description"],
            "capabilities": definition["capabilities"],
            "schema": {},
        }, source_agent="marceloclaro.loader")
        count += 1
    logger.info(f"{count} agentes registrados no Blackboard.")
    return count
