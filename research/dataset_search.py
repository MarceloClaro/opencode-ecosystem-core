# -*- coding: utf-8 -*-
"""SPEC-935-R1007 — Buscador de datasets multi-provedor (stdlib-only).

Busca metadados em Zenodo, DataCite, Figshare, OpenAlex, Hugging Face e GBIF;
normaliza, deduplica, pontua relevância e prontidão FAIR de forma determinística
e emite manifesto com SHA-256.

Princípios:
- Rede só por `runner` injetável; sem runner o provedor fica `unavailable`.
- Nenhum valor é fabricado: campo ausente é `None`.
- Fonte bloqueada nunca vira resultado.
- Licença ausente nunca é tratada como aberta.
- O ranking expõe pesos e componentes; a ordem é estável e auditável.

Uso:
    python3 -m research.dataset_search "soil moisture" --limit 10
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from html import unescape
from typing import Any, Callable, Iterable, Sequence
from urllib.parse import quote_plus, urlparse

from research.source_policy import is_blocked_url

PROVIDERS: tuple[str, ...] = (
    "zenodo",
    "datacite",
    "figshare",
    "openalex",
    "huggingface",
    "gbif",
)

DEFAULT_WEIGHTS = {"relevance": 0.6, "fair": 0.3, "recency": 0.1}

_OPEN_LICENSE_HINTS = (
    "cc0",
    "cc-by",
    "cc by",
    "public domain",
    "pddl",
    "odc-by",
    "odbl",
    "mit",
    "apache",
    "bsd",
    "gpl",
    "creativecommons.org/publicdomain",
    "creativecommons.org/licenses/by/",
)
_RESTRICTED_LICENSE_HINTS = ("nc", "nd", "noncommercial", "no derivatives")

_CORE_FORMATS = frozenset(
    {
        "csv", "tsv", "parquet", "json", "jsonl", "ndjson", "nc", "netcdf",
        "tif", "tiff", "geotiff", "h5", "hdf5", "sqlite", "db", "feather",
        "arrow", "zarr", "las", "laz", "shp", "geojson",
    }
)
_ARCHIVE_FORMATS = frozenset({"zip", "tar", "gz", "tgz", "7z", "rar"})


# ── infraestrutura ───────────────────────────────────────────────────────────


def _utc_now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _norm(value: object) -> str:
    return str(value or "").strip().lower()


def _as_int(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_year(value: object) -> int | None:
    if isinstance(value, int):
        return value if 1000 <= value <= 3000 else None
    text = str(value or "").strip()
    match = re.match(r"^(\d{4})", text)
    return int(match.group(1)) if match else None


def _strip_html(value: object) -> str:
    text = unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _extension(name: str) -> str | None:
    base = name.lower().rstrip("/").split("/")[-1]
    if "." not in base:
        return None
    return base.rsplit(".", 1)[-1]


def _formats_from_names(names: Iterable[str]) -> tuple[str, ...]:
    found = {ext for ext in (_extension(n) for n in names) if ext}
    return tuple(sorted(found))


def classify_license(value: object) -> tuple[str | None, str]:
    """Devolve (licença original, classe open|restricted|unknown)."""
    if value is None:
        return None, "unknown"
    text = _strip_html(value)
    if not text:
        return None, "unknown"
    s = text.lower()
    if any(h in s for h in _RESTRICTED_LICENSE_HINTS):
        return text, "restricted"
    if any(h in s for h in _OPEN_LICENSE_HINTS):
        return text, "open"
    return text, "unknown"


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ── registro ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DatasetRecord:
    provider: str
    source_id: str
    title: str
    authors: tuple[str, ...] = ()
    year: int | None = None
    doi: str | None = None
    url: str = ""
    license: str | None = None
    license_class: str = "unknown"
    access: str = "unknown"
    formats: tuple[str, ...] = ()
    description: str = ""
    updated: str | None = None
    downloads: int | None = None
    citations: int | None = None
    provenance: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "source_id": self.source_id,
            "title": self.title,
            "authors": list(self.authors),
            "year": self.year,
            "doi": self.doi,
            "url": self.url,
            "license": self.license,
            "license_class": self.license_class,
            "access": self.access,
            "formats": list(self.formats),
            "description": self.description,
            "updated": self.updated,
            "downloads": self.downloads,
            "citations": self.citations,
            "provenance": list(self.provenance),
        }


def _record(
    *,
    provider: str,
    source_id: str,
    title: str,
    endpoint: str,
    retrieved_at: str,
    raw: Any,
    **fields: Any,
) -> DatasetRecord:
    license_value, license_class = classify_license(fields.pop("license", None))
    provenance = {
        "provider": provider,
        "endpoint": endpoint,
        "retrieved_at": retrieved_at,
        "raw_sha256": _sha256_json(raw),
    }
    return DatasetRecord(
        provider=provider,
        source_id=str(source_id),
        title=_strip_html(title),
        license=license_value,
        license_class=license_class,
        provenance=(provenance,),
        **fields,
    )


# ── requisições ──────────────────────────────────────────────────────────────


def build_request(provider: str, query: str, limit: int = 10) -> dict[str, Any]:
    """Monta a requisição HTTP de cada provedor (sem executar)."""
    if provider not in PROVIDERS:
        raise ValueError(f"provedor desconhecido: {provider!r}")
    if limit <= 0:
        raise ValueError("limit deve ser > 0")

    q = quote_plus(query.strip())
    headers = {"Accept": "application/json", "User-Agent": "opencode-core-dataset-search/1.0"}

    if provider == "zenodo":
        url = f"https://zenodo.org/api/records?q={q}&type=dataset&size={limit}"
        return {"provider": provider, "method": "GET", "url": url, "body": None, "headers": headers}
    if provider == "datacite":
        url = (
            "https://api.datacite.org/dois"
            f"?query={q}&resource-type-id=dataset&page%5Bsize%5D={limit}"
        )
        return {"provider": provider, "method": "GET", "url": url, "body": None, "headers": headers}
    if provider == "figshare":
        body = json.dumps({"search_for": query.strip(), "page_size": limit})
        return {
            "provider": provider,
            "method": "POST",
            "url": "https://api.figshare.com/v2/articles/search",
            "body": body,
            "headers": {**headers, "Content-Type": "application/json"},
        }
    if provider == "openalex":
        url = f"https://api.openalex.org/works?search={q}&filter=type:dataset&per-page={limit}"
        return {"provider": provider, "method": "GET", "url": url, "body": None, "headers": headers}
    if provider == "huggingface":
        url = f"https://huggingface.co/api/datasets?search={q}&limit={limit}"
        return {"provider": provider, "method": "GET", "url": url, "body": None, "headers": headers}
    # gbif
    url = f"https://api.gbif.org/v1/dataset/search?q={q}&limit={limit}"
    return {"provider": provider, "method": "GET", "url": url, "body": None, "headers": headers}


# ── parsers ──────────────────────────────────────────────────────────────────


def _parse_zenodo(payload: Any, endpoint: str, retrieved_at: str) -> list[DatasetRecord]:
    out: list[DatasetRecord] = []
    hits = ((payload or {}).get("hits") or {}).get("hits") or []
    for item in hits:
        md = item.get("metadata") or {}
        lic = md.get("license")
        lic_value = lic.get("id") if isinstance(lic, dict) else lic
        files = item.get("files") or []
        links = item.get("links") or {}
        url = links.get("self_html") or item.get("doi_url") or ""
        authors = tuple(
            str(c.get("name")).strip()
            for c in (md.get("creators") or [])
            if isinstance(c, dict) and c.get("name")
        )
        out.append(
            _record(
                provider="zenodo",
                source_id=item.get("id", ""),
                title=md.get("title", ""),
                endpoint=endpoint,
                retrieved_at=retrieved_at,
                raw=item,
                authors=authors,
                year=_as_year(md.get("publication_date")),
                doi=(item.get("doi") or None),
                url=url,
                license=lic_value,
                access="open",
                formats=_formats_from_names(f.get("key", "") for f in files if isinstance(f, dict)),
                description=_strip_html(md.get("description")),
                updated=item.get("updated"),
            )
        )
    return out


def _parse_datacite(payload: Any, endpoint: str, retrieved_at: str) -> list[DatasetRecord]:
    out: list[DatasetRecord] = []
    for item in (payload or {}).get("data") or []:
        attrs = item.get("attributes") or {}
        titles = attrs.get("titles") or []
        title = titles[0].get("title", "") if titles and isinstance(titles[0], dict) else ""
        creators = tuple(
            str(c.get("name")).strip()
            for c in (attrs.get("creators") or [])
            if isinstance(c, dict) and c.get("name")
        )
        rights = attrs.get("rightsList") or []
        lic = None
        if rights and isinstance(rights[0], dict):
            lic = rights[0].get("rightsIdentifier") or rights[0].get("rights")
        doi = attrs.get("doi") or item.get("id")
        out.append(
            _record(
                provider="datacite",
                source_id=item.get("id", ""),
                title=title,
                endpoint=endpoint,
                retrieved_at=retrieved_at,
                raw=item,
                authors=creators,
                year=_as_year(attrs.get("publicationYear")),
                doi=doi,
                url=attrs.get("url") or (f"https://doi.org/{doi}" if doi else ""),
                license=lic,
                access="open",
                description=_strip_html((attrs.get("descriptions") or [{}])[0].get("description", ""))
                if attrs.get("descriptions")
                else "",
            )
        )
    return out


def _parse_figshare(payload: Any, endpoint: str, retrieved_at: str) -> list[DatasetRecord]:
    out: list[DatasetRecord] = []
    for item in payload or []:
        lic = item.get("license")
        lic_value = lic.get("name") if isinstance(lic, dict) else lic
        out.append(
            _record(
                provider="figshare",
                source_id=item.get("id", ""),
                title=item.get("title", ""),
                endpoint=endpoint,
                retrieved_at=retrieved_at,
                raw=item,
                year=_as_year(item.get("published_date")),
                doi=item.get("doi") or None,
                url=item.get("url_public_html") or item.get("url") or "",
                license=lic_value,
                access="open",
                updated=item.get("modified_date") or item.get("published_date"),
            )
        )
    return out


def _parse_openalex(payload: Any, endpoint: str, retrieved_at: str) -> list[DatasetRecord]:
    out: list[DatasetRecord] = []
    for work in (payload or {}).get("results") or []:
        best = work.get("best_oa_location") or {}
        primary = work.get("primary_location") or {}
        doi = str(work.get("doi") or "").replace("https://doi.org/", "") or None
        oa = work.get("open_access") or {}
        out.append(
            _record(
                provider="openalex",
                source_id=str(work.get("id", "")),
                title=work.get("title") or work.get("display_name") or "",
                endpoint=endpoint,
                retrieved_at=retrieved_at,
                raw=work,
                year=_as_year(work.get("publication_year")),
                doi=doi,
                url=best.get("landing_page_url") or primary.get("landing_page_url") or work.get("id", ""),
                license=best.get("license"),
                access="open" if oa.get("is_oa") else "unknown",
                citations=_as_int(work.get("cited_by_count")),
            )
        )
    return out


def _parse_huggingface(payload: Any, endpoint: str, retrieved_at: str) -> list[DatasetRecord]:
    out: list[DatasetRecord] = []
    for item in payload or []:
        tags = [str(t) for t in (item.get("tags") or [])]
        lic = next((t.split(":", 1)[1] for t in tags if t.startswith("license:")), None)
        formats = tuple(sorted({t.split(":", 1)[1] for t in tags if t.startswith("format:")}))
        updated = item.get("lastModified")
        access = "restricted" if item.get("gated") or item.get("private") else "open"
        author = item.get("author")
        out.append(
            _record(
                provider="huggingface",
                source_id=str(item.get("id", "")),
                title=str(item.get("id", "")),
                endpoint=endpoint,
                retrieved_at=retrieved_at,
                raw=item,
                authors=(author,) if author else (),
                year=_as_year(updated),
                url=f"https://huggingface.co/datasets/{item.get('id')}" if item.get("id") else "",
                license=lic,
                access=access,
                formats=formats,
                updated=updated,
                downloads=_as_int(item.get("downloads")),
            )
        )
    return out


def _parse_gbif(payload: Any, endpoint: str, retrieved_at: str) -> list[DatasetRecord]:
    out: list[DatasetRecord] = []
    for item in (payload or {}).get("results") or []:
        key = item.get("key")
        out.append(
            _record(
                provider="gbif",
                source_id=str(key or ""),
                title=item.get("title", ""),
                endpoint=endpoint,
                retrieved_at=retrieved_at,
                raw=item,
                year=_as_year(item.get("pubDate") or item.get("created")),
                doi=item.get("doi") or None,
                url=f"https://www.gbif.org/dataset/{key}" if key else "",
                license=item.get("license"),
                access="open",
                description=_strip_html(item.get("description")),
                updated=item.get("modified") or item.get("pubDate"),
            )
        )
    return out


_PARSERS: dict[str, Callable[[Any, str, str], list[DatasetRecord]]] = {
    "zenodo": _parse_zenodo,
    "datacite": _parse_datacite,
    "figshare": _parse_figshare,
    "openalex": _parse_openalex,
    "huggingface": _parse_huggingface,
    "gbif": _parse_gbif,
}


def parse(
    provider: str,
    payload: Any,
    *,
    endpoint: str,
    retrieved_at: str,
    rejected: list[dict[str, Any]] | None = None,
) -> list[DatasetRecord]:
    """Normaliza um payload e descarta fontes bloqueadas."""
    if provider not in _PARSERS:
        raise ValueError(f"provedor desconhecido: {provider!r}")
    records = _PARSERS[provider](payload, endpoint, retrieved_at)
    allowed: list[DatasetRecord] = []
    for rec in records:
        if is_blocked_url(rec.url) or (rec.doi and is_blocked_url(rec.doi)):
            if rejected is not None:
                rejected.append(
                    {"provider": provider, "reason": "unauthorized_source", "url": rec.url or rec.doi}
                )
            continue
        allowed.append(rec)
    return allowed


# ── deduplicação ─────────────────────────────────────────────────────────────


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _strip_html(title).lower()).strip()


def _richness(rec: DatasetRecord) -> tuple[int, int]:
    filled = sum(
        1
        for value in (rec.authors, rec.year, rec.doi, rec.url, rec.license, rec.description)
        if value
    )
    return (filled, len(rec.description or ""))


def _merge(group: Sequence[DatasetRecord]) -> DatasetRecord:
    primary = max(group, key=_richness)
    rank = {"open": 3, "restricted": 2, "unknown": 1}
    best_license = max(group, key=lambda r: rank.get(r.license_class, 0))
    best_access = max(group, key=lambda r: rank.get(r.access, 0))
    provenance: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rec in group:
        for prov in rec.provenance:
            key = str(prov.get("raw_sha256"))
            if key not in seen:
                seen.add(key)
                provenance.append(dict(prov))
    formats = tuple(sorted({fmt for rec in group for fmt in rec.formats}))
    authors = max((rec.authors for rec in group), key=len, default=())
    description = max((rec.description or "" for rec in group), key=len, default="")
    doi = next((rec.doi for rec in group if rec.doi), None)
    downloads = max((rec.downloads for rec in group if rec.downloads is not None), default=None)
    citations = max((rec.citations for rec in group if rec.citations is not None), default=None)
    updated = max((rec.updated for rec in group if rec.updated), default=None)

    return DatasetRecord(
        **{
            **primary.to_dict(),
            "authors": authors,
            "doi": doi,
            "license": best_license.license,
            "license_class": best_license.license_class,
            "access": best_access.access,
            "formats": formats,
            "description": description,
            "updated": updated,
            "downloads": downloads,
            "citations": citations,
            "provenance": tuple(provenance),
        }
    )


def deduplicate(records: Iterable[DatasetRecord]) -> list[DatasetRecord]:
    """Agrupa por DOI (case-insensitive) ou título normalizado + ano."""
    groups: dict[str, list[DatasetRecord]] = {}
    order: list[str] = []
    for rec in records:
        if rec.doi:
            key = f"doi:{rec.doi.lower()}"
        else:
            key = f"title:{_norm_title(rec.title)}|{rec.year}"
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(rec)
    return [_merge(groups[key]) for key in order]


# ── pontuação ────────────────────────────────────────────────────────────────


def fair_score(record: DatasetRecord) -> dict[str, Any]:
    """Prontidão FAIR observável (0..1), com componentes explícitos."""
    formats = set(record.formats)
    if formats & _CORE_FORMATS:
        machine = 0.15
    elif formats & _ARCHIVE_FORMATS:
        machine = 0.05
    else:
        machine = 0.0

    components = {
        "identifiable": 0.25 if record.doi else 0.0,
        "licensed": {"open": 0.20, "restricted": 0.10}.get(record.license_class, 0.0),
        "access": {"open": 0.20, "restricted": 0.05}.get(record.access, 0.0),
        "machine_readable": machine,
        "documented": 0.10 if len(record.description or "") >= 100 else 0.0,
        "versioned": 0.10 if record.updated else 0.0,
    }
    return {"score": round(sum(components.values()), 4), "components": components}


def relevance_score(query: str, record: DatasetRecord) -> float:
    """Sobreposição de termos com pesos por campo (0..1)."""
    q = _tokens(query)
    if not q:
        return 0.0
    title = _tokens(record.title)
    description = _tokens(record.description)
    authors = _tokens(" ".join(record.authors))
    raw = (
        3.0 * len(q & title) / len(q)
        + 1.0 * len(q & description) / len(q)
        + 0.5 * len(q & authors) / len(q)
    )
    return round(min(1.0, raw / 4.5), 4)


def _recency_score(year: int | None, now_year: int) -> float:
    if year is None:
        return 0.0
    idade = max(0, now_year - year)
    return round(max(0.0, 1.0 - idade / 10.0), 4)


def rank(
    query: str,
    records: Iterable[DatasetRecord],
    *,
    weights: dict[str, float] | None = None,
    now_year: int | None = None,
) -> list[dict[str, Any]]:
    """Ordena de forma estável e explica cada componente."""
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    if abs(sum(w.values()) - 1.0) > 1e-9:
        raise ValueError("pesos devem somar 1.0")
    year_ref = now_year or datetime.datetime.now(datetime.timezone.utc).year

    rows: list[dict[str, Any]] = []
    for rec in records:
        fair = fair_score(rec)
        rel = relevance_score(query, rec)
        recency = _recency_score(rec.year, year_ref)
        final = round(w["relevance"] * rel + w["fair"] * fair["score"] + w["recency"] * recency, 6)
        row = rec.to_dict()
        row["scores"] = {
            "relevance": rel,
            "fair": fair["score"],
            "recency": recency,
            "final": final,
            "components": fair["components"],
            "weights": w,
        }
        rows.append(row)

    rows.sort(key=lambda r: (-r["scores"]["final"], (r["doi"] or "").lower(), r["title"].lower()))
    return rows


# ── busca e manifesto ────────────────────────────────────────────────────────

Runner = Callable[[str, dict[str, Any]], Any]


def search(
    query: str,
    *,
    providers: Sequence[str] = PROVIDERS,
    limit: int = 10,
    runner: Runner | None = None,
    now: str | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Executa a busca. Sem runner, cada provedor fica `unavailable`."""
    if not str(query).strip():
        raise ValueError("query vazia")

    retrieved_at = _utc_now(now)
    rejected: list[dict[str, Any]] = []
    records: list[DatasetRecord] = []
    status: dict[str, dict[str, Any]] = {}

    for provider in providers:
        request = build_request(provider, query, limit)
        if runner is None:
            status[provider] = {"status": "unavailable", "count": 0}
            continue
        try:
            payload = runner(provider, request)
        except Exception as exc:  # noqa: BLE001 — falha de provedor não derruba a busca
            status[provider] = {"status": "error", "count": 0, "error": type(exc).__name__}
            continue
        parsed = parse(provider, payload, endpoint=request["url"], retrieved_at=retrieved_at, rejected=rejected)
        records.extend(parsed)
        status[provider] = {"status": "ok", "count": len(parsed)}

    merged = deduplicate(records)
    ranked = rank(query, merged, weights=weights, now_year=_as_year(retrieved_at))

    return {
        "query": query,
        "retrieved_at": retrieved_at,
        "providers": status,
        "count": len(ranked),
        "results": ranked[:limit],
        "rejected": rejected,
    }


def manifest(report: dict[str, Any]) -> dict[str, str]:
    """Manifesto canônico do relatório; qualquer alteração muda o SHA-256."""
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return {"sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(), "payload": payload}


def http_runner(provider: str, request: dict[str, Any], timeout: int = 45, attempts: int = 3) -> Any:
    """Runner padrão via urllib (rede real), com retry limitado em 429/5xx.

    O retry é determinístico em quantidade e usa `Retry-After` quando presente.
    Falha persistente propaga a exceção; `search` a converte em `status=error`
    sem derrubar os demais provedores.
    """
    import time
    import urllib.error
    import urllib.request

    data = request["body"].encode("utf-8") if request.get("body") else None
    last: Exception | None = None

    for attempt in range(attempts):
        req = urllib.request.Request(
            request["url"],
            data=data,
            method=request["method"],
            headers=request.get("headers") or {},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 — endpoints fixos
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last = exc
            retryable = exc.code in (429, 500, 502, 503, 504)
            if not retryable or attempt == attempts - 1:
                raise
            header = exc.headers.get("Retry-After") if exc.headers else None
            delay = float(header) if header and str(header).isdigit() else 0.5 * (2**attempt)
            time.sleep(min(delay, 5.0))

    raise last if last else RuntimeError("falha desconhecida")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Busca científica de datasets (SPEC-935-R1007)")
    parser.add_argument("query", help="termos de busca")
    parser.add_argument("--providers", default=",".join(PROVIDERS))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--offline", action="store_true", help="sem rede: só monta requisições")
    parser.add_argument("--json", action="store_true", help="imprime JSON")
    args = parser.parse_args(argv)

    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    if args.offline:
        report = search(args.query, providers=providers, limit=args.limit, runner=None)
    else:
        report = search(args.query, providers=providers, limit=args.limit, runner=http_runner)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for row in report["results"]:
            print(f"{row['scores']['final']:.3f}  {row['provider']:11s}  {row['title'][:90]}")
    print(f"# {report['count']} resultados | sha256={manifest(report)['sha256'][:16]}…", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
