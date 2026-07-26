#!/usr/bin/env python3
"""
DatasetDataSource — Datasets Científicos (Zenodo, DataCite, UCI, Figshare)
=============================================================================
Busca datasets de pesquisa em repositórios científicos abertos.

Fontes:
    - Zenodo: 300K+ datasets de pesquisa (CERN)
    - DataCite: 30M+ DOIs de dados de pesquisa
    - UCI ML Repository: 600+ datasets clássicos de ML
    - Figshare: 3M+ itens de pesquisa

Uso:
    from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource
    dds = DatasetDataSource()
    result = dds.search("climate", source="zenodo")
    result = dds.search("iris", source="uci")
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
    "zenodo": [
        {"id": 1000000, "titulo": "Climate Change Dataset 2024",
         "autores": ["IPCC"],
         "ano": 2024, "tipo": "dataset",
         "doi": "10.5281/zenodo.1000000",
         "url": "https://zenodo.org/record/1000000"},
        {"id": 1000001, "titulo": "Global Temperature Records",
         "autores": ["NOAA"],
         "ano": 2023, "tipo": "dataset",
         "doi": "10.5281/zenodo.1000001",
         "url": "https://zenodo.org/record/1000001"},
    ],
    "datacite": [
        {"doi": "10.5061/dryad.abc123",
         "titulo": "Ecological Niche Modeling Dataset",
         "autores": ["Silva, J."],
         "ano": 2024, "editor": "Dryad",
         "url": "https://doi.org/10.5061/dryad.abc123"},
        {"doi": "10.5284/abcdef",
         "titulo": "Archaeological Survey Data",
         "autores": ["Smith, A."],
         "ano": 2023, "editor": "Archaeology Data Service",
         "url": "https://doi.org/10.5284/abcdef"},
    ],
    "uci": [
        {"id": 1, "nome": "Iris",
         "instancias": 150, "atributos": 4,
         "tarefa": "Classification", "ano": 1936,
         "url": "https://archive.ics.uci.edu/ml/datasets/iris"},
        {"id": 53, "nome": "Wine",
         "instancias": 178, "atributos": 13,
         "tarefa": "Classification", "ano": 1991,
         "url": "https://archive.ics.uci.edu/ml/datasets/wine"},
        {"id": 94, "nome": "Air Quality",
         "instancias": 9358, "atributos": 15,
         "tarefa": "Regression", "ano": 2016,
         "url": "https://archive.ics.uci.edu/ml/datasets/air+quality"},
    ],
    "figshare": [
        {"id": 123456, "titulo": "Survey on AI in Healthcare",
         "autores": "WHO Research Group",
         "ano": 2024, "tipo": "dataset",
         "url": "https://figshare.com/articles/dataset/123456"},
        {"id": 123457, "titulo": "Genomic Variants Database",
         "autores": "Broad Institute",
         "ano": 2023, "tipo": "dataset",
         "url": "https://figshare.com/articles/dataset/123457"},
    ],
}


class DatasetDataSource(DataSource):
    """
    Fonte de datasets científicos: Zenodo, DataCite, UCI, Figshare.
    """

    name = "datasets"

    def __init__(self):
        super().__init__()
        self._sources = {
            "zenodo": self._search_zenodo,
            "datacite": self._search_datacite,
            "uci": self._search_uci,
            "figshare": self._search_figshare,
        }

    def search(
        self, query: str, source: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        start = time.time()

        if source and source in self._sources:
            return self._sources[source](query, start)

        # Roteamento automático
        ql = query.lower()
        if any(w in ql for w in ["zenodo", "cern"]):
            return self._search_zenodo(query, start)
        elif any(w in ql for w in ["datacite", "doi", "data citation"]):
            return self._search_datacite(query, start)
        elif any(w in ql for w in ["uci", "ml repository", "machine learning repo"]):
            return self._search_uci(query, start)
        elif any(w in ql for w in ["figshare"]):
            return self._search_figshare(query, start)
        else:
            # Fallback: Zenodo (maior cobertura)
            return self._search_zenodo(query, start)

    # ─── Zenodo ──────────────────────────────────────────────

    def _search_zenodo(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            params = urllib.parse.urlencode({
                "q": query,
                "size": 5,
                "type": "dataset",
                "sort": "mostrecent",
            })
            url = f"https://zenodo.org/api/records?{params}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OpenCodeEcosystem/1.0")

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            hits = data.get("hits", {}).get("hits", data if isinstance(data, list) else [])
            if isinstance(hits, list):
                for item in hits:
                    metadata = item.get("metadata", item)
                    results.append({
                        "id": item.get("id", ""),
                        "titulo": metadata.get("title", ""),
                        "autores": [
                            c.get("name", "") for c in metadata.get("creators", [])
                        ],
                        "ano": metadata.get("publication_date", "")[:4],
                        "tipo": metadata.get("resource_type", {}).get("type", "dataset"),
                        "doi": metadata.get("doi", ""),
                        "url": item.get("links", {}).get("self", f"https://zenodo.org/record/{item.get('id', '')}"),
                        "fonte": "Zenodo",
                    })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "zenodo", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "zenodo", MOCK_DATA["zenodo"],
                                     "offline", elapsed)

    # ─── DataCite ────────────────────────────────────────────

    def _search_datacite(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            params = urllib.parse.urlencode({
                "query": query,
                "rows": 5,
            })
            url = f"https://api.datacite.org/dois?{params}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OpenCodeEcosystem/1.0")

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data.get("data", []):
                attrs = item.get("attributes", {})
                results.append({
                    "doi": attrs.get("doi", ""),
                    "titulo": attrs.get("titles", [{}])[0].get("title", ""),
                    "autores": [
                        c.get("name", "") for c in attrs.get("creators", [])
                    ],
                    "ano": attrs.get("publicationYear", ""),
                    "editor": attrs.get("publisher", ""),
                    "url": f"https://doi.org/{attrs.get('doi', '')}",
                    "fonte": "DataCite",
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "datacite", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "datacite", MOCK_DATA["datacite"],
                                     "offline", elapsed)

    # ─── UCI ML Repository ───────────────────────────────────

    def _search_uci(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            # UCI não tem API REST oficial. Usamos scraping do arquivo de datasets.
            url = "https://archive.ics.uci.edu/ml/datasets.php"
            params = urllib.parse.urlencode({
                "term": query,
                "search": "Search",
            })
            req = urllib.request.Request(f"{url}?{params}")
            req.add_header("User-Agent", "OpenCodeEcosystem/1.0")

            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8")

            # Parsing simples do HTML para extrair datasets
            results = []
            import re
            # Busca padrões de links de dataset
            pattern = r'<a[^>]*href="([^"]*datasets[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html)
            for url_match, name in matches[:5]:
                results.append({
                    "nome": name.strip(),
                    "url": f"https://archive.ics.uci.edu/ml/{url_match}",
                    "fonte": "UCI ML Repository",
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "uci", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "uci", MOCK_DATA["uci"],
                                     "offline", elapsed)

    # ─── Figshare ────────────────────────────────────────────

    def _search_figshare(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            params = urllib.parse.urlencode({
                "search": query,
                "page_size": 5,
                "item_type": 3,  # dataset
            })
            url = f"https://api.figshare.com/v2/articles?{params}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OpenCodeEcosystem/1.0")

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data:
                results.append({
                    "id": item.get("id", ""),
                    "titulo": item.get("title", ""),
                    "autores": [
                        a.get("full_name", "") for a in item.get("authors", [])
                    ] if item.get("authors") else [],
                    "ano": str(item.get("published_date", ""))[:4],
                    "tipo": "dataset" if item.get("item_type") == 3 else "other",
                    "url": item.get("url", f"https://figshare.com/articles/dataset/{item.get('id', '')}"),
                    "fonte": "Figshare",
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "figshare", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "figshare", MOCK_DATA["figshare"],
                                     "offline", elapsed)
