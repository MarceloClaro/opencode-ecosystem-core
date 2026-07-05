# SPEC-024: Audit Integration — Relatórios e Verificação Econômica

**Status**: Draft
**Versão**: 1.0
**Data**: 2026-06-07
**Autor**: AntigravityOrchestrator / OpenCode Ecosystem v5.1.0
**Gap**: Camada de auditoria e relatórios sobre Token Economy

---

## 1. SDD — Design Orientado a Especificação

### 1.1 Problema

Token Economy Core (SPEC-022) e Agent Economics (SPEC-023) implementam operações
financeiras, mas não possuem:

- Relatórios consolidados de saldo e gastos por agente
- Verificação de consistência entre ledger e audit trail
- Métricas de saúde econômica do ecossistema
- Exportação de dados financeiros para análise externa

### 1.2 Arquitetura

```
┌────────────────────────────────────────────────────────┐
│               Audit Integration Layer                    │
│                                                          │
│  ┌──────────────────┐  ┌────────────────────┐         │
│  │  BalanceReport    │  │  SpendingReport    │         │
│  │  · all balances   │  │  · by agent        │         │
│  │  · total supply   │  │  · by period       │         │
│  │  · distribution   │  │  · by category     │         │
│  └────────┬─────────┘  └────────┬───────────┘         │
│           │                     │                       │
│  ┌────────▼─────────────────────▼───────────┐         │
│  │       CrossReference Engine               │         │
│  │  · ledger ↔ audit trail consistency       │         │
│  │  · hash chain verification                │         │
│  └────────┬─────────────────────┬───────────┘         │
│           │                     │                       │
│  ┌────────▼─────────┐  ┌───────▼────────────┐        │
│  │  EconHealth       │  │  ReportExporter    │        │
│  │  · supply metrics │  │  · JSON            │        │
│  │  · velocity       │  │  · CSV             │        │
│  │  · fee revenue    │  │  · Markdown        │        │
│  └──────────────────┘  └────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Data Sources                                      │  │
│  │  TokenEconomy.ledger · TokenEconomy.audit_trail   │  │
│  │  AgentEconomics · AuditEntry (conftest)            │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### 1.3 Componentes

| Componente | Responsabilidade |
|------------|------------------|
| **BalanceReport** | Relatório consolidado de saldos de todos os agentes |
| **SpendingReport** | Gastos por agente com breakdown por período/categoria |
| **CrossReferenceEngine** | Verifica consistência entre ledger e audit trail |
| **EconHealth** | Métricas de saúde: supply, velocidade, fee revenue |
| **ReportExporter** | Exporta relatórios em JSON/CSV/Markdown |

### 1.4 Fluxos Principais

**Generate Balance Report**: BalanceReport.generate() →
iterate agents → collect balances → compute distribution →
return structured report

**Generate Spending Report**: SpendingReport.generate(agent_id, period) →
filter ledger by agent → aggregate by reason → return breakdown

**Cross-Reference**: CrossReferenceEngine.verify() →
iterate audit_trail → match against ledger entries →
verify SHA-256 hashes → report mismatches

**Health Metrics**: EconHealth.compute() →
total_supply, velocity = total_transfer_volume / total_supply,
fee_revenue = sum of fee transactions → return dashboard

### 1.5 Restrições de Segurança

1. Reports nunca expõem nonces ou signatures individuais
2. Cross-reference falha se hash chain estiver quebrada
3. Health metrics são computacionais (sem side effects)
4. Exportação omite dados sensíveis (nonce, signature raw)
5. Períodos sem transações geram relatório vazio, não erro

---

## 2. TDD — Test-Driven Specification

### 2.1 Dataclasses Compartilhadas (extensões)

```python
@dataclass
class BalanceReport:
    generated_at: str
    total_agents: int
    total_supply: int
    total_staked: int
    agents: list[dict]  # [{agent_id, balance, staked, tier}]

@dataclass
class SpendingSummary:
    agent_id: str
    period: str          # "daily" | "weekly" | "all"
    total_spent: int
    by_reason: dict      # {"transfer": 200, "fee": 50}
    transaction_count: int

@dataclass
class EconHealthMetrics:
    total_supply: int
    circulating_supply: int
    staked_supply: int
    total_burned: int
    fee_revenue: int
    transaction_count: int
    unique_agents: int
    velocity: float       # transfer_volume / total_supply
```

### 2.2 Casos de Teste

#### CT-01: Balance Report Completo
Gerar relatório consolidado de todos os saldos.

```python
def test_balance_report():
    audit = TokenAudit(TokenEconomy())
    audit.economy.mint("agent-a", 1000)
    audit.economy.mint("agent-b", 500)
    report = audit.generate_balance_report()
    assert report.total_agents == 2
    assert report.total_supply == 1500
    assert len(report.agents) == 2
```

#### CT-02: Spending Report por Agente
Agrupar gastos de um agente por razão/período.

```python
def test_spending_report():
    audit = TokenAudit(TokenEconomy())
    audit.economy.mint("agent-a", 1000)
    audit.economy.transfer("agent-a", "agent-b", 200)
    audit.economy.burn("agent-a", 100)
    report = audit.spending_report("agent-a", period="all")
    assert report.total_spent == 300  # transfer 200 + burn 100
    assert report.transaction_count == 2
    assert "transfer" in report.by_reason
```

#### CT-03: Cross-Reference Ledger ↔ Audit
Verificar integridade entre ledger e audit trail.

```python
def test_cross_reference():
    audit = TokenAudit(TokenEconomy())
    audit.economy.mint("agent-a", 500)
    audit.economy.transfer("agent-a", "agent-b", 200)
    mismatches = audit.cross_reference()
    assert len(mismatches) == 0  # tudo consistente
    ledger_len = len(audit.economy.ledger)
    audit_len = len(audit.economy.audit_trail)
    assert ledger_len == audit_len  # 1:1 mapping
```

#### CT-04: Economic Health Metrics
Calcular métricas de saúde do ecossistema.

```python
def test_econ_health():
    audit = TokenAudit(TokenEconomy())
    audit.economy.mint("agent-a", 1000)
    audit.economy.mint("agent-b", 500)
    audit.economy.transfer("agent-a", "agent-b", 300)
    audit.economy.burn("agent-a", 100)
    health = audit.health_metrics()
    assert health.total_supply == 1400  # 1500 - 100 burn
    assert health.transaction_count == 4  # 2 mint + 1 transfer + 1 burn
    assert health.unique_agents == 2
    assert health.velocity > 0
```

---

## 3. Matriz de Rastreabilidade

| CT | Nome | Nível | Coverage Target |
|:--:|------|:-----:|:---------------:|
| 01 | Balance Report Completo | N2 | 100% |
| 02 | Spending Report por Agente | N2 | 100% |
| 03 | Cross-Reference Ledger ↔ Audit | N3 | 100% |
| 04 | Economic Health Metrics | N3 | 100% |

---

## 4. Validação Cruzada

- **SPEC-022 ↔ SPEC-024**: 0.95 — Audit Integration consome TokenEconomy
- **SPEC-023 ↔ SPEC-024**: 0.90 — Staking e slashing aparecem nos reports
- **SPEC-019 ↔ SPEC-024**: 0.85 — AuditEntry reutilizado para cross-reference

---

## 5. Referências

- OpenCode Ecosystem AGENTS.md v5.1.0
- SPEC-022 Token Economy Core
- SPEC-023 Agent Economics
