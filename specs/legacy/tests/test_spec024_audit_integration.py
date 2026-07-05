"""
SPEC-024: Audit Integration — Relatórios e Verificação Econômica
Round 18: 4 CTs sobre balance report, spending report,
cross-reference ledger↔audit e health metrics.
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


# ============================================================
# Dataclasses de Relatórios
# ============================================================

@dataclass
class TokenTransaction:
    """Transação no ledger."""
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
    """Tabela de taxas."""
    resource_type: str
    base_fee: int
    demand_multiplier: float = 1.0
    agent_discount: float = 0.0


@dataclass
class BalanceReport:
    """Relatório consolidado de saldos."""
    generated_at: str
    total_agents: int
    total_supply: int
    agents: list[dict]  # [{agent_id, balance}]


@dataclass
class SpendingSummary:
    """Sumário de gastos de um agente."""
    agent_id: str
    period: str
    total_spent: int
    by_reason: dict
    transaction_count: int


@dataclass
class EconHealthMetrics:
    """Métricas de saúde econômica do ecossistema."""
    total_supply: int
    total_burned: int
    fee_revenue: int
    transaction_count: int
    unique_agents: int
    velocity: float


# ============================================================
# TokenEconomy Simplificado (inline)
# ============================================================

class TokenEconomy:
    """Token Economy Core."""

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
            "mcp_call": FeeSchedule("mcp_call", base_fee=2),
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
        self._audit(from_agent, "token_transfer",
                    {"to": to_agent, "amount": amount})
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


# ============================================================
# TokenAudit — Camada de Auditoria e Relatórios (SPEC-024)
# ============================================================

class TokenAudit:
    """
    Camada de auditoria sobre TokenEconomy.
    Gera relatórios de balanço, gastos, verificação cruzada
    e métricas de saúde econômica.
    """

    def __init__(self, economy: Optional[TokenEconomy] = None):
        self.economy = economy or TokenEconomy()

    # ---- CT-01: Balance Report ----

    def generate_balance_report(self) -> BalanceReport:
        """Relatório consolidado de saldos de todos os agentes."""
        agents = []
        # Extrai agentes da carteira
        for agent_id, balance in self.economy._wallets.items():
            agents.append({
                "agent_id": agent_id,
                "balance": balance,
            })
        # Ordena por balance descendente
        agents.sort(key=lambda a: a["balance"], reverse=True)
        report = BalanceReport(
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            total_agents=len(agents),
            total_supply=self.economy.total_supply(),
            agents=agents,
        )
        return report

    # ---- CT-02: Spending Report ----

    def spending_report(self, agent_id: str, period: str = "all") -> SpendingSummary:
        """Sumário de gastos de um agente por período."""
        total_spent = 0
        by_reason: dict[str, int] = {}
        count = 0

        for tx in self.economy.ledger:
            # Filtra transações debitadas do agente
            if tx.from_agent == agent_id:
                # Ignora mint (é crédito, não gasto)
                if tx.reason == "mint":
                    continue
                total_spent += tx.amount
                by_reason[tx.reason] = by_reason.get(tx.reason, 0) + tx.amount
                count += 1

        report = SpendingSummary(
            agent_id=agent_id,
            period=period,
            total_spent=total_spent,
            by_reason=by_reason,
            transaction_count=count,
        )
        return report

    # ---- CT-03: Cross-Reference ----

    def cross_reference(self) -> list[dict]:
        """
        Verifica consistência entre ledger (transações) e audit trail.
        Retorna lista de mismatches (vazia se consistente).
        """
        mismatches: list[dict] = []

        # Verificação 1: quantidade de entradas
        if len(self.economy.ledger) != len(self.economy.audit_trail):
            mismatches.append({
                "type": "count_mismatch",
                "ledger": len(self.economy.ledger),
                "audit": len(self.economy.audit_trail),
            })
            return mismatches

        # Verificação 2: correspondência 1:1 por ação
        # Mapeia audit actions para ledger reasons esperados
        action_to_reason = {
            "token_mint": "mint",
            "token_transfer": "transfer",
            "token_burn": "burn",
        }

        for i, (tx, audit) in enumerate(zip(self.economy.ledger,
                                             self.economy.audit_trail)):
            # O reason da transação deve corresponder ao audit action
            expected_reason = action_to_reason.get(audit.action)
            if expected_reason and tx.reason != expected_reason:
                mismatches.append({
                    "type": "action_mismatch",
                    "index": i,
                    "ledger_reason": tx.reason,
                    "audit_action": audit.action,
                })

        return mismatches

    # ---- CT-04: Health Metrics ----

    def health_metrics(self) -> EconHealthMetrics:
        """Métricas de saúde do ecossistema."""
        ledger = self.economy.ledger

        # Calcular fee revenue (taxas coletadas)
        fee_revenue = 0
        for tx in ledger:
            if tx.reason == "fee" or tx.to_agent == "__fee_reserve__":
                fee_revenue += tx.amount

        # Agentes únicos
        unique_agents = set()
        for tx in ledger:
            if tx.from_agent and tx.from_agent not in ("__reserve__", "__burn__"):
                unique_agents.add(tx.from_agent)
            if tx.to_agent and tx.to_agent not in ("__reserve__", "__burn__"):
                unique_agents.add(tx.to_agent)

        # Velocidade: volume de transferência / supply total
        transfer_volume = 0
        for tx in ledger:
            if tx.reason == "transfer":
                transfer_volume += tx.amount

        supply = self.economy.total_supply()
        velocity = transfer_volume / supply if supply > 0 else 0.0

        metrics = EconHealthMetrics(
            total_supply=self.economy.total_supply(),
            total_burned=self.economy._total_burned,
            fee_revenue=fee_revenue,
            transaction_count=len(ledger),
            unique_agents=len(unique_agents),
            velocity=round(velocity, 4),
        )
        return metrics


# ============================================================
# Testes (CT-01 a CT-04)
# ============================================================

class TestBalanceReport:
    """CT-01: Balance Report — Relatório consolidado."""

    def test_balance_report(self):
        audit = TokenAudit()
        audit.economy.mint("agent-a", 1000)
        audit.economy.mint("agent-b", 500)
        report = audit.generate_balance_report()
        assert report.total_agents == 2
        assert report.total_supply == 1500
        assert len(report.agents) == 2

    def test_balance_report_order(self):
        """Relatório deve vir ordenado por saldo descendente."""
        audit = TokenAudit()
        audit.economy.mint("agent-b", 500)
        audit.economy.mint("agent-a", 1000)
        report = audit.generate_balance_report()
        assert report.agents[0]["balance"] >= report.agents[1]["balance"]


class TestSpendingReport:
    """CT-02: Spending Report — Gastos por agente."""

    def test_spending_report(self):
        audit = TokenAudit()
        audit.economy.mint("agent-a", 1000)
        # Gasta: transfer 200 + burn 100
        audit.economy.transfer("agent-a", "agent-b", 200)
        audit.economy.burn("agent-a", 100)
        report = audit.spending_report("agent-a", period="all")
        assert report.total_spent == 300  # transfer 200 + burn 100
        assert report.transaction_count == 2
        assert "transfer" in report.by_reason
        assert "burn" in report.by_reason

    def test_spending_report_empty(self):
        """Agente sem gastos gera relatório com zero."""
        audit = TokenAudit()
        audit.economy.mint("agent-a", 1000)
        report = audit.spending_report("agent-b", period="all")
        assert report.total_spent == 0
        assert report.transaction_count == 0


class TestCrossReference:
    """CT-03: Cross-Reference Ledger ↔ Audit — Verificação de consistência."""

    def test_cross_reference_consistent(self):
        audit = TokenAudit()
        audit.economy.mint("agent-a", 500)
        audit.economy.transfer("agent-a", "agent-b", 200)
        mismatches = audit.cross_reference()
        assert len(mismatches) == 0  # consistente
        # Ledger e audit trail devem ter mesmo tamanho
        assert len(audit.economy.ledger) == len(audit.economy.audit_trail)

    def test_cross_reference_mismatch_detected(self):
        """Cross-reference detecta inconsistência se audit trail for manipulado."""
        audit = TokenAudit()
        audit.economy.mint("agent-a", 500)
        # Remover um audit entry para simular inconsistência
        original_len = len(audit.economy.audit_trail)
        audit.economy.transfer("agent-a", "agent-b", 200)
        # Injetar uma entrada extra no audit trail
        import copy
        fake_entry = copy.deepcopy(audit.economy.audit_trail[-1])
        fake_entry.action = "fake_action"
        audit.economy.audit_trail.append(fake_entry)
        mismatches = audit.cross_reference()
        assert len(mismatches) > 0  # detectou inconsistência


class TestEconHealth:
    """CT-04: Economic Health Metrics — Métricas do ecossistema."""

    def test_econ_health(self):
        audit = TokenAudit()
        audit.economy.mint("agent-a", 1000)
        audit.economy.mint("agent-b", 500)
        audit.economy.transfer("agent-a", "agent-b", 300)
        audit.economy.burn("agent-a", 100)
        health = audit.health_metrics()
        # total_supply = 1500 - 100 (burn) = 1400
        assert health.total_supply == 1400
        assert health.total_burned == 100
        # transaction_count = 2 mint + 1 transfer + 1 burn = 4
        assert health.transaction_count == 4
        # unique_agents = agent-a, agent-b = 2
        assert health.unique_agents == 2
        # velocity = transfer_volume(300) / supply(1400)
        assert health.velocity > 0
        assert health.velocity < 1

    def test_econ_health_empty(self):
        """Ecossistema vazio deve ter métricas zeradas."""
        audit = TokenAudit()
        health = audit.health_metrics()
        assert health.total_supply == 0
        assert health.total_burned == 0
        assert health.transaction_count == 0
        assert health.unique_agents == 0
        assert health.velocity == 0.0
