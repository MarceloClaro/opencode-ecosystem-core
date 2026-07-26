# -*- coding: utf-8 -*-
"""Testes RED herméticos de CA28 da SPEC-935-R212 v1.1.

Os testes exercitam somente a geração em memória ou em ``tmp_path``. Nenhum
arquivo de produção, spec ou configuração versionada é alterado.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = PROJECT_ROOT / "agents" / "catalog"
MUTATION_TOOLS = ("write", "edit", "bash")
WILDCARD_PATTERNS = {"*", "**", "**/*"}

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integrations.opencode_cli import build_config, write_config


def _normalized_scalar(value: Any) -> str | None:
    """Normaliza ações booleanas e textuais usadas pelas duas APIs de config."""

    if value is True:
        return "allow"
    if value is False:
        return "deny"
    if isinstance(value, str):
        normalized = value.strip().strip("\"'").lower()
        if normalized in {"allow", "ask", "deny"}:
            return normalized
    return None


def _broad_action(value: Any) -> str | None:
    """Obtém a última regra curinga, conforme a precedência do OpenCode."""

    direct = _normalized_scalar(value)
    if direct is not None:
        return direct
    if not isinstance(value, Mapping):
        return None

    broad: str | None = None
    for pattern, action in value.items():
        if str(pattern).strip().strip("\"'") in WILDCARD_PATTERNS:
            normalized = _normalized_scalar(action)
            if normalized is not None:
                broad = normalized
    return broad


def _mutation_actions(agent: Mapping[str, Any], tool: str) -> list[str]:
    """Coleta concessões/negações amplas em ``tools`` e ``permission``."""

    actions: list[str] = []
    tools = agent.get("tools")
    if isinstance(tools, Mapping) and tool in tools:
        action = _broad_action(tools[tool])
        if action is not None:
            actions.append(action)

    permission = agent.get("permission")
    top_level_action = _normalized_scalar(permission)
    if top_level_action is not None:
        actions.append(top_level_action)
    elif isinstance(permission, Mapping):
        permission_keys = ("write", "edit") if tool == "write" else (tool,)
        for permission_key in permission_keys:
            if permission_key in permission:
                action = _broad_action(permission[permission_key])
                if action is not None:
                    actions.append(action)
    return actions


def _has_unrestricted_allow(agent: Mapping[str, Any], tool: str) -> bool:
    actions = _mutation_actions(agent, tool)
    return "allow" in actions and "deny" not in actions


def _has_explicit_deny_without_allow(
    agent: Mapping[str, Any],
    tool: str,
) -> bool:
    actions = _mutation_actions(agent, tool)
    return "deny" in actions and "allow" not in actions


def _frontmatter(source: str) -> str:
    """Extrai YAML inicial mesmo quando há comentário HTML antes dele."""

    without_leading_comment = re.sub(
        r"^\s*<!--.*?-->\s*",
        "",
        source,
        count=1,
        flags=re.DOTALL,
    )
    match = re.match(r"^---\s*\n(.*?)\n---", without_leading_comment, re.DOTALL)
    return match.group(1) if match else ""


def _declared_mutation_denials(path: Path) -> set[str]:
    """Lê somente negações explícitas de ``tools``/``permission`` do YAML.

    O parser é intencionalmente estreito e baseado em indentação: isso mantém o
    teste sem dependência YAML e cobre apenas as três chaves de segurança cujo
    contrato CA28 precisa preservar.
    """

    section: str | None = None
    permission_tool: str | None = None
    tool_actions: dict[str, str] = {}
    permission_rules: dict[str, list[tuple[str | None, str]]] = {}

    for raw_line in _frontmatter(path.read_text(encoding="utf-8")).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indentation = len(raw_line) - len(raw_line.lstrip(" "))
        key, separator, raw_value = raw_line.strip().partition(":")
        if not separator:
            continue
        key = key.strip().strip("\"'")
        value = raw_value.strip().strip("\"'").lower()

        if indentation == 0:
            section = key if key in {"tools", "permission"} else None
            permission_tool = None
            continue

        if section == "tools" and indentation == 2 and key in MUTATION_TOOLS:
            tool_actions[key] = value
            continue

        if section != "permission":
            continue
        if indentation == 2:
            permission_tool = key if key in MUTATION_TOOLS else None
            if permission_tool is not None and value:
                permission_rules.setdefault(permission_tool, []).append((None, value))
            continue
        if indentation >= 4 and permission_tool is not None:
            permission_rules.setdefault(permission_tool, []).append((key, value))

    denials = {tool for tool, action in tool_actions.items() if action == "false"}
    for tool, rules in permission_rules.items():
        broad_action: str | None = None
        for pattern, action in rules:
            if pattern is None or pattern in WILDCARD_PATTERNS:
                broad_action = action
        if broad_action == "deny":
            denials.add(tool)
    return denials


def _read_only_declarations() -> dict[str, set[str]]:
    """Retorna agentes que negam escrita/edição e suas negações declaradas."""

    declarations: dict[str, set[str]] = {}
    for path in sorted(CATALOG_DIR.glob("*.md")):
        denials = _declared_mutation_denials(path)
        denies_file_mutation = {"write", "edit"} <= denials
        if denies_file_mutation:
            declarations[path.stem] = denials
    return declarations


def test_build_config_nao_concede_write_edit_bash_universalmente():
    """CA28 negativo: nenhum dos três poderes pode ser dado a todo agente."""

    # Arrange: materializa a configuração completa e seus agentes.
    agents = build_config()["agent"]
    assert agents

    # Act: identifica concessões irrestritas para cada poder de mutação.
    universally_allowed = {
        tool: {
            agent_id
            for agent_id, agent in agents.items()
            if _has_unrestricted_allow(agent, tool)
        }
        for tool in MUTATION_TOOLS
    }

    # Assert: a geração nunca pode usar o mesmo allow irrestrito para todos.
    all_agent_ids = set(agents)
    for tool, allowed_agent_ids in universally_allowed.items():
        assert allowed_agent_ids != all_agent_ids, (
            f"build_config() concedeu {tool!r} irrestrito aos "
            f"{len(all_agent_ids)} agentes"
        )


def test_security_auditor_tem_toda_mutacao_explicitamente_negada():
    """CA28 negativo: o auditor de segurança permanece estritamente read-only."""

    # Arrange: confirma primeiro o contrato autoral do frontmatter.
    source_denials = _declared_mutation_denials(
        CATALOG_DIR / "security-auditor.md"
    )
    assert source_denials == set(MUTATION_TOOLS)

    # Act: consulta a entrada efetivamente produzida pelo gerador.
    generated_agent = build_config()["agent"]["security-auditor"]

    # Assert: tools/permission devem negar, e nunca conceder, cada mutação.
    for tool in MUTATION_TOOLS:
        assert _has_explicit_deny_without_allow(generated_agent, tool), (
            f"security-auditor não preservou a negação de {tool}: "
            f"{generated_agent!r}"
        )


def test_todos_os_agentes_declarados_read_only_preservam_negacoes_de_mutacao():
    """CA28 negativo: o gerador preserva as restrições autorais do catálogo."""

    # Arrange: deriva localmente os agentes read-only e suas negações explícitas.
    declarations = _read_only_declarations()
    agents = build_config()["agent"]
    assert "security-auditor" in declarations
    assert "contextscout" in declarations

    # Act: coleta ausências e escaladas de privilégio de forma reproduzível.
    violations: list[str] = []
    for agent_id, denied_tools in declarations.items():
        generated_agent = agents.get(agent_id)
        if generated_agent is None:
            violations.append(f"{agent_id}: ausente da configuração")
            continue
        for tool in sorted(denied_tools):
            if not _has_explicit_deny_without_allow(generated_agent, tool):
                violations.append(
                    f"{agent_id}: negação declarada de {tool} não preservada"
                )

    # Assert: nenhuma declaração read-only pode virar permissão de mutação.
    assert not violations, "Escaladas no build_config():\n- " + "\n- ".join(violations)


def test_coder_mantem_capacidades_necessarias_de_implementacao():
    """CA28 positivo: least privilege não remove escrita, edição ou shell do coder."""

    # Arrange: obtém somente o agente essencial responsável por implementação.
    coder = build_config()["agent"]["coder"]

    # Act: calcula as concessões amplas semanticamente, em tools ou permission.
    allowed = {
        tool: _has_unrestricted_allow(coder, tool) for tool in MUTATION_TOOLS
    }

    # Assert: o coder continua apto a escrever, editar e executar testes/comandos.
    assert allowed == {"write": True, "edit": True, "bash": True}


def test_build_config_e_identico_ao_opencode_json_apos_geracao(
    tmp_path: Path,
):
    """CA23/CA28 positivo: gerar é determinístico e não cria drift no artefato."""

    # Arrange: captura a saída em memória e escolhe destino temporário hermético.
    expected = build_config()
    generated_path = tmp_path / "opencode.json"

    # Act: executa a geração somente dentro de tmp_path e relê ambos os artefatos.
    returned = write_config(str(generated_path))
    persisted = json.loads(generated_path.read_text(encoding="utf-8"))
    committed = json.loads(
        (PROJECT_ROOT / "opencode.json").read_text(encoding="utf-8")
    )

    # Assert: memória, geração temporária e opencode.json versionado são idênticos.
    assert returned == expected
    assert persisted == expected
    assert committed == expected
