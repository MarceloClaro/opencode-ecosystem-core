# -*- coding: utf-8 -*-
"""
Free Model Catalog — SPEC-935-R500
==================================
Catálogo curado de modelos free reais do OpenCode Ecosystem, com base no
benchmark empírico R499 (mesma tarefa IMO, condição scaffold MASWOS):

  - mimo-v2.5-free            score 0.987 (23.8 s, acurácia 1.0)
  - big-pickle                score 0.923 (43.0 s, acurácia 1.0)
  - nemotron-3-ultra-free     score 0.709 (107.4 s, acurácia 1.0)
  - muse-spark-1.3-free       score 0.324 (18.1 s, acurácia 0.0 — rápido mas
                              não resolveu: "fake reasoning")
  - muse-spark-1.2-free       score 0.312 (24.4 s, acurácia 0.0)

Acessibilidade real (R499): deepseek-v4-flash (saldo), gemini-2.5-flash
(erro servidor), gpt-4o-mini/claude-haiku-4 (sem resposta) — NÃO incluídos
como disponíveis.

Hermético, anti-overclaim: scores medidos na mesma tarefa/condição; nenhuma
alegação de superioridade genérica; muse spark rebaixado por acurácia zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

# ── Curadoria R499 ────────────────────────────────────────────────────────────

FREE_BENCHMARK: List[Dict[str, Any]] = [
    {
        "model_id": "opencode/mimo-v2.5-free",
        "name": "Mimo V2.5 Free",
        "provider": "opencode-go",
        "tier": "free",
        "score": 0.987,
        "latency_c2_s": 23.8,
        "accuracy_c2": 1.0,
        "conformity_c2": 1.0,
        "accessible": True,
        "note": "Melhor custo-benefício free (R499); typo Unicode cosmético de sobrescrito",
    },
    {
        "model_id": "opencode/big-pickle",
        "name": "Big Pickle",
        "provider": "opencode",
        "tier": "free",
        "score": 0.923,
        "latency_c2_s": 43.0,
        "accuracy_c2": 1.0,
        "conformity_c2": 1.0,
        "accessible": True,
        "note": "Modelo do orquestrador; correta e conforme no C2, sem typo (R499)",
    },
    {
        "model_id": "opencode/nemotron-3-ultra-free",
        "name": "Nemotron 3 Ultra Free",
        "provider": "opencode-zen",
        "tier": "free",
        "score": 0.709,
        "latency_c2_s": 107.4,
        "accuracy_c2": 1.0,
        "conformity_c2": 1.0,
        "accessible": True,
        "note": "Correto sob scaffold MASWOS, porém 4–5× mais lento (R499)",
    },
    {
        "model_id": "opencode/muse-spark-1.3-contributor-free",
        "name": "Muse Spark 1.3 Contributor Free",
        "provider": "opencode",
        "tier": "free",
        "score": 0.324,
        "latency_c2_s": 18.1,
        "accuracy_c2": 0.0,
        "conformity_c2": 0.0,
        "accessible": True,
        "note": "Rápido mas acurácia 0: anuncia verificação sem entregar resposta (fake reasoning, R499)",
    },
    {
        "model_id": "opencode/muse-spark-1.2-contributor-free",
        "name": "Muse Spark 1.2 Contributor Free",
        "provider": "opencode",
        "tier": "free",
        "score": 0.312,
        "latency_c2_s": 24.4,
        "accuracy_c2": 0.0,
        "conformity_c2": 0.0,
        "accessible": True,
        "note": "Idem 1.3 (R499)",
    },
]

# Ordem de preferência por tipo de tarefa (score do R499 decide).
BEST_FREE_BY_TASK: Dict[str, List[str]] = {
    "academic": ["opencode/mimo-v2.5-free", "opencode/big-pickle",
                 "opencode/nemotron-3-ultra-free",
                 "opencode/muse-spark-1.3-contributor-free",
                 "opencode/muse-spark-1.2-contributor-free"],
    "math": ["opencode/mimo-v2.5-free", "opencode/big-pickle",
             "opencode/nemotron-3-ultra-free",
             "opencode/muse-spark-1.3-contributor-free",
             "opencode/muse-spark-1.2-contributor-free"],
    "reasoning": ["opencode/mimo-v2.5-free", "opencode/big-pickle",
                  "opencode/nemotron-3-ultra-free",
                  "opencode/muse-spark-1.3-contributor-free",
                  "opencode/muse-spark-1.2-contributor-free"],
    "writing": ["opencode/big-pickle", "opencode/mimo-v2.5-free",
                "opencode/nemotron-3-ultra-free"],
}

DEFAULT_FREE_ORDER: List[str] = [m["model_id"] for m in
                                 sorted(FREE_BENCHMARK, key=lambda m: -m["score"])]


def best_free_model(task_type: str, available: List[str] | None = None) -> str:
    """Retorna o melhor modelo free para o task_type (curadoria R499)."""
    order = BEST_FREE_BY_TASK.get(task_type, DEFAULT_FREE_ORDER)
    if available is None:
        return order[0]
    for model_id in order:
        if model_id in available:
            return model_id
    return order[0]


def list_free_models() -> List[Dict[str, Any]]:
    """Modelos do catálogo free para o ModelRouter (list_all_models)."""
    return [
        {
            "model_id": m["model_id"],
            "name": m["name"],
            "provider": m["provider"],
            "strengths": ["academic", "math", "reasoning"],
            "context_window": 128000,
            "thinking": False,
            "tier": "free",
            "source": "curadoria R499",
            "score": m["score"],
            "accessible": m["accessible"],
        }
        for m in FREE_BENCHMARK
    ]