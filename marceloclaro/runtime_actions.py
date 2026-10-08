"""Validação pura de interfaces científicas R671, antes de efeitos."""
from __future__ import annotations

import json
import re

METHODS = {"runtime": "scientific_runtime_run", "dataset": "scientific_dataset_download",
           "personalizar": "scientific_dataset_custom", "plugins": "scientific_plugin_action",
           "notebook": "gemini_notebook_action"}


def validate_action(kind, config):
    if kind == "notebook":
        from integrations.gemini_notebook import validate_notebook_config
        return validate_notebook_config(config)
    from integrations.scientific_plugins import _json, _slug, PLUGINS, validate_plugin_request
    if not isinstance(config, dict):
        raise ValueError("Configuração deve ser objeto JSON")
    out = json.loads(_json(config))
    if kind == "runtime":
        from integrations.live_scientific_runtime import validate_runtime_config
        return validate_runtime_config(out)
    fields = {
        "dataset": {"provider", "dataset_id", "filenames", "output_dir", "revision", "max_bytes"},
        "personalizar": {"source_manifests", "output_dir", "name", "domain", "seed"},
    }
    if kind in fields:
        if set(out) - fields[kind]:
            raise ValueError("Campos desconhecidos")
        path = out.get("output_dir")
        if not isinstance(path, str) or not 1 <= len(path) <= 2000 or "\x00" in path:
            raise ValueError("Diretório de saída inválido")
        if kind == "dataset":
            from integrations.dataset_cli import _filename
            if out.get("provider") not in {"kaggle", "huggingface"}:
                raise ValueError("Provedor desconhecido")
            dataset = out.get("dataset_id")
            if not isinstance(dataset, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}/[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", dataset):
                raise ValueError("Dataset inválido")
            files = out.get("filenames")
            if not isinstance(files, list) or not 1 <= len(files) <= 5 or any(not isinstance(f, str) for f in files) or len(set(files)) != len(files):
                raise ValueError("Seleção de arquivos inválida")
            for filename in files:
                _filename(filename)
            revision = out.get("revision")
            if revision is not None and (not isinstance(revision, str) or ".." in revision or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", revision)):
                raise ValueError("Versão inválida")
            if out["provider"] == "kaggle" and revision is not None and not re.fullmatch(r"[1-9][0-9]{0,8}", revision):
                raise ValueError("Versão Kaggle deve ser número positivo")
            maximum = out.get("max_bytes", 20000000)
            if type(maximum) is not int or not 1 <= maximum <= 20000000:
                raise ValueError("Limite de download inválido")
        else:
            manifests = out.get("source_manifests")
            if not isinstance(manifests, list) or not 1 <= len(manifests) <= 5 or any(not isinstance(p, str) or not 1 <= len(p) <= 2000 for p in manifests):
                raise ValueError("Manifestos de origem inválidos")
            if type(out.get("seed", 668)) is not int or not 0 <= out.get("seed", 668) <= 2**32-1:
                raise ValueError("Semente inválida")
            for key in ("name", "domain"):
                if key in out:
                    _slug(out[key])
        return out
    if kind != "plugins":
        raise ValueError("Interface desconhecida")
    operation = out.get("operation")
    schemas = {
        "status": set(), "sync": {"cache_root", "plugin_ids"},
        "skill": {"plugin_id", "skill_name"}, "request": {"plugin_id", "action", "arguments", "intent"},
        "result": {"request_id"}, "response": {"request_id", "host_tool", "request_sha256", "result", "reported_by"},
        "local": {"plugin_id", "action", "arguments"},
    }
    if operation not in schemas or set(out) - schemas[operation] - {"operation"}:
        raise ValueError("Operação/campos de plugins desconhecidos")
    if operation in {"skill", "request", "local"} and out.get("plugin_id") not in PLUGINS:
        raise ValueError("Plugin desconhecido")
    if operation == "skill":
        _slug(out.get("skill_name"))
    if operation == "request":
        validate_plugin_request(out.get("plugin_id"), out.get("action"), out.get("arguments"), out.get("intent"))
    if operation in {"result", "response"}:
        _slug(out.get("request_id"))
    if operation == "sync":
        if "cache_root" in out and (not isinstance(out["cache_root"], str) or not 1 <= len(out["cache_root"]) <= 2000):
            raise ValueError("Cache inválido")
        ids = out.get("plugin_ids", list(PLUGINS))
        if not isinstance(ids, list) or not 1 <= len(ids) <= 12 or any(pid not in PLUGINS for pid in ids) or len(set(ids)) != len(ids):
            raise ValueError("Seleção de plugins inválida")
    if operation == "response":
        if not isinstance(out.get("request_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", out["request_sha256"]):
            raise ValueError("Hash da requisição inválido")
        for key in ("host_tool", "reported_by"):
            if not isinstance(out.get(key), str) or not 1 <= len(out[key]) <= 200:
                raise ValueError("Identidade do host/ferramenta inválida")
        if not isinstance(out.get("result"), dict) or not out["result"]:
            raise ValueError("Resposta ausente")
    if operation == "local":
        args = out.get("arguments", {})
        allowed = {("boltz-api-cli", "version"), ("boltz-api-cli", "auth_status"),
                   ("life-sciences-literature", "pubmed_search")}
        if (out["plugin_id"], out.get("action")) not in allowed or not isinstance(args, dict):
            raise ValueError("Operação local não registrada")
        if out["plugin_id"] == "boltz-api-cli" and args:
            raise ValueError("Operação Boltz não recebe argumentos")
        if out["plugin_id"] == "life-sciences-literature" and (set(args) != {"term"} or not isinstance(args["term"], str) or not 1 <= len(args["term"]) <= 500):
            raise ValueError("Pesquisa PubMed inválida")
    return out
