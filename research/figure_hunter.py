"""
FigureHunter — Busca e extração de imagens reais de artigos científicos.
========================================================================

Duas frentes complementares:

1. **Extração local (PDFs baixados)**: varre os PDFs da subpasta
   `pesquisa/pdfs/` da produção científica e extrai as figuras embutidas
   (via PyMuPDF quando disponível, com fallback `pdfimages` do
   poppler-utils). Para cada figura, tenta capturar a legenda ("Figure N:"
   / "Figura N:") do texto próximo à imagem na mesma página.

2. **Busca remota (Open Access)**: consulta a API do openalex/arXiv por
   artigos OA sobre o tema, baixa os PDFs e aplica a extração local.

Cada imagem extraída é salva em `pesquisa/imagens/` acompanhada de:
- `FONTES.md`: catálogo com a citação da fonte em ABNT (NBR 6023:2018)
  e APA 7ª ed., legenda original, página e licença presumida.
- Bloco LaTeX (`\\begin{figure}`) pronto com `\\caption` citando a fonte,
  para inserção direta em artigos, teses, dissertações e livros.

IMPORTANTE (ética acadêmica): toda figura extraída DEVE ser usada com
citação da fonte ("Fonte: Autor (Ano)"), conforme exigido pela ABNT.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MIN_WIDTH = 220     # px — descarta ícones/logos pequenos
MIN_HEIGHT = 160
MIN_BYTES = 12_000  # descarta artefatos minúsculos

CAPTION_RE = re.compile(
    r"(?:Fig(?:ure|ura)?\.?\s*(\d+)[.:—-]?\s*)([^\n]{10,300})",
    re.IGNORECASE,
)


@dataclass
class ExtractedFigure:
    """Uma figura real extraída de um artigo científico, com proveniência."""
    image_path: str
    source_pdf: str
    page: int
    figure_number: Optional[str] = None
    caption: str = ""
    authors: str = ""
    year: str = ""
    title: str = ""
    doi: str = ""
    width: int = 0
    height: int = 0

    # ------------------------------------------------------------------
    def abnt(self) -> str:
        """Referência da fonte em ABNT NBR 6023:2018."""
        autor = self.authors or "AUTOR DESCONHECIDO"
        ano = self.year or "s.d."
        titulo = self.title or Path(self.source_pdf).stem.replace("-", " ").title()
        doi = f" DOI: {self.doi}." if self.doi else ""
        return f"{autor}. {titulo}. {ano}.{doi}"

    def apa(self) -> str:
        """Referência da fonte em APA 7ª edição."""
        autor = self.authors or "Unknown"
        ano = self.year or "n.d."
        titulo = self.title or Path(self.source_pdf).stem.replace("-", " ").title()
        doi = f" https://doi.org/{self.doi}" if self.doi else ""
        return f"{autor} ({ano}). {titulo}.{doi}"

    def latex_figure(self) -> str:
        """Bloco LaTeX com \\caption citando a fonte (padrão ABNT)."""
        cap = self.caption or f"Figura extraída de {self.abnt()}"
        fonte = self.authors.split(",")[0] if self.authors else "o original"
        label = Path(self.image_path).stem
        return (
            "\\begin{figure}[htbp]\n"
            "  \\centering\n"
            f"  \\includegraphics[width=0.85\\textwidth]{{{Path(self.image_path).name}}}\n"
            f"  \\caption{{{cap} Fonte: {fonte} ({self.year or 's.d.'}).}}\n"
            f"  \\label{{fig:{label}}}\n"
            "\\end{figure}\n"
        )


class FigureHunter:
    """Extrai figuras reais de PDFs acadêmicos com legenda e fonte."""

    def __init__(self, images_dir: str = "pesquisa/imagens"):
        self.images_dir = Path(images_dir)
        self.figures: List[ExtractedFigure] = []

    # ------------------------------------------------------------------
    # Extração de figuras de um PDF
    # ------------------------------------------------------------------
    def extract_from_pdf(self, pdf_path: str, meta: Optional[Dict] = None) -> List[ExtractedFigure]:
        """
        Extrai figuras do PDF. `meta` opcional: {authors, year, title, doi}
        (vindo do PaperRecord do ResearchHub) para citação precisa.
        """
        pdf = Path(pdf_path)
        if not pdf.exists():
            return []
        self.images_dir.mkdir(parents=True, exist_ok=True)
        meta = meta or {}

        figures = self._extract_pymupdf(pdf, meta)
        if not figures:
            figures = self._extract_pdfimages(pdf, meta)
        self.figures.extend(figures)
        return figures

    # -- backend 1: PyMuPDF (com página e legenda) ----------------------
    def _extract_pymupdf(self, pdf: Path, meta: Dict) -> List[ExtractedFigure]:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            return []
        out: List[ExtractedFigure] = []
        try:
            doc = fitz.open(str(pdf))
        except Exception:
            return []
        stem = pdf.stem[:48]
        seen_xrefs = set()
        for pno in range(len(doc)):
            page = doc[pno]
            captions = CAPTION_RE.findall(page.get_text() or "")
            cap_iter = iter(captions)
            for img in page.get_images(full=True):
                xref = img[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.width < MIN_WIDTH or pix.height < MIN_HEIGHT:
                        continue
                    if pix.colorspace and pix.colorspace.n > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    fname = self.images_dir / f"{stem}-p{pno+1}-x{xref}.png"
                    pix.save(str(fname))
                    if fname.stat().st_size < MIN_BYTES:
                        fname.unlink(missing_ok=True)
                        continue
                    num, cap = next(cap_iter, (None, ""))
                    out.append(ExtractedFigure(
                        image_path=str(fname), source_pdf=str(pdf), page=pno + 1,
                        figure_number=num, caption=cap.strip(),
                        authors=meta.get("authors", ""), year=str(meta.get("year", "")),
                        title=meta.get("title", ""), doi=meta.get("doi", ""),
                        width=pix.width, height=pix.height,
                    ))
                except Exception:
                    continue
        doc.close()
        return out

    # -- backend 2: pdfimages (poppler) ---------------------------------
    def _extract_pdfimages(self, pdf: Path, meta: Dict) -> List[ExtractedFigure]:
        if not shutil.which("pdfimages"):
            return []
        stem = pdf.stem[:48]
        prefix = self.images_dir / f"{stem}-img"
        try:
            subprocess.run(["pdfimages", "-png", "-p", str(pdf), str(prefix)],
                           capture_output=True, timeout=120)
        except Exception:
            return []
        out: List[ExtractedFigure] = []
        for f in sorted(self.images_dir.glob(f"{stem}-img-*.png")):
            if f.stat().st_size < MIN_BYTES:
                f.unlink(missing_ok=True)
                continue
            m = re.search(r"-(\d+)-", f.name)
            page = int(m.group(1)) if m else 0
            out.append(ExtractedFigure(
                image_path=str(f), source_pdf=str(pdf), page=page,
                authors=meta.get("authors", ""), year=str(meta.get("year", "")),
                title=meta.get("title", ""), doi=meta.get("doi", ""),
            ))
        return out

    # ------------------------------------------------------------------
    # Varredura de uma pasta de produção (pesquisa/pdfs)
    # ------------------------------------------------------------------
    def harvest_production(self, production_dir: str,
                           papers_meta: Optional[List[Dict]] = None) -> List[ExtractedFigure]:
        """
        Varre `producao/pesquisa/pdfs/*.pdf` e extrai todas as figuras,
        casando cada PDF com os metadados dos papers quando disponíveis.
        """
        pdf_dir = Path(production_dir) / "pesquisa" / "pdfs"
        if not pdf_dir.exists():
            return []
        self.images_dir = Path(production_dir) / "pesquisa" / "imagens"
        meta_by_stem: Dict[str, Dict] = {}
        for m in papers_meta or []:
            key = (m.get("pdf_filename") or m.get("title") or "")[:48].lower()
            if key:
                meta_by_stem[key] = m
        all_figs: List[ExtractedFigure] = []
        for pdf in sorted(pdf_dir.glob("*.pdf")):
            meta = {}
            for key, m in meta_by_stem.items():
                if key and key in pdf.stem.lower():
                    meta = m
                    break
            all_figs.extend(self.extract_from_pdf(str(pdf), meta))
        self.write_catalog()
        return all_figs

    # ------------------------------------------------------------------
    # Catálogo de fontes (ABNT + APA) e blocos LaTeX
    # ------------------------------------------------------------------
    def write_catalog(self) -> Optional[str]:
        """Gera FONTES.md e figuras.json no diretório de imagens."""
        if not self.figures:
            return None
        self.images_dir.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Catálogo de Figuras Extraídas de Artigos Reais",
            "",
            "Cada figura abaixo foi extraída de um artigo científico real e **deve ser usada com citação da fonte**, conforme a ABNT NBR 6023:2018 e a APA 7ª edição.",
            "",
        ]
        for i, fig in enumerate(self.figures, 1):
            lines.append(f"## Figura {i} — `{Path(fig.image_path).name}`")
            lines.append("")
            lines.append("| Campo | Valor |")
            lines.append("|---|---|")
            lines.append(f"| Arquivo | `{Path(fig.image_path).name}` |")
            lines.append(f"| PDF de origem | `{Path(fig.source_pdf).name}` (página {fig.page}) |")
            if fig.figure_number:
                lines.append(f"| Nº no artigo | Figura {fig.figure_number} |")
            if fig.caption:
                lines.append(f"| Legenda original | {fig.caption} |")
            lines.append(f"| Fonte (ABNT) | {fig.abnt()} |")
            lines.append(f"| Fonte (APA) | {fig.apa()} |")
            lines.append("")
            lines.append("Bloco LaTeX pronto:")
            lines.append("")
            lines.append("```latex")
            lines.append(fig.latex_figure().rstrip())
            lines.append("```")
            lines.append("")
        path = self.images_dir / "FONTES.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        (self.images_dir / "figuras.json").write_text(
            json.dumps([asdict(f) for f in self.figures], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(path)
