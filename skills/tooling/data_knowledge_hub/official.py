#!/usr/bin/env python3
"""
OfficialDataSource — Dados Oficiais Brasileiros (IBGE, IPEA, dados.gov.br)
============================================================================
Busca dados governamentais, censitários e de indicadores públicos.

Fontes:
    - IBGE/SIDRA: API pública — PNAD, PINTEC, censo, IPCA, séries
    - IPEA/Ipeadata: séries macroeconômicas, sociais, regionais
    - dados.gov.br: CKAN — catálogo de dados abertos do governo federal
    - Datajud CNJ (já existente): dados processuais

Uso:
    from skills.tooling.data_knowledge_hub.official import OfficialDataSource
    ods = OfficialDataSource()
    result = ods.search("IPCA", source="ibge")
    result = ods.search("PIB", source="ipea")
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from .base import DataSource


# ─── Dados Mockados (modo offline) ─────────────────────────

MOCK_DATA = {
    "ibge": [
        {"indicador": "IPCA", "valor": 0.38, "unidade": "%",
         "periodo": "Jun/2024", "fonte": "IBGE/SIDRA"},
        {"indicador": "PNAD Contínua - Taxa de Desocupação",
         "valor": 7.1, "unidade": "%", "periodo": "Mai/2024",
         "fonte": "IBGE/PNAD"},
        {"indicador": "População Estimada", "valor": 203080756,
         "unidade": "pessoas", "periodo": "2024",
         "fonte": "IBGE"},
    ],
    "ipea": [
        {"serie": "PIB - Variação real anual", "valor": 2.9,
         "unidade": "% a.a.", "periodo": "2023", "fonte": "IPEA"},
        {"serie": "Taxa de investimento (FBCF/PIB)", "valor": 18.1,
         "unidade": "%", "periodo": "2023", "fonte": "IPEA"},
        {"serie": "Índice de Gini", "valor": 0.518,
         "unidade": "0-1", "periodo": "2022", "fonte": "IPEA"},
    ],
    "dados_gov": [
        {"titulo": "Dados Abertos da Educação Superior",
         "orgao": "MEC/INEP", "formato": "CSV",
         "url": "https://dados.gov.br/dados/conjuntos-dados/educacao-superior"},
        {"titulo": "Séries Históricas do IPCA",
         "orgao": "IBGE", "formato": "CSV",
         "url": "https://dados.gov.br/dados/conjuntos-dados/ipca"},
    ],
}


class OfficialDataSource(DataSource):
    """
    Fonte de dados oficiais brasileiros: IBGE, IPEA, dados.gov.br.
    """

    name = "official"

    def __init__(self):
        super().__init__()
        self._sources = {
            "ibge": self._search_ibge,
            "ipea": self._search_ipea,
            "dados_gov": self._search_dados_gov,
        }

    def search(
        self, query: str, source: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        start = time.time()

        if source and source in self._sources:
            return self._sources[source](query, start)

        # Roteamento automático
        ql = query.lower()
        if any(w in ql for w in ["ibge", "sidra", "ipca", "pnad", "censo",
                                  "população", "desemprego"]):
            return self._search_ibge(query, start)
        elif any(w in ql for w in ["ipea", "ipeadata"]):
            return self._search_ipea(query, start)
        elif any(w in ql for w in ["dados gov", "dados.gov", "ckan",
                                    "dados abertos"]):
            return self._search_dados_gov(query, start)
        else:
            # Fallback: IBGE
            return self._search_ibge(query, start)

    # ─── IBGE/SIDRA ──────────────────────────────────────────

    def _search_ibge(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            ql = query.lower()

            # Tabelas SIDRA conhecidas
            table_map = {
                "ipca": 7060,
                "pnad": 4093,
                "censo": 4714,
                "população": 4714,
                "pib": 1846,
                "desemprego": 4093,
            }

            table_id = None
            for term, tid in table_map.items():
                if term in ql:
                    table_id = tid
                    break

            if not table_id:
                table_id = 7060  # IPCA default

            # SIDRA API: https://servicodados.ibge.gov.br/api/v3/
            url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{table_id}/periodos/2024/variaveis?view=flat"
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")

            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception:
                # Fallback API para séries históricas
                url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{table_id}/periodos/-5/variaveis?view=flat"
                req = urllib.request.Request(url)
                req.add_header("Accept", "application/json")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

            results = []
            if isinstance(data, list):
                for item in data:
                    results.append({
                        "id": item.get("id", ""),
                        "nome": item.get("nome", ""),
                        "unidade": item.get("unidade", ""),
                        "fonte": "IBGE/SIDRA",
                    })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "ibge", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "ibge", MOCK_DATA["ibge"],
                                     "offline", elapsed)

    # ─── IPEA/Ipeadata ───────────────────────────────────────

    def _search_ipea(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            # API IPEA: http://www.ipeadata.gov.br/api/
            # Formato: http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{codigo}')
            codes = {
                "pib": "PIBPMG",
                "gini": "GINI",
                "investimento": "FBCF",
            }

            ql = query.lower()
            code = "PIBPMG"  # default
            for term, c in codes.items():
                if term in ql:
                    code = c
                    break

            url = f"http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{code}')"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            values = data.get("value", [])
            for item in values[:5]:
                results.append({
                    "codigo": code,
                    "valor": item.get("VALVALOR", 0),
                    "data": item.get("VALDATA", ""),
                    "fonte": "IPEA",
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "ipea", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "ipea", MOCK_DATA["ipea"],
                                     "offline", elapsed)

    # ─── dados.gov.br (CKAN) ─────────────────────────────────

    def _search_dados_gov(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            # CKAN API do dados.gov.br
            params = urllib.parse.urlencode({
                "q": query,
                "rows": 5,
                "format": "json",
            })
            url = f"https://dados.gov.br/api/3/action/package_search?{params}"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for pkg in data.get("result", {}).get("results", []):
                results.append({
                    "titulo": pkg.get("title", ""),
                    "orgao": pkg.get("organization", {}).get("title", ""),
                    "formato": ", ".join(
                        r.get("format", "") for r in pkg.get("resources", [])
                    ),
                    "url": pkg.get("resources", [{}])[0].get("url", "")
                    if pkg.get("resources") else "",
                    "descricao": pkg.get("notes", "")[:200],
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "dados_gov", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "dados_gov", MOCK_DATA["dados_gov"],
                                     "offline", elapsed)
