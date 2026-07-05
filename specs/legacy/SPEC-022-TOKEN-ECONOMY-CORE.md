# SPEC-022: Token Economy Core

**Status**: Draft
**Versão**: 1.0
**Data**: 2026-06-07
**Autor**: AntigravityOrchestrator / OpenCode Ecosystem v5.1.0
**Gap**: Token Economy — Sistema de Incentivos Econômicos para Agentes

---

## 1. SDD — Design Orientado a Especificação

### 1.1 Problema

O ecossistema OpenCode possui 128 agentes que consomem recursos computacionais
(CPU, memória, chamadas MCP, tokens LLM) sem qualquer mecanismo de rateio,
incentivo ou rastreamento econômico. Não há como:

- Recompensar agentes que contribuem com valor ao ecossistema
- Cobrar taxas proporcionais ao uso de recursos compartilhados
- Rastrear o custo de cada execução de pipeline
- Implementar políticas de prioridade baseadas em stake

### 1.2 Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                  Token Economy Core                   │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Agent   │  │  Token   │  │   TokenLedger     │   │
│  │  Wallet  │◄─┤  Mint/   │◄─┤   (append-only)   │   │
│  │          │  │  Burn    │  │                   │   │
│  └────┬─────┘  └──────────┘  └──────────────────┘   │
│       │                                               │
│  ┌────▼─────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Fee     │  │  Agent   │  │   AuditTrail      │   │
│  │  Market  │◄─┤  Reward  │◄─┤   (Integration)   │   │
│  │          │  │  Engine  │  │                   │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
│                                                       │
│  ┌─────────────────────────────────────────────┐     │
│  │  Integration Layer                           │     │
│  │  AuditSystem · DecisionNode · SPEC-019       │     │
│  └─────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

### 1.3 Componentes

| Componente | Responsabilidade |
|------------|------------------|
| **AgentWallet** | Saldo de tokens por agente |
| **TokenMint** | Emissão controlada de novos tokens |
| **TokenBurn** | Destruição de tokens |
| **TokenTransfer** | Transferência entre agentes com validação de saldo |
| **TokenLedger** | Registro imutável append-only de todas as transações |
| **FeeMarket** | Cálculo dinâmico de taxas por uso de recursos |
| **AgentRewardEngine** | Distribuição de recompensas por contribuição |
| **AuditIntegration** | Conexão com AuditSystem para rastreabilidade |

### 1.4 Fluxos Principais

**Mint**: Admin → TokenMint.mint(agent, amount) → Ledger.append(tx) → Wallet.balance += amount

**Transfer**: Agent → TokenTransfer.transfer(from, to, amount) → Ledger.append(tx) → Wallet update

**Fee**: Resource → FeeMarket.calculate(resource_type, demand) → Transfer(fee) → Ledger

**Reward**: AuditSystem verifies contribution → AgentRewardEngine.distribute(agent, amount) → Mint

### 1.5 Restrições de Segurança

1. Ledger é **append-only** — transações nunca são removidas ou alteradas
2. Saldo nunca pode ser negativo — InsufficientBalanceError
3. Mint requer autorização explícita (admin-only)
4. Fee market é calculado por fórmula determinística (sem oracle externo)
5. Recompensas exigem verificação do AuditSystem

---

## 2. TDD — Test-Driven Specification

### 2.1 Dataclasses Compartilhadas

```python
@dataclass
class AgentToken:
    agent_id: str
    symbol: str        # ex: "OPEN"
    balance: int       # saldo em unidades atômicas (1 token = 10^6 units)
    nonce: int         # anti-replay

@dataclass
class TokenTransaction:
    tx_id: str
    from_agent: str
    to_agent: str
    amount: int
    token_symbol: str
    timestamp: float
    reason: str        # "mint" | "transfer" | "burn" | "fee" | "reward"
    nonce: int
    signature: str     # hash da transação

@dataclass
class FeeSchedule:
    resource_type: str     # "compute" | "storage" | "mcp_call" | "llm_token"
    base_fee: int          # unidades atômicas por operação
    demand_multiplier: float  # > 1.0 em períodos de alta demanda
    agent_discount: float  # 0.0-1.0, baseado em stake
```

### 2.2 Casos de Teste

#### CT-01: Token Mint
Criar tokens para um agente com quantidade especificada.

```python
def test_token_mint():
    economy = TokenEconomy()
    economy.mint("agent-a", 1000)
    assert economy.balance("agent-a") == 1000
```

#### CT-02: Token Transfer
Transferir tokens entre agentes com dedução correta de saldo.

```python
def test_token_transfer():
    economy = TokenEconomy()
    economy.mint("agent-a", 1000)
    economy.transfer("agent-a", "agent-b", 400)
    assert economy.balance("agent-a") == 600
    assert economy.balance("agent-b") == 400
```

#### CT-03: Token Burn
Queimar tokens e verificar redução de saldo e supply total.

```python
def test_token_burn():
    economy = TokenEconomy()
    economy.mint("agent-a", 1000)
    economy.burn("agent-a", 300)
    assert economy.balance("agent-a") == 700
    assert economy.total_supply() == 700
```

#### CT-04: Insufficient Balance
Rejeitar transferência com saldo insuficiente (exceção).

```python
def test_insufficient_balance():
    economy = TokenEconomy()
    economy.mint("agent-a", 100)
    with pytest.raises(InsufficientBalanceError):
        economy.transfer("agent-a", "agent-b", 200)
    assert economy.balance("agent-a") == 100  # saldo preservado
```

#### CT-05: Ledger Immutability
Verificar que transações no ledger são imutáveis (append-only).

```python
def test_ledger_immutability():
    economy = TokenEconomy()
    economy.mint("agent-a", 500)
    economy.transfer("agent-a", "agent-b", 200)
    assert len(economy.ledger) == 2
    tx = economy.ledger[1]
    # Simula tentativa de alteração
    with pytest.raises(AttributeError):
        tx.amount = 999
```

#### CT-06: Fee Market Dynamic
Calcular taxa dinâmica baseada em demanda do recurso.

```python
def test_fee_market_dynamic():
    economy = TokenEconomy()
    fee = economy.calculate_fee("compute", demand_level="high")
    base = economy.calculate_fee("compute", demand_level="low")
    assert fee > base  # alta demanda = taxa maior
```

#### CT-07: Agent Reward
Recompensar agente por contribuição verificada.

```python
def test_agent_reward():
    economy = TokenEconomy()
    economy.mint("reserve", 5000)
    economy.reward("agent-a", 200, reason="code_review")
    assert economy.balance("agent-a") == 200
```

#### CT-08: Audit Integration
Integrar TokenLedger com AuditTrail (SPEC-019).

```python
def test_audit_integration():
    economy = TokenEconomy()
    audit = AuditTrail()
    economy.set_audit_trail(audit)
    economy.mint("agent-a", 1000)
    assert len(audit.entries) >= 1
    assert audit.entries[-1]["action"] == "token_mint"
```

---

## 3. Matriz de Rastreabilidade

| CT | Nome | Nível | Coverage Target |
|:--:|------|:-----:|:---------------:|
| 01 | Token Mint | N1 | 100% |
| 02 | Token Transfer | N1 | 100% |
| 03 | Token Burn | N1 | 100% |
| 04 | Insufficient Balance | N2 | 100% |
| 05 | Ledger Immutability | N2 | 100% |
| 06 | Fee Market Dynamic | N2 | 100% |
| 07 | Agent Reward | N2 | 100% |
| 08 | Audit Integration | N3 | 100% |

---

## 4. Validação Cruzada

- **SPEC-019 ↔ SPEC-022**: 0.80 — AuditTrail reutilizado para integridade do ledger
- **SPEC-020 ↔ SPEC-022**: 0.70 — Stream de transações pode alimentar analytics
- **SPEC-021 ↔ SPEC-022**: 0.75 — Low-Code Platform expõe wallet como componente visual
- **DecisionNode ↔ SPEC-022**: 0.85 — Decisões registram impacto econômico

---

## 5. Referências

- Buterin, V. (2014). Ethereum Whitepaper. https://ethereum.org/whitepaper
- OpenCode Ecosystem AGENTS.md v5.1.0
- SPEC-019 Federated API Governance
