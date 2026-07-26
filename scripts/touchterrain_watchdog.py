#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TouchTerrain Watchdog — auto-recuperação de hangs (SPEC-935-R145/R212)
========================================================================
Mitigação operacional para o esgotamento de threads do TouchTerrain. O
watchdog consulta somente o endpoint leve e local ``/healthz`` e reinicia o
serviço após três falhas consecutivas.

O estado é persistido por substituição atômica e todo o ciclo é protegido por
um lock ``fcntl`` não bloqueante. Assim, execuções concorrentes do timer não
duplicam o restart. Um cooldown também limita novas tentativas, inclusive
quando a tentativa anterior de restart falha.

Uso compatível:
  python3 scripts/touchterrain_watchdog.py
  python3 scripts/touchterrain_watchdog.py --url http://localhost:8081/healthz \
      --service geomaker-touchterrain --timeout 10

Os caminhos de estado e lock podem ser injetados pela API ou pela CLI. Sem
dependências externas — apenas biblioteca padrão do Python.
"""

import argparse
import errno
import fcntl
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping


DEFAULT_URL = "http://127.0.0.1:8081/healthz"
DEFAULT_SERVICE = "geomaker-touchterrain"
DEFAULT_TIMEOUT = 10.0
DEFAULT_STATE_PATH = Path("/run/geomaker-touchterrain-watchdog/state.json")
DEFAULT_LOCK_PATH = Path("/run/geomaker-touchterrain-watchdog/watchdog.lock")
FAILURE_THRESHOLD = 3
RESTART_COOLDOWN_SECONDS = 15.0 * 60.0
STATE_VERSION = 1

PathValue = str | os.PathLike[str]


@dataclass(frozen=True, slots=True)
class WatchdogState:
    """Estado mínimo compartilhado entre execuções do timer."""

    failure_count: int = 0
    last_restart_at: float | None = None
    updated_at: float = 0.0


def check_health(url: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
    """Retorna ``True`` quando ``url`` responde com status HTTP menor que 500."""

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status < 500
    except urllib.error.HTTPError as error:
        # Uma resposta 4xx comprova liveness; somente 5xx indica indisponibilidade.
        return error.code < 500
    except Exception:
        return False


def restart_service(service_name: str) -> bool:
    """Executa ``systemctl restart`` sem elevação e traduz o código de saída."""

    try:
        result = subprocess.run(
            ["systemctl", "restart", service_name],
            timeout=60,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def log(message: str) -> None:
    """Registra uma mensagem curta no stderr, apropriada para o journal."""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[{timestamp}] touchterrain_watchdog: {message}",
        file=sys.stderr,
        flush=True,
    )


def _prepare_parent(path: Path) -> None:
    """Cria o diretório privado que conterá estado ou lock."""

    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)


@contextmanager
def _exclusive_lock(path: Path) -> Iterator[bool]:
    """Tenta adquirir um ``flock`` exclusivo sem bloquear outra execução."""

    _prepare_parent(path)
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    descriptor = os.open(path, flags, 0o600)
    acquired = False
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            acquired = True
        except OSError as error:
            if error.errno not in (errno.EACCES, errno.EAGAIN):
                raise

        yield acquired
    finally:
        if acquired:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _safe_state(now: float) -> WatchdogState:
    """Falha fechada por um cooldown quando um estado existente é inválido."""

    return WatchdogState(last_restart_at=now, updated_at=now)


def _load_state(path: Path, now: float) -> WatchdogState:
    """Lê e valida o estado; conteúdo corrompido nunca libera restart em rajada."""

    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return WatchdogState(updated_at=now)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        log(f"Estado inválido em {path}: {error}; cooldown de segurança aplicado.")
        return _safe_state(now)

    if not isinstance(payload, Mapping):
        log(f"Estado inválido em {path}: objeto JSON esperado; cooldown aplicado.")
        return _safe_state(now)

    raw_failure_count = payload.get("failure_count", 0)
    failure_count = (
        raw_failure_count
        if isinstance(raw_failure_count, int)
        and not isinstance(raw_failure_count, bool)
        and raw_failure_count >= 0
        else 0
    )

    raw_last_restart = payload.get("last_restart_at")
    last_restart_at = (
        float(raw_last_restart)
        if isinstance(raw_last_restart, (int, float))
        and not isinstance(raw_last_restart, bool)
        and math.isfinite(float(raw_last_restart))
        else None
    )
    if last_restart_at is not None and last_restart_at > now:
        # Recuos no relógio de parede não podem encerrar o cooldown cedo.
        last_restart_at = now

    return WatchdogState(
        failure_count=failure_count,
        last_restart_at=last_restart_at,
        updated_at=now,
    )


def _atomic_write_text(path: Path, content: str) -> None:
    """Grava no mesmo filesystem e publica o arquivo somente após ``fsync``."""

    _prepare_parent(path)
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

        directory_flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            directory_flags |= os.O_DIRECTORY
        directory_descriptor = os.open(path.parent, directory_flags)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def _persist_state(path: Path, state: WatchdogState) -> None:
    """Serializa o estado canônico como um objeto JSON compacto."""

    payload = {
        "version": STATE_VERSION,
        "failure_count": state.failure_count,
        "last_restart_at": state.last_restart_at,
        "updated_at": state.updated_at,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    _atomic_write_text(path, serialized)


def _cooldown_remaining(
    state: WatchdogState,
    now: float,
    cooldown_seconds: float,
) -> float:
    """Calcula o cooldown restante sem falhar aberto diante de recuo do relógio."""

    if state.last_restart_at is None:
        return 0.0
    elapsed = max(0.0, now - state.last_restart_at)
    return max(0.0, cooldown_seconds - elapsed)


def _run_locked(
    *,
    url: str,
    service: str,
    timeout: float,
    state_path: Path,
    failure_threshold: int,
    cooldown_seconds: float,
) -> bool:
    """Executa o ciclo enquanto o chamador mantém o lock interprocesso."""

    now = time.time()
    state = _load_state(state_path, now)

    if check_health(url, timeout=timeout):
        _persist_state(
            state_path,
            WatchdogState(
                failure_count=0,
                last_restart_at=state.last_restart_at,
                updated_at=now,
            ),
        )
        log(f"OK — {url} respondeu dentro de {timeout}s; contador zerado.")
        return True

    failure_count = min(state.failure_count + 1, failure_threshold)
    failed_state = WatchdogState(
        failure_count=failure_count,
        last_restart_at=state.last_restart_at,
        updated_at=now,
    )

    if failure_count < failure_threshold:
        _persist_state(state_path, failed_state)
        log(
            f"FALHA {failure_count}/{failure_threshold} — {url} não respondeu; "
            "restart ainda não permitido."
        )
        return True

    cooldown_remaining = _cooldown_remaining(
        failed_state,
        now,
        cooldown_seconds,
    )
    if cooldown_remaining > 0:
        _persist_state(state_path, failed_state)
        log(
            f"FALHA {failure_count}/{failure_threshold} — restart suprimido por "
            f"cooldown ({cooldown_remaining:.0f}s restantes)."
        )
        return True

    # Registra a tentativa antes do efeito externo. Se o processo cair após o
    # systemctl, a próxima execução ainda observará o cooldown e não duplicará.
    _persist_state(
        state_path,
        WatchdogState(
            failure_count=0,
            last_restart_at=now,
            updated_at=now,
        ),
    )
    log(
        f"FALHA {failure_count}/{failure_threshold} — {url} não respondeu; "
        f"reiniciando {service}..."
    )
    restarted = restart_service(service)
    if restarted:
        log(f"Serviço {service} reiniciado com sucesso.")
    else:
        log(f"ERRO ao reiniciar {service}; cooldown de segurança mantido.")
    return restarted


def run_once(
    url: str = DEFAULT_URL,
    service: str = DEFAULT_SERVICE,
    timeout: float = DEFAULT_TIMEOUT,
    state_path: PathValue = DEFAULT_STATE_PATH,
    lock_path: PathValue = DEFAULT_LOCK_PATH,
    *,
    failure_threshold: int = FAILURE_THRESHOLD,
    cooldown_seconds: float = RESTART_COOLDOWN_SECONDS,
) -> bool:
    """Executa um ciclo idempotente do watchdog.

    Retorna ``True`` quando o ciclo foi processado ou ignorado por lock/cooldown
    e ``False`` quando não foi possível manter o estado ou o restart falhou.
    """

    if failure_threshold <= 0:
        raise ValueError("failure_threshold deve ser positivo")
    if cooldown_seconds < 0 or not math.isfinite(cooldown_seconds):
        raise ValueError("cooldown_seconds deve ser finito e não negativo")

    resolved_state_path = Path(state_path)
    resolved_lock_path = Path(lock_path)
    try:
        with _exclusive_lock(resolved_lock_path) as acquired:
            if not acquired:
                log(f"Ciclo ignorado: lock já ocupado em {resolved_lock_path}.")
                return True
            return _run_locked(
                url=url,
                service=service,
                timeout=timeout,
                state_path=resolved_state_path,
                failure_threshold=failure_threshold,
                cooldown_seconds=cooldown_seconds,
            )
    except OSError as error:
        log(f"ERRO de estado/lock do watchdog: {error}.")
        return False


def _build_parser() -> argparse.ArgumentParser:
    """Constrói a CLI preservando as opções históricas."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--service", default=DEFAULT_SERVICE)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--lock-path", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument(
        "--failure-threshold",
        type=int,
        default=FAILURE_THRESHOLD,
    )
    parser.add_argument(
        "--cooldown-seconds",
        type=float,
        default=RESTART_COOLDOWN_SECONDS,
    )
    return parser


def main() -> int:
    """Executa a interface de linha de comando."""

    arguments = _build_parser().parse_args()
    succeeded = run_once(
        url=arguments.url,
        service=arguments.service,
        timeout=arguments.timeout,
        state_path=arguments.state_path,
        lock_path=arguments.lock_path,
        failure_threshold=arguments.failure_threshold,
        cooldown_seconds=arguments.cooldown_seconds,
    )
    return 0 if succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
