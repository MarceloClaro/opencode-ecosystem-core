"""R1246: migração, transações e concorrência do armazenamento MetaBus."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

metabus_module = importlib.import_module("mci.metabus")


@pytest.fixture
def isolated_metabus(monkeypatch, tmp_path):
    state_dir = tmp_path / ".mci_state"
    state_dir.mkdir()
    memory_path = state_dir / "shared_memory.json"
    events_path = state_dir / "metabus_events.jsonl"
    database_path = state_dir / "metabus.sqlite3"
    monkeypatch.setattr(metabus_module, "MEMORY_FILE", str(memory_path))
    monkeypatch.setattr(metabus_module, "EVENTS_FILE", str(events_path))
    monkeypatch.setattr(metabus_module, "DATABASE_FILE", str(database_path), raising=False)
    memory = metabus_module.MetacognitiveMemory()
    bus = metabus_module.MetaBus()
    bus.memory = memory
    bus.subscribers = {}
    return memory, bus, memory_path, events_path, database_path


def _connect(path: Path):
    return sqlite3.connect(path, timeout=5)


def _raises(expected, operation):
    """Converte expectativa de exceção em assert Python para o classificador RED."""
    try:
        operation()
    except expected:
        return True
    except Exception:
        return False
    return False


def test_legacy_json_and_jsonl_migrate_once_without_mutating_sources(isolated_metabus):
    _, bus, memory_path, events_path, database_path = isolated_metabus
    legacy_memory = {
        "episodic": [
            {"id": "legacy-episode-1", "type": "observation", "agent_id": "a",
             "context": "legacy context", "observation": {"value": 7}}
        ],
        "semantic": {"legacy-topic": {"lessons": ["preserve me"], "metadata": {"v": 1}}},
        "confidence_ledger": {"a": 0.73},
    }
    legacy_events = [
        {"event_id": "legacy-event-1", "timestamp": "2026-01-01T00:00:00+00:00",
         "topic": "legacy.one", "source": "legacy", "payload": {"n": 1}},
        {"event_id": "legacy-event-2", "timestamp": "2026-01-02T00:00:00+00:00",
         "topic": "legacy.two", "source": "legacy", "payload": {"n": 2}},
    ]
    memory_path.write_text(json.dumps(legacy_memory), encoding="utf-8")
    events_path.write_text(
        "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in legacy_events),
        encoding="utf-8",
    )
    original_memory = memory_path.read_bytes()
    original_events = events_path.read_bytes()

    imported = metabus_module.MetacognitiveMemory()
    bus.memory = imported
    assert imported.episodic == legacy_memory["episodic"]
    assert imported.semantic == legacy_memory["semantic"]
    assert imported.confidence_ledger == legacy_memory["confidence_ledger"]
    assert bus.get_recent_events(limit=10) == legacy_events
    assert database_path.is_file(), "SQLite deve ser o armazenamento ativo do MetaBus"
    assert memory_path.read_bytes() == original_memory
    assert events_path.read_bytes() == original_events

    with _connect(database_path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM episodes").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 2

    restarted = metabus_module.MetacognitiveMemory()
    bus.memory = restarted
    assert restarted.episodic == legacy_memory["episodic"]
    assert bus.get_recent_events(limit=10) == legacy_events
    restarted.record_observation("a", "new context", {"value": 8})
    after_second_restart = metabus_module.MetacognitiveMemory()
    assert len(after_second_restart.episodic) == 2
    with _connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 2


def test_malformed_event_lines_are_quarantined_and_preserved(isolated_metabus):
    _, bus, memory_path, events_path, database_path = isolated_metabus
    valid = {"event_id": "valid-event", "timestamp": "t", "topic": "ok",
             "source": "legacy", "payload": {}}
    raw_lines = [json.dumps(valid) + "\n", '{"event_id":\n', "not-json\n"]
    memory_path.write_text(json.dumps({"episodic": [], "semantic": {}, "confidence_ledger": {}}),
                           encoding="utf-8")
    events_path.write_text("".join(raw_lines), encoding="utf-8")
    original = events_path.read_bytes()

    memory = metabus_module.MetacognitiveMemory()
    bus.memory = memory

    assert [event["event_id"] for event in bus.get_recent_events(limit=10)] == ["valid-event"]
    assert events_path.read_bytes() == original
    assert database_path.is_file(), "migração deve materializar o banco SQLite"
    with _connect(database_path) as connection:
        rows = connection.execute(
            "SELECT line_number, raw_sha256, raw_line FROM migration_quarantine ORDER BY line_number"
        ).fetchall()
    assert [row[0] for row in rows] == [2, 3]
    assert rows[0][1] == hashlib.sha256(raw_lines[1].encode()).hexdigest()
    assert rows[1][2].decode() == raw_lines[2]


def test_corrupt_legacy_memory_blocks_migration_without_mutation(isolated_metabus):
    _, _, memory_path, _, database_path = isolated_metabus
    corrupt = b'{"episodic": ['
    memory_path.write_bytes(corrupt)

    assert _raises(RuntimeError, metabus_module.MetacognitiveMemory), \
        "memória legada corrompida precisa bloquear a inicialização"

    assert memory_path.read_bytes() == corrupt
    if database_path.exists():
        with _connect(database_path) as connection:
            marker = connection.execute(
                "SELECT value FROM meta WHERE key = 'legacy_import_v1'"
            ).fetchone()
        assert marker is None


def test_reflection_and_retention_commit_to_sqlite_atomically(isolated_metabus):
    memory, _, _, _, database_path = isolated_metabus
    memory.episodic = [
        {"id": f"old-{index}", "agent_id": "agent", "context": "historical"}
        for index in range(1000)
    ]
    memory.confidence_ledger = {"agent": 0.77}
    assert memory._save(strict=True) is True

    memory.add_reflection("agent", "new context", "new reflection", 1.0)

    assert len(memory.episodic) == 1000
    assert memory.episodic[0]["id"] == "old-1"
    assert memory.episodic[-1]["reflection"] == "new reflection"
    assert memory.confidence_ledger["agent"] == pytest.approx(0.839)
    assert database_path.is_file(), "estado persistido deve residir em SQLite"
    with _connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM episodes").fetchone()[0] == 1000
        assert connection.execute(
            "SELECT score FROM confidence_ledger WHERE topic = 'agent'"
        ).fetchone()[0] == pytest.approx(0.839)

    restarted = metabus_module.MetacognitiveMemory()
    assert len(restarted.episodic) == 1000
    assert restarted.episodic[0]["id"] == "old-1"
    assert restarted.episodic[-1]["reflection"] == "new reflection"
    assert restarted.confidence_ledger["agent"] == pytest.approx(0.839)


def test_failed_episode_insert_rolls_back_reflection_and_confidence(isolated_metabus):
    memory, _, _, _, database_path = isolated_metabus
    memory.confidence_ledger = {"agent": 0.77}
    memory._save(strict=True)
    assert database_path.is_file(), "SQLite deve existir antes da injeção de falha"
    before_episodes = list(memory.episodic)
    before_ledger = dict(memory.confidence_ledger)
    with _connect(database_path) as connection:
        connection.execute("""
            CREATE TRIGGER reject_episode_insert BEFORE INSERT ON episodes
            BEGIN SELECT RAISE(ABORT, 'injected episode failure'); END
        """)

    with pytest.raises(RuntimeError):
        memory.add_reflection("agent", "context", "reflection", 1.0)

    assert memory.episodic == before_episodes
    assert memory.confidence_ledger == before_ledger
    with _connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM episodes").fetchone()[0] == 0
        assert connection.execute(
            "SELECT score FROM confidence_ledger WHERE topic = 'agent'"
        ).fetchone()[0] == pytest.approx(0.77)


def test_failed_event_insert_does_not_dispatch_subscribers(isolated_metabus):
    _, bus, _, _, database_path = isolated_metabus
    assert database_path.is_file(), "SQLite deve existir antes da injeção de falha"
    received = []
    bus.subscribe("unit.persist", lambda event: received.append(event))
    with _connect(database_path) as connection:
        connection.execute("""
            CREATE TRIGGER reject_event_insert BEFORE INSERT ON events
            BEGIN SELECT RAISE(ABORT, 'injected event failure'); END
        """)

    with pytest.raises(RuntimeError):
        bus.publish("unit.persist", {"must_not_dispatch": True}, source_agent="test")

    assert received == []
    assert bus.get_recent_events(limit=10, topic_prefix="unit.persist") == []


def test_concurrent_process_publishers_preserve_every_event(isolated_metabus, tmp_path):
    _, bus, _, _, database_path = isolated_metabus
    # Initialise the schema before the writer processes race to publish.
    assert database_path.is_file(), "SQLite deve existir antes de iniciar os writers"
    root = Path(__file__).resolve().parents[1]
    worker_code = r'''
import sys
from mci.metabus import metabus
worker, count = sys.argv[1], int(sys.argv[2])
for index in range(count):
    metabus.publish("parallel.write", {"worker": worker, "index": index}, source_agent=worker)
'''
    env = dict(os.environ)
    env["MCI_DATABASE_FILE"] = str(database_path)
    env["MCI_STATE_DIR"] = str(tmp_path / "state")
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", worker_code, f"worker-{worker}", "35"],
            cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        for worker in range(4)
    ]
    for process in processes:
        stdout, stderr = process.communicate(timeout=90)
        assert process.returncode == 0, f"stdout={stdout}\nstderr={stderr}"

    events = bus.get_recent_events(limit=1000, topic_prefix="parallel.write")
    assert len(events) == 140
    assert len({event["event_id"] for event in events}) == 140
    assert {event["source"] for event in events} == {f"worker-{index}" for index in range(4)}
    with _connect(database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM events WHERE topic = 'parallel.write'"
        ).fetchone()[0] == 140


def test_recent_event_filters_use_indexes_and_keep_chronological_order(isolated_metabus):
    _, bus, _, events_path, database_path = isolated_metabus
    assert database_path.is_file(), "SQLite deve existir antes da consulta"
    rows = [
        ("query.hit", "worker", 1),
        ("query.hit", "other", 2),
        ("query.hit.detail", "worker", 3),
        ("unrelated", "worker", 4),
        ("query.hit", "worker", 5),
    ]
    for topic, source, number in rows:
        bus.publish(topic, {"n": number}, source_agent=source)

    recent = bus.get_recent_events(limit=2, topic_prefix="query.hit", source="worker")
    assert [event["payload"]["n"] for event in recent] == [3, 5]
    with _connect(database_path) as connection:
        indexes = {row[1] for row in connection.execute("PRAGMA index_list('events')")}
    assert {"idx_events_topic_seq", "idx_events_source_seq"}.issubset(indexes)
    assert not events_path.exists(), "eventos novos não devem voltar ao JSONL legado"


def test_memory_network_reads_sqlite_events_and_episodes(isolated_metabus, tmp_path):
    memory, bus, _, _, database_path = isolated_metabus
    memory.record_observation("agent-db", "SQLite episode", {"summary": "observed"})
    bus.publish("task.post", {"task_id": "task-db", "description": "SQLite task"},
                source_agent="test")

    from webapp.memory_network_visualizer import CoreMemoryNetworkSource

    snapshot = CoreMemoryNetworkSource(tmp_path).snapshot()
    node_ids = {node["id"] for node in snapshot["nodes"]}
    assert "task:task-db" in node_ids
    assert any(node.get("source") == "agent-db" for node in snapshot["nodes"])
    assert snapshot["mode"] == "observed"
    assert not snapshot["externally_validated"]
