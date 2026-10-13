# -*- coding: utf-8 -*-
"""R828 — diagnostic_explanations: interpretação delimitada do diagnose.

O diagnose é heurística lexical sobre o corpus (autodescoberta), não prova
de qualidade, probabilidade ou cobertura funcional. Este módulo formula a
explicação sem converter escores em qualidade e sem alegar integridade.
"""
from __future__ import annotations
from typing import Any, Dict


def explain_diagnostic_report(report: Dict[str, Any]) -> str:
    """Explica o relatório em linguagem delimitada (português formal)."""
    noo = report.get("noological", {}) if isinstance(report, dict) else {}
    tel = report.get("teleological", {}) if isinstance(report, dict) else {}
    summary = noo.get("summary", {})
    cov = noo.get("coverage", noo.get("coverage_percent", noo.get("overall_coverage_pct", "não registrada")))
    total = noo.get("total_categories", summary.get("total_categories", "não registrado"))
    covered = noo.get("covered_categories", noo.get("categories_covered", summary.get("categories_covered", "não registradas")))
    missing = noo.get("missing_categories", noo.get("categories_absent", summary.get("categories_absent", "não registradas")))
    gaps = tel.get("gaps", [])
    measure = report.get("measurement", {})
    source = "a entrada retida identificada por hash" if measure.get("kind") == "retained_input_lexical" else "o corpus local de autodescoberta"
    lines = [
        f"O diagnose é uma heurística lexical sobre {source},",
        "não uma certificação de qualidade.",
        f"Cobertura noológica de corpus: {cov}% ({covered}/{total}), {missing} categorias ausentes.",
        "Uma lista vazia de lacunas nomeadas não elimina categorias ausentes.",
        "Escores teleológicos, de ruído (SPS) e de compressão (CR) não certificam",
        "qualidade funcional, probabilidade de acerto ou prontidão externa;",
        "são indicadores de sinal do corpus para priorização, e exigem validação",
        "funcional independente (testes, revisão humana) antes de qualquer promoção de confiança.",
    ]
    if gaps:
        lines.append(f"Lacunas teleológicas listadas: {len(gaps)} (ver relatório).")
    return " ".join(lines)
