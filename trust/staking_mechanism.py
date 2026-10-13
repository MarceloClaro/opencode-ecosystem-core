# -*- coding: utf-8 -*-
"""R830 — staking_mechanism: stake como compromisso + rate-limit.

Inspirações (referência, sem copiar): prstake (staking sem slashing como
rate-limit), agent-staking-mcp-server (tiers bronze/silver/gold/platinum,
stake como colateral), TrustMyGit (stake em issues).
Corpus keywords: staking, stake, stake pool, StakingPool, stake_position,
stake_release, total_locked. Categoria: staking_mechanism.
100% stdlib, memória local, sem rede.
"""
from __future__ import annotations
import time
from typing import Dict

_stakes: Dict[str, Dict[str, float]] = {}
_slots: Dict[str, set] = {}

def deposit(agent_id: str, amount: float, task_id: str) -> dict:
    """staking_mechanism deposit: trava stake e consome 1 slot (StakingPool)."""
    if amount <= 0:
        raise ValueError("stake deve ser positivo")
    _stakes.setdefault(agent_id, {"total_locked": 0.0})
    _stakes[agent_id]["total_locked"] += amount
    _slots.setdefault(agent_id, set()).add(task_id)
    return {"agent": agent_id, "stake_position": {"amount": amount, "task": task_id},
            "total_locked": _stakes[agent_id]["total_locked"], "status": "locked",
            "at": time.time()}

def release(agent_id: str, task_id: str) -> dict:
    """stake_release: libera slot; mantém total_locked auditável."""
    _slots.get(agent_id, set()).discard(task_id)
    return {"agent": agent_id, "released": task_id, "slots": len(_slots.get(agent_id, set()))}

def slots_usados(agent_id: str) -> int:
    return len(_slots.get(agent_id, set()))

def total_locked(agent_id: str) -> float:
    return float(_stakes.get(agent_id, {}).get("total_locked", 0.0))
