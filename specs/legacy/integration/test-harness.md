# Spec: Test Harness — Validacao Cross-Component do Ecossistema

**Versao:** 1.0.0
**Status:** proposed
**Manutencao SWEBOK:** preventiva
**Ultima revisao:** 2026-05-27

---

## 1. Comportamento Esperado

Test harness que valida a integracao entre componentes do ecossistema. Diferente de testes unitarios (que testam modulos isolados), este harness testa fluxos cross-component:

- Agent → Skill → MCP (cadeia de delegacao completa)
- Evolution Cycle: SENSE → DISCOVER → INSTALL → VERIFY → EVOLVE → LEARN
- Health Check cross-component
- Knowledge Graph: criacao de entidades + relacoes + consulta
- IPC: comunicacao entre processos

## 2. Usuarios e Contexto

- **Usuarios:** CI pipeline, desenvolvedores do ecossistema
- **Volume:** 10-15 cenarios de integracao
- **Ambiente:** Python 3.11+, pytest, com MCPs mockados
- **Dependencias:** todos os componentes core

## 3. Restricoes

- MCPs externos (websearch, playwright, github) devem ser mockados
- MCPs locais (memory, sqlite, sequential-thinking) podem ser reais
- Cada cenario deve limpar seu estado ao final (teardown)
- Testes de integracao nao devem modificar arquivos reais do ecossistema

## 4. Casos de Borda

- MCP offline: mock deve simular timeout e verificar fallback
- Concorrencia: 2 agentes acessando o mesmo state manager
- Corrupcao de estado: DB SQLite corrompido → FileStateManager deve continuar funcionando
- Evolucao com falha: ciclo de evolucao interrompido → rollback para estado anterior

## 5. Criterios de Aceitacao

- [ ] Fluxo Agent→Skill→MCP funciona com mock
- [ ] Evolution cycle completa sem erros (com MCPs mockados)
- [ ] Health check detecta MCP offline
- [ ] Knowledge graph: create → relate → search consistente
- [ ] State manager: SQLite corrompido → FileStateManager operacional
- [ ] IPC: comando enviado → resposta recebida em < 5s
- [ ] Rollback de evolucao: estado restaurado apos falha

## 6. Cenarios de Teste

### Cenario 1: Cadeia Agent→Skill→MCP
```
1. Agent "test-agent" registrado
2. Skill "test-skill" carregada
3. MCP "memory" mockado
4. Agent.execute() → delega para Skill → Skill usa MCP
5. Verificar: MCP recebeu chamada correta, resultado propagado
```

### Cenario 2: Evolution Cycle
```
1. Estado inicial capturado (snapshot DB)
2. SENSE: detectar necessidade (mock)
3. DISCOVER: encontrar solucao (mock)
4. INSTALL: instalar skill/plugin (real)
5. VERIFY: testes passam (real)
6. EVOLVE: atualizar estado (real)
7. LEARN: registrar aprendizado (real)
8. Verificar: estado final != estado inicial, sem erros
```

### Cenario 3: Resiliencia State Manager
```
1. Corromper SQLite DB (simulado)
2. Tentar set/get via SQLite → erro
3. Tentar set/get via FileStateManager → sucesso
4. Health check reporta SQLite degraded, File OK
```
