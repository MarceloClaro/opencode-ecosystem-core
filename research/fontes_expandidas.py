# -*- coding: utf-8 -*-
"""SPEC-980 — Fontes expandidas: Sucupira, PubMed, arXiv, CAPES e brasileiras (stdlib-only)."""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Callable, Dict, List

UA = "opencode-ecosystem-core/1.0 (SPEC-980; mailto:validacao@exemplo.org)"
_BLOCKED = ("sci-hub", "scihub")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _norm_doi(v: str | None) -> str | None:
    if not v:
        return None
    v = re.sub(r"^https?://(dx\.)?doi\.org/", "", str(v).strip(), flags=re.I)
    v = re.sub(r"^doi:\s*", "", v, flags=re.I).strip().lower()
    return v if v.startswith("10.") and "/" in v else None


def _hash(o: dict) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _check(url: str | None) -> None:
    s = str(url or "").lower()
    for b in _BLOCKED:
        if b in s:
            raise PermissionError("blocked: unauthorized_source")


def _fetch(url: str, timeout: int = 20) -> bytes:
    _check(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def buscar_pubmed(query: str, limit: int = 5, fetcher: Callable | None = None) -> List[Dict]:
    q = urllib.parse.quote_plus(query)
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=" + q + "&retmax=" + str(limit) + "&retmode=json"
    try:
        raw = fetcher(url) if fetcher else _fetch(url)
        j = json.loads(raw.decode("utf-8", errors="replace"))
        ids = (j.get("esearchresult") or {}).get("idlist", [])[:limit]
        out = []
        for pmid in ids:
            out.append({"titulo": "PubMed:" + str(pmid), "pmid": pmid, "autores": [], "ano": None,
                        "doi": None, "url": "https://pubmed.ncbi.nlm.nih.gov/" + str(pmid) + "/",
                        "fonte": "pubmed", "url_consulta": url, "data_consulta": _now()})
        for r in out:
            r["hash_resposta"] = _hash(r)
        return out
    except Exception:
        return []


def buscar_arxiv(query: str, limit: int = 5, fetcher=None) -> List[Dict]:
    q = urllib.parse.quote_plus(query)
    url = "http://export.arxiv.org/api/query?search_query=all:" + q + "&start=0&max_results=" + str(limit)
    try:
        raw = fetcher(url) if fetcher else _fetch(url)
        root = ET.fromstring(raw)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        out = []
        for e in root.findall("a:entry", ns)[:limit]:
            title = (e.findtext("a:title", default="", namespaces=ns) or "").strip()
            authors = [a.findtext("a:name", default="", namespaces=ns) for a in e.findall("a:author", ns)]
            aid = (e.findtext("a:id", default="", namespaces=ns) or "").strip().split("/abs/")[-1]
            pdf = "https://arxiv.org/pdf/" + aid + ".pdf" if aid else None
            out.append({"titulo": title, "autores": authors, "arxiv_id": aid, "pdf_url": pdf,
                        "url": "https://arxiv.org/abs/" + aid, "fonte": "arxiv",
                        "url_consulta": url, "data_consulta": _now()})
        for r in out:
            r["hash_resposta"] = _hash(r)
        return out
    except Exception:
        return []


def _oai_search(base: str, fonte: str, query: str, limit: int, fetcher=None) -> List[Dict]:
    url = base + urllib.parse.quote_plus(query)
    try:
        if fetcher:
            fetcher(url)
        return [{"titulo": fonte + ":" + query, "fonte": fonte, "url": url,
                 "url_consulta": url, "data_consulta": _now(),
                 "nota": "landing publica; detalhe via OAI sob demanda"}]
    except Exception:
        return []


def buscar_scielo(query: str, limit: int = 5, fetcher=None) -> List[Dict]:
    return _oai_search("https://search.scielo.org/?q=", "scielo", query, limit, fetcher)[:limit]


def buscar_lilacs(query: str, limit: int = 5, fetcher=None) -> List[Dict]:
    return _oai_search("https://pesquisa.bvsalud.org/portal/?q=", "lilacs", query, limit, fetcher)[:limit]


def buscar_oasisbr_btdt(query: str, limit: int = 5, fetcher=None) -> List[Dict]:
    a = _oai_search("https://oasisbr.ibict.br/search?query=", "oasisbr", query, limit, fetcher)
    b = _oai_search("https://bdtd.ibict.br/search?query=", "bdtd", query, limit, fetcher)
    return (a + b)[:limit]


def buscar_sucupira_observatorio(query: str, limit: int = 5, fetcher=None) -> List[Dict]:
    q = urllib.parse.quote_plus(query)
    url = "https://apigw-proxy.capes.gov.br/observatorio/data/observatorio/ies?search=" + q + "&page=0&size=" + str(min(limit, 10))
    try:
        raw = fetcher(url) if fetcher else _fetch(url)
        j = json.loads(raw.decode("utf-8", errors="replace"))
        items = []
        if isinstance(j, dict):
            items = j.get("content", j.get("data", []))
        elif isinstance(j, list):
            items = j
        out = []
        for it in (items or [])[:limit]:
            nome = it.get("nome", it.get("nm_ies", query)) if isinstance(it, dict) else query
            out.append({"titulo": str(nome), "fonte": "sucupira",
                        "url": "https://sucupira.capes.gov.br/", "url_consulta": url,
                        "data_consulta": _now(), "extra": it})
        if not out:
            out = [{"titulo": "sucupira:" + query, "fonte": "sucupira", "url_consulta": url,
                    "data_consulta": _now(), "nota": "sem itens ou formato variante"}]
        for r in out:
            r["hash_resposta"] = _hash({k: str(v)[:200] for k, v in r.items()})
        return out
    except Exception:
        return []


def buscar_capes_dados_abertos(query: str, limit: int = 5, fetcher=None) -> List[Dict]:
    q = urllib.parse.quote_plus(query)
    url = "https://dadosabertos.capes.gov.br/api/3/action/package_search?q=" + q + "&rows=" + str(min(limit, 10))
    try:
        raw = fetcher(url) if fetcher else _fetch(url)
        j = json.loads(raw.decode("utf-8", errors="replace"))
        res = (j.get("result") or {}).get("results", [])[:limit]
        out = []
        for r in res:
            name = r.get("name", "")
            out.append({"titulo": r.get("title", query), "fonte": "capes_dados_abertos",
                        "url": "https://dadosabertos.capes.gov.br/dataset/" + name,
                        "url_consulta": url, "data_consulta": _now()})
        for r in out:
            r["hash_resposta"] = _hash(r)
        if not out:
            return [{"titulo": "capes:" + query, "fonte": "capes_dados_abertos",
                     "url_consulta": url, "data_consulta": _now()}]
        return out
    except Exception:
        return []


def consultar_portal_capes(doi_ou_titulo: str) -> Dict:
    return {"status": "unavailable", "fonte": "portal_capes",
            "reason": "login institucional exigido; sem bypass",
            "rota_institucional": "Acesse https://www.periodicos.capes.gov.br/ via VPN/login institucional ou peca a biblioteca.",
            "data_consulta": _now()}


def buscar_todas(query: str, limit: int = 5, runners: Dict | None = None) -> List[Dict]:
    runners = runners or {}
    fns = {"pubmed": buscar_pubmed, "arxiv": buscar_arxiv, "scielo": buscar_scielo,
           "lilacs": buscar_lilacs, "oasisbr_bdtd": buscar_oasisbr_btdt,
           "sucupira": buscar_sucupira_observatorio, "capes_abertos": buscar_capes_dados_abertos}
    agg, vistos = [], set()
    for nome, fn in fns.items():
        fetcher = runners.get(nome)
        try:
            res = fn(query, limit, fetcher)
        except TypeError:
            res = fn(query, limit)
        for r in res:
            _check(r.get("pdf_url") or r.get("url"))
            d = _norm_doi(r.get("doi"))
            key = d or (r.get("fonte"), r.get("titulo"))
            if key in vistos:
                continue
            vistos.add(key)
            agg.append(r)
    return agg
