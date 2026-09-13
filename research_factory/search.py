# -*- coding: utf-8 -*-
"""Pesquisa Open Science com failover multi-provedor (SPEC-935-R476, M1/R471).

Orquestra buscas apenas sobre fontes de ciência aberta, na ordem canônica
OpenAlex -> Crossref -> EuropePMC -> arXiv, com failover: se uma fonte falha,
a próxima é tentada e o recibo registra todas as tentativas. Fontes fora da
política (ex.: resolvedores restritos) são bloqueadas com recibo, sem execução.

Política: `open_science_only`; nenhuma fonte restrita em DEFAULT_SOURCES.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set

# Ordem canônica de tentativa (lista!) e conjunto de política (frozenset).
OPEN_SCIENCE_ORDER: List[str] = ["openalex", "crossref", "europepmc", "arxiv"]
OPEN_SCIENCE_SOURCES = frozenset(OPEN_SCIENCE_ORDER)


@dataclass
class SearchReceipt:
    """Recibo auditável de uma busca open science com failover."""

    query: str
    policy: str = "open_science_only"
    permitted_sources: Set[str] = field(default_factory=set)
    attempted: List[str] = field(default_factory=list)
    succeeded: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    blocked: List[str] = field(default_factory=list)
    succeeded_source: Optional[str] = None
    records_count: int = 0
    orchestrator: str = "marceloclaro"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["permitted_sources"] = sorted(self.permitted_sources)
        return data


class OpenScienceSearchOrchestrator:
    """Failover multi-provedor restrito à política open science."""

    def __init__(
        self,
        searcher_factory: Optional[Callable[[str], Any]] = None,
        allowlist: Optional[Set[str]] = None,
    ) -> None:
        # searcher_factory: callable(source) -> objeto com .search(query, limit_per_platform)
        self.searcher_factory = searcher_factory
        self.allowlist = set(allowlist) if allowlist else set(OPEN_SCIENCE_SOURCES)

    def search(
        self,
        query: str,
        limit_per_platform: int = 5,
    ) -> tuple[SearchReceipt, List[Dict[str, Any]]]:
        return self.search_with_sources(
            query=query,
            sources=None,
            limit_per_platform=limit_per_platform,
        )

    def search_with_sources(
        self,
        query: str,
        sources: Optional[Sequence[str]] = None,
        limit_per_platform: int = 5,
    ) -> tuple[SearchReceipt, List[Dict[str, Any]]]:
        """Busca nas fontes pedidas observando a allowlist da política.

        Fontes fora da allowlist entram em `blocked` e nunca são executadas.
        """
        requested = list(sources) if sources is not None else list(OPEN_SCIENCE_ORDER)
        permitted = [s for s in requested if s in self.allowlist]
        blocked = [s for s in requested if s not in self.allowlist]

        attempted: List[str] = []
        succeeded: List[str] = []
        failed: List[str] = []
        records: List[Dict[str, Any]] = []

        if self.searcher_factory is not None:
            for source in permitted:
                attempted.append(source)
                try:
                    searcher = self.searcher_factory(source)
                    rows = searcher.search(
                        query, limit_per_platform=limit_per_platform
                    )
                    succeeded.append(source)
                    records.extend(rows or [])
                except Exception:
                    failed.append(source)

        receipt = SearchReceipt(
            query=query,
            permitted_sources=set(self.allowlist),
            attempted=attempted,
            succeeded=succeeded,
            failed=failed,
            blocked=blocked,
            succeeded_source=succeeded[0] if succeeded else None,
            records_count=len(records),
        )
        return receipt, records