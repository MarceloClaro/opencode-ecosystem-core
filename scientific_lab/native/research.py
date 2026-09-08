"""Pesquisa científica nativa v4.2 sobre o subsistema ``research`` do Core.

A camada apenas descobre/ordena candidatos e usa o PaperDownloader do Core.
O downloader v4.2 é open-science-only: não contorna paywalls.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
from .common import dump, now, slug, uid

ARTICLE_PLATFORMS = [
    "openalex", "europepmc", "scielo", "arxiv", "semantic_scholar",
    "core", "crossref", "pubmed", "biorxiv",
]
OA_SOURCES = {"openalex", "europepmc", "arxiv", "semantic_scholar", "core"}

def _score(rec) -> float:
    score = 0.0
    if getattr(rec, "pdf_url", None): score += 100
    if getattr(rec, "source", None) in OA_SOURCES: score += 30
    if getattr(rec, "doi", None): score += 15
    score += min(int(getattr(rec, "citations", 0) or 0), 100) / 20.0
    return score

def _to_item(rec, index: int) -> dict:
    source = getattr(rec, "source", "") or "unknown"
    return {
        "article_id": f"ART-{index:04d}",
        "title": getattr(rec, "title", "") or "",
        "doi": getattr(rec, "doi", None) or None,
        "year": getattr(rec, "year", None),
        "authors": list(getattr(rec, "authors", []) or []),
        "venue": getattr(rec, "venue", "") or None,
        "source": source,
        "record_url": getattr(rec, "url", None),
        "landing_url": getattr(rec, "url", None),
        "pdf_url": getattr(rec, "pdf_url", None),
        "oa": bool(getattr(rec, "pdf_url", None) and source in OA_SOURCES),
        "oa_status": "candidate_open" if getattr(rec, "pdf_url", None) and source in OA_SOURCES else None,
        "license": None,
        "cited_by_count": int(getattr(rec, "citations", 0) or 0),
        "retrieval_priority": _score(rec),
        "also_found_in": [],
    }

def search(query: str, workspace: Path, *, limit: int = 30, per_platform: int = 5,
           platforms: Iterable[str] | None = None, searcher_factory=None) -> tuple[Path, list, dict]:
    if not query.strip(): raise ValueError("query vazia")
    if searcher_factory is None:
        from research.searchers import MultiSearcher
        searcher_factory = MultiSearcher
    selected = [p for p in (platforms or ARTICLE_PLATFORMS) if p in ARTICLE_PLATFORMS]
    searcher = searcher_factory(platforms=selected)
    records = [r for r in searcher.search(query, limit_per_platform=per_platform)
               if (getattr(r, "extra", {}) or {}).get("type") not in {"repository", "dataset"}]
    records.sort(key=_score, reverse=True)
    records = records[:limit]
    items = [_to_item(rec, i) for i, rec in enumerate(records, 1)]
    search_id = uid("ASEARCH")
    manifest = {
        "schema_version": "1.0", "search_id": search_id, "query": query,
        "created_at": now(), "source_priority": selected, "results": items,
        "errors": [], "policy": "open_science_only",
        "limitations": [
            "Resultados são candidatos; metadados e conteúdo devem ser conferidos antes de sustentar claims.",
            "Ausência de PDF aberto não implica ausência do artigo.",
        ],
    }
    path = workspace / "01_sources/metadata" / f"search-{slug(query)}-{search_id[-6:]}.json"
    dump(path, manifest)
    return path, records, manifest

def harvest(query: str, workspace: Path, *, limit: int = 30, per_platform: int = 5,
            max_downloads: int = 10, platforms: Iterable[str] | None = None,
            searcher_factory=None, downloader_factory=None) -> dict:
    workspace = workspace.resolve()
    manifest_path, records, manifest = search(
        query, workspace, limit=limit, per_platform=per_platform,
        platforms=platforms, searcher_factory=searcher_factory,
    )
    if downloader_factory is None:
        from research.downloader import PaperDownloader
        downloader_factory = PaperDownloader
    outdir = workspace / "01_sources/pdfs"
    downloader = downloader_factory(str(outdir))
    results = downloader.download(records[:max_downloads])
    receipts = []
    receipt_dir = workspace / "09_provenance/articles"
    for idx, result in enumerate(results, 1):
        item = manifest["results"][idx-1] if idx <= len(manifest["results"]) else {
            "article_id": f"ART-{idx:04d}", "title": getattr(result.record, "title", ""),
            "source": getattr(result.record, "source", None), "doi": getattr(result.record, "doi", None),
            "record_url": getattr(result.record, "url", None),
        }
        extra = dict(getattr(result, "extra", {}) or {})
        receipt = {
            "schema_version": "1.0", "receipt_id": uid("ADL"),
            "search_id": manifest["search_id"], "article_id": item["article_id"],
            "title": item.get("title") or "", "doi": item.get("doi"),
            "source": item.get("source"), "source_url": item.get("record_url"),
            "resolved_pdf_url": extra.get("resolved_pdf_url"),
            "rights_basis": extra.get("rights_basis", "not_verified_open"),
            "license": extra.get("license"), "downloaded_at": extra.get("downloaded_at"),
            "path": result.pdf_path, "sha256": extra.get("sha256"),
            "bytes": int(extra.get("bytes", 0) or 0),
            "status": "downloaded" if result.ok else ("not_open" if extra.get("rights_basis") == "not_verified_open" else "failed"),
            "content_type": extra.get("content_type"),
            "validation": list(extra.get("validation", [])),
            "limitations": list(extra.get("limitations", [])) or ([result.error] if result.error else []),
        }
        rp = receipt_dir / f"{receipt['receipt_id']}.json"; dump(rp, receipt); receipts.append(str(rp))
    summary = {
        "manifest": str(manifest_path), "results": len(records),
        "downloads_attempted": min(len(records), max_downloads),
        "downloads_ok": sum(bool(r.ok) for r in results), "receipts": receipts,
        "policy": "open_science_only",
    }
    dump(workspace / "09_provenance/articles/harvest-summary.json", summary)
    return summary
