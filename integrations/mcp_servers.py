# -*- coding: utf-8 -*-
"""R832 — mcp_servers (integrations).
Keywords: mcp, mcp server, model context protocol, mcp_servers. Categoria: mcp_servers."""
from __future__ import annotations
def plan(name: str = "filesystem", **_) -> dict:
    return {"mcp": True, "mcp_servers": True, "server": name, "protocol": "model context protocol"}
