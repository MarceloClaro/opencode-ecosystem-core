#!/usr/bin/env python3
"""
DataKnowledgeHub — Descoberta Unificada de Dados e Conhecimento (SPEC-965)
=============================================================================
Hub central que integra todas as fontes de dados e conhecimento em uma
única interface. Roteia consultas automaticamente para a fonte ideal.

Componentes:
    - FinancialDataSource: yfinance, BCB/SGS, FRED, World Bank
    - OfficialDataSource: IBGE/SIDRA, IPEA, dados.gov.br
    - KnowledgeDataSource: Wikipedia, Wikidata, ConceptNet, Google Scholar
    - DatasetDataSource: Zenodo, DataCite, UCI, Figshare
    - DomainRouter: classifica domínio da consulta

Uso:
    from skills.tooling.data_knowledge_hub import DataKnowledgeHub
    hub = DataKnowledgeHub()

    # Busca automaticamente roteada
    result = hub.search("cotação PETR4 hoje")
    result = hub.search("o que é machine learning")
    result = hub.search("dataset climate change")
    result = hub.search("IPCA acumulado 2024")

    # Ou especifica a fonte
    result = hub.search("GDP", domain="financeiro", source="fred")
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .base import DataSource
from .financial import FinancialDataSource
from .official import OfficialDataSource
from .knowledge import KnowledgeDataSource
from .datasets import DatasetDataSource
from .router import DomainRouter
from .validation import CrossValidator
from .calibration import CalibrationLayer
from .audit import AuditTrail


class DataKnowledgeHub:
    """
    Hub unificado de dados e conhecimento com validação cruzada,
    calibração de confiança e audit trail.

    Roteia consultas automaticamente para a fonte adequada com
    base na classificação de domínio do DomainRouter.

    Atributos:
        financial: FinancialDataSource
        official: OfficialDataSource
        knowledge: KnowledgeDataSource
        datasets: DatasetDataSource
        router: DomainRouter
        cross_validator: CrossValidator (validação entre fontes)
        calibration: CalibrationLayer (confiança combinada)
        audit: AuditTrail (log imutável de decisões)
    """

    def __init__(self):
        self.financial = FinancialDataSource()
        self.official = OfficialDataSource()
        self.knowledge = KnowledgeDataSource()
        self.datasets = DatasetDataSource()
        self.router = DomainRouter()
        self.cross_validator = CrossValidator()
        self.calibration = CalibrationLayer()
        self.audit = AuditTrail()

        # Cache com TTL por domínio
        self._cache: Dict[str, Tuple[float, Dict]] = {}
        self._cache_ttl = {
            "financeiro": 3600,      # 1h (dados mudam rápido)
            "oficial": 86400,        # 24h (indicadores mudam devagar)
            "conhecimento": 86400,   # 24h (conhecimento estável)
            "dataset": 604800,       # 7d (datasets raramente mudam)
            "academico": 86400,      # 24h
            "generico": 3600,        # 1h
        }

        self._stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "online": 0,
            "offline": 0,
            "domains": {},
            "sources": {},
        }

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        source: Optional[str] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Busca dados em qualquer domínio.

        Args:
            query: termo de busca
            domain: domínio específico (opcional — auto-detectar se None)
            source: fonte específica dentro do domínio (opcional)
            use_cache: se True, usa cache

        Returns:
            Dict com resultados padronizados
        """
        start = time.time()

        # 1. Classificar domínio
        if domain is None:
            domain = self.router.classify(query)

        # 2. Verificar cache
        cache_key = f"{domain}:{source or 'auto'}:{query.lower().strip()}"
        if use_cache and cache_key in self._cache:
            timestamp, result = self._cache[cache_key]
            ttl = self._cache_ttl.get(domain, 3600)
            if time.time() - timestamp < ttl:
                self._stats["cache_hits"] += 1
                self._stats["total_queries"] += 1
                result["cached"] = True
                return result

        self._stats["cache_misses"] += 1

        # 3. Rotear para a fonte adequada
        source_map = {
            "financeiro": (self.financial, source),
            "oficial": (self.official, source),
            "conhecimento": (self.knowledge, source),
            "dataset": (self.datasets, source),
            "academico": (self.knowledge, "google_scholar"),
            # "generico" tenta conhecimento primeiro
        }

        data_source, specific_source = source_map.get(domain, (self.knowledge, None))
        result = data_source.search(query, source=specific_source)

        # 4. Atualizar estatísticas
        self._stats["total_queries"] += 1
        self._stats["domains"][domain] = self._stats["domains"].get(domain, 0) + 1
        src = result.get("source", "unknown")
        self._stats["sources"][src] = self._stats["sources"].get(src, 0) + 1
        if result.get("status") == "online":
            self._stats["online"] += 1
        else:
            self._stats["offline"] += 1

        # 5. Validação cruzada (se houver dados para validar)
        cross_validated = False
        validation_details = {}
        consensus_score = 0.5
        metric_name = query.strip().upper()

        if result.get("results") and len(result["results"]) > 0:
            # Extrair observações para validação
            primary_results = result["results"]
            obs_primary = _extract_observations(primary_results, src)

            if obs_primary:
                # Tenta buscar da fonte alternativa para cross-validation
                alt_sources = _get_alternative_sources(domain, src)
                all_obs = [{"source": src, "value": obs_primary["value"],
                            "unit": obs_primary.get("unit", "")}]

                for alt_src in alt_sources:
                    try:
                        alt_result = data_source.search(query, source=alt_src)
                        if alt_result.get("results"):
                            obs_alt = _extract_observations(
                                alt_result["results"], alt_src
                            )
                            if obs_alt:
                                all_obs.append({
                                    "source": alt_src,
                                    "value": obs_alt["value"],
                                    "unit": obs_alt.get("unit", ""),
                                })
                    except Exception:
                        continue

                if len(all_obs) >= 2:
                    validation = self.cross_validator.validate(metric_name, all_obs)
                    validation_details = validation
                    cross_validated = True
                    consensus_score = validation.get("confidence", 0.5)

        # 6. Calibração de confiança
        calibration = self.calibration.calibrate(
            source=src,
            domain=domain,
            consensus_score=consensus_score,
        )
        confidence = calibration["confidence"]

        # 7. Audit trail
        audit_id = self.audit.record(
            query=query,
            domain=domain,
            source=src,
            confidence=confidence,
            decision_context="data_knowledge_hub:search",
            raw_result=result.get("results", []),
            cross_validated=cross_validated,
            calibration_details=calibration,
        )

        # 8. Adicionar metadados do hub
        result["domain"] = domain
        result["cached"] = False
        result["hub_elapsed_ms"] = round((time.time() - start) * 1000, 2)
        result["confidence"] = confidence
        result["audit_id"] = audit_id
        result["cross_validated"] = cross_validated
        result["validation_details"] = validation_details
        result["calibration"] = calibration

        # 9. Armazenar em cache
        if use_cache:
            self._cache[cache_key] = (time.time(), result)

        return result

    # ─── Atalhos por domínio ─────────────────────────────────

    def search_finance(
        self, query: str, source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atalho para busca financeira."""
        return self.search(query, domain="financeiro", source=source)

    def search_official(
        self, query: str, source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atalho para busca de dados oficiais."""
        return self.search(query, domain="oficial", source=source)

    def search_knowledge(
        self, query: str, source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atalho para busca de conhecimento."""
        return self.search(query, domain="conhecimento", source=source)

    def search_dataset(
        self, query: str, source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atalho para busca de datasets."""
        return self.search(query, domain="dataset", source=source)

    def search_academic(
        self, query: str, source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atalho para busca acadêmica."""
        return self.search(query, domain="academico", source=source)

    # ─── Utilitários ─────────────────────────────────────────

    def clear_cache(self):
        """Limpa todo o cache."""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """Retorna número de entradas no cache."""
        return len(self._cache)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do hub."""
        total = self._stats["total_queries"]
        return {
            **self._stats,
            "cache_size": len(self._cache),
            "cache_hit_rate": round(
                self._stats["cache_hits"] / total * 100, 1
            ) if total > 0 else 0,
            "online_rate": round(
                self._stats["online"] / total * 100, 1
            ) if total > 0 else 0,
            "validation_stats": self.cross_validator.get_stats(),
            "calibration_stats": self.calibration.get_stats(),
            "audit_stats": self.audit.get_stats(),
        }

    def get_report(self) -> str:
        """Relatório legível do hub."""
        s = self.get_stats()
        lines = [
            "DataKnowledgeHub",
            "=" * 55,
            f"Total de consultas: {s['total_queries']}",
            f"  - Cache hit rate: {s['cache_hit_rate']}%",
            f"  - Online rate: {s['online_rate']}%",
            f"  - Domínios consultados: {len(s['domains'])}",
            f"  - Fontes usadas: {len(s['sources'])}",
            "",
            "Domínios:",
        ]
        for dom, count in sorted(s["domains"].items(), key=lambda x: -x[1]):
            lines.append(f"  - {dom}: {count} consultas")
        lines.extend(["", "Fontes:"])
        for src, count in sorted(s["sources"].items(), key=lambda x: -x[1]):
            lines.append(f"  - {src}: {count} consultas")
        return "\n".join(lines)


# ─── Helpers ──────────────────────────────────────────────────

# Fontes alternativas para cross-validation por domínio
ALTERNATIVE_SOURCES = {
    "financeiro": ["yfinance", "bcb", "fred", "world_bank", "alpha_vantage"],
    "oficial": ["ibge", "ipea", "dados_gov"],
    "conhecimento": ["wikipedia", "wikidata", "conceptnet", "google_scholar"],
    "dataset": ["zenodo", "datacite", "uci", "figshare"],
    "academico": ["google_scholar", "wikipedia"],
    "generico": ["wikipedia", "wikidata"],
}


def _extract_observations(
    results: List[Dict[str, Any]], source: str
) -> Optional[Dict[str, Any]]:
    """Extrai valor numérico e unidade de resultados para validação."""
    if not results:
        return None

    first = results[0]
    value = None
    unit = ""

    # Tentar campos comuns de valor numérico
    for key in ("valor", "value", "price", "valor_float", "regularMarketPrice"):
        v = first.get(key)
        if v is not None:
            try:
                value = float(v)
                break
            except (ValueError, TypeError):
                continue

    # Tentar campos de unidade
    for key in ("unidade", "unit", "currency"):
        u = first.get(key)
        if u:
            unit = u
            break
    # Unidades default por fonte
    if not unit:
        unit = {"bcb": "%", "ibge": "%", "yfinance": "BRL",
                "fred": "USD", "world_bank": "USD"}.get(source, "")

    if value is not None:
        return {"value": value, "unit": unit}
    return None


def _get_alternative_sources(domain: str, current_source: str) -> List[str]:
    """Retorna fontes alternativas para validação cruzada."""
    sources = ALTERNATIVE_SOURCES.get(domain, [])
    return [s for s in sources if s != current_source]


# Singleton
_default_hub: Optional[DataKnowledgeHub] = None


def get_hub() -> DataKnowledgeHub:
    global _default_hub
    if _default_hub is None:
        _default_hub = DataKnowledgeHub()
    return _default_hub


# ─── Teste Rápido ───────────────────────────────────────────

if __name__ == "__main__":
    hub = get_hub()

    print("=== DataKnowledgeHub - Teste Rápido ===")
    print()

    # Teste de classificação
    test_queries = [
        "cotação PETR4 hoje",
        "IPCA acumulado 2024",
        "o que é machine learning",
        "dataset climate change",
        "artigo transformers NLP",
    ]

    print("Classificação de Domínio:")
    for q in test_queries:
        domain = hub.router.classify(q)
        print(f"  [{domain:15s}] {q}")

    print()

    # Teste de busca (modo offline/mock)
    print("Busca Financeira (modo offline):")
    r = hub.search_finance("PETR4")
    print(f"  Fonte: {r['source']}, Status: {r['status']}, "
          f"Resultados: {r['count']}")

    print("\nBusca Conhecimento (modo offline):")
    r = hub.search_knowledge("machine learning")
    print(f"  Fonte: {r['source']}, Status: {r['status']}, "
          f"Resultados: {r['count']}")

    print("\nBusca Datasets (modo offline):")
    r = hub.search_dataset("climate")
    print(f"  Fonte: {r['source']}, Status: {r['status']}, "
          f"Resultados: {r['count']}")

    print(f"\n{hub.get_report()}")
