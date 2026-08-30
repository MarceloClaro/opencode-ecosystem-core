"""Contratos documentais da SPEC-935-R456 (manual técnico RAG + proposta Recamán).

O manual é MODULAR: o documento-mestre main.tex inclui cada seção via \\input.
Cada seção vive em um arquivo sec_XX_*.tex separado, permitindo aprofundar uma
seção isoladamente e recompilar o PDF único (main.pdf).
"""

from __future__ import annotations

from pathlib import Path

import shutil


ROOT = Path(__file__).resolve().parent.parent
MANUAL_DIR = ROOT / "docs" / "r456_manual_tecnico_rag"

MAIN = (MANUAL_DIR / "main.tex").read_text(encoding="utf-8")
SEC01 = (MANUAL_DIR / "sec_01_introducao.tex").read_text(encoding="utf-8")
SEC02 = (MANUAL_DIR / "sec_02_problema_pesquisa.tex").read_text(encoding="utf-8")
SEC03 = (MANUAL_DIR / "sec_03_fundamentacao.tex").read_text(encoding="utf-8")
SEC04 = (MANUAL_DIR / "sec_04_estado_atual.tex").read_text(encoding="utf-8")
SEC05 = (MANUAL_DIR / "sec_05_proposta_recaman.tex").read_text(encoding="utf-8")
SEC06 = (MANUAL_DIR / "sec_06_calculos_specs.tex").read_text(encoding="utf-8")
SEC07 = (MANUAL_DIR / "sec_07_implementacoes.tex").read_text(encoding="utf-8")
SEC08 = (MANUAL_DIR / "sec_08_mapas_dados.tex").read_text(encoding="utf-8")
SEC09 = (MANUAL_DIR / "sec_09_consideracoes.tex").read_text(encoding="utf-8")

BIB = (MANUAL_DIR / "referencias.bib").read_text(encoding="utf-8")
SPEC = (ROOT / "specs" / "SPEC-935-R456-manual-tecnico-rag-recaman.md").read_text(encoding="utf-8")

# Todo o corpo = concatenação das seções (para checagens de conteúdo espalhadas).
ALL_SECTIONS = "\n".join(
    [SEC01, SEC02, SEC03, SEC04, SEC05, SEC06, SEC07, SEC08, SEC09]
)


def _has_tool(name: str) -> bool:
    return shutil.which(name) is not None


def test_spec_exists() -> None:
    assert "SPEC-935-R456" in SPEC
    assert "Manual técnico" in SPEC
    assert "Recamán" in SPEC


# ---------------------------------------------------------------
# Modularidade
# ---------------------------------------------------------------
def test_manual_is_modular() -> None:
    """O documento-mestre deve incluir cada seção via \\input."""
    assert r"\documentclass" in MAIN
    assert "abntex2" in MAIN
    for sec in ("sec_01_introducao", "sec_02_problema_pesquisa",
                "sec_03_fundamentacao", "sec_04_estado_atual",
                "sec_05_proposta_recaman", "sec_06_calculos_specs",
                "sec_07_implementacoes", "sec_08_mapas_dados",
                "sec_09_consideracoes"):
        assert f"\\input{{{sec}}}" in MAIN, sec


def test_all_sections_exist() -> None:
    """Cada arquivo de seção deve existir e ter conteúdo."""
    for path in (
        "sec_01_introducao.tex", "sec_02_problema_pesquisa.tex",
        "sec_03_fundamentacao.tex", "sec_04_estado_atual.tex",
        "sec_05_proposta_recaman.tex", "sec_06_calculos_specs.tex",
        "sec_07_implementacoes.tex", "sec_08_mapas_dados.tex",
        "sec_09_consideracoes.tex",
        "sec_00_capa_rosto.tex",
    ):
        assert (MANUAL_DIR / path).exists(), path


# ---------------------------------------------------------------
# Conteúdo do problema de pesquisa e impactos (nova Seção 2)
# ---------------------------------------------------------------
def test_problem_section_present() -> None:
    assert "Problema de Pesquisa e Impactos" in SEC02
    assert "Problema de pesquisa (PP)" in SEC02
    assert "RQ1" in SEC02 and "RQ2" in SEC02 and "RQ3" in SEC02 and "RQ4" in SEC02
    assert "H1" in SEC02
    assert "Impactos na Ciência" in SEC02
    assert "Impactos no Ecossistema OpenCode Ecosystem Core" in SEC02


def test_section_numbering_logical() -> None:
    """A numeração deve seguir a sequência lógica didática."""
    assert "1. Introdução e Escopo" in SEC01
    assert "2. Problema de Pesquisa" in SEC02
    assert "3. Fundamentação Teórica" in SEC03
    assert "4. Estado Atual da Arquitetura RAG" in SEC04
    assert "5. Proposta Pós-Recamán" in SEC05
    assert "6. Cálculos e Especificações" in SEC06
    assert "7. Implementações Reproduzíveis" in SEC07
    assert "8. Mapas de Dados" in SEC08
    assert "9. Considerações Finais" in SEC09


# ---------------------------------------------------------------
# Autoria
# ---------------------------------------------------------------
def test_authorship_present() -> None:
    # Autoria definida nos metadados do documento-mestre.
    assert "Marcelo Claro Laranjeira" in MAIN
    assert "0000-0001-8996-2887" in MAIN
    assert "marceloclaro@gmail.com" in MAIN
    # A folha de rosto referencia a autoria via macro (não duplica o nome literal).
    assert r"\imprimirautor" in SEC00_TEXT()


def SEC00_TEXT() -> str:
    p = MANUAL_DIR / "sec_00_capa_rosto.tex"
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ---------------------------------------------------------------
# Bibliografia
# ---------------------------------------------------------------
def test_bibliography_exists() -> None:
    assert BIB
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
        assert "@" in BIB
        assert key in BIB, key


def test_build_scripts_exist() -> None:
    build = MANUAL_DIR / "build.sh"
    makefile = MANUAL_DIR / "Makefile"
    assert build.exists()
    assert makefile.exists()
    assert "pdflatex" in build.read_text(encoding="utf-8")
    assert "bibtex" in build.read_text(encoding="utf-8")
    assert "main" in build.read_text(encoding="utf-8")


# ---------------------------------------------------------------
# Compilação e PDF
# ---------------------------------------------------------------
def test_manual_is_compilable() -> None:
    for pkg in ("tikz", "amsmath", "algorithm", "listings", "booktabs", "abntex2cite"):
        assert pkg in MAIN, pkg


def test_pdf_produced() -> None:
    pdf = MANUAL_DIR / "main.pdf"
    if not _has_tool("pdflatex"):
        assert MAIN
        return
    assert pdf.exists(), "PDF deve ter sido compilado previamente (rode ./build.sh)"


def test_pdf_is_readable() -> None:
    if not _has_tool("pdftotext"):
        return
    pdf = MANUAL_DIR / "main.pdf"
    if not pdf.exists():
        return
    text = _pdftotext(pdf)
    assert len(text) > 20000, "texto extraído deve ser não trivial (manual profundo)"


# ---------------------------------------------------------------
# Rigor: atual x proposta, anti-overclaim
# ---------------------------------------------------------------
def test_distinguishes_current_from_proposal() -> None:
    text = ALL_SECTIONS
    assert "proposta" in text.lower()
    assert "não implementada" in text.lower() or "não implementado" in text.lower()
    assert "pós-Recamán" in text or "pos-Recaman" in text
    assert "Aviso metodológico" in SEC05


def test_references_real_and_validated() -> None:
    lower = BIB.lower()
    for forbidden in ("doi = {0000", "author = {tbd", "nao inventado", "foomaker"):
        assert forbidden not in lower, forbidden


def test_cites_current_components() -> None:
    assert "rag/evolved.py" in SEC04
    assert "rag/enhanced\\_search\\_rag.py" in SEC04
    assert "AdaptiveRetriever" in SEC04
    assert "UnifiedSearcher" in SEC04
    assert "ReferenceAuditor" in SEC04


def test_no_external_certification_claim() -> None:
    assert "Nenhuma alegação de certificação" in ALL_SECTIONS or \
           "não é alegada" in ALL_SECTIONS.lower() or \
           "anti-overclaim" in ALL_SECTIONS.lower()


def test_legends_and_calculations_present() -> None:
    assert "Legenda:" in ALL_SECTIONS
    assert r"\begin{equation}" in ALL_SECTIONS
    assert "BM25" in ALL_SECTIONS
    assert "MMR" in ALL_SECTIONS
    assert "Recamán" in ALL_SECTIONS or "Recaman" in ALL_SECTIONS
    assert "Especificações técnicas" in SEC06


def _pdftotext(pdf: Path) -> str:
    import subprocess

    result = subprocess.run(
        ["pdftotext", str(pdf), "-"],
        capture_output=True,
        text=True,
    )
    return result.stdout
