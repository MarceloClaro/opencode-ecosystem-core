"""Catálogo Gemini Notebook e política pura; nunca executa um callback CLI.

O inventário importa o pacote externo apenas na chamada explícita. A integração
central executa esse inventário em subprocesso com o checkout pinado.
"""

from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from typing import Any


MCP_NAMES = (
    "refresh_auth", "save_auth_tokens", "batch", "notebook_query", "chat_configure",
    "notebook_query_start", "notebook_query_status", "chat_list", "chat_get", "chat_export",
    "collection_list", "collection_create", "collection_edit", "collection_set_emoji",
    "collection_delete", "cross_notebook_query", "download_artifact", "download_all_artifacts",
    "export_artifact", "label", "notebook_list", "notebook_get", "notebook_describe",
    "notebook_create", "notebook_rename", "notebook_delete", "note", "pipeline",
    "research_start", "research_status", "research_import", "server_info",
    "notebook_share_status", "notebook_share_public", "notebook_share_invite",
    "notebook_share_batch", "tag", "source_add", "source_list_drive", "source_sync_drive",
    "source_rename", "source_delete", "source_describe", "source_get_content", "studio_create",
    "studio_status", "studio_delete", "studio_revise", "usage_get",
)
SKILL_DESTINATIONS = (
    "claude-code", "cursor", "agents", "gemini-cli", "codex", "opencode",
    "antigravity", "cline", "openclaw", "alef-agent", "hermes", "other",
)

_MCP_READ = frozenset({
    "notebook_list", "notebook_get", "notebook_query_status", "chat_list", "chat_get",
    "chat_export", "collection_list", "source_list_drive", "source_get_content",
    "server_info", "usage_get", "notebook_share_status",
})
_MCP_INFERENCE = frozenset({
    "notebook_describe", "source_describe", "notebook_query", "notebook_query_start",
    "cross_notebook_query",
})
_MCP_WRITE = frozenset({
    "notebook_create", "notebook_rename", "source_add", "source_rename", "source_sync_drive",
    "chat_configure", "collection_create", "collection_edit", "collection_set_emoji",
    "research_start", "research_import", "studio_create", "studio_revise",
})
_MCP_DESTRUCTIVE = frozenset({
    "notebook_delete", "source_delete", "collection_delete", "studio_delete",
})
_EFFECT_ORDER = {v: i for i, v in enumerate((
    "read", "inference", "download", "write", "destructive", "publish", "auth_private",
))}
_STUDIO_TYPES = frozenset({
    "audio", "video", "infographic", "slide_deck", "report", "flashcards", "quiz", "data_table", "mind_map",
})
_DOWNLOAD_TYPES = _STUDIO_TYPES | {"data_table_xlsx", "file"}


def _enum_if_present(arguments: dict[str, Any], key: str, allowed: set[str] | frozenset[str]) -> None:
    if key in arguments and (not isinstance(arguments[key], str) or arguments[key].lower() not in allowed):
        raise ValueError(f"Subtipo desconhecido para {key}.")


def _boolean(arguments: dict[str, Any], key: str, default: bool = False) -> bool:
    value = arguments.get(key, default)
    if type(value) is not bool:
        raise ValueError(f"{key} deve ser booleano.")
    return value


def _action(arguments: dict[str, Any], allowed: dict[str, str], default: str | None = None) -> str:
    value = arguments.get("action", default)
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"Ação desconhecida; ações permitidas: {', '.join(allowed)}.")
    return allowed[value]


def classify_mcp_operation(name: str, args: dict[str, Any]) -> str:
    """Classifica o efeito externo real, inclusive ações compostas ou implícitas."""
    if name not in MCP_NAMES or not isinstance(args, dict):
        raise ValueError("Ferramenta MCP desconhecida ou argumentos inválidos.")
    if name == "source_add":
        _enum_if_present(args, "source_type", {"url", "text", "drive", "file"})
    if name == "studio_create":
        _enum_if_present(args, "artifact_type", _STUDIO_TYPES)
    if name == "download_artifact":
        _enum_if_present(args, "artifact_type", _DOWNLOAD_TYPES)
    if name == "export_artifact":
        _enum_if_present(args, "export_type", {"docs", "sheets"})
    if name == "research_start":
        _enum_if_present(args, "source", {"web", "drive"})
        _enum_if_present(args, "mode", {"fast", "deep"})
    if name in {"refresh_auth", "save_auth_tokens"}:
        return "auth_private"
    if name in _MCP_READ:
        return "read"
    if name in _MCP_INFERENCE:
        return "inference"
    if name in _MCP_WRITE:
        return "write"
    if name in _MCP_DESTRUCTIVE:
        return "destructive"
    if name in {"download_artifact", "download_all_artifacts"}:
        return "download"
    if name in {"export_artifact", "notebook_share_invite", "notebook_share_batch"}:
        return "publish"
    if name == "notebook_share_public":
        return "publish" if _boolean(args, "is_public", True) else "write"
    if name == "research_status":
        return "write" if _boolean(args, "auto_import") else "read"
    if name == "studio_status":
        return _action(args, {"status": "read", "list_types": "read", "rename": "write"}, "status")
    if name == "note":
        return _action(args, {"list": "read", "create": "write", "update": "write", "delete": "destructive"})
    if name == "label":
        effect = _action(args, {
            "auto": "write", "list": "write", "reorganize": "destructive", "create": "write",
            "rename": "write", "set_emoji": "write", "move_source": "write", "delete": "destructive",
        })
        if args.get("action") == "reorganize" and _boolean(args, "unlabeled_only"):
            return "write"
        return effect
    if name == "tag":
        return _action(args, {"add": "write", "remove": "write", "list": "read", "select": "read"})
    if name == "batch":
        if set(args) - {"action", "query", "source_url", "titles", "artifact_type", "notebook_names", "tags", "all", "confirm"}:
            raise ValueError("Campos batch desconhecidos.")
        if args.get("action") == "studio":
            _enum_if_present(args, "artifact_type", _STUDIO_TYPES)
        return _action(args, {"query": "inference", "add_source": "write", "create": "write", "delete": "destructive", "studio": "write"})
    if name == "pipeline":
        if set(args) - {"action", "notebook_id", "pipeline_name", "input_url", "steps", "_pipeline_steps"}:
            raise ValueError("Campos pipeline desconhecidos.")
        effect = _action(args, {"list": "read", "run": "destructive"})
        if args.get("action") == "list":
            return effect
        steps = args.get("_pipeline_steps", args.get("steps"))
        if steps is None:
            return "destructive"
        if not isinstance(steps, list) or not steps or len(steps) > 100:
            raise ValueError("Pipeline deve conter de 1 a 100 passos conhecidos.")
        effects = []
        allowed_steps = {"source_add", "notebook_query", "studio_create", "notebook_create", "notebook_delete"}
        for step in steps:
            if not isinstance(step, dict) or step.get("action") not in allowed_steps:
                raise ValueError("Ação de pipeline desconhecida.")
            params = step.get("params", {})
            if not isinstance(params, dict):
                raise ValueError("Parâmetros de pipeline inválidos.")
            effects.append(classify_mcp_operation(step["action"], params))
        return max(effects, key=_EFFECT_ORDER.__getitem__)
    raise ValueError("Ferramenta MCP sem política de efeitos.")


def _json_default(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_json_default(item) for item in value]
    return str(value)


def cli_inventory() -> list[dict[str, Any]]:
    """Obtém os callbacks/parametrizações Typer sem chamar qualquer callback."""
    from typer.main import get_command
    from notebooklm_tools.cli.main import app

    root = get_command(app)
    rows: list[dict[str, Any]] = []

    def walk(command: Any, path: tuple[str, ...] = ()) -> None:
        children = getattr(command, "commands", {})
        if command.callback is not None:
            params = []
            for param in command.params:
                kind = type(param).__name__
                type_name = type(param.type).__name__
                params.append({
                    "name": param.name,
                    "opts": list(getattr(param, "opts", [])),
                    "secondary_opts": list(getattr(param, "secondary_opts", [])),
                    "type": str(param.type),
                    "type_name": type_name,
                    "required": bool(param.required),
                    "nargs": param.nargs,
                    "is_flag": bool(getattr(param, "is_flag", False)),
                    "multiple": bool(getattr(param, "multiple", False)),
                    "argument": "Argument" in kind,
                    "choices": _json_default(getattr(param.type, "choices", None)),
                    "min": getattr(param.type, "min", None),
                    "max": getattr(param.type, "max", None),
                    "default": _json_default(param.default),
                    "help": getattr(param, "help", "") or "",
                })
            rows.append({
                "path": list(path), "help": command.help or "", "params": params,
                "callback": command.callback.__name__, "group": bool(children),
                "invoke_without_command": bool(getattr(command, "invoke_without_command", False)),
                "children": sorted(children),
            })
        for name, child in children.items():
            walk(child, path + (name,))

    walk(root)
    return rows


_SHELL_TOKENS = frozenset({";", "&&", "||", "|", ">", ">>", "<", "<<", "&"})
_PRIVATE_OPTIONS = frozenset({"--file", "-f", "--manual", "-m", "--cdp-url"})


def _convert(value: str, param: dict[str, Any]) -> Any:
    choices = param.get("choices")
    if choices is not None and value not in choices:
        raise ValueError(f"Valor inválido para {param['name']}.")
    type_name = param.get("type_name", param.get("type", "")).upper()
    if "INT" in type_name:
        try:
            converted: Any = int(value)
        except ValueError as exc:
            raise ValueError(f"{param['name']} deve ser inteiro.") from exc
    elif "FLOAT" in type_name:
        try:
            converted = float(value)
        except ValueError as exc:
            raise ValueError(f"{param['name']} deve ser número.") from exc
        if not math.isfinite(converted):
            raise ValueError("Números devem ser finitos.")
    else:
        return value
    for key, predicate in (("min", lambda x, y: x < y), ("max", lambda x, y: x > y)):
        limit = param.get(key)
        if limit is not None and predicate(converted, limit):
            raise ValueError(f"{param['name']} fora do intervalo permitido.")
    return converted


def _parse_params(tokens: list[str], params: list[dict[str, Any]], *, help_only: bool = False) -> dict[str, Any]:
    options = {}
    positional = []
    values = {}
    for param in params:
        if param.get("argument"):
            positional.append(param)
        else:
            for opt in param.get("opts", []):
                options[opt] = (param, True)
            for opt in param.get("secondary_opts", []):
                options[opt] = (param, False)
        values[param["name"]] = deepcopy(param.get("default"))
    position_tokens = []
    seen = set()
    index = 0
    positional_only = False
    while index < len(tokens):
        token = tokens[index]
        if token == "--help":
            index += 1
            continue
        if token == "--" and not positional_only:
            positional_only = True
            index += 1
            continue
        if token.startswith("-") and not positional_only:
            opt, separator, inline = token.partition("=")
            if opt not in options:
                # Negative numbers are legal positional values for numeric parameters.
                if re.fullmatch(r"-\d+(?:\.\d+)?", token):
                    position_tokens.append(token)
                    index += 1
                    continue
                raise ValueError(f"Opção desconhecida: {opt}.")
            param, flag_value = options[opt]
            name = param["name"]
            if name in seen and not param.get("multiple"):
                raise ValueError(f"Opção repetida: {opt}.")
            seen.add(name)
            if param.get("is_flag"):
                if separator:
                    raise ValueError(f"Flag não aceita valor: {opt}.")
                value = flag_value
            else:
                if separator:
                    value = inline
                else:
                    index += 1
                    if index >= len(tokens) or tokens[index].startswith("--"):
                        raise ValueError(f"Valor ausente para {opt}.")
                    value = tokens[index]
                value = _convert(value, param)
            if param.get("multiple"):
                if name not in values or values[name] is None or name not in seen or not isinstance(values[name], list):
                    values[name] = []
                values[name].append(value)
            else:
                values[name] = value
        else:
            position_tokens.append(token)
        index += 1
    cursor = 0
    for param in positional:
        count = param.get("nargs", 1)
        if count == -1:
            values[param["name"]] = [_convert(v, param) for v in position_tokens[cursor:]]
            cursor = len(position_tokens)
        elif cursor + count <= len(position_tokens):
            items = [_convert(v, param) for v in position_tokens[cursor:cursor + count]]
            values[param["name"]] = items[0] if count == 1 else items
            cursor += count
        elif param.get("required") and not help_only:
            raise ValueError(f"Argumento ausente: {param['name']}.")
    if cursor != len(position_tokens):
        raise ValueError("Argumentos posicionais excedentes.")
    if not help_only:
        for param in params:
            value = values.get(param["name"])
            if param.get("required") and (value is None or (param.get("nargs") == -1 and not value)):
                raise ValueError(f"Parâmetro obrigatório ausente: {param['name']}.")
    return values


def _cli_effect(path: tuple[str, ...], values: dict[str, Any]) -> str:
    if not path:
        return "read"
    if path == ("login",):
        return "read" if values.get("check") is True else "auth_private"
    if path == ("login", "profile", "list"):
        return "read"
    if path == ("login", "profile", "delete"):
        return "destructive"
    if path[0] in {"login", "auth"}:
        return "auth_private"
    if path == ("usage",) or path == ("doctor",):
        return "read"
    if path[0] == "doctor":
        return "auth_private"
    verb_aliases = {
        ("list", "notebooks"): ("notebook", "list"), ("list", "sources"): ("source", "list"),
        ("list", "artifacts"): ("studio", "status"), ("list", "aliases"): ("alias", "list"),
        ("list", "stale-sources"): ("source", "stale"), ("list", "skills"): ("skill", "list"),
        ("get", "notebook"): ("notebook", "get"), ("get", "source"): ("source", "get"),
        ("get", "config"): ("config", "get"), ("get", "alias"): ("alias", "get"),
        ("delete", "notebook"): ("notebook", "delete"), ("delete", "source"): ("source", "delete"),
        ("delete", "artifact"): ("studio", "delete"), ("delete", "alias"): ("alias", "delete"),
        ("add", "url"): ("source", "add"), ("add", "text"): ("source", "add"),
        ("add", "drive"): ("source", "add"), ("rename", "notebook"): ("notebook", "rename"),
        ("rename", "source"): ("source", "rename"), ("rename", "studio"): ("studio", "rename"),
        ("status", "artifacts"): ("studio", "status"), ("status", "research"): ("research", "status"),
        ("describe", "notebook"): ("notebook", "describe"), ("describe", "source"): ("source", "describe"),
        ("query", "notebook"): ("notebook", "query"), ("sync", "sources"): ("source", "sync"),
        ("content", "source"): ("source", "content"), ("stale", "sources"): ("source", "stale"),
        ("configure", "chat"): ("chat", "configure"), ("set", "alias"): ("alias", "set"),
        ("set", "config"): ("config", "set"), ("show", "config"): ("config", "show"),
        ("show", "aliases"): ("alias", "list"), ("show", "skill"): ("skill", "show"),
        ("install", "skill"): ("skill", "install"), ("uninstall", "skill"): ("skill", "uninstall"),
        ("update", "skill"): ("skill", "update"),
    }
    if path[0] == "create":
        return "write"
    path = verb_aliases.get(path, path)
    group = path[0]
    action = path[-1]
    if group in {"audio", "report", "quiz", "flashcards", "mindmap", "slides", "infographic", "video", "data-table"}:
        return "read" if action == "list" else "write"
    if group == "notebook":
        return {"list": "read", "get": "read", "describe": "inference", "query": "inference", "create": "write", "rename": "write", "delete": "destructive"}[action]
    if group == "label":
        if action == "delete" or (action == "reorganize" and not values.get("unlabeled_only", False)):
            return "destructive"
        return "write"
    if group == "note":
        return "read" if action == "list" else ("destructive" if action == "delete" else "write")
    if group == "source":
        return {"list": "read", "get": "read", "content": "read", "stale": "read", "describe": "inference", "add": "write", "rename": "write", "sync": "write", "delete": "destructive"}[action]
    if group == "chats":
        if action == "to-note":
            return "write"
        return "download" if action == "export" and values.get("output") else "read"
    if group == "chat":
        return "inference" if action == "start" else "write"
    if group == "studio":
        return {"status": "read", "rename": "write", "delete": "destructive"}[action]
    if group == "research":
        return "read" if action == "status" and not values.get("auto_import", False) else "write"
    if group in {"alias", "config"}:
        return "read" if action in {"list", "get", "show"} else ("destructive" if action == "delete" else "write")
    if group == "download":
        return "download"
    if group == "share":
        return "read" if action == "status" else ("write" if action == "private" else "publish")
    if group == "export":
        return "publish"
    if group in {"skill", "setup"}:
        return "read" if action in {"list", "show"} else ("destructive" if action in {"uninstall", "remove"} else "write")
    if group == "batch":
        return "inference" if action == "query" else ("destructive" if action == "delete" else "write")
    if group == "cross":
        return "inference"
    if group == "pipeline":
        return "read" if action == "list" else ("write" if action == "create" else "destructive")
    if group == "tag":
        return "read" if action in {"list", "select"} else "write"
    raise ValueError("Comando CLI sem política de efeitos.")


def classify_cli_argv(argv: list[str], catalog: list[dict[str, Any]]) -> dict[str, Any]:
    """Valida tokens sem shell, converte parâmetros e classifica todos os caminhos."""
    if not isinstance(argv, list) or len(argv) > 200 or not all(isinstance(v, str) and len(v) <= 65536 for v in argv):
        raise ValueError("Argumentos CLI inválidos.")
    # O serviço central exige o executável fixo; callers da política pura podem
    # fornecer somente os argumentos. Nunca resolvemos outro binário aqui.
    argv = list(argv[1:] if argv and argv[0] == "nlm" else argv)
    if not isinstance(catalog, list):
        raise ValueError("Catálogo CLI inválido.")
    for token in argv:
        if token in _SHELL_TOKENS or any(s in token for s in ("\x00", "\n", "\r", "`", "$(")):
            raise ValueError("Tokens de shell não são aceitos.")
        if token.partition("=")[0] in {"--debug", "--install-completion"}:
            raise ValueError("Debug e instalação de completion não são aceitos no canal compartilhado.")
    entries = {tuple(row["path"]): row for row in catalog}
    if len(entries) != len(catalog) or () not in entries:
        raise ValueError("Catálogo CLI deve possuir raiz e caminhos únicos.")
    prefixes = {p[:i] for p in entries for i in range(len(p) + 1)}
    root = entries[()]
    prefix_tokens = []
    index = 0
    root_options = {opt: p for p in root["params"] for opt in p.get("opts", []) + p.get("secondary_opts", [])}
    while index < len(argv) and argv[index].startswith("-"):
        token = argv[index]
        if token == "--help":
            prefix_tokens.append(token)
            index += 1
            continue
        opt = token.partition("=")[0]
        if opt not in root_options:
            raise ValueError(f"Opção raiz desconhecida: {opt}.")
        prefix_tokens.append(token)
        if not root_options[opt].get("is_flag") and "=" not in token:
            index += 1
            if index >= len(argv):
                raise ValueError("Valor ausente para opção raiz.")
            prefix_tokens.append(argv[index])
        index += 1
    _parse_params(prefix_tokens, root["params"], help_only="--help" in argv)
    path: tuple[str, ...] = ()
    while index < len(argv) and path + (argv[index],) in prefixes:
        path += (argv[index],)
        index += 1
    help_only = "--help" in argv
    if path not in entries:
        if help_only and path in prefixes and argv[index:] == ["--help"]:
            return {"command_path": list(path), "effect": "read", "parameters": {}, "help_only": True, "interactive": False}
        raise ValueError("Caminho de comando CLI desconhecido ou grupo sem comando.")
    if path and path[0] == "login" and any(token.partition("=")[0] in _PRIVATE_OPTIONS for token in argv[index:]):
        raise ValueError("Importação manual de credenciais exige CLI privada; não passa pelo Core compartilhado.")
    params = _parse_params(argv[index:], entries[path]["params"], help_only=help_only)
    if not path and prefix_tokens:
        params.update(_parse_params(prefix_tokens, root["params"], help_only=help_only))
    effect = "read" if help_only else _cli_effect(path, params)
    interactive = not help_only and (path == ("chat", "start") or (path == ("login",) and not params.get("check")))
    return {"command_path": list(path), "effect": effect, "parameters": params, "help_only": help_only, "interactive": interactive}


def main() -> None:
    print(json.dumps(cli_inventory(), ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
