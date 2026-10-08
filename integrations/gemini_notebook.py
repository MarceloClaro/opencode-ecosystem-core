"""R674: CLI, MCP e skill oficiais sob a entrada central do Core."""
from __future__ import annotations

import asyncio
from copy import deepcopy
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import jsonschema

from integrations.gemini_notebook_transport import GeminiNotebookTransport, sanitize_output

UPSTREAM = "https://github.com/MarceloClaro/gemini-notebook-mcp-cli"
SECRET = re.compile(r"cookies?|authorization|password|secret|(?:access|refresh|auth|csrf)[_-]?token|api[_-]?key|session[_-]?id", re.I)


def _no_secrets(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise ValueError("Configuração excede profundidade permitida")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or SECRET.search(key):
                raise ValueError("Credenciais devem permanecer no fluxo privado upstream")
            _no_secrets(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _no_secrets(item, depth + 1)
    elif isinstance(value, str) and ("\x00" in value or re.search(
            r"(?i)(?:bearer\s|cookie\s*:|password=|token=)|\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b|\bAIza[A-Za-z0-9_-]{20,}\b", value)):
        raise ValueError("Argumento contém credencial ou caractere inválido")


def validate_notebook_config(config: Any) -> dict[str, Any]:
    """Validação pura, executada antes de construir orquestrador/processos."""
    if not isinstance(config, dict):
        raise ValueError("Configuração deve ser objeto JSON")
    try:
        raw = json.dumps(config, ensure_ascii=False, allow_nan=False).encode()
    except (ValueError, TypeError, RecursionError) as exc:
        raise ValueError("Configuração JSON inválida") from exc
    if len(raw) > 131072:
        raise ValueError("Configuração excede 128 KiB")
    _no_secrets(config)
    fields = {"status": set(), "catalog": {"timeout_seconds"}, "skill": set(),
              "mcp": {"tool", "arguments", "confirm", "dry_run", "timeout_seconds"},
              "cli": {"argv", "confirm", "dry_run", "timeout_seconds"}}
    operation = config.get("operation")
    if operation not in fields or set(config) - fields[operation] - {"operation"}:
        raise ValueError("Operação/campos Notebook desconhecidos")
    for flag in ("confirm", "dry_run"):
        if flag in config and type(config[flag]) is not bool:
            raise ValueError("Confirmação e preflight devem ser booleanos")
    timeout = config.get("timeout_seconds", 60)
    if type(timeout) not in {int, float} or not math.isfinite(timeout) or not 1 <= timeout <= 300:
        raise ValueError("Timeout deve estar entre 1 e 300 segundos")
    if operation == "mcp":
        if not isinstance(config.get("tool"), str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,127}", config["tool"]):
            raise ValueError("Ferramenta inválida")
        if not isinstance(config.get("arguments", {}), dict):
            raise ValueError("Argumentos devem ser objeto JSON")
    if operation == "cli":
        argv = config.get("argv")
        if not isinstance(argv, list) or not 1 <= len(argv) <= 128 or argv[0] != "nlm" or any(
                not isinstance(item, str) or not item or len(item) > 8192 for item in argv):
            raise ValueError("CLI exige vetor iniciado por nlm")
        if any(SECRET.search(item.lstrip("-")) for item in argv if item.startswith("-")):
            raise ValueError("Autenticação privada não aceita argumentos pelo Core")
    return json.loads(raw)


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


class GeminiNotebookService:
    def __init__(self, root: str | Path, *, transport: Any = None):
        self.root = Path(root).resolve()
        self.output_root = self.root / "outputs/gemini-notebook"
        self.transport = transport or GeminiNotebookTransport(
            self.root, env_overrides={"NOTEBOOKLM_DOWNLOAD_DIR": str(self.output_root)}, persistent=True)

    def _cli_catalog(self) -> list[dict[str, Any]]:
        # Inventário sem callbacks, isolado dos imports do orquestrador.
        run = subprocess.run([sys.executable, "-B", "-m", "integrations.gemini_notebook_catalog"],
                             cwd=self.root, stdin=subprocess.DEVNULL, capture_output=True,
                             timeout=30, check=False)
        if run.returncode or len(run.stdout) > 1048576:
            raise RuntimeError("Inventário CLI indisponível")
        data = json.loads(run.stdout)
        if not isinstance(data, list):
            raise RuntimeError("Inventário CLI inválido")
        return data

    def status(self) -> dict[str, Any]:
        try:
            version = importlib.metadata.version("notebooklm-mcp-cli")
        except importlib.metadata.PackageNotFoundError:
            version = None
        paths = {name: self.transport.resolve_binary(name) for name in ("nlm", "notebooklm-mcp")}
        return {"status": "completed", "package_version": version, "upstream": UPSTREAM,
                "binaries": {name: {"available": path is not None, "path": str(path) if path else None}
                             for name, path in paths.items()},
                "authentication": "not_checked", "process_executed": False,
                "mcp_profile": "upstream_active_profile", "externally_validated": False}

    def _save_catalog(self, discovery: dict[str, Any], cli: list[dict[str, Any]]) -> dict[str, Any]:
        document = {"upstream": UPSTREAM, "package_version": self.status()["package_version"],
                    "mcp": discovery, "cli": cli}
        digest = _hash(document)
        path = self.root / ".opencode/gemini-notebook/catalog.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
        path.with_suffix(".sha256").write_text(digest + "\n", encoding="utf-8")
        return {"status": "completed" if discovery.get("status") == "completed" else "partial",
                "mcp": discovery, "cli": cli, "mcp_tool_count": len(discovery.get("tools", [])),
                "cli_entry_count": len(cli), "catalog_path": str(path), "catalog_sha256": digest,
                "process_executed": discovery.get("process_executed", False)}

    def skill(self) -> dict[str, Any]:
        from reversa_universal.skill_dispatch import ReversaSkillDispatcher
        location = importlib.util.find_spec("notebooklm_tools")
        if location is None or not location.submodule_search_locations:
            return {"status": "blocked", "reason": "package_not_installed", "process_executed": False}
        source = Path(next(iter(location.submodule_search_locations))).resolve() / "data"
        destination = self.root / ".opencode/skills/nlm-skill"
        files = [source / "SKILL.md", source / "AGENTS_SECTION.md",
                 *sorted((source / "references").glob("*.md"))]
        planned = []
        for path in files:
            if not path.is_file() or not path.resolve().is_relative_to(source.resolve()) or path.stat().st_size > 131072:
                raise ValueError("Fonte da skill inválida")
            target = destination / path.relative_to(source)
            data = path.read_bytes()
            if target.exists() and target.read_bytes() != data:
                raise ValueError("Skill local modificada; não será sobrescrita")
            planned.append((path, target, data))
        distribution = importlib.metadata.distribution("notebooklm-mcp-cli")
        license_entry = next((path for path in distribution.files or [] if path.name == "LICENSE"), None)
        if license_entry is None:
            return {"status": "blocked", "reason": "package_license_missing", "process_executed": False}
        license_source = Path(distribution.locate_file(license_entry))
        if license_source.is_symlink() or not license_source.is_file() or license_source.stat().st_size > 32768:
            raise ValueError("Licença pública do pacote inválida")
        license_data = license_source.read_bytes()
        if not license_data.startswith(b"MIT License") or b"Permission is hereby granted" not in license_data:
            raise ValueError("Licença pública MIT ausente")
        license_target = destination / "LICENSE"
        if license_target.exists() and license_target.read_bytes() != license_data:
            raise ValueError("Licença local modificada; não será sobrescrita")
        manifest = []
        for path, target, data in planned:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            manifest.append({"source": str(path), "target": str(target), "sha256": hashlib.sha256(data).hexdigest()})
        license_target.write_bytes(license_data)
        decision = ReversaSkillDispatcher(self.root).plan("nlm-skill").to_dict()
        return {"status": "prepared", "skill": decision, "files": manifest,
                "license": {"id": "MIT", "source": str(license_source), "target": str(license_target),
                            "sha256": hashlib.sha256(license_data).hexdigest()},
                "instruction_text": (destination / "SKILL.md").read_text(encoding="utf-8"),
                "skill_sha256": manifest[0]["sha256"], "process_executed": False,
                "execution_mode": "read_in_current_orchestrator_context"}

    def _download_path(self, raw: str, *, directory: bool = False) -> Path:
        if not isinstance(raw, str) or not raw or "\x00" in raw:
            raise ValueError("Caminho de download inválido")
        # A raiz lógica não pode ser remapeada por links para outra pasta.
        if self.output_root.resolve() != self.output_root or not self.output_root.resolve().is_relative_to(self.root):
            raise ValueError("Raiz de download contém link ou está fora do workspace")
        candidate = Path(raw).expanduser()
        candidate = self.output_root / candidate if not candidate.is_absolute() else candidate
        if candidate.exists() or candidate.is_symlink():
            raise ValueError("Download exige destino novo")
        target = candidate.resolve()
        if not target.is_relative_to(self.output_root) or target == self.output_root:
            raise ValueError("Download fora da raiz de saída")
        return target

    def _downloads(self, effect: str, arguments: dict[str, Any]) -> tuple[dict[str, Any], list[Path]]:
        arguments = deepcopy(arguments)
        if effect != "download":
            return arguments, []
        paths = []
        for key in ("output_path", "output_dir", "output_directory"):
            if key in arguments and arguments[key] is not None:
                target = self._download_path(arguments[key], directory=key != "output_path")
                arguments[key] = str(target)
                paths.append(target)
        if not paths:
            # download_all usa diretório; demais ferramentas exigem arquivo explícito.
            raise ValueError("Download exige caminho explícito em outputs/gemini-notebook")
        return arguments, paths

    def _verify_downloads(self, result: dict[str, Any], paths: list[Path], *, directories: bool = False) -> dict[str, Any]:
        artifacts = []
        invalid = False
        for path in paths:
            if (path.is_symlink() or (path.exists() and directories != path.is_dir())
                    or self.output_root.resolve() != self.output_root):
                invalid = True
                continue
            candidates = sorted(path.rglob("*")) if directories and path.is_dir() else [path]
            if len(candidates) > 2000:
                invalid = True
                continue
            for file in candidates:
                if file.is_symlink() or not file.resolve().is_relative_to(self.output_root):
                    invalid = True
                    continue
                if file.is_file() and file.stat().st_size:
                    size = file.stat().st_size
                    if size > 1_073_741_824:
                        invalid = True
                        continue
                    digest = hashlib.sha256()
                    read = 0
                    with file.open("rb") as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            read += len(chunk)
                            digest.update(chunk)
                    if read != size or file.stat().st_size != size:
                        invalid = True
                        continue
                    artifacts.append({"path": str(file), "bytes": size, "sha256": digest.hexdigest()})
        result["artifacts"] = artifacts
        if invalid:
            result.update(status="failed", business_success=False, reason="download_artifact_invalid")
        elif result.get("status") == "completed" and (not artifacts or any(not path.exists() for path in paths)):
            result.update(status="failed", business_success=False, reason="download_artifact_missing")
        return result

    def _cached_schema(self, tool: str) -> dict[str, Any] | None:
        path = self.root / ".opencode/gemini-notebook/catalog.json"
        try:
            if (not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(self.root)
                    or path.with_suffix(".sha256").is_symlink() or path.stat().st_size > 1_048_576):
                return None
            document = json.loads(path.read_text(encoding="utf-8"))
            expected = path.with_suffix(".sha256").read_text(encoding="utf-8").strip()
            if (expected != _hash(document) or document.get("upstream") != UPSTREAM
                    or document.get("package_version") != self.status()["package_version"]
                    or document.get("mcp", {}).get("status") != "completed"):
                return None
            row = next((item for item in document["mcp"]["tools"] if item["name"] == tool), None)
            return deepcopy(row["inputSchema"]) if row else None
        except (OSError, ValueError, KeyError, TypeError, RecursionError):
            return None

    @staticmethod
    def _validate_schema(arguments: dict[str, Any], schema: dict[str, Any]) -> None:
        from integrations.gemini_notebook_transport import _strict_schema
        schema = _strict_schema(schema)
        schema["additionalProperties"] = False
        def local_refs(value, depth=0):
            if depth > 32:
                raise ValueError("Schema MCP excede profundidade permitida")
            if isinstance(value, dict):
                for key in ("$ref", "$dynamicRef", "$recursiveRef"):
                    if key in value and (not isinstance(value[key], str) or not value[key].startswith("#")):
                        raise ValueError("Schema MCP contém referência externa")
                for child in value.values():
                    local_refs(child, depth + 1)
            elif isinstance(value, list):
                for child in value:
                    local_refs(child, depth + 1)
        local_refs(schema)
        try:
            jsonschema.validate(arguments, schema, format_checker=jsonschema.FormatChecker())
        except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            raise ValueError("Argumentos não correspondem ao schema MCP instalado") from exc

    @staticmethod
    def _normalize_result(result: dict[str, Any]) -> dict[str, Any]:
        """Preserva estados de negócio sem confundir a aceitação com conclusão."""
        raw = result.get("result")
        payload = raw
        if isinstance(raw, dict) and isinstance(raw.get("structuredContent"), dict):
            payload = raw["structuredContent"]
        elif isinstance(raw, dict) and isinstance(raw.get("content"), list):
            payload = {}
            for block in raw["content"]:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    try:
                        candidate = json.loads(block["text"])
                    except (ValueError, RecursionError):
                        continue
                    if isinstance(candidate, dict):
                        payload = candidate
                        break
        if not isinstance(payload, dict):
            return result
        transport_ok = result.get("transport_success") is True or result.get("exit_code") == 0
        if not transport_ok:
            return result
        state = re.sub(r"[^a-z]", "", str(payload.get("status", payload.get("state", ""))).lower())
        failed = payload.get("failed", 0)
        succeeded = payload.get("succeeded", payload.get("downloaded", 0))
        if type(failed) is int and failed > 0:
            result.update(status="partial" if type(succeeded) is int and succeeded > 0 else "failed",
                          business_success=False)
        elif state == "partial":
            result.update(status="partial", business_success=False)
        elif state in {"inprogress", "pending", "running", "processing", "generating", "queued", "accepted"}:
            result.update(status="pending", business_success=None)
        elif state in {"error", "failed", "failure", "expired", "blocked", "denied", "cancelled", "canceled"} or payload.get("success") is False or payload.get("ok") is False:
            result.update(status="failed", business_success=False)
        return result

    @staticmethod
    def _gate(effect: str, config: dict[str, Any]) -> dict[str, Any] | None:
        if effect == "auth_private":
            return {"status": "blocked", "reason": "use_private_upstream_login", "process_executed": False}
        if config.get("dry_run"):
            return {"status": "prepared", "effect": effect, "process_executed": False, "remote_operation_executed": False}
        if effect != "read" and config.get("confirm") is not True:
            return {"status": "blocked", "reason": "explicit_operation_confirmation_required",
                    "effect": effect, "process_executed": False}
        return None

    async def _mcp(self, config: dict[str, Any]) -> dict[str, Any]:
        from integrations.gemini_notebook_catalog import classify_mcp_operation
        from integrations.gemini_notebook_pipeline import pipeline_preflight
        tool = config["tool"]
        arguments = config.get("arguments", {})
        if tool == "pipeline" and ({"steps", "_pipeline_steps"} & set(arguments)):
            raise ValueError("Passos declarados pelo chamador não comprovam a definição upstream")
        effect = classify_mcp_operation(tool, arguments)
        pipeline = None
        if tool == "pipeline" and arguments.get("action") == "run":
            pipeline = pipeline_preflight(arguments.get("pipeline_name"), arguments.get("notebook_id"), arguments.get("input_url", ""))
            effect = pipeline.get("effect", "destructive")
            if pipeline["status"] != "prepared":
                return {"status": "blocked", "effect": effect, "reason": pipeline.get("reason"),
                        "pipeline": pipeline, "process_executed": False, "remote_operation_executed": False}
        if effect != "read" and config.get("confirm") is True and arguments.get("confirm") is False:
            raise ValueError("Confirmação upstream contradiz a autorização da operação")
        # Private credentials and denied effects are rejected before starting a server.
        if effect == "auth_private" or (effect != "read" and not config.get("confirm") and not config.get("dry_run")):
            return {**self._gate(effect, config), **({"pipeline": pipeline} if pipeline else {})}
        arguments, paths = self._downloads(effect, arguments)
        if config.get("dry_run"):
            schema = self._cached_schema(tool)
            if schema is not None:
                self._validate_schema(arguments, schema)
            return {**self._gate(effect, config), "tool": tool,
                    **({"pipeline": pipeline} if pipeline else {}),
                    "schema_validated": schema is not None,
                    "validation_scope": "cached_schema" if schema is not None else "policy_only",
                    "schema_source": "hashed_version_matched_cache" if schema is not None else None,
                    "cache_freshness": "execution_rediscovers_installed_server"}
        discovery = await self.transport.discover_mcp(config.get("timeout_seconds", 60))
        if discovery.get("status") != "completed":
            return discovery
        metadata = next((row for row in discovery["tools"] if row["name"] == tool), None)
        if metadata is None:
            return {"status": "blocked", "reason": "tool_not_enabled", "process_executed": False}
        if effect != "read" and config.get("confirm") is True and "confirm" in metadata["inputSchema"].get("properties", {}):
            arguments["confirm"] = True
        self._validate_schema(arguments, metadata["inputSchema"])
        blocked = self._gate(effect, config)
        if blocked:
            return blocked
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
        if pipeline is not None:
            current = pipeline_preflight(arguments.get("pipeline_name"), arguments.get("notebook_id"), arguments.get("input_url", ""))
            if current["status"] != "prepared" or any(current.get(key) != pipeline.get(key)
                    for key in ("definition_sha256", "effective_steps_sha256", "definition_source")):
                return {"status": "blocked", "reason": "pipeline_definition_changed", "effect": effect,
                        "pipeline": pipeline, "process_executed": False, "remote_operation_executed": False}
        result = await self.transport.call_mcp(tool, arguments, config.get("timeout_seconds", 60))
        result = self._normalize_result({**result, "effect": effect, "tool": tool})
        if pipeline is not None:
            result["pipeline"] = pipeline
        return self._verify_downloads(result, paths, directories=tool == "download_all_artifacts") if paths else result

    async def _cli(self, config: dict[str, Any]) -> dict[str, Any]:
        from integrations.gemini_notebook_catalog import classify_cli_argv
        from integrations.gemini_notebook_pipeline import pipeline_preflight
        catalog = self._cli_catalog()
        argv = list(config["argv"])
        operation = classify_cli_argv(argv[1:], catalog)
        if operation.get("interactive"):
            return {"status": "blocked", "reason": "interactive_cli_not_supported", "process_executed": False}
        effect = operation["effect"]
        pipeline = None
        if operation["command_path"] == ["pipeline", "run"]:
            params = operation["parameters"]
            pipeline = pipeline_preflight(params.get("pipeline_name"), params.get("notebook_id"), params.get("input_url", ""))
            effect = pipeline.get("effect", "destructive")
            if pipeline["status"] != "prepared":
                return {"status": "blocked", "effect": effect, "reason": pipeline.get("reason"),
                        "pipeline": pipeline, "process_executed": False, "remote_operation_executed": False}
        row = next(item for item in catalog if item["path"] == operation["command_path"])
        confirmation = next((item for item in row["params"] if item["name"] == "confirm"), None)
        if effect != "read" and config.get("confirm") is True and confirmation is not None:
            negative = set(confirmation.get("secondary_opts", []))
            if any(item.split("=", 1)[0] in negative for item in argv):
                raise ValueError("Flag upstream contradiz a autorização da operação")
            if operation["parameters"].get("confirm") is not True:
                argv.append(next((flag for flag in confirmation["opts"] if flag.startswith("--")), confirmation["opts"][0]))
        paths = []
        if effect == "download":
            outputs = {flag: param["name"] for param in row["params"]
                       if param["name"] in {"output", "output_dir", "output_path", "output_directory"}
                       for flag in param.get("opts", [])}
            for index, item in enumerate(argv):
                if item in outputs and index + 1 < len(argv):
                    target = self._download_path(argv[index + 1])
                    argv[index + 1] = str(target)
                    paths.append(target)
                elif "=" in item and item.split("=", 1)[0] in outputs:
                    flag, value = item.split("=", 1)
                    target = self._download_path(value)
                    argv[index] = flag + "=" + str(target)
                    paths.append(target)
            if not paths:
                raise ValueError("Download CLI exige destino explícito")
        blocked = self._gate(effect, config)
        if blocked:
            return {**blocked, "command_path": operation["command_path"],
                    **({"pipeline": pipeline} if pipeline else {})}
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
        if pipeline is not None:
            current = pipeline_preflight(params.get("pipeline_name"), params.get("notebook_id"), params.get("input_url", ""))
            if current["status"] != "prepared" or any(current.get(key) != pipeline.get(key)
                    for key in ("definition_sha256", "effective_steps_sha256", "definition_source")):
                return {"status": "blocked", "reason": "pipeline_definition_changed", "effect": effect,
                        "pipeline": pipeline, "process_executed": False, "remote_operation_executed": False}
        result = await self.transport.run_cli(argv, config.get("timeout_seconds", 60))
        result = self._normalize_result({**result, "effect": effect, "command_path": operation["command_path"]})
        if pipeline is not None:
            result["pipeline"] = pipeline
        command = operation["command_path"]
        changed = ((command and command[0] == "config" and command[-1] in {"set", "reset"})
                   or command[:2] == ["login", "switch"]
                   or command[:2] == ["login", "profile"] and command[-1] in {"create", "rename", "delete"})
        if changed and result.get("status") in {"completed", "partial"} and hasattr(self.transport, "close_persistent"):
            reset = await self.transport.close_persistent()
            result["session_reset"] = isinstance(reset, dict) and reset.get("status") == "completed"
            result["volatile_jobs_may_be_discarded"] = True
        return self._verify_downloads(result, paths, directories=operation["command_path"] == ["download", "all"]) if paths else result

    def run(self, **request: Any) -> dict[str, Any]:
        config = validate_notebook_config(request)
        operation = config["operation"]
        if operation == "status":
            return self.status()
        if operation == "skill":
            return self.skill()
        if operation == "catalog":
            discovery = asyncio.run(self.transport.discover_mcp(config.get("timeout_seconds", 60)))
            return self._save_catalog(discovery, self._cli_catalog())
        result = asyncio.run(self._mcp(config) if operation == "mcp" else self._cli(config))
        return sanitize_output(result)
