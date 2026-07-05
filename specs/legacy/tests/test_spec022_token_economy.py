"""
SPEC-022: Token Economy Core — 8 CTs (TDD)
Round 18: Sistema de Incentivos Econômicos para Agentes OpenCode
"""
import pytest
import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional
from conftest import AuditEntry


# ============================================================
# Exceções
# ============================================================

class InsufficientBalanceError(Exception):
    """Saldo insuficiente para transferência ou burn."""
    pass


class UnauthorizedMintError(Exception):
    """Tentativa de mint sem autorização."""
    pass


# ============================================================
# Implementação sob teste
# ============================================================

@dataclass(frozen=True)
class TokenTransaction:
    """Transação imutável no ledger de tokens."""
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


class TokenEconomy:
    """
    Sistema de Token Economy para agentes OpenCode.
    Gerencia mint, transfer, burn, ledger, fee market e recompensas.
    """

    def __init__(self, symbol: str = "OPEN", admin_id: str = "admin"):
        self.symbol = symbol
        self.admin_id = admin_id
        self._wallets: dict[str, int] = {}          # agent_id → balance
        self._nonces: dict[str, int] = {}            # agent_id → nonce
        self._ledger: list[TokenTransaction] = []    # append-only
        self._tx_counter: int = 0
        self._total_minted: int = 0
        self._total_burned: int = 0
        self._fee_schedules: dict[str, FeeSchedule] = {
            "compute": FeeSchedule("compute", base_fee=10, demand_multiplier=1.0),
            "storage": FeeSchedule("storage", base_fee=5, demand_multiplier=1.0),
            "mcp_call": FeeSchedule("mcp_call", base_fee=2, demand_multiplier=1.0),
            "llm_token": FeeSchedule("llm_token", base_fee=1, demand_multiplier=1.0),
        }
        self._demand_levels: dict[str, str] = {}     # resource → "low"|"medium"|"high"
        self.audit_trail: list[AuditEntry] = []

    # ---- Helpers internos ----

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

    # ---- API Pública ----

    def balance(self, agent_id: str) -> int:
        """Retorna saldo de um agente."""
        self._init_wallet(agent_id)
        return self._wallets[agent_id]

    def total_supply(self) -> int:
        """Supply circulante total (minted - burned)."""
        return self._total_minted - self._total_burned

    @property
    def ledger(self) -> list[TokenTransaction]:
        """Retorna cópia do ledger (imutável externamente)."""
        return list(self._ledger)

    # --- Mint ---

    def mint(self, agent_id: str, amount: int, caller: str = "admin") -> str:
        """Emitir novos tokens para um agente."""
        if caller != self.admin_id:
            raise UnauthorizedMintError(
                f"Apenas {self.admin_id} pode emitir tokens"
            )
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

    # --- Transfer ---

    def transfer(self, from_agent: str, to_agent: str,
                 amount: int) -> str:
        """Transferir tokens entre agentes."""
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
        self._audit(from_agent, "token_transfer",
                    {"to": to_agent, "amount": amount})
        return tx.tx_id

    # --- Burn ---

    def burn(self, agent_id: str, amount: int) -> str:
        """Queimar tokens (destruir permanentemente)."""
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

    # --- Fee Market ---

    def set_demand(self, resource_type: str, level: str) -> None:
        """Define nível de demanda para um recurso."""
        self._demand_levels[resource_type] = level

    def calculate_fee(self, resource_type: str,
                      demand_level: Optional[str] = None) -> int:
        """Calcular taxa para um tipo de recurso."""
        schedule = self._fee_schedules.get(resource_type)
        if not schedule:
            raise ValueError(f"Recurso desconhecido: {resource_type}")
        level = demand_level or self._demand_levels.get(resource_type, "medium")
        multiplier = {"low": 1.0, "medium": 2.0, "high": 4.0}.get(level, 1.0)
        discount = schedule.agent_discount
        raw_fee = schedule.base_fee * multiplier
        final_fee = int(raw_fee * (1.0 - discount))
        return max(final_fee, 1)

    # --- Reward ---

    def reward(self, agent_id: str, amount: int,
               reason: str = "contribution",
               caller: str = "admin") -> str:
        """Recompensar agente por contribuição verificada."""
        if caller != self.admin_id:
            # Rewards só podem ser emitidas pelo admin/reserve
            raise UnauthorizedMintError(
                "Apenas admin pode distribuir recompensas"
            )
        self._init_wallet(agent_id)
        # Reward = mint da reserva
        return self.mint(agent_id, amount, caller=caller)

    # --- Ledger Query ---

    def get_transactions(self, agent_id: str,
                         limit: int = 10) -> list[TokenTransaction]:
        """Histórico de transações de um agente."""
        result = []
        for tx in reversed(self._ledger):
            if tx.from_agent == agent_id or tx.to_agent == agent_id:
                result.append(tx)
                if len(result) >= limit:
                    break
        return result


# ============================================================
# Testes (CT-01 a CT-08)
# ============================================================

class TestTokenMint:
    """CT-01: Mint — Emissão de Tokens"""

    def test_token_mint(self):
        economy = TokenEconomy()
        tx_id = economy.mint("agent-a", 1000)
        assert economy.balance("agent-a") == 1000
        assert tx_id.startswith("TX-")


class TestTokenTransfer:
    """CT-02: Transfer — Transferência entre Agentes"""

    def test_token_transfer(self):
        economy = TokenEconomy()
        economy.mint("agent-a", 1000)
        economy.transfer("agent-a", "agent-b", 400)
        assert economy.balance("agent-a") == 600
        assert economy.balance("agent-b") == 400


class TestTokenBurn:
    """CT-03: Burn — Queima de Tokens"""

    def test_token_burn(self):
        economy = TokenEconomy()
        economy.mint("agent-a", 1000)
        before = economy.total_supply()
        economy.burn("agent-a", 300)
        assert economy.balance("agent-a") == 700
        assert economy.total_supply() == before - 300


class TestInsufficientBalance:
    """CT-04: Saldo Insuficiente — Rejeitar transferência"""

    def test_insufficient_balance(self):
        economy = TokenEconomy()
        economy.mint("agent-a", 100)
        with pytest.raises(InsufficientBalanceError):
            economy.transfer("agent-a", "agent-b", 200)
        assert economy.balance("agent-a") == 100  # saldo preservado


class TestLedgerImmutability:
    """CT-05: Ledger Imutável — Append-only"""

    def test_ledger_immutability(self):
        economy = TokenEconomy()
        economy.mint("agent-a", 500)
        economy.transfer("agent-a", "agent-b", 200)
        assert len(economy.ledger) == 2
        # Verifica que transações são frozen (imutáveis)
        tx = economy.ledger[1]
        assert tx.reason == "transfer"
        assert tx.from_agent == "agent-a"
        assert tx.to_agent == "agent-b"
        assert tx.amount == 200
        # Tentativa de alterar transação frozen deve falhar via dataclass
        # (a anotação frozen=True gera __setattr__ que levanta FrozenInstanceError)
        import dataclasses
        with pytest.raises(dataclasses.FrozenInstanceError):
            tx.amount = 999


class TestFeeMarketDynamic:
    """CT-06: Fee Market — Taxa Dinâmica por Demanda"""

    def test_fee_market_dynamic(self):
        economy = TokenEconomy()
        economy.set_demand("compute", "high")
        economy.set_demand("compute", "low")
        fee_high = economy.calculate_fee("compute", demand_level="high")
        fee_low = economy.calculate_fee("compute", demand_level="low")
        assert fee_high > fee_low
        # Default (medium) deve ficar entre low e high
        fee_medium = economy.calculate_fee("compute", demand_level="medium")
        assert fee_low < fee_medium < fee_high


class TestAgentReward:
    """CT-07: Reward — Recompensa por Contribuição"""

    def test_agent_reward(self):
        economy = TokenEconomy()
        economy.mint("reserve", 5000)
        # Reward emite novos tokens (mint da reserva)
        economy.reward("agent-a", 200, reason="code_review")
        assert economy.balance("agent-a") == 200


class TestAuditIntegration:
    """CT-08: Audit — Integração com Audit Trail"""

    def test_audit_integration(self):
        economy = TokenEconomy()
        economy.mint("agent-a", 1000)
        assert len(economy.audit_trail) >= 1
        last = economy.audit_trail[-1]
        assert last.action == "token_mint"
        assert last.params.get("amount") == 1000
        assert last.hash != ""

    def test_ledger_transparency(self):
        """Verificação adicional: ledger contém metadados completos."""
        economy = TokenEconomy()
        economy.mint("agent-a", 500)
        economy.transfer("agent-a", "agent-b", 200)
        economy.burn("agent-b", 50)
        txs = economy.get_transactions("agent-a")
        assert len(txs) == 2  # mint + transfer
        assert txs[0].reason == "transfer"  # mais recente primeiro
