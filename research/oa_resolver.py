# -*- coding: utf-8 -*-
"""SPEC-935-R1008 — resolução de PDF por vias legais.

Consulta provedores de acesso aberto (Unpaywall, OpenAlex, Crossref) por
`runner` injetável, exige licença observada e URL HTTP(S), e recusa qualquer
fonte bloqueada antes de devolver um candidato.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Mapping

from research.legal_oa_pipeline import is_download_allowed, normalize_doi
from research.source_policy import is_blocked_url

SOURCES: tuple[str, ...] = ("unpaywall", "openalex", "crossref")
_HOST_PRIORITY = {"publisher": 3, "repository": 2, "preprint": 1}

Runner = Callable[[str], Any]


def _validate_doi(norm: str) -> str:
    if not re.match(r"^10\.\d{4,9}/\S+$", norm, re.IGNORECASE):
        raise ValueError(f"DOI inválido: {norm!r}")
    return norm


def _candidate(source: str, data: Mapping[str, Any]) -> dict[str, Any] | None:
    url = (
        data.get("pdf_url")
        or data.get("url_pdf_ou_landing")
        or data.get("best_oa_pdf_url")
        or data.get("url_for_pdf")
    )
    license_value = data.get("license") or data.get("licenca")
    return {
        "source": source,
        "pdf_url": str(url).strip() if url else None,
        "license": license_value,
        "is_oa": data.get("is_oa"),
        "host_type": data.get("host_type") or data.get("oa_status") or "repository",
        "version": data.get("version"),
        "landing_page": data.get("landing_page_url") or data.get("url"),
    }


def openalex_work(doi: str, *, mailto: str | None = None, timeout: int = 45) -> dict[str, Any]:
    """Busca o registro do trabalho no OpenAlex (metadados + localização OA)."""
    import json
    import urllib.parse
    import urllib.request

    norm = _validate_doi(normalize_doi(doi))
    url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(norm, safe='/')}"
    if mailto:
        url += f"?mailto={urllib.parse.quote(mailto)}"
    req = urllib.request.Request(url, headers={"User-Agent": "opencode-core-oa-resolver/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 — endpoint fixo
        return json.loads(response.read().decode("utf-8"))


def openalex_runner(doi: str, *, mailto: str | None = None, timeout: int = 45) -> dict[str, Any]:
    """Runner de produção: devolve o candidato OA a partir do OpenAlex."""
    work = openalex_work(doi, mailto=mailto, timeout=timeout)
    best = work.get("best_oa_location") or {}
    primary = work.get("primary_location") or {}
    return {
        "pdf_url": best.get("pdf_url"),
        "license": best.get("license"),
        "is_oa": (work.get("open_access") or {}).get("is_oa"),
        "host_type": best.get("host_type"),
        "version": best.get("version"),
        "landing_page_url": best.get("landing_page_url") or primary.get("landing_page_url"),
    }


def resolve(doi: str, *, runners: Mapping[str, Runner] | None = None) -> dict[str, Any]:
    """Resolve um PDF legal; sem runners devolve `no_legal_pdf` (fail-closed)."""
    norm = _validate_doi(normalize_doi(doi))
    rejected: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for source in SOURCES:
        runner = (runners or {}).get(source)
        if runner is None:
            continue
        try:
            data = runner(norm)
        except Exception as exc:  # noqa: BLE001 — falha de provedor não derruba a resolução
            rejected.append({"source": source, "reason": "runner_error", "detail": type(exc).__name__})
            continue
        if not isinstance(data, Mapping):
            rejected.append({"source": source, "reason": "invalid_payload"})
            continue

        cand = _candidate(source, data)
        url = cand["pdf_url"]
        if not url:
            rejected.append({"source": source, "reason": "no_pdf_url"})
            continue
        if is_blocked_url(url) or is_blocked_url(cand.get("landing_page")):
            rejected.append({"source": source, "reason": "unauthorized_source", "url": url})
            continue
        if not url.lower().startswith(("http://", "https://")):
            rejected.append({"source": source, "reason": "unsupported_scheme", "url": url})
            continue
        if cand.get("is_oa") is False:
            rejected.append({"source": source, "reason": "not_open_access", "url": url})
            continue

        gate = is_download_allowed({"license": cand["license"], "pdf_url": url})
        if not gate.get("allowed"):
            rejected.append({"source": source, "reason": "license_or_url_missing", "url": url})
            continue

        candidates.append(cand)

    if not candidates:
        return {
            "doi": norm,
            "status": "no_legal_pdf",
            "candidates": [],
            "chosen": None,
            "rejected": rejected,
        }

    chosen = sorted(
        candidates,
        key=lambda c: (-_HOST_PRIORITY.get(str(c.get("host_type")), 0), c["source"]),
    )[0]
    return {
        "doi": norm,
        "status": "ok",
        "candidates": candidates,
        "chosen": chosen,
        "rejected": rejected,
    }
