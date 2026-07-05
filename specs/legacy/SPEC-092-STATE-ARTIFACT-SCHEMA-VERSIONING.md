# SPEC-092: State Artifact Schema Versioning

## 1. Visão Geral
**Objetivo:** Disciplinar todos os artefatos de estado do ecossistema com schemas formais (JSON Schema + Pydantic), versionamento semântico, migração automática e validação obrigatória em tempo de leitura/escrita.

**Motivação:** O diagnóstico revelou ~30+ arquivos de estado JSON sem schema formal, 3 implementações concorrentes de state manager, e mais de 100 locais com `json.load`/`json.dump` direto sem validação. Isso cria fragilidade, inconsistência e impossibilidade de evolução controlada.

## 2. Arquitetura

### 2.1 Schema Registry

```
ecosystem/schemas/
├── __init__.py
├── registry.py              # SchemaRegistry central
├── versions.py              # Versionamento semântico
├── validators.py            # Validadores por tipo de schema
├── migration.py             # Engine de migração entre versões
├── state/                   # Schemas de artefatos de estado
│   ├── __init__.py
│   ├── ecosystem_state.json      # JSON Schema para ecosystem-state.json
│   ├── health_report.json        # JSON Schema para health-report
│   ├── bridge_state.json         # JSON Schema para bridge-state
│   ├── evolution_cycle.json      # JSON Schema para evolution-cycle
│   ├── learnings.json            # JSON Schema para learnings
│   ├── token_stats.json          # JSON Schema para token-stats
│   └── sync_status.json          # JSON Schema para sync-status
└── pydantic/                # Modelos Pydantic equivalentes
    ├── __init__.py
    ├── ecosystem_state.py
    ├── health_report.py
    └── evolution_cycle.py
```

### 2.2 State Manager Unificado (Refatorado)

```python
class SchemaAwareStateManager:
    """
    Wrapper sobre state managers existentes que adiciona:
    - Validação contra schema na escrita
    - Validação contra schema na leitura (com reparo automático)
    - Versionamento de schema
    - Migração automática entre versões
    - Audit trail de mudanças
    """
    
    VERSION_KEY = "__schema_version__"
    
    def __init__(self, backend: IStateManager, schema_registry: SchemaRegistry):
        self._backend = backend
        self._schemas = schema_registry
    
    def set(self, key: str, value: dict, schema_name: str | None = None) -> None:
        """Valida e persiste estado com schema."""
        if schema_name:
            self._schemas.validate(schema_name, value)
            value[self.VERSION_KEY] = self._schemas.current_version(schema_name)
        self._backend.set(key, self._encode(value))
    
    def get(self, key: str, schema_name: str | None = None) -> dict:
        """Lê, valida e migra estado se necessário."""
        raw = self._backend.get(key)
        if raw is None:
            return {}
        value = self._decode(raw)
        if schema_name and self._needs_migration(value, schema_name):
            value = self._schemas.migrate(schema_name, value)
            self.set(key, value, schema_name)
        return value
```

### 2.3 JSON Schema Example (ecosystem-state.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://opencode.ecosystem/schemas/ecosystem-state.json",
  "title": "EcosystemState",
  "version": "7.2.0",
  "type": "object",
  "required": ["version", "current_cycle", "last_updated", "history"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Versão semântica do schema"
    },
    "current_cycle": {
      "type": "string",
      "pattern": "^R\\d+$",
      "description": "Ciclo evolutivo atual"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp ISO 8601 da última atualização"
    },
    "tests_passing": {
      "type": "integer",
      "minimum": 0,
      "description": "Número de testes passando"
    },
    "total_cts": {
      "type": "integer",
      "minimum": 0,
      "description": "Total de casos de teste"
    },
    "history": {
      "type": "object",
      "patternProperties": {
        "^R\\d+$": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100
        }
      },
      "description": "Histórico de scores por ciclo"
    }
  }
}
```

### 2.4 Schema Versionamento Semântico

```
MAJOR.MINOR.PATCH
  │      │      └── Correção: campo opcional adicionado, docs
  │      └────────── Menor: campo obrigatório adicionado, tipo relaxado
  └──────────────── Major: quebra de compatibilidade retroativa
```

### 2.5 Artifacts com Schema

| Artefato | Schema | Versão Atual | Prioridade |
|----------|--------|-------------|------------|
| `ecosystem-state.json` | `ecosystem_state.json` | 7.2.0 | CRÍTICA |
| `health-report.json` | `health_report.json` | 1.0.0 | ALTA |
| `bridge-state.json` | `bridge_state.json` | 1.0.0 | ALTA |
| `evolution-cycle.json` | `evolution_cycle.json` | 1.0.0 | ALTA |
| `learnings.json` | `learnings.json` | 1.0.0 | MÉDIA |
| `token-stats.json` | `token_stats.json` | 1.0.0 | MÉDIA |
| `sync-status.json` | `sync_status.json` | 1.0.0 | MÉDIA |
| `manus-state.json` | `manus_state.json` | 1.0.0 | MÉDIA |
| `dashboard-metrics.json` | `dashboard_metrics.json` | 1.0.0 | BAIXA |
| `installed.json` | `installed.json` | 1.0.0 | BAIXA |

## 3. Requisitos TDD

| CT ID | Descrição | Critério |
|-------|-----------|----------|
| CT-9201 | SchemaRegistry registra schema JSON | `register()` com schema válido não lança exceção |
| CT-9202 | Validação de estado contra schema | Dado inválido lança `SchemaValidationError` |
| CT-9203 | Dado válido passa pela validação | `validate()` retorna True |
| CT-9204 | Migração automática entre versões | `migrate(v1 → v2)` preserva dados e adiciona campos |
| CT-9205 | SchemaAwareStateManager.set() valida na escrita | Rejeita dados fora do schema |
| CT-9206 | SchemaAwareStateManager.get() valida na leitura | Corrige dados corrompidos automaticamente |
| CT-9207 | Versionamento semântico funcional | `bump_major()` incrementa corretamente |
| CT-9208 | ecosystem-state.json schema válido | JSON Schema é sintaticamente correto |
| CT-9209 | Audit trail registra mudanças de estado | Cada `set()` gera entrada imutável |
| CT-9210 | Migração batch de todos os artefatos | `migrate_all()` processa sem erro |

## 4. ADRs

### ADR-architectu-092-1: JSON Schema + Pydantic Dual
**Decisão:** Manter schemas em JSON Schema (portável, auto-documentado) e modelos Pydantic equivalentes (validação runtime em Python). Motivo: JSON Schema permite validação em qualquer linguagem; Pydantic fornece type hints e autocomplete no ecossistema Python.

### ADR-architectu-092-2: Version in-band no artefato
**Decisão:** A versão do schema é armazenada dentro do próprio artefato (`__schema_version__`). Motivo: auto-contido, dispensa lookup externo, facilita migração offline.
