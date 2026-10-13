# -*- coding: utf-8 -*-
"""R832 — git_manager (integrations).
Keywords: git, git-manager, git_manager, github, git-manager. Categoria: git_manager."""
from __future__ import annotations
import shutil
def plan(action: str = "status", **_) -> dict:
    return {"git": True, "git_manager": True, "github": True, "available": shutil.which("git") is not None, "argv": ["git", action]}
