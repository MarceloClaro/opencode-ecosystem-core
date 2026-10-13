# -*- coding: utf-8 -*-
"""R832 — bernstein_orchestrator: maestro multi-agente (agents/).
Keywords: bernstein, bernstein-orchestrator, maestro. Categoria: bernstein_orchestrator."""
from __future__ import annotations
def describe() -> dict:
    return {"agent": "bernstein_orchestrator", "role": "maestro", "capabilities": ["plan", "delegate", "review"]}
def delegate(task: str) -> dict:
    t = (task or "").strip()
    if not t:
        return {"approved": False, "reason": "tarefa vazia", "agent": "bernstein_orchestrator"}
    return {"approved": True, "agent": "bernstein_orchestrator", "plan": ["decompor", "delegar", "verificar"], "task": t[:200]}
