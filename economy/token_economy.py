# -*- coding: utf-8 -*-
"""
Token Economy — SPEC-022 a SPEC-025 (portado do OpenCode_Ecosystem)
===================================================================
Economia de agentes do ecossistema:

1. TokenLedger — livro-razão de saldos por agente (créditos OCT: OpenCode Tokens)
2. StakingPool — agentes fazem stake ao aceitar tarefas (compromisso econômico)
3. SlashingEngine — penaliza stake de agentes que falham entregas (SPEC-023)
4. FeeMarket — mercado de taxas por prioridade de tarefa (SPEC-022)
5. TokenEconomyMonitor — auditoria integrada (SPEC-024)

100% stdlib. Persistência opcional via JSON.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

INITIAL_BALANCE = 100.0     # saldo inicial de cada agente (OCT)
MIN_STAKE = 1.0             # stake mínimo por tarefa
SLASH_RATE = 0.5            # fração do stake perdida em falha (SPEC-023)
REWARD_RATE = 0.2           # recompensa proporcional ao stake em sucesso
BASE_FEE = 1.0              # taxa base do fee market
PRIORITY_MULTIPLIERS = {"low": 0.5, "normal": 1.0, "high": 2.0, "critical": 4.0}


@dataclass
class StakePosition:
    """Posição de stake de um agente vinculada a uma tarefa."""
    stake_id: str
    agent_id: str
    task_id: str
    amount: float
    status: str = "locked"  # locked | released | slashed
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None


@dataclass
class FeeQuote:
    """Cotação do fee market para uma tarefa."""
    task_id: str
    priority: str
    base_fee: float
    congestion_multiplier: float
    total_fee: float


class TokenLedger:
    """Livro-razão de saldos (SPEC-022). Auditável: registra todas as transações."""

    def __init__(self):
        self.balances: Dict[str, float] = {}
        self.transactions: List[Dict[str, Any]] = []

    def ensure_account(self, agent_id: str) -> float:
        if agent_id not in self.balances:
            self.balances[agent_id] = INITIAL_BALANCE
            self._log("genesis", agent_id, INITIAL_BALANCE, "Saldo inicial")
        return self.balances[agent_id]

    def transfer(self, from_id: str, to_id: str, amount: float, reason: str = "") -> bool:
        self.ensure_account(from_id)
        self.ensure_account(to_id)
        if amount <= 0 or self.balances[from_id] < amount:
            return False
        self.balances[from_id] -= amount
        self.balances[to_id] += amount
        self._log("transfer", f"{from_id}->{to_id}", amount, reason)
        return True

    def credit(self, agent_id: str, amount: float, reason: str = "") -> None:
        self.ensure_account(agent_id)
        self.balances[agent_id] += amount
        self._log("credit", agent_id, amount, reason)

    def debit(self, agent_id: str, amount: float, reason: str = "") -> bool:
        self.ensure_account(agent_id)
        if self.balances[agent_id] < amount:
            return False
        self.balances[agent_id] -= amount
        self._log("debit", agent_id, amount, reason)
        return True

    def _log(self, kind: str, subject: str, amount: float, reason: str) -> None:
        self.transactions.append({
            "kind": kind, "subject": subject, "amount": round(amount, 4),
            "reason": reason, "timestamp": time.time(),
        })

    def audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.transactions[-limit:]


class StakingPool:
    """Pool de staking (SPEC-023): agentes travam OCT ao aceitar tarefas."""

    def __init__(self, ledger: TokenLedger):
        self.ledger = ledger
        self.positions: Dict[str, StakePosition] = {}

    def stake(self, agent_id: str, task_id: str, amount: float = MIN_STAKE) -> Optional[StakePosition]:
        amount = max(amount, MIN_STAKE)
        if not self.ledger.debit(agent_id, amount, f"stake para {task_id}"):
            return None
        position = StakePosition(
            stake_id=f"stk-{uuid.uuid4().hex[:8]}",
            agent_id=agent_id, task_id=task_id, amount=amount,
        )
        self.positions[position.stake_id] = position
        return position

    def release(self, task_id: str, reward_rate: float = REWARD_RATE) -> List[StakePosition]:
        """Sucesso: devolve o stake + recompensa proporcional."""
        resolved = []
        for pos in self._by_task(task_id, "locked"):
            reward = pos.amount * reward_rate
            self.ledger.credit(pos.agent_id, pos.amount + reward,
                               f"stake liberado + recompensa ({task_id})")
            pos.status = "released"
            pos.resolved_at = time.time()
            resolved.append(pos)
        return resolved

    def slash(self, task_id: str, slash_rate: float = SLASH_RATE) -> List[StakePosition]:
        """Falha: parte do stake é queimada (slashing), o restante volta."""
        resolved = []
        for pos in self._by_task(task_id, "locked"):
            refund = pos.amount * (1.0 - slash_rate)
            if refund > 0:
                self.ledger.credit(pos.agent_id, refund,
                                   f"reembolso parcial pós-slashing ({task_id})")
            pos.status = "slashed"
            pos.resolved_at = time.time()
            resolved.append(pos)
        return resolved

    def _by_task(self, task_id: str, status: str) -> List[StakePosition]:
        return [p for p in self.positions.values()
                if p.task_id == task_id and p.status == status]

    def total_locked(self) -> float:
        return sum(p.amount for p in self.positions.values() if p.status == "locked")


class FeeMarket:
    """Fee market (SPEC-022): o custo de postar tarefas varia com prioridade e congestão."""

    def __init__(self, ledger: TokenLedger):
        self.ledger = ledger
        self.open_tasks = 0
        self.quotes: List[FeeQuote] = []

    def quote(self, task_id: str, priority: str = "normal") -> FeeQuote:
        multiplier = PRIORITY_MULTIPLIERS.get(priority, 1.0)
        # Congestão: cada 10 tarefas abertas aumentam a taxa em 10%
        congestion = 1.0 + (self.open_tasks // 10) * 0.1
        q = FeeQuote(
            task_id=task_id, priority=priority, base_fee=BASE_FEE,
            congestion_multiplier=round(congestion, 2),
            total_fee=round(BASE_FEE * multiplier * congestion, 4),
        )
        self.quotes.append(q)
        return q

    def charge(self, payer_id: str, task_id: str, priority: str = "normal") -> Optional[FeeQuote]:
        q = self.quote(task_id, priority)
        if not self.ledger.debit(payer_id, q.total_fee, f"fee de postagem ({task_id}, {priority})"):
            return None
        self.open_tasks += 1
        return q

    def settle(self) -> None:
        """Marca a resolução de uma tarefa aberta (reduz congestão)."""
        self.open_tasks = max(0, self.open_tasks - 1)


class TokenEconomy:
    """Fachada da economia de agentes (SPEC-022~025) integrada ao orquestrador.

    Ciclo por tarefa:
        fee = economy.post_task(orchestrator_id, task_id, priority)
        economy.commit(agent_id, task_id, stake)      # agente aceita
        economy.resolve(task_id, success=True/False)  # release ou slash
    """

    def __init__(self, state_path: Optional[str] = None):
        self.ledger = TokenLedger()
        self.staking = StakingPool(self.ledger)
        self.fee_market = FeeMarket(self.ledger)
        self.state_path = state_path

    def post_task(self, payer_id: str, task_id: str, priority: str = "normal") -> Optional[FeeQuote]:
        return self.fee_market.charge(payer_id, task_id, priority)

    def commit(self, agent_id: str, task_id: str, stake: float = MIN_STAKE) -> Optional[StakePosition]:
        return self.staking.stake(agent_id, task_id, stake)

    def resolve(self, task_id: str, success: bool) -> Dict[str, Any]:
        if success:
            positions = self.staking.release(task_id)
        else:
            positions = self.staking.slash(task_id)
        self.fee_market.settle()
        return {
            "task_id": task_id,
            "success": success,
            "positions": [asdict(p) for p in positions],
        }

    def balance(self, agent_id: str) -> float:
        return self.ledger.ensure_account(agent_id)

    def report(self) -> Dict[str, Any]:
        """Auditoria integrada (SPEC-024): estado completo da economia."""
        return {
            "balances": {k: round(v, 4) for k, v in sorted(self.ledger.balances.items())},
            "total_locked": round(self.staking.total_locked(), 4),
            "open_tasks": self.fee_market.open_tasks,
            "transactions": len(self.ledger.transactions),
            "stakes": {
                "locked": sum(1 for p in self.staking.positions.values() if p.status == "locked"),
                "released": sum(1 for p in self.staking.positions.values() if p.status == "released"),
                "slashed": sum(1 for p in self.staking.positions.values() if p.status == "slashed"),
            },
        }

    def save(self) -> None:
        if not self.state_path:
            return
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump({
                "balances": self.ledger.balances,
                "transactions": self.ledger.transactions[-500:],
            }, f, ensure_ascii=False, indent=2)


# Singleton do ecossistema
token_economy = TokenEconomy()
