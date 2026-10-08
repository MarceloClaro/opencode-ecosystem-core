"""SPEC-935-R644: observações locais das CLIs; nunca guarda texto de tarefas.

O inventário lê metadados já observados sem iniciar uma CLI. SQLite mantém as
atualizações atômicas entre processos; falhas de disco degradam para memória.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import threading
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


class HarnessHealthStore:
    """Guarda apenas categoria, duração e instantes de execuções concluídas."""

    COOLDOWN_SECONDS = 120.0
    _ERRORS = {
        "authentication": "A CLI não confirmou autenticação válida.",
        "account_limit": "O provedor recusou a execução por limite ou saldo da conta.",
        "unavailable": "A CLI ou o serviço está temporariamente indisponível.",
        "timeout": "A CLI excedeu o tempo permitido para a tarefa.",
        "unsupported_arguments": "A CLI instalada não aceita os argumentos do executor.",
        "read_restrictions": "A CLI não conseguiu executar sob as restrições de leitura.",
        "invalid_output": "A CLI não confirmou resultado final válido.",
        "execution_failed": "A CLI não confirmou a conclusão da execução.",
    }
    _COOLDOWN_CATEGORIES = {"authentication", "account_limit", "unavailable", "timeout"}
    _SCHEMA = """CREATE TABLE IF NOT EXISTS harness_health (
        executor TEXT PRIMARY KEY,
        fingerprint TEXT NOT NULL,
        last_attempt REAL NOT NULL,
        last_success REAL,
        last_failure REAL,
        duration REAL NOT NULL,
        success INTEGER NOT NULL,
        error_category TEXT,
        cooldown_until REAL
    )"""

    def __init__(self, path: str | Path, clock: Callable[[], float] | None = None):
        self.path = Path(path)
        self._clock = clock or time.time
        self._memory: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _fingerprint(cli_path: str | None) -> str:
        if cli_path is None:
            return ""
        path = Path(cli_path)
        try:
            resolved = str(path.resolve())
            stat = path.stat()
            parts = [resolved, stat.st_mtime_ns, stat.st_size]
        except (OSError, RuntimeError):
            parts = [str(path.absolute()), None, None]
        return hashlib.sha256(json.dumps(parts).encode("utf-8")).hexdigest()

    def identity_for(self, cli_path: str) -> str:
        """Captura a identidade do binário antes de iniciar a execução."""
        return self._fingerprint(cli_path)

    @staticmethod
    def _timestamp(value: float | None) -> str | None:
        if value is None:
            return None
        try:
            return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")
        except (ValueError, OSError, OverflowError):
            return None

    def _connect(self, *, create: bool) -> sqlite3.Connection:
        # Um link na posição do banco não pode redirecionar a escrita local.
        if self.path.is_symlink():
            raise OSError("Banco de saúde não pode ser um link simbólico.")
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            try:
                descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                pass
            else:
                os.close(descriptor)
            connection = sqlite3.connect(str(self.path), timeout=1.0)
            try:
                connection.execute(self._SCHEMA)
            except sqlite3.Error:
                connection.close()
                raise
        else:
            connection = sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True, timeout=.25)
        connection.row_factory = sqlite3.Row
        return connection

    def _read(self, executor: str, fingerprint: str) -> dict[str, Any] | None:
        memory = self._memory.get(executor)
        if memory is not None and memory["fingerprint"] != fingerprint:
            memory = None
        disk = None
        if self.path.is_file():
            try:
                with closing(self._connect(create=False)) as connection:
                    row = connection.execute("SELECT * FROM harness_health WHERE executor=? AND fingerprint=?", (executor, fingerprint)).fetchone()
                    disk = dict(row) if row else None
                    if disk is not None:
                        disk["storage"] = "persistent"
            except (OSError, sqlite3.Error):
                pass
        if memory is not None and (disk is None or memory["last_attempt"] > disk["last_attempt"]):
            return memory.copy()
        return disk or (memory.copy() if memory is not None else None)

    def snapshot(self, executor: str, cli_path: str | None) -> dict[str, Any]:
        """Lê uma observação do mesmo binário, sem criar estado nem inferência."""
        empty = {
            "last_outcome": None, "last_attempt_at": None,
            "last_success_at": None, "last_failure_at": None,
            "duration_seconds": None, "error_category": None, "error": None,
            "cooldown_until": None, "cooldown_remaining_seconds": 0.0,
            "verification": "installation_only", "storage": "unobserved",
        }
        with self._lock:
            record = self._read(executor, self._fingerprint(cli_path))
            if record is None:
                return empty
            try:
                category = record.get("error_category")
                if category is not None and category not in self._ERRORS:
                    category = "execution_failed"
                successful = record["success"] == 1
                cooldown_until = record.get("cooldown_until")
                # Uma alteração no relógio não deve produzir bloqueio ilimitado.
                now = self._clock()
                remaining = min(self.COOLDOWN_SECONDS, max(0.0, float(cooldown_until or 0) - now)) if now >= record["last_attempt"] else 0.0
                duration = float(record["duration"])
                if not math.isfinite(duration) or duration < 0:
                    return empty
                return {
                    "last_outcome": "success" if successful else "failure",
                    "last_attempt_at": self._timestamp(record["last_attempt"]),
                    "last_success_at": self._timestamp(record.get("last_success")),
                    "last_failure_at": self._timestamp(record.get("last_failure")),
                    "duration_seconds": duration,
                    "error_category": category,
                    "error": self._ERRORS.get(category),
                    "cooldown_until": self._timestamp(cooldown_until),
                    "cooldown_remaining_seconds": remaining,
                    "verification": "execution_succeeded" if successful else "execution_failed",
                    "storage": record["storage"],
                }
            except (TypeError, ValueError, KeyError):
                return empty

    def record(self, executor: str, cli_path: str, *, success: bool,
               duration_seconds: float, error_category: str | None = None,
               observed_identity: str | None = None) -> None:
        """Transação curta por resultado; nenhum prompt/retorno é aceito aqui."""
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", executor):
            return
        duration = float(duration_seconds)
        if not math.isfinite(duration) or duration < 0:
            duration = 0.0
        now = self._clock()
        fingerprint = observed_identity if isinstance(observed_identity, str) and re.fullmatch(r"[0-9a-f]{64}", observed_identity) else self._fingerprint(cli_path)
        category = None if success else error_category if error_category in self._ERRORS else "execution_failed"
        cooldown = now + self.COOLDOWN_SECONDS if category in self._COOLDOWN_CATEGORIES else None
        with self._lock:
            previous = self._read(executor, fingerprint) or {}
            row = {
                "executor": executor, "fingerprint": fingerprint, "last_attempt": now,
                "last_success": now if success else previous.get("last_success"),
                "last_failure": previous.get("last_failure") if success else now,
                "duration": duration, "success": int(bool(success)),
                "error_category": category, "cooldown_until": cooldown,
                "storage": "memory",
            }
            self._memory[executor] = row
            try:
                with closing(self._connect(create=True)) as connection, connection:
                    # BEGIN IMMEDIATE serializa o read/modify/write entre instâncias.
                    connection.execute("BEGIN IMMEDIATE")
                    persisted = connection.execute("SELECT * FROM harness_health WHERE executor=? AND fingerprint=?", (executor, fingerprint)).fetchone()
                    if persisted:
                        for key in ("last_success", "last_failure"):
                            known = [value for value in (persisted[key], row[key]) if value is not None]
                            row[key] = max(known) if known else None
                        # Um escritor atrasado preserva a execução mais recente,
                        # mas ainda contribui seu instante de sucesso/falha.
                        if persisted["last_attempt"] > row["last_attempt"]:
                            for key in ("last_attempt", "duration", "success", "error_category", "cooldown_until"):
                                row[key] = persisted[key]
                    values = tuple(row[key] for key in ("executor", "fingerprint", "last_attempt", "last_success", "last_failure", "duration", "success", "error_category", "cooldown_until"))
                    connection.execute("""INSERT INTO harness_health VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(executor) DO UPDATE SET
                        fingerprint=excluded.fingerprint, last_attempt=excluded.last_attempt,
                        last_success=excluded.last_success, last_failure=excluded.last_failure,
                        duration=excluded.duration, success=excluded.success,
                        error_category=excluded.error_category, cooldown_until=excluded.cooldown_until
                        WHERE excluded.last_attempt >= harness_health.last_attempt""", values)
                row["storage"] = "persistent"
            except (OSError, sqlite3.Error):
                # Resultado real preservado mesmo com disco cheio, bloqueado ou inválido.
                pass
