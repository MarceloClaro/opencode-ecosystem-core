# -*- coding: utf-8 -*-
"""
Downloader de Artigos Científicos (SPEC-017)
=============================================
Baixa PDFs de artigos com roteamento em duas camadas:

1. **scihub-cli** (Oxidane-bot) — se instalado (`pip install scihub-cli`),
   usa o roteamento multi-fonte inteligente (OpenAlex, Europe PMC, arXiv,
   Unpaywall, Sci-Hub) com suporte nativo a `--to-md`.
2. **Fallback stdlib** — download direto do `pdf_url` do PaperRecord
   (arXiv PDF, best_oa_location do OpenAlex, Europe PMC fullTextPDF),
   com validação de magic bytes `%PDF-`.

O paper-download-mcp (mesmo autor) expõe a mesma engine via MCP; a
integração MCP é documentada em integrations/opencode_cli.py.
"""

import logging
import re
import shutil
import subprocess
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .searchers import PaperRecord, USER_AGENT

logger = logging.getLogger("research.downloader")


@dataclass
class DownloadResult:
    record: PaperRecord
    ok: bool
    pdf_path: Optional[str] = None
    method: str = ""            # "scihub-cli" | "direct" | "-"
    error: str = ""
    extra: Dict = field(default_factory=dict)


def _slugify(text: str, max_len: int = 70) -> str:
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:max_len].rstrip("-") or "paper"


def _is_pdf(path: Path) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(5) == b"%PDF-"
    except OSError:
        return False


class PaperDownloader:
    """Baixa PDFs para a subpasta `pesquisa/pdfs/` da produção científica."""

    def __init__(self, output_dir: str, email: Optional[str] = None,
                 timeout: int = 30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.email = email
        self.timeout = timeout
        self.scihub_cli = shutil.which("scihub-cli")

    # ------------------------------------------------------------------
    def download(self, records: List[PaperRecord]) -> List[DownloadResult]:
        """Baixa todos os registros; tenta scihub-cli em lote, depois fallback."""
        results: List[DownloadResult] = []
        pending: List[PaperRecord] = []

        # separa o que tem pdf_url direto (rápido) do que precisa de roteamento
        for rec in records:
            if rec.extra.get("type") in ("repository", "dataset"):
                results.append(DownloadResult(
                    rec, ok=False, method="-",
                    error="registro não é artigo (repositório/dataset)"))
            else:
                pending.append(rec)

        direct_fail: List[PaperRecord] = []
        for rec in pending:
            res = self._download_direct(rec)
            if res.ok:
                results.append(res)
            else:
                direct_fail.append(rec)

        # roteamento multi-fonte via scihub-cli para os que falharam
        if direct_fail and self.scihub_cli:
            results.extend(self._download_via_scihub_cli(direct_fail))
        else:
            for rec in direct_fail:
                results.append(DownloadResult(
                    rec, ok=False, method="-",
                    error="sem pdf_url OA e scihub-cli não instalado "
                          "(instale com: pip install scihub-cli)"))
        return results

    # ------------------------------------------------------------------
    def _download_direct(self, rec: PaperRecord) -> DownloadResult:
        """Download direto do pdf_url (arXiv / OA) com validação %PDF-."""
        if not rec.pdf_url:
            return DownloadResult(rec, ok=False, error="sem pdf_url")
        fname = f"[{rec.year or 's.d.'}] - {_slugify(rec.title)}.pdf"
        dest = self.output_dir / fname
        try:
            req = urllib.request.Request(
                rec.pdf_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = resp.read()
            if not data.startswith(b"%PDF-"):
                return DownloadResult(
                    rec, ok=False, method="direct",
                    error="resposta não é PDF (provável página HTML/paywall)")
            dest.write_bytes(data)
            logger.info(f"[direct] baixado: {dest.name} ({len(data)//1024} KiB)")
            return DownloadResult(rec, ok=True, pdf_path=str(dest), method="direct")
        except Exception as exc:
            return DownloadResult(rec, ok=False, method="direct", error=str(exc))

    # ------------------------------------------------------------------
    def _download_via_scihub_cli(
            self, records: List[PaperRecord]) -> List[DownloadResult]:
        """Roteamento multi-fonte em lote via scihub-cli (Oxidane-bot)."""
        ids = [r.identifier() for r in records if r.identifier()]
        results: List[DownloadResult] = []
        no_id = [r for r in records if not r.identifier()]
        for rec in no_id:
            results.append(DownloadResult(rec, ok=False, method="-",
                                          error="sem identificador (DOI/arXiv/URL)"))
        if not ids:
            return results

        input_file = self.output_dir / "_scihub_input.txt"
        input_file.write_text("\n".join(str(i) for i in ids), encoding="utf-8")
        cmd = [self.scihub_cli, str(input_file), "-o", str(self.output_dir)]
        if self.email:
            cmd += ["--email", self.email]
        try:
            before = {p.name for p in self.output_dir.glob("*.pdf")}
            subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            after = {p for p in self.output_dir.glob("*.pdf")
                     if p.name not in before and _is_pdf(p)}
        except Exception as exc:
            logger.warning(f"[scihub-cli] execução falhou: {exc}")
            after = set()
        finally:
            input_file.unlink(missing_ok=True)

        # associa os novos PDFs aos registros por heurística de título/ano
        remaining = list(after)
        for rec in records:
            if not rec.identifier():
                continue
            match = None
            key_words = set(_slugify(rec.title).split("-")[:5])
            for p in remaining:
                pdf_words = set(_slugify(p.stem).split("-"))
                if key_words and len(key_words & pdf_words) >= min(3, len(key_words)):
                    match = p
                    break
            if match:
                remaining.remove(match)
                results.append(DownloadResult(
                    rec, ok=True, pdf_path=str(match), method="scihub-cli"))
            else:
                results.append(DownloadResult(
                    rec, ok=False, method="scihub-cli",
                    error="download não obtido pelas fontes disponíveis"))
        # PDFs excedentes não associados ainda contam como sucesso genérico
        for p in remaining:
            results.append(DownloadResult(
                PaperRecord(title=p.stem, source="scihub-cli"),
                ok=True, pdf_path=str(p), method="scihub-cli"))
        return results
