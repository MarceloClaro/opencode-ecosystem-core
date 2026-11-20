"""Persistência transacional SQLite do MetaBus (SPEC-935-R1246)."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = 1
MAX_EPISODES = 1000
MAX_LEGACY_MEMORY_BYTES = 64 * 1024 * 1024
MAX_LEGACY_EVENT_LINE_BYTES = 8 * 1024 * 1024
SQLITE_BUSY_TIMEOUT_MS = 5000


class MetaBusPersistenceError(RuntimeError):
    """Erro explícito de leitura, migração ou persistência do MetaBus."""


def _reject_constant(value: str):
    raise ValueError(f"constante JSON inválida: {value}")


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def _json_load(value: str | bytes) -> Any:
    return json.loads(value, parse_constant=_reject_constant)


def _entry_columns(entry: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    ident = entry.get("id")
    stamp = entry.get("timestamp")
    agent = entry.get("agent_id")
    return (
        ident if isinstance(ident, str) else None,
        stamp if isinstance(stamp, str) else None,
        agent if isinstance(agent, str) else None,
    )


class MetaBusSQLiteStore:
    """Store SQLite pequeno, sem conexões persistentes entre chamadas.

    Cada operação abre uma conexão curta e usa transação própria. WAL e
    ``busy_timeout`` serializam writers multiprocesso sem compartilhar handles.
    """

    def __init__(
        self,
        path: str | os.PathLike[str],
        *,
        legacy_memory_path: str | os.PathLike[str] | None = None,
        legacy_events_path: str | os.PathLike[str] | None = None,
    ):
        self.path = Path(path).expanduser().resolve()
        self.legacy_memory_path = (
            Path(legacy_memory_path).expanduser().resolve()
            if legacy_memory_path is not None else None
        )
        self.legacy_events_path = (
            Path(legacy_events_path).expanduser().resolve()
            if legacy_events_path is not None else None
        )
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            str(self.path), timeout=SQLITE_BUSY_TIMEOUT_MS / 1000,
            isolation_level=None,
        )
        try:
            connection.row_factory = sqlite3.Row
            connection.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA case_sensitive_like=ON")
            yield connection
        finally:
            connection.close()

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        statements = (
            "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
            """CREATE TABLE IF NOT EXISTS episodes (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT,
                created_at TEXT,
                agent_id TEXT,
                entry_type TEXT,
                entry_json TEXT NOT NULL
            )""",
            "CREATE INDEX IF NOT EXISTS idx_episodes_seq ON episodes(seq)",
            "CREATE INDEX IF NOT EXISTS idx_episodes_agent_seq ON episodes(agent_id, seq)",
            "CREATE INDEX IF NOT EXISTS idx_episodes_type_seq ON episodes(entry_type, seq)",
            """CREATE TABLE IF NOT EXISTS semantic_topics (
                topic TEXT PRIMARY KEY,
                data_json TEXT NOT NULL,
                updated_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS confidence_ledger (
                topic TEXT PRIMARY KEY,
                value_json TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                timestamp_json TEXT,
                topic TEXT,
                source TEXT,
                event_json TEXT NOT NULL
            )""",
            "CREATE INDEX IF NOT EXISTS idx_events_topic_seq ON events(topic, seq)",
            "CREATE INDEX IF NOT EXISTS idx_events_source_seq ON events(source, seq)",
            "CREATE INDEX IF NOT EXISTS idx_events_seq ON events(seq)",
            """CREATE TABLE IF NOT EXISTS migration_quarantine (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                raw_sha256 TEXT NOT NULL,
                raw_line BLOB NOT NULL,
                reason TEXT NOT NULL
            )""",
        )
        for statement in statements:
            connection.execute(statement)

    def _initialize(self) -> None:
        try:
            with self._connection() as connection:
                try:
                    mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
                    if str(mode).lower() != "wal":
                        raise MetaBusPersistenceError("sqlite_wal_unavailable")
                    connection.execute("BEGIN IMMEDIATE")
                    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
                    if version > SCHEMA_VERSION:
                        raise MetaBusPersistenceError("metabus_schema_newer_than_runtime")
                    self._create_schema(connection)
                    migrated = connection.execute(
                        "SELECT value FROM meta WHERE key='legacy_import_v1'"
                    ).fetchone()
                    if migrated is None:
                        report = self._import_legacy(connection)
                        connection.execute(
                            "INSERT INTO meta(key, value) VALUES('legacy_import_v1', ?)",
                            (_json_dump(report),),
                        )
                    connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
                    connection.commit()
                except BaseException:
                    # Schema, version, imported records and migration marker
                    # all share one transaction; failed migration rolls back.
                    if connection.in_transaction:
                        connection.rollback()
                    raise
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
        except MetaBusPersistenceError:
            raise
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_sqlite_initialization_failed") from exc

    def _legacy_memory(self) -> tuple[dict[str, Any], str | None]:
        path = self.legacy_memory_path
        if path is None or not path.is_file():
            return {"episodic": [], "semantic": {}, "confidence_ledger": {}}, None
        try:
            if path.stat().st_size > MAX_LEGACY_MEMORY_BYTES:
                raise ValueError("legacy_memory_size_limit")
            raw = path.read_bytes()
            data = _json_load(raw)
            if not isinstance(data, dict):
                raise ValueError("legacy_memory_root_must_be_object")
            episodic = data.get("episodic", [])
            semantic = data.get("semantic", {})
            confidence = data.get("confidence_ledger", {})
            if (
                not isinstance(episodic, list)
                or any(not isinstance(item, dict) for item in episodic)
                or not isinstance(semantic, dict)
                or not isinstance(confidence, dict)
            ):
                raise ValueError("legacy_memory_shape_invalid")
            # Validate serialization before starting inserts; no NaN/Infinity
            # may become an invalid SQLite JSON payload.
            for item in episodic:
                _json_dump(item)
            for item in semantic.values():
                _json_dump(item)
            for item in confidence.values():
                _json_dump(item)
            return {
                "episodic": episodic,
                "semantic": semantic,
                "confidence_ledger": confidence,
            }, hashlib.sha256(raw).hexdigest()
        except Exception as exc:
            raise MetaBusPersistenceError("legacy_memory_corrupt") from exc

    @staticmethod
    def _insert_episode(connection: sqlite3.Connection, entry: dict[str, Any]) -> None:
        entry_id, created_at, agent_id = _entry_columns(entry)
        entry_type = entry.get("type")
        if not isinstance(entry_type, str):
            entry_type = None
        connection.execute(
            "INSERT INTO episodes(entry_id, created_at, agent_id, entry_type, entry_json) "
            "VALUES(?, ?, ?, ?, ?)",
            (entry_id, created_at, agent_id, entry_type, _json_dump(entry)),
        )

    @staticmethod
    def _insert_event(connection: sqlite3.Connection, event: dict[str, Any]) -> None:
        event_id = event.get("event_id")
        topic = event.get("topic")
        source = event.get("source")
        timestamp = event.get("timestamp")
        connection.execute(
            "INSERT INTO events(event_id, timestamp_json, topic, source, event_json) "
            "VALUES(?, ?, ?, ?, ?)",
            (
                event_id if isinstance(event_id, str) else None,
                _json_dump(timestamp) if "timestamp" in event else None,
                topic if isinstance(topic, str) else None,
                source if isinstance(source, str) else None,
                _json_dump(event),
            ),
        )

    @staticmethod
    def _quarantine(
        connection: sqlite3.Connection, source_name: str, line_number: int,
        raw_line: bytes, reason: str,
    ) -> None:
        connection.execute(
            "INSERT INTO migration_quarantine(source_name, line_number, raw_sha256, raw_line, reason) "
            "VALUES(?, ?, ?, ?, ?)",
            (source_name, line_number, hashlib.sha256(raw_line).hexdigest(), raw_line, reason),
        )

    def _import_legacy(self, connection: sqlite3.Connection) -> dict[str, Any]:
        memory, memory_hash = self._legacy_memory()
        for entry in memory["episodic"]:
            self._insert_episode(connection, entry)
        for topic, data in memory["semantic"].items():
            if not isinstance(topic, str):
                raise MetaBusPersistenceError("legacy_semantic_topic_invalid")
            updated_at = data.get("updated_at") if isinstance(data, dict) else None
            connection.execute(
                "INSERT INTO semantic_topics(topic, data_json, updated_at) VALUES(?, ?, ?)",
                (topic, _json_dump(data), updated_at if isinstance(updated_at, str) else None),
            )
        for topic, value in memory["confidence_ledger"].items():
            if not isinstance(topic, str):
                raise MetaBusPersistenceError("legacy_confidence_key_invalid")
            connection.execute(
                "INSERT INTO confidence_ledger(topic, value_json) VALUES(?, ?)",
                (topic, _json_dump(value)),
            )

        events_hash = None
        imported_events = quarantined_events = 0
        path = self.legacy_events_path
        if path is not None and path.is_file():
            digest = hashlib.sha256()
            try:
                with path.open("rb") as stream:
                    for line_number, raw_line in enumerate(stream, 1):
                        digest.update(raw_line)
                        if not raw_line.strip():
                            continue
                        if len(raw_line) > MAX_LEGACY_EVENT_LINE_BYTES:
                            self._quarantine(
                                connection, path.name, line_number, raw_line,
                                "event_line_size_limit",
                            )
                            quarantined_events += 1
                            continue
                        try:
                            event = _json_load(raw_line.decode("utf-8"))
                            if not isinstance(event, dict):
                                raise ValueError("event_root_must_be_object")
                            self._insert_event(connection, event)
                            imported_events += 1
                        except Exception as exc:
                            self._quarantine(
                                connection, path.name, line_number, raw_line,
                                "invalid_event_json:" + type(exc).__name__,
                            )
                            quarantined_events += 1
                events_hash = digest.hexdigest()
            except OSError as exc:
                raise MetaBusPersistenceError("legacy_events_unreadable") from exc

        return {
            "version": 1,
            "memory_sha256": memory_hash,
            "events_sha256": events_hash,
            "episodes_imported": len(memory["episodic"]),
            "semantic_topics_imported": len(memory["semantic"]),
            "confidence_entries_imported": len(memory["confidence_ledger"]),
            "events_imported": imported_events,
            "events_quarantined": quarantined_events,
        }

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def load_memory(self) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
        try:
            with self._connection() as connection:
                episodes = [
                    _json_load(row[0])
                    for row in connection.execute(
                        "SELECT entry_json FROM episodes ORDER BY seq"
                    )
                ]
                semantic = {
                    row["topic"]: _json_load(row["data_json"])
                    for row in connection.execute(
                        "SELECT topic, data_json FROM semantic_topics ORDER BY topic"
                    )
                }
                confidence = {
                    row["topic"]: _json_load(row["value_json"])
                    for row in connection.execute(
                        "SELECT topic, value_json FROM confidence_ledger ORDER BY topic"
                    )
                }
            return episodes, semantic, confidence
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_memory_read_failed") from exc

    def save_memory_snapshot(
        self, episodic: list[dict[str, Any]], semantic: dict[str, Any],
        confidence_ledger: dict[str, Any],
    ) -> None:
        try:
            with self._transaction() as connection:
                connection.execute("DELETE FROM episodes")
                connection.execute("DELETE FROM semantic_topics")
                connection.execute("DELETE FROM confidence_ledger")
                for entry in episodic[-MAX_EPISODES:]:
                    if not isinstance(entry, dict):
                        raise ValueError("episode_must_be_object")
                    self._insert_episode(connection, entry)
                for topic, data in semantic.items():
                    if not isinstance(topic, str):
                        raise ValueError("semantic_topic_must_be_text")
                    updated_at = data.get("updated_at") if isinstance(data, dict) else None
                    connection.execute(
                        "INSERT INTO semantic_topics(topic, data_json, updated_at) VALUES(?, ?, ?)",
                        (topic, _json_dump(data), updated_at if isinstance(updated_at, str) else None),
                    )
                for topic, value in confidence_ledger.items():
                    if not isinstance(topic, str):
                        raise ValueError("confidence_key_must_be_text")
                    connection.execute(
                        "INSERT INTO confidence_ledger(topic, value_json) VALUES(?, ?)",
                        (topic, _json_dump(value)),
                    )
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_snapshot_write_failed") from exc

    @staticmethod
    def _trim_episodes(connection: sqlite3.Connection) -> None:
        connection.execute(
            "DELETE FROM episodes WHERE seq NOT IN "
            "(SELECT seq FROM episodes ORDER BY seq DESC LIMIT ?)",
            (MAX_EPISODES,),
        )

    def add_observation(self, entry: dict[str, Any]) -> None:
        try:
            with self._transaction() as connection:
                self._insert_episode(connection, entry)
                self._trim_episodes(connection)
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_observation_persistence_failed") from exc

    def add_reflection(self, entry: dict[str, Any], agent_id: str, score: float) -> float:
        try:
            with self._transaction() as connection:
                row = connection.execute(
                    "SELECT value_json FROM confidence_ledger WHERE topic=?", (agent_id,)
                ).fetchone()
                current = _json_load(row[0]) if row is not None else 0.5
                if isinstance(current, bool):
                    current = 0.5
                try:
                    current_score = float(current)
                except (TypeError, ValueError, OverflowError):
                    current_score = 0.5
                if not math.isfinite(current_score):
                    current_score = 0.5
                updated = (max(0.0, min(1.0, current_score)) * 0.7) + (score * 0.3)
                self._insert_episode(connection, entry)
                connection.execute(
                    "INSERT INTO confidence_ledger(topic, value_json) VALUES(?, ?) "
                    "ON CONFLICT(topic) DO UPDATE SET value_json=excluded.value_json",
                    (agent_id, _json_dump(updated)),
                )
                self._trim_episodes(connection)
            return updated
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_reflection_persistence_failed") from exc

    def update_confidence(self, topic: str, score: float) -> float:
        try:
            with self._transaction() as connection:
                row = connection.execute(
                    "SELECT value_json FROM confidence_ledger WHERE topic=?", (topic,)
                ).fetchone()
                current = _json_load(row[0]) if row is not None else 0.5
                try:
                    current = float(current)
                except (TypeError, ValueError, OverflowError):
                    current = 0.5
                if not math.isfinite(current):
                    current = 0.5
                updated = (max(0.0, min(1.0, current)) * 0.7) + (
                    max(0.0, min(1.0, score)) * 0.3
                )
                connection.execute(
                    "INSERT INTO confidence_ledger(topic, value_json) VALUES(?, ?) "
                    "ON CONFLICT(topic) DO UPDATE SET value_json=excluded.value_json",
                    (topic, _json_dump(updated)),
                )
            return updated
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_confidence_persistence_failed") from exc

    def upsert_semantic_topic(
        self, topic: str, lesson: str | None, metadata: dict[str, Any] | None,
        updated_at: str,
    ) -> dict[str, Any]:
        try:
            with self._transaction() as connection:
                row = connection.execute(
                    "SELECT data_json FROM semantic_topics WHERE topic=?", (topic,)
                ).fetchone()
                if row is None:
                    entry: Any = {"lessons": [], "metadata": {}, "updated_at": None}
                else:
                    entry = _json_load(row[0])
                if not isinstance(entry, dict):
                    entry = {"lessons": [], "metadata": {"legacy_value": entry}, "updated_at": None}
                lessons = entry.setdefault("lessons", [])
                if not isinstance(lessons, list):
                    lessons = entry["lessons"] = []
                if lesson and lesson not in lessons:
                    lessons.append(lesson)
                current_metadata = entry.setdefault("metadata", {})
                if not isinstance(current_metadata, dict):
                    current_metadata = entry["metadata"] = {}
                if metadata:
                    current_metadata.update(metadata)
                entry["updated_at"] = updated_at
                connection.execute(
                    "INSERT INTO semantic_topics(topic, data_json, updated_at) VALUES(?, ?, ?) "
                    "ON CONFLICT(topic) DO UPDATE SET data_json=excluded.data_json, updated_at=excluded.updated_at",
                    (topic, _json_dump(entry), updated_at),
                )
            return entry
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_semantic_persistence_failed") from exc

    def append_event(self, event: dict[str, Any]) -> None:
        try:
            with self._transaction() as connection:
                self._insert_event(connection, event)
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_event_persistence_failed") from exc

    @staticmethod
    def _escape_like_prefix(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"

    def recent_events(
        self, limit: int, topic_prefix: str | None = None, source: str | None = None,
    ) -> list[dict[str, Any]]:
        if limit == 0:
            return []
        clauses: list[str] = []
        parameters: list[Any] = []
        if topic_prefix:
            clauses.append("topic LIKE ? ESCAPE '\\'")
            parameters.append(self._escape_like_prefix(str(topic_prefix)))
        if source:
            clauses.append("source = ?")
            parameters.append(str(source))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        parameters.append(limit)
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    f"SELECT event_json FROM events{where} ORDER BY seq DESC LIMIT ?",
                    parameters,
                ).fetchall()
            return [_json_load(row[0]) for row in reversed(rows)]
        except Exception as exc:
            raise MetaBusPersistenceError("metabus_event_read_failed") from exc

    @staticmethod
    def read_projection(
        path: str | os.PathLike[str], *, event_limit: int = 200,
        episode_limit: int = 200, semantic_limit: int = 100,
    ) -> dict[str, Any]:
        """Lê uma projeção limitada sem criar banco, schema ou side effects."""
        database = Path(path).expanduser().resolve()
        uri = database.as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True, timeout=1.0)
        try:
            connection.execute("PRAGMA query_only=ON")
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version != SCHEMA_VERSION:
                raise ValueError("unsupported_metabus_schema")
            events = [
                _json_load(row[0]) for row in reversed(connection.execute(
                    "SELECT event_json FROM events ORDER BY seq DESC LIMIT ?", (event_limit,)
                ).fetchall())
            ]
            episodic = [
                _json_load(row[0]) for row in reversed(connection.execute(
                    "SELECT entry_json FROM episodes ORDER BY seq DESC LIMIT ?", (episode_limit,)
                ).fetchall())
            ]
            semantic_rows = connection.execute(
                "SELECT topic, data_json FROM semantic_topics ORDER BY topic LIMIT ?",
                (semantic_limit,),
            ).fetchall()
            semantic = {row[0]: _json_load(row[1]) for row in semantic_rows}
            return {"events": events, "memory": {"episodic": episodic, "semantic": semantic}}
        finally:
            connection.close()
