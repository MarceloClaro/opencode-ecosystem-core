"""R672: broker Unix privado que mantém jobs do servidor MCP entre CLIs Core."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import stat
import struct
import subprocess
import sys
import time
import uuid

import jsonschema

from .gemini_notebook_transport import (
    GeminiNotebookTransport, INPUT_LIMIT, OUTPUT_LIMIT, _Blocked, _NAME,
    _OutputLimit, _SECRET_KEY, _json_bytes, _strict_schema, _timeout,
    classify_tool_result, sanitize_output,
)


def _private_directory(root: Path) -> Path:
    current = root
    for name in (".opencode", "notebooklm", "broker"):
        current = current / name
        if current.is_symlink():
            raise ValueError("Diretório de sessão não pode ser symlink")
        current.mkdir(exist_ok=True, mode=0o700)
        if not current.is_dir() or current.stat().st_uid != os.getuid():
            raise ValueError("Diretório de sessão não pertence ao usuário")
    current.chmod(0o700)
    return current


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _configuration(transport):
    binary = transport.resolve_binary("notebooklm-mcp")
    if binary is None:
        raise _Blocked("Servidor oficial não instalado")
    if any(_SECRET_KEY.search(key) for key in transport.env_overrides):
        raise ValueError("Credenciais não podem ser persistidas no broker")
    environment = {key: value for key, value in os.environ.items()
                   if key.startswith(("NOTEBOOKLM_", "NLM_", "GOOGLE_", "GEMINI_", "R672_", "XDG_"))
                   or key == "HOME"}
    versions = {}
    for name in ("notebooklm-mcp-cli", "fastmcp", "mcp"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "absent"
    effective_environment = {**os.environ, **transport.env_overrides}
    storage = Path(effective_environment.get("NOTEBOOKLM_MCP_CLI_PATH",
                   str(Path(effective_environment.get("HOME", str(Path.home()))) / ".notebooklm-mcp-cli")))
    config_path = storage / "config.toml"
    try:
        config_metadata = config_path.stat()
        config_signature = {"mtime_ns": config_metadata.st_mtime_ns, "size": config_metadata.st_size}
    except FileNotFoundError:
        config_signature = {"absent": True}
    identity = {"binary": str(binary), "binary_sha256": _hash_file(binary),
                "versions": versions, "repo_root": str(transport.repo_root),
                "profile_config_metadata": config_signature,
                "env_hash": hashlib.sha256(_json_bytes(environment)).hexdigest(),
                "overrides": transport.env_overrides,
                "idle_seconds": transport._session_idle_seconds}
    fingerprint = hashlib.sha256(_json_bytes(identity)).hexdigest()
    # Valores do ambiente herdado permanecem somente na memória dos processos.
    return {"repo_root": str(transport.repo_root), "binary": str(binary),
            "binary_sha256": identity["binary_sha256"], "env_overrides": transport.env_overrides,
            "idle_seconds": transport._session_idle_seconds, "fingerprint": fingerprint}


def _check_local_file(path: Path, *, socket_file=False):
    if path.is_symlink():
        raise ValueError("Arquivo de sessão não pode ser symlink")
    if path.exists():
        metadata = path.lstat()
        if metadata.st_uid != os.getuid():
            raise ValueError("Arquivo de sessão não pertence ao usuário")
        if socket_file and not stat.S_ISSOCK(metadata.st_mode):
            raise ValueError("Destino de sessão existente não é socket")
        if not socket_file and not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Metadado de sessão deve ser arquivo regular")
        if metadata.st_mode & 0o077:
            raise ValueError("Arquivo de sessão exige permissões privadas")


def _socket_alias(path: Path):
    # AF_UNIX limita o comprimento do caminho; /proc/self/fd preserva o destino
    # dentro do workspace mesmo em diretórios de testes com nomes longos.
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    return fd, f"/proc/self/fd/{fd}/{path.name}"


async def _exchange(path: Path, payload: dict, timeout_seconds: float):
    _check_local_file(path, socket_file=True)
    fd, alias = _socket_alias(path)
    writer = None
    try:
        async with asyncio.timeout(timeout_seconds):
            reader, writer = await asyncio.open_unix_connection(alias, limit=OUTPUT_LIMIT)
            writer.write(_json_bytes(payload) + b"\n")
            await writer.drain()
            try:
                raw = await reader.readline()
            except ValueError as exc:
                raise _OutputLimit() from exc
            if not raw or len(raw) > OUTPUT_LIMIT:
                raise _OutputLimit()
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise ValueError("Resposta de sessão inválida")
            return result
    finally:
        os.close(fd)
        if writer is not None:
            writer.close()
            await writer.wait_closed()


def _pid_alive(path: Path):
    _check_local_file(path)
    if not path.exists():
        return False
    try:
        pid = json.loads(path.read_text())["pid"]
        if type(pid) is not int or pid < 2:
            return False
        os.kill(pid, 0)
        return True
    except (ValueError, KeyError, ProcessLookupError):
        return False


async def _ensure_broker(config, base, socket_path):
    lock_path = base / (socket_path.stem + ".lock")
    _check_local_file(lock_path)
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        await asyncio.to_thread(fcntl.flock, lock_fd, fcntl.LOCK_EX)
        if socket_path.exists():
            try:
                response = await _exchange(socket_path, {"operation": "ping"}, 5)
                if response.get("fingerprint") == config["fingerprint"]:
                    return
                raise ValueError("Identidade da sessão divergente")
            except (ConnectionError, FileNotFoundError, TimeoutError):
                pid_path = base / (socket_path.stem + ".pid")
                if _pid_alive(pid_path):
                    raise _Blocked("Sessão existente não respondeu; preservada para diagnóstico")
                _check_local_file(socket_path, socket_file=True)
                socket_path.unlink()
        config_path = base / (socket_path.stem + ".json")
        _check_local_file(config_path)
        config_fd = os.open(config_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(config_fd, "wb") as stream:
            stream.write(_json_bytes(config))
        subprocess.Popen([sys.executable, "-m", "integrations.gemini_notebook_session",
                          "--broker", str(config_path)],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         cwd=Path(__file__).resolve().parents[1], start_new_session=True, close_fds=True)
        for _ in range(150):
            try:
                response = await _exchange(socket_path, {"operation": "ping"}, 0.3)
                if response.get("fingerprint") == config["fingerprint"]:
                    return
            except (ConnectionError, FileNotFoundError, TimeoutError):
                await asyncio.sleep(0.05)
        raise _Blocked("Broker local não iniciou")
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


async def persistent_request(transport, operation, tool_name=None, arguments=None, timeout_seconds=60):
    try:
        timeout_seconds = _timeout(timeout_seconds)
        if operation not in {"discover", "call", "close"}:
            raise ValueError("Operação de sessão inválida")
        if operation == "close":
            return await _close_all(transport, timeout_seconds)
        if operation == "call":
            if not isinstance(tool_name, str) or not _NAME.fullmatch(tool_name) or not isinstance(arguments, dict):
                raise ValueError("Ferramenta e argumentos inválidos")
            _json_bytes(arguments)
            if tool_name == "notebook_query_status":
                return await _route_job_status(transport, arguments, timeout_seconds)
        config = _configuration(transport)
        base = _private_directory(transport.repo_root)
        socket_path = base / (config["fingerprint"][:16] + ".sock")
        _check_local_file(socket_path, socket_file=True)
        if operation == "close" and not socket_path.exists():
            return {"status": "completed", "session_closed": True, "process_executed": False}
        if operation != "close":
            await _ensure_broker(config, base, socket_path)
        response = await _exchange(socket_path, {"operation": operation, "tool": tool_name,
                                  "arguments": arguments, "timeout_seconds": timeout_seconds},
                                   timeout_seconds + 15)
        if operation == "call" and tool_name == "notebook_query_start" and response.get("status") not in {"failed", "blocked", "lost"}:
            query_id = _extract_query_id(response.get("result", {}))
            if query_id:
                try:
                    _register_job(base, query_id, config["fingerprint"], response.get("session_id"))
                except (_Blocked, ValueError) as exc:
                    return {"status": "blocked", "reason": str(exc), "process_executed": True,
                            "untracked_job_created": True, "persistent_session": True}
        return {**response, "persistent_session": True, "session_fingerprint": config["fingerprint"]}
    except (_Blocked, ValueError) as exc:
        return {"status": "blocked", "reason": sanitize_output(str(exc)), "process_executed": False,
                "persistent_session": True}
    except Exception as exc:
        return {"status": "failed", "reason": "timeout" if isinstance(exc, TimeoutError) else sanitize_output(str(exc)),
                "process_executed": False, "persistent_session": True}


def _extract_query_id(result):
    data = result.get("structuredContent", {}) if isinstance(result, dict) else {}
    if isinstance(data, dict) and isinstance(data.get("query_id"), str):
        return data["query_id"]
    for block in result.get("content", []) if isinstance(result, dict) else []:
        try:
            data = json.loads(block.get("text", ""))
        except (ValueError, TypeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("query_id"), str):
            return data["query_id"]
    return None


def _job_directory(base):
    directory = base / "jobs"
    if directory.is_symlink():
        raise ValueError("Registro de jobs não pode ser symlink")
    directory.mkdir(exist_ok=True, mode=0o700)
    if not directory.is_dir() or directory.stat().st_uid != os.getuid():
        raise ValueError("Registro de jobs não pertence ao usuário")
    directory.chmod(0o700)
    return directory


def _job_path(base, query_id):
    if not isinstance(query_id, str) or not _NAME.fullmatch(query_id):
        raise ValueError("Identificador de job inválido")
    return _job_directory(base) / (hashlib.sha256(query_id.encode()).hexdigest() + ".json")


def _read_job(path):
    _check_local_file(path)
    if path.stat().st_size > INPUT_LIMIT:
        raise ValueError("Registro de job excede limite")
    record = json.loads(path.read_text())
    if not isinstance(record, dict) or set(record) != {"query_id", "session_fingerprint", "session_id"}:
        raise ValueError("Registro de job inválido")
    fingerprint = record["session_fingerprint"]
    if not isinstance(fingerprint, str) or len(fingerprint) != 64 or any(char not in "0123456789abcdef" for char in fingerprint):
        raise ValueError("Identidade de sessão do job inválida")
    if not isinstance(record["session_id"], str) or not _NAME.fullmatch(record["session_id"]):
        raise ValueError("Identidade do processo do job inválida")
    return record


def _register_job(base, query_id, fingerprint, session_id):
    path = _job_path(base, query_id)
    lock_path = path.with_suffix(".lock")
    _check_local_file(lock_path)
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        _check_local_file(path)
        record = {"query_id": query_id, "session_fingerprint": fingerprint, "session_id": session_id}
        if path.exists() and _read_job(path) != record:
            raise _Blocked("Identificador de job já pertence a outra sessão")
        temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(_json_bytes(record))
        temporary.replace(path)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def _lost_job(query_id, reason):
    return {"status": "lost", "reason": reason, "query_id": query_id,
            "volatile_jobs_lost": True, "process_executed": False,
            "persistent_session": True}


async def _route_job_status(transport, arguments, timeout_seconds):
    if set(arguments) != {"query_id"}:
        raise ValueError("Argumentos incompatíveis com notebook_query_status")
    query_id = arguments.get("query_id")
    base = _private_directory(transport.repo_root)
    path = _job_path(base, query_id)
    _check_local_file(path)
    if not path.exists():
        return _lost_job(query_id, "job_not_registered_in_core_session")
    record = _read_job(path)
    if record["query_id"] != query_id:
        raise ValueError("Registro de job não corresponde ao identificador")
    fingerprint = record["session_fingerprint"]
    socket_path = base / (fingerprint[:16] + ".sock")
    _check_local_file(socket_path, socket_file=True)
    if not socket_path.exists():
        return _lost_job(query_id, "session_expired_or_closed")
    try:
        response = await _exchange(socket_path, {"operation": "call", "tool": "notebook_query_status",
                                   "arguments": arguments, "expected_session_id": record["session_id"],
                                   "timeout_seconds": timeout_seconds}, timeout_seconds + 15)
    except (ConnectionError, FileNotFoundError):
        return _lost_job(query_id, "origin_session_unavailable")
    if response.get("session_reset"):
        response = {**response, "status": "lost", "runtime_reason": response.get("reason"),
                    "reason": "origin_session_lost", "volatile_jobs_lost": True}
    return {**response, "persistent_session": True, "session_fingerprint": fingerprint}


async def _close_all(transport, timeout_seconds):
    base = _private_directory(transport.repo_root)
    closed, lost = 0, False
    async with asyncio.timeout(timeout_seconds):
        sockets = sorted(base.glob("*.sock"))
        if len(sockets) > 64:
            raise ValueError("Quantidade excessiva de sessões locais")
        for path in sockets:
            if not re_session_name(path.stem):
                raise ValueError("Nome de socket de sessão inválido")
            _check_local_file(path, socket_file=True)
            config_path = path.with_suffix(".json")
            _check_local_file(config_path)
            if config_path.stat().st_size > INPUT_LIMIT:
                raise ValueError("Configuração de sessão excede limite")
            config = json.loads(config_path.read_text())
            if config.get("repo_root") != str(transport.repo_root) or config.get("fingerprint", "")[:16] != path.stem:
                raise ValueError("Identidade de sessão fora do workspace")
            try:
                response = await _exchange(path, {"operation": "close"}, timeout_seconds)
                lost |= bool(response.get("volatile_jobs_lost"))
                while path.exists():
                    await asyncio.sleep(0.02)
            except ConnectionError:
                if _pid_alive(path.with_suffix(".pid")):
                    raise _Blocked("Sessão não respondeu ao encerramento")
                _check_local_file(path, socket_file=True)
                path.unlink()
            closed += 1
    return {"status": "completed", "session_closed": True, "sessions_closed": closed,
            "volatile_jobs_lost": lost, "process_executed": False, "persistent_session": True}


def re_session_name(name):
    return len(name) == 16 and all(char in "0123456789abcdef" for char in name)


class _Broker:
    def __init__(self, config, path):
        self.config, self.config_path = config, path
        self.socket_path = path.with_suffix(".sock")
        self.transport = GeminiNotebookTransport(config["repo_root"], config["env_overrides"])
        self.lock = asyncio.Lock()
        self.stop = asyncio.Event()
        self.last_activity = time.monotonic()
        self.context, self.session, self.discovery = None, None, None
        self.volatile_jobs = set()
        self.session_id = None

    async def reset(self):
        if self.context is not None:
            await self.context.__aexit__(None, None, None)
        self.context = self.session = self.discovery = None
        self.volatile_jobs.clear()
        self.session_id = None

    async def ready(self):
        if self.session is None:
            if _hash_file(Path(self.config["binary"])) != self.config["binary_sha256"]:
                raise ValueError("Executável mudou após configuração da sessão")
            self.context = self.transport._session(Path(self.config["binary"]))
            self.session = await self.context.__aenter__()
            self.discovery = await self.session.discover()
            self.session_id = uuid.uuid4().hex

    async def operation(self, payload):
        operation = payload.get("operation")
        if operation == "ping":
            return {"status": "completed", "fingerprint": self.config["fingerprint"]}
        if operation == "close":
            self.stop.set()
            return {"status": "pending", "session_closed": False, "volatile_jobs_lost": bool(self.volatile_jobs),
                    "process_executed": False}
        if operation not in {"call", "discover"}:
            raise _Blocked("Operação de broker desconhecida")
        timeout_seconds = _timeout(payload.get("timeout_seconds", 60))
        try:
            await asyncio.wait_for(self.lock.acquire(), timeout=timeout_seconds)
        except TimeoutError:
            return {"status": "blocked", "reason": "session_busy", "process_executed": False,
                    "session_reset": False, "volatile_jobs_lost": False}
        try:
            self.last_activity = time.monotonic()
            try:
                async with asyncio.timeout(timeout_seconds):
                    expected_session = payload.get("expected_session_id")
                    if expected_session is not None and (self.session is None or self.session_id != expected_session):
                        return {"status": "lost", "reason": "origin_session_restarted",
                                "volatile_jobs_lost": True, "process_executed": False}
                    await self.ready()
                    self.session.bytes_read = 0
                    if operation == "discover":
                        return {**self.discovery, "status": "completed", "process_executed": True,
                                "transport": "mcp_stdio", "remote_inference_executed": False,
                                "session_id": self.session_id, "retention_idle_seconds": self.config["idle_seconds"]}
                    name, arguments = payload.get("tool"), payload.get("arguments")
                    tools = {tool["name"]: tool for tool in self.discovery["tools"]}
                    if name not in tools or not isinstance(arguments, dict):
                        raise _Blocked("Operação não descoberta no servidor oficial")
                    _json_bytes(arguments)
                    schema = _strict_schema(tools[name]["inputSchema"])
                    try:
                        validator = jsonschema.validators.validator_for(schema)
                        validator.check_schema(schema)
                        validator(schema, format_checker=jsonschema.FormatChecker()).validate(arguments)
                    except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
                        raise _Blocked("Argumentos incompatíveis com inputSchema") from exc
                    result = await self.session.rpc("tools/call", {"name": name, "arguments": arguments})
                    classified = classify_tool_result(result)
                    if name == "notebook_query_start":
                        data = result.get("structuredContent", {})
                        if not data:
                            for item in result.get("content", []):
                                try:
                                    data = json.loads(item.get("text", ""))
                                except (ValueError, TypeError):
                                    continue
                                if isinstance(data, dict) and "query_id" in data:
                                    break
                        if isinstance(data, dict) and data.get("query_id"):
                            self.volatile_jobs.add(data["query_id"])
                    if name == "notebook_query_status" and classified["status"] in {"completed", "failed"}:
                        self.volatile_jobs.discard(arguments.get("query_id"))
                    return {**classified, "tool": name, "process_executed": True,
                            "transport": "mcp_stdio", "server": self.discovery["name"],
                            "server_version": self.discovery["version"],
                            "session_id": self.session_id, "retention_idle_seconds": self.config["idle_seconds"],
                            "response_sha256": hashlib.sha256(_json_bytes(result, OUTPUT_LIMIT)).hexdigest()}
            except _Blocked as exc:
                return {"status": "blocked", "reason": str(exc), "process_executed": self.session is not None}
            except Exception as exc:
                executed = self.session is not None
                lost = bool(self.volatile_jobs)
                await self.reset()
                return {"status": "failed", "reason": "timeout" if isinstance(exc, TimeoutError)
                        else "output_limit" if isinstance(exc, _OutputLimit) else sanitize_output(str(exc)),
                        "process_executed": executed, "session_reset": True, "volatile_jobs_lost": lost}
            finally:
                self.last_activity = time.monotonic()
        finally:
            self.lock.release()

    async def handle(self, reader, writer):
        try:
            peer = writer.get_extra_info("socket")
            _, uid, _ = struct.unpack("3i", peer.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            if uid != os.getuid():
                raise ValueError("Cliente de sessão não autorizado")
            async with asyncio.timeout(10):
                raw = await reader.readline()
            if len(raw) > INPUT_LIMIT:
                raise ValueError("Entrada de sessão excede limite")
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("Mensagem de sessão inválida")
            result = await self.operation(payload)
            writer.write(_json_bytes(result, OUTPUT_LIMIT) + b"\n")
            await writer.drain()
        except Exception:
            writer.write(b'{"status":"failed","reason":"invalid_session_request"}\n')
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def idle(self):
        while not self.stop.is_set():
            await asyncio.sleep(min(1, self.config["idle_seconds"] / 2))
            if not self.lock.locked() and time.monotonic() - self.last_activity > self.config["idle_seconds"]:
                self.stop.set()

    async def run(self):
        base = _private_directory(self.transport.repo_root)
        if self.config_path.parent != base or self.config_path.stem != self.config["fingerprint"][:16]:
            raise ValueError("Configuração de broker fora do workspace")
        _check_local_file(self.socket_path, socket_file=True)
        if self.socket_path.exists():
            raise ValueError("Socket existente não será substituído pelo broker")
        pid_path = self.config_path.with_suffix(".pid")
        _check_local_file(pid_path)
        pid_fd = os.open(pid_path, os.O_CREAT | os.O_TRUNC | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(pid_fd, "w") as stream:
            json.dump({"pid": os.getpid(), "fingerprint": self.config["fingerprint"]}, stream)
        fd, alias = _socket_alias(self.socket_path)
        idle = None
        try:
            server = await asyncio.start_unix_server(self.handle, path=alias, limit=INPUT_LIMIT)
            self.socket_path.chmod(0o600)
            idle = asyncio.create_task(self.idle())
            async with server:
                await self.stop.wait()
                async with self.lock:
                    await self.reset()
        finally:
            os.close(fd)
            if idle is not None:
                idle.cancel()
                await asyncio.gather(idle, return_exceptions=True)
            if self.socket_path.exists():
                _check_local_file(self.socket_path, socket_file=True)
                self.socket_path.unlink()
            if pid_path.exists():
                _check_local_file(pid_path)
                pid_path.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", required=True)
    arguments = parser.parse_args()
    path = Path(arguments.broker).absolute()
    _check_local_file(path)
    if path.stat().st_size > INPUT_LIMIT:
        raise ValueError("Configuração de sessão excede limite")
    config = json.loads(path.read_text())
    asyncio.run(_Broker(config, path).run())


if __name__ == "__main__":
    main()
