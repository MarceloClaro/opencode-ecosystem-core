#!/usr/bin/env python3
"""Migração em massa do catálogo de agentes para formato A2A v1.0 (R348).

Uso:
    python3 scripts/migrate_a2a_v1.py              # simular (dry-run)
    python3 scripts/migrate_a2a_v1.py --apply       # aplicar migrações
    python3 scripts/migrate_a2a_v1.py --apply --agent nome.md  # agente específico

Estratégia de derivação de skills:
  1. Se já existe 'capabilities' legacy → converte diretamente em skills A2A
  2. Se existe 'description' → extrai termos-chave e gera skills
  3. Se existe conteúdo do agente → extrai headings (##) como skills
  4. Fallback → deriva do nome do agente
"""

import os
import re
import sys
import json
import hashlib
import yaml
from typing import Dict, List, Optional, Tuple
from pathlib import Path

CATALOG_DIR = Path("agents/catalog")
SKIP_AGENTS = {
    "marceloclaro.md",           # orquestrador primário — não é subagente
    "master-orchestrator.md",    # orquestrador mestre
    "bernstein-orchestrator.md", # orquestrador Bernstein
    "antigravity-orchestrator.md", # orquestrador Antigravity
    "literary-orchestrator-phd.md", # orquestrador literário
    "kdp-orchestrator-phd.md",   # orquestrador KDP
    "stage-orchestrator.md",     # orquestrador de estágios
    "reversa.md",                # orquestrador Reversa
    "reversa-planner.md",        # suborquestrador Reversa
    "reversa-synthesis.md",      # suborquestrador Reversa
}

A2A_EXAMPLES_BY_DOMAIN = {
    "literary": [
        "Analise a estrutura narrativa deste capítulo",
        "Avalie a coerência temporal dos fragmentos",
    ],
    "kdp": [
        "Prepare o PDF de miolo para este manuscrito",
        "Verifique as margens internas do livro",
    ],
    "code": [
        "Revise este código para segurança e performance",
        "Implemente a funcionalidade descrita na spec",
    ],
    "cloud": [
        "Configure o banco de dados Cloud SQL",
        "Otimize a query BigQuery para este dataset",
    ],
    "maswos": [
        "Execute o pipeline MASWOS para este tópico",
        "Pesquise literatura acadêmica sobre este tema",
    ],
    "academic": [
        "Produza artigo acadêmico com metodologia Qualis A1",
        "Analise os dados estatísticos do experimento",
    ],
    "data": [
        "Analise este dataset e gere visualizações",
        "Construa pipeline de dados para ETL",
    ],
    "mira": [
        "Gere apresentação MIRA sobre este tópico",
        "Crie animação central para o slide de abertura",
    ],
    "reversa": [
        "Analise a arquitetura deste sistema legado",
        "Documente as regras de negócio do sistema",
    ],
    "general": [
        "Execute esta tarefa conforme especificação",
        "Analise e reporte os resultados",
    ],
}


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], int, int]:
    """Extrai metadados de um arquivo markdown.

    Tenta, em ordem:
    1. YAML frontmatter padrão (--- ... ---)
    2. HTML comment com KV pairs (<!-- chave: valor -->)
    3. Fallback: retorna dicionário vazio com detecção por **ID:**

    Retorna (metadata, start_line, end_line).
    """
    lines = content.split("\n")

    # --- TENTATIVA 1: YAML frontmatter padrão ---
    yaml_start = -1
    yaml_end = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            if yaml_start == -1:
                yaml_start = i
            else:
                yaml_end = i
                break

    if yaml_end > yaml_start:
        yaml_text = "\n".join(lines[yaml_start + 1 : yaml_end])
        try:
            meta = yaml.safe_load(yaml_text) or {}
            return meta, yaml_start, yaml_end
        except yaml.YAMLError:
            pass

    # --- TENTATIVA 2: HTML comment com KV pairs ---
    html_comment = re.search(r"<!--\s*\n?(.*?)\n?\s*-->", content, re.DOTALL)
    if html_comment:
        comment_text = html_comment.group(1).strip()
        meta = {}
        for line in comment_text.split("\n"):
            line = line.strip()
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                # Detecta YAML multiline (>)
                if value == ">" or value == ">-":
                    continue
                value = value.strip("'\"")
                meta[key] = value
        if meta:
            # Calcula linha final do comentário HTML
            end_line = content[:html_comment.end()].count("\n")
            return meta, 0, end_line

    # --- TENTATIVA 3: Markdown sem frontmatter, extrai do corpo ---
    # Procura padrão **ID:** `agent-id` ou `# Title`
    meta = {}
    id_match = re.search(r'\*\*ID:\*\*\s*`(.+?)`', content)
    if id_match:
        meta["name"] = id_match.group(1)
    else:
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Extrai ID do título se tiver formato "nome — descrição"
            if "—" in title:
                meta["name"] = title.split("—")[0].strip()
            else:
                meta["name"] = title.strip()

    # Procura descrição no primeiro parágrafo após o título
    paras = re.split(r"\n\s*\n", content)
    for p in paras[:3]:
        p = p.strip()
        if p and not p.startswith("#") and not p.startswith("**") and not p.startswith("<!--"):
            if len(p) > 20:
                meta["description"] = p[:200]
                break

    return meta if meta else None, 0, 0


def normalize_skill_id(name_id: str, description_chunk: str = "") -> str:
    """Normaliza texto em snake_case skill ID (máx 45 chars)."""
    source = description_chunk or name_id

    # Remove markdown: **, *, `, [](), etc.
    source = re.sub(r"\*\*(.+?)\*\*", r"\1", source)
    source = re.sub(r"\*(.+?)\*", r"\1", source)
    source = re.sub(r"`(.+?)`", r"\1", source)
    source = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", source)

    # Remove acentos
    replacements = {
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e", "í": "i", "ó": "o",
        "ô": "o", "õ": "o", "ú": "u", "ç": "c",
        "ü": "u",
    }
    for old, new in replacements.items():
        source = source.replace(old, new)

    # Remove caracteres especiais, mantém letras, números, espaços e hífens
    source = re.sub(r"[^a-zA-Z0-9\s-]", " ", source)
    # Lowercase, substitui espaços por hífen, limpa
    skill_id = source.lower().strip()
    skill_id = re.sub(r"\s+", "-", skill_id)
    skill_id = re.sub(r"-+", "-", skill_id)
    skill_id = skill_id.strip("-")
    # Extrai palavras-chave: pega primeiras 3-4 palavras mais significativas
    words = skill_id.split("-")
    # Remove stopwords curtas no ID
    stop_id = {"para", "com", "que", "dos", "das", "uma", "pela", "como",
               "mais", "mas", "por", "seu", "sua", "via", "em", "de", "da", "do"}
    meaningful = [w for w in words if w not in stop_id and len(w) > 1]
    if meaningful:
        # Pega até 4 palavras significativas
        skill_id = "-".join(meaningful[:4])
    # Limita tamanho
    if len(skill_id) > 45:
        # Pega primeiras palavras até caber
        truncated = ""
        for w in meaningful:
            candidate = f"{truncated}-{w}" if truncated else w
            if len(candidate) <= 45:
                truncated = candidate
            else:
                break
        skill_id = truncated or meaningful[0][:45].rstrip("-")

    if not skill_id:
        skill_id = hashlib.md5(source.encode()).hexdigest()[:8]
    return skill_id


def extract_skills_from_description(agent_id: str, description: str) -> List[Dict]:
    """Deriva skills de uma descrição textual usando heurísticas.

    Estratégia:
    1. Divide description em chunks semânticos (vírgulas, 'e', ';')
    2. Cada chunk vira uma skill candidata
    3. Normaliza ID e nome
    4. Gera exemplos genéricos do domínio
    """
    if not description:
        return []

    # Remove prefixos comuns
    desc = description.strip().rstrip(".")
    desc = re.sub(r"^(Especialista|Expert|PhD|Mestre) (em|PhD) ", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"^(Você é o|Você é) ", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"^(Agente|Orquestrador|Coordenador|Analista|Especialista) ", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"^do ecossistema ", "", desc, flags=re.IGNORECASE)

    # Divide em chunks semânticos
    # Primeiro tenta split por vírgula + conector
    chunks = re.split(r",\s*(?:e|para|com|de|em)\s+", desc)

    # Se só deu um chunk, tenta split por "e " ou ponto e vírgula
    if len(chunks) <= 1:
        chunks = re.split(r"[;.]\s*", desc)
    if len(chunks) <= 1:
        chunks = re.split(r"\s+e\s+", desc)
    # Se ainda só deu um chunk, tenta split por palavras-chave
    if len(chunks) <= 1:
        chunks = re.split(r"\s+(?:para|com|de|em|por meio de|através de)\s+", desc)

    # Filtra chunks vazios ou muito curtos
    chunks = [c.strip().rstrip(".,") for c in chunks if len(c.strip()) > 10]

    # Se ainda não temos chunks, cria um único skill do nome do agente
    if not chunks:
        return []

    # Remove chunks duplicados (case insensitive)
    seen = set()
    unique_chunks = []
    for c in chunks:
        key = c.lower().strip()
        if key not in seen:
            seen.add(key)
            unique_chunks.append(c)

    # Converte chunks em skills
    skills = []
    for chunk in unique_chunks[:6]:  # max 6 skills
        # Limpa markdown do chunk para ID
        chunk_clean = re.sub(r"[\*\`]", "", chunk).strip()
        skill_id = normalize_skill_id(agent_id, chunk_clean[:60])
        if not skill_id or len(skill_id) < 3:
            continue

        # Nome: capitalize primeiras letras
        name = chunk_clean[:70].strip().capitalize()

        # Gera tags do chunk
        words = [w.lower().strip(".,;:()").replace(":", "") for w in chunk_clean.split() if len(w) > 3]
        stopwords = {"para", "com", "que", "dos", "das", "uma", "pela",
                     "como", "mais", "mas", "por", "seu", "sua", "seus",
                     "através", "através", "meio", "sobre", "entre",
                     "the", "and", "with", "this", "that", "but", "for",
                     "are", "not", "you", "all", "can", "was", "use", "via"}
        tags = [w for w in words if w not in stopwords and len(w) > 2][:4]

        # Descrição mais curta e natural
        short_desc = chunk_clean[:120].lower().strip()
        if len(short_desc) > 80:
            short_desc = short_desc[:80].rstrip(",") + "."

        skills.append({
            "id": skill_id,
            "name": name,
            "description": f"Capacidade especializada em {short_desc}",
            "tags": tags,
            "examples": [
                f"Aplique {skill_id.replace('-', ' ')} neste contexto",
                f"Avalie usando {skill_id.replace('-', ' ')}",
            ],
        })

    return skills


def extract_skills_from_content(agent_id: str, content: str, description: str) -> List[Dict]:
    """Deriva skills adicionais do conteúdo do agente (headings, responsabilidades).

    Retorna skills complementares às da description.
    """
    skills = []
    seen_ids = set()

    # Extrai headings ## como possíveis skills
    headings = re.findall(r"^##\s+(.+)", content, re.MULTILINE)

    # Palavras-chave que indicam seções ricas em skills
    relevant_headings = ["responsabilidades", "responsabilidade", "habilidades",
                         "capacidades", "competências", "escopo", "atividades",
                         "funções", "o que faz", "skills", "expertise"]
    for h in headings:
        h_lower = h.lower().strip()
        if any(r in h_lower for r in relevant_headings):
            # Pega o texto após o heading até o próximo heading
            pattern = rf"^##\s+{re.escape(h)}\s*$(.+?)(?=^##|\Z)"
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                section_text = match.group(1).strip()
                # Extrai itens de lista
                items = re.findall(r"^[-*]\s+(.+)", section_text, re.MULTILINE)
                for item in items[:4]:
                    skill_id = normalize_skill_id(agent_id, item[:50])
                    if skill_id and skill_id not in seen_ids and len(skill_id) >= 3:
                        seen_ids.add(skill_id)
                        item_clean = re.sub(r"[\*\`]", "", item).strip()
                        skills.append({
                            "id": skill_id,
                            "name": item_clean[:60].capitalize(),
                            "description": f"Executa {item_clean.lower()} conforme protocolo especializado.",
                            "tags": [w.lower().strip(".,") for w in item_clean.split()[:3] if len(w) > 3],
                            "examples": [
                                f"Execute {skill_id.replace('-', ' ')}",
                                f"Aplique {skill_id.replace('-', ' ')} no contexto atual",
                            ],
                        })

    # Se ainda não temos skills, extrai do protocolo SDD/TDD
    if not skills:
        sdd_match = re.search(r"##\s*Protocolo SDD/TDD.*?(?=##|\Z)", content, re.DOTALL)
        if sdd_match:
            sdd_text = sdd_match.group(0)
            skill_id = normalize_skill_id(agent_id, "sdd-tdd-" + agent_id)
            skills.append({
                "id": skill_id[:50].rstrip("-"),
                "name": f"SDD/TDD {agent_id.replace('-', ' ').title()}",
                "description": f"Aplica protocolo SDD/TDD: SDD (especificação) → TDD RED/GREEN/REFACTOR.",
                "tags": ["sdd", "tdd", "metodologia"],
                "examples": [
                    "Execute ciclo SDD para esta tarefa",
                    "Aplique TDD: RED → GREEN → REFACTOR",
                ],
            })

    return skills


def determine_domain(agent_id: str, description: str, category: str = "") -> str:
    """Determina o domínio do agente para templates de exemplo."""
    text = f"{agent_id} {description} {category}".lower()

    domain_map = [
        ("literary", ["literary", "literário", "narratology", "character",
                      "psychology", "symbolic", "imagery", "neurolinguistic",
                      "fiction", "poetry", "romance", "escrita", "literatura"]),
        ("kdp", ["kdp", "amazon", "kindle", "ebook", "epub", "publishing",
                 "isbn", "book", "livro", "miolo", "capa", "lombada"]),
        ("maswos", ["maswos", "academic", "paper", "artigo", "qualis",
                    "thesis", "pesquisa", "pesquisador"]),
        ("mira", ["mira", "apresentação", "slide", "deck", "animation"]),
        ("cloud", ["cloud", "gcp", "bigquery", "alloydb", "cloudsql",
                   "spanner", "dataflow"]),
        ("data", ["data", "dataset", "dados", "analytics", "pipeline",
                  "etl", "database"]),
        ("reversa", ["reversa", "engenharia reversa", "legado", "reverse"]),
        ("code", ["code", "coder", "developer", "dev", "programação",
                  "software", "refactoring", "coding"]),
        ("academic", ["academic", "university", "professor", "phd",
                      "pesquisa", "ciência", "science"]),
    ]

    for domain, keywords in domain_map:
        if any(k in text for k in keywords):
            return domain
    return "general"


def build_agent_skills(agent_id: str, meta: Dict, content: str) -> List[Dict]:
    """Constrói lista de skills A2A v1.0 para um agente.

    Pipeline:
      1. Legacy 'capabilities' → direct conversion
      2. Description → NLP extraction
      3. Content (headings, SDD) → complementary skills
      4. Fallback → agent name
    """
    skills = []
    seen_ids = set()
    description = meta.get("description", "") or ""
    category = meta.get("category", "")

    # PASSO 1: Legacy 'capabilities'
    caps = meta.get("capabilities", [])
    if isinstance(caps, dict):
        caps = list(caps.keys())  # para casos como {extendedAgentCard: True}
    if caps and isinstance(caps, list):
        for cap in caps:
            if isinstance(cap, str):
                skill_id = cap.strip().lower().replace(":", "-")
                if skill_id and skill_id not in seen_ids:
                    seen_ids.add(skill_id)
                    name = cap.replace("-", " ").replace("_", " ").title()
                    # Tags mais descritivas
                    tag_parts = skill_id.replace(":", "-").split("-")
                    tag_root = tag_parts[0] if tag_parts else skill_id
                    skills.append({
                        "id": skill_id,
                        "name": name[:60],
                        "description": f"Capacidade especializada em {name.lower()}.",
                        "tags": [tag_root, skill_id[:20]] if len(tag_root) > 2 else [skill_id[:20]],
                        "examples": [
                            f"Aplique {skill_id.replace('-', ' ').replace(':', ' ')}",
                            f"Execute operação de {skill_id.replace('-', ' ').replace(':', ' ')}",
                        ],
                    })

    # PASSO 2: Description → skills
    desc_skills = extract_skills_from_description(agent_id, description)
    for skill in desc_skills:
        if skill["id"] not in seen_ids:
            seen_ids.add(skill["id"])
            skills.append(skill)

    # PASSO 3: Content → skills complementares
    content_skills = extract_skills_from_content(agent_id, content, description)
    for skill in content_skills:
        if skill["id"] not in seen_ids:
            seen_ids.add(skill["id"])
            skills.append(skill)

    # PASSO 4: Fallback — deriva do nome
    if not skills:
        # Extrai palavras significativas do agent_id
        parts = agent_id.replace("-", " ").replace("_", " ").split()
        # Remove palavras genéricas
        generic = {"agent", "phd", "master", "specialist", "general"}
        meaningful = [p for p in parts if p.lower() not in generic]
        if meaningful:
            fallback_name = " ".join(meaningful).title()
        else:
            fallback_name = agent_id

        skill_id = normalize_skill_id(agent_id, fallback_name[:60])
        domain = determine_domain(agent_id, description, category)
        examples = A2A_EXAMPLES_BY_DOMAIN.get(domain, A2A_EXAMPLES_BY_DOMAIN["general"])

        skills.append({
            "id": skill_id[:50].rstrip("-"),
            "name": fallback_name[:60],
            "description": f"Executa tarefas especializadas de {fallback_name.lower()} conforme protocolo SDD/TDD.",
            "tags": [p.lower() for p in meaningful[:3]] if meaningful else [skill_id],
            "examples": examples[:2],
        })

    return skills[:8]  # max 8 skills


def determine_tags(agent_id: str, meta: Dict, skills: List[Dict]) -> List[str]:
    """Deriva tags do agente a partir de múltiplas fontes."""
    tags = set()
    description = meta.get("description", "") or ""
    category = meta.get("category", "") or ""
    agent_type = meta.get("type", "") or ""

    # Da descrição — limpa markdown primeiro
    clean_desc = re.sub(r"\*\*(.+?)\*\*", r"\1", description)
    clean_desc = re.sub(r"\*(.+?)\*", r"\1", clean_desc)
    words = re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", clean_desc.lower())
    stopwords = {"para", "com", "que", "dos", "das", "uma", "pela",
                 "como", "mais", "mas", "por", "seu", "sua", "via",
                 "toda", "deve", "em", "nunca", "mesmo", "dados",
                 "esta", "entre", "sobre", "através"}
    for w in words:
        if w not in stopwords and len(w) > 2:
            tags.add(w)

    # Das skills — tags já limpas
    for s in skills:
        for t in s.get("tags", []):
            if isinstance(t, str) and len(t) > 2:
                # Remove markdown das tags
                t_clean = re.sub(r"[\*`]", "", t).strip().lower()
                if t_clean and len(t_clean) > 2:
                    tags.add(t_clean)

    # Do nome do agente (partes significativas)
    parts = re.split(r"[-_]", agent_id.lower())
    generic = {"agent", "phd", "specialist", "general", "master", "md"}
    for p in parts:
        if p not in generic and len(p) > 3:
            tags.add(p)

    # Da categoria/tipo legado
    if category:
        tags.add(category.lower())
    if agent_type:
        tags.add(agent_type.lower())

    return sorted(list(tags))[:10]


def generate_examples(agent_id: str, meta: Dict, skills: List[Dict]) -> List[str]:
    """Gera exemplos de uso do agente."""
    domain = determine_domain(agent_id, meta.get("description", ""), meta.get("category", ""))
    examples = A2A_EXAMPLES_BY_DOMAIN.get(domain, A2A_EXAMPLES_BY_DOMAIN["general"])

    # Adiciona exemplos específicos das skills
    extra = []
    for s in skills[:2]:
        if s.get("examples"):
            extra.append(s["examples"][0])

    combined = examples + extra
    return combined[:4]


def is_already_a2a(meta: Dict) -> bool:
    """Verifica se o agente já está no formato A2A v1.0."""
    if not meta:
        return False
    return bool(meta.get("skills")) and bool(meta.get("version"))


def _yaml_inline_list(items: list) -> str:
    """Renderiza lista inline: [item1, item2, item3]."""
    escaped = []
    for item in items:
        s = str(item).strip()
        # Adiciona aspas se contiver caracteres especiais
        if any(c in s for c in ',[]:#'):
            s = f"'{s}'"
        escaped.append(s)
    return "[" + ", ".join(escaped) + "]"


def _yaml_skills_block(skills: list, indent: int = 0) -> str:
    """Renderiza bloco skills com inline lists para tags/examples."""
    pad = " " * indent
    lines = []
    for skill in skills:
        lines.append(f"{pad}- id: {skill.get('id', 'unknown')}")
        lines.append(f"{pad}  name: {skill.get('name', '')}")
        desc = skill.get('description', '')
        # Description longa: usa >- multilinha
        if len(desc) > 80:
            lines.append(f"{pad}  description: >-")
            # Quebra em palavras
            words = desc.split()
            chunk = ""
            for w in words:
                if len(chunk) + len(w) + 1 > 100:
                    lines.append(f"{pad}    {chunk}")
                    chunk = w
                else:
                    chunk = f"{chunk} {w}".strip()
            if chunk:
                lines.append(f"{pad}    {chunk}")
        else:
            lines.append(f"{pad}  description: {desc}")

        # Tags inline
        tags = skill.get('tags', [])
        if tags:
            lines.append(f"{pad}  tags: {_yaml_inline_list(tags)}")
        else:
            lines.append(f"{pad}  tags: []")

        # Examples inline
        examples = skill.get('examples', [])
        if examples:
            lines.append(f"{pad}  examples: {_yaml_inline_list(examples)}")
        else:
            lines.append(f"{pad}  examples: []")

    return "\n".join(lines)


def _yaml_simple_value(value) -> str:
    """Renderiza um valor YAML simples."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return _yaml_inline_list(value)
    if isinstance(value, dict):
        # Dict simples: permissões/tools
        kv = []
        for k, v in value.items():
            if isinstance(v, dict):
                sub = "; ".join(f"{sk}: {sv}" for sk, sv in v.items())
                kv.append(f"{k}: {sub}")
            else:
                kv.append(f"{k}: {v}")
        return "; ".join(kv)
    # String — verifica se precisa de aspas
    s = str(value)
    if any(c in s for c in ':,#{}[]'):
        s = f"'{s}'"
    return s


def build_a2a_frontmatter(agent_id: str, meta: Dict, content: str) -> str:
    """Constrói o frontmatter YAML A2A v1.0 completo.

    Usa YAML gerado manualmente para garantir:
    - tags/examples sempre inline (compatível com catalog_loader)
    - skills block com lists inline
    - Nenhum bloco-style aninhado que trave o parser
    """
    if meta is None:
        meta = {}

    # Deriva skills
    skills = build_agent_skills(agent_id, meta, content)

    # Deriva tags
    tags = determine_tags(agent_id, meta, skills)

    # Deriva exemplos
    examples = generate_examples(agent_id, meta, skills)

    # Preserva campos legados
    legacy_fields = {}
    for key in ["mode", "temperature", "type", "category", "model", "agent_id"]:
        if key in meta:
            legacy_fields[key] = meta[key]

    # Permissions e tools são dicts complexos
    tools = meta.get("tools")
    permission = meta.get("permission")

    # Monta YAML linha a linha
    yaml_lines = []
    yaml_lines.append(f"name: {agent_id}")
    desc = meta.get("description", f"Agente especializado {agent_id}")
    # Description longa: usa >-
    if len(desc) > 80:
        yaml_lines.append("description: >-")
        words = desc.split()
        chunk = ""
        for w in words:
            if len(chunk) + len(w) + 1 > 100:
                yaml_lines.append(f"  {chunk}")
                chunk = w
            else:
                chunk = f"{chunk} {w}".strip()
        if chunk:
            yaml_lines.append(f"  {chunk}")
    else:
        yaml_lines.append(f"description: {desc}")

    yaml_lines.append("version: '1.0.0'")

    # Skills block (sempre inline tags/examples)
    yaml_lines.append("skills:")
    yaml_lines.append(_yaml_skills_block(skills, indent=0))

    # Tags e examples top-level inline
    if tags:
        yaml_lines.append(f"tags: {_yaml_inline_list(tags)}")
    if examples:
        yaml_lines.append(f"examples: {_yaml_inline_list(examples)}")

    # Campos legados
    for key, value in legacy_fields.items():
        yaml_lines.append(f"{key}: {_yaml_simple_value(value)}")

    # Tools (dict)
    if tools:
        yaml_lines.append("tools:")
        for k, v in tools.items():
            yaml_lines.append(f"  {k}: {_yaml_simple_value(v)}")

    # Permission (dict aninhado)
    if permission:
        yaml_lines.append("permission:")
        for k, v in permission.items():
            if isinstance(v, dict):
                yaml_lines.append(f"  {k}:")
                for sk, sv in v.items():
                    yaml_lines.append(f"    {sk}: {_yaml_simple_value(sv)}")
            else:
                yaml_lines.append(f"  {k}: {_yaml_simple_value(v)}")

    return "---\n" + "\n".join(yaml_lines) + "\n---\n"


def migrate_agent(filepath: Path, apply: bool = False, force: bool = False, verbose: bool = True) -> Dict:
    """Migra um único agente para A2A v1.0.

    Retorna dict com status da migração.
    """
    filename = filepath.name
    result = {
        "agent": filename,
        "status": "skipped",
        "reason": "",
        "skills_count": 0,
    }

    if filename in SKIP_AGENTS:
        result["reason"] = "orchestrator (skip list)"
        return result

    content = filepath.read_text(encoding="utf-8")
    meta, yaml_start, yaml_end = parse_frontmatter(content)

    if meta and is_already_a2a(meta) and not force:
        result["reason"] = "already A2A v1.0"
        result["skills_count"] = len(meta.get("skills", []))
        return result

    # Determina agent_id do meta ou filename
    agent_id = None
    if meta:
        agent_id = meta.get("name") or meta.get("agent_id")
    if not agent_id:
        agent_id = filename.replace(".md", "")

    # Constrói novo frontmatter
    new_frontmatter = build_a2a_frontmatter(agent_id, meta, content)

    if meta and yaml_end > 0:
        # Substitui frontmatter existente
        body_start = yaml_end + 1
        # Mantém linhas antes do frontmatter (comentários HTML)
        header_lines = content.split("\n")[:yaml_start]
        body = "\n".join(content.split("\n")[body_start:])
        new_content = "\n".join(header_lines) + "\n" + new_frontmatter + "\n" + body if header_lines else new_frontmatter + "\n" + body
    else:
        # Adiciona frontmatter no início
        body = content
        new_content = new_frontmatter + "\n" + body

    # Limpa duplicatas de linhas em branco
    new_content = re.sub(r"\n{3,}", "\n\n", new_content)
    new_content = new_content.strip() + "\n"

    result["skills_count"] = len(build_agent_skills(agent_id, meta, content))

    if apply:
        filepath.write_text(new_content, encoding="utf-8")

    if meta:
        result["old_format"] = f"YAML ({len(meta)} fields)"
    else:
        result["old_format"] = "NO_YAML"

    result["status"] = "migrated" if apply else "simulated"

    if verbose:
        old = f"[{result['old_format']}]"
        verb = "→ MIGRADO" if apply else "→ SIMULADO"
        print(f"  {filename:50s} {old:20s} {verb} ({result['skills_count']} skills)")

    return result


def main():
    apply = "--apply" in sys.argv
    force = "--force" in sys.argv or "-f" in sys.argv
    specific = None
    for arg in sys.argv[1:]:
        if arg.startswith("--agent="):
            specific = arg.split("=", 1)[1]
        if arg.startswith("--agent "):
            idx = sys.argv.index(arg) + 1
            if idx < len(sys.argv):
                specific = sys.argv[idx]

    if not apply:
        print("\n🔍 MODO SIMULAÇÃO (dry-run). Use --apply para aplicar as migrações.\n")
    else:
        mode = "FORÇADA" if force else "NORMAL"
        print(f"\n⚡ APLICANDO migrações A2A v1.0 (modo {mode})...\n")

    agents = sorted(CATALOG_DIR.glob("*.md"))
    if specific:
        agents = [CATALOG_DIR / specific]

    results = {"migrated": 0, "already_a2a": 0, "skipped": 0, "simulated": 0, "errors": 0}
    total_skills = 0

    for agent_path in agents:
        try:
            r = migrate_agent(agent_path, apply=apply, force=force, verbose=True)
            if r["status"] == "migrated":
                results["migrated"] += 1
                total_skills += r["skills_count"]
            elif r["status"] == "simulated":
                results["simulated"] += 1
                total_skills += r["skills_count"]
            elif r["status"] == "skipped" and r["reason"] == "already A2A v1.0":
                results["already_a2a"] += 1
                total_skills += r["skills_count"]
            elif r["status"] == "skipped":
                results["skipped"] += 1
        except Exception as e:
            results["errors"] += 1
            print(f"  {agent_path.name:50s} ❌ ERRO: {e}")

    # Summary
    print(f"\n{'='*70}")
    if apply:
        print(f"✅ MIGRAÇÃO CONCLUÍDA")
    else:
        print(f"📋 SIMULAÇÃO — execute com --apply para aplicar")
    print(f"{'='*70}")
    print(f"  Agentes migrados:     {results['migrated']}")
    print(f"  Já A2A v1.0:          {results['already_a2a']}")
    print(f"  Pulados (orquestr.):  {results['skipped']}")
    print(f"  Erros:                {results['errors']}")
    if apply or results["simulated"]:
        print(f"  Skills geradas:       {total_skills}")
    print()

    # Validate after migration
    if apply:
        print("🔎 Validando integridade...")
        validate_after_migration()

    return 0 if results["errors"] == 0 else 1


def validate_after_migration():
    """Valida que todos os agentes têm frontmatter A2A válido."""
    errors = 0
    for agent_path in sorted(CATALOG_DIR.glob("*.md")):
        if agent_path.name in SKIP_AGENTS:
            continue
        content = agent_path.read_text(encoding="utf-8")
        meta, _, _ = parse_frontmatter(content)
        if not meta:
            print(f"  ⚠️  {agent_path.name}: sem YAML frontmatter")
            errors += 1
            continue
        if "name" not in meta:
            print(f"  ⚠️  {agent_path.name}: sem 'name' no frontmatter")
            errors += 1
            continue
        # Verifica skills e version (permitindo orquestradores sem)
        if agent_path.name not in SKIP_AGENTS:
            if "skills" not in meta:
                print(f"  ⚠️  {agent_path.name}: sem 'skills' no frontmatter")
                errors += 1
            if "version" not in meta:
                print(f"  ⚠️  {agent_path.name}: sem 'version' no frontmatter")
                errors += 1
    if errors == 0:
        print(f"  ✅ Todos os {len(list(CATALOG_DIR.glob('*.md'))) - len(SKIP_AGENTS)} agentes validados com sucesso!")
    else:
        print(f"  ⚠️  {errors} agente(s) com problemas")
    print()


if __name__ == "__main__":
    sys.exit(main())
