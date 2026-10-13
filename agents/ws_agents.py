# -*- coding: utf-8 -*-
"""R832 — ws_agents (agents/).
Keywords: ws-coder, ws-researcher, ws-reviewer, ws-scribe. Categoria: ws_agents."""
from __future__ import annotations
def describe() -> dict:
    return {"agent": "ws_agents", "role": "ws", "members": ["ws-coder", "ws-researcher", "ws-reviewer", "ws-scribe"]}
def delegate(task: str) -> dict:
    return {"approved": True, "agent": "ws_agents", "ws": True, "task": (task or '')[:200]}
