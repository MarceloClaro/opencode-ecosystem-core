#!/usr/bin/env python3
"""
DomainRouter — Roteamento de Consultas por Domínio de Conhecimento
=====================================================================
Classifica a consulta do usuário em um domínio e roteia para a
fonte de dados mais adequada.

Domínios:
    - financeiro: yfinance, BCB, FRED, World Bank
    - oficial: IBGE, IPEA, dados.gov.br
    - conhecimento: Wikipedia, Wikidata, ConceptNet
    - dataset: Zenodo, DataCite, UCI, Figshare
    - academico: delega ao MultiSearcher existente (research/searchers.py)

Uso:
    from skills.tooling.data_knowledge_hub.router import DomainRouter
    router = DomainRouter()
    dominio = router.classify("cotação PETR4 hoje")  # "financeiro"
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple


class DomainRouter:
    """
    Classifica consultas em domínios de conhecimento para roteamento
    à fonte de dados adequada.
    """

    def __init__(self):
        self._stats = {
            "total_classifications": 0,
            "domains": {},
            "avg_ms": 0.0,
        }

        # Regras de classificação por domínio
        self._rules = {
            "financeiro": [
                # Ações e ativos
                r"\b(petr|vale|itub|bbas|b3sa|weg|ambev|magalu|mglu|bova|ibov)\b",
                r"\b(cotação|cotacao|ação|acao|stock|share|ticker)\b",
                r"\b(dólar|dolar|euro|libra|iene|usd|brl|eur|gbp)\b",
                # Índices macro
                r"\b(ipca|selic|inflação|juros|pib|cambio|câmbio)\b",
                r"\b(fred|bcb|banco central|fed|federal reserve)\b",
                # Mercado
                r"\b(bolsa|mercado financeiro|renda fixa|renda variavel)\b",
                r"\b(world bank|banco mundial|fmi|imf)\b",
            ],
            "oficial": [
                r"\b(ibge|sidra|pnad|pintec|censo|população)\b",
                r"\b(ipea|ipeadata)\b",
                r"\b(dados\.gov|dados abertos|ckan|governo)\b",
                r"\b(datajud|cnj|processo judicial|tribunal)\b",
            ],
            "conhecimento": [
                r"\b(o que é|o que e|definição|definir|significa|conceito)\b",
                r"\b(wikipedia|wikidata|conceptnet|enciclopédia)\b",
                r"\b(conceito de|história do|origem do|como funciona)\b",
            ],
            "dataset": [
                r"\b(dataset|base de dados|base de dados|conjunto de dados)\b",
                r"\b(zenodo|datacite|figshare|uci|kaggle)\b",
                r"\b(repositório de dados|data repository|open data)\b",
            ],
            "academico": [
                r"\b(artigo|paper|publicação|publicacao|periódico|periodico)\b",
                r"\b(arxiv|semantic scholar|crossref|openalex|pubmed|scielo)\b",
                r"\b(pesquisa|tese|dissertação|monografia)\b",
                r"\b(doi|issn|isbn|citação|citation|referência|referencia)\b",
                r"\b(machine learning|deep learning|ia|inteligência artificial)\b",
                r"\b(método|metodologia|resultados|experimento)\b",
            ],
        }

    def classify(self, query: str) -> str:
        """
        Classifica uma consulta em um domínio.

        Args:
            query: texto da consulta

        Returns:
            Nome do domínio: "financeiro", "oficial", "conhecimento",
            "dataset", "academico", ou "generico" se não classificar
        """
        start = time.time()
        ql = query.lower().strip()

        scores = {}
        for domain, patterns in self._rules.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, ql)
                score += len(matches)
            if score > 0:
                scores[domain] = score

        # Escolher domínio com maior score
        if scores:
            result = max(scores, key=scores.get)
        else:
            result = "generico"

        # Atualizar stats
        elapsed_ms = (time.time() - start) * 1000
        self._stats["total_classifications"] += 1
        self._stats["domains"][result] = self._stats["domains"].get(result, 0) + 1
        total = self._stats["total_classifications"]
        self._stats["avg_ms"] = (
            (self._stats["avg_ms"] * (total - 1) + elapsed_ms) / total
        )

        return result

    def get_supported_domains(self) -> List[str]:
        """Retorna lista de domínios suportados."""
        return list(self._rules.keys())

    def get_rules_for_domain(self, domain: str) -> List[str]:
        """Retorna regras para um domínio específico."""
        return self._rules.get(domain, [])

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de classificação."""
        return {
            **self._stats,
            "domains_supported": len(self._rules),
        }

    def explain(self, query: str) -> Dict[str, Any]:
        """
        Explica a classificação de uma consulta.

        Returns:
            Dict com domínio, score, regras匹配
        """
        ql = query.lower().strip()
        details = {}
        for domain, patterns in self._rules.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, ql)
                if found:
                    matches.append({"pattern": pattern, "matches": found})
            if matches:
                details[domain] = matches

        result = self.classify(query)
        return {
            "query": query,
            "classified_as": result,
            "match_details": details,
            "total_rules_matched": sum(
                len(m) for m in details.values()
            ),
        }
