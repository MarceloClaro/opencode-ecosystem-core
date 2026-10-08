"""Create and migrate the daemon-owned SQLite registry database."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any

from alembic import command
from alembic.config import Config
from filelock import FileLock, Timeout
from sqlalchemy import create_engine, event
from sqlalchemy.pool import NullPool

from .paths import prepare_registry_path, registry_path

MIGRATIONS_DIR = Path(__file__).with_name("migrations")
MIGRATION_LOCK_TIMEOUT_SECONDS = 30.0


class RegistryDatabase:
    """One SQLAlchemy engine for one registry path."""

    def __init__(self, path: Path) -> None:
        self.path = prepare_registry_path(path)
        self.engine = create_engine(
            f"sqlite+pysqlite:///{self.path}",
            poolclass=NullPool,
            connect_args={"timeout": 5.0},
        )
        event.listen(self.engine, "connect", _configure_connection)
        with _migration_lock(self.path):
            self._upgrade()
            self._check()
        _protect_database_files(self.path)

    def _upgrade(self) -> None:
        config = Config()
        config.set_main_option("script_location", str(MIGRATIONS_DIR))
        with self.engine.connect() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")

    def _check(self) -> None:
        with self.engine.connect() as connection:
            result = connection.exec_driver_sql("PRAGMA quick_check").scalar_one()
        if result != "ok":
            raise RuntimeError(f"registry integrity check failed: {result}")


@lru_cache(maxsize=None)
def database_for_path(path: str) -> RegistryDatabase:
    return RegistryDatabase(Path(path))


def default_database() -> RegistryDatabase:
    return database_for_path(str(registry_path()))


@contextmanager
def _migration_lock(
    path: Path,
    *,
    timeout_seconds: float = MIGRATION_LOCK_TIMEOUT_SECONDS,
) -> Iterator[None]:
    lock_path = Path(f"{path}.migrate.lock")
    lock = FileLock(
        lock_path,
        timeout=timeout_seconds,
        mode=0o600,
        preserve_lock_file=True,
    )
    try:
        lock.acquire()
    except Timeout:
        raise RuntimeError(f"timed out waiting for registry migration lock: {lock_path}") from None
    try:
        yield
    finally:
        lock.release()


def _configure_connection(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA busy_timeout = 5000")
        cursor.execute("PRAGMA foreign_keys = ON")
        mode = cursor.execute("PRAGMA journal_mode = WAL").fetchone()[0]
        if str(mode).lower() != "wal":
            raise RuntimeError(f"SQLite did not enable WAL mode: {mode}")
        cursor.execute("PRAGMA synchronous = FULL")
        cursor.execute("PRAGMA trusted_schema = OFF")
    finally:
        cursor.close()


def _protect_database_files(path: Path) -> None:
    for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
        try:
            if candidate.exists():
                os.chmod(candidate, 0o600)
        except FileNotFoundError:
            if candidate == path:
                raise
