# -*- coding: utf-8 -*-
"""
Catalog Loader — 128+ Agentes Especializados
============================================
Carrega o catálogo completo de agentes especializados portados do
OpenCode_Ecosystem original (agents/catalog/*.md) e registra cada um
no Blackboard com um Agent Card (A2A).

O frontmatter do catálogo original usa o formato:
    ---
    name: 00_editor_chefe_phd
    type: maswos-agent
    category: academic
    location: ...
    ---

Capacidades são derivadas de `category` + `type` + heurística sobre o nome,
permitindo que o AttentionRouter roteie tarefas para agentes do catálogo.
"""

import os
import re
import glob
from typing import Any, Dict, List

CATALOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents", "catalog"
)

# Mapeamento categoria -> capacidades base
CATEGORY_CAPABILITIES = {
    "academic": ["academic_writing", "qualis_a1", "research"],
    "research": ["research", "search", "literature_review"],
    "engineering": ["python", "code_review", "architecture"],
    "quantum": ["quantum", "qiskit", "simulation"],
    "orchestration": ["orchestration", "coordination"],
    "audit": ["audit", "verification", "compliance"],
    "data": ["data_analysis", "statistics"],
    "legal": ["legal", "juridico"],
    "health": ["health", "medical"],
}

# Heurísticas sobre o nome do agente -> capacidades extras
NAME_HINTS = {
    "estatistica": ["statistics", "data_analysis"],
    "metodologia": ["methodology", "reproducibility"],
    "revisao": ["review", "literature_review"],
    "citac": ["citations", "abnt"],
    "abnt": ["abnt", "citations"],
    "qualis": ["qualis_a1", "audit"],
    "quantum": ["quantum", "simulation"],
    "orchestrator": ["orchestration"],
    "orquestr": ["orchestration"],
    "auditoria": ["audit", "verification"],
    "codigo": ["python", "code_review"],
    "code": ["python", "code_review"],
    "dados": ["data_analysis"],
    "data": ["data_analysis"],
    "visualiza": ["visualization"],
    "abstract": ["academic_writing"],
    "resumo": ["academic_writing"],
    "editor": ["editorial", "academic_writing"],
    "discussao": ["academic_writing", "argumentation"],
    "resultados": ["academic_writing", "data_analysis"],
    "conclusao": ["academic_writing"],
    "seguranca": ["security"],
    "security": ["security"],
    "scanner": ["diagnostics", "audit"],
    "trust": ["trust", "security"],
    "reasoning": ["reasoning"],
    "raciocinio": ["reasoning"],
    "summarizer": ["summarize", "document_analysis"],
    "sumariz": ["summarize", "document_analysis"],
    "email": ["drafting", "communication"],
    "research": ["research", "search"],
    "legal": ["legal", "juridico"],
}


def _parse_frontmatter(content: str) -> Dict[str, str]:
    """Extrai frontmatter YAML simples (chave: valor) sem dependências externas."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    meta: Dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
    return meta


def _derive_capabilities(name: str, meta: Dict[str, str]) -> List[str]:
    caps: List[str] = []
    category = (meta.get("category") or "").lower()
    caps.extend(CATEGORY_CAPABILITIES.get(category, []))
    agent_type = (meta.get("type") or "").lower()
    if "maswos" in agent_type:
        caps.append("maswos")
    lowered = name.lower()
    for hint, extra in NAME_HINTS.items():
        if hint in lowered:
            caps.extend(extra)
    if not caps:
        caps = ["general"]
    # dedup preservando ordem
    seen = set()
    unique = []
    for c in caps:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def load_catalog_definitions(catalog_dir: str = CATALOG_DIR) -> List[Dict[str, Any]]:
    """Lê agents/catalog/*.md e retorna definições normalizadas."""
    definitions: List[Dict[str, Any]] = []
    for path in sorted(glob.glob(os.path.join(catalog_dir, "*.md"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        meta = _parse_frontmatter(content)
        name = meta.get("name") or os.path.splitext(os.path.basename(path))[0]
        # descrição: primeira linha não vazia após o frontmatter que não seja heading
        body = re.sub(r"^---.*?---\s*", "", content, flags=re.DOTALL)
        desc = ""
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("**"):
                desc = line
                break
        definitions.append({
            "agent_id": name,
            "name": name.replace("_", " ").title(),
            "description": desc or f"Agente especializado do catálogo: {name}",
            "capabilities": _derive_capabilities(name, meta),
            "category": meta.get("category", "general"),
            "type": meta.get("type", "specialist"),
            "source_file": path,
        })
    return definitions


def register_catalog_agents(metabus) -> int:
    """Registra todos os agentes do catálogo no Blackboard via MetaBus.

    Retorna o número de agentes registrados.
    """
    count = 0
    for definition in load_catalog_definitions():
        metabus.publish("agent.register", {
            "agent_id": definition["agent_id"],
            "name": definition["name"],
            "description": definition["description"],
            "capabilities": definition["capabilities"],
            "metadata": {
                "category": definition["category"],
                "type": definition["type"],
                "origin": "OpenCode_Ecosystem/agents",
            },
        }, source_agent="catalog_loader")
        count += 1
    return count
