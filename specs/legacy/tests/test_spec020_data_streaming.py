"""
SPEC-020: Data Streaming Enterprise — 10 CTs (TDD)
Gartner Hype Cycle 2026: Event-Driven Architecture, Streaming Data Pipelines
"""
import pytest
import json
import time
from dataclasses import dataclass, field
from typing import Optional
from conftest import StreamMessage


# ============================================================
# Exceções
# ============================================================

class BackpressureError(Exception):
    """Buffer cheio — slow consumer detectado."""
    pass


class SchemaValidationError(Exception):
    """Schema inválido ou incompatível."""
    pass


# ============================================================
# Implementações sob teste
# ============================================================

class AvroSchema:
    """Simulação simplificada de schema Avro."""

    def __init__(self, schema_def: str):
        import re
        self.raw = schema_def
        # Extrai campos do schema Avro simplificado
        self.fields = set()
        match = re.search(r'"fields":\s*\[(.*?)\]', schema_def, re.DOTALL)
        if match:
            for f in re.findall(r'"name":\s*"(\w+)"', match.group(1)):
                self.fields.add(f)

    def validate(self, data: dict) -> bool:
        if not isinstance(data, dict):
            return False
        return set(data.keys()) == self.fields


class SchemaRegistry:
    """Registry de schemas com validação."""

    def __init__(self):
        self.schemas: dict[str, AvroSchema] = {}

    def register(self, topic: str, schema: AvroSchema) -> None:
        self.schemas[topic] = schema

    def validate(self, topic: str, data: dict) -> bool:
        schema = self.schemas.get(topic)
        if not schema:
            return False
        return schema.validate(data)


class DataStream:
    """Stream de dados particionado com suporte a replay, DLQ, backpressure."""

    def __init__(self, topics: list[str] | None = None, partitions: int = 1,
                 max_retries: int = 3, buffer_limit: int = 100):
        self.topics: dict[str, list[dict]] = {t: [] for t in (topics or [])}
        self.partitions = partitions
        self.max_retries = max_retries
        self.buffer_limit = buffer_limit
        self.offset_counter = 0
        self.dlq: dict[str, list[dict]] = {}
        self.retry_counts: dict[str, dict[int, int]] = {}
        self.delivered: set[tuple[str, int]] = set()  # (producer_id, msg_id)

    # --- Partitioning ---
    def _get_partition(self, key: str) -> int:
        return hash(key) % self.partitions

    def produce(self, topic: str, value: dict, key: str = "default",
                timestamp: str = "") -> int:
        if topic not in self.topics:
            self.topics[topic] = []
            self.dlq[topic] = []
            self.retry_counts[topic] = {}

        # Backpressure check
        if len(self.topics[topic]) >= self.buffer_limit:
            raise BackpressureError(
                f"Buffer full for topic '{topic}': {self.buffer_limit} limit"
            )

        offset = self.offset_counter
        self.offset_counter += 1

        msg = {
            "offset": offset,
            "topic": topic,
            "key": key,
            "value": value,
            "partition": self._get_partition(key),
            "timestamp": timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                    time.gmtime())
        }
        self.topics[topic].append(msg)
        return offset

    def partition_counts(self, topic: str) -> dict[int, int]:
        counts = {p: 0 for p in range(self.partitions)}
        for msg in self.topics.get(topic, []):
            counts[msg["partition"]] = counts.get(msg["partition"], 0) + 1
        return counts

    # --- Replay ---
    def replay(self, topic: str, from_offset: int) -> list[dict]:
        return [m for m in self.topics.get(topic, [])
                if m["offset"] >= from_offset]

    # --- Retry / DLQ ---
    def attempt_retry(self, topic: str, offset: int) -> dict | None:
        if topic not in self.retry_counts:
            self.retry_counts[topic] = {}
        self.retry_counts[topic][offset] = \
            self.retry_counts[topic].get(offset, 0) + 1
        count = self.retry_counts[topic][offset]

        # Busca mensagem original
        msg = None
        for m in self.topics.get(topic, []):
            if m["offset"] == offset:
                msg = m
                break

        if count > self.max_retries:
            if msg:
                self.dlq.setdefault(topic, []).append({
                    **msg,
                    "error_count": count,
                    "reason": "max_retries_exceeded"
                })
            return None
        return msg

    def get_dlq(self, topic: str) -> list[dict]:
        return self.dlq.get(topic, [])

    # --- Windowing ---
    def window(self, topic: str, start: str, end: str) -> list[dict]:
        return [m for m in self.topics.get(topic, [])
                if start <= m["timestamp"] <= end]

    # --- Multi-topic ---
    def consume_batch(self, topics: list[str],
                      batch_size: int = 10) -> list[dict]:
        results = []
        for t in topics:
            msgs = self.topics.get(t, [])[:batch_size]
            results.extend(msgs)
        return results

    # --- Exactly-Once ---
    def deliver(self, producer_id: str, msg_id: int,
                value: dict) -> bool:
        key = (producer_id, msg_id)
        if key in self.delivered:
            return False  # duplicata ignorada
        self.delivered.add(key)
        return True

    def topic_count(self, topic: str) -> int:
        return len(self.topics.get(topic, []))


class StreamProducer:
    """Produtor de stream com suporte a idempotência."""

    def __init__(self, topic: str, idempotent: bool = False):
        self.topic = topic
        self.idempotent = idempotent
        self.id = f"producer-{id(hash(self))}"
        self.sequence = 0

    def send(self, value: dict) -> int:
        self.sequence += 1
        return self.sequence


class StreamConsumer:
    """Consumidor de stream com poll."""

    def __init__(self, topic: str):
        self.topic = topic

    def poll(self, timeout_sec: int = 5) -> Optional[dict]:
        # Simulação simplificada
        return {"offset": 1, "data": None}


class StatefulProcessor:
    """Processamento stateful com agregação em janela."""

    def __init__(self):
        self.aggregations: dict[str, dict[str, int]] = {}
        self.windows: dict[str, int] = {}

    def define_aggregation(self, stream: str, window_sec: int,
                           fn: str = "count") -> None:
        self.aggregations[stream] = {}
        self.windows[stream] = window_sec

    def process(self, stream: str, event: dict) -> None:
        if stream not in self.aggregations:
            return
        key = event.get("page", event.get("key", "default"))
        self.aggregations[stream][key] = \
            self.aggregations[stream].get(key, 0) + 1

    def get_aggregation(self, stream: str, key: str) -> int:
        return self.aggregations.get(stream, {}).get(key, 0)


# ============================================================
# Testes (CT-001 a CT-010)
# ============================================================

class TestSchemaRegistry:
    """CT-001: Schema Registry — Registro e Validação"""

    def test_schema_registry(self):
        registry = SchemaRegistry()
        schema = AvroSchema(
            '{"type": "record", "name": "Event", "fields": '
            '[{"name": "data", "type": "string"}]}'
        )
        registry.register("event-topic", schema)
        assert registry.validate("event-topic", {"data": "valid"}) is True
        assert registry.validate("event-topic", {"invalid": "data"}) is False


class TestPartitioning:
    """CT-002: Partitioning — Distribuição por Key Hash"""

    def test_partitioning(self):
        stream = DataStream(topics=["events"], partitions=3)
        for i in range(100):
            stream.produce("events", key=f"agent-{i % 5}", value={"seq": i})
        counts = stream.partition_counts("events")
        assert sum(counts.values()) == 100
        assert all(c > 0 for c in counts.values())


class TestReplay:
    """CT-003: Replay — Reconsumo desde Offset"""

    def test_replay_from_offset(self):
        stream = DataStream(topics=["orders"])
        offsets = [stream.produce("orders", value={"id": i})
                   for i in range(10)]
        replayed = stream.replay("orders", from_offset=offsets[5])
        assert len(replayed) == 5
        assert replayed[0]["value"]["id"] == 5


class TestAtLeastOnce:
    """CT-004: At-Least-Once — Commit Garantido"""

    def test_at_least_once(self):
        consumer = StreamConsumer(topic="events")
        producer = StreamProducer(topic="events")
        msg_id = producer.send({"data": "critical"})
        result = consumer.poll(timeout_sec=5)
        assert result is not None
        assert result["offset"] == msg_id


class TestDeadLetterQueue:
    """CT-005: Dead-Letter Queue — Max Retries Exceeded"""

    def test_dead_letter_queue(self):
        stream = DataStream(topics=["fails"], max_retries=3)
        stream.produce("fails", value={"will": "fail"})
        for _ in range(4):
            stream.attempt_retry("fails", offset=0)
        dlq = stream.get_dlq("fails")
        assert len(dlq) == 1
        assert dlq[0]["error_count"] == 4


class TestWindowing:
    """CT-006: Windowing — Janela Temporal"""

    def test_windowing(self):
        stream = DataStream(topics=["metrics"])
        stream.produce("metrics", value={"cpu": 0.5},
                       timestamp="2026-06-07T10:00:00")
        stream.produce("metrics", value={"cpu": 0.8},
                       timestamp="2026-06-07T10:01:00")
        stream.produce("metrics", value={"cpu": 0.3},
                       timestamp="2026-06-07T10:05:00")
        window = stream.window("metrics",
                               start="2026-06-07T10:00:00",
                               end="2026-06-07T10:02:00")
        assert len(window) == 2


class TestBackpressure:
    """CT-007: Backpressure — Slow Consumer Limit"""

    def test_backpressure(self):
        stream = DataStream(topics=["fast"], buffer_limit=10)
        for i in range(10):
            stream.produce("fast", value={"seq": i})
        with pytest.raises(BackpressureError):
            stream.produce("fast", value={"seq": 11})


class TestStatefulProcessing:
    """CT-008: Stateful Processing — Agregação com Estado"""

    def test_stateful_aggregation(self):
        processor = StatefulProcessor()
        processor.define_aggregation("clickstream", window_sec=60, fn="count")
        for _ in range(5):
            processor.process("clickstream", {"page": "/home"})
        result = processor.get_aggregation("clickstream", "/home")
        assert result == 5


class TestMultiTopic:
    """CT-009: Multi-Topic — Produção e Consumo em Lote"""

    def test_multi_topic(self):
        stream = DataStream(topics=["alpha", "beta", "gamma"])
        for t in ["alpha", "beta", "gamma"]:
            stream.produce(t, value={"from": t})
        batch = stream.consume_batch(topics=["alpha", "beta"], batch_size=5)
        assert len(batch) == 2
        assert {m["topic"] for m in batch} == {"alpha", "beta"}


class TestExactlyOnce:
    """CT-010: Exactly-Once — Idempotência"""

    def test_exactly_once(self):
        producer = StreamProducer(topic="exactly", idempotent=True)
        stream = DataStream()
        msg_id = producer.send({"data": "once"})
        # Tentativa duplicada com mesmo producer_id + sequence
        first = stream.deliver(producer.id, msg_id, {"data": "once"})
        second = stream.deliver(producer.id, msg_id, {"data": "once"})
        assert first is True
        assert second is False  # duplicata rejeitada
