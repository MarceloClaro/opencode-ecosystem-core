# SPEC-020: Data Streaming Enterprise para Pipeline Multiagente

## Contexto

**Gartner Hype Cycle 2026**: Event-Driven Architecture (Slope of Enlightenment, Moderado, 2-5 anos); Streaming Data Pipelines (Plateau of Productivity, Moderado, <2 anos)
**Gap**: O ecossistema OpenCode não possui pipeline de streaming enterprise — apenas comunicação síncrona via MCP request/response e File IPC assíncrono. Sem suporte a particionamento, replay, exactly-once, ou backpressure.
**Tipo**: TDD (Test-Driven Development) + SDD (Spec-Driven Development)

## Arquitetura (SDD)

```
┌─────────────────────────────────────────────────────┐
│              Streaming Middleware Layer              │
├─────────────────────────────────────────────────────┤
│  Schema Registry  │  Partitioner  │  Replay Engine  │
│  Avro/Protobuf    │  Key-hash     │  Offset-based   │
├─────────┬─────────┴──────┬───────┴────────┬────────┤
│  Topic A│  Topic B       │  Topic C       │ DLQ    │
│  Agent  │  Event Bus     │  Metrics       │        │
└─────────┴────────────────┴────────────────┴────────┘
```

### Contratos de Segurança (SDD)

1. **Schema Registry**: Validação de schema, evolução compatível (Avro/Protobuf)
2. **Partitioning**: Key-hash distribuído; ordenação por partição
3. **Replay**: Reconsumo de offsets com checkpoint
4. **At-Least-Once**: Confirmação de commit após processamento
5. **Dead-Letter Queue**: Mensagens não processáveis após 3 retries
6. **Backpressure**: Slow consumer → buffer limit → alerta
7. **Exactly-Once**: Idempotência via producer-id + sequence number

## Casos de Teste (TDD)

### CT-001: Schema Registry — Registro e Validação
```python
def test_schema_registry():
    registry = SchemaRegistry()
    schema = AvroSchema("{\"type\": \"record\", \"name\": \"Event\", \"fields\": [...]}")
    registry.register("event-topic", schema)
    assert registry.validate("event-topic", {"data": "valid"}) == True
    assert registry.validate("event-topic", {"invalid": "data"}) == False
```

### CT-002: Partitioning — Distribuição por Key Hash
```python
def test_partitioning():
    stream = DataStream(topics=["events"], partitions=3)
    for i in range(100):
        stream.produce("events", key=f"agent-{i%5}", value={"seq": i})
    counts = stream.partition_counts("events")
    assert sum(counts.values()) == 100
    assert all(c > 0 for c in counts.values())  # todas as partitions usadas
```

### CT-003: Replay — Reconsumo desde Offset
```python
def test_replay_from_offset():
    stream = DataStream(topics=["orders"])
    offsets = [stream.produce("orders", value={"id": i}) for i in range(10)]
    replayed = stream.replay("orders", from_offset=offsets[5])
    assert len(replayed) == 5
    assert replayed[0].value["id"] == 5
```

### CT-004: At-Least-Once — Commit Garantido
```python
def test_at_least_once():
    consumer = StreamConsumer(topic="events")
    producer = StreamProducer(topic="events")
    msg_id = producer.send({"data": "critical"})
    result = consumer.poll(timeout_sec=5)
    assert result is not None
    assert result.offset == msg_id
```

### CT-005: Dead-Letter Queue — Max Retries Exceeded
```python
def test_dead_letter_queue():
    stream = DataStream(topics=["fails"], max_retries=3)
    stream.produce("fails", value={"will": "fail"})
    for _ in range(4):
        stream.attempt_retry("fails", offset=0)  # 3 retries + 1 extra
    dlq = stream.get_dlq("fails")
    assert len(dlq) == 1
    assert dlq[0].error_count == 4
```

### CT-006: Windowing — Janela Temporal
```python
def test_windowing():
    stream = DataStream(topics=["metrics"])
    stream.produce("metrics", value={"cpu": 0.5}, timestamp="2026-06-07T10:00:00")
    stream.produce("metrics", value={"cpu": 0.8}, timestamp="2026-06-07T10:01:00")
    stream.produce("metrics", value={"cpu": 0.3}, timestamp="2026-06-07T10:05:00")
    window = stream.window("metrics", start="2026-06-07T10:00:00", end="2026-06-07T10:02:00")
    assert len(window) == 2
```

### CT-007: Backpressure — Slow Consumer Limit
```python
def test_backpressure():
    stream = DataStream(topics=["fast"], buffer_limit=10)
    for i in range(15):
        stream.produce("fast", value={"seq": i})
    with pytest.raises(BackpressureError):
        stream.produce("fast", value={"seq": 16})  # buffer full
```

### CT-008: Stateful Processing — Agregação com Estado
```python
def test_stateful_aggregation():
    processor = StatefulProcessor()
    processor.define_aggregation("clickstream", window_sec=60, fn="count")
    for _ in range(5):
        processor.process("clickstream", {"page": "/home"})
    result = processor.get_aggregation("clickstream", "/home")
    assert result == 5
```

### CT-009: Multi-Topic — Produção e Consumo em Lote
```python
def test_multi_topic():
    stream = DataStream(topics=["alpha", "beta", "gamma"])
    for t in ["alpha", "beta", "gamma"]:
        stream.produce(t, value={"from": t})
    batch = stream.consume_batch(topics=["alpha", "beta"], batch_size=5)
    assert len(batch) == 2
    assert {m.topic for m in batch} == {"alpha", "beta"}
```

### CT-010: Exactly-Once — Idempotência
```python
def test_exactly_once():
    producer = StreamProducer(topic="exactly", idempotent=True)
    stream = DataStream()
    msg_id = producer.send({"data": "once"})
    # Tentativa duplicada com mesmo producer_id + sequence
    stream.deliver(producer.id, msg_id, {"data": "once"})
    stream.deliver(producer.id, msg_id, {"data": "once"})  # duplicata
    assert stream.topic_count("exactly") == 1  # apenas 1 mensagem
```

## Critérios de Aceitação

- [ ] 10/10 CTs aprovados (RED → GREEN)
- [ ] Cobertura mínima: 85%
- [ ] Latência P99 < 10ms (in-memory), < 100ms (com log persistence)
- [ ] Suporte a Avro e Protobuf para schema registry
- [ ] Compatibilidade retroativa com File IPC existente

## Integração com Ecossistema

| Componente | Relação | Prioridade |
|-----------|---------|:----------:|
| File IPC | Bridge entre streaming e file-based | Alta |
| Process Lifecycle | Pipeline de consumo contínuo | Média |
| Graph Memory Updater | Consumo de streams de eventos para grafo | Alta |
| MCP Streaming | Extensão do protocolo MCP para streaming | Alta |
