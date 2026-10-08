"""R670: instruções locais e tickets de conectores científicos hospedados."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from typing import Any


PLUGINS = {
    "genomic-intelligence": ("Genomic Intelligence", "openai-curated-remote/app-6a73c480231c819181d7440a0e1499c9", "1.1.0"),
    "wolfram": ("Wolfram", "openai-curated-remote/app-69fe0bf66c8481919c513d799406436e", "3.0.0"),
    "boltz-api-cli": ("Boltz", "openai-curated-remote/boltz-api-cli", "0.1.1"),
    "ngs-analysis-workbench": ("NGS Analysis Workbench", "openai-curated-remote/ngs-analysis-workbench", "0.2.16"),
    "cowork-plugin-management": ("cowork-plugin-management", "claude-cowork/cowork-plugin-management", "0.2.2"),
    "data": ("data", "claude-cowork/data", "1.1.0"),
    "plugin-management": ("Plugin Management", "openai-curated-remote/plugin-management", "0.1.0"),
    "academixpertplus-kariri": ("AcademiXpertPlus KARIRI", "created-by-me-remote/gpt-d8a67608fa47bd06edd9d64b5f46fa6d", "0.5.1+bundle.4c816d33a9b41bebd57e17594e90d987"),
    "scigrant": ("SciGrant", "openai-curated-remote/app-6ab77d700b148191a79dc4d2df6babb6", "0.1.0"),
    "life-sciences-literature": ("Life Sciences Literature", "openai-curated-remote/life-sciences-literature", "0.1.5"),
    "plugin-creator": ("Plugin Creator", "openai-curated-remote/plugin-creator", "0.1.22"),
    "anthropic-skills": ("anthropic-skills", "claude-cowork/anthropic-skills", "1.0.0"),
}
# Ferramentas hospedadas são chamadas pelo host que já mantém a conexão OAuth.
# Nenhuma URL de transporte ou credencial é inferida do identificador de app.
HOST_OPERATIONS = {
    ("genomic-intelligence", "list_models"): ("mcp__codex_apps__genomic_intelligence_list_models", {"task"}),
    ("genomic-intelligence", "fetch_sequence"): ("mcp__codex_apps__genomic_intelligence_fetch_ensembl_sequence", {"gene", "species", "flank_bp"}),
    ("wolfram", "context"): ("mcp__codex_apps__wolfram_wolframcontext", {"context"}),
    ("wolfram", "evaluate"): ("mcp__codex_apps__wolfram_wolframlanguageevaluator", {"code", "timeConstraint"}),
    ("wolfram", "query"): ("mcp__codex_apps__wolfram_wolframalpha", {"input"}),
    ("ngs-analysis-workbench", "targets"): ("mcp__ngs_compute__list_compute_targets", set()),
    ("scigrant", "workflow"): ("mcp__codex_apps__scigrant_get_scigrant_workflow", set()),
    ("plugin-management", "search"): ("mcp__codex_apps__plugin_management_search_plugins", {"query", "limit"}),
    ("plugin-management", "dependencies"): ("mcp__codex_apps__plugin_management_get_plugin_dependencies", {"plugin_reference"}),
    ("plugin-creator", "metadata"): ("mcp__codex_apps__plugin_creator_get_plugin_metadata", {"plugin_id"}),
}
_ID = re.compile(r"[A-Za-z0-9_-]{1,100}\Z")
_SECRET = re.compile(r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret|authorization)", re.I)


def _slug(value: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("Identificador inválido")
    return value


def _json(value: Any, limit: int = 131072) -> bytes:
    def check(item: Any, depth: int = 0):
        if depth > 12:
            raise ValueError("Objeto excessivamente profundo")
        if isinstance(item, dict):
            if any(not isinstance(k, str) or _SECRET.search(k) for k in item):
                raise ValueError("Campo inválido ou segredo não permitido")
            for child in item.values():
                check(child, depth + 1)
        elif isinstance(item, (list, tuple)):
            for child in item:
                check(child, depth + 1)
    check(value)
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()
    except (ValueError, TypeError) as exc:
        raise ValueError("Objeto JSON finito obrigatório") from exc
    if len(raw) > limit:
        raise ValueError("Objeto excede limite de bytes")
    return raw


def validate_plugin_request(plugin_id, operation, arguments, intent=None):
    _slug(plugin_id)
    _slug(operation)
    if (plugin_id, operation) not in HOST_OPERATIONS:
        raise ValueError("Operação hospedada não registrada")
    if not isinstance(arguments, dict):
        raise ValueError("Argumentos devem ser objeto JSON")
    tool, fields = HOST_OPERATIONS[plugin_id, operation]
    if set(arguments) - fields:
        raise ValueError("Argumentos desconhecidos")
    _json(arguments)
    required = {"list_models": "task", "fetch_sequence": "gene", "evaluate": "code",
                "context": "context", "query": "input", "search": "query",
                "dependencies": "plugin_reference", "metadata": "plugin_id"}.get(operation)
    if required and (not isinstance(arguments.get(required), str) or not arguments[required].strip()):
        raise ValueError("Argumento obrigatório ausente ou inválido")
    if operation == "list_models" and arguments["task"] not in {"promoter", "splice", "enhancer", "chromatin", "expression", "annotation"}:
        raise ValueError("Tarefa genômica desconhecida")
    if plugin_id == "scigrant" and intent != "grant_writing":
        raise ValueError("SciGrant exige intenção explícita de redação de projeto")
    if intent is not None and intent != "grant_writing":
        raise ValueError("Intenção desconhecida")
    if "timeConstraint" in arguments and (type(arguments["timeConstraint"]) is not int or not 1 <= arguments["timeConstraint"] <= 60):
        raise ValueError("Tempo de avaliação inválido")
    if "flank_bp" in arguments and (type(arguments["flank_bp"]) is not int or not 0 <= arguments["flank_bp"] <= 100000):
        raise ValueError("Flanco genômico inválido")
    if "limit" in arguments and (type(arguments["limit"]) is not int or not 1 <= arguments["limit"] <= 50):
        raise ValueError("Limite de busca inválido")
    return tool


class ScientificPluginService:
    def __init__(self, repo_root: str | Path):
        self.root = Path(repo_root).resolve()
        self.storage = self.root / ".opencode/scientific-plugins"

    def _path(self, *parts):
        path = self.storage.joinpath(*parts)
        if not path.resolve().is_relative_to(self.storage):
            raise ValueError("Caminho fora da raiz de plugins")
        return path

    @staticmethod
    def _write(path, value):
        raw = _json(value, 8 * 1024 * 1024)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp = tempfile.mkstemp(dir=path.parent, prefix=".receipt-")
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if Path(temp).exists():
                Path(temp).unlink()

    @staticmethod
    def _load(path):
        with path.open("rb") as stream:
            raw = stream.read(8 * 1024 * 1024 + 1)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError("Registro excedeu limite")
        return json.loads(raw)

    def _registry(self):
        path = self._path("registry.json")
        return self._load(path) if path.exists() else {}

    def status(self):
        registry = self._registry()
        plugins = []
        for key, (name, source, version) in PLUGINS.items():
            entry = registry.get(key, {})
            plugins.append({"id": key, "name": name, "version": version,
                            "source_cache": source, "instructions_installed": bool(entry),
                            "skills": entry.get("skills", []),
                            "host_operations": [op for (pid, op) in HOST_OPERATIONS if pid == key],
                            "local_connector_execution": False,
                            "connector_scope": "authenticated_host" if any(pid == key for pid, _ in HOST_OPERATIONS) else "local_instructions_or_cli"})
        return {"status": "catalogued", "plugins": plugins, "executed": False,
                "external_validation": False}

    @staticmethod
    def _snapshot(package):
        files = {}
        total = 0
        for path in sorted(package.rglob("*")):
            if path.is_symlink():
                raise ValueError("Links não são importados")
            if path.is_file():
                if not path.resolve().is_relative_to(package.resolve()):
                    raise ValueError("Arquivo fora da origem")
                total += path.stat().st_size
                if total > 128 * 1024 * 1024 or len(files) >= 2000:
                    raise ValueError("Pacote excede limites de importação")
                files[str(path.relative_to(package))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return files

    def sync(self, *, cache_root: str | Path, plugin_ids=None):
        ids = list(PLUGINS) if plugin_ids is None else plugin_ids
        if not isinstance(ids, list) or not 1 <= len(ids) <= 12 or len(set(ids)) != len(ids):
            raise ValueError("Seleção de plugins inválida")
        if any(pid not in PLUGINS for pid in ids):
            raise ValueError("Plugin não solicitado")
        cache = Path(cache_root).resolve()
        prepared = []
        for pid in ids:
            name, relative, version = PLUGINS[pid]
            package = cache / relative / version
            if not package.resolve().is_relative_to(cache) or not package.is_dir():
                raise ValueError("Pacote instalado ausente ou fora do cache: " + pid)
            files = self._snapshot(package)
            prepared.append((pid, name, version, package, files))
        registry = self._registry()
        result = []
        for pid, name, version, source, files in prepared:
            target = self._path("packages", pid, version)
            if target.exists():
                if self._snapshot(target) != files:
                    raise ValueError("Pacote existente diverge; preservado")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                stage = Path(tempfile.mkdtemp(dir=target.parent, prefix=".import-"))
                try:
                    shutil.copytree(source, stage, dirs_exist_ok=True, symlinks=False)
                    if self._snapshot(stage) != files:
                        raise ValueError("Origem mudou durante importação")
                    os.rename(stage, target)
                finally:
                    if stage.exists():
                        shutil.rmtree(stage)
            skills = sorted(p.parts[1] for p in map(Path, files)
                            if len(p.parts) == 3 and p.parts[0] == "skills" and p.parts[2] == "SKILL.md")
            entry = {"id": pid, "name": name, "version": version,
                     "source_root": str(source), "package_root": str(target),
                     "files": files, "skills": skills, "origin": "third_party_or_user"}
            registry[pid] = entry
            result.append(entry)
        self._write(self._path("registry.json"), registry)
        return {"status": "completed", "plugins": result, "executed": False,
                "credentials_copied": False}

    def skill(self, plugin_id, skill_name):
        _slug(plugin_id)
        _slug(skill_name)
        entry = self._registry().get(plugin_id)
        if not entry or skill_name not in entry["skills"]:
            raise ValueError("Skill do plugin não instalada")
        package = self._path("packages", plugin_id, PLUGINS[plugin_id][2])
        if self._snapshot(package) != entry["files"]:
            raise ValueError("Falha de integridade do pacote")
        path = package / "skills" / skill_name / "SKILL.md"
        from reversa_universal.skill_dispatch import ReversaSkillDispatcher
        from integrations.harness_federation.artifact import invocation_policy
        import yaml
        dispatcher = ReversaSkillDispatcher(self.root)
        decision = dispatcher.plan_path(path).to_dict()
        raw = path.read_bytes()
        frontmatter = yaml.safe_load(dispatcher._frontmatter(raw.decode("utf-8-sig"))) or {}
        policy_path = path.parent / "agents/openai.yaml"
        policy = (yaml.safe_load(policy_path.read_text()).get("policy", {})
                  if policy_path.exists() else {})
        merged, reasons = invocation_policy(frontmatter, policy)
        if reasons:
            raise ValueError("Política de invocação inválida")
        return {**decision, "plugin_id": plugin_id, "policy": merged,
                "skill_document": raw.decode("utf-8-sig"), "package_root": str(package),
                "source_file_sha256": hashlib.sha256(raw).hexdigest(),
                "executed": False, "status": "instruction_only"}

    def request(self, plugin_id, operation, arguments, *, intent=None):
        tool = validate_plugin_request(plugin_id, operation, arguments, intent)
        body = {"plugin_id": plugin_id, "operation": operation, "host_tool": tool,
                "arguments": json.loads(_json(arguments)), "intent": intent}
        request = {**body, "request_id": uuid.uuid4().hex,
                   "request_sha256": hashlib.sha256(_json(body)).hexdigest(),
                   "status": "awaiting_host", "executed": False,
                   "instruction": "O host autenticado chama host_tool com arguments e devolve um recibo vinculado. Não executar nomes como comandos shell."}
        self._write(self._path("requests", request["request_id"] + ".json"), request)
        return request

    def result(self, request_id):
        _slug(request_id)
        request = self._load(self._path("requests", request_id + ".json"))
        response = self._path("responses", request_id + ".json")
        return self._load(response) if response.exists() else request

    def accept_host_response(self, request_id, *, host_tool, request_sha256, result, reported_by):
        _slug(request_id)
        if not isinstance(reported_by, str) or not 1 <= len(reported_by) <= 200:
            raise ValueError("Identidade do host obrigatória")
        response_path = self._path("responses", request_id + ".json")
        if response_path.exists():
            raise ValueError("Recibo já registrado")
        request = self._load(self._path("requests", request_id + ".json"))
        body = {k: request[k] for k in ("plugin_id", "operation", "host_tool", "arguments", "intent")}
        expected = hashlib.sha256(_json(body)).hexdigest()
        if host_tool != request["host_tool"] or request_sha256 != request["request_sha256"] or expected != request_sha256:
            raise ValueError("Recibo não corresponde à requisição")
        if not isinstance(result, dict) or not result:
            raise ValueError("Resposta do conector ausente")
        raw = _json(result, 1024 * 1024)
        normalized = json.loads(raw)
        is_error = normalized.get("isError") is True
        nested = normalized.get("structuredContent", {})
        if isinstance(nested, dict) and nested.get("isError") is True:
            is_error = True
        receipt = {"request_id": request_id, "request_sha256": expected,
                   "plugin_id": request["plugin_id"], "host_tool": host_tool,
                   "status": "failed" if is_error else "completed",
                   "response_sha256": hashlib.sha256(raw).hexdigest(), "result": normalized,
                   "reported_by": reported_by, "source_authenticity": "host_reported",
                   "host_reported_execution": True, "local_connector_execution": False,
                   "external_validation": False}
        self._write(response_path, receipt)
        return receipt

    def run_local(self, plugin_id, operation, arguments=None):
        arguments = arguments or {}
        _json(arguments)
        if plugin_id == "boltz-api-cli" and operation in {"version", "auth_status"} and not arguments:
            executable = self.root / ".venv/bin/boltz-api"
            argv = [str(executable), "--version"] if operation == "version" else [str(executable), "auth", "status", "--format", "json"]
            stdin = None
        elif plugin_id == "life-sciences-literature" and operation == "pubmed_search":
            if set(arguments) != {"term"} or not isinstance(arguments["term"], str) or not 1 <= len(arguments["term"]) <= 500:
                raise ValueError("Pesquisa PubMed delimitada obrigatória")
            plan = self.skill(plugin_id, "ncbi-entrez-skill")
            executable = Path(plan["instruction_root"]) / "scripts/ncbi_entrez.py"
            argv = [sys.executable, "-B", str(executable)]
            stdin = json.dumps({"endpoint": "esearch", "params": {"db": "pubmed", "term": arguments["term"], "retmode": "json", "retmax": 5}, "max_items": 5, "timeout_sec": 20})
        else:
            raise ValueError("Operação local não registrada")
        if not executable.is_file():
            return {"status": "blocked", "reason": "Executável não instalado", "executed": False}
        run = subprocess.run(argv, input=stdin, capture_output=True, text=True, timeout=35,
                             env={**os.environ, "BOLTZ_API_NO_UPDATE_CHECK": "1", "PYTHONDONTWRITEBYTECODE": "1"})
        # O estado de auth nunca persiste payloads que possam conter credenciais.
        output = run.stdout[:100000] if operation != "auth_status" else "payload omitido"
        reported_ok = run.returncode == 0
        if operation == "pubmed_search":
            try:
                reported_ok = reported_ok and json.loads(run.stdout).get("ok") is True
            except ValueError:
                reported_ok = False
        return {"status": "completed" if reported_ok else "blocked", "plugin_id": plugin_id,
                "operation": operation, "executed": True, "inference_executed": False,
                "exit_code": run.returncode, "output": output,
                "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                "external_validation": False}
