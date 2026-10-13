# -*- coding: utf-8 -*-
"""R832 — context_manager (mci).
Keywords: context_manager, context-manager, context manager, contextscout. Categoria: context_manager."""
from __future__ import annotations
def budget(text: str, max_chars: int = 1000) -> dict:
    t = text or ""
    trunc = len(t) > max_chars
    return {"kept": t[:max_chars], "truncated": trunc, "trunc": trunc, "original_len": len(t), "manager": "context_manager"}
