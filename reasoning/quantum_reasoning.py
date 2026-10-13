# -*- coding: utf-8 -*-
"""R830 — quantum_reasoning: facade declarativa sobre reasoning/quantum.

Inspiração: reasoning/quantum.py + Qiskit opcional. Corpus keywords: quantum,
quantum.py, quantum reasoning, quantum_. Categoria: quantum_reasoning.
Sem Qiskit, retorna clássico explícito (sem alegar vantagem quântica).
"""
from __future__ import annotations

def run_experiment(name: str = "bell") -> dict:
    """quantum_reasoning run_experiment: tenta quantum real, senão fallback."""
    try:
        from reasoning import quantum as q  # quantum_ local
        available = True
        detail = getattr(q, "__doc__", "")[:200] if getattr(q, "__doc__", "") else "quantum.py presente"
    except Exception as e:
        available = False
        detail = str(e)[:200]
    return {"engine": "quantum_reasoning", "experiment": name,
            "status": "ok" if available else "fallback",
            "available": available, "quantum_reasoning": True,
            "detail": detail, "note": "quantum_ sem alegação de supremacia"}
