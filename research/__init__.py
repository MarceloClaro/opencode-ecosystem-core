# -*- coding: utf-8 -*-
"""
research — Subsistema de Busca e Extração Acadêmica (SPEC-017)
===============================================================
Buscadores multiplataforma (arXiv, OpenAlex, Crossref, Semantic Scholar,
Europe PMC/PubMed, GitHub, Kaggle), download de PDFs (scihub-cli /
paper-download-mcp / OA direto), conversão PDF→Markdown e fichamentos +
resenhas críticas em ABNT (NBR 6023:2018 / NBR 10520:2023) e APA 7.
"""

from .searchers import MultiSearcher, PaperRecord
from .downloader import PaperDownloader, DownloadResult
from .pdf2md import Pdf2Markdown
from .fichamento import (CitationFormatter, CriticalAnalyzer,
                         CriticalAnalysis, FichamentoWriter)
from .hub import ResearchHub

__all__ = [
    "MultiSearcher", "PaperRecord",
    "PaperDownloader", "DownloadResult",
    "Pdf2Markdown",
    "CitationFormatter", "CriticalAnalyzer", "CriticalAnalysis",
    "FichamentoWriter",
    "ResearchHub",
]
