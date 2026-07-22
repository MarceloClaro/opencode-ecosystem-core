# -*- coding: utf-8 -*-
"""
Buscadores e Extratores Multiplataforma (SPEC-017)
===================================================
Busca artigos científicos e repositórios nas principais plataformas:

- arXiv                (http://export.arxiv.org/api/query)
- Semantic Scholar     (https://api.semanticscholar.org/graph/v1)
- Crossref             (https://api.crossref.org/works)
- OpenAlex             (https://api.openalex.org/works)
- Europe PMC           (https://www.ebi.ac.uk/europepmc/webservices/rest)
- SciELO               (via Crossref member filter + busca direta)
- GitHub               (https://api.github.com/search/repositories, ou gh CLI)
- Kaggle               (kaggle CLI, se credenciais disponíveis)

100% stdlib (urllib). Cada buscador degrada graciosamente em caso de
falha de rede, retornando lista vazia com o erro registrado.

Inspiração: scihub-cli e paper-download-mcp (Oxidane-bot).
"""

import json
import logging
import shutil
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger("research.searchers")

USER_AGENT = "opencode-ecosystem-core/1.0 (research subsystem; mailto:contact@example.org)"
DEFAULT_TIMEOUT = 20


@dataclass
class PaperRecord:
    """Registro normalizado de um artigo científico ou repositório."""
    title: str
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: str = ""
    venue: str = ""
    source: str = ""              # plataforma de origem
    citations: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def identifier(self) -> Optional[str]:
        """Melhor identificador para download (DOI > arXiv > URL)."""
        if self.doi:
            return self.doi
        if self.arxiv_id:
            return self.arxiv_id
        return self.pdf_url or self.url

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _http_get(url: str, headers: Optional[Dict[str, str]] = None,
              timeout: int = DEFAULT_TIMEOUT) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _http_get_json(url: str, headers: Optional[Dict[str, str]] = None,
                   timeout: int = DEFAULT_TIMEOUT) -> Any:
    return json.loads(_http_get(url, headers, timeout))


class BaseSearcher:
    """Interface comum: search(query, limit) -> List[PaperRecord]."""
    name = "base"

    def search(self, query: str, limit: int = 10) -> List[PaperRecord]:
        try:
            return self._search(query, limit)
        except Exception as exc:
            logger.warning(f"[{self.name}] busca falhou: {exc}")
            return []

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        raise NotImplementedError


class ArxivSearcher(BaseSearcher):
    """Busca no arXiv via API Atom oficial."""
    name = "arxiv"
    NS = {"atom": "http://www.w3.org/2005/Atom"}

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        url = ("http://export.arxiv.org/api/query?search_query=all:"
               f"{urllib.parse.quote(query)}&start=0&max_results={limit}"
               "&sortBy=relevance")
        root = ET.fromstring(_http_get(url))
        records = []
        for entry in root.findall("atom:entry", self.NS):
            def txt(tag):
                el = entry.find(f"atom:{tag}", self.NS)
                return (el.text or "").strip() if el is not None else ""
            arxiv_url = txt("id")
            arxiv_id = arxiv_url.rsplit("/abs/", 1)[-1] if "/abs/" in arxiv_url else None
            pdf_url = None
            for link in entry.findall("atom:link", self.NS):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href")
            year = None
            published = txt("published")
            if published[:4].isdigit():
                year = int(published[:4])
            records.append(PaperRecord(
                title=" ".join(txt("title").split()),
                authors=[(a.find("atom:name", self.NS).text or "").strip()
                         for a in entry.findall("atom:author", self.NS)],
                year=year,
                arxiv_id=arxiv_id,
                url=arxiv_url,
                pdf_url=pdf_url or (f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else None),
                abstract=" ".join(txt("summary").split()),
                venue="arXiv",
                source=self.name,
            ))
        return records


class SemanticScholarSearcher(BaseSearcher):
    """Busca na Semantic Scholar Graph API (gratuita, sem chave)."""
    name = "semantic_scholar"
    FIELDS = "title,authors,year,externalIds,abstract,venue,citationCount,openAccessPdf,url"

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        url = ("https://api.semanticscholar.org/graph/v1/paper/search?"
               f"query={urllib.parse.quote(query)}&limit={limit}&fields={self.FIELDS}")
        data = _http_get_json(url)
        records = []
        for p in data.get("data", []):
            ext = p.get("externalIds") or {}
            oa = p.get("openAccessPdf") or {}
            records.append(PaperRecord(
                title=p.get("title") or "",
                authors=[a.get("name", "") for a in (p.get("authors") or [])],
                year=p.get("year"),
                doi=ext.get("DOI"),
                arxiv_id=ext.get("ArXiv"),
                url=p.get("url"),
                pdf_url=oa.get("url"),
                abstract=p.get("abstract") or "",
                venue=p.get("venue") or "",
                citations=p.get("citationCount"),
                source=self.name,
            ))
        return records


class CrossrefSearcher(BaseSearcher):
    """Busca na Crossref REST API (metadados DOI oficiais)."""
    name = "crossref"

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        url = (f"https://api.crossref.org/works?query={urllib.parse.quote(query)}"
               f"&rows={limit}&select=DOI,title,author,issued,container-title,"
               "abstract,URL,is-referenced-by-count,link")
        data = _http_get_json(url)
        records = []
        for it in data.get("message", {}).get("items", []):
            year = None
            issued = it.get("issued", {}).get("date-parts", [[None]])
            if issued and issued[0] and issued[0][0]:
                year = issued[0][0]
            authors = []
            for a in it.get("author", []) or []:
                nome = " ".join(x for x in [a.get("given"), a.get("family")] if x)
                if nome:
                    authors.append(nome)
            pdf_url = None
            for link in it.get("link", []) or []:
                if "pdf" in (link.get("content-type") or ""):
                    pdf_url = link.get("URL")
                    break
            abstract = it.get("abstract") or ""
            # Crossref devolve abstract em JATS XML; remove tags simples
            for tag in ("<jats:p>", "</jats:p>", "<jats:title>", "</jats:title>"):
                abstract = abstract.replace(tag, " ")
            records.append(PaperRecord(
                title=(it.get("title") or [""])[0],
                authors=authors,
                year=year,
                doi=it.get("DOI"),
                url=it.get("URL"),
                pdf_url=pdf_url,
                abstract=" ".join(abstract.split()),
                venue=(it.get("container-title") or [""])[0],
                citations=it.get("is-referenced-by-count"),
                source=self.name,
            ))
        return records


class OpenAlexSearcher(BaseSearcher):
    """Busca na OpenAlex API (sucessora do Microsoft Academic Graph)."""
    name = "openalex"

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        url = (f"https://api.openalex.org/works?search={urllib.parse.quote(query)}"
               f"&per-page={limit}")
        data = _http_get_json(url)
        records = []
        for w in data.get("results", []):
            doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
            oa = w.get("open_access") or {}
            best = w.get("best_oa_location") or {}
            abstract = ""
            inv = w.get("abstract_inverted_index")
            if inv:
                # reconstrói o abstract do índice invertido
                pos = {}
                for word, idxs in inv.items():
                    for i in idxs:
                        pos[i] = word
                abstract = " ".join(pos[i] for i in sorted(pos))
            records.append(PaperRecord(
                title=w.get("display_name") or "",
                authors=[a.get("author", {}).get("display_name", "")
                         for a in (w.get("authorships") or [])],
                year=w.get("publication_year"),
                doi=doi,
                url=w.get("id"),
                pdf_url=best.get("pdf_url") or oa.get("oa_url"),
                abstract=abstract,
                venue=(w.get("primary_location") or {}).get("source", {}).get("display_name", "") if (w.get("primary_location") or {}).get("source") else "",
                citations=w.get("cited_by_count"),
                source=self.name,
            ))
        return records


class EuropePmcSearcher(BaseSearcher):
    """Busca no Europe PMC (literatura biomédica OA)."""
    name = "europepmc"

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
               f"query={urllib.parse.quote(query)}&format=json&pageSize={limit}")
        data = _http_get_json(url)
        records = []
        for r in data.get("resultList", {}).get("result", []):
            pmcid = r.get("pmcid")
            pdf_url = (f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}"
                       "/fullTextPDF") if pmcid else None
            records.append(PaperRecord(
                title=r.get("title") or "",
                authors=(r.get("authorString") or "").split(", "),
                year=int(r["pubYear"]) if str(r.get("pubYear", "")).isdigit() else None,
                doi=r.get("doi"),
                url=f"https://europepmc.org/article/{r.get('source')}/{r.get('id')}",
                pdf_url=pdf_url,
                venue=r.get("journalTitle") or "",
                citations=r.get("citedByCount"),
                source=self.name,
            ))
        return records


class ScieloSearcher(BaseSearcher):
    """Busca artigos SciELO via Crossref (member 530 = SciELO)."""
    name = "scielo"

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        url = (f"https://api.crossref.org/members/530/works?"
               f"query={urllib.parse.quote(query)}&rows={limit}"
               "&select=DOI,title,author,issued,container-title,URL")
        data = _http_get_json(url)
        records = []
        for it in data.get("message", {}).get("items", []):
            year = None
            issued = it.get("issued", {}).get("date-parts", [[None]])
            if issued and issued[0] and issued[0][0]:
                year = issued[0][0]
            authors = []
            for a in it.get("author", []) or []:
                nome = " ".join(x for x in [a.get("given"), a.get("family")] if x)
                if nome:
                    authors.append(nome)
            records.append(PaperRecord(
                title=(it.get("title") or [""])[0],
                authors=authors,
                year=year,
                doi=it.get("DOI"),
                url=it.get("URL"),
                venue=(it.get("container-title") or [""])[0],
                source=self.name,
            ))
        return records


class GitHubSearcher(BaseSearcher):
    """Busca repositórios no GitHub (gh CLI se autenticado, senão API pública)."""
    name = "github"

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        if shutil.which("gh"):
            try:
                out = subprocess.run(
                    ["gh", "search", "repos", query, "--limit", str(limit),
                     "--json", "fullName,description,url,stargazersCount,updatedAt"],
                    capture_output=True, text=True, timeout=30)
                if out.returncode == 0 and out.stdout.strip():
                    repos = json.loads(out.stdout)
                    return [self._to_record(r) for r in repos]
            except Exception as exc:
                logger.debug(f"[github] gh CLI falhou, tentando API: {exc}")
        url = ("https://api.github.com/search/repositories?"
               f"q={urllib.parse.quote(query)}&per_page={limit}&sort=stars")
        data = _http_get_json(url, headers={"Accept": "application/vnd.github+json"})
        return [self._to_record({
            "fullName": r.get("full_name"),
            "description": r.get("description"),
            "url": r.get("html_url"),
            "stargazersCount": r.get("stargazers_count"),
            "updatedAt": r.get("updated_at"),
        }) for r in data.get("items", [])]

    def _to_record(self, r: Dict[str, Any]) -> PaperRecord:
        year = None
        updated = r.get("updatedAt") or ""
        if updated[:4].isdigit():
            year = int(updated[:4])
        return PaperRecord(
            title=r.get("fullName") or "",
            year=year,
            url=r.get("url"),
            abstract=r.get("description") or "",
            venue="GitHub",
            source=self.name,
            citations=r.get("stargazersCount"),
            extra={"type": "repository", "stars": r.get("stargazersCount")},
        )


class KaggleSearcher(BaseSearcher):
    """Busca datasets no Kaggle (requer kaggle CLI com credenciais)."""
    name = "kaggle"

    def _search(self, query: str, limit: int) -> List[PaperRecord]:
        if not shutil.which("kaggle"):
            logger.info("[kaggle] CLI não instalada; instale com `pip install kaggle` "
                        "e configure ~/.kaggle/kaggle.json")
            return []
        out = subprocess.run(
            ["kaggle", "datasets", "list", "-s", query, "--csv"],
            capture_output=True, text=True, timeout=45)
        if out.returncode != 0:
            logger.warning(f"[kaggle] erro: {out.stderr[:200]}")
            return []
        lines = out.stdout.strip().splitlines()
        if len(lines) < 2:
            return []
        import csv as _csv
        import io as _io
        reader = _csv.DictReader(_io.StringIO(out.stdout))
        records = []
        for i, row in enumerate(reader):
            if i >= limit:
                break
            ref = row.get("ref") or ""
            records.append(PaperRecord(
                title=row.get("title") or ref,
                url=f"https://www.kaggle.com/datasets/{ref}" if ref else None,
                abstract=f"Dataset Kaggle ({row.get('size', '?')}, "
                         f"downloads: {row.get('downloadCount', '?')})",
                venue="Kaggle",
                source=self.name,
                extra={"type": "dataset", "ref": ref,
                       "downloads": row.get("downloadCount")},
            ))
        return records


ALL_SEARCHERS = {
    "arxiv": ArxivSearcher,
    "semantic_scholar": SemanticScholarSearcher,
    "crossref": CrossrefSearcher,
    "openalex": OpenAlexSearcher,
    "europepmc": EuropePmcSearcher,
    "scielo": ScieloSearcher,
    "github": GitHubSearcher,
    "kaggle": KaggleSearcher,
}


class MultiSearcher:
    """Busca federada em múltiplas plataformas com deduplicação por DOI/título."""

    def __init__(self, platforms: Optional[List[str]] = None):
        names = platforms or list(ALL_SEARCHERS.keys())
        self.searchers = [ALL_SEARCHERS[n]() for n in names if n in ALL_SEARCHERS]

    def search(self, query: str, limit_per_platform: int = 5) -> List[PaperRecord]:
        seen: set = set()
        results: List[PaperRecord] = []
        for searcher in self.searchers:
            for rec in searcher.search(query, limit_per_platform):
                key = (rec.doi or "").lower() or rec.title.lower().strip()[:80]
                if key and key not in seen:
                    seen.add(key)
                    results.append(rec)
        return results
