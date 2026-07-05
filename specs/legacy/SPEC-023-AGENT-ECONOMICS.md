# SPEC-023: Agent Economics — Rewards, Slashing e Governança Financeira

**Status**: Draft
**Versão**: 1.0
**Data**: 2026-06-07
**Autor**: AntigravityOrchestrator / OpenCode Ecosystem v5.1.0
**Gap**: Mecanismos econômicos de agentes sobre Token Economy Core (SPEC-022)

---

## 1. SDD — Design Orientado a Especificação

### 1.1 Problema

O Token Economy Core (SPEC-022) fornece operações básicas (mint, transfer, burn,
fee market, reward, audit). Não há mecanismos de:

- **Precificação por operação**: agentes executam operações sem custo individual
- **Rate limiting**: agentes sem saldo mínimo não podem operar
- **Staking**: agentes não podem travar tokens para obter benefícios
- **Slashing**: não há penalidade por má conduta ou inatividade
- **Allowances**: agentes não têm limites de gasto por período
- **Tiers**: não há diferenciação de agentes por nível de stake

### 1.2 Arquitetura

```
┌────────────────────────────────────────────────────────┐
│                 Agent Economics Layer                    │
│                                                          │
│  ┌────────────────┐  ┌──────────────────┐              │
│  │  AgentPricing   │  │   RateLimiter    │              │
│  │  · cost/op      │  │   · min_balance  │              │
│  │  · fee_deduct   │  │   · throttle     │              │
│  └───────┬────────┘  └────────┬─────────┘              │
│          │                     │                         │
│  ┌───────▼─────────────────────▼─────────┐              │
│  │          TokenEconomy (SPEC-022)       │              │
│  │          · mint / transfer / burn      │              │
│  │          · ledger / fee market         │              │
│  └───────┬─────────────────────┬─────────┘              │
│          │                     │                         │
│  ┌───────▼────────┐  ┌────────▼────────┐              │
│  │   AgentStake    │  │  SlashManager   │              │
│  │  · stake()      │  │  · slash()      │              │
│  │  · unstake()    │  │  · appeal()     │              │
│  │  · tier()       │  │                 │              │
│  └────────────────┘  └──────────────────┘              │
│                                                          │
│  ┌────────────────┐  ┌──────────────────┐              │
│  │  AllowanceCtrl  │  │   TierSystem     │              │
│  │  · daily_limit  │  │   · Bronze       │              │
│  │  · weekly_limit │  │   · Silver       │              │
│  │  · reset()      │  │   · Gold         │              │
│  └────────────────┘  └──────────────────┘              │
└────────────────────────────────────────────────────────┘
```

### 1.3 Componentes

| Componente | Responsabilidade |
|------------|------------------|
| **AgentPricing** | Define custo por operação (execute_task, mcp_call, llm_inference) |
| **RateLimiter** | Bloqueia operações se saldo do agente abaixo do mínimo |
| **AgentStake** | Gerencia tokens travados para prioridade e benefícios |
| **SlashManager** | Penaliza agentes por má conduta ou inatividade |
| **AllowanceController** | Limites de gasto por período (diário/semanal) |
| **TierSystem** | Níveis baseados em stake total (Bronze/Silver/Gold) |

### 1.4 Fluxos Principais

**Execute operation**: Agent → Pricing.cost(op_type) → RateLimiter.check(agent) →
AllowanceCtrl.check(agent, cost) → deduct → execute → audit

**Stake**: Agent → Stake.stake(amount) → TokenEconomy.transfer → locked balance → tier recalc

**Slash**: AuditSystem → SlashManager.slash(agent, amount, reason) →
TokenEconomy.burn(staked) → tier recalc → audit

**Tier calc**: TierSystem recompute on stake change → apply benefits
(discount, priority, limits)

### 1.5 Restrições de Segurança

1. Slashing atua primeiro sobre stake locked, depois sobre saldo livre
2. Allowance reset automático no início de cada período
3. Tier apenas aumenta; downgrade requer período de carência
4. RateLimiter não bloqueia o admin
5. Pricing é configurável por tipo de operação

---

## 2. TDD — Test-Driven Specification

### 2.1 Dataclasses Compartilhadas (extensões)

```python
@dataclass
class AgentStakeInfo:
    agent_id: str
    staked_amount: int = 0
    locked_until: float = 0.0
    tier: str = "bronze"  # bronze | silver | gold

@dataclass
class OperationCost:
    op_type: str          # "execute_task" | "mcp_call" | "llm_inference"
    base_cost: int        # unidades atômicas
    per_unit_cost: int = 0  # custo adicional por unidade

@dataclass
class AgentAllowance:
    agent_id: str
    daily_limit: int
    weekly_limit: int
    daily_spent: int = 0
    weekly_spent: int = 0
    last_daily_reset: str = ""
    last_weekly_reset: str = ""
```

### 2.2 Casos de Teste

#### CT-01: Agent Operation Pricing
Deduzir custo da carteira do agente ao executar operação.

```python
def test_operation_pricing():
    econ = AgentEconomics(TokenEconomy())
    econ.economy.mint("agent-a", 1000)
    econ.execute("agent-a", "mcp_call", params={"service": "search"})
    assert econ.economy.balance("agent-a") == 1000 - econ.pricing("mcp_call")
```

#### CT-02: Token-Based Rate Limiting
Bloquear operação se saldo do agente estiver abaixo do mínimo.

```python
def test_rate_limiting():
    econ = AgentEconomics(TokenEconomy())
    econ.set_min_balance("agent-a", 500)
    econ.economy.mint("agent-a", 100)
    with pytest.raises(InsufficientBalanceError):
        econ.execute("agent-a", "mcp_call")
```

#### CT-03: Agent Staking
Travar tokens e verificar tier upgrade.

```python
def test_agent_staking():
    econ = AgentEconomics(TokenEconomy())
    econ.economy.mint("agent-a", 5000)
    econ.stake("agent-a", 3000)
    assert econ.get_stake("agent-a") == 3000
    assert econ.get_tier("agent-a") == "silver"
    assert econ.economy.balance("agent-a") == 2000  # saldo livre
```

#### CT-04: Slashing por Má Conduta
Penalizar agente com perda de tokens staked.

```python
def test_agent_slashing():
    econ = AgentEconomics(TokenEconomy())
    econ.economy.mint("agent-a", 5000)
    econ.stake("agent-a", 3000)
    econ.slash("agent-a", 1000, "violation")
    assert econ.get_stake("agent-a") == 2000  # stake reduzido
    assert econ.economy.total_supply() == 4000  # queimado
    assert len(econ.audit_trail) > 0
```

#### CT-05: Spending Allowance
Respeitar limite diário de gasto do agente.

```python
def test_spending_allowance():
    econ = AgentEconomics(TokenEconomy(), daily_limit=500)
    econ.economy.mint("agent-a", 5000)
    ok1 = econ.check_allowance("agent-a", 300)
    ok2 = econ.check_allowance("agent-a", 300)  # excede
    assert ok1 is True
    assert ok2 is False
```

#### CT-06: Agent Tier Benefits
Gold tier recebe desconto em taxas.

```python
def test_tier_benefits():
    econ = AgentEconomics(TokenEconomy())
    econ.economy.mint("agent-a", 10000)
    econ.stake("agent-a", 8000)
    assert econ.get_tier("agent-a") == "gold"
    fee = econ.calculate_operation_cost("agent-a", "mcp_call")
    # gold tier tem 50% discount
    expected = int(econ.pricing("mcp_call") * 0.5)
    assert fee == expected
```

---

## 3. Matriz de Rastreabilidade

| CT | Nome | Nível | Coverage Target |
|:--:|------|:-----:|:---------------:|
| 01 | Agent Operation Pricing | N2 | 100% |
| 02 | Token-Based Rate Limiting | N2 | 100% |
| 03 | Agent Staking | N2 | 100% |
| 04 | Slashing por Má Conduta | N3 | 100% |
| 05 | Spending Allowance | N2 | 100% |
| 06 | Agent Tier Benefits | N3 | 100% |

---

## 4. Validação Cruzada

- **SPEC-022 ↔ SPEC-023**: 0.95 — Agent Economics estende Token Economy Core
- **SPEC-023 ↔ SPEC-024**: 0.90 — Slashing e allowances são auditáveis
- **DecisionNode ↔ SPEC-023**: 0.85 — Decisões de stake/slash registradas

---

## 5. Referências

- Buterin, V. (2014). Ethereum Whitepaper. https://ethereum.org/whitepaper
- OpenCode Ecosystem AGENTS.md v5.1.0
- SPEC-022 Token Economy Core
