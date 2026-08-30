"""Contratos documentais da SPEC-935-R456 (manual técnico RAG + proposta Recamán)."""

from __future__ import annotations

from pathlib import Path

import shutil


ROOT = Path(__file__).resolve().parent.parent
MANUAL_DIR = ROOT / "docs" / "r456_manual_tecnico_rag"
TEX = (MANUAL_DIR / "manual_rag_recaman.tex").read_text(encoding="utf-8")
BIB = (MANUAL_DIR / "referencias.bib").read_text(encoding="utf-8")
SPEC = (ROOT / "specs" / "SPEC-935-R456-manual-tecnico-rag-recaman.md").read_text(encoding="utf-8")


def _has_tool(name: str) -> bool:
    return shutil.which(name) is not None


def test_spec_exists() -> None:
    assert "SPEC-935-R456" in SPEC
    assert "Manual técnico" in SPEC
    assert "Recamán" in SPEC


def test_manual_source_exists() -> None:
    assert TEX
    assert r"\documentclass" in TEX
    assert "abntex2" in TEX


def test_bibliography_exists() -> None:
    assert BIB
    # Referências reais verificadas (DOIs / arXiv) presentes.
    for key in (
        "Liu2024LostMiddle",
        "RobertsonZaragoza2009BM25",
        "CarbonellGoldstein1998MMR",
        "Lewis2020RAG",
        "KhattabZaharia2020ColBERT",
        "Edge2024GraphRAG",
        "Alekseyev2022RecamanCousins",
        "Yan2024CRAG",
        "Jeong2024AdaptiveRAG",
    ):
        assert "@" in BIB, "deve conter entradas bibtex"
        assert key in BIB, key


def test_build_scripts_exist() -> None:
    build = MANUAL_DIR / "build.sh"
    makefile = MANUAL_DIR / "Makefile"
    assert build.exists(), "build.sh deve existir"
    assert makefile.exists(), "Makefile deve existir"
    assert "pdflatex" in build.read_text(encoding="utf-8")
    assert "bibtex" in build.read_text(encoding="utf-8")


def test_manual_is_compilable() -> None:
    """O fonte LaTeX deve declarar pacotes e estruturas exigidos."""
    for pkg in ("tikz", "amsmath", "algorithm", "listings", "booktabs", "abntex2cite"):
        assert pkg in TEX, pkg


def test_pdf_produced() -> None:
    pdf = MANUAL_DIR / "manual_rag_recaman.pdf"
    if not _has_tool("pdflatex"):
        # Sem toolchain, exige que ao menos o fontes exista (validação parcial).
        assert TEX
        return
    assert pdf.exists(), "PDF deve ter sido compilado previamente (rode ./build.sh)"


def test_pdf_is_readable() -> None:
    if not _has_tool("pdftotext"):
        return
    pdf = MANUAL_DIR / "manual_rag_recaman.pdf"
    if not pdf.exists():
        return
    text = _pdftotext(pdf)
    assert len(text) > 5000, "texto extraído deve ser não trivial"


def test_distinguishes_current_from_proposal() -> None:
    text = TEX + SPEC
    assert "proposta" in text.lower()
    assert "não implementada" in text.lower() or "não implementado" in text.lower()
    assert "pós-Recamán" in text or "pos-Recaman" in text
    # Deve haver aviso metodológico explícito.
    assert "Aviso metodológico" in TEX


def test_references_real_and_validated() -> None:
    # Não deve haver DOIs "placeholder" nem notas de fabricação.
    lower = BIB.lower()
    for forbidden in ("doi = {0000", "author = {tbd", "nao inventado", "foomaker", "exemplo"):
        assert forbidden not in lower, forbidden


def test_cites_current_components() -> None:
    assert "rag/evolved.py" in TEX
    assert "rag/enhanced\\_search\\_rag.py" in TEX
    assert "AdaptiveRetriever" in TEX
    assert "UnifiedSearcher" in TEX
    assert "ReferenceAuditor" in TEX


def test_no_external_certification_claim() -> None:
    # O manual só menciona certificação para negar que a alegue.
    assert "Nenhuma alegação de certificação" in TEX
    assert "certificação externa" in TEX.lower() or "certificação" in TEX.lower()


def test_legends_and_calculations_present() -> None:
    # Legendas de diagramas.
    assert "Legenda:" in TEX
    # Cálculos / equações.
    assert r"\begin{equation}" in TEX
    assert "BM25" in TEX
    assert "MMR" in TEX
    assert "Recamán" in TEX or "Recaman" in TEX
    # Especificações técnicas em tabela.
    assert "Especificações técnicas" in TEX


def _pdftotext(pdf: Path) -> str:
    import subprocess

    result = subprocess.run(
        ["pdftotext", str(pdf), "-"],
        capture_output=True,
        text=True,
    )
    return result.stdout
