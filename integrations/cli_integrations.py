# -*- coding: utf-8 -*-
"""R832 — cli_integrations (integrations).
Keywords: cli, command line, integrations/, opencode_cli, integrations. Categoria: cli_integrations."""
from __future__ import annotations
import shutil
def plan(cmd: str = "status", **_) -> dict:
    return {"cli": True, "integrations": "cli_integrations", "available": shutil.which("opencode") is not None, "argv": ["opencode", cmd]}
