# -*- coding: utf-8 -*-
"""CalibratedRoutingAdvisor — conselho de roteamento calibrado (SPEC-935-R504).

Consome resultados empíricos (ex.: R503 — mimo 4/9, big-pickle 1/9) e
RECOMENDA scores calibrados para o catálogo. Nunca altera o catálogo
sozinho: `applied=False` e `requires_activation=True` (shadow, não push).
Fórmula conservadora: quanto menor o n de outcomes, menor o deslocamento
em relação ao score original (não confiar em amostra pequena).
"""
from __future__ import annotations

from typing import Any, Dict, List


class CalibratedRoutingAdvisor:
    def __init__(self, min_n_for_full_weight: int = 20):
        self.min_n_for_full_weight = min_n_for_full_weight

    def advise(self, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        advice = []
        for item in catalog:
            model_id = item["model_id"]
            score_orig = float(item.get("score", 0.5))
            if "outcomes_n" in item and item["outcomes_n"] > 0:
                acc = item["outcomes_ok"] / item["outcomes_n"]
                n = item["outcomes_n"]
            else:
                acc = float(item.get("calibrated_accuracy", item.get("accuracy_c2", 0.0)))
                n = int(item.get("outcomes_n", 1))
            # peso da evidência empírica cresce com n (até min_n_for_full_weight)
            w = min(1.0, n / self.min_n_for_full_weight)
            rec = (1 - w) * score_orig + w * acc
            advice.append({
                "model_id": model_id,
                "score_original": round(score_orig, 4),
                "calibrated_accuracy": round(acc, 6),
                "n_outcomes": n,
                "recommended_score": round(rec, 4),
                "applied": False,
                "requires_activation": True,
                "note": "recomendação shadow — ativação explícita requerida",
            })
        return advice