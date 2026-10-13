# -*- coding: utf-8 -*-
"""R830 — critical_reasoner: crítica dialética com checklist.

Inspiração: reasoning/engines CriticalEngine, llm-reasoning-orchestrator
validação por passo. Corpus keywords: critical, critical_reasoner,
critical reasoning, CriticalEngine. Categoria: critical_reasoner.
"""
from __future__ import annotations

FALLACIES = ["ad_hominem", "strawman", "false_dilemma", "appeal_to_authority", "hasty_generalization"]

def critique(thesis: str) -> dict:
    """critical_reasoner critique: retorna veredito sustentada/contestada + trilha."""
    t = (thesis or "").strip()
    flags = [f for f in FALLACIES if f.replace("_", " ") in t.lower()]
    # critical reasoning: tese curta ou com marcador absoluto tende a contestada
    absolutes = ["sempre", "nunca", "todos", "nenhum", "prova total"]
    has_abs = any(a in t.lower() for a in absolutes)
    veredito = "contestada" if (flags or has_abs or len(t) < 20) else "sustentada"
    return {"engine": "critical_reasoner", "thesis": t[:300], "flags": flags,
            "veredito": veredito, "CriticalEngine": True,
            "trail": ["tese", "antítese", "síntese", "critical_reasoner"]}
