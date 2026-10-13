# -*- coding: utf-8 -*-
"""R832 — cooperative_governance (governanca).
Keywords: cooperative, cooperative_governance, governança, cooperative governance. Categoria: cooperative_governance."""
from __future__ import annotations
def quorum(votes_for: int = 0, total: int = 0, threshold: float = 0.6) -> dict:
    q = (votes_for / total) if total else 0.0
    return {"quorum": q >= threshold, "quorum_str": str(q >= threshold).lower(), "ratio": q, "governance": "cooperative_governance"}
