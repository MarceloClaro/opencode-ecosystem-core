# -*- coding: utf-8 -*-
"""R832 — orchestration_pipeline (mci).
Keywords: orchestration, pipeline/, orchestration.py, stage-orchestrator. Categoria: orchestration_pipeline."""
from __future__ import annotations
from typing import List, Dict
def order(steps: List[Dict]) -> dict:
    done, ordered, remaining = set(), [], list(steps)
    for _ in range(len(steps) + 1):
        prog = False
        for s in list(remaining):
            if all(d in done for d in s.get("deps", [])):
                ordered.append(s["id"]); done.add(s["id"]); remaining.remove(s); prog = True
        if not remaining or not prog:
            break
    return {"order": ordered, "a": ordered[0] if ordered else None, "unresolved": [s["id"] for s in remaining], "pipeline": "orchestration_pipeline"}
