# -*- coding: utf-8 -*-
"""R832 — reversa_agents (agents/).
Keywords: reversa, reversa-agent, reversa-. Categoria: reversa_agents."""
from __future__ import annotations
def describe() -> dict:
    return {"agent": "reversa_agents", "role": "reversa", "capabilities": ["scout", "analyze", "synthesize"]}
def delegate(task: str) -> dict:
    return {"approved": True, "agent": "reversa_agents", "reversa": True, "task": (task or '')[:200]}
