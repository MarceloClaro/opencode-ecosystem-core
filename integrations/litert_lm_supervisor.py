# -*- coding: utf-8 -*-
"""Supervisor canônico e hermético do daemon local LiteRT-LM.

O módulo concentra o ciclo de vida do processo em um único ponto. Importá-lo
não cria diretórios, não abre sockets e não inicia processos; qualquer efeito
operacional exige uma chamada explícita a ``status``, ``ensure``, ``wait`` ou
``stop``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any, Iterator
from urllib import request as urllib_request

import fcntl


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LITERT_HOST = "127.0.0.1"
LITERT_PORT = 9379
LITERT_COMMAND = (
    "litert-lm",
    "serve",
    "--host",
    LITERT_HOST,
    "--port",
    str(LITERT_PORT),
)

_STATE_VERSION = 1
_SENSITIVE_ENV_NAME = re.compile(
    r"(?:^|_)(?:KEY|TOKEN|SECRET)(?:_|$)",
    re.IGNORECASE,
)
_ALLOWED_CHILD_ENVIRONMENT = frozenset(
    {
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "PATH",
        "TMPDIR",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_RUNTIME_DIR",
        "LITERT_LM_MODELS_DIR",
        "LITERT_LM_CONTEXT_TOKENS",
        "LITERT_LM_MAX_TOKENS",
    }
)

_THREAD_LOCKS_GUARD = threading.Lock()
_THREAD_LOCKS: dict[str, threading.RLock] = {}
_PROCESS_REGISTRY_GUARD = threading.Lock()
_PROCESS_REGISTRY: dict[tuple[str, int], Any] = {}


def _default_runtime_dir() -> Path:
    """Seleciona um diretório privado sem depender de configuração do daemon."""

    configured = os.environ.get("XDG_RUNTIME_DIR", "").strip()
    if configured and Path(configured).is_absolute():
        return Path(configured) / "opencode" / "litert-lm"
    user_id = os.getuid() if hasattr(os, "getuid") else 0
    return Path(tempfile.gettempdir()) / f"opencode-litert-lm-{user_id}"


class SupervisorState(str, Enum):
    """Estados fechados publicados pela API e pela CLI."""

    OFFLINE = "offline"
    STARTING = "starting"
    READY = "ready"
    CIRCUIT_OPEN = "circuit_open"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class SupervisorConfig:
    """Limites do supervisor; host, porta e comando não são configuráveis."""

    runtime_dir: Path = field(default_factory=_default_runtime_dir)
    startup_timeout_seconds: float = 300.0
    poll_interval_seconds: float = 1.0
    failure_threshold: int = 3
    circuit_open_seconds: float = 15.0 * 60.0
    termination_timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "runtime_dir", Path(self.runtime_dir))
        if self.startup_timeout_seconds <= 0:
            raise ValueError("startup_timeout_seconds deve ser positivo")
        if self.poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds deve ser positivo")
        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold deve ser positivo")
        if self.circuit_open_seconds <= 0:
            raise ValueError("circuit_open_seconds deve ser positivo")
        if self.termination_timeout_seconds <= 0:
            raise ValueError("termination_timeout_seconds deve ser positivo")

    @property
    def lock_path(self) -> Path:
        return self.runtime_dir / "supervisor.lock"

    @property
    def state_path(self) -> Path:
        return self.runtime_dir / "state.json"

    @property
    def pid_path(self) -> Path:
        return self.runtime_dir / "litert-lm.pid"

    @property
    def log_path(self) -> Path:
        return self.runtime_dir / "litert-lm.log"


@dataclass(frozen=True, slots=True)
class SupervisorStatus:
    """Envelope estruturado e serializável retornado pelo lifecycle."""

    state: SupervisorState
    ready: bool
    pid: int | None
    host: str
    port: int
    failure_count: int
    circuit_open_until: float | None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["state"] = self.state.value
        return payload


@dataclass(frozen=True, slots=True)
class _PersistedState:
    state: SupervisorState = SupervisorState.OFFLINE
    ready: bool = False
    pid: int | None = None
    failure_count: int = 0
    circuit_open_until: float | None = None
    updated_at: float = 0.0

    def public(self) -> SupervisorStatus:
        return SupervisorStatus(
            state=self.state,
            ready=self.ready,
            pid=self.pid,
            host=LITERT_HOST,
            port=LITERT_PORT,
            failure_count=self.failure_count,
            circuit_open_until=self.circuit_open_until,
        )


def _thread_lock_for(path: Path) -> threading.RLock:
    key = str(path.resolve(strict=False))
    with _THREAD_LOCKS_GUARD:
        return _THREAD_LOCKS.setdefault(key, threading.RLock())


def _atomic_write_text(path: Path, content: str) -> None:
    """Substitui um arquivo no mesmo filesystem após flush e fsync."""

    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def _default_readiness_probe() -> bool:
    """Consulta somente o endpoint fixo de loopback e valida seu envelope."""

    endpoint = f"http://{LITERT_HOST}:{LITERT_PORT}/v1/models"
    try:
        with urllib_request.urlopen(endpoint, timeout=0.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return isinstance(payload, Mapping) and isinstance(payload.get("data"), list)
    except Exception:
        return False


def _default_pid_is_alive(pid: int) -> bool:
    """Valida um PID positivo sem enviar sinal destrutivo."""

    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


class LiteRTSupervisor:
    """Coordena uma única instância do daemon entre threads e processos."""

    def __init__(
        self,
        config: SupervisorConfig | None = None,
        *,
        process_factory: Callable[..., Any] = subprocess.Popen,
        readiness_probe: Callable[..., bool] = _default_readiness_probe,
        pid_is_alive: Callable[[int], bool] = _default_pid_is_alive,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config or SupervisorConfig()
        self._process_factory = process_factory
        self._readiness_probe = readiness_probe
        self._pid_is_alive = pid_is_alive
        self._clock = clock
        self._sleeper = sleeper
        self._owned_process: Any | None = None

    def _prepare_runtime_dir(self) -> None:
        runtime_dir = self.config.runtime_dir
        if runtime_dir.is_symlink():
            raise RuntimeError("runtime_dir não pode ser um link simbólico")
        runtime_dir.mkdir(mode=0o700, parents=True, exist_ok=True)

    @contextmanager
    def _lifecycle_lock(self) -> Iterator[None]:
        """Combina RLock por caminho e flock exclusivo interprocesso."""

        self._prepare_runtime_dir()
        thread_lock = _thread_lock_for(self.config.lock_path)
        with thread_lock:
            flags = os.O_CREAT | os.O_RDWR
            if hasattr(os, "O_CLOEXEC"):
                flags |= os.O_CLOEXEC
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(self.config.lock_path, flags, 0o600)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX)
                yield
            finally:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
                os.close(descriptor)

    def _load_state_locked(self) -> _PersistedState:
        path = self.config.state_path
        if not path.exists():
            return self._state_from_pid_file()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                raise ValueError("state.json não contém um objeto")
            raw_pid = payload.get("pid")
            pid = (
                raw_pid
                if isinstance(raw_pid, int) and not isinstance(raw_pid, bool) and raw_pid > 0
                else None
            )
            raw_failure_count = payload.get("failure_count", 0)
            failure_count = (
                raw_failure_count
                if isinstance(raw_failure_count, int)
                and not isinstance(raw_failure_count, bool)
                and raw_failure_count >= 0
                else 0
            )
            raw_open_until = payload.get("circuit_open_until")
            circuit_open_until = (
                float(raw_open_until)
                if isinstance(raw_open_until, (int, float))
                and not isinstance(raw_open_until, bool)
                else None
            )
            return _PersistedState(
                state=SupervisorState(str(payload.get("state", "offline"))),
                ready=bool(payload.get("ready", False)),
                pid=pid,
                failure_count=failure_count,
                circuit_open_until=circuit_open_until,
                updated_at=float(payload.get("updated_at", 0.0)),
            )
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            return _PersistedState(
                state=SupervisorState.UNAVAILABLE,
                updated_at=self._clock(),
            )

    def _state_from_pid_file(self) -> _PersistedState:
        try:
            raw_pid = int(self.config.pid_path.read_text(encoding="utf-8").strip())
        except (FileNotFoundError, OSError, TypeError, ValueError):
            return _PersistedState(updated_at=self._clock())
        if raw_pid <= 0:
            return _PersistedState(updated_at=self._clock())
        return _PersistedState(
            state=SupervisorState.STARTING,
            pid=raw_pid,
            updated_at=self._clock(),
        )

    def _persist_state_locked(self, state: _PersistedState) -> None:
        payload = {
            "version": _STATE_VERSION,
            "state": state.state.value,
            "ready": state.ready,
            "pid": state.pid,
            "host": LITERT_HOST,
            "port": LITERT_PORT,
            "failure_count": state.failure_count,
            "circuit_open_until": state.circuit_open_until,
            "updated_at": state.updated_at,
        }
        if state.pid is not None:
            _atomic_write_text(self.config.pid_path, f"{state.pid}\n")
            _atomic_write_text(
                self.config.state_path,
                json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
            )
            return

        _atomic_write_text(
            self.config.state_path,
            json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        )
        try:
            self.config.pid_path.unlink()
        except FileNotFoundError:
            pass

    def _probe_ready(self) -> bool:
        try:
            return bool(self._readiness_probe())
        except Exception:
            return False

    def _pid_alive(self, pid: int | None) -> bool:
        if pid is None:
            return False
        process = self._registered_process(pid)
        if process is not None:
            try:
                return process.poll() is None
            except Exception:
                pass
        try:
            return bool(self._pid_is_alive(pid))
        except Exception:
            return False

    def _record_failure_locked(self, state: _PersistedState) -> _PersistedState:
        failure_count = state.failure_count + 1
        now = self._clock()
        if failure_count >= self.config.failure_threshold:
            failed = _PersistedState(
                state=SupervisorState.CIRCUIT_OPEN,
                ready=False,
                pid=None,
                failure_count=failure_count,
                circuit_open_until=now + self.config.circuit_open_seconds,
                updated_at=now,
            )
        else:
            failed = _PersistedState(
                state=SupervisorState.UNAVAILABLE,
                ready=False,
                pid=None,
                failure_count=failure_count,
                circuit_open_until=None,
                updated_at=now,
            )
        self._persist_state_locked(failed)
        return failed

    def _reconcile_locked(self) -> _PersistedState:
        state = self._load_state_locked()
        now = self._clock()

        if self._probe_ready():
            live_pid = state.pid if self._pid_alive(state.pid) else None
            ready = _PersistedState(
                state=SupervisorState.READY,
                ready=True,
                pid=live_pid,
                failure_count=0,
                circuit_open_until=None,
                updated_at=now,
            )
            if ready != state:
                self._persist_state_locked(ready)
            return ready

        if state.circuit_open_until is not None:
            if now < state.circuit_open_until:
                circuit = replace(
                    state,
                    state=SupervisorState.CIRCUIT_OPEN,
                    ready=False,
                    pid=None,
                )
                if circuit != state:
                    self._persist_state_locked(circuit)
                return circuit
            state = replace(
                state,
                state=SupervisorState.UNAVAILABLE,
                ready=False,
                pid=None,
                circuit_open_until=None,
                updated_at=now,
            )
            self._persist_state_locked(state)

        if state.pid is not None:
            if self._pid_alive(state.pid):
                starting = replace(
                    state,
                    state=SupervisorState.STARTING,
                    ready=False,
                    updated_at=state.updated_at or now,
                )
                if starting != state:
                    self._persist_state_locked(starting)
                return starting
            return self._record_failure_locked(state)

        expected_state = (
            SupervisorState.UNAVAILABLE
            if state.state is SupervisorState.UNAVAILABLE
            else SupervisorState.OFFLINE
        )
        offline = replace(
            state,
            state=expected_state,
            ready=False,
            pid=None,
            circuit_open_until=None,
        )
        if offline != state:
            self._persist_state_locked(offline)
        return offline

    @staticmethod
    def _child_environment() -> dict[str, str]:
        environment: dict[str, str] = {}
        for name in _ALLOWED_CHILD_ENVIRONMENT:
            value = os.environ.get(name)
            if value is None or _SENSITIVE_ENV_NAME.search(name):
                continue
            environment[name] = value
        environment.setdefault("PATH", os.defpath)
        environment.setdefault("LITERT_LM_CONTEXT_TOKENS", "20480")
        environment.setdefault("LITERT_LM_MAX_TOKENS", "20480")
        return environment

    def _register_process(self, process: Any, pid: int) -> None:
        key = (str(self.config.state_path.resolve(strict=False)), pid)
        with _PROCESS_REGISTRY_GUARD:
            _PROCESS_REGISTRY[key] = process
        self._owned_process = process

    def _registered_process(self, pid: int | None) -> Any | None:
        if pid is None:
            return None
        key = (str(self.config.state_path.resolve(strict=False)), pid)
        with _PROCESS_REGISTRY_GUARD:
            return _PROCESS_REGISTRY.get(key)

    def _unregister_process(self, pid: int | None) -> None:
        if pid is None:
            return
        key = (str(self.config.state_path.resolve(strict=False)), pid)
        with _PROCESS_REGISTRY_GUARD:
            _PROCESS_REGISTRY.pop(key, None)
        owned_pid = getattr(self._owned_process, "pid", None)
        if owned_pid == pid:
            self._owned_process = None

    def _spawn_locked(self, previous: _PersistedState) -> _PersistedState:
        process: Any | None = None
        # stdout/stderr do filho iam para DEVNULL: quando o litert-lm real
        # morre logo após o spawn (ex.: "Address already in use" por uma
        # porta ocupada por um processo travado/órfão de uma sessão
        # anterior), esse diagnóstico era descartado -- o supervisor só via
        # "processo morreu, falha N", sem nenhuma pista da causa real.
        # Redireciona para um arquivo real no runtime_dir (append, para não
        # truncar diagnósticos de tentativas anteriores na mesma sessão).
        log_file = open(self.config.log_path, "ab")
        try:
            try:
                process = self._process_factory(
                    list(LITERT_COMMAND),
                    cwd=str(PROJECT_ROOT),
                    env=self._child_environment(),
                    stdin=subprocess.DEVNULL,
                    stdout=log_file,
                    stderr=log_file,
                    shell=False,
                    close_fds=True,
                    start_new_session=True,
                )
                pid = getattr(process, "pid", None)
                if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
                    raise RuntimeError("process_factory retornou PID inválido")
                self._register_process(process, pid)
                starting = _PersistedState(
                    state=SupervisorState.STARTING,
                    ready=False,
                    pid=pid,
                    failure_count=previous.failure_count,
                    circuit_open_until=None,
                    updated_at=self._clock(),
                )
                self._persist_state_locked(starting)
                return starting
            except Exception:
                if process is not None:
                    self._terminate_process(process)
                return self._record_failure_locked(previous)
        finally:
            # O filho herdou seu próprio descritor via close_fds/duplicação
            # do subprocess; a cópia do pai pode (e deve) ser fechada aqui
            # sem afetar a escrita contínua do processo filho no arquivo.
            log_file.close()

    def status(self) -> SupervisorStatus:
        """Reconcilia readiness, PID e circuito sem iniciar um processo."""

        with self._lifecycle_lock():
            return self._reconcile_locked().public()

    def ensure(self, *, non_blocking: bool = False) -> SupervisorStatus:
        """Solicita uma única inicialização e opcionalmente aguarda readiness."""

        with self._lifecycle_lock():
            state = self._reconcile_locked()
            if state.state in {SupervisorState.READY, SupervisorState.CIRCUIT_OPEN}:
                return state.public()
            if state.pid is None:
                state = self._spawn_locked(state)
            result = state.public()

        if non_blocking or result.state is not SupervisorState.STARTING:
            return result
        return self.wait(timeout_seconds=self.config.startup_timeout_seconds)

    def wait(self, timeout_seconds: float | None = None) -> SupervisorStatus:
        """Aguarda readiness e limpa o processo conhecido quando há timeout."""

        timeout = (
            self.config.startup_timeout_seconds
            if timeout_seconds is None
            else float(timeout_seconds)
        )
        if timeout < 0:
            raise ValueError("timeout_seconds não pode ser negativo")
        deadline = self._clock() + timeout
        last_status = self.status()

        while True:
            if last_status.ready or last_status.state is SupervisorState.CIRCUIT_OPEN:
                return last_status
            if last_status.pid is None:
                return last_status

            process = self._registered_process(last_status.pid)
            if process is not None:
                try:
                    return_code = process.poll()
                except Exception:
                    return_code = None
                if return_code is not None:
                    return self._finish_failed_process(last_status.pid)

            remaining = deadline - self._clock()
            if remaining <= 0:
                return self._cleanup_timeout(last_status.pid)
            self._sleeper(min(self.config.poll_interval_seconds, remaining))
            last_status = self.status()

    def _finish_failed_process(self, pid: int) -> SupervisorStatus:
        self._unregister_process(pid)
        with self._lifecycle_lock():
            state = self._load_state_locked()
            if state.pid != pid:
                return self._reconcile_locked().public()
            return self._record_failure_locked(state).public()

    def _terminate_process(self, process: Any) -> None:
        try:
            if process.poll() is not None:
                return
        except Exception:
            pass
        try:
            process.terminate()
        except (OSError, ProcessLookupError):
            return
        try:
            process.wait(timeout=self.config.termination_timeout_seconds)
            return
        except subprocess.TimeoutExpired:
            pass
        except (OSError, ProcessLookupError):
            return
        try:
            process.kill()
        except (OSError, ProcessLookupError):
            return
        try:
            process.wait(timeout=self.config.termination_timeout_seconds)
        except (OSError, ProcessLookupError, subprocess.TimeoutExpired):
            pass

    def _terminate_pid(self, pid: int) -> None:
        if not self._pid_alive(pid):
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except (OSError, ProcessLookupError):
            return
        deadline = self._clock() + self.config.termination_timeout_seconds
        while self._pid_alive(pid) and self._clock() < deadline:
            self._sleeper(
                min(self.config.poll_interval_seconds, deadline - self._clock())
            )
        if self._pid_alive(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                pass

    def _cleanup_timeout(self, pid: int) -> SupervisorStatus:
        process = self._registered_process(pid)
        if process is not None:
            self._terminate_process(process)
        else:
            self._terminate_pid(pid)
        self._unregister_process(pid)
        with self._lifecycle_lock():
            state = self._load_state_locked()
            if state.pid != pid:
                return self._reconcile_locked().public()
            return self._record_failure_locked(state).public()

    def stop(self) -> SupervisorStatus:
        """Encerra somente o PID conhecido e limpa PID/circuito persistidos."""

        with self._lifecycle_lock():
            state = self._load_state_locked()
            pid = state.pid if self._pid_alive(state.pid) else None
            if pid is not None:
                process = self._registered_process(pid)
                if process is not None:
                    self._terminate_process(process)
                else:
                    self._terminate_pid(pid)
                self._unregister_process(pid)
            stopped = _PersistedState(
                state=SupervisorState.OFFLINE,
                ready=False,
                pid=None,
                failure_count=0,
                circuit_open_until=None,
                updated_at=self._clock(),
            )
            self._persist_state_locked(stopped)
            return stopped.public()


def _status_payload(value: object) -> dict[str, Any]:
    if isinstance(value, SupervisorStatus):
        return value.to_dict()
    if isinstance(value, Mapping):
        payload = dict(value)
    elif hasattr(value, "_asdict"):
        payload = dict(value._asdict())
    else:
        payload = asdict(value) if hasattr(value, "__dataclass_fields__") else {}
    state = payload.get("state")
    if isinstance(state, Enum):
        payload["state"] = state.value
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="litert-lm-supervisor")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("status", "wait", "stop"):
        subparser = commands.add_parser(command)
        subparser.add_argument("--json", action="store_true", dest="as_json")
    ensure_parser = commands.add_parser("ensure")
    ensure_parser.add_argument("--non-blocking", action="store_true")
    ensure_parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Executa a CLI sem iniciar o daemon fora de um comando explícito."""

    arguments = _build_parser().parse_args(argv)
    supervisor = LiteRTSupervisor()
    if arguments.command == "status":
        result = supervisor.status()
    elif arguments.command == "ensure":
        result = supervisor.ensure(non_blocking=bool(arguments.non_blocking))
    elif arguments.command == "wait":
        result = supervisor.wait()
    else:
        result = supervisor.stop()
    print(json.dumps(_status_payload(result), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
