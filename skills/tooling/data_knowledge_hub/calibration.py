#!/usr/bin/env python3
"""
CalibrationLayer — Calibração de Confiança entre Fontes de Dados
===================================================================
Calcula a confiança combinada de um resultado com base em:

1. **Autoridade da fonte** (0.3-1.0): BCB/IPEA = 1.0, Wikipedia = 0.7, ConceptNet = 0.5
2. **Frescor dos dados**: decay exponencial com TTL por domínio
3. **Consenso entre fontes**: 0.5 (sem pares) a 1.0 (consenso total)

Fórmula: confiança = autoridade × frescor × consenso

Uso:
    from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer
    cal = CalibrationLayer()
    result = cal.calibrate("bcb", "financeiro", 0.95)
"""

from __future__ import annotations

import math
import time
from typing import Any, Dict, Optional

# Scores de autoridade por fonte (0.0 - 1.0)
AUTHORITY_SCORES = {
    # Financeiro
    "bcb": 1.0,
    "banco_central": 1.0,
    "ibge": 1.0,
    "ipea": 0.95,
    "fred": 0.90,
    "world_bank": 0.90,
    "alpha_vantage": 0.75,
    "yfinance": 0.75,
    # Oficial
    "dados_gov": 0.90,
    "datajud": 0.85,
    # Conhecimento
    "wikidata": 0.80,
    "wikipedia": 0.70,
    "google_scholar": 0.75,
    "conceptnet": 0.50,
    # Datasets
    "zenodo": 0.85,
    "datacite": 0.85,
    "figshare": 0.75,
    "uci": 0.80,
    # Fallback
    "offline": 0.50,
    "mock": 0.30,
    "unknown": 0.40,
}

# TTL por domínio (segundos) — usado no decay de frescor
DOMAIN_TTL = {
    "financeiro": 3600,      # 1 hora
    "oficial": 86400,        # 24 horas
    "conhecimento": 86400,   # 24 horas
    "dataset": 604800,       # 7 dias
    "academico": 86400,      # 24 horas
    "generico": 3600,        # 1 hora
}


class CalibrationLayer:
    """
    Camada de calibração: calcula confiança combinada.
    """

    def __init__(self):
        self._stats = {
            "total_calibrations": 0,
            "total_confidence_sum": 0.0,
            "avg_ms": 0.0,
        }

    def calibrate(
        self,
        source: str,
        domain: str,
        consensus_score: float = 0.5,
        freshness: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calcula confiança calibrada para um resultado.

        Args:
            source: nome da fonte (ex: "bcb", "yfinance", "wikipedia")
            domain: domínio (ex: "financeiro", "conhecimento")
            consensus_score: 0.5 (sem pares) a 1.0 (consenso total)
            freshness: timestamp Unix dos dados (None = agora)

        Returns:
            Dict com authority, freshness, consensus, confidence
        """
        start = time.time()

        # 1. Autoridade
        authority = self.get_authority(source)

        # 2. Frescor
        now = time.time()
        freshness_weight = self._freshness_weight(
            freshness or now, domain
        )

        # 3. Consenso
        consensus = max(0.5, min(1.0, consensus_score))

        # 4. Confiança combinada (produto ponderado)
        confidence = round(authority * freshness_weight * consensus, 4)

        elapsed_ms = (time.time() - start) * 1000
        self._stats["total_calibrations"] += 1
        self._stats["total_confidence_sum"] += confidence
        total = self._stats["total_calibrations"]
        self._stats["avg_ms"] = (
            (self._stats["avg_ms"] * (total - 1) + elapsed_ms) / total
        )

        return {
            "authority": authority,
            "freshness": round(freshness_weight, 4),
            "consensus": consensus,
            "confidence": confidence,
            "source": source,
            "domain": domain,
            "elapsed_ms": round(elapsed_ms, 2),
        }

    def get_authority(self, source: str) -> float:
        """Retorna score de autoridade de uma fonte."""
        source_lower = source.lower().replace(" ", "_")
        return AUTHORITY_SCORES.get(source_lower, AUTHORITY_SCORES["unknown"])

    def _freshness_weight(self, data_timestamp: float, domain: str) -> float:
        """
        Calcula peso de frescor com decay exponencial.

        Fórmula: e^(-λ × Δt), onde λ = 1 / TTL_do_domínio
        """
        ttl = DOMAIN_TTL.get(domain, 3600)
        age = time.time() - data_timestamp

        if age <= 0:
            return 1.0  # dados futuros ou agora = frescor máximo

        lambda_decay = 1.0 / ttl
        weight = math.exp(-lambda_decay * age)
        return max(0.1, min(1.0, weight))  # mínimo 0.1

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de calibração."""
        total = self._stats["total_calibrations"]
        return {
            **self._stats,
            "avg_confidence": round(
                self._stats["total_confidence_sum"] / total, 4
            ) if total > 0 else 0.0,
            "sources_mapped": len(AUTHORITY_SCORES),
        }
