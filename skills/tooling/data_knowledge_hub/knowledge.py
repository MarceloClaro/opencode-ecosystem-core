#!/usr/bin/env python3
"""
KnowledgeDataSource — Conhecimento Geral (Wikipedia, Wikidata, ConceptNet, Google Scholar)
=============================================================================================
Busca conceitos, definições, fatos e relações semânticas.

Fontes:
    - Wikipedia: artigos enciclopédicos (gratuito)
    - Wikidata: grafo de conhecimento estruturado (SPARQL)
    - ConceptNet: rede semântica de conceitos (gratuito)
    - Google Scholar: citações e artigos (via scholarly)

Uso:
    from skills.tooling.data_knowledge_hub.knowledge import KnowledgeDataSource
    kds = KnowledgeDataSource()
    result = kds.search("machine learning", source="wikipedia")
    result = kds.search("Albert Einstein", source="wikidata")
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from .base import DataSource


# ─── Dados Mockados (modo offline) ─────────────────────────

MOCK_DATA = {
    "wikipedia": [
        {"titulo": "Machine learning",
         "sumario": "Machine learning (ML) is a field of study in artificial intelligence "
                    "concerned with the development and study of statistical algorithms that "
                    "can learn from data and generalize to unseen data.",
         "url": "https://en.wikipedia.org/wiki/Machine_learning",
         "categoria": "Artificial intelligence"},
        {"titulo": "Deep learning",
         "sumario": "Deep learning is a subset of machine learning that uses neural networks "
                    "with many layers (deep neural networks) to model complex patterns in data.",
         "url": "https://en.wikipedia.org/wiki/Deep_learning",
         "categoria": "Artificial intelligence"},
    ],
    "wikidata": [
        {"id": "Q25287", "label": "Inteligência artificial",
         "descricao": "field of study in computer science",
         "url": "https://www.wikidata.org/wiki/Q25287"},
        {"id": "Q203000", "label": "Machine learning",
         "descricao": "field of study in artificial intelligence",
         "url": "https://www.wikidata.org/wiki/Q203000"},
    ],
    "conceptnet": [
        {"conceito": "/c/pt/inteligência_artificial",
         "relacao": "IsA", "target": "/c/en/artificial_intelligence",
         "peso": 5.0},
        {"conceito": "/c/pt/machine_learning",
         "relacao": "UsedFor", "target": "/c/en/prediction",
         "peso": 3.0},
    ],
    "google_scholar": [
        {"titulo": "Attention is all you need",
         "autores": "Vaswani et al.",
         "ano": 2017, "citacoes": 95000,
         "url": "https://scholar.google.com/scholar?q=attention+is+all+you+need"},
        {"titulo": "Deep learning",
         "autores": "LeCun, Bengio, Hinton",
         "ano": 2015, "citacoes": 80000,
         "url": "https://scholar.google.com/scholar?q=deep+learning"},
    ],
}


class KnowledgeDataSource(DataSource):
    """
    Fonte de conhecimento geral: Wikipedia, Wikidata, ConceptNet, Google Scholar.
    """

    name = "knowledge"

    def __init__(self):
        super().__init__()
        self._sources = {
            "wikipedia": self._search_wikipedia,
            "wikidata": self._search_wikidata,
            "conceptnet": self._search_conceptnet,
            "google_scholar": self._search_google_scholar,
        }

    def search(
        self, query: str, source: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        start = time.time()

        if source and source in self._sources:
            return self._sources[source](query, start)

        # Roteamento automático
        ql = query.lower()
        if any(w in ql for w in ["o que é", "o que e", "conceito", "definição",
                                  "definir", "significa", "wikipedia",
                                  "significado"]):
            return self._search_wikipedia(query, start)
        elif any(w in ql for w in ["wikidata", "sparql", "entidade", "ontologia",
                                    "classe", "propriedade"]):
            return self._search_wikidata(query, start)
        elif any(w in ql for w in ["conceito", "relação", "relacao", "análogo",
                                    "similar", "conceptnet", "rede semântica"]):
            return self._search_conceptnet(query, start)
        elif any(w in ql for w in ["scholar", "citações", "citacoes", "artigo",
                                    "paper", "publicação", "publicacao",
                                    "google scholar"]):
            return self._search_google_scholar(query, start)
        else:
            # Fallback: Wikipedia
            return self._search_wikipedia(query, start)

    # ─── Wikipedia ───────────────────────────────────────────

    def _search_wikipedia(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            params = urllib.parse.urlencode({
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": 5,
                "srprop": "snippet",
            })
            url = f"https://pt.wikipedia.org/w/api.php?{params}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OpenCodeEcosystem/1.0")

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data.get("query", {}).get("search", []):
                results.append({
                    "titulo": item.get("title", ""),
                    "snippet": item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                    "page_id": item.get("pageid", 0),
                    "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', '').replace(' ', '_'))}",
                    "idioma": "pt",
                })

            if not results:
                # Tentar inglês
                url_en = f"https://en.wikipedia.org/w/api.php?{params}"
                req_en = urllib.request.Request(url_en)
                req_en.add_header("User-Agent", "OpenCodeEcosystem/1.0")
                with urllib.request.urlopen(req_en, timeout=10) as resp_en:
                    data_en = json.loads(resp_en.read().decode("utf-8"))
                for item in data_en.get("query", {}).get("search", []):
                    results.append({
                        "titulo": item.get("title", ""),
                        "snippet": item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                        "page_id": item.get("pageid", 0),
                        "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', '').replace(' ', '_'))}",
                        "idioma": "en",
                    })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "wikipedia", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "wikipedia", MOCK_DATA["wikipedia"],
                                     "offline", elapsed)

    # ─── Wikidata ─────────────────────────────────────────────

    def _search_wikidata(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            # Wikidata SPARQL via API
            sparql = urllib.parse.quote(
                f"SELECT ?item ?itemLabel ?itemDescription WHERE {{ "
                f"  ?item wdt:P31 wd:Q5 . "
                f"  ?item ?label \"{query}\"@en . "
                f"  SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"en,pt\". }} "
                f"}} LIMIT 5"
            )
            url = f"https://query.wikidata.org/sparql?format=json&query={sparql}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OpenCodeEcosystem/1.0")

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data.get("results", {}).get("bindings", []):
                results.append({
                    "id": item.get("item", {}).get("value", "").split("/")[-1],
                    "label": item.get("itemLabel", {}).get("value", ""),
                    "descricao": item.get("itemDescription", {}).get("value", ""),
                    "url": item.get("item", {}).get("value", ""),
                    "fonte": "Wikidata",
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "wikidata", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "wikidata", MOCK_DATA["wikidata"],
                                     "offline", elapsed)

    # ─── ConceptNet ───────────────────────────────────────────

    def _search_conceptnet(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            # Busca no ConceptNet
            query_encoded = urllib.parse.quote(f"/c/pt/{query.lower().replace(' ', '_')}")
            url = f"https://api.conceptnet.io{query_encoded}?limit=5"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OpenCodeEcosystem/1.0")

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for edge in data.get("edges", []):
                results.append({
                    "conceito": edge.get("start", {}).get("label", ""),
                    "relacao": edge.get("rel", {}).get("label", ""),
                    "target": edge.get("end", {}).get("label", ""),
                    "peso": edge.get("weight", 0),
                    "fonte": "ConceptNet",
                })

            # Se não achou em português, tenta inglês
            if not results:
                query_en = urllib.parse.quote(f"/c/en/{query.lower().replace(' ', '_')}")
                url_en = f"https://api.conceptnet.io{query_en}?limit=5"
                req_en = urllib.request.Request(url_en)
                req_en.add_header("User-Agent", "OpenCodeEcosystem/1.0")
                with urllib.request.urlopen(req_en, timeout=10) as resp_en:
                    data_en = json.loads(resp_en.read().decode("utf-8"))
                for edge in data_en.get("edges", []):
                    results.append({
                        "conceito": edge.get("start", {}).get("label", ""),
                        "relacao": edge.get("rel", {}).get("label", ""),
                        "target": edge.get("end", {}).get("label", ""),
                        "peso": edge.get("weight", 0),
                        "fonte": "ConceptNet",
                    })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "conceptnet", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "conceptnet", MOCK_DATA["conceptnet"],
                                     "offline", elapsed)

    # ─── Google Scholar ───────────────────────────────────────

    def _search_google_scholar(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            # Tenta scholarly (biblioteca externa)
            try:
                import scholarly
                search_query = scholarly.search_pubs(query)
                results = []
                for i, pub in enumerate(search_query):
                    if i >= 5:
                        break
                    results.append({
                        "titulo": pub.get("bib", {}).get("title", ""),
                        "autores": ", ".join(pub.get("bib", {}).get("author", [])),
                        "ano": pub.get("bib", {}).get("year", ""),
                        "citacoes": pub.get("cites", 0),
                        "url": pub.get("pub_url", ""),
                        "fonte": "Google Scholar",
                    })

                elapsed = (time.time() - start_time) * 1000
                success = len(results) > 0
                self._record_query(elapsed, success)
                return self._make_result(query, "google_scholar", results,
                                         "online" if success else "offline", elapsed)

            except ImportError:
                # Fallback: usamos o searchers.py que já tem Semantic Scholar
                try:
                    from research.searchers import SemanticScholarSearcher
                    ss = SemanticScholarSearcher()
                    raw_results = ss.search(query, limit=5)
                    results = []
                    for r in raw_results:
                        results.append({
                            "titulo": r.get("title", ""),
                            "autores": ", ".join(
                                a.get("name", "") for a in r.get("authors", [])
                            ) if r.get("authors") else "",
                            "ano": r.get("year", ""),
                            "citacoes": r.get("citationCount", 0),
                            "url": r.get("url", ""),
                            "fonte": "Semantic Scholar (via Google Scholar fallback)",
                        })

                    elapsed = (time.time() - start_time) * 1000
                    success = len(results) > 0
                    self._record_query(elapsed, success)
                    return self._make_result(query, "google_scholar", results,
                                             "online" if success else "offline", elapsed)
                except Exception:
                    raise

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "google_scholar",
                                     MOCK_DATA["google_scholar"],
                                     "offline", elapsed)
