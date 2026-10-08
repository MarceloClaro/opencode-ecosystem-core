"""R672: cliente MCP stdio delimitado e execução da CLI oficial instalada.

Não implementa APIs privadas do NotebookLM nem lê o armazenamento de login.
O serviço central determina quais operações e argumentos estão autorizados.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
from typing import Any

import jsonschema


OUTPUT_LIMIT = 1_048_576
INPUT_LIMIT = 131_072
_SECRET_KEY = re.compile(
    r"authorization|cookies?|set[-_]cookie|(?:access|refresh|auth|csrf)[-_]?token|"
    r"api[-_]?key|password|secret|session[-_]?cookie", re.I,
)
_NAME = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z")


def sanitize_output(value: Any) -> Any:
    """Remove credenciais usuais sem ler ou revelar arquivos de autenticação."""
    if isinstance(value, dict):
        return {key: "[REDACTED]" if _SECRET_KEY.search(str(key)) else sanitize_output(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_output(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r"(?im)\b(authorization|cookie|set-cookie)\s*[:=][^\r\n]*",
                       r"\1: [REDACTED]", value)
        value = re.sub(r"(?i)([\"']?(?:access_token|refresh_token|auth_token|csrf_token|"
                       r"api_key|api-key|password|secret)[\"']?\s*[:=]\s*)"
                       r"(?:\"[^\"]*\"|'[^']*'|[^\s,;&}]+)",
                       r"\1[REDACTED]", value)
        value = re.sub(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]", value,
                       flags=re.I)
        value = re.sub(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
                       "[REDACTED]", value)
        value = re.sub(r"\bAIza[A-Za-z0-9_-]{20,}\b", "[REDACTED]", value)
        return value
    return value


def _business_states(value: Any, depth: int = 0) -> set[str]:
    if depth > 32:
        return {"failed"}
    states = set()
    if isinstance(value, dict):
        failure_count = value.get("failed")
        succeeded, total = value.get("succeeded"), value.get("total_steps")
        if type(failure_count) in {int, float} and failure_count > 0:
            states.add("partial" if type(succeeded) in {int, float} and succeeded > 0 else "failed")
        elif type(succeeded) in {int, float} and type(total) in {int, float} and succeeded < total:
            states.add("partial" if succeeded > 0 else "pending")
        for key, item in value.items():
            if key in {"success", "ok"}:
                if item is False:
                    states.add("failed")
                elif item is True:
                    states.add("completed")
            if key in {"status", "state"} and isinstance(item, str):
                state = item.casefold()
                if state in {"error", "failed", "failure", "blocked", "cancelled", "canceled", "timeout"}:
                    states.add("failed")
                elif state in {"success", "completed", "ok"}:
                    states.add("completed")
                elif state in {"partial", "pending", "running", "generating"}:
                    states.add(state)
                elif state in {"queued", "waiting"}:
                    states.add("pending")
                elif state in {"in_progress", "in-progress", "processing", "started"}:
                    states.add("running")
            states.update(_business_states(item, depth + 1))
    elif isinstance(value, list):
        for item in value:
            states.update(_business_states(item, depth + 1))
    elif isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (ValueError, TypeError, RecursionError):
            if re.match(r"^\s*(?:Error|Failed|Failure)\s*:", value, re.I):
                states.add("failed")
        else:
            if isinstance(decoded, (dict, list)):
                states.update(_business_states(decoded, depth + 1))
    return states


def _business_status(value: Any) -> tuple[str, bool | None]:
    states = _business_states(value)
    # Estados mistos e incompletos prevalecem sobre flags genéricas de sucesso.
    for state in ("partial", "failed", "generating", "running", "pending"):
        if state in states:
            return state, False if state in {"failed", "partial"} else None
    return "completed", True if "completed" in states else None


def _business_flags(value: Any, depth: int = 0) -> tuple[bool, bool]:
    """Compatibilidade interna: confirmação positiva somente na conclusão total."""
    states = _business_states(value, depth)
    return bool(states & {"failed", "partial"}), states == {"completed"}


def classify_tool_result(result: dict[str, Any]) -> dict[str, Any]:
    """Distingue transporte concluído de erro comunicado pela aplicação."""
    if not isinstance(result, dict):
        return {"status": "failed", "transport_success": False,
                "business_success": False, "result": sanitize_output(result)}
    status, business_success = _business_status(result)
    if result.get("isError") is True:
        status, business_success = "failed", False
    return {"status": status,
            "transport_success": True,
            "business_success": business_success,
            "result": sanitize_output(result)}


def _json_bytes(value: Any, limit: int = INPUT_LIMIT) -> bytes:
    try:
        raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("JSON finito obrigatório") from exc
    if len(raw) > limit:
        raise ValueError("Entrada excede limite de bytes")
    return raw


def _timeout(value: Any) -> float:
    if type(value) not in {int, float} or not math.isfinite(value) or not 0.05 <= value <= 600:
        raise ValueError("Tempo limite inválido")
    return float(value)


def _strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Schemas MCP por vezes omitem additionalProperties; aplicar contrato fechado."""
    result = deepcopy(schema)

    def visit(item: Any):
        if isinstance(item, dict):
            for ref in ("$ref", "$dynamicRef", "$recursiveRef"):
                if ref in item and (not isinstance(item[ref], str) or not item[ref].startswith("#")):
                    raise _Blocked("Referência de schema externa não permitida")
            if (item.get("type") == "object" or "properties" in item) and "additionalProperties" not in item:
                # patternProperties e mapas declarados continuam sendo respeitados.
                item["additionalProperties"] = False
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(result)
    return result


class _OutputLimit(Exception):
    pass


class _Blocked(Exception):
    pass


class _ProtocolSession:
    def __init__(self, process: asyncio.subprocess.Process):
        self.process = process
        self.sequence = 0
        self.bytes_read = 0
        self.stderr = bytearray()
        self.stderr_limit = asyncio.get_running_loop().create_future()
        self.stderr_task = asyncio.create_task(self._read_stderr())

    async def _read_stderr(self):
        try:
            while chunk := await self.process.stderr.read(65_536):
                self.stderr.extend(chunk)
                if len(self.stderr) > OUTPUT_LIMIT:
                    self.stderr_limit.set_exception(_OutputLimit())
                    return
        except Exception as exc:
            if not self.stderr_limit.done():
                self.stderr_limit.set_exception(exc)

    async def close(self):
        self.stderr_task.cancel()
        await asyncio.gather(self.stderr_task, return_exceptions=True)
        if self.stderr_limit.done() and not self.stderr_limit.cancelled():
            self.stderr_limit.exception()
        self.stderr_limit.cancel()

    async def send(self, message: dict[str, Any]):
        self.process.stdin.write(_json_bytes(message) + b"\n")
        await self.process.stdin.drain()

    async def receive(self):
        task = asyncio.create_task(self.process.stdout.readline())
        try:
            ready, _ = await asyncio.wait([task, self.stderr_limit],
                                          return_when=asyncio.FIRST_COMPLETED)
            if self.stderr_limit in ready:
                await self.stderr_limit
            try:
                raw = await task
            except (ValueError, asyncio.LimitOverrunError) as exc:
                raise _OutputLimit() from exc
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
        if not raw:
            raise RuntimeError("Servidor MCP encerrou antes da resposta")
        self.bytes_read += len(raw)
        if self.bytes_read > OUTPUT_LIMIT:
            raise _OutputLimit()
        try:
            result = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except (ValueError, RecursionError) as exc:
            raise RuntimeError("Resposta MCP inválida") from exc
        if not isinstance(result, dict) or result.get("jsonrpc") != "2.0":
            raise RuntimeError("Envelope MCP inválido")
        return result

    async def rpc(self, method: str, params: dict[str, Any] | None = None):
        self.sequence += 1
        request_id = self.sequence
        await self.send({"jsonrpc": "2.0", "id": request_id, "method": method,
                         "params": params or {}})
        for _ in range(128):
            message = await self.receive()
            if "method" in message:
                if "id" in message:
                    if message["method"] == "ping":
                        await self.send({"jsonrpc": "2.0", "id": message["id"], "result": {}})
                    else:
                        await self.send({"jsonrpc": "2.0", "id": message["id"],
                                         "error": {"code": -32601, "message": "Método não suportado"}})
                continue
            if message.get("id") != request_id:
                raise RuntimeError("Resposta MCP não corresponde à requisição")
            if "error" in message:
                raise RuntimeError("Servidor MCP comunicou erro de protocolo")
            if not isinstance(message.get("result"), dict):
                raise RuntimeError("Resultado MCP deve ser objeto")
            return message["result"]
        raise RuntimeError("Excesso de notificações MCP")

    async def discover(self):
        initialization = await self.rpc("initialize", {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "opencode-core-notebook-transport", "version": "R672"},
        })
        if not isinstance(initialization.get("serverInfo"), dict):
            raise RuntimeError("Identidade do servidor MCP ausente")
        await self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools, cursors, cursor = [], set(), None
        for _ in range(20):
            page = await self.rpc("tools/list", {"cursor": cursor} if cursor else {})
            if not isinstance(page.get("tools"), list):
                raise RuntimeError("Lista de ferramentas MCP inválida")
            for tool in page["tools"]:
                if not isinstance(tool, dict) or not _NAME.fullmatch(str(tool.get("name", ""))):
                    raise RuntimeError("Nome de ferramenta MCP inválido")
                if not isinstance(tool.get("inputSchema"), dict):
                    raise RuntimeError("Schema de ferramenta MCP ausente")
                tools.append({key: deepcopy(tool.get(key, {} if key == "annotations" else ""))
                              for key in ("name", "description", "inputSchema", "annotations")})
            cursor = page.get("nextCursor")
            if not cursor:
                break
            if not isinstance(cursor, str) or cursor in cursors:
                raise RuntimeError("Paginação MCP inválida")
            cursors.add(cursor)
        else:
            raise RuntimeError("Excesso de páginas MCP")
        if len({tool["name"] for tool in tools}) != len(tools):
            raise RuntimeError("Ferramentas MCP duplicadas")
        info = initialization["serverInfo"]
        return {"name": info.get("name", ""), "version": info.get("version", ""),
                "protocol_version": initialization.get("protocolVersion", ""), "tools": tools}


class GeminiNotebookTransport:
    """API assíncrona para o servidor e a CLI instalados, sem fallback remoto."""

    def __init__(self, repo_root: str | Path | None = None,
                 env_overrides: dict[str, str] | None = None,
                 persistent: bool = False, _session_idle_seconds: float = 3600):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
        if env_overrides is not None and (not isinstance(env_overrides, dict)
                or any(not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
                       or not isinstance(value, str) or "\0" in value
                       for key, value in env_overrides.items())):
            raise ValueError("Configuração interna de ambiente inválida")
        _json_bytes(env_overrides or {})
        # Apenas o serviço central fornece overrides; esta opção não é uma CLI pública.
        self.env_overrides = dict(env_overrides or {})
        if type(persistent) is not bool or type(_session_idle_seconds) not in {int, float} or not 0.1 <= _session_idle_seconds <= 3600:
            raise ValueError("Configuração interna de sessão inválida")
        self.persistent = persistent
        self._session_idle_seconds = float(_session_idle_seconds)

    def resolve_binary(self, name: str) -> Path | None:
        if name not in {"nlm", "notebooklm-mcp"}:
            raise ValueError("Executável não suportado")
        if name == "nlm" and os.environ.get("NLM_BIN"):
            explicit = Path(os.environ["NLM_BIN"]).expanduser()
            if not explicit.is_absolute():
                raise ValueError("NLM_BIN exige caminho absoluto")
            return explicit.resolve() if explicit.is_file() and os.access(explicit, os.X_OK) else None
        local = self.repo_root / ".venv" / "bin" / name
        if local.is_file() and os.access(local, os.X_OK):
            return local.resolve()
        fallback = shutil.which(name)
        return Path(fallback).resolve() if fallback else None

    async def _terminate(self, process):
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            if process.returncode is None:
                process.kill()
        await process.wait()

    @asynccontextmanager
    async def _session(self, binary: Path):
        process = await asyncio.create_subprocess_exec(
            str(binary), "--transport", "stdio", "--no-debug",
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE, cwd=self.repo_root,
            start_new_session=True, limit=OUTPUT_LIMIT,
            env={**os.environ, **self.env_overrides, "NOTEBOOKLM_MCP_DEBUG": "false"},
        )
        session = _ProtocolSession(process)
        try:
            yield session
        finally:
            await self._terminate(process)
            await session.close()

    async def _mcp_operation(self, name=None, arguments=None, timeout_seconds=60):
        process_executed = False
        try:
            timeout_seconds = _timeout(timeout_seconds)
            if name is not None:
                if not isinstance(name, str) or not _NAME.fullmatch(name):
                    raise ValueError("Nome de ferramenta inválido")
                if not isinstance(arguments, dict):
                    raise ValueError("Argumentos devem ser objeto JSON")
                _json_bytes(arguments)
            binary = self.resolve_binary("notebooklm-mcp")
            if binary is None:
                raise _Blocked("Servidor oficial não instalado")
            async with asyncio.timeout(timeout_seconds):
                async with self._session(binary) as session:
                    process_executed = True
                    discovery = await session.discover()
                    if name is None:
                        # Nomes de propriedades de schemas são metadados públicos,
                        # mesmo quando descrevem campos de credenciais.
                        return {**discovery, "status": "completed",
                                "process_executed": True, "transport": "mcp_stdio",
                                "remote_inference_executed": False}
                    tools = {tool["name"]: tool for tool in discovery["tools"]}
                    if name not in tools:
                        raise _Blocked("Operação não descoberta no servidor oficial")
                    schema = _strict_schema(tools[name]["inputSchema"])
                    try:
                        validator = jsonschema.validators.validator_for(schema)
                        validator.check_schema(schema)
                        validator(schema, format_checker=jsonschema.FormatChecker()).validate(arguments)
                    except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
                        raise _Blocked("Argumentos incompatíveis com inputSchema") from exc
                    result = await session.rpc("tools/call", {"name": name, "arguments": arguments})
                    classified = classify_tool_result(result)
                    return {**classified, "tool": name, "process_executed": True,
                            "transport": "mcp_stdio", "server": discovery["name"],
                            "server_version": discovery["version"],
                            "response_sha256": hashlib.sha256(_json_bytes(result, OUTPUT_LIMIT)).hexdigest()}
        except (_Blocked, ValueError) as exc:
            return {"status": "blocked", "reason": sanitize_output(str(exc)),
                    "process_executed": process_executed, "transport": "mcp_stdio"}
        except TimeoutError:
            reason = "timeout"
        except _OutputLimit:
            reason = "output_limit"
        except Exception as exc:
            reason = sanitize_output(str(exc))[:2_000]
        return {"status": "failed", "reason": reason, "process_executed": process_executed,
                "transport": "mcp_stdio"}

    async def discover_mcp(self, timeout_seconds=60):
        if self.persistent:
            from .gemini_notebook_session import persistent_request
            return await persistent_request(self, "discover", timeout_seconds=timeout_seconds)
        return await self._mcp_operation(timeout_seconds=timeout_seconds)

    async def call_mcp(self, tool_name: str, arguments: dict[str, Any], timeout_seconds=60):
        if self.persistent:
            from .gemini_notebook_session import persistent_request
            return await persistent_request(self, "call", tool_name, arguments, timeout_seconds)
        return await self._mcp_operation(tool_name, arguments, timeout_seconds)

    async def close_persistent(self, timeout_seconds=10):
        from .gemini_notebook_session import persistent_request
        return await persistent_request(self, "close", timeout_seconds=timeout_seconds)

    async def run_cli(self, argv: list[str], timeout_seconds=60):
        """Recebe argv completo começando por `nlm`; nunca utiliza shell."""
        process, tasks = None, []
        try:
            timeout_seconds = _timeout(timeout_seconds)
            if not isinstance(argv, list) or not argv or argv[0] != "nlm" or len(argv) > 100:
                raise ValueError("Vetor CLI inválido; executável deve ser nlm")
            if any(not isinstance(arg, str) or "\0" in arg or len(arg.encode()) > 16_384 for arg in argv):
                raise ValueError("Argumento CLI inválido")
            _json_bytes(argv)
            if any(arg in {"--debug", "--verbose", "--dump-cookies", "--dump-auth"} for arg in argv):
                raise ValueError("Debug e dumps de autenticação não são permitidos")
            binary = self.resolve_binary("nlm")
            if binary is None:
                raise _Blocked("CLI oficial não instalada")

            async def read_limited(stream):
                data = bytearray()
                while chunk := await stream.read(65_536):
                    data.extend(chunk)
                    if len(data) > OUTPUT_LIMIT:
                        raise _OutputLimit()
                return bytes(data).decode("utf-8", errors="replace")

            async with asyncio.timeout(timeout_seconds):
                process = await asyncio.create_subprocess_exec(
                    str(binary), *argv[1:], stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=self.repo_root, start_new_session=True,
                    env={**os.environ, **self.env_overrides},
                )
                tasks = [asyncio.create_task(read_limited(process.stdout)),
                         asyncio.create_task(read_limited(process.stderr))]
                stdout, stderr = await asyncio.gather(*tasks)
                code = await process.wait()
            try:
                result = json.loads(stdout)
            except (ValueError, RecursionError):
                result = None
            status, business_success = _business_status(result if result is not None else stdout)
            if code != 0:
                status, business_success = "failed", False
            return {"status": status,
                    "process_executed": True, "transport": "cli", "exit_code": code,
                    "stdout": sanitize_output(stdout), "stderr": sanitize_output(stderr),
                    "result": sanitize_output(result),
                    "business_success": business_success,
                    "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest()}
        except (_Blocked, ValueError) as exc:
            return {"status": "blocked", "reason": sanitize_output(str(exc)),
                    "process_executed": process is not None, "transport": "cli"}
        except TimeoutError:
            reason = "timeout"
        except _OutputLimit:
            reason = "output_limit"
        except Exception as exc:
            reason = sanitize_output(str(exc))[:2_000]
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            if process is not None:
                await self._terminate(process)
        return {"status": "failed", "reason": reason, "process_executed": process is not None,
                "transport": "cli"}
