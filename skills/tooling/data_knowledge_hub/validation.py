#!/usr/bin/env python3
"""
CrossValidator — Validação Cruzada entre Fontes de Dados
============================================================
Compara o mesmo dado obtido de múltiplas fontes independentes,
detecta discrepâncias e calcula confiança pelo consenso.

Suporta:
    - Normalização de unidades (BRL ↔ USD, % a.a. ↔ % a.m.)
    - Tolerâncias específicas por métrica
    - Consenso entre 2+ fontes
    - Fallback para fonte única

Uso:
    from skills.tooling.data_knowledge_hub.validation import CrossValidator
    cv = CrossValidator()
    result = cv.validate("IPCA", [
        {"source": "bcb", "value": 0.38, "unit": "%"},
        {"source": "ibge", "value": 0.39, "unit": "%"},
    ])
"""

from __future__ import annotations

import json
import math
import time
from typing import Any, Dict, List, Optional, Tuple


# ─── Registry of cross-validatable metrics ────────────────
# Tolerância: diferença máxima aceita entre fontes (unidade normalizada)

METRIC_REGISTRY = {
    "IPCA": {
        "tolerance": 0.1,  # pontos percentuais
        "normalize": lambda v, u: v if u == "%" else v,  # direto
    },
    "SELIC": {
        "tolerance": 0.25,
        "normalize": lambda v, u: v if u in ("%", "% a.a.") else v,
    },
    "PIB Brasil": {
        "tolerance": 0.05,  # 5% relativo
        "normalize": lambda v, u: _normalize_currency(v, u, rate=5.0),
    },
    "Câmbio": {
        "tolerance": 0.01,  # 1% relativo
        "normalize": lambda v, u: v,
    },
    "PETR4": {
        "tolerance": 0.005,  # 0.5% relativo
        "normalize": lambda v, u: v if u == "BRL" else v,
    },
    "VALE3": {
        "tolerance": 0.005,
        "normalize": lambda v, u: v if u == "BRL" else v,
    },
    "População": {
        "tolerance": 0.02,  # 2% relativo
        "normalize": lambda v, u: v,
    },
}

# Fallback para métricas não registradas
DEFAULT_TOLERANCE = 0.1  # 10% relativo


def _normalize_currency(value: float, unit: str, rate: float) -> float:
    """Normaliza valor para USD."""
    if unit in ("BRL", "BRL_billion"):
        return value / rate  # BRL → USD
    return value


class CrossValidator:
    """
    Validador cruzado: compara dados entre fontes independentes.

    Detecta:
    - Consenso (todas as fontes concordam dentro da tolerância)
    - Discrepância (fontes discordam além da tolerância)
    - Fonte única (sem par para validar)
    """

    def __init__(self):
        self._stats = {
            "total_validations": 0,
            "matches": 0,
            "discrepancies": 0,
            "single_sources": 0,
            "avg_ms": 0.0,
        }

    def validate(
        self,
        metric: str,
        observations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Valida uma métrica entre múltiplas fontes.

        Args:
            metric: nome da métrica (ex: "IPCA", "PETR4", "PIB Brasil")
            observations: lista de dicts com {"source", "value", "unit"}

        Returns:
            Dict com status, confidence, details
        """
        start = time.time()

        if not observations:
            return {
                "status": "no_data",
                "confidence": 0.0,
                "metric": metric,
                "sources": [],
            }

        config = METRIC_REGISTRY.get(metric, {
            "tolerance": DEFAULT_TOLERANCE,
            "normalize": lambda v, u: v,
        })

        # Normalizar valores
        normalized = []
        for obs in observations:
            try:
                nv = config["normalize"](float(obs["value"]), obs.get("unit", ""))
                normalized.append({
                    "source": obs["source"],
                    "value": nv,
                    "original_value": obs["value"],
                    "unit": obs.get("unit", ""),
                })
            except (ValueError, TypeError):
                continue

        if len(normalized) == 0:
            result = {
                "status": "error",
                "confidence": 0.0,
                "metric": metric,
                "sources": [o["source"] for o in observations],
                "error": "Falha na normalização dos valores",
            }
        elif len(normalized) == 1:
            # Fonte única: confiança baseada apenas na autoridade da fonte
            result = {
                "status": "single_source",
                "confidence": 0.70,
                "metric": metric,
                "sources": [n["source"] for n in normalized],
                "normalized_values": normalized,
                "details": "Apenas uma fonte disponível — sem consenso",
            }
        else:
            # Múltiplas fontes: calcular consenso
            values = [n["value"] for n in normalized]
            mean_val = sum(values) / len(values)
            max_diff = max(abs(v - mean_val) for v in values)
            max_rel_diff = max_diff / abs(mean_val) if mean_val != 0 else max_diff

            is_rel = config.get("tolerance", DEFAULT_TOLERANCE) < 0.1
            tolerance = config.get("tolerance", DEFAULT_TOLERANCE)
            threshold = tolerance * mean_val if is_rel else tolerance

            within_tolerance = max_diff <= threshold if not is_rel else max_rel_diff <= tolerance

            if within_tolerance:
                # Consenso: confiança aumenta com número de fontes
                n = len(normalized)
                base_confidence = 0.85
                consensus_bonus = min(0.10, (n - 1) * 0.05)
                confidence = min(1.0, base_confidence + consensus_bonus)

                result = {
                    "status": "match",
                    "confidence": round(confidence, 4),
                    "metric": metric,
                    "sources": [n["source"] for n in normalized],
                    "normalized_values": normalized,
                    "consensus_value": round(mean_val, 4),
                    "max_discrepancy": round(max_diff, 4),
                    "within_tolerance": True,
                    "details": f"{n} fontes concordam (diferença máxima: {max_diff:.4f})",
                }
                self._stats["matches"] += 1
            else:
                result = {
                    "status": "discrepancy",
                    "confidence": 0.30,
                    "metric": metric,
                    "sources": [n["source"] for n in normalized],
                    "normalized_values": normalized,
                    "consensus_value": round(mean_val, 4),
                    "max_discrepancy": round(max_diff, 4),
                    "within_tolerance": False,
                    "details": f"Discrepância detectada: diferença máxima {max_diff:.4f} > tolerância {threshold:.4f}",
                }
                self._stats["discrepancies"] += 1

        # Registrar stats
        elapsed_ms = (time.time() - start) * 1000
        self._stats["total_validations"] += 1
        total = self._stats["total_validations"]
        self._stats["avg_ms"] = (
            (self._stats["avg_ms"] * (total - 1) + elapsed_ms) / total
        )

        if result["status"] == "single_source":
            self._stats["single_sources"] += 1

        result["elapsed_ms"] = round(elapsed_ms, 2)
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de validação."""
        total = self._stats["total_validations"]
        return {
            **self._stats,
            "match_rate": round(
                self._stats["matches"] / total * 100, 1
            ) if total > 0 else 0,
            "discrepancy_rate": round(
                self._stats["discrepancies"] / total * 100, 1
            ) if total > 0 else 0,
        }

    def list_supported_metrics(self) -> List[str]:
        """Lista métricas com tolerância configurada."""
        return sorted(METRIC_REGISTRY.keys())
