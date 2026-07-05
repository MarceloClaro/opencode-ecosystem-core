# SPEC-091: Module Contract Registry

## 1. Visão Geral
**Objetivo:** Formalizar todos os contratos entre módulos do ecossistema através de um Contract Registry centralizado, com interfaces tipadas (Protocols/ABCs), testes de aderência, e documentação gerada automaticamente.

**Motivação:** O diagnóstico revelou que apenas 15 contratos formais (ABCs/Protocols) existem em 3 locais (`core/interfaces.py`, `basis-research/interfaces.py`, `editais-br/worker/connectors/base.py`), enquanto o restante do ecossistema (~85% dos módulos) usa acoplamento direto sem contratos.

## 2. Arquitetura

### 2.1 Contract Registry

```
ecosystem/contracts/
├── __init__.py           # ContractRegistry, contract decorator
├── registry.py           # Implementação do registro central
├── interfaces/           # Definições formais de contratos
│   ├── __init__.py
│   ├── istate_manager.py     # IStateManager (refatorado)
│   ├── ievent_bus.py         # IEventBus (refatorado)
│   ├── icache.py             # ICache (refatorado)
│   ├── itask_queue.py        # ITaskQueue (refatorado)
│   ├── iagent.py             # IAgent (novo, unificado)
│   ├── iplugin.py            # IPlugin (novo, unificado)
│   ├── iscanner.py           # IScanner (novo)
│   ├── ipipeline.py          # IPipeline (novo)
│   ├── iadapter.py           # IAdapter (novo)
│   └── iskill.py             # ISkill (novo)
├── protocols/            # Protocols duck-typing
│   ├── __init__.py
│   ├── p_serializable.py
│   ├── p_configurable.py
│   └── p_health_checkable.py
├── tests/                # Testes de contrato (contract testing)
│   ├── __init__.py
│   ├── test_state_manager_contract.py
│   ├── test_event_bus_contract.py
│   ├── test_agent_contract.py
│   └── test_scanner_contract.py
└── registry.json         # Snapshot serializado do registro
```

### 2.2 Contract Registry API

```python
# ecossistema/contracts/registry.py

@dataclass
class ContractEntry:
    """Um contrato registrado no ecossistema."""
    name: str                    # Nome único do contrato
    interface: type              # Classe ABC/Protocol
    module_path: str             # Caminho do módulo
    implementations: list[str]   # Implementações registradas
    version: str                 # Versão semântica do contrato
    status: Literal["stable", "draft", "deprecated"]
    test_suite: str | None       # Caminho para testes de contrato

class ContractRegistry:
    """Registro central de contratos entre módulos."""
    
    def register(self, contract: ContractEntry) -> None: ...
    def get(self, name: str) -> ContractEntry: ...
    def implementations_of(self, interface: type) -> list[str]: ...
    def verify_all(self) -> dict[str, bool]: ...  # Verifica aderência
    def snapshot(self) -> dict: ...                # Para serialização
    def export_graph(self) -> dict: ...            # Para grafo de dependências
```

### 2.3 Interfaces Definidas

| Contrato | Métodos Abstratos | Módulos Cobertos |
|----------|-------------------|------------------|
| `IStateManager` | get, set, delete, keys, exists, close | SQLiteStateManager, FileStateManager, UnifiedStateManager |
| `IEventBus` | subscribe, unsubscribe, publish, subscriber_count, topics, clear | AsyncEventBus |
| `ICache` | get, set, delete, has, clear, stats | TTLCache |
| `ITaskQueue` | start, stop, enqueue, get_task, cancel | TaskQueue |
| `IAgent` | initialize, execute, health_check | Todos os 130 agentes |
| `IPlugin` | on_load, on_unload, execute_hook | Todos os 12 plugins |
| `IScanner` | scan, analyze, report | 5 scanners (Noológico, Teleológico, Evolutivo, Potentiality, Social) |
| `IPipeline` | run, validate, get_status | Pipeline acadêmico, CI/CD, ASDE |
| `IAdapter` | can_handle, execute, describe | Adaptadores Nexus, Basis, Artigo, Editais |

## 3. Requisitos TDD

| CT ID | Descrição | Critério |
|-------|-----------|----------|
| CT-9101 | ContractRegistry existe e aceita registros | `register()` não lança exceção |
| CT-9102 | Registry.get() retorna contrato por nome | `get("IStateManager")` retorna `ContractEntry` |
| CT-9103 | Registry.implementations_of() lista implementações | Retorna lista não-vazia para IStateManager |
| CT-9104 | Contrato IAgent definido com métodos abstratos | initialize, execute, health_check |
| CT-9105 | Contrato IScanner definido com métodos abstratos | scan, analyze, report |
| CT-9106 | ContractRegistry.verify_all() verifica aderência | Retorna dict com resultados booleanos |
| CT-9107 | Contrato IAdapter definido | can_handle, execute, describe |
| CT-9108 | Registry.snapshot() serializa para dict | Contém todos os campos obrigatórios |
| CT-9109 | Registry.export_graph() gera dependências | Formato compatível com SPEC-093 |
| CT-9110 | Teste de contrato para IStateManager | Falha se implementação não cumprir contrato |

## 4. Migração

### Fase 1 (este ciclo)
- Criar `ecosystem/contracts/` com interfaces e registry
- Registrar contratos existentes (`core/interfaces.py`)
- Adicionar IAgent, IPlugin, IScanner, IPipeline, IAdapter

### Fase 2 (próximo ciclo)
- Adaptar módulos existentes para implementar contratos
- Substituir imports diretos por lookup no registry

## 5. ADRs

### ADR-architectu-091-1: ABC + Protocol Use Dual Strategy
**Decisão:** Usar ABCs para contratos que exigem herança formal e `typing.Protocol` para duck-typing. Motivo: ABCs fornecem verificação em tempo de execução; Protocols permitem acoplamento frouxo sem herança forçada.

### ADR-architectu-091-2: Contract Testing Separado
**Decisão:** Testes de contrato residem em `ecosystem/contracts/tests/`, não em `tests/`. Motivo: testam o *contrato* em si, não a implementação. Podem ser reusados por qualquer implementação futura.
