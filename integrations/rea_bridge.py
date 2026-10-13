"""SPEC-935-R808 / SPEC-935-R841: ponte local MCP de operações estáticas REA.

O inventário não abre alvos. A conclusão operacional conserva a Evidence do
servidor e não equivale a validação externa, autenticação ou inferência de LLM.
A operação ``layers`` mapeia a prontidão das camadas de provedor; a operação
``layer`` despacha a inspeção estática por caminho de uma camada instalada.
"""

from __future__ import annotations

import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import contextvars
from datetime import timedelta
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

from integrations.rea_layers import (
    ENCODINGS,
    LAYER_IDS,
    engine_environment,
    layer_inspection,
    layers_status,
    probe_layer,
)


class ReaBridge:
    """Executa um handshake e uma operação estática em processo MCP isolado."""

    REPOSITORY = "https://github.com/MarceloClaro/rea"
    OPERATIONS = frozenset({"status", "catalog", "session", "layers", "layer",
                            "analyze", "analyze_binary"})
    MAX_TIMEOUT_SECONDS = 180
    MAX_BINARY_BYTES = 128 * 1024 * 1024

    @staticmethod
    def _child_environment(*, native_required: bool = False) -> dict[str, str]:
        """Configuração local explícita; overrides inválidos nunca usam fallback."""
        environment = dict(os.environ)
        if environment.get("CORE_REA_LOCAL_ONLY") == "1":
            from integrations.rea_assistant import worker_environment
            environment = worker_environment(environment, root=environment["CORE_REA_WORKSPACE"])
        root = Path.home() / ".local/share/opencode-core/native-rea"
        defaults = {"GHIDRA_INSTALL_DIR": root / "ghidra_12.1.4_PUBLIC",
                    "JAVA_HOME": root / "jdk-21.0.12.1+1"}
        for key, default in defaults.items():
            if key not in environment and default.is_dir():
                environment[key] = str(default)
        for key, value in engine_environment().items():
            environment.setdefault(key, value)
        if native_required:
            for key, files in (("GHIDRA_INSTALL_DIR", ("support/analyzeHeadless",)),
                               ("JAVA_HOME", ("bin/java", "bin/javac"))):
                value = environment.get(key, "")
                path = Path(value).expanduser()
                if not value or not path.is_absolute() or any(
                    not (path / file).is_file() or not os.access(path / file, os.X_OK)
                    for file in files
                ):
                    raise ValueError(f"{key} deve apontar para instalação absoluta completa e executável.")
            environment["REA_ANALYSIS_PROVIDER"] = "ghidra"
        return environment

    def __init__(self, repo_root: str | Path | None = None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()

    @staticmethod
    def _resolve_node() -> str | None:
        override = os.environ.get("REA_NODE_BIN")
        candidates = [Path(override).expanduser()] if override else [
            Path(found) for found in (
                shutil.which("node"),
                str(Path.home() / ".local" / "bin" / "node"),
                str(Path.home() / ".local" / "share" / "opencode-core" / "node" / "bin" / "node"),
            ) if found
        ]
        return next((str(path.resolve()) for path in candidates if path.is_file() and os.access(path, os.X_OK)), None)

    @staticmethod
    def _source_dir() -> Path:
        return Path(os.environ.get("REA_SOURCE_DIR") or Path.home() / ".local" / "share" / "opencode-core" / "rea").expanduser().resolve()

    @staticmethod
    def _source_commit(source: Path) -> str | None:
        git = shutil.which("git")
        if not git or not (source / ".git").exists():
            return None
        try:
            result = subprocess.run([git, "-C", str(source), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=2, shell=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        commit = result.stdout.strip()
        return commit if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40,64}", commit) else None

    def status(self, *, include_commit: bool = True) -> dict[str, Any]:
        """Descobre arquivos e dependências sem iniciar REA ou aplicações alvo."""
        source = self._source_dir()
        node = self._resolve_node()
        metadata: dict[str, Any] = {}
        try:
            value = json.loads((source / "package.json").read_text(encoding="utf-8"))
            if isinstance(value, dict):
                metadata = value
        except (OSError, ValueError):
            pass
        launcher = source / "scripts" / "rea.mjs"
        missing = []
        if metadata.get("name") != "rea-agents" or not isinstance(metadata.get("version"), str):
            missing.append("package.json REA válido")
        for file in (launcher, source / "dist" / "main.js"):
            if not file.is_file():
                missing.append(str(file))
        if not (source / "node_modules").is_dir():
            missing.append("dependências Node instaladas")
        if node is None:
            missing.append("executável Node")
        for dependency in ("mcp", "anyio"):
            if importlib.util.find_spec(dependency) is None:
                missing.append(f"dependência Python {dependency}")
        provenance = {
            "repository": self.REPOSITORY,
            "commit": self._source_commit(source) if include_commit else None,
            "version": metadata.get("version"),
            "runtime": {"source_dir": str(source), "node": node, "launcher": str(launcher)},
            "response_sha256": None,
        }
        available = not missing
        native_provider: dict[str, Any] = {"provider": "ghidra", "configuration_available": False,
                                          "verification": "installation_only"}
        try:
            environment = self._child_environment(native_required=True)
            native_provider.update(configuration_available=True,
                ghidra_install_dir=environment["GHIDRA_INSTALL_DIR"], java_home=environment["JAVA_HOME"])
            properties = Path(environment["GHIDRA_INSTALL_DIR"]) / "Ghidra/application.properties"
            if properties.is_file():
                values = dict(line.split("=", 1) for line in properties.read_text(encoding="utf-8").splitlines() if "=" in line)
                native_provider["declared_version"] = values.get("application.version")
        except (ValueError, OSError, UnicodeError) as exc:
            native_provider["reason"] = str(exc)
        return {
            "operation": "status", "status": "completed" if available else "unavailable",
            "success": available, "available": available,
            "installed": bool(metadata.get("name") == "rea-agents" and launcher.is_file()),
            "verification": "installation_only", "provenance": provenance,
            "native_provider": native_provider,
            "response": None, "error": None if available else "Runtime REA indisponível: " + ", ".join(missing),
            "reason": "Instalação detectada; handshake, providers e autenticação não são testados pelo inventário." if available else "Instale e compile REA ou ajuste REA_SOURCE_DIR e REA_NODE_BIN.",
        }

    def _local_path(self, path: Any, message: str) -> Path:
        if not isinstance(path, str) or not path.strip() or "\x00" in path:
            raise ValueError(message)
        target = Path(path).expanduser()
        if not target.is_absolute():
            target = self.repo_root / target
        target = target.resolve()
        if not target.exists() or not (target.is_file() or target.is_dir()):
            raise ValueError("O alvo REA deve ser arquivo ou diretório local existente.")
        return target

    def _validate(self, config: Any) -> dict[str, Any]:
        if not isinstance(config, dict):
            raise ValueError("A configuração REA deve ser um objeto.")
        if set(config) - {"operation", "path", "timeout_seconds", "procedure", "layer", "encoding"}:
            raise ValueError("Campos desconhecidos na configuração REA.")
        operation = config.get("operation")
        if not isinstance(operation, str) or operation not in self.OPERATIONS:
            raise ValueError("Operação REA inválida; use status, catalog, session, layers, "
                             "layer, analyze ou analyze_binary.")
        timeout = config.get("timeout_seconds", 60)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= self.MAX_TIMEOUT_SECONDS or not math.isfinite(timeout):
            raise ValueError("timeout_seconds deve ser um número finito maior que zero e até 180.")
        validated = {"operation": operation, "timeout_seconds": float(timeout)}
        if operation == "layers":
            if set(config) - {"operation", "timeout_seconds"}:
                raise ValueError("layers aceita apenas operation e timeout_seconds.")
            return validated
        if operation == "layer":
            if "procedure" in config:
                raise ValueError("procedure somente é permitido na análise binária.")
            layer_id = config.get("layer")
            if not isinstance(layer_id, str) or layer_id not in LAYER_IDS:
                raise ValueError("layer deve ser uma camada REA conhecida.")
            inspection = layer_inspection(layer_id)
            if not inspection:
                raise ValueError("A camada informada não oferece inspeção estática por caminho.")
            target = self._local_path(config.get("path"), "Inspeção de camada REA exige path local explícito.")
            validated.update(layer=layer_id, path=str(target), tool=inspection["tool"],
                             path_field=inspection["path_field"], fixed=dict(inspection["fixed"]))
            if inspection.get("encoding"):
                encoding = config.get("encoding", "raw")
                if not isinstance(encoding, str) or encoding not in ENCODINGS:
                    raise ValueError("encoding deve ser raw ou hex.")
                validated["encoding"] = encoding
            elif "encoding" in config:
                raise ValueError("encoding somente é permitido em camadas que o exigem.")
            return validated
        if operation in {"analyze", "analyze_binary"}:
            if "layer" in config or "encoding" in config:
                raise ValueError("layer e encoding somente são permitidos na operação layer.")
            target = self._local_path(config.get("path"), "Análise REA exige path local explícito.")
            validated["path"] = str(target)
            if operation == "analyze_binary":
                if not target.is_file() or target.stat().st_size > self.MAX_BINARY_BYTES:
                    raise ValueError("Análise binária exige arquivo local de até 128 MiB.")
                procedure = config.get("procedure", "main")
                if (not isinstance(procedure, str) or not procedure.strip() or len(procedure) > 256
                        or any(ord(character) < 32 for character in procedure)):
                    raise ValueError("procedure deve conter 1 a 256 caracteres sem controles.")
                validated["procedure"] = procedure
                with target.open("rb") as stream:
                    validated["target_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
            return validated
        if "path" in config:
            raise ValueError("path somente é permitido nas operações de análise.")
        if "layer" in config or "encoding" in config:
            raise ValueError("layer e encoding somente são permitidos na operação layer.")
        if "procedure" in config:
            raise ValueError("procedure somente é permitido na análise binária.")
        return validated

    @staticmethod
    def _dump(value: Any) -> dict[str, Any]:
        result = value.model_dump(mode="json", by_alias=True, exclude_none=True)
        if not isinstance(result, dict):
            raise ValueError("Resposta MCP inválida.")
        return result

    async def _exchange(self, config: dict[str, Any], inventory: dict[str, Any], errlog: Any,
                        cancel_check=None) -> dict[str, Any]:
        import anyio
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        if cancel_check is not None and cancel_check():
            from integrations.execution_control import ExecutionCancelled
            raise ExecutionCancelled("Operação REA cancelada antes de iniciar transporte.")
        runtime = inventory["provenance"]["runtime"]
        parameters = StdioServerParameters(
            command=runtime["node"], args=[runtime["launcher"], "mcp"],
            cwd=runtime["source_dir"], env=self._child_environment(native_required=config["operation"] == "analyze_binary"),
        )
        # The transport owns an external process group and performs stdin-close,
        # SIGTERM and SIGKILL cleanup. The deadline's cancellation scope ends
        # before transport teardown, so cancellation cannot bypass that cleanup.
        async with stdio_client(parameters, errlog=errlog) as (read_stream, write_stream):
            async def perform() -> dict[str, Any]:
                async with ClientSession(read_stream, write_stream, read_timeout_seconds=timedelta(seconds=config["timeout_seconds"])) as session:
                    initialized = self._dump(await session.initialize())
                    tools: list[dict[str, Any]] = []
                    cursor = None
                    seen_cursors = set()
                    while True:
                        page = self._dump(await session.list_tools(cursor=cursor))
                        tools.extend(page.get("tools", []))
                        cursor = page.get("nextCursor")
                        if not cursor:
                            break
                        if cursor in seen_cursors or len(seen_cursors) >= 32:
                            raise ValueError("Paginação do catálogo MCP inválida.")
                        seen_cursors.add(cursor)
                    if not tools:
                        raise ValueError("O servidor MCP não anunciou ferramentas.")
                    operation = config["operation"]
                    if operation == "catalog":
                        # A single catalog copy retains names, annotations and
                        # schemas without repeating them in summary fields.
                        return {"response": {"tools": tools}, "server": initialized.get("serverInfo"), "tool_count": len(tools)}
                    if operation == "layer":
                        tool = next((row for row in tools if row.get("name") == config["tool"]), None)
                        if tool is None:
                            raise ValueError(f"O servidor MCP não anunciou {config['tool']}.")
                        properties = tool.get("inputSchema", {}).get("properties", {})
                        fields = {config["path_field"], *config["fixed"]}
                        if config.get("encoding") is not None:
                            fields.add("encoding")
                        missing = sorted(field for field in fields if field not in properties)
                        if missing:
                            raise ValueError(f"Schema REA incompatível: {config['tool']} sem {', '.join(missing)}.")
                        arguments = {config["path_field"]: config["path"], **config["fixed"]}
                        if config.get("encoding") is not None:
                            arguments["encoding"] = config["encoding"]
                        response = self._dump(await session.call_tool(config["tool"], arguments=arguments))
                        return {"response": response, "server": initialized.get("serverInfo"),
                                "tool_count": len(tools), "tool": config["tool"]}
                    if operation == "analyze_binary":
                        required = {"open_binary": {"path", "provider_id"},
                                    "analyze_function": {"procedure"}, "binary_session": set(), "close_binary": set()}
                        for name, fields in required.items():
                            tool = next((row for row in tools if row.get("name") == name), None)
                            if tool is None or not fields.issubset(tool.get("inputSchema", {}).get("properties", {})):
                                raise ValueError(f"Schema REA incompatível: {name} ou parâmetros ausentes.")
                        responses: dict[str, Any] = {}
                        inventory["response"] = responses
                        inventory["cleanup"] = {"attempted": False, "closed": False}
                        try:
                            responses["open"] = self._dump(await session.call_tool("open_binary", arguments={"path": config["path"], "provider_id": "ghidra"}))
                            if self._response_error(responses["open"], "open_binary"):
                                return {"response": responses, "server": initialized.get("serverInfo"), "tool_count": len(tools), "tool": "analyze_function"}
                            responses["analysis"] = self._dump(await session.call_tool("analyze_function", arguments={"procedure": config["procedure"]}))
                            responses["session"] = self._dump(await session.call_tool("binary_session", arguments={}))
                        finally:
                            inventory["cleanup"]["attempted"] = True
                            # Cancelar o pedido não elimina a obrigação de fechar
                            # os recursos nativos; a limpeza tem seu próprio teto.
                            with anyio.CancelScope(shield=True):
                                with anyio.move_on_after(5):
                                    try:
                                        responses["close"] = self._dump(await session.call_tool("close_binary", arguments={}))
                                        # O contrato upstream de close_binary é
                                        # result=null. Provar o estado final exige
                                        # consultar a sessão, não inferir por ACK.
                                        if not self._response_error(responses["close"], "close_binary"):
                                            responses["closed_session"] = self._dump(await session.call_tool("binary_session", arguments={}))
                                            closed = self._structured(responses["closed_session"])
                                            inventory["cleanup"]["closed"] = (not self._response_error(responses["closed_session"], "native_stage")
                                                and isinstance(closed, dict) and isinstance(closed.get("result"), dict)
                                                and closed["result"].get("open") is False)
                                    except Exception:
                                        inventory["cleanup"]["closed"] = False
                        return {"response": responses, "server": initialized.get("serverInfo"), "tool_count": len(tools), "tool": "analyze_function"}
                    name = "binary_session" if operation == "session" else "analyze_javascript_application"
                    tool = next((tool for tool in tools if tool.get("name") == name), None)
                    if tool is None:
                        raise ValueError(f"O servidor MCP não anunciou {name}.")
                    arguments: dict[str, Any] = {}
                    if operation == "analyze":
                        if "input_path" not in tool.get("inputSchema", {}).get("properties", {}):
                            raise ValueError("Schema REA incompatível: input_path ausente.")
                        arguments = {
                            "input_path": config["path"], "detail": "complete",
                            "format": "auto", "integrity_policy": "fail",
                        }
                        if "analysis_timeout_ms" in tool.get("inputSchema", {}).get("properties", {}):
                            arguments["analysis_timeout_ms"] = max(1, int(config["timeout_seconds"] * 1000))
                    response = self._dump(await session.call_tool(name, arguments=arguments))
                    return {"response": response, "server": initialized.get("serverInfo"), "tool_count": len(tools), "tool": name}
            cancelled = False
            outcome = None
            with anyio.fail_after(config["timeout_seconds"]):
                async with anyio.create_task_group() as monitoring:
                    with anyio.CancelScope() as scope:
                        async def monitor():
                            nonlocal cancelled
                            while True:
                                if cancel_check is not None and cancel_check():
                                    cancelled = True
                                    scope.cancel()
                                    return
                                await anyio.sleep(.05)
                        monitoring.start_soon(monitor)
                        try:
                            outcome = await perform()
                        finally:
                            monitoring.cancel_scope.cancel()
            if cancelled:
                from integrations.execution_control import ExecutionCancelled
                raise ExecutionCancelled("Operação REA cancelada após limpeza do transporte.")
            return outcome

    @staticmethod
    def _structured(response: dict[str, Any]) -> Any:
        value = response.get("structuredContent")
        if value is None:
            for block in response.get("content", []):
                if block.get("type") == "text":
                    try:
                        return json.loads(block.get("text", ""))
                    except (ValueError, TypeError):
                        continue
        return value

    @staticmethod
    def _response_error(response: dict[str, Any], operation: str) -> str | None:
        if operation == "catalog":
            return None
        if operation == "analyze_binary":
            for key in ("open", "analysis", "session", "close", "closed_session"):
                if not isinstance(response.get(key), dict):
                    return f"REA não confirmou a etapa nativa {key}."
                error = ReaBridge._response_error(response[key], "native_stage")
                if error:
                    return error
            evidence = ReaBridge._structured(response["analysis"])
            if (not isinstance(evidence, dict) or evidence.get("operation") != "analyze_function"
                    or not isinstance(evidence.get("evidence_id"), str) or not evidence["evidence_id"].strip()
                    or not isinstance(evidence.get("provider"), dict)
                    or evidence["provider"].get("id") != "ghidra"
                    or not isinstance(evidence["provider"].get("version"), str)
                    or not evidence["provider"]["version"].strip()):
                return "REA não entregou Evidence nativa identificada do provider Ghidra."
            return None
        if response.get("isError"):
            return "REA retornou isError; consulte a resposta MCP preservada."
        if not response.get("content") and response.get("structuredContent") is None:
            return "REA encerrou a operação sem entregar conteúdo."
        value = response.get("structuredContent")
        if value is None:
            for block in response.get("content", []):
                if block.get("type") == "text":
                    try:
                        value = json.loads(block.get("text", ""))
                    except (ValueError, TypeError):
                        continue
                    break
        if isinstance(value, dict) and (
            ("error" in value and value["error"] is not None)
            or value.get("ok") is False or value.get("success") is False
            or value.get("status") in ("failed", "error", "unavailable")
        ):
            return "REA retornou erro estruturado; consulte a resposta MCP preservada."
        if operation == "session":
            session_value = value.get("result") if isinstance(value, dict) else None
            if isinstance(session_value, dict) and (
                ("error" in session_value and session_value["error"] is not None)
                or session_value.get("ok") is False
                or session_value.get("success") is False
                or session_value.get("status") in ("failed", "error", "unavailable")
            ):
                return "REA retornou erro na sessão; consulte a resposta MCP preservada."
            identity = session_value.get("server_identity") if isinstance(session_value, dict) else None
            if not isinstance(identity, dict):
                return "REA não entregou a identidade da sessão solicitada."
            for section in ("package", "server"):
                details = identity.get(section)
                if not isinstance(details, dict) or any(
                    not isinstance(details.get(field), str) or not details[field].strip()
                    for field in ("name", "version")
                ):
                    return "REA entregou uma identidade de sessão incompleta ou inválida."
        if operation == "analyze" and (
            not isinstance(value, dict)
            or value.get("operation") != "analyze_javascript_application"
            or not isinstance(value.get("evidence_id"), str)
            or not value["evidence_id"].strip()
        ):
            return "REA não entregou uma Evidence identificada da análise solicitada."
        if operation == "layer":
            if not isinstance(value, dict) or not value:
                return "REA não entregou conteúdo estruturado para a camada solicitada."
            evidence_id = value.get("evidence_id")
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                return "REA entregou Evidence de camada sem identificador válido."
            if not isinstance(value.get("operation"), str) or not value["operation"].strip():
                return "REA entregou Evidence sem operação identificada."
        return None

    @staticmethod
    def _exception_code(exc: BaseException) -> str:
        if isinstance(exc, TimeoutError):
            return "timeout"
        if isinstance(exc, BaseExceptionGroup):
            if any(ReaBridge._exception_code(child) == "timeout" for child in exc.exceptions):
                return "timeout"
        # MCP also uses its own McpError for a request-level deadline.
        if "timed out" in str(exc).lower() or "timeout" in str(exc).lower():
            return "timeout"
        return "mcp_failure"

    @staticmethod
    def _exception_message(exc: BaseException) -> str:
        if isinstance(exc, BaseExceptionGroup):
            return "; ".join(ReaBridge._exception_message(child) for child in exc.exceptions)
        return str(exc) or type(exc).__name__

    def action(self, config: dict[str, Any]) -> dict[str, Any]:
        """Valida a operação, executa MCP sem shell e preserva a resposta integral."""
        validated = self._validate(config)
        result = self.status()
        operation = validated["operation"]
        if operation == "status":
            return result
        if operation == "layers":
            report = layers_status()
            report["rea_installed"] = result["available"]
            report["provenance"] = {"repository": self.REPOSITORY, "commit": None,
                                    "version": result["provenance"].get("version"),
                                    "runtime": result["provenance"].get("runtime"), "response_sha256": None}
            return report
        result["operation"] = operation
        if not result["available"]:
            return result
        result.update(status="failed", success=False, verification="mcp_execution", reason="Conclusão operacional MCP não atribui validação externa ou confiança adicional.")
        if operation == "layer":
            result["provenance"]["layer"] = validated["layer"]
            result["provenance"]["layer_tool"] = validated["tool"]
            readiness = probe_layer(validated["layer"])
            result["provenance"]["layer_readiness"] = {
                "ready": readiness["ready"], "engine": readiness["engine"], "reason": readiness["reason"]}
        if operation == "analyze_binary":
            result["provenance"]["target_sha256"] = validated["target_sha256"]
            try:
                environment = self._child_environment(native_required=True)
                result["provenance"]["native_runtime"] = {key: environment[key] for key in ("GHIDRA_INSTALL_DIR", "JAVA_HOME")}
            except ValueError as exc:
                result.update(error_code="provider_unavailable", error=str(exc))
                return result
        started = time.monotonic()
        try:
            import anyio
            from integrations.execution_control import is_cancelled
            cancellation_context = contextvars.copy_context()
            cancel_check = lambda: cancellation_context.run(is_cancelled)
            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as errlog:
                def execute() -> dict[str, Any]:
                    # asyncio.to_thread copies the gateway's ContextVars,
                    # including AnyIO/sniffio's async-library marker. A fresh
                    # context avoids falsely detecting a running child loop.
                    return contextvars.Context().run(anyio.run, self._exchange, validated, result, errlog, cancel_check)
                try:
                    try:
                        asyncio.get_running_loop()
                    except RuntimeError:
                        response = execute()
                    else:
                        # The synchronous public API is also called by async MCP
                        # gateways; keep the child session in its own event loop.
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            response = executor.submit(execute).result()
                    result.update(response)
                finally:
                    errlog.seek(0)
                    log = errlog.read(65_537)
                    if log:
                        result["stderr"] = log[:65_536]
                        result["stderr_truncated"] = len(log) > 65_536
            error = self._response_error(result["response"], operation)
            if operation == "layer" and error is None:
                value = self._structured(result["response"])
                if value.get("operation") != validated["tool"]:
                    error = "REA entregou Evidence de outra operação, fora da camada solicitada."
            if operation == "analyze_binary" and error is None:
                evidence = self._structured(result["response"]["analysis"])
                session_value = self._structured(result["response"]["session"])
                session_value = session_value.get("result") if isinstance(session_value, dict) else None
                subject = evidence.get("subject", {})
                with Path(validated["path"]).open("rb") as stream:
                    after = hashlib.file_digest(stream, "sha256").hexdigest()
                if (after != validated["target_sha256"] or not isinstance(subject, dict)
                        or subject.get("digest", {}).get("sha256") != after
                        or not isinstance(session_value, dict) or session_value.get("open") is not True
                        or session_value.get("sha256") != after
                        or session_value.get("analysis_provider_binding", {}).get("provider", {}).get("id") != "ghidra"):
                    error = "REA entregou alvo ou vínculo de sessão divergente da análise solicitada."
                elif result.get("cleanup", {}).get("closed") is not True:
                    error = "REA não confirmou o fechamento dos recursos nativos."
            result.update(status="failed" if error else "completed", success=error is None, error=error)
            if error:
                result["error_code"] = "tool_failure"
        except Exception as exc:
            from integrations.execution_control import ExecutionCancelled
            code = "cancelled" if isinstance(exc, ExecutionCancelled) else self._exception_code(exc)
            result.update(error_code=code, error="Tempo limite MCP excedido; processo REA encerrado." if code == "timeout" else f"Falha na execução MCP REA: {self._exception_message(exc)}")
        finally:
            result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        if result["response"] is not None:
            encoded = json.dumps(result["response"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            result["provenance"]["response_sha256"] = hashlib.sha256(encoded).hexdigest()
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ponte de servidor MCP REA instalado")
    parser.add_argument("operation", choices=["mcp"])
    parser.parse_args(argv)
    inventory = ReaBridge().status()
    if not inventory["available"]:
        print(inventory["error"], file=sys.stderr)
        return 1
    runtime = inventory["provenance"]["runtime"]
    # O ambiente é passado ao filho; os defaults do processo pai permanecem.
    environment = ReaBridge._child_environment()
    os.execve(runtime["node"], [runtime["node"], runtime["launcher"], "mcp"], environment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
