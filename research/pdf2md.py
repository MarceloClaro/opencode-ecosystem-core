# -*- coding: utf-8 -*-
"""
Conversor PDF → Markdown (SPEC-017)
====================================
Converte os PDFs baixados em Markdown legível, salvo na subpasta
`pesquisa/md/` da pasta única de produção científica.

Backends, em ordem de preferência (mesma estratégia do scihub-cli --to-md):
1. **pymupdf4llm**  — extração otimizada para LLMs (se instalado)
2. **pdftotext**    — poppler-utils, com `-layout` (pré-instalado em Linux)
3. **pypdf**        — fallback puro-Python

Cada Markdown gerado recebe frontmatter YAML com os metadados do artigo
para facilitar leitura, fichamento e rastreabilidade.
"""

import logging
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .searchers import PaperRecord

logger = logging.getLogger("research.pdf2md")


class Pdf2Markdown:
    """Converte PDF em Markdown com cadeia de fallbacks."""

    def __init__(self, md_dir: str):
        self.md_dir = Path(md_dir)
        self.md_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def convert(self, pdf_path: str,
                record: Optional[PaperRecord] = None) -> Optional[str]:
        """Converte um PDF; retorna o caminho do .md ou None se falhar."""
        pdf = Path(pdf_path)
        if not pdf.exists():
            logger.warning(f"PDF inexistente: {pdf}")
            return None
        dest = self.md_dir / (pdf.stem + ".md")

        text = (self._via_pymupdf4llm(pdf)
                or self._via_pdftotext(pdf)
                or self._via_pypdf(pdf))
        if not text or not text.strip():
            logger.warning(f"nenhum backend extraiu texto de {pdf.name}")
            return None

        text = self._cleanup(text)
        frontmatter = self._frontmatter(pdf, record)
        dest.write_text(frontmatter + text, encoding="utf-8")
        logger.info(f"convertido: {dest.name} ({len(text)//1024} KiB de texto)")
        return str(dest)

    # ------------------------------------------------------------------
    def _via_pymupdf4llm(self, pdf: Path) -> Optional[str]:
        try:
            import pymupdf4llm  # type: ignore
            return pymupdf4llm.to_markdown(str(pdf))
        except ImportError:
            return None
        except Exception as exc:
            logger.debug(f"pymupdf4llm falhou: {exc}")
            return None

    def _via_pdftotext(self, pdf: Path) -> Optional[str]:
        if not shutil.which("pdftotext"):
            return None
        try:
            out = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
                capture_output=True, text=True, timeout=120)
            return out.stdout if out.returncode == 0 else None
        except Exception as exc:
            logger.debug(f"pdftotext falhou: {exc}")
            return None

    def _via_pypdf(self, pdf: Path) -> Optional[str]:
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError:
            try:
                from PyPDF2 import PdfReader  # type: ignore
            except ImportError:
                return None
        try:
            reader = PdfReader(str(pdf))
            return "\n\n".join((page.extract_text() or "")
                               for page in reader.pages)
        except Exception as exc:
            logger.debug(f"pypdf falhou: {exc}")
            return None

    # ------------------------------------------------------------------
    @staticmethod
    def _cleanup(text: str) -> str:
        """Limpeza leve: normaliza quebras e remove hifenização de fim de linha."""
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)          # de-hifenização
        text = re.sub(r"[ \t]+\n", "\n", text)                # trailing spaces
        text = re.sub(r"\n{4,}", "\n\n\n", text)              # excesso de \n
        return text.strip() + "\n"

    @staticmethod
    def _frontmatter(pdf: Path, record: Optional[PaperRecord]) -> str:
        lines = ["---"]
        if record:
            lines.append(f'title: "{record.title.replace(chr(34), chr(39))}"')
            if record.authors:
                lines.append("authors:")
                lines.extend(f'  - "{a}"' for a in record.authors[:20])
            if record.year:
                lines.append(f"year: {record.year}")
            if record.doi:
                lines.append(f"doi: {record.doi}")
            if record.venue:
                lines.append(f'venue: "{record.venue}"')
            lines.append(f"source: {record.source or 'desconhecida'}")
        lines.append(f"pdf: {pdf.name}")
        lines.append("converted_by: opencode-ecosystem-core/research")
        lines.append("---\n\n")
        return "\n".join(lines)
