# -*- coding: utf-8 -*-
"""
Catalog Loader — 128+ Agentes Especializados (A2A v1.0 + Semantic Matching)
============================================================================
Carrega o catálogo completo de agentes especializados portados do
OpenCode_Ecosystem original (agents/catalog/*.md) e registra cada um
no Blackboard com um Agent Card (A2A v1.0 — Google/Linux Foundation 2025).

Melhorias implementadas (R347):
  1. Agent Card A2A v1.0 — skills[], tags, examples, capabilities estendidas
  2. Semantic Matching — embeddings via LiteRT-LM/Colibri (fallback hash)
  3. Skill Handbook — confiança per-skill para roteamento consciente

O frontmatter do catálogo suporta dois formatos:

Formato legado (simples):
    ---
    name: 00_editor_chefe_phd
    type: maswos-agent
    category: academic
    ---

Formato A2A v1.0 (recomendado):
    ---
    name: literary-neurolinguistic-engineering-phd
    description: "PhD em escrita hipnótica"
    version: "1.0.0"
    skills:
      - id: hypnotic-prose-analysis
        name: Análise de Prosa Hipnótica
        tags: [hypnosis, neurolinguistic, literary-analysis]
        examples: ["Analise esta passagem para técnicas de hipnose"]
    capabilities:
      extendedAgentCard: true
    ---
"""

import os
import re
import glob
import logging
import yaml
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("catalog_loader")

CATALOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents", "catalog"
)

# Mapeamento categoria -> capacidades base (legado)
CATEGORY_CAPABILITIES = {
    "academic": ["academic_writing", "qualis_a1", "research"],
    "research": ["research", "search", "literature_review"],
    "engineering": ["python", "code_review", "architecture"],
    "quantum": ["quantum", "qiskit", "simulation"],
    "orchestration": ["orchestration", "coordination"],
    "audit": ["audit", "verification", "compliance"],
    "literary": ["literary_writing", "neurolinguistic", "creative_writing", "narrative_design"],
    "data": ["data_analysis", "statistics"],
    "legal": ["legal", "juridico"],
    "health": ["health", "medical"],
    "publishing": ["publishing", "amazon_kdp", "book_formatting"],
}

# Heurísticas sobre o nome do agente -> capacidades extras (fallback legado)
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
    "literary": ["literary_writing", "narrative_design"],
    "literatura": ["literary_writing", "literature_review"],
    "neurolinguistic": ["neurolinguistic", "hypnotic_writing", "perceptual_engineering"],
    "writing": ["creative_writing", "literary_writing"],
    "escrita": ["creative_writing", "literary_writing"],
    "hipno": ["hypnotic_writing", "neurolinguistic"],
    "research": ["research", "search"],
    "legal": ["legal", "juridico"],
    "kdp": ["amazon_kdp", "book_formatting", "publishing"],
    "amazon": ["amazon_kdp", "publishing"],
    "interior": ["interior_layout", "book_formatting"],
    "miolo": ["interior_layout", "book_formatting"],
    "cover": ["cover_design", "print_layout"],
    "capa": ["cover_design", "print_layout"],
    "epub": ["ebook", "epub", "digital_publishing"],
    "ebook": ["ebook", "digital_publishing"],
    "preflight": ["pdf_preflight", "audit", "verification"],
    "isbn": ["isbn", "metadata", "bibliographic_compliance"],
    "metadata": ["metadata", "bibliographic_compliance"],
    "qa": ["quality_assurance", "verification"],
}


# ═══════════════════════════════════════════════════════════════════════════
# PARSER DE FRONTMATTER (A2A v1.0 + legado)
# ═══════════════════════════════════════════════════════════════════════════

def _strip_leading_html_comment(content: str) -> str:
    """Remove um bloco `<!-- ... -->` no topo do arquivo, se existir."""
    return re.sub(r"^\s*<!--.*?-->\s*", "", content, count=1, flags=re.DOTALL)


def _parse_inline_list(value: str) -> List[str]:
    """Parseia lista inline no formato [a, b, c]."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        items = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        return items
    return [value]


def _parse_skills_block(lines: List[str], start_idx: int) -> Tuple[List[Dict[str, Any]], int]:
    """Parseia um bloco skills: indentado no frontmatter.

    Formato esperado:
      skills:
        - id: hypnotic-prose-analysis
          name: Análise de Prosa Hipnótica
          tags: [hypnosis, neurolinguistic]
          examples:
            - "Analise esta passagem"
            - "Identifique comandos"

    Abordagem robusta: processa linha a linha com máquina de estados,
    tratando corretamente:
    - Multilinhas com >-
    - Listas aninhadas (examples)
    - Linhas com : que não são chave:valor (ex.: "horror: literário")

    Returns:
        (lista_de_skills, índice_da_próxima_linha)
    """
    def _is_key_value(line: str) -> bool:
        """Verifica se a linha contém um par chave:valor (e não texto com ':')."""
        # key: value — a parte antes de : deve ser um identificador simples
        stripped = line.strip()
        if ":" not in stripped:
            return False
        before, _, _ = stripped.partition(":")
        before = before.strip()
        # Chave é identificador simples: letras, números, underscore, hífen
        # Se tem espaços ou é muito longa (> 40), provavelmente é texto
        if not before or len(before) > 40:
            return False
        if " " in before:
            return False
        # Se começa com "- ", é item de lista
        if before.startswith("-"):
            return False
        return True

    def _is_multiline_start(value: str) -> bool:
        return value.strip() in (">", ">-", "|", "|-")

    skills = []
    i = start_idx
    current_skill: Optional[Dict[str, Any]] = None
    skill_indent = 0
    current_list_key: Optional[str] = None
    multiline_key: Optional[str] = None
    multiline_parts: List[str] = []
    _finalized = False  # evita duplicação do último skill

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            # Linha vazia: se estamos acumulando multiline, continua
            if multiline_key is not None:
                i += 1
                continue
            i += 1
            continue

        indent = len(line) - len(line.lstrip())

        # Detecta indentação
        if skill_indent == 0:
            if line.lstrip().startswith("- "):
                skill_indent = indent
            else:
                i += 1
                continue

        # Fim do bloco
        if indent < skill_indent and not line.lstrip().startswith("- "):
            if current_skill:
                skills.append(current_skill)
                _finalized = True
            break

        # Se estamos acumulando descrição multilinha
        if multiline_key is not None:
            # Para a multilinha se encontrar: nova skill, key:value, ou indent = skill_indent
            is_kv = indent > skill_indent and _is_key_value(line)
            is_new_skill = indent == skill_indent and line.lstrip().startswith("- ")
            is_list_item = indent > skill_indent and line.lstrip().startswith("- ")
            is_end_block = indent < skill_indent

            if is_new_skill or is_kv or is_list_item or is_end_block:
                # Finaliza a multilinha
                if current_skill is not None:
                    current_skill[multiline_key] = " ".join(multiline_parts)
                multiline_key = None
                multiline_parts = []
                # Não incrementa i — reprocessa esta linha
                continue
            else:
                # Continuação da multilinha
                multiline_parts.append(line.strip())
                i += 1
                continue

        # Nova skill
        if indent == skill_indent and line.lstrip().startswith("- "):
            if current_skill:
                skills.append(current_skill)
            current_skill = {}
            current_list_key = None
            after_dash = line.lstrip("- ").strip()
            if _is_key_value(after_dash):
                key, _, value = after_dash.partition(":")
                current_skill[key.strip()] = value.strip()
            i += 1
            continue

        # Item de lista (examples)
        if (current_skill is not None and indent > skill_indent
                and line.lstrip().startswith("- ")):
            item_value = line.lstrip("- ").strip().strip("\"'")
            if current_list_key:
                if current_list_key not in current_skill:
                    current_skill[current_list_key] = []
                current_skill[current_list_key].append(item_value)
            i += 1
            continue

        # Campo key:value dentro de uma skill
        if current_skill is not None and indent > skill_indent and _is_key_value(line):
            content = line[skill_indent:] if len(line) > skill_indent else line
            key, _, value = content.partition(":")
            key = key.strip()
            value = value.strip()

            # Reseta list key
            current_list_key = None

            # Lista inline
            if value.startswith("["):
                current_skill[key] = _parse_inline_list(value)
            # Booleanos
            elif value.lower() == "true":
                current_skill[key] = True
            elif value.lower() == "false":
                current_skill[key] = False
            # Números simples
            elif value.replace(".", "").isdigit() and value.count(".") <= 1:
                current_skill[key] = float(value) if "." in value else int(value)
            # Multilinha
            elif _is_multiline_start(value):
                multiline_key = key
                multiline_parts = []
            # Lista vazia (próximas linhas começam com "- ")
            elif not value and i + 1 < len(lines):
                next_line = lines[i + 1].rstrip()
                if next_line.lstrip().startswith("- "):
                    current_list_key = key
                    current_skill[key] = []
            else:
                current_skill[key] = value

        i += 1

    # Finaliza última skill (apenas se ainda não foi finalizada no loop)
    if current_skill and not _finalized:
        # Se ainda estávamos acumulando multilinha
        if multiline_key is not None and multiline_parts:
            current_skill[multiline_key] = " ".join(multiline_parts)
        skills.append(current_skill)

    return skills, i


def _parse_frontmatter_v2(content: str) -> Dict[str, Any]:
    """Parser de frontmatter YAML usando yaml.safe_load padrão.

    Substitui o parser customizado anterior que tinha bugs com:
    - Block-style lists (tags:\n  - item1)
    - Strings multilinha (>-)
    - Inline lists dentro de skills

    Usa yaml.safe_load que é robusto para todos os formatos YAML.
    """
    content = _strip_leading_html_comment(content)
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    yaml_text = match.group(1)
    try:
        meta = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError:
        return {}

    # Garante que skills está no formato esperado
    skills = meta.get("skills", [])
    if isinstance(skills, list):
        for s in skills:
            # Converte tags string p/ lista se necessário
            if isinstance(s.get("tags"), str):
                s["tags"] = [s["tags"]]
            if "id" not in s:
                s["id"] = s.get("name", "unknown").lower().replace(" ", "-")
    else:
        meta.pop("skills", None)

    return meta


# ═══════════════════════════════════════════════════════════════════════════
# DERIVAÇÃO DE CAPACIDADES (A2A + legado)
# ═══════════════════════════════════════════════════════════════════════════

def _derive_capabilities_from_skills(skills: List[Dict[str, Any]]) -> List[str]:
    """Deriva capacidades das tags das skills (formato A2A).

    Exemplo: skills[].tags = ["hypnosis", "neurolinguistic", "literary-analysis"]
    -> capacidades = ["hypnosis", "neurolinguistic", "literary_analysis", "literary_writing"]
    """
    caps: List[str] = []
    seen: set = set()

    for skill in skills:
        for tag in skill.get("tags", []):
            # Converte para string (YAML pode interpretar '00' como int 0)
            tag_str = str(tag) if not isinstance(tag, str) else tag
            # Normaliza: hífen -> underscore
            norm = tag_str.lower().replace("-", "_").replace(" ", "_")
            if norm not in seen:
                seen.add(norm)
                caps.append(norm)

    return caps


def _derive_capabilities_legacy(name: str, meta: Dict[str, str]) -> List[str]:
    """Derivação legada por category + nome (fallback quando não há skills A2A)."""
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
    # dedup
    seen = set()
    unique = []
    for c in caps:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def _derive_capabilities(name: str, meta: Dict[str, Any]) -> List[str]:
    """Deriva capacidades: prioriza skills A2A, fallback para legado.

    Se o frontmatter tem skills[] no formato A2A, as capacidades
    são derivadas das tags. Caso contrário, usa category + nome.
    """
    skills = meta.get("skills", [])
    if skills and isinstance(skills, list):
        a2a_caps = _derive_capabilities_from_skills(skills)
        if a2a_caps:
            return a2a_caps

    # Fallback legado
    return _derive_capabilities_legacy(name, meta)


def _extract_skills(meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrai lista de skills do frontmatter (A2A v1.0) ou deriva do legado."""
    skills = meta.get("skills", [])
    if skills and isinstance(skills, list):
        # Garante que toda skill tem id
        for s in skills:
            if "id" not in s:
                s["id"] = s.get("name", "unknown").lower().replace(" ", "-")
        return skills

    # Deriva skill única do formato legado
    name = meta.get("name", "unknown")
    desc = meta.get("description", "")
    caps = _derive_capabilities(name, meta)
    return [{
        "id": name,
        "name": name.replace("_", " ").title(),
        "description": desc or f"Agente especializado: {name}",
        "tags": caps,
    }]


# ═══════════════════════════════════════════════════════════════════════════
# CARREGAMENTO DO CATÁLOGO
# ═══════════════════════════════════════════════════════════════════════════

def load_catalog_definitions(catalog_dir: str = CATALOG_DIR) -> List[Dict[str, Any]]:
    """Lê agents/catalog/*.md e retorna definições normalizadas (A2A v1.0).

    Returns:
        Lista de dicts com agent_id, name, description, capabilities,
        skills (A2A), category, type, source_file
    """
    definitions: List[Dict[str, Any]] = []
    for path in sorted(glob.glob(os.path.join(catalog_dir, "*.md"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        meta = _parse_frontmatter_v2(content)
        name = meta.get("name") or os.path.splitext(os.path.basename(path))[0]

        # Descrição: frontmatter > legado
        desc = meta.get("description", "").strip()
        if not desc:
            body = _strip_leading_html_comment(content)
            body = re.sub(r"^---.*?---\s*", "", body, flags=re.DOTALL)
            for line in body.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("**"):
                    desc = line
                    break

        # Extrai skills (A2A) ou deriva do legado
        skills = _extract_skills(meta)

        # Capacidades: das skills A2A > legado
        capabilities = _derive_capabilities(name, meta)

        # Versão
        version = str(meta.get("version", "0.1.0"))

        # Episteme explícita (frontmatter opcional — SPEC-935-R363);
        # ausente é o caso normal: a inferência heurística cobre no registro
        episteme_raw = meta.get("episteme")
        episteme = str(episteme_raw).strip().lower() if episteme_raw else None

        definition = {
            "agent_id": name,
            "name": name.replace("_", " ").title(),
            "description": desc or f"Agente especializado do catálogo: {name}",
            "capabilities": capabilities,
            "skills": skills,  # A2A skills[]
            "version": version,
            "category": meta.get("category", "general"),
            "type": meta.get("type", "specialist"),
            "episteme": episteme,
            "metadata": {
                "a2a_version": "1.0" if meta.get("skills") else "legacy",
                "extended_agent_card": (
                    meta.get("capabilities", {}).get("extendedAgentCard", False)
                    if isinstance(meta.get("capabilities"), dict)
                    else False
                ),
            },
            "source_file": path,
        }
        definitions.append(definition)

    return definitions


# ═══════════════════════════════════════════════════════════════════════════
# REGISTRO NO BLACKBOARD (com SemanticMatcher)
# ═══════════════════════════════════════════════════════════════════════════

def register_catalog_agents(metabus) -> int:
    """Registra todos os agentes do catálogo no Blackboard via MetaBus.

    Para agentes com skills A2A, registra também no SemanticMatcher
    para matching semântico (Melhoria #2).

    Retorna o número de agentes registrados.
    """
    # Import semântico (lazy para evitar circular imports)
    try:
        from transformer.semantic_matcher import semantic_matcher
        has_semantic = True
    except Exception:
        has_semantic = False
        logger.warning("SemanticMatcher indisponível — usando matching legado")

    count = 0
    for definition in load_catalog_definitions():
        agent_id = definition["agent_id"]
        skills = definition.get("skills", [])

        agent_payload = {
            "agent_id": agent_id,
            "name": definition["name"],
            "description": definition["description"],
            "capabilities": definition["capabilities"],
            "metadata": {
                "category": definition["category"],
                "type": definition["type"],
                "a2a_version": definition["metadata"]["a2a_version"],
                "version": definition["version"],
                "origin": "OpenCode_Ecosystem/agents",
            },
        }

        # Se tem skills A2A, inclui no payload
        if skills:
            agent_payload["skills"] = skills

        metabus.publish("agent.register", agent_payload, source_agent="catalog_loader")

        # Registra no SemanticMatcher se disponível
        if has_semantic and skills:
            try:
                semantic_matcher.register_agent_skills(
                    agent_id=agent_id,
                    skills=skills,
                    initial_confidence=0.5,
                    episteme=definition.get("episteme"),
                    category=definition.get("category", ""),
                    agent_type=definition.get("type", ""),
                )
            except Exception as exc:
                logger.debug(f"Erro ao registrar {agent_id} no SemanticMatcher: {exc}")

        count += 1

    if has_semantic:
        stats = semantic_matcher.get_stats()
        logger.info(
            f"Catálogo: {count} agentes registrados | "
            f"SemanticMatcher: {stats['handbook']['total_skills']} skills | "
            f"Engine: {stats['engine']['provider']}"
        )

    return count
