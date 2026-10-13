# -*- coding: utf-8 -*-
"""SPEC-977 — Pipeline de Acesso Aberto Legal por DOI (stdlib-only).

Contratos R-977.1 a R-977.9. Runner injetável fail-closed (padrão R473).
Nenhuma dependência nova. Nenhum contato com Sci-Hub.
"""
from __future__ import annotations

import datetime
import hashlib
import re
from urllib.parse import urlparse

_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
_BLOCKED_SUBSTRINGS = ("sci-hub", "scihub", "sci-hub.")
_ALLOWED_LICENSE_HINTS = ("cc-", "public", "open", "oa", "unpaywall", "publisher-oa")


def normalize_doi(doi: str) -> str:
    """Normaliza DOI de forma determinística (INV-977.4)."""
    if not isinstance(doi, str):
        raise ValueError("DOI deve ser str")
    v = doi.strip().lower()
    v = re.sub(r"^https?://(dx\.)?doi\.org/", "", v)
    v = re.sub(r"^doi:\s*", "", v)
    return v


def _validate_doi_or_raise(norm: str) -> str:
    if not _DOI_RE.match(norm):
        raise ValueError(f"DOI inválido: {norm!r}")
    return norm


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _hash_payload(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def resolve_doi(doi: str, runner=None) -> dict:
    """R-977.1: resolve metadados canônicos via Crossref (injetável).

    - DOI inválido: ValueError antes de qualquer rede.
    - Sem runner: abstém-se com status=unavailable (fail-closed).
    - Com runner: delega e preserva proveniência; nunca fabrica metadados.
    """
    norm = _validate_doi_or_raise(normalize_doi(doi))
    if runner is None:
        return {
            "doi": norm,
            "status": "unavailable",
            "fonte": "crossref",
            "licenca": None,
            "data_consulta": _utc_now_iso(),
            "reason": "runner ausente",
            "evidence_eligible": False,
        }
    data = runner(norm)
    if not isinstance(data, dict):
        raise ValueError("runner deve retornar dict")
    out = dict(data)
    out.setdefault("doi", norm)
    out.setdefault("fonte", "crossref")
    out.setdefault("data_consulta", _utc_now_iso())
    out.setdefault("evidence_eligible", False)
    return out


def enrich_openalex(doi: str, runner=None) -> dict:
    """R-977.2: enriquece via OpenAlex sem presumir OA (INV-977.2)."""
    norm = _validate_doi_or_raise(normalize_doi(doi))
    if runner is None:
        return {
            "doi": norm,
            "status": "unknown",
            "fonte": "openalex",
            "is_oa": False,
            "licenca": None,
            "best_oa_location": None,
            "data_consulta": _utc_now_iso(),
            "evidence_eligible": False,
        }
    data = runner(norm)
    if not isinstance(data, dict):
        raise ValueError("runner deve retornar dict")
    out = dict(data)
    out.setdefault("doi", norm)
    out.setdefault("fonte", "openalex")
    out.setdefault("data_consulta", _utc_now_iso())
    # Sem prova não presume OA.
    if out.get("status") == "unknown" and out.get("is_oa") not in (False, None):
        out["is_oa"] = False
    if "is_oa" not in out:
        out["is_oa"] = False
    out.setdefault("evidence_eligible", False)
    return out


def check_unpaywall(doi: str, runner=None) -> dict:
    """R-977.3: verifica OA via Unpaywall; sem runner => unavailable."""
    norm = _validate_doi_or_raise(normalize_doi(doi))
    if runner is None:
        return {
            "doi": norm,
            "status": "unavailable",
            "fonte": "unpaywall",
            "licenca": None,
            "oa_status": "unavailable",
            "url_pdf_ou_landing": None,
            "data_consulta": _utc_now_iso(),
            "evidence_eligible": False,
        }
    data = runner(norm)
    if not isinstance(data, dict):
        raise ValueError("runner deve retornar dict")
    out = dict(data)
    out.setdefault("doi", norm)
    out.setdefault("fonte", "unpaywall")
    out.setdefault("data_consulta", _utc_now_iso())
    out.setdefault("evidence_eligible", False)
    return out


def is_download_allowed(info: dict) -> dict:
    """R-977.4 + INV-977.1: só permite com licença observada + URL."""
    if not isinstance(info, dict):
        return {"allowed": False, "reason": "info inválida"}
    lic = info.get("license", info.get("licenca"))
    url = info.get("pdf_url", info.get("url_pdf_ou_landing"))
    lic_s = str(lic or "").strip().lower()
    url_s = str(url or "").strip()
    has_license_hint = any(h in lic_s for h in _ALLOWED_LICENSE_HINTS)
    has_url = url_s.lower().startswith(("http://", "https://"))
    if has_license_hint and has_url:
        return {"allowed": True, "license": lic, "pdf_url": url_s, "evidence_eligible": True}
    return {"allowed": False, "reason": "license_or_url_missing", "evidence_eligible": False}


def handle_closed_access(doi: str) -> dict:
    """R-977.5 + R-977.6: fechado => rota institucional + proveniência."""
    norm = _validate_doi_or_raise(normalize_doi(doi))
    data_consulta = _utc_now_iso()
    payload_base = f"{norm}|closed_access|{data_consulta}|crossref+openalex+unpaywall"
    return {
        "doi": norm,
        "allowed": False,
        "reason": "closed_access",
        "fonte": "crossref+openalex+unpaywall (closed)",
        "licenca": "closed",
        "url_pdf_ou_landing": None,
        "data_consulta": data_consulta,
        "rota_institucional": (
            "Acesso fechado. Utilize assinatura institucional, "
            "empréstimo interbibliotecário ou contato com os autores. "
            "Nenhuma via não autorizada foi tentada."
        ),
        "hash_resposta": _hash_payload(payload_base),
        "evidence_eligible": False,
    }


def _is_blocked_source(url: str) -> bool:
    s = str(url or "").strip().lower()
    if s.startswith("scihub-mcp://"):
        return True
    for b in _BLOCKED_SUBSTRINGS:
        if b in s:
            return True
    try:
        host = (urlparse(s).hostname or "")
        if "sci-hub" in host or "scihub" in host:
            return True
    except Exception:
        pass
    return False


def guarded_fetch(url: str, runner=None):
    """R-977.7 + INV-977.3: bloqueia Sci-Hub antes de qualquer rede."""
    if _is_blocked_source(url):
        raise PermissionError(f"blocked: unauthorized_source {url!r}")
    if runner is None:
        raise RuntimeError("unavailable: runner ausente")
    return runner(url)
