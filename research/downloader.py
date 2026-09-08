# -*- coding: utf-8 -*-
"""
Downloader Open Science de Artigos Científicos (SPEC-017 v2)
============================================================
Baixa PDFs apenas por rotas explicitamente abertas/auditáveis.

Ordem operacional:
1. ``pdf_url`` já classificado por uma fonte OA conhecida (arXiv, OpenAlex,
   Semantic Scholar openAccessPdf, Europe PMC, SciELO, bioRxiv/medRxiv etc.);
2. resolução por DOI no OpenAlex;
3. resolução por DOI no Unpaywall quando um e-mail foi configurado;
4. resolução por DOI no Europe PMC para literatura biomédica.

A Crossref permanece autoridade de DOI/metadados, não repositório universal de
PDF. Uma URL de publisher não é considerada aberta apenas por responder HTTP
200. Todo arquivo é validado por magic bytes ``%PDF-``, limite de tamanho e
SHA-256 antes de ser registrado como obtido.

Este módulo usa somente a stdlib e não chama executores externos para contornar
paywalls. Ausência de uma cópia aberta resulta em falha explícita e auditável.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .searchers import PaperRecord, USER_AGENT

logger = logging.getLogger("research.downloader")

MAX_PDF_BYTES = 100 * 1024 * 1024
DIRECT_OA_SOURCES = {
    "arxiv",
    "openalex",
    "semantic_scholar",
    "europepmc",
    "scielo",
    "biorxiv",
    "medrxiv",
    "doaj",
    "core",
}


@dataclass
class DownloadResult:
    record: PaperRecord
    ok: bool
    pdf_path: Optional[str] = None
    method: str = ""  # direct_oa | openalex_oa | unpaywall_oa | europepmc_oa | -
    error: str = ""
    extra: Dict = field(default_factory=dict)


def _slugify(text: str, max_len: int = 70) -> str:
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:max_len].rstrip("-") or "paper"


def _normalise_doi(doi: Optional[str]) -> Optional[str]:
    if not doi:
        return None
    value = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.lower().startswith(prefix):
            value = value[len(prefix):]
            break
    return value.strip() or None


def _safe_http_url(url: Optional[str]) -> bool:
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _public_source_url(url: str) -> str:
    """Remove query/fragment antes de persistir provenance.

    Alguns repositórios fornecem URLs assinadas de curta duração. O hash da URL
    completa preserva correlação operacional sem gravar parâmetros que podem
    conter tokens temporários.
    """
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


class PaperDownloader:
    """Baixa PDFs abertos para ``pesquisa/pdfs/`` com receipts mínimos."""

    def __init__(self, output_dir: str, email: Optional[str] = None,
                 timeout: int = 30, max_pdf_bytes: int = MAX_PDF_BYTES):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.email = (email or "").strip() or None
        self.timeout = timeout
        self.max_pdf_bytes = max_pdf_bytes

    def download(self, records: List[PaperRecord]) -> List[DownloadResult]:
        results: List[DownloadResult] = []
        for rec in records:
            if rec.extra.get("type") in ("repository", "dataset"):
                results.append(DownloadResult(
                    rec,
                    ok=False,
                    method="-",
                    error="registro não é artigo (repositório/dataset)",
                ))
                continue
            results.append(self._download_one(rec))
        return results

    def _download_one(self, rec: PaperRecord) -> DownloadResult:
        """Tenta as rotas em ordem e interrompe no primeiro PDF válido.

        O iterador é deliberadamente lazy: se uma URL OA direta funciona, não
        consulta OpenAlex; se OpenAlex funciona, não consulta Unpaywall/Europe
        PMC. Isso reduz tráfego, latência e exposição desnecessária de DOI.
        """
        errors: List[str] = []
        seen = set()
        for method, url, metadata in self._candidate_urls(rec):
            if not _safe_http_url(url) or url in seen:
                continue
            seen.add(url)
            result = self._download_pdf(rec, method, url, metadata)
            if result.ok:
                return result
            errors.append(f"{method}: {result.error}")

        return DownloadResult(
            rec,
            ok=False,
            method="-",
            error=(
                "; ".join(errors)
                if errors
                else "nenhuma rota open-access/repositório/preprint localizada"
            ),
            extra={"doi": _normalise_doi(rec.doi), "attempted_routes": len(seen)},
        )

    def _candidate_urls(self, rec: PaperRecord) -> Iterable[Tuple[str, str, Dict]]:
        source = (rec.source or "").strip().lower()
        explicitly_oa = bool(
            rec.extra.get("open_access")
            or rec.extra.get("is_oa")
            or rec.extra.get("access_basis") in {
                "open_access", "repository", "preprint", "public_domain"
            }
        )

        # URL direta apenas quando a origem/registro já a classifica como aberta.
        if rec.pdf_url and (source in DIRECT_OA_SOURCES or explicitly_oa):
            yield "direct_oa", rec.pdf_url, {
                "resolver": source or "record",
                "access_basis": rec.extra.get("access_basis") or "open_access",
            }

        doi = _normalise_doi(rec.doi)
        if not doi:
            return

        openalex = self._resolve_openalex_oa(doi)
        if openalex:
            yield "openalex_oa", openalex[0], openalex[1]

        if self.email:
            unpaywall = self._resolve_unpaywall_oa(doi)
            if unpaywall:
                yield "unpaywall_oa", unpaywall[0], unpaywall[1]

        epmc = self._resolve_europepmc_oa(doi)
        if epmc:
            yield "europepmc_oa", epmc[0], epmc[1]

    def _json_get(self, url: str) -> Dict:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            raw = resp.read(5 * 1024 * 1024 + 1)
        if len(raw) > 5 * 1024 * 1024:
            raise ValueError("resposta de metadados excedeu 5 MiB")
        return json.loads(raw.decode("utf-8", errors="replace"))

    def _resolve_openalex_oa(self, doi: str) -> Optional[Tuple[str, Dict]]:
        identifier = urllib.parse.quote(f"https://doi.org/{doi}", safe=":/")
        url = f"https://api.openalex.org/works/{identifier}"
        if self.email:
            separator = "&" if "?" in url else "?"
            url += separator + urllib.parse.urlencode({"mailto": self.email})
        try:
            data = self._json_get(url)
            location = data.get("best_oa_location") or {}
            pdf_url = location.get("pdf_url")
            if not _safe_http_url(pdf_url):
                return None
            return pdf_url, {
                "resolver": "openalex",
                "access_basis": "open_access",
                "license": location.get("license"),
                "version": location.get("version"),
                "landing_page_url": location.get("landing_page_url"),
            }
        except Exception as exc:
            logger.debug("[openalex] DOI %s não resolvido: %s", doi, exc)
            return None

    def _resolve_unpaywall_oa(self, doi: str) -> Optional[Tuple[str, Dict]]:
        if not self.email:
            return None
        url = (
            "https://api.unpaywall.org/v2/"
            + urllib.parse.quote(doi, safe="")
            + "?"
            + urllib.parse.urlencode({"email": self.email})
        )
        try:
            data = self._json_get(url)
            location = data.get("best_oa_location") or {}
            pdf_url = location.get("url_for_pdf")
            if not _safe_http_url(pdf_url):
                return None
            return pdf_url, {
                "resolver": "unpaywall",
                "access_basis": "open_access",
                "license": location.get("license"),
                "version": location.get("version"),
                "host_type": location.get("host_type"),
                "landing_page_url": location.get("url_for_landing_page"),
            }
        except Exception as exc:
            logger.debug("[unpaywall] DOI %s não resolvido: %s", doi, exc)
            return None

    def _resolve_europepmc_oa(self, doi: str) -> Optional[Tuple[str, Dict]]:
        query = f'DOI:"{doi}"'
        url = (
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
            + urllib.parse.urlencode({"query": query, "format": "json", "pageSize": 3})
        )
        try:
            data = self._json_get(url)
            for item in data.get("resultList", {}).get("result", []):
                pmcid = item.get("pmcid")
                if not pmcid:
                    continue
                return (
                    f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextPDF",
                    {
                        "resolver": "europepmc",
                        "access_basis": "repository",
                        "pmcid": pmcid,
                    },
                )
        except Exception as exc:
            logger.debug("[europepmc] DOI %s não resolvido: %s", doi, exc)
        return None

    def _write_receipt(self, rec: PaperRecord, dest: Path, method: str,
                       url: str, metadata: Dict, digest: str, total: int) -> Path:
        receipt_path = dest.with_suffix(".receipt.json")
        receipt = {
            "schema": "open-science-download-receipt-v1",
            "title": rec.title,
            "doi": _normalise_doi(rec.doi),
            "source": rec.source,
            "method": method,
            "resolver": metadata.get("resolver"),
            "access_basis": metadata.get("access_basis"),
            "license": metadata.get("license"),
            "version": metadata.get("version"),
            "pdf_path": dest.name,
            "bytes": total,
            "sha256": digest,
            "validated_pdf_magic": True,
            "source_url": _public_source_url(url),
            "source_url_sha256": hashlib.sha256(url.encode("utf-8")).hexdigest(),
        }
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return receipt_path

    def _download_pdf(self, rec: PaperRecord, method: str, url: str,
                      metadata: Dict) -> DownloadResult:
        fname = f"[{rec.year or 's.d.'}] - {_slugify(rec.title)}.pdf"
        dest = self.output_dir / fname
        tmp = dest.with_suffix(dest.suffix + ".part")
        sha = hashlib.sha256()
        total = 0

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1",
                },
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                content_length = resp.headers.get("Content-Length")
                if content_length and int(content_length) > self.max_pdf_bytes:
                    raise ValueError("PDF excede o limite configurado")

                first = resp.read(5)
                if first != b"%PDF-":
                    raise ValueError("resposta não é PDF (magic bytes ausentes)")

                with open(tmp, "wb") as fh:
                    fh.write(first)
                    sha.update(first)
                    total = len(first)
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > self.max_pdf_bytes:
                            raise ValueError("PDF excede o limite configurado")
                        fh.write(chunk)
                        sha.update(chunk)

            digest = sha.hexdigest()
            tmp.replace(dest)
            receipt_path = self._write_receipt(
                rec, dest, method, url, metadata or {}, digest, total
            )
            extra = dict(metadata or {})
            extra.update({
                "sha256": digest,
                "bytes": total,
                "source_url": _public_source_url(url),
                "source_url_sha256": hashlib.sha256(url.encode("utf-8")).hexdigest(),
                "validated_pdf_magic": True,
                "receipt": str(receipt_path),
            })
            logger.info("[%s] baixado: %s (%d KiB)", method, dest.name, total // 1024)
            return DownloadResult(
                rec,
                ok=True,
                pdf_path=str(dest),
                method=method,
                extra=extra,
            )
        except Exception as exc:
            tmp.unlink(missing_ok=True)
            return DownloadResult(
                rec,
                ok=False,
                method=method,
                error=str(exc),
                extra={
                    "source_url": _public_source_url(url),
                    "source_url_sha256": hashlib.sha256(url.encode("utf-8")).hexdigest(),
                    **(metadata or {}),
                },
            )
