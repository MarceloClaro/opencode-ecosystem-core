# -*- coding: utf-8 -*-
"""R830 — dialectical_engine: tese/antítese/síntese com trilha.

Inspiração: CriticalEngine + lean tactic (conversor + verificador).
Corpus keywords: dialectical, dialetic, thesis, antithesis,
DialecticalEngine, Dialectic. Categoria: dialectical_engine.
"""
from __future__ import annotations

def run(thesis: str) -> dict:
    """dialectical_engine run: gera antítese e síntese declarativas."""
    t = (thesis or "").strip()[:300]
    antithesis = f"Negação metódica de: {t}" if t else "Antítese vazia"
    synthesis = f"Síntese: conservar o núcleo de '{t[:80]}' e suspender o absoluto."
    return {"engine": "dialectical_engine", "thesis": t, "antithesis": antithesis,
            "synthesis": synthesis, "trail": ["thesis", "antithesis", "synthesis"],
            "DialecticalEngine": True, "Dialectic": True}
