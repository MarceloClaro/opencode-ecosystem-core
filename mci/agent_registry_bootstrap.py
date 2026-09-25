# -*- coding: utf-8 -*-
"""
Auto-registro de agentes do catálogo no Blackboard (A2A)
=========================================================
Popula o Blackboard (protocolo A2A) com Agent Cards derivados do catálogo
de agentes (`agents/catalog/*.md`) para que o orquestrador possa realizar
matching real de capacidades (CFP) em vez de operar com o blackboard vazio.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL

Fluxo:
1. ``load_catalog_agents`` lê cada ``*.md`` do catálogo e extrai metadados
   (frontmatter YAML com fallbacks) via ``parse_agent_catalog_md``.
2. ``register_catalog_agents`` publica um evento ``agent.register`` no MetaBus
   para cada agente válido — o mesmo caminho usado pelo MCP
   ``mci_register_agent`` — garantindo que os cards respeitem a lógica
   existente do ``Blackboard._handle_registration``.
3. Arquivos malformados (frontmatter ausente/quebrado) são pulados com
   contagem explícita; registro é idempotente (sobrescreve o card).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .metabus import metabus

logger = logging.getLogger("mci-agent-registry-bootstrap")

CATALOG_DEFAULT_DIR = Path("agents/catalog")
_MAX_DESCRIPTION_CHARS = 600
_DEFAULT_CAPABILITY = "agente"


def _extract_name(meta: Dict[str, Any], first_line: str, stem: str) -> str:
    """Nome do frontmatter (ou da primeira linha não vazia, ou do arquivo)."""
    raw = meta.get("name")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    if first_line.strip():
        return first_line.strip()
    return stem


def _extract_description(meta: Dict[str, Any], body_lines: List[str]) -> str:
    """Descrição do frontmatter (aceita block scalar ``>-``) com truncamento."""
    raw = meta.get("description", "")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()[:_MAX_DESCRIPTION_CHARS]
    # Fallback: primeiras linhas do corpo após o frontmatter
    joined = " ".join(line.strip() for line in body_lines if line.strip())
    return joined[:_MAX_DESCRIPTION_CHARS] if joined else ""


def _extract_capabilities(meta: Dict[str, Any]) -> List[str]:
    """Capabilities derivadas de ``skills[].id`` + ``tags`` + chaves de domínio.

    Ordem de prioridade: skills (ids), tags, chaves conhecidas de domínio
    (``domain``, ``category``, ``area``) e o default ``"agente"`` como
    capacidade mínima garantida. Sempre deduplicadas preservando ordem.
    """
    caps: List[str] = []
    skills = meta.get("skills", [])
    if isinstance(skills, list):
        for skill in skills:
            if isinstance(skill, dict) and isinstance(skill.get("id"), str):
                caps.append(skill["id"].strip())
            elif isinstance(skill, str):
                caps.append(skill.strip())
    for key in ("tags", "categories"):
        raw = meta.get(key, [])
        if isinstance(raw, list):
            for tag in raw:
                if isinstance(tag, str) and tag.strip():
                    caps.append(tag.strip())
    for key in ("domain", "category", "area"):
        raw = meta.get(key)
        if isinstance(raw, str) and raw.strip():
            caps.append(raw.strip())

    seen = set()
    unique: List[str] = []
    for cap in caps:
        cap = re.sub(r"\s+", " ", cap).strip().lower()
        if cap and cap not in seen:
            seen.add(cap)
            unique.append(cap)
    if not unique:
        unique.append(_DEFAULT_CAPABILITY)
    return unique


def parse_agent_catalog_md(path: Path, content: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Extrai metadados de um arquivo do catálogo de agentes.

    Retorna ``None`` para arquivos sem frontmatter YAML válido (são pulados).
    O ``agent_id`` é o nome do arquivo sem extensão (slug estável).
    """
    if content is None:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    if not content.startswith("---"):
        return None

    lines = content.splitlines()
    end_idx: Optional[int] = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None

    try:
        meta = yaml.safe_load("\n".join(lines[1:end_idx])) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(meta, dict):
        return None

    body_lines = lines[end_idx + 1:]
    first_line = body_lines[0] if body_lines else ""
    stem = path.stem

    info = {
        "agent_id": stem,
        "name": _extract_name(meta, first_line, stem),
        "description": _extract_description(meta, body_lines),
        "capabilities": _extract_capabilities(meta),
        "schema": {},
    }
    return info


def load_catalog_agents(catalog_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Carrega metadados dos agentes válidos do catálogo."""
    catalog_dir = Path(catalog_dir or CATALOG_DEFAULT_DIR)
    if not catalog_dir.is_dir():
        logger.warning("Diretório do catálogo de agentes não encontrado: %s", catalog_dir)
        return []

    agents: List[Dict[str, Any]] = []
    for path in sorted(catalog_dir.glob("*.md")):
        info = parse_agent_catalog_md(path)
        if info is None:
            logger.debug("Agente pulado (frontmatter inválido): %s", path.name)
            continue
        agents.append(info)
    return agents


def register_catalog_agents(
    catalog_dir: Optional[Path] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Registra os agentes do catálogo no Blackboard via MetaBus.

    Idempotente: re-registrar um agente sobrescreve o card existente
    (mesmo comportamento do MCP ``mci_register_agent``).
    """
    agents = load_catalog_agents(catalog_dir)
    if limit is not None:
        agents = agents[:limit]

    registered = 0
    agent_ids: List[str] = []
    for info in agents:
        metabus.publish(
            "agent.register",
            {
                "agent_id": info["agent_id"],
                "name": info["name"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "schema": info["schema"],
            },
            source_agent="agent-registry-bootstrap",
        )
        registered += 1
        agent_ids.append(info["agent_id"])

    total_files = len(list(Path(catalog_dir or CATALOG_DEFAULT_DIR).glob("*.md")))
    summary: Dict[str, Any] = {
        "registered": registered,
        "skipped": total_files - registered,
        "agent_ids": agent_ids,
    }
    logger.info("Auto-registro concluído: %d agentes registrados, %d pulados.", registered, summary["skipped"])
    return summary


if __name__ == "__main__":  # pragma: no cover
    import json

    result = register_catalog_agents()
    print(json.dumps(result, indent=2, ensure_ascii=False))