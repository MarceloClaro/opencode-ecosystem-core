"""
SPEC-023: Agent Economics — Rewards, Slashing e Governança Financeira
Round 18: 6 CTs sobre precificação, rate limiting, staking, slashing,
allowances e tier benefits para agentes OpenCode.
"""
import pytest
import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional, Any
from conftest import AuditEntry


# ============================================================
# Exceções
# ============================================================

class InsufficientBalanceError(Exception):
    """Saldo insuficiente para operação."""
    pass


class UnauthorizedMintError(Exception):
    """Tentativa de mint sem autorização."""
    pass


class RateLimitExceeded(Exception):
    """Agente excedeu limite de gasto no período."""
    pass


# ============================================================
# Dataclasses
# ============================================================

@dataclass
class TokenTransaction:
    """Transação no ledger de tokens."""
    tx_id: str
    from_agent: str
    to_agent: str
    amount: int
    token_symbol: str
    timestamp: float
    reason: str
    nonce: int
    signature: str = ""


@dataclass
class FeeSchedule:
    """Tabela de taxas por tipo de recurso."""
    resource_type: str
    base_fee: int
    demand_multiplier: float = 1.0
    agent_discount: float = 0.0


@dataclass
class OperationCost:
    """Custo de operação para agente."""
    op_type: str           # "execute_task" | "mcp_call" | "llm_inference"
    base_cost: int         # unidades atômicas
    per_unit_cost: int = 0


@dataclass
class AgentStakeInfo:
    """Informação de stake de um agente."""
    agent_id: str
    staked_amount: int = 0
    locked_until: float = 0.0
    tier: str = "bronze"


@dataclass
class AgentAllowance:
    """Limites de gasto por período."""
    agent_id: str
    daily_limit: int
    weekly_limit: int
    daily_spent: int = 0
    weekly_spent: int = 0
    last_daily_reset: str = ""
    last_weekly_reset: str = ""


# ============================================================
# TokenEconomy Simplificado (inline para evitar dependência externa)
# ============================================================

class TokenEconomy:
    """Token Economy Core — operações financeiras básicas."""

    def __init__(self, symbol: str = "OPEN", admin_id: str = "admin"):
        self.symbol = symbol
        self.admin_id = admin_id
        self._wallets: dict[str, int] = {}
        self._nonces: dict[str, int] = {}
        self._ledger: list[TokenTransaction] = []
        self._tx_counter: int = 0
        self._total_minted: int = 0
        self._total_burned: int = 0
        self._fee_schedules: dict[str, FeeSchedule] = {
            "compute": FeeSchedule("compute", base_fee=10),
            "storage": FeeSchedule("storage", base_fee=5),
            "mcp_call": FeeSchedule("mcp_call", base_fee=2),
            "llm_token": FeeSchedule("llm_token", base_fee=1),
        }
        self._demand_levels: dict[str, str] = {}
        self.audit_trail: list[AuditEntry] = []

    def _next_tx_id(self) -> str:
        self._tx_counter += 1
        return f"TX-{self._tx_counter:06d}"

    def _init_wallet(self, agent_id: str) -> None:
        if agent_id not in self._wallets:
            self._wallets[agent_id] = 0
            self._nonces[agent_id] = 0

    def _next_nonce(self, agent_id: str) -> int:
        self._init_wallet(agent_id)
        nonce = self._nonces[agent_id]
        self._nonces[agent_id] += 1
        return nonce

    def _append_ledger(self, tx: TokenTransaction) -> None:
        self._ledger.append(tx)

    def _sign(self, raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _audit(self, agent_id: str, action: str, params: dict) -> None:
        entry = AuditEntry(
            agent_id=agent_id,
            service="token-economy",
            action=action,
            params=params,
            result="ok",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        raw = f"{entry.agent_id}|{entry.service}|{entry.action}|{json.dumps(params, sort_keys=True)}|{entry.timestamp}"
        entry.hash = hashlib.sha256(raw.encode()).hexdigest()
        self.audit_trail.append(entry)

    def balance(self, agent_id: str) -> int:
        self._init_wallet(agent_id)
        return self._wallets[agent_id]

    def total_supply(self) -> int:
        return self._total_minted - self._total_burned

    @property
    def ledger(self) -> list[TokenTransaction]:
        return list(self._ledger)

    def mint(self, agent_id: str, amount: int, caller: str = "admin") -> str:
        if caller != self.admin_id:
            raise UnauthorizedMintError(f"Apenas {self.admin_id} pode emitir tokens")
        if amount <= 0:
            raise ValueError("Amount deve ser positivo")
        self._init_wallet(agent_id)
        self._wallets[agent_id] += amount
        self._total_minted += amount
        nonce = self._next_nonce(agent_id)
        raw = f"mint|{agent_id}|{amount}|{nonce}"
        tx = TokenTransaction(
            tx_id=self._next_tx_id(),
            from_agent="__reserve__",
            to_agent=agent_id,
            amount=amount,
            token_symbol=self.symbol,
            timestamp=time.time(),
            reason="mint",
            nonce=nonce,
            signature=self._sign(raw)
        )
        self._append_ledger(tx)
        self._audit(agent_id, "token_mint", {"amount": amount})
        return tx.tx_id

    def transfer(self, from_agent: str, to_agent: str, amount: int) -> str:
        if amount <= 0:
            raise ValueError("Amount deve ser positivo")
        self._init_wallet(from_agent)
        self._init_wallet(to_agent)
        if self._wallets[from_agent] < amount:
            raise InsufficientBalanceError(
                f"Saldo insuficiente: {self._wallets[from_agent]} < {amount}"
            )
        self._wallets[from_agent] -= amount
        self._wallets[to_agent] += amount
        nonce = self._next_nonce(from_agent)
        raw = f"transfer|{from_agent}|{to_agent}|{amount}|{nonce}"
        tx = TokenTransaction(
            tx_id=self._next_tx_id(),
            from_agent=from_agent,
            to_agent=to_agent,
            amount=amount,
            token_symbol=self.symbol,
            timestamp=time.time(),
            reason="transfer",
            nonce=nonce,
            signature=self._sign(raw)
        )
        self._append_ledger(tx)
        self._audit(from_agent, "token_transfer", {"to": to_agent, "amount": amount})
        return tx.tx_id

    def burn(self, agent_id: str, amount: int) -> str:
        if amount <= 0:
            raise ValueError("Amount deve ser positivo")
        self._init_wallet(agent_id)
        if self._wallets[agent_id] < amount:
            raise InsufficientBalanceError(
                f"Saldo insuficiente para burn: {self._wallets[agent_id]} < {amount}"
            )
        self._wallets[agent_id] -= amount
        self._total_burned += amount
        nonce = self._next_nonce(agent_id)
        raw = f"burn|{agent_id}|{amount}|{nonce}"
        tx = TokenTransaction(
            tx_id=self._next_tx_id(),
            from_agent=agent_id,
            to_agent="__burn__",
            amount=amount,
            token_symbol=self.symbol,
            timestamp=time.time(),
            reason="burn",
            nonce=nonce,
            signature=self._sign(raw)
        )
        self._append_ledger(tx)
        self._audit(agent_id, "token_burn", {"amount": amount})
        return tx.tx_id

    def calculate_fee(self, resource_type: str, demand_level: str = "medium") -> int:
        schedule = self._fee_schedules.get(resource_type)
        if not schedule:
            raise ValueError(f"Recurso desconhecido: {resource_type}")
        multiplier = {"low": 1.0, "medium": 2.0, "high": 4.0}.get(demand_level, 1.0)
        discount = schedule.agent_discount
        raw_fee = schedule.base_fee * multiplier
        final_fee = int(raw_fee * (1.0 - discount))
        return max(final_fee, 1)


# ============================================================
# AgentEconomics — Camada de Economia de Agentes (SPEC-023)
# ============================================================

class AgentEconomics:
    """
    Gerencia precificação, rate limiting, staking, slashing,
    allowances e tiers para agentes OpenCode.
    """

    def __init__(self, economy: Optional[TokenEconomy] = None,
                 daily_limit: int = 1000,
                 weekly_limit: int = 5000):
        self.economy = economy or TokenEconomy()
        self._operation_costs: dict[str, OperationCost] = {
            "execute_task": OperationCost("execute_task", base_cost=50),
            "mcp_call": OperationCost("mcp_call", base_cost=20),
            "llm_inference": OperationCost("llm_inference", base_cost=10),
        }
        self._min_balances: dict[str, int] = {}  # agent_id → saldo mínimo
        self._stakes: dict[str, AgentStakeInfo] = {}
        self._allowances: dict[str, AgentAllowance] = {}
        self._default_daily_limit = daily_limit
        self._default_weekly_limit = weekly_limit
        self._slash_audit: list[dict] = []

    # ---- Pricing ----

    def pricing(self, op_type: str) -> int:
        """Retorna custo base de um tipo de operação."""
        cost = self._operation_costs.get(op_type)
        if not cost:
            raise ValueError(f"Tipo de operação desconhecido: {op_type}")
        return cost.base_cost

    # ---- Rate Limiting ----

    def set_min_balance(self, agent_id: str, min_balance: int) -> None:
        """Define saldo mínimo para o agente operar."""
        self._min_balances[agent_id] = min_balance

    def check_balance(self, agent_id: str) -> bool:
        """Verifica se agente tem saldo acima do mínimo."""
        min_bal = self._min_balances.get(agent_id, 0)
        return self.economy.balance(agent_id) >= min_bal

    def execute(self, agent_id: str, op_type: str,
                params: Optional[dict] = None) -> str:
        """
        Executa uma operação: verifica saldo mínimo, allowance,
        deduz custo e registra no ledger.
        """
        cost = self.pricing(op_type)

        # Rate limiting: saldo mínimo
        min_bal = self._min_balances.get(agent_id, 0)
        balance = self.economy.balance(agent_id)
        if balance < min_bal:
            raise InsufficientBalanceError(
                f"Agente {agent_id} tem saldo {balance}, mínimo {min_bal}"
            )

        # Allowance: verificar limite diário
        if not self._check_allowance_internal(agent_id, cost):
            raise RateLimitExceeded(
                f"Agente {agent_id} excedeu allowance diário"
            )

        # Deduzir custo via transfer para a reserva
        from_balance = self.economy.balance(agent_id)
        if from_balance < cost:
            raise InsufficientBalanceError(
                f"Saldo insuficiente: {from_balance} < {cost}"
            )
        self.economy.transfer(agent_id, "__fee_reserve__", cost)

        # Atualizar allowance spent
        self._record_spend(agent_id, cost)

        return f"exec-{op_type}-{agent_id}"

    # ---- Staking ----

    def stake(self, agent_id: str, amount: int) -> str:
        """Trava tokens para obter benefícios de tier."""
        balance = self.economy.balance(agent_id)
        if balance < amount:
            raise InsufficientBalanceError(
                f"Saldo insuficiente para staking: {balance} < {amount}"
            )

        # Transferir stake para reserva de staking
        self.economy.transfer(agent_id, "__stake_reserve__", amount)

        stake_info = self._stakes.get(agent_id)
        if stake_info:
            stake_info.staked_amount += amount
        else:
            stake_info = AgentStakeInfo(
                agent_id=agent_id,
                staked_amount=amount,
                locked_until=time.time() + 86400 * 7,  # 7 dias
            )
        self._stakes[agent_id] = stake_info
        self._recompute_tier(agent_id)
        return f"stake-{agent_id}"

    def unstake(self, agent_id: str, amount: int) -> str:
        """Libera tokens staked (se período de lock expirou)."""
        stake_info = self._stakes.get(agent_id)
        if not stake_info or stake_info.staked_amount < amount:
            raise InsufficientBalanceError("Stake insuficiente")

        if time.time() < stake_info.locked_until:
            raise PermissionError("Stake ainda está em período de lock")

        stake_info.staked_amount -= amount
        # Devolver da reserva de staking
        self.economy.transfer("__stake_reserve__", agent_id, amount)
        self._recompute_tier(agent_id)
        return f"unstake-{agent_id}"

    def get_stake(self, agent_id: str) -> int:
        """Retorna quantidade de tokens staked."""
        info = self._stakes.get(agent_id)
        return info.staked_amount if info else 0

    def get_tier(self, agent_id: str) -> str:
        """Retorna tier atual do agente."""
        info = self._stakes.get(agent_id)
        return info.tier if info else "bronze"

    # ---- Slashing ----

    def slash(self, agent_id: str, amount: int, reason: str) -> str:
        """Penaliza agente queimando tokens (primeiro staked, depois saldo)."""
        stake_info = self._stakes.get(agent_id)
        # Prioridade: queimar do stake primeiro
        remaining = amount
        if stake_info and stake_info.staked_amount > 0:
            to_burn = min(stake_info.staked_amount, remaining)
            stake_info.staked_amount -= to_burn
            self.economy.burn("__stake_reserve__", to_burn)
            remaining -= to_burn
            self._recompute_tier(agent_id)

        # Se ainda restar, queimar do saldo livre
        if remaining > 0:
            self.economy.burn(agent_id, remaining)

        # Registrar no audit de slashing
        entry = {
            "agent_id": agent_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        }
        self._slash_audit.append(entry)
        self.economy._audit(agent_id, "token_slash",
                           {"amount": amount, "reason": reason})
        return f"slash-{agent_id}"

    # ---- Allowance ----

    def check_allowance(self, agent_id: str, amount: int) -> bool:
        """Verifica e consome allowance — retorna True se aprovado."""
        if not self._check_allowance_internal(agent_id, amount):
            return False
        self._record_spend(agent_id, amount)
        return True

    def _check_allowance_internal(self, agent_id: str, amount: int) -> bool:
        allowance = self._allowances.get(agent_id)
        if not allowance:
            # Cria allowance default na primeira verificação
            allowance = AgentAllowance(
                agent_id=agent_id,
                daily_limit=self._default_daily_limit,
                weekly_limit=self._default_weekly_limit,
            )
            self._allowances[agent_id] = allowance

        today = time.strftime("%Y-%m-%d")
        week = time.strftime("%Y-W%W")

        # Reset diário
        if allowance.last_daily_reset != today:
            allowance.daily_spent = 0
            allowance.last_daily_reset = today

        # Reset semanal
        if allowance.last_weekly_reset != week:
            allowance.weekly_spent = 0
            allowance.last_weekly_reset = week

        # Verificar limites
        if allowance.daily_spent + amount > allowance.daily_limit:
            return False
        if allowance.weekly_spent + amount > allowance.weekly_limit:
            return False
        return True

    def _record_spend(self, agent_id: str, amount: int) -> None:
        allowance = self._allowances.get(agent_id)
        if allowance:
            allowance.daily_spent += amount
            allowance.weekly_spent += amount

    # ---- Tier System ----

    TIER_THRESHOLDS = {
        "gold": 5000,
        "silver": 1000,
        "bronze": 0,
    }

    TIER_DISCOUNTS = {
        "gold": 0.5,
        "silver": 0.25,
        "bronze": 0.0,
    }

    def _recompute_tier(self, agent_id: str) -> None:
        """Recomputa tier baseado no stake total."""
        stake_info = self._stakes.get(agent_id)
        if not stake_info:
            return
        staked = stake_info.staked_amount
        if staked >= self.TIER_THRESHOLDS["gold"]:
            stake_info.tier = "gold"
        elif staked >= self.TIER_THRESHOLDS["silver"]:
            stake_info.tier = "silver"
        else:
            stake_info.tier = "bronze"

    def calculate_operation_cost(self, agent_id: str, op_type: str) -> int:
        """Calcula custo de operação com desconto por tier."""
        base = self.pricing(op_type)
        tier = self.get_tier(agent_id)
        discount = self.TIER_DISCOUNTS.get(tier, 0.0)
        final = int(base * (1.0 - discount))
        return max(final, 1)

    # ---- Estado ----

    @property
    def slash_audit(self) -> list[dict]:
        """Retorna histórico de slashing."""
        return list(self._slash_audit)


# ============================================================
# Testes (CT-01 a CT-06)
# ============================================================

class TestOperationPricing:
    """CT-01: Agent Operation Pricing — Deduzir custo da carteira."""

    def test_operation_pricing(self):
        econ = AgentEconomics()
        econ.economy.mint("agent-a", 1000)
        op_cost = econ.pricing("mcp_call")
        assert op_cost == 20
        tx_id = econ.execute("agent-a", "mcp_call")
        assert tx_id.startswith("exec-")
        assert econ.economy.balance("agent-a") == 980  # 1000 - 20


class TestRateLimiting:
    """CT-02: Token-Based Rate Limiting — Bloquear operação sem saldo mínimo."""

    def test_rate_limiting(self):
        econ = AgentEconomics()
        econ.set_min_balance("agent-a", 500)
        econ.economy.mint("agent-a", 100)  # abaixo do mínimo
        with pytest.raises(InsufficientBalanceError):
            econ.execute("agent-a", "mcp_call")

    def test_rate_limiting_ok_when_above(self):
        """Agente com saldo acima do mínimo consegue operar."""
        econ = AgentEconomics()
        econ.set_min_balance("agent-a", 500)
        econ.economy.mint("agent-a", 1000)
        tx_id = econ.execute("agent-a", "execute_task")
        assert tx_id.startswith("exec-")
        assert econ.economy.balance("agent-a") == 950  # 1000 - 50


class TestAgentStaking:
    """CT-03: Agent Staking — Travar tokens e verificar tier."""

    def test_agent_staking(self):
        econ = AgentEconomics()
        econ.economy.mint("agent-a", 5000)
        result = econ.stake("agent-a", 3000)
        assert result.startswith("stake-")
        assert econ.get_stake("agent-a") == 3000
        assert econ.get_tier("agent-a") == "silver"
        # Saldo livre = 5000 - 3000 = 2000
        assert econ.economy.balance("agent-a") == 2000

    def test_staking_insufficient_balance(self):
        """Staking com saldo insuficiente é rejeitado."""
        econ = AgentEconomics()
        econ.economy.mint("agent-a", 100)
        with pytest.raises(InsufficientBalanceError):
            econ.stake("agent-a", 500)


class TestAgentSlashing:
    """CT-04: Slashing por Má Conduta — Penalizar agente."""

    def test_agent_slashing(self):
        econ = AgentEconomics()
        econ.economy.mint("agent-a", 5000)
        econ.stake("agent-a", 3000)
        before_supply = econ.economy.total_supply()
        result = econ.slash("agent-a", 1000, "violation")
        assert result.startswith("slash-")
        # Stake reduzido de 3000 para 2000
        assert econ.get_stake("agent-a") == 2000
        # Supply total = 5000 - 1000 (burned)
        assert econ.economy.total_supply() == before_supply - 1000
        # Audit trail registrado
        assert len(econ.slash_audit) == 1
        assert econ.slash_audit[0]["reason"] == "violation"

    def test_slash_from_balance_when_no_stake(self):
        """Slashing sem stake atinge saldo livre."""
        econ = AgentEconomics()
        econ.economy.mint("agent-a", 500)
        before = econ.economy.total_supply()
        econ.slash("agent-a", 100, "inactivity")
        assert econ.economy.balance("agent-a") == 400
        assert econ.economy.total_supply() == before - 100


class TestSpendingAllowance:
    """CT-05: Spending Allowance — Respeitar limite diário."""

    def test_spending_allowance(self):
        econ = AgentEconomics(daily_limit=500)
        econ.economy.mint("agent-a", 5000)
        # Primeira operação ok (300 < 500)
        ok1 = econ.check_allowance("agent-a", 300)
        assert ok1 is True
        # Segunda operação excede (300 + 300 > 500)
        ok2 = econ.check_allowance("agent-a", 300)
        assert ok2 is False

    def test_allowance_blocked_execution(self):
        """Execução bloqueada se allowance for excedido."""
        econ = AgentEconomics(daily_limit=100)
        econ.economy.mint("agent-a", 5000)
        econ.execute("agent-a", "execute_task")  # custa 50, ok
        econ.execute("agent-a", "execute_task")  # custa 50, total 100, ok
        with pytest.raises(RateLimitExceeded):
            econ.execute("agent-a", "mcp_call")  # custa 20, excede 100


class TestTierBenefits:
    """CT-06: Agent Tier Benefits — Gold tier recebe desconto."""

    def test_tier_benefits(self):
        econ = AgentEconomics()
        econ.economy.mint("agent-a", 10000)
        econ.stake("agent-a", 8000)
        assert econ.get_tier("agent-a") == "gold"
        # Gold tier: 50% discount no custo
        base_cost = econ.pricing("mcp_call")  # 20
        discounted = econ.calculate_operation_cost("agent-a", "mcp_call")
        expected = int(base_cost * 0.5)  # 10
        assert discounted == expected

    def test_silver_tier_discount(self):
        """Silver tier recebe 25% de desconto."""
        econ = AgentEconomics()
        econ.economy.mint("agent-b", 5000)
        econ.stake("agent-b", 2000)  # silver
        assert econ.get_tier("agent-b") == "silver"
        discounted = econ.calculate_operation_cost("agent-b", "mcp_call")
        expected = int(20 * 0.75)  # 15
        assert discounted == expected

    def test_bronze_no_discount(self):
        """Bronze tier não recebe desconto."""
        econ = AgentEconomics()
        econ.economy.mint("agent-c", 500)
        discounted = econ.calculate_operation_cost("agent-c", "mcp_call")
        assert discounted == 20  # sem desconto
