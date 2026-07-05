# -*- coding: utf-8 -*-
"""
ResearchHub — Pipeline unificado de pesquisa acadêmica (SPEC-017)
==================================================================
Orquestra o fluxo completo em uma **pasta única de produção científica**:

    producao_cientifica/<tema>-<timestamp>/
    └── pesquisa/
        ├── pdfs/               # PDFs baixados (scihub-cli / direct OA)
        ├── md/                 # PDFs convertidos em Markdown legível
        ├── fichamentos/        # Fichamentos ABNT (bibliográfico+citação+crítico)
        ├── resenhas/           # Resenhas críticas vinculadas ao tema
        ├── referencias_abnt.md # Referências ABNT NBR 6023:2018 (alfabética)
        ├── referencias_apa.md  # Referências APA 7ª edição
        ├── referencias.bib     # BibTeX para os templates LaTeX
        ├── repositorios.md     # Repositórios GitHub e datasets Kaggle
        └── RESEARCH_MANIFEST.json

Fluxo: buscar (multiplataforma) → ranquear por aderência ao tema →
baixar PDFs → converter PDF→MD → fichar → resenhar → consolidar referências.
"""

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

from .searchers import MultiSearcher, PaperRecord
from .downloader import PaperDownloader
from .pdf2md import Pdf2Markdown
from .fichamento import CitationFormatter, CriticalAnalyzer, FichamentoWriter
from .osint import OsintLinkTree
from .figure_hunter import FigureHunter

logger = logging.getLogger("research.hub")


def _slug(text: str, max_len: int = 50) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[-\s]+", "-", s)
    return s[:max_len].rstrip("-") or "pesquisa"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class ResearchHub:
    """Fachada do subsistema de busca e extração acadêmica."""

    def __init__(self, topic: str,
                 production_folder: Optional[str] = None,
                 output_root: str = "producao_cientifica",
                 platforms: Optional[List[str]] = None,
                 email: Optional[str] = None):
        self.topic = topic
        if production_folder:
            self.folder = Path(production_folder)
        else:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            self.folder = Path(output_root) / f"{_slug(topic)}-{stamp}"
        self.pesquisa = self.folder / "pesquisa"
        self.pdf_dir = self.pesquisa / "pdfs"
        self.md_dir = self.pesquisa / "md"
        self.fich_dir = self.pesquisa / "fichamentos"
        self.res_dir = self.pesquisa / "resenhas"
        for d in (self.pdf_dir, self.md_dir, self.fich_dir, self.res_dir):
            d.mkdir(parents=True, exist_ok=True)

        self.searcher = MultiSearcher(platforms=platforms)
        self.downloader = PaperDownloader(str(self.pdf_dir), email=email)
        self.converter = Pdf2Markdown(str(self.md_dir))
        self.writer = FichamentoWriter(str(self.fich_dir), str(self.res_dir), topic)
        self.analyzer = CriticalAnalyzer(topic)
        self.osint = OsintLinkTree(max_depth=1)

    # ------------------------------------------------------------------
    def run(self, max_papers: int = 8, limit_per_platform: int = 4,
            download: bool = True, use_llm: bool = False,
            llm_provider: str = "auto",
            llm_model: Optional[str] = None) -> Dict:
        """Executa o pipeline completo; retorna o manifest da pesquisa.

        Com ``use_llm=True``, fichamentos e resenhas são enriquecidos por
        LLM com prioridade para **modelos locais via Ollama** (privacidade
        e custo zero); ``llm_provider`` aceita ``auto``/``ollama``/``openai``
        e ``llm_model`` permite escolher o modelo (ex.: ``llama3.2``).
        """
        logger.info(f"[hub] tema: {self.topic!r} → {self.folder}")

        self._llm_enriched = 0
        self._llm_meta = None
        if use_llm:
            try:
                from .llm_client import LLMClient
                self._llm_meta = LLMClient(provider=llm_provider,
                                           model=llm_model).describe()
            except Exception:  # metadados são opcionais
                self._llm_meta = None

        # 1. Busca multiplataforma
        all_records = self.searcher.search(
            self.topic, limit_per_platform=limit_per_platform)
        papers = [r for r in all_records
                  if r.extra.get("type") not in ("repository", "dataset")]
        repos = [r for r in all_records
                 if r.extra.get("type") in ("repository", "dataset")]

        # 2. Ranqueamento por aderência ao tema
        papers.sort(key=lambda r: self.analyzer.analyze(r).aderencia_score,
                    reverse=True)
        papers = papers[:max_papers]
        logger.info(f"[hub] {len(papers)} artigos selecionados, "
                    f"{len(repos)} repositórios/datasets")

        # 3. Download dos PDFs
        pdf_by_key: Dict[str, str] = {}
        download_report = []
        if download and papers:
            for res in self.downloader.download(papers):
                key = res.record.title
                download_report.append({
                    "title": key, "ok": res.ok, "method": res.method,
                    "pdf": res.pdf_path, "error": res.error})
                if res.ok and res.pdf_path:
                    pdf_by_key[key] = res.pdf_path

        # 4. Conversão PDF → Markdown
        md_by_key: Dict[str, str] = {}
        for rec in papers:
            pdf = pdf_by_key.get(rec.title)
            if pdf:
                md = self.converter.convert(pdf, rec)
                if md:
                    md_by_key[rec.title] = md

        # 5. Fichamento + resenha crítica de CADA artigo
        fichamentos, resenhas = [], []
        for rec in papers:
            md_path = md_by_key.get(rec.title, "")
            fulltext = ""
            if md_path:
                try:
                    fulltext = Path(md_path).read_text(encoding="utf-8")
                except OSError:
                    pass
            fichamentos.append(self.writer.fichamento(rec, fulltext, md_path))
            resenha_path = self.writer.resenha(rec, fulltext)
            resenhas.append(resenha_path)
            if use_llm:
                enriched = self.writer.enrich_with_llm(
                    rec, fulltext, resenha_path,
                    provider=llm_provider, model=llm_model)
                self._llm_enriched += 1 if enriched else 0

        # 6. Referências consolidadas + repositórios
        self._write_references(papers)
        self._write_repos(repos)

        # 7. Extração de figuras reais dos PDFs (com fonte ABNT/APA)
        figures_report = self._hunt_figures(papers, pdf_by_key)

        # 7b. OSINT LinkTree: Analisar a "Dark Web" acadêmica das referências
        refs_text = "\n".join(p.url for p in papers if p.url)
        osint_report = self.osint.analyze_references(refs_text)
        with open(self.pesquisa / "OSINT_REPORT.json", "w", encoding="utf-8") as f:
            json.dump(osint_report, f, ensure_ascii=False, indent=2)

        # 8. Manifest com checksums
        manifest = self._write_manifest(papers, repos, download_report,
                                        pdf_by_key, md_by_key,
                                        fichamentos, resenhas,
                                        figures_report)
        logger.info(f"[hub] pipeline concluído: {manifest['resumo']}")
        return manifest

    # ------------------------------------------------------------------
    def _hunt_figures(self, papers: List[PaperRecord],
                      pdf_by_key: Dict[str, str]) -> Dict:
        """Extrai figuras reais dos PDFs baixados, com fonte ABNT/APA."""
        hunter = FigureHunter(str(self.pesquisa / "imagens"))
        total = 0
        for rec in papers:
            pdf = pdf_by_key.get(rec.title)
            if not pdf:
                continue
            meta = {
                "authors": "; ".join(rec.authors) if rec.authors else "",
                "year": rec.year or "",
                "title": rec.title,
                "doi": rec.doi or "",
            }
            figs = hunter.extract_from_pdf(pdf, meta)
            total += len(figs)
        catalog = hunter.write_catalog()
        logger.info(f"[hub] {total} figuras reais extraídas → {catalog}")
        return {"figuras_extraidas": total, "catalogo": catalog or ""}

    # ------------------------------------------------------------------
    def _write_references(self, papers: List[PaperRecord]) -> None:
        cit = CitationFormatter
        ordered = sorted(papers, key=lambda r: cit.abnt(r).lower())

        abnt_lines = [
            "# Referências — ABNT NBR 6023:2018",
            "", f"**Tema:** {self.topic}", "",
            "_Em ordem alfabética, conforme exigido pela norma._", "",
        ]
        abnt_lines += [f"{cit.abnt(r)}\n" for r in ordered]
        (self.pesquisa / "referencias_abnt.md").write_text(
            "\n".join(abnt_lines), encoding="utf-8")

        apa_lines = [
            "# References — APA 7th edition",
            "", f"**Topic:** {self.topic}", "",
        ]
        apa_lines += [f"{cit.apa(r)}\n" for r in ordered]
        (self.pesquisa / "referencias_apa.md").write_text(
            "\n".join(apa_lines), encoding="utf-8")

        bib_entries = []
        seen_keys = set()
        for r in ordered:
            first = (r.authors[0].split(",")[0].split()[-1].lower()
                     if r.authors else "anon")
            key = re.sub(r"\W", "", f"{first}{r.year or 'nd'}")
            while key in seen_keys:
                key += "x"
            seen_keys.add(key)
            bib_entries.append(cit.bibtex(r, key))
        (self.pesquisa / "referencias.bib").write_text(
            "\n\n".join(bib_entries) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------
    def _write_repos(self, repos: List[PaperRecord]) -> None:
        if not repos:
            return
        lines = [
            "# Repositórios de código e datasets",
            "", f"**Tema:** {self.topic}", "",
            "| Nome | Plataforma | Descrição | URL |",
            "| --- | --- | --- | --- |",
        ]
        for r in repos:
            desc = (r.abstract or "").replace("|", "/")[:120]
            lines.append(f"| {r.title} | {r.source} | {desc} | {r.url} |")
        (self.pesquisa / "repositorios.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------
    def _write_manifest(self, papers, repos, download_report,
                        pdf_by_key, md_by_key, fichamentos, resenhas,
                        figures_report: Optional[Dict] = None) -> Dict:
        files = {}
        for p in sorted(self.pesquisa.rglob("*")):
            if p.is_file() and p.name != "RESEARCH_MANIFEST.json":
                files[str(p.relative_to(self.folder))] = _sha256(p)
        manifest = {
            "topic": self.topic,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "platforms": [type(s).__name__ for s in self.searcher.searchers],
            "resumo": {
                "artigos_selecionados": len(papers),
                "pdfs_baixados": len(pdf_by_key),
                "convertidos_md": len(md_by_key),
                "fichamentos": len(fichamentos),
                "resenhas": len(resenhas),
                "repositorios_datasets": len(repos),
                "figuras_extraidas": (figures_report or {}).get("figuras_extraidas", 0),
            },
            "downloads": download_report,
            "normas": ["ABNT NBR 6023:2018", "ABNT NBR 10520:2023", "APA 7"],
            "llm": {
                "enabled": getattr(self, "_llm_meta", None) is not None,
                "provider": getattr(self, "_llm_meta", None),
                "resenhas_enriquecidas": getattr(self, "_llm_enriched", 0),
            },
            "files_sha256": files,
        }
        (self.pesquisa / "RESEARCH_MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8")
        return manifest
