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
import re
import sys
from collections.abc import Mapping
from typing import Any, Dict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "opencode.json")

_PERMISSION_ACTIONS = frozenset({"allow", "ask", "deny"})
_BROAD_PATTERNS = frozenset({"*", "**", "**/*"})
_MUTATION_PERMISSIONS = ("edit", "bash")
_DEFAULT_AGENT_PERMISSIONS = {"edit": "deny", "bash": "deny"}
_ESSENTIAL_AGENT_PERMISSIONS = {
    "academic_writer": {"edit": "allow", "bash": "deny"},
    "auditor": {"edit": "deny", "bash": "deny"},
    "coder": {"edit": "allow", "bash": "allow"},
    "researcher": {"edit": "deny", "bash": "deny"},
    "reviewer": {"edit": "deny", "bash": "deny"},
}


def _strip_leading_html_comment(content: str) -> str:
    """Remove o comentário de metadados que antecede vários frontmatters."""
    return re.sub(r"^\s*<!--.*?-->\s*", "", content, count=1, flags=re.DOTALL)


def _split_yaml_entry(line: str) -> tuple[str, str] | None:
    """Separa uma entrada YAML simples sem quebrar dois-pontos entre aspas."""
    quote: str | None = None
    escaped = False
    for index, character in enumerate(line):
        if quote is not None:
            if quote == '"' and character == "\\" and not escaped:
                escaped = True
                continue
            if character == quote and not escaped:
                quote = None
            escaped = False
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == ":":
            return line[:index], line[index + 1:]
    return None


def _strip_yaml_comment(value: str) -> str:
    """Descarta comentário YAML somente quando ``#`` está fora de aspas."""
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if quote is not None:
            if quote == '"' and character == "\\" and not escaped:
                escaped = True
                continue
            if character == quote and not escaped:
                quote = None
            escaped = False
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def _yaml_scalar(raw_value: str) -> Any:
    """Materializa apenas escalares necessários às políticas de ferramentas."""
    value = _strip_yaml_comment(raw_value).strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    return value


def _frontmatter_policy_sections(path: str) -> Dict[str, Any]:
    """Lê ``tools`` e ``permission`` de um frontmatter YAML simples.

    O gerador não depende de PyYAML em runtime. O parser é deliberadamente
    estreito: aceita os escalares e os dois níveis de mapas usados pelas regras
    OpenCode, preservando a ordem de inserção que define a precedência.
    """
    try:
        with open(path, "r", encoding="utf-8") as source:
            content = _strip_leading_html_comment(source.read())
    except OSError:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if match is None:
        return {}

    sections: Dict[str, Any] = {}
    current_section: str | None = None
    current_rule: str | None = None
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indentation = len(raw_line) - len(raw_line.lstrip(" "))
        entry = _split_yaml_entry(raw_line.strip())
        if entry is None:
            continue
        raw_key, raw_value = entry
        key = str(_yaml_scalar(raw_key.strip()))
        value = raw_value.strip()

        if indentation == 0:
            current_rule = None
            if key not in {"tools", "permission"}:
                current_section = None
                continue
            current_section = key
            sections[key] = _yaml_scalar(value) if value else {}
            continue

        if current_section is None or not isinstance(
            sections.get(current_section), dict
        ):
            continue
        section = sections[current_section]
        if indentation == 2:
            if value:
                section[key] = _yaml_scalar(value)
                current_rule = None
            else:
                section[key] = {}
                current_rule = key
            continue
        if indentation >= 4 and current_rule is not None:
            rule = section.get(current_rule)
            if isinstance(rule, dict) and value:
                rule[key] = _yaml_scalar(value)
    return sections


def _permission_action(value: Any) -> str | None:
    """Converte booleanos legados e ações textuais ao formato OpenCode 1.18.4."""
    if isinstance(value, bool):
        return "allow" if value else "deny"
    if isinstance(value, str) and value.strip().lower() in _PERMISSION_ACTIONS:
        return value.strip().lower()
    return None


def _permission_rule(value: Any) -> str | Dict[str, str] | None:
    """Normaliza uma ação ou mapa ordenado de padrões para ações."""
    action = _permission_action(value)
    if action is not None:
        return action
    if not isinstance(value, Mapping):
        return None

    normalized: Dict[str, str] = {}
    for pattern, raw_action in value.items():
        action = _permission_action(raw_action)
        if action is not None:
            normalized[str(pattern)] = action
    return normalized or None


def _canonical_permission_key(key: Any) -> str:
    """Unifica write/edit/patch no gate ``edit`` do OpenCode 1.18.4."""
    normalized = str(key)
    return "edit" if normalized in {"write", "edit", "patch"} else normalized


def _copy_permissions(permissions: Mapping[str, Any]) -> Dict[str, Any]:
    """Copia regras sem compartilhar mapas mutáveis entre agentes."""
    copied: Dict[str, Any] = {}
    for key, value in permissions.items():
        copied[key] = dict(value) if isinstance(value, Mapping) else value
    return copied


def _agent_permissions(
    source_file: str,
    fallback: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Deriva permissões autorais e aplica defaults fechados às mutações."""
    sections = _frontmatter_policy_sections(source_file)
    permissions: Dict[str, Any] = {}

    tools = sections.get("tools")
    if isinstance(tools, Mapping):
        for tool, enabled in tools.items():
            action = _permission_action(enabled)
            if action is not None:
                permissions[_canonical_permission_key(tool)] = action

    declared = sections.get("permission")
    direct_action = _permission_action(declared)
    if direct_action is not None:
        permissions["*"] = direct_action
    elif isinstance(declared, Mapping):
        for tool, raw_rule in declared.items():
            rule = _permission_rule(raw_rule)
            if rule is not None:
                permissions[_canonical_permission_key(tool)] = rule

    if not sections and fallback is not None:
        permissions = _copy_permissions(fallback)

    # Permissões omitidas seriam ``allow`` pelo OpenCode. Fechá-las aqui evita
    # escalada silenciosa; mapas autorais sem curinga usam aprovação por padrão.
    for permission_name in _MUTATION_PERMISSIONS:
        if permission_name not in permissions and "*" not in permissions:
            permissions[permission_name] = "deny"
            continue
        rule = permissions.get(permission_name)
        if isinstance(rule, Mapping) and not any(
            pattern in _BROAD_PATTERNS for pattern in rule
        ):
            permissions[permission_name] = {"*": "ask", **dict(rule)}

    return permissions or _copy_permissions(_DEFAULT_AGENT_PERMISSIONS)


def _catalog_agents() -> Dict[str, Any]:
    """Mapeia o catálogo de agentes para o formato de agentes do OpenCode CLI."""
    sys.path.insert(0, ROOT)
    from marceloclaro.catalog_loader import load_catalog_definitions

    agents: Dict[str, Any] = {}
    definitions = sorted(
        load_catalog_definitions(),
        key=lambda definition: os.path.basename(str(definition["source_file"])),
    )
    for d in definitions:
        # Chave = slug do nome do arquivo (estável, único, reproduzível).
        # NÃO usar d["agent_id"] (vem do frontmatter `name:`, que pode ser
        # um nome de exibição com espaços/maiúsculas e varia entre arquivos —
        # isso tornava o opencode.json não-reproduzível; ver SPEC-935-R137).
        slug = os.path.splitext(os.path.basename(d["source_file"]))[0]
        agents[slug] = {
            "description": d["description"][:200],
            "mode": "subagent",
            "prompt": "{file:./agents/catalog/" + os.path.basename(d["source_file"]) + "}",
            "permission": _agent_permissions(str(d["source_file"])),
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
                "permission": _agent_permissions(
                    os.path.join(agents_dir, name),
                    _ESSENTIAL_AGENT_PERMISSIONS.get(
                        agent_id, _DEFAULT_AGENT_PERMISSIONS
                    ),
                ),
            }
    return agents


def build_config() -> Dict[str, Any]:
    """Monta o opencode.json completo do ecossistema."""
    agents = _essential_agents()
    agents.update(_catalog_agents())
    # O orquestrador primário prevalece sobre eventuais homônimos do catálogo
    agents.pop("marceloclaro", None)
    # Agente especial da skill LiteRT/nano; não pertence ao catálogo legado.
    agents["nano-orchestrator"] = {
        "description": "Agente especializado em nano-orquestração de manuscritos (30-500 laudas) com LiteRT-LM, pipeline 7 fases SPEC-935-R53, SDD+TDD estrito. Use para manuscritos grandes, teses, livros técnicos.",
        "mode": "subagent",
        "prompt": "{file:./.opencode/agents/nano-orchestrator.md}",
        "temperature": 0.7,
        "permission": _agent_permissions(
            os.path.join(ROOT, ".opencode", "agents", "nano-orchestrator.md")
        ),
    }

    return {
        "$schema": "https://opencode.ai/config.json",
        "instructions": ["AGENTS.md"],
        "model": "litert-lm/litert-community/gemma-4-E2B-it-litert-lm",
        "permission": {"edit": "ask", "bash": "ask"},
        "provider": {
            "opencode-go": {
                "options": {
                    "apiKey": "{env:OPENCODE_API_KEY}",
                    "baseURL": "https://opencode.ai/zen/go/v1"
                }
            },
            "opencode-zen": {
                "options": {
                    "apiKey": "{env:OPENCODE_ZEN_API_KEY}",
                    "baseURL": "https://opencode.ai/zen/v1"
                }
            },
            "openai": {
                "options": {
                    "apiKey": "{env:OPENAI_API_KEY}",
                    "baseURL": "https://api.openai.com/v1"
                },
                "models": {
                    "gpt-4o": {"name": "GPT-4o"},
                    "gpt-4o-mini": {"name": "GPT-4o Mini (rápido)"},
                    "gpt-4.1": {"name": "GPT-4.1"},
                    "o3": {"name": "o3 (raciocínio)"},
                    "o4-mini": {"name": "o4-mini (raciocínio rápido)"}
                }
            },
            "litert-lm": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "LiteRT-LM (on-device)",
                "options": {
                    "apiKey": "sk-no-key-required",
                    "baseURL": "http://localhost:9379/v1"
                },
                "models": {
                    "litert-community/gemma-4-E2B-it-litert-lm": {
                        "name": "Gemma 4 2B Expert (on-device)",
                        "limit": {"context": 20480, "output": 2048}
                    },
                    "litert-community/gemma-4-E4B-it-litert-lm": {
                        "name": "Gemma 4 4B Expert (on-device)",
                        "limit": {"context": 20480, "output": 2048}
                    },
                    "litert-community/gemma-4-12B-it-litert-lm": {
                        "name": "Gemma 4 12B (on-device)",
                        "limit": {"context": 20480, "output": 2048}
                    },
                    "litert-community/Qwen3-0.6B": {
                        "name": "Qwen3 0.6B (on-device)",
                        "limit": {"context": 20480, "output": 2048}
                    }
                }
            },
            "colibri": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "Colibri Engine (OLMoE / GLM-5.2)",
                "options": {
                    "apiKey": "sk-no-key-required",
                    "baseURL": "http://localhost:8090/v1"
                },
                "models": {
                    "olmoe-1b-7b": {
                        "name": "OLMoE 1B/7B (Colibri MoE)",
                        "limit": {"context": 4096, "output": 1024}
                    },
                    "glm-5.2-colibri": {
                        "name": "GLM-5.2 (Colibri 744B MoE)",
                        "limit": {"context": 4096, "output": 1024}
                    }
                }
            }
        },
        "skills": {
            "paths": [".opencode/skills"]
        },
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
                "permission": {
                    "edit": "ask",
                    "bash": "ask",
                    "task": "allow",
                },
            },
            **agents,
        },
        "mcp": {
            "litert-lm": {
                "type": "local",
                "command": ["python3", ".opencode/mcp/litert_lm_server.py"],
                "enabled": True,
            },
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
            "pypi-search": {
                "type": "local",
                "command": ["python3", "skills/tooling/pypi_mcp_server.py"],
                "enabled": True,
            },
            "colibri-mcp": {
                "type": "local",
                "command": ["python3", "colibri/colibri_mcp_server.py"],
                "enabled": True,
            },
            "scanners-mcp": {
                "type": "local",
                "command": ["python3", "scanners/scanners_mcp_server.py"],
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
            "models": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from integrations.model_router import model_router; import json; print(json.dumps(model_router.list_all_models(), ensure_ascii=False, indent=2))\"",
                "description": "Lista todos os modelos disponíveis nos providers OpenCode Go e OpenCode Zen"
            },
            "route": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from integrations.model_router import model_router; import json; r = model_router.route('$ARGUMENTS' or 'coding'); print(json.dumps({'provider': r.provider_id, 'model': r.model_id, 'reason': r.reason, 'alternatives': [f'{p}/{m}' for p,m in r.alternatives]}, ensure_ascii=False, indent=2))\"",
                "description": "Roteia uma tarefa para o melhor modelo (ex: /route coding, /route reasoning, /route academic)"
            },
            "sdd": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from sdd.spec_engine import spec_registry; import json; print(json.dumps(spec_registry.coverage_report(), ensure_ascii=False, indent=2))\"",
                "description": "Relatório de cobertura SDD: specs formais e dinâmicas do ecossistema"
            },
            "tdd": {
                "template": "python3 -m pytest '$ARGUMENTS' -v --tb=short 2>&1 | tail -40",
                "description": "Executa a bateria de testes TDD (ex: /tdd tests/test_opencode_go_zen.py)"
            },
            "pypi": {
                "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from skills.tooling.pypi_search import search, format_output; import json; q = '$ARGUMENTS'.strip(); result = search(q, limit=10) if q else search('*', limit=5); print(format_output(result, json_output=('--json' in sys.argv)))\"",
                "description": "Busca bibliotecas Python no PyPI com scoring multicritério. Ex: /pypi scihub paper download, /pypi requests --json"
            }
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
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"opencode.json inválido ou ilegível: {exc}")
        return False
    if not isinstance(config, dict):
        print("opencode.json inválido — o conteúdo deve ser um objeto JSON")
        return False

    if config != build_config():
        print("opencode.json diverge do resultado de build_config() — regenere a configuração")
        return False

    n_agents = len(config.get("agent", {}))
    n_mcp = len(config.get("mcp", {}))
    n_cmd = len(config.get("command", {}))
    print(f"opencode.json OK: {n_agents} agentes, {n_mcp} MCP servers, {n_cmd} comandos")
    return n_agents > 0


class OpenCodeCLIIntegration:
    """Fachada orientada a objeto sobre `build_config`/`write_config`/
    `check_config`, para uso a partir de scripts externos (ex.:
    `installer/windows/provision.sh`, que já chamava esta classe antes
    dela existir — o passo de regeneração do `opencode.json` durante o
    provisionamento falhava silenciosamente por causa disso)."""

    def __init__(self, root: str = "."):
        self.root = os.path.abspath(root)
        self.config_path = os.path.join(self.root, "opencode.json")

    def build_config(self) -> Dict[str, Any]:
        return build_config()

    def generate_config(self) -> str:
        """Gera/regrava o opencode.json e retorna o path gravado."""
        config = build_config()
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return self.config_path

    def check(self) -> bool:
        return check_config(self.config_path)


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check_config() else 1)
    cfg = write_config()
    print(f"opencode.json gerado com {len(cfg['agent'])} agentes, "
          f"{len(cfg['mcp'])} MCP servers e {len(cfg['command'])} comandos.")
