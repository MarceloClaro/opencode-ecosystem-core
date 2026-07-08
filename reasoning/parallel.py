# -*- coding: utf-8 -*-
"""
ParallelReasoning — Ensemble multi-thread para motores de raciocínio
====================================================================
SPEC-917: executa motores em paralelo com ThreadPoolExecutor para reduzir
latência do modo ensemble.
"""

from __future__ import annotations

import inspect
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional


class ParallelReasoning:
    """Executor paralelo para `MultiReasoningEngine`."""

    def __init__(self, multi_engine: Any, max_workers: Optional[int] = None):
        self.multi_engine = multi_engine
        self.max_workers = max_workers or min(8, max(1, len(multi_engine.engines)))

    def ensemble(self, query: str, **kwargs) -> Dict[str, Any]:
        """Executa todos os motores em paralelo e agrega o melhor resultado."""
        results: Dict[str, Dict[str, Any]] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_name = {}
            for name, engine in self.multi_engine.engines.items():
                params = set(inspect.signature(engine.reason).parameters)
                filtered = {k: v for k, v in kwargs.items() if k in params}
                future = executor.submit(engine.reason, query, **filtered)
                future_to_name[future] = name

            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    results[name] = future.result().to_dict()
                except Exception as exc:
                    results[name] = {"engine": name, "error": str(exc)[:200]}

        valid = [r for r in results.values() if "confidence" in r]
        best = max(valid, key=lambda r: r["confidence"]) if valid else None

        return {
            "query": query,
            "results": results,
            "best_engine": best["engine"] if best else None,
            "mode": "parallel",
            "workers": self.max_workers,
        }
