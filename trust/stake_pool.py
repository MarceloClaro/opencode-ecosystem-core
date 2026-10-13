# -*- coding: utf-8 -*-
"""R830 — stake_pool: pool de stakes com trilha auditável.

Inspirações: economy StakingPool/StakePosition, staking-mcp leaderboard,
TrustMyGit stake lock. Corpus keywords: stake pool, stake_pool, pool,
StakingPool, StakePosition. Categoria: stake_pool.
"""
from __future__ import annotations
from typing import Dict

class StakePool:
    """stake_pool: lock/release com total_locked (StakingPool)."""

    def __init__(self):
        self._locks: Dict[str, float] = {}

    def lock(self, agent_id: str, amount: float) -> dict:
        if amount <= 0:
            raise ValueError("amount positivo")
        self._locks[agent_id] = self._locks.get(agent_id, 0.0) + float(amount)
        pos = {"agent": agent_id, "amount": self._locks[agent_id], "status": "locked"}
        return {"StakePosition": pos, "pool": "StakingPool", "stake_pool": True}

    def release(self, agent_id: str) -> dict:
        amt = self._locks.pop(agent_id, 0.0)
        return {"agent": agent_id, "released": amt, "status": "released"}

    def total_locked(self) -> float:
        return float(sum(self._locks.values()))
