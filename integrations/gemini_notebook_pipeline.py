"""Preflight somente leitura de pipelines oficiais Gemini Notebook.

Extrai os templates literais do módulo instalado por AST e lê exclusivamente
definições YAML de pipelines. Não importa o cliente, acessa login ou executa
callbacks. O executor deve verificar novamente o hash antes de despachar.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse

import yaml

from integrations.gemini_notebook_catalog import classify_mcp_operation


_LIMIT = 131072
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
_PRIVATE_KEY = re.compile(r"cookie|authorization|password|secret|credential|session[_-]?id|(?:access|refresh|auth|csrf)[_-]?token|api[_-]?key", re.I)
_PRIVATE_VALUE = re.compile(r"(?i)(?:\bbearer\s+|\bcookie\s*:|\bpassword\s*=|\b(?:access|refresh|auth|csrf)_?token\s*=)")
_STEP_FIELDS = {
    "source_add": {"type", "url", "text"},
    "notebook_query": {"query"},
    "studio_create": {"artifact_type", "focus_prompt", "audio_format", "audio_length", "report_format", "custom_prompt", "language"},
    "notebook_create": {"title"},
    "notebook_delete": set(),
}


class _Blocked(ValueError):
    pass


def _official_module() -> Path:
    spec = importlib.util.find_spec("notebooklm_tools")
    if spec is None or not spec.submodule_search_locations:
        raise _Blocked("official_pipeline_module_unavailable")
    return Path(next(iter(spec.submodule_search_locations))).resolve() / "services/pipeline.py"


def _read_limited(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise _Blocked("unsafe_pipeline_definition")
    before = path.stat()
    if before.st_size > _LIMIT:
        raise _Blocked("pipeline_definition_too_large")
    with path.open("rb") as handle:
        data = handle.read(_LIMIT + 1)
    after = path.stat()
    if len(data) > _LIMIT:
        raise _Blocked("pipeline_definition_too_large")
    if (before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_ino, after.st_mtime_ns, after.st_size):
        raise _Blocked("pipeline_definition_changed_during_read")
    return data


def _builtins() -> tuple[dict[str, Any], Path, bytes]:
    path = _official_module()
    raw = _read_limited(path)
    try:
        tree = ast.parse(raw.decode("utf-8"))
        candidates = []
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "BUILTIN_PIPELINES" for t in node.targets):
                candidates.append(node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "BUILTIN_PIPELINES":
                candidates.append(node.value)
        if len(candidates) != 1:
            raise ValueError("literal unavailable")
        templates = ast.literal_eval(candidates[0])
        if not isinstance(templates, dict):
            raise ValueError("mapping required")
    except (ValueError, TypeError, SyntaxError, UnicodeError, RecursionError) as exc:
        raise _Blocked("official_pipeline_templates_not_literal") from exc
    return templates, path, raw


class _UniqueLoader(yaml.SafeLoader):
    def construct_mapping(self, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[str, Any]:
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise _Blocked("ambiguous_pipeline_mapping")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def _bounded_value(value: Any, *, depth: int = 0, budget: list[int] | None = None, ancestors: set[int] | None = None) -> None:
    budget = budget if budget is not None else [2000]
    ancestors = ancestors if ancestors is not None else set()
    budget[0] -= 1
    if depth > 16 or budget[0] < 0:
        raise _Blocked("pipeline_definition_structure_too_large")
    if isinstance(value, (dict, list)):
        marker = id(value)
        if marker in ancestors:
            raise _Blocked("recursive_pipeline_definition")
        ancestors.add(marker)
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str) or _PRIVATE_KEY.search(key):
                    raise _Blocked("private_pipeline_configuration")
                _bounded_value(item, depth=depth + 1, budget=budget, ancestors=ancestors)
        else:
            for item in value:
                _bounded_value(item, depth=depth + 1, budget=budget, ancestors=ancestors)
        ancestors.remove(marker)
    elif isinstance(value, str):
        if len(value) > 65536 or "\x00" in value or _PRIVATE_VALUE.search(value):
            raise _Blocked("private_or_invalid_pipeline_value")
    elif value is None or type(value) in {bool, int}:
        return
    elif type(value) is float:
        if not math.isfinite(value):
            raise _Blocked("nonfinite_pipeline_value")
    else:
        raise _Blocked("unsupported_pipeline_value")


def _canonical(value: Any) -> bytes:
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(data) > _LIMIT:
        raise _Blocked("pipeline_definition_too_large")
    return data


def _validate_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise _Blocked("invalid_pipeline_source_url")


def pipeline_preflight(name: str, notebook_id: str, input_url: str = "", root: str | Path | None = None) -> dict[str, Any]:
    """Inspeciona a definição que o upstream selecionará sem escrever arquivos.

    ``root`` é o armazenamento upstream (contém ``pipelines/*.yaml``), não o
    repositório Core. Sem ele, usa NOTEBOOKLM_MCP_CLI_PATH ou a pasta padrão.
    Templates builtin têm precedência, como no loader oficial. Hashes vinculam
    a definição original, o arquivo de origem e os passos efetivos mostrados.
    """
    base: dict[str, Any] = {"status": "blocked", "process_executed": False, "remote_operation_executed": False}
    try:
        if not isinstance(name, str) or not _NAME.fullmatch(name) or not isinstance(notebook_id, str) or not notebook_id.strip() or len(notebook_id) > 200:
            raise _Blocked("invalid_pipeline_request")
        if not isinstance(input_url, str) or len(input_url) > 8192 or "\x00" in notebook_id + input_url:
            raise _Blocked("invalid_pipeline_request")
        _bounded_value({"notebook_id": notebook_id, "input_url": input_url})
        if input_url:
            _validate_url(input_url)
        templates, module, module_raw = _builtins()
        if name in templates:
            definition = templates[name]
            source, raw, kind = module, module_raw, "builtin"
        else:
            storage = Path(root).expanduser() if root is not None else Path(os.environ.get("NOTEBOOKLM_MCP_CLI_PATH", "").strip() or Path.home() / ".notebooklm-mcp-cli")
            storage = storage.resolve()
            directory = storage / "pipelines"
            if directory.is_symlink():
                raise _Blocked("unsafe_pipeline_definition")
            source = directory / f"{name}.yaml"
            if not source.exists() and not source.is_symlink():
                raise _Blocked("pipeline_not_found")
            if not source.resolve().is_relative_to(storage):
                raise _Blocked("unsafe_pipeline_definition")
            raw = _read_limited(source)
            try:
                definition = yaml.load(raw.decode("utf-8"), Loader=_UniqueLoader)
            except (yaml.YAMLError, UnicodeError, RecursionError) as exc:
                raise _Blocked("invalid_pipeline_yaml") from exc
            kind = "user"
        _bounded_value(definition)
        if not isinstance(definition, dict) or set(definition) - {"name", "description", "steps"}:
            raise _Blocked("invalid_pipeline_definition")
        if "name" in definition and definition["name"] != name:
            raise _Blocked("pipeline_definition_name_mismatch")
        actual_steps = definition.get("steps")
        if not isinstance(actual_steps, list) or not 1 <= len(actual_steps) <= 100:
            raise _Blocked("invalid_pipeline_steps")
        variables = {"NOTEBOOK_ID": notebook_id, "INPUT_URL": input_url}
        unsupported = set()
        steps = []
        for index, step in enumerate(actual_steps, 1):
            if not isinstance(step, dict) or set(step) - {"action", "params"} or step.get("action") not in _STEP_FIELDS:
                raise _Blocked("unsupported_pipeline_step")
            action = step["action"]
            params = step.get("params", {})
            if not isinstance(params, dict) or set(params) - _STEP_FIELDS[action]:
                raise _Blocked("unsupported_pipeline_parameters")
            resolved = {}
            for key, value in params.items():
                if not isinstance(value, str):
                    raise _Blocked("invalid_pipeline_parameters")
                if value.startswith("$"):
                    variable = value[1:]
                    if variable not in variables or not variables[variable]:
                        raise _Blocked("unresolved_pipeline_variable")
                    if variable == "NOTEBOOK_ID":
                        unsupported.add(variable)
                    value = variables[variable]
                resolved[key] = value
            if action == "source_add":
                source_type = resolved.get("type", "url")
                if source_type not in {"url", "text"}:
                    # _execute_step não passa document_id/file_path ao serviço.
                    raise _Blocked("unsupported_pipeline_source_type")
                if source_type == "url":
                    _validate_url(resolved.get("url", ""))
                elif not resolved.get("text", "").strip():
                    raise _Blocked("missing_pipeline_source_text")
            if action == "notebook_query" and not resolved.get("query", "").strip():
                raise _Blocked("missing_pipeline_query")
            effect = classify_mcp_operation(action, resolved)
            steps.append({"step": index, "action": action, "notebook_id": notebook_id, "params": resolved, "effect": effect})
        effect = classify_mcp_operation("pipeline", {"action": "run", "steps": steps})
        result = {**base, "status": "prepared", "pipeline_name": name, "notebook_id": notebook_id,
                  "definition_source": {"kind": kind, "path": str(source), "sha256": hashlib.sha256(raw).hexdigest(),
                                        "official_module_sha256": hashlib.sha256(module_raw).hexdigest()},
                  "definition_sha256": hashlib.sha256(_canonical(definition)).hexdigest(),
                  "effective_steps_sha256": hashlib.sha256(_canonical(steps)).hexdigest(),
                  "step_count": len(steps), "steps": steps, "effect": effect}
        if unsupported:
            # O preview resolve o identificador para mostrar a intenção, porém a
            # interface oficial só injeta INPUT_URL. Bloqueia discrepância.
            result.update(status="blocked", reason="unsupported_upstream_variable", unsupported_variables=sorted(unsupported))
        return result
    except _Blocked as exc:
        return {**base, "reason": str(exc)}
    except (OSError, ValueError, TypeError, RecursionError):
        return {**base, "reason": "pipeline_preflight_failed"}
