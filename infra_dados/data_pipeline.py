# -*- coding: utf-8 -*-
"""R832 — data_pipeline (infra_dados).
Keywords: data/, data pipeline, dataset, evidence_graph. Categoria: data_pipeline."""
from __future__ import annotations
def normalize(rows=None) -> dict:
    rows = rows or []
    clean = [{k: v for k, v in r.items() if v is not None} for r in rows if isinstance(r, dict)]
    return {"rows": clean, "count": len(clean), "dataset": True, "pipeline": "data_pipeline"}
