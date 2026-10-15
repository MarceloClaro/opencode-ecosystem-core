"""R670/R895: registro canônico de instruções locais e tickets hospedados.

Importar instruções não executa hooks, tarefas de domínio ou conectores.
Autenticação pertence ao host e não é transferida ao Core pela importação.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import Any

PLUGINS = {
    "genomic-intelligence": ("Genomic Intelligence", "openai-curated-remote/app-6a73c480231c819181d7440a0e1499c9", "1.1.0"),
    "wolfram": ("Wolfram", "openai-curated-remote/app-69fe0bf66c8481919c513d799406436e", "3.0.0"),
    "boltz-api-cli": ("Boltz", "openai-curated-remote/boltz-api-cli", "0.1.1"),
    "ngs-analysis-workbench": ("NGS Analysis Workbench", "openai-curated-remote/ngs-analysis-workbench", "0.2.18"),
    "cowork-plugin-management": ("cowork-plugin-management", "claude-cowork/cowork-plugin-management", "0.2.2"),
    "data": ("data", "claude-cowork/data", "1.1.0"),
    "plugin-management": ("Plugin Management", "openai-curated-remote/plugin-management", "0.1.0"),
    "academixpertplus-kariri": ("AcademiXpertPlus KARIRI", "created-by-me-remote/gpt-d8a67608fa47bd06edd9d64b5f46fa6d", "0.5.1+bundle.4c816d33a9b41bebd57e17594e90d987"),
    "scigrant": ("SciGrant", "openai-curated-remote/app-6ab77d700b148191a79dc4d2df6babb6", "0.1.0"),
    "life-sciences-literature": ("Life Sciences Literature", "openai-curated-remote/life-sciences-literature", "0.1.5"),
    "plugin-creator": ("Plugin Creator", "openai-curated-remote/plugin-creator", "0.1.27"),
    "anthropic-skills": ("anthropic-skills", "claude-cowork/anthropic-skills", "1.0.0"),
    "superpowers": ("Superpowers", "openai-curated-remote/superpowers", "6.4.2"),
    "bio-research": ("Bio Research", "claude-cowork/bio-research", "1.2.0"),
    "design": ("Design", "claude-cowork/design", "1.2.0"),
    "visualize": ("Visualize", "openai-bundled/visualize", "1.0.49"),
    "human-resources": ("Human Resources", "claude-cowork/human-resources", "1.3.0"),
    "work-pets": ("Work Pets", "openai-curated-remote/work-pets", "0.1.6"),
    "enterprise-search": ("Enterprise Search", "claude-cowork/enterprise-search", "1.3.0"),
    "legal": ("Legal", "claude-cowork/legal", "1.3.0"),
    "productivity": ("Productivity", "claude-cowork/productivity", "1.3.1"),
    "dr-alex-ramos": ("Dr. Alex Ramos", "created-by-me-remote/gpt-e7255c6825a9703dd051c73056c06459", "1.6.0"),
    "contas-escolares-airam-veras": ("Contas Escolares Airam Veras", "created-by-me-remote/contas-escolares-airam-veras", "1.1.0"),
    "medico-virtual-supremo": ("Médico Virtual Supremo", "created-by-me-remote/gpt-6ceee9ff15bc7f1a4007d43b810f1876", "0.4.0"),
    "sites": ("Sites", "openai-curated-remote/sites", "1.0.2-remix-a.1"),
}
# Seleção solicitada, não outro registro: os cinco perfis legados adicionais
# continuam no mesmo PLUGINS e na mesma registry.json.
REQUESTED_PLUGIN_IDS = (
    "superpowers", "scigrant", "wolfram", "anthropic-skills",
    "cowork-plugin-management", "bio-research", "plugin-creator", "data", "design",
    "visualize", "human-resources", "work-pets", "enterprise-search",
    "life-sciences-literature", "legal", "productivity", "dr-alex-ramos",
    "contas-escolares-airam-veras", "medico-virtual-supremo", "sites",
)
# Ferramentas hospedadas são chamadas pelo host que já mantém a conexão OAuth.
# Nenhuma URL de transporte ou credencial é inferida do identificador de app.
HOST_OPERATIONS = {
    ("genomic-intelligence", "list_models"): ("mcp__codex_apps__genomic_intelligence_list_models", {"task"}),
    ("genomic-intelligence", "fetch_sequence"): ("mcp__codex_apps__genomic_intelligence_fetch_ensembl_sequence", {"gene", "species", "flank_bp"}),
    ("wolfram", "context"): ("mcp__codex_apps__wolfram_wolframcontext", {"context"}),
    ("wolfram", "evaluate"): ("mcp__codex_apps__wolfram_wolframlanguageevaluator", {"code", "timeConstraint"}),
    ("wolfram", "query"): ("mcp__codex_apps__wolfram_wolframalpha", {"query"}),
    ("ngs-analysis-workbench", "targets"): ("mcp__ngs_compute__list_compute_targets", set()),
    ("scigrant", "workflow"): ("mcp__codex_apps__scigrant_get_scigrant_workflow", set()),
    ("plugin-management", "search"): ("mcp__codex_apps__plugin_management_search_plugins", {"query", "limit"}),
    ("plugin-management", "dependencies"): ("mcp__codex_apps__plugin_management_get_plugin_dependencies", {"plugin_reference"}),
    ("plugin-creator", "metadata"): ("mcp__codex_apps__plugin_creator_get_plugin_metadata", {"plugin_id"}),
    ("work-pets", "list"): ("mcp__codex_apps__pets_list_pets", {"cursor", "limit"}),
    ("sites", "list"): ("mcp__codex_apps__sites_list_sites", {"cursor", "limit", "include_editable", "role"}),
}
_ID = re.compile(r"[A-Za-z0-9_-]{1,100}\Z")
_SECRET = re.compile(r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret|authorization)", re.IGNORECASE)
_CREDENTIAL_NAMES = frozenset({".env", "credentials.json", "credentials", "auth.json",
                              "token.json", "tokens.json", "id_rsa", "id_ed25519"})


def _host_arguments(plugin_id, operation, arguments):
    """Compatibilidade R670 para Wolfram; tickets novos usam o schema oficial."""
    if (plugin_id == "wolfram" and operation == "query" and isinstance(arguments, dict)
            and set(arguments) == {"input"}):
        return {"query": arguments["input"]}
    return arguments


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


def _manifest_json(registry: Any) -> bytes:
    """Serializa somente metadados canônicos; nomes de arquivos não são campos de payload.

    A exceção ao filtro de nomes de segredo limita-se ao mapa relativo path→SHA256.
    Argumentos, respostas e demais metadados continuam passando por _json.
    """
    fields = {"id", "name", "version", "source_root", "package_root", "files", "skills", "origin"}
    if not isinstance(registry, dict) or len(registry) > len(PLUGINS):
        raise ValueError("Manifesto de plugins inválido")
    metadata = {}
    maps = {}
    for pid, entry in registry.items():
        if (not isinstance(pid, str) or pid not in PLUGINS or not isinstance(entry, dict)
                or set(entry) != fields or entry.get("id") != pid
                or entry.get("name") != PLUGINS[pid][0]
                or entry.get("origin") != "third_party_or_user"):
            raise ValueError("Manifesto de plugin inválido")
        if any(not isinstance(entry.get(key), str) or not 1 <= len(entry[key]) <= 4096
               for key in ("version", "source_root", "package_root")):
            raise ValueError("Metadados de manifesto inválidos")
        skills = entry["skills"]
        if (not isinstance(skills, list) or len(skills) > 2000
                or any(not isinstance(skill, str) or not _ID.fullmatch(skill) for skill in skills)
                or len(set(skills)) != len(skills)):
            raise ValueError("Skills de manifesto inválidas")
        files = entry["files"]
        if not isinstance(files, dict) or not 1 <= len(files) <= 2000:
            raise ValueError("Arquivos de manifesto inválidos")
        for relative, digest in files.items():
            if (not isinstance(relative, str) or not 1 <= len(relative) <= 4096
                    or "\\" in relative or ":" in relative
                    or any(ord(char) < 32 for char in relative)):
                raise ValueError("Caminho de manifesto inválido")
            path = PurePosixPath(relative)
            if (path.is_absolute() or relative != path.as_posix()
                    or any(part in {".", ".."} for part in path.parts)):
                raise ValueError("Caminho de manifesto inválido")
            for part in path.parts:
                lowered = part.lower()
                if (lowered in _CREDENTIAL_NAMES or lowered in {".ssh", ".git"}
                        or (lowered.startswith(".env.") and lowered not in {
                            ".env.example", ".env.sample", ".env.template"})):
                    raise ValueError("Caminho sensível de credenciais no manifesto")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("SHA256 de arquivo inválido no manifesto")
        metadata[pid] = {key: value for key, value in entry.items() if key != "files"}
        maps[pid] = files
    normalized = json.loads(_json(metadata, 8 * 1024 * 1024))
    for pid, files in maps.items():
        normalized[pid]["files"] = files
    raw = json.dumps(normalized, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError("Manifesto excede limite de bytes")
    return raw


def validate_plugin_request(plugin_id, operation, arguments, intent=None):
    _slug(plugin_id)
    _slug(operation)
    if (plugin_id, operation) not in HOST_OPERATIONS:
        raise ValueError("Operação hospedada não registrada")
    arguments = _host_arguments(plugin_id, operation, arguments)
    if not isinstance(arguments, dict):
        raise ValueError("Argumentos devem ser objeto JSON")
    tool, fields = HOST_OPERATIONS[plugin_id, operation]
    if set(arguments) - fields:
        raise ValueError("Argumentos desconhecidos")
    _json(arguments)
    required = {"list_models": "task", "fetch_sequence": "gene", "evaluate": "code",
                "context": "context", "query": "query", "search": "query",
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
    if plugin_id == "work-pets" and arguments.get("limit", 20) > 20:
        raise ValueError("Limite de pets deve estar entre 1 e 20")
    if "cursor" in arguments and arguments["cursor"] is not None and (
            not isinstance(arguments["cursor"], str) or not 1 <= len(arguments["cursor"]) <= 2000):
        raise ValueError("Cursor inválido")
    if "include_editable" in arguments and type(arguments["include_editable"]) is not bool:
        raise ValueError("include_editable deve ser booleano")
    if "role" in arguments and arguments["role"] not in (None, "owner", "editor"):
        raise ValueError("Papel de site inválido")
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
    def _write(path, value, *, manifest=False):
        raw = _manifest_json(value) if manifest else _json(value, 8 * 1024 * 1024)
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
        registry = self._load(path) if path.exists() else {}
        if not isinstance(registry, dict):
            raise ValueError("Registro de plugins inválido")
        return registry

    def _instruction_state(self, plugin_id, entry):
        if not isinstance(entry, dict) or not entry:
            return "not_installed", False
        version = PLUGINS[plugin_id][2]
        if entry.get("version") != version:
            return "version_mismatch", False
        try:
            package = self._path("packages", plugin_id, version)
            valid = bool(entry.get("files")) and self._snapshot(package) == entry["files"]
        except (OSError, ValueError, TypeError):
            valid = False
        return ("ready", True) if valid else ("integrity_failed", False)

    def status(self):
        registry = self._registry()
        plugins = []
        for key, (name, source, version) in PLUGINS.items():
            entry = registry.get(key, {})
            instruction_status, integrity = self._instruction_state(key, entry)
            operations = [op for (pid, op) in HOST_OPERATIONS if pid == key]
            kinds = ["local_instructions"]
            if operations:
                kinds.append("host_connector")
            if key in {"boltz-api-cli", "life-sciences-literature"}:
                kinds.append("allowlisted_local_cli")
            plugins.append({"id": key, "name": name, "version": version,
                            "source_cache": source, "instructions_installed": integrity,
                            "instruction_status": instruction_status, "hash_integrity": integrity,
                            "skills": entry.get("skills", []) if integrity else [],
                            "capability_kinds": kinds, "host_operations": operations,
                            "host_authentication": "not_verified" if operations else "not_applicable",
                            "local_connector_execution": False,
                            "connector_scope": "authenticated_host" if operations else "local_instructions_or_cli"})
        return {"status": "catalogued", "plugins": plugins, "executed": False,
                "external_validation": False}

    @staticmethod
    def _snapshot(package):
        files = {}
        total = 0
        for path in sorted(package.rglob("*")):
            if path.is_symlink():
                raise ValueError("Links não são importados")
            relative_parts = path.relative_to(package).parts
            if path.name.lower() in _CREDENTIAL_NAMES or any(part in {".ssh", ".git"} for part in relative_parts):
                raise ValueError("Arquivo sensível de credenciais não é importado")
            if path.name.lower().startswith(".env.") and path.name.lower() not in {
                    ".env.example", ".env.sample", ".env.template"}:
                raise ValueError("Arquivo sensível de credenciais não é importado")
            if path.is_file():
                if not path.resolve().is_relative_to(package.resolve()):
                    raise ValueError("Arquivo fora da origem")
                total += path.stat().st_size
                if total > 128 * 1024 * 1024 or len(files) >= 2000:
                    raise ValueError("Pacote excede limites de importação")
                files[path.relative_to(package).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        return files

    def sync(self, *, cache_root: str | Path, plugin_ids=None):
        ids = list(PLUGINS) if plugin_ids is None else plugin_ids
        if (not isinstance(ids, list) or not 1 <= len(ids) <= len(PLUGINS)
                or any(not isinstance(pid, str) for pid in ids) or len(set(ids)) != len(ids)):
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
        self._write(self._path("registry.json"), registry, manifest=True)
        return {"status": "completed", "plugins": result, "executed": False,
                "credentials_copied": False}

    def skill(self, plugin_id, skill_name):
        _slug(plugin_id)
        _slug(skill_name)
        if plugin_id not in PLUGINS:
            raise ValueError("Plugin não registrado")
        entry = self._registry().get(plugin_id)
        if not entry or skill_name not in entry["skills"]:
            raise ValueError("Skill do plugin não instalada")
        if entry.get("version") != PLUGINS[plugin_id][2]:
            raise ValueError("Versão instalada divergente; sincronize o plugin")
        package = self._path("packages", plugin_id, PLUGINS[plugin_id][2])
        if self._snapshot(package) != entry["files"]:
            raise ValueError("Falha de integridade do pacote")
        path = package / "skills" / skill_name / "SKILL.md"
        import yaml

        from integrations.harness_federation.artifact import invocation_policy
        from reversa_universal.skill_dispatch import ReversaSkillDispatcher
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
        arguments = _host_arguments(plugin_id, operation, arguments)
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
        # Estado de habilitação é autoritativo, mesmo com transporte MCP válido.
        unavailable = {"failed", "error", "unavailable", "not_entitled", "expired", "suspended",
                       "not_started", "temporarily_unavailable", "authentication_required", "blocked"}
        if normalized.get("status") in unavailable or (isinstance(nested, dict) and nested.get("status") in unavailable):
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
