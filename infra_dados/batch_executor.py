# -*- coding: utf-8 -*-
"""R832 — batch_executor (infra_dados).
Keywords: batch, batch-executor, executor, batch-executor. Categoria: batch_executor."""
from __future__ import annotations
def order(jobs=None) -> dict:
    jobs = list(jobs or [])
    a = jobs[0] if jobs else None
    return {"order": sorted(jobs), "a": a, "executor": "batch_executor", "batch": True}
