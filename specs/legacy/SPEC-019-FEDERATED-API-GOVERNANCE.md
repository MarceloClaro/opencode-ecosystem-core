# SPEC-019: Federated API Governance para Agentes Multiagente

## Contexto

**Gartner Hype Cycle 2026**: API Gateway/Brokering (Slope of Enlightenment, Moderado, 2-5 anos para Plateau)
**Gap**: O ecossistema OpenCode não possui política federada de governança de API entre agentes — cada agente gerencia dependências sem coordenador central
**Tipo**: TDD (Test-Driven Development) + SDD (Spec-Driven Development)

## Arquitetura (SDD)

```
┌─────────────────────────────────────────────────┐
│            Federated API Governor                │
├─────────────────────────────────────────────────┤
│  Registry  │  Policy Engine  │  Audit Trail     │
│  ───────── │  ─────────────  │  ───────────     │
│  Service A │  Rate Limit:100 │  2026-06-07T...  │
│  Service B │  RBAC: admin    │  2026-06-07T...  │
│  Service C │  Circuit: 3/5   │  2026-06-07T...  │
└────────────┴────────────────┴──────────────────┘
         │              │              │
         ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ Agent A  │  │ Agent B  │  │ Agent C  │
  │ (API cli)│  │ (API cli)│  │ (API cli)│
  └──────────┘  └──────────┘  └──────────┘
```

### Contratos de Segurança (SDD)

1. **Autenticação**: JWT com claims `agent_id`, `scope`, `ttl`
2. **Autorização**: RBAC hierárquico (admin > dev > agent > readonly)
3. **Rate Limiting**: Token bucket por agente, defaults: 100/min (agent), 1000/min (admin)
4. **Circuit Breaker**: 3 falhas consecutivas → 30s half-open → 5 sucessos → closed
5. **Audit Trail**: Log imutável de todas as chamadas (who, what, when, result)
6. **Cache**: Respostas cacheadas por 60s com invalidação por evento

## Casos de Teste (TDD)

### CT-001: Registry — Registro de Serviço
```python
def test_register_service():
    governor = FederatedAPIGovernor()
    service = APIService(name="alpha", version="1.0", endpoints=["/predict", /health"])
    result = governor.register(service)
    assert result.status == "registered"
    assert governor.registry.get("alpha") == service
```

### CT-002: Policy Engine — Rate Limiting por Agente
```python
def test_rate_limit_agent():
    governor = FederatedAPIGovernor()
    governor.set_policy("agent-alpha", RateLimit(calls=5, window_sec=60))
    for i in range(5):
        assert governor.check_rate_limit("agent-alpha") == True
    assert governor.check_rate_limit("agent-alpha") == False  # exceeded
```

### CT-003: Circuit Breaker — 3 Falhas → Open
```python
def test_circuit_breaker_trips():
    governor = FederatedAPIGovernor()
    service = "model-serving"
    for _ in range(3):
        governor.record_failure(service)
    assert governor.get_circuit_state(service) == "open"
```

### CT-004: Audit Trail — Imutabilidade
```python
def test_audit_trail_immutable():
    governor = FederatedAPIGovernor()
    governor.call("agent-a", "service-b", "predict", {"x": 1})
    governor.call("agent-b", "service-a", "health", {})
    entries = governor.get_audit(limit=2)
    assert len(entries) == 2
    assert entries[0].agent_id == "agent-b"  # most recent first
    assert "hash" in entries[0].model_dump()
```

### CT-005: Discovery — Descoberta Automática
```python
def test_service_discovery():
    governor = FederatedAPIGovernor()
    governor.register(APIService(name="gamma", version="2.0"))
    governor.register(APIService(name="delta", version="1.5"))
    services = governor.discover(query="version>=2.0")
    assert len(services) == 1
    assert services[0].name == "gamma"
```

### CT-006: Federation — Propagação de Políticas entre Nós
```python
def test_federation_propagation():
    node_a = FederatedAPIGovernor(node_id="a")
    node_b = FederatedAPIGovernor(node_id="b")
    node_a.federate_with(node_b)
    node_a.set_policy("global", RateLimit(calls=50, window_sec=60))
    assert node_b.get_policy("global") is not None
```

### CT-007: Cache — Invalidação por Evento
```python
def test_cache_invalidation():
    governor = FederatedAPIGovernor()
    governor.cache_set("key:model-1", {"data": "cached"}, ttl_sec=60)
    assert governor.cache_get("key:model-1") is not None
    governor.invalidate("model-1")
    assert governor.cache_get("key:model-1") is None
```

### CT-008: Versioning — Múltiplas Versões de API
```python
def test_api_versioning():
    governor = FederatedAPIGovernor()
    governor.register(APIService(name="api", version="1.0", endpoints=["/v1/data"]))
    governor.register(APIService(name="api", version="2.0", endpoints=["/v2/data"]))
    v1 = governor.resolve("api", version="1.0")
    v2 = governor.resolve("api", version="2.0")
    assert v1.endpoints == ["/v1/data"]
    assert v2.endpoints == ["/v2/data"]
```

## Critérios de Aceitação

- [ ] 8/8 CTs aprovados (RED → GREEN)
- [ ] Cobertura mínima: 85% (pytest-cov)
- [ ] Audit trail com hash SHA-256 (imutabilidade)
- [ ] Performance: < 5ms overhead por chamada governada
- [ ] Documentação dos endpoints gRPC/REST gerada

## Integração com Ecossistema

| Componente | Relação | Prioridade |
|-----------|---------|:----------:|
| Container DI | Host do governor | Alta |
| MCP Servers | Registro automático | Alta |
| Code GraphRAG | Descoberta de dependências | Média |
| Audit Trail TSAC | Log imutável | Alta |
