"""R1243: MetaBus limits, confidence inputs and retained-memory consistency."""

from __future__ import annotations

import json
import importlib
import math
import sqlite3

import pytest

metabus_module = importlib.import_module("mci.metabus")


def _memory(monkeypatch, tmp_path):
    monkeypatch.setattr(metabus_module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    monkeypatch.setattr(metabus_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(metabus_module, "DATABASE_FILE", str(tmp_path / "metabus.sqlite3"))
    return metabus_module.MetacognitiveMemory()


def _raises(expected, operation):
    """Return an assertion-friendly result for TDDHistory's RED classifier."""
    try:
        operation()
    except expected:
        return True
    except Exception:
        return False
    return False


def test_memory_context_limit_zero_is_empty_and_invalid_limits_are_rejected(monkeypatch, tmp_path):
    memory = _memory(monkeypatch, tmp_path)
    memory.episodic.append({"id": "episode-1", "agent_id": "agent", "context": "marker"})

    assert memory.get_recent_context(limit=0) == []
    assert memory.get_recent_context(limit=1)[0]["id"] == "episode-1"
    for invalid in (-1, 1001, True, 1.5, "1"):
        assert _raises(ValueError, lambda: memory.get_recent_context(limit=invalid))


def test_memory_search_limit_zero_is_empty_and_invalid_limits_are_rejected(monkeypatch, tmp_path):
    memory = _memory(monkeypatch, tmp_path)
    memory.record_observation("agent", "retention marker", {"result_summary": "distinctive memory"})

    assert memory.search_memory("distinctive memory", limit=0) == []
    assert len(memory.search_memory("distinctive memory", limit=1)) == 1
    for invalid in (-1, 1001, True, 1.5, "1"):
        assert _raises(ValueError, lambda: memory.search_memory("distinctive memory", limit=invalid))


def test_metabus_recent_events_limit_zero_is_empty_and_invalid_limits_are_rejected(monkeypatch, tmp_path):
    path = tmp_path / "events.jsonl"
    database = tmp_path / "metabus.sqlite3"
    events = [
        {"event_id": "e1", "topic": "test.one", "source": "test", "payload": {}},
        {"event_id": "e2", "topic": "test.two", "source": "test", "payload": {}},
    ]
    path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
    monkeypatch.setattr(metabus_module, "EVENTS_FILE", str(path))
    monkeypatch.setattr(metabus_module, "DATABASE_FILE", str(database))

    assert metabus_module.metabus.get_recent_events(limit=0) == []
    assert len(metabus_module.metabus.get_recent_events(limit=1)) == 1
    for invalid in (-1, 1001, True, 1.5, "1"):
        assert _raises(ValueError, lambda: metabus_module.metabus.get_recent_events(limit=invalid))


def test_reflection_score_must_be_finite_normalized_and_does_not_mutate_on_rejection(monkeypatch, tmp_path):
    memory = _memory(monkeypatch, tmp_path)
    before_ledger = dict(memory.confidence_ledger)

    for invalid_score in (True, math.nan, math.inf, -0.01, 1.01, "0.5"):
        assert _raises(
            (TypeError, ValueError),
            lambda: memory.add_reflection("agent", "context", "reflection", invalid_score),
        )
        assert memory.episodic == []
        assert memory.confidence_ledger == before_ledger

    for invalid_fields in (("", "context", "reflection"), ("agent", "", "reflection"),
                           ("agent", "context", ""),
                           ("a" * (metabus_module.MAX_AGENT_ID_LENGTH + 1), "context", "reflection"),
                           ("agent", "c" * (metabus_module.MAX_CONTEXT_LENGTH + 1), "reflection"),
                           ("agent", "context", "r" * (metabus_module.MAX_REFLECTION_LENGTH + 1))):
        assert _raises((TypeError, ValueError), lambda: memory.add_reflection(*invalid_fields, 0.5))
        assert memory.episodic == []
        assert memory.confidence_ledger == before_ledger

    memory.add_reflection("agent", "context", "reflection", 1.0)
    assert memory.confidence_ledger["agent"] == pytest.approx(0.65)


def test_reflection_persistence_failure_rolls_back_episode_and_confidence(monkeypatch, tmp_path):
    memory = _memory(monkeypatch, tmp_path)
    memory.episodic.extend(
        {"id": f"preexisting-{index}", "agent_id": "agent", "context": "historical"}
        for index in range(1000)
    )
    memory.confidence_ledger["agent"] = 0.77
    memory._save(strict=True)
    before_episodic = list(memory.episodic)
    before_ledger = dict(memory.confidence_ledger)
    def fail_write(*_args, **_kwargs):
        raise RuntimeError("injected persistence failure")
    monkeypatch.setattr(memory._store, "add_reflection", fail_write)

    assert _raises(
        RuntimeError,
        lambda: memory.add_reflection("agent", "context", "reflection", 1.0),
    )

    assert memory.episodic == before_episodic
    assert memory.confidence_ledger == before_ledger


def test_successful_save_keeps_runtime_and_disk_retention_in_sync(monkeypatch, tmp_path):
    memory = _memory(monkeypatch, tmp_path)
    memory.episodic.extend(
        {"id": f"old-{index}", "agent_id": "agent", "context": "historical"}
        for index in range(1000)
    )
    memory._save(strict=True)

    memory.add_reflection("agent", "new context", "new reflection", 0.5)

    with sqlite3.connect(tmp_path / "metabus.sqlite3") as connection:
        persisted = [json.loads(row[0]) for row in connection.execute(
            "SELECT entry_json FROM episodes ORDER BY seq"
        )]
    assert len(memory.episodic) == 1000
    assert len(persisted) == 1000
    assert memory.episodic[0]["id"] == "old-1"
    assert persisted == memory.episodic
    assert memory.episodic[-1]["reflection"] == "new reflection"

    memory.record_observation("agent", "new observation", {"result_summary": "saved"})
    with sqlite3.connect(tmp_path / "metabus.sqlite3") as connection:
        persisted = [json.loads(row[0]) for row in connection.execute(
            "SELECT entry_json FROM episodes ORDER BY seq"
        )]
    assert len(memory.episodic) == 1000
    assert persisted == memory.episodic
    assert memory.episodic[-1]["observation"]["result_summary"] == "saved"
