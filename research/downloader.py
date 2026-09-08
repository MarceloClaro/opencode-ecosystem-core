# -*- coding: utf-8 -*-
"""Downloader de Artigos Científicos — Open Science Only (SPEC-017 v2 / R469).

Política operacional:
1. aceita link direto somente quando o registro veio de fonte classificada como OA;
2. para registros sem PDF, resolve cópia aberta por DOI via OpenAlex, Unpaywall
   (quando e-mail configurado) e Europe PMC;
3. arXiv/preprints e repositórios OA são permitidos;
4. nunca contorna paywall, login, CAPTCHA ou controle de acesso;
5. valida magic bytes ``%PDF-`` e registra SHA-256/provenance no resultado.

Crossref/PubMed permanecem excelentes fontes de metadados, mas uma URL de
publisher/DOI por si só não autoriza download automático.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .searchers import PaperRecord, USER_AGENT

logger = logging.getLogger("research.downloader")
OA_DIRECT_SOURCES = {"arxiv", "openalex", "europepmc", "semantic_scholar", "core"}
MAX_BYTES = 100 * 1024 * 1024


@dataclass
class DownloadResult:
    record: PaperRecord
    ok: bool
    pdf_path: Optional[str] = None
    method: str = ""
    error: str = ""
    extra: Dict = field(default_factory=dict)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _slugify(text: str, max_len: int = 70) -> str:
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:max_len].rstrip("-") or "paper"


def _norm_doi(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value.strip(), flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I).strip().lower()
    return value if value.startswith("10.") and "/" in value else None


def _fetch_json(url: str, timeout: int) -> Dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _download_bytes(url: str, timeout: int) -> Tuple[bytes, str, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read(MAX_BYTES + 1)
        ctype = resp.headers.get("Content-Type", "")
        final_url = resp.geturl()
    if len(data) > MAX_BYTES:
        raise ValueError("arquivo excede limite de 100 MiB")
    return data, ctype, final_url


class PaperDownloader:
    """Baixa somente cópias abertas verificáveis para ``output_dir``."""

    def __init__(self, output_dir: str, email: Optional[str] = None, timeout: int = 30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.email = email or os.environ.get("UNPAYWALL_EMAIL") or os.environ.get("CROSSREF_MAILTO")
        self.timeout = timeout

    def download(self, records: List[PaperRecord]) -> List[DownloadResult]:
        results: List[DownloadResult] = []
        for rec in records:
            if rec.extra.get("type") in ("repository", "dataset"):
                results.append(DownloadResult(rec, ok=False, method="-", error="registro não é artigo"))
                continue
            try:
                url, method, rights_basis, license_name = self._resolve_open_copy(rec)
            except Exception as exc:
                results.append(DownloadResult(
                    rec, ok=False, method="resolver", error=f"falha ao resolver cópia aberta: {exc}",
                    extra={"rights_basis": "not_verified_open", "limitations": ["Resolver OA falhou; nenhum acesso alternativo foi tentado."]},
                ))
                continue
            if not url:
                results.append(DownloadResult(
                    rec, ok=False, method="-", error="nenhuma cópia aberta verificada encontrada",
                    extra={"rights_basis": "not_verified_open", "limitations": ["Ausência de PDF OA não implica ausência do artigo."]},
                ))
                continue
            results.append(self._download_resolved(rec, url, method, rights_basis, license_name))
        return results

    def _resolve_open_copy(self, rec: PaperRecord) -> Tuple[Optional[str], Optional[str], str, Optional[str]]:
        source = (rec.source or "").lower()
        if rec.pdf_url and (source in OA_DIRECT_SOURCES or rec.extra.get("open_access") is True):
            basis = "preprint" if source == "arxiv" else "open_access"
            return rec.pdf_url, f"{source or 'direct'}_oa", basis, rec.extra.get("license")

        doi = _norm_doi(rec.doi)
        if doi:
            oa = self._resolve_openalex(doi)
            if oa and oa.get("pdf_url"):
                return oa["pdf_url"], "openalex_oa", "open_access", oa.get("license")
            if self.email:
                up = self._resolve_unpaywall(doi)
                if up and up.get("pdf_url"):
                    basis = "repository" if up.get("host_type") == "repository" else "open_access"
                    return up["pdf_url"], "unpaywall_oa", basis, up.get("license")
            epmc = self._resolve_europepmc(doi)
            if epmc:
                return epmc, "europepmc_oa", "repository", None

        if rec.arxiv_id:
            return f"https://arxiv.org/pdf/{rec.arxiv_id}", "arxiv_preprint", "preprint", None
        return None, None, "not_verified_open", None

    def _resolve_openalex(self, doi: str) -> Optional[Dict]:
        external = "https://doi.org/" + doi
        url = "https://api.openalex.org/works/" + urllib.parse.quote(external, safe=":/")
        data = _fetch_json(url, self.timeout)
        oa = data.get("open_access") or {}
        best = data.get("best_oa_location") or {}
        if not oa.get("is_oa") or not best.get("pdf_url"):
            return None
        return {"pdf_url": best.get("pdf_url"), "license": best.get("license"), "version": best.get("version")}

    def _resolve_unpaywall(self, doi: str) -> Optional[Dict]:
        params = urllib.parse.urlencode({"email": self.email})
        url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='')}?{params}"
        data = _fetch_json(url, self.timeout)
        loc = data.get("best_oa_location") or {}
        return {
            "pdf_url": loc.get("url_for_pdf"), "license": loc.get("license"),
            "host_type": loc.get("host_type"), "oa_status": data.get("oa_status"),
        }

    def _resolve_europepmc(self, doi: str) -> Optional[str]:
        params = urllib.parse.urlencode({"query": f'DOI:"{doi}"', "format": "json", "pageSize": 3})
        data = _fetch_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + params, self.timeout)
        for row in data.get("resultList", {}).get("result", []):
            if str(row.get("isOpenAccess", "")).upper() == "Y" and row.get("pmcid"):
                return f"https://www.ebi.ac.uk/europepmc/webservices/rest/{row['pmcid']}/fullTextPDF"
        return None

    def _download_resolved(self, rec: PaperRecord, url: str, method: str,
                           rights_basis: str, license_name: Optional[str]) -> DownloadResult:
        fname = f"[{rec.year or 's.d.'}] - {_slugify(rec.title)}.pdf"
        dest = self.output_dir / fname
        try:
            data, ctype, final_url = _download_bytes(url, self.timeout)
            if not data.startswith(b"%PDF-"):
                return DownloadResult(
                    rec, ok=False, method=method,
                    error="resposta não é PDF (HTML, landing page ou controle de acesso)",
                    extra={"resolved_pdf_url": final_url, "rights_basis": rights_basis,
                           "license": license_name, "content_type": ctype,
                           "validation": ["magic_bytes_failed"],
                           "limitations": ["Conteúdo rejeitado; nada foi persistido."]},
                )
            dest.write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            return DownloadResult(
                rec, ok=True, pdf_path=str(dest), method=method,
                extra={"resolved_pdf_url": final_url, "rights_basis": rights_basis,
                       "license": license_name, "downloaded_at": _now(), "sha256": digest,
                       "bytes": len(data), "content_type": ctype,
                       "validation": ["magic_bytes_%PDF-", "sha256_recorded"],
                       "limitations": []},
            )
        except Exception as exc:
            logger.warning("[%s] download falhou: %s", method, exc)
            return DownloadResult(
                rec, ok=False, method=method, error=str(exc),
                extra={"resolved_pdf_url": url, "rights_basis": rights_basis,
                       "license": license_name, "validation": [],
                       "limitations": ["Falha de rede/servidor; nenhum fallback não autorizado foi usado."]},
            )
