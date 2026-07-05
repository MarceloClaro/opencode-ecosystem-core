# SPEC-021: Low-Code Agent Platform — Composição Declarativa de Agentes

## Contexto

**Gartner Hype Cycle 2026**: Low-Code Application Platforms (Slope of Enlightenment, Moderado, <2 anos); Componentes Low-Code para Agentes (Peak of Inflated Expectations, Transformacional, 2-5 anos)
**Gap**: O ecossistema OpenCode não possui interface visual para composição de agentes — toda configuração é via código, JSON ou Markdown. Usuários não-técnicos não conseguem criar ou modificar pipelines multiagente.
**Tipo**: TDD (Test-Driven Development) + SDD (Spec-Driven Development)

## Arquitetura (SDD)

```
┌───────────────────────────────────────────────────────────┐
│               Low-Code Agent Platform                     │
├───────────────────────────────────────────────────────────┤
│  Schema Declarativo │  Visual Builder  │  Code Exporter   │
│  YAML/JSON-based    │  Web UI (React)  │  Python/TS out   │
├──────────────────────┴─────────────────┴─────────────────┤
│                     Execution Engine                       │
│  (Pipeline Runner — compatível com ANP existente)         │
└───────────────────────────────────────────────────────────┘
```

### Contratos de Segurança (SDD)

1. **Schema Declarativo**: Definição YAML/JSON de agentes, conexões, parâmetros
2. **Validação**: Schema JSON contra agentes registrados no Registry
3. **Exportação**: Geração de código Python/TypeScript funcional
4. **Versioning**: Histórico de versões do pipeline declarativo
5. **Isolamento**: Cada pipeline executa em sandbox com limites de recursos
6. **Descoberta**: Catálogo de agentes disponíveis para composição

## Casos de Teste (TDD)

### CT-001: Schema Declarativo — Definição de Pipeline
```python
def test_declarative_pipeline():
    lc = LowCodePlatform()
    schema = {
        "version": "1.0",
        "agents": [
            {"id": "extractor", "type": "seeker", "params": {"query": "AI papers"}},
            {"id": "summarizer", "type": "writer", "params": {"style": "academic"}}
        ],
        "connections": [
            {"from": "extractor.output", "to": "summarizer.input"}
        ]
    }
    pipeline = lc.load_schema(schema)
    assert len(pipeline.agents) == 2
    assert len(pipeline.connections) == 1
    assert pipeline.validate() == True
```

### CT-002: Validação — Schema Inválido
```python
def test_invalid_schema():
    lc = LowCodePlatform()
    schema = {"agents": []}  # sem versão
    with pytest.raises(SchemaValidationError):
        lc.load_schema(schema)
```

### CT-003: Exportação — Geração de Código Python
```python
def test_code_export():
    lc = LowCodePlatform()
    lc.load_schema(VALID_SCHEMA)
    code = lc.export("python")
    assert "def pipeline():" in code
    assert "extractor" in code
    assert "summarizer" in code
    # Verificar que o código gerado é executável
    exec(code)
    assert callable(pipeline)
```

### CT-004: Versioning — Histórico de Versões
```python
def test_pipeline_versioning():
    lc = LowCodePlatform()
    v1 = lc.load_schema(VALID_SCHEMA.copy())
    v2 = lc.load_schema(VALID_SCHEMA.copy(), agents_extra=[...])
    assert v1.version == "1.0"
    assert v2.version == "1.1"
    history = lc.get_history(limit=2)
    assert len(history) == 2
```

### CT-005: Deploy — Pipeline Executável
```python
def test_pipeline_deploy():
    lc = LowCodePlatform()
    pipeline = lc.load_schema(VALID_SCHEMA)
    deployment = lc.deploy(pipeline)
    assert deployment.status == "running"
    assert deployment.endpoint is not None
    result = deployment.invoke(input_data={"text": "test"})
    assert result is not None
```

### CT-006: Discovery — Catálogo de Agentes
```python
def test_agent_discovery():
    lc = LowCodePlatform()
    lc.register_agent_type("seeker", {
        "description": "Pesquisador acadêmico",
        "inputs": [{"name": "query", "type": "string"}],
        "outputs": [{"name": "papers", "type": "list"}]
    })
    catalog = lc.discover_agents(filter="academic")
    assert len(catalog) >= 1
    assert catalog[0].id == "seeker"
```

## Critérios de Aceitação

- [ ] 6/6 CTs aprovados (RED → GREEN)
- [ ] Cobertura mínima: 85%
- [ ] Schema JSON-Schema Draft 2020-12 validado
- [ ] Código gerado deve ser executável (pytest no output)
- [ ] Integração com catálogo de agentes existente (128 agentes)

## Integração com Ecossistema

| Componente | Relação | Prioridade |
|-----------|---------|:----------:|
| Agent Node Pipeline (ANP) | Engine de execução | Alta |
| Schema Registry (SPEC-020) | Registro de schemas declarativos | Média |
| Registry (SPEC-019) | Descoberta de agentes disponíveis | Alta |
| Code GraphRAG | Visualização de dependências entre agentes | Média |
| Visual Builder (React) | Interface web de composição | Baixa (fase 2) |
