"""R1094: edição Grimório/RPG do Molambudos."""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "literatura/molambudos/Molambudos_Grimorio_R1094"
R1075 = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075"
PDF = BOOK / "main.pdf"
COVER = BOOK / "capa/capa_grimorio.pdf"
REPORT = ROOT / "reports/r1094/README.md"


def read(rel: str) -> str:
    return (BOOK / rel).read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_edition_structure_preserves_84_fragments_and_adds_apparatus() -> None:
    assert BOOK.is_dir()
    main = read("main.tex")
    assert len(re.findall(r"\\fragdef\{[^}]+\}\\input\{fragmentos/", main)) == 84
    fragments = [p for p in (BOOK / "fragmentos").rglob("*.tex") if "_removidos" not in str(p) and p.name != "epilogo_revisado.tex"]
    assert len(fragments) == 84
    assert sum(p.read_text(encoding="utf-8").count("\\fragtitle{") for p in fragments) == 84
    for rel in (
        "frontmatter/rpg_titlepage.tex",
        "frontmatter/rpg_protocolo.tex",
        "frontmatter/rpg_ficha.tex",
        "frontmatter/rpg_tabela_rotas.tex",
        "frontmatter/rpg_handouts.tex",
        "frontmatter/rpg_bestiario.tex",
        "capa/capa_grimorio.tex",
    ):
        assert (BOOK / rel).is_file(), rel
    for token in (
        "\\usepackage{yfonts}",
        "\\usepackage{tcolorbox}",
        "\\newtcolorbox{rpgbox}",
        "\\newtcolorbox{rpgdark}",
        "\\renewcommand{\\partopener}",
        "\\renewcommand{\\fragtitle}",
        "rpg_titlepage",
        "rpg_protocolo",
        "rpg_ficha",
        "rpg_tabela_rotas",
        "rpg_handouts",
        "rpg_bestiario",
    ):
        assert token in main, token


def test_r1075_remains_untouched() -> None:
    assert R1075.is_dir()
    source = (R1075 / "main.tex").read_text(encoding="utf-8")
    assert len(re.findall(r"\\fragdef\{[^}]+\}\\input\{fragmentos/", source)) == 84
    assert "223 rotas" in source
    if (R1075 / "main_kdp_pt_160x230mm.pdf").is_file():
        assert sha256(R1075 / "main_kdp_pt_160x230mm.pdf") == (
            "bd78c8db32db2976e2c087bf342cf909a232c56f3348885ea577d9f82773902a"
        )


def test_pdf_has_rpg_apparatus_and_no_old_defects() -> None:
    fitz = pytest.importorskip("fitz")
    assert PDF.is_file()
    pdf = fitz.open(PDF)
    assert 380 <= pdf.page_count <= 410
    assert abs(pdf[0].rect.width - 453.543) < 0.5
    assert abs(pdf[0].rect.height - 651.968) < 0.5
    text = re.sub(r"\s+", " ", "\n".join(page.get_text() for page in pdf))
    for key in (
        "PROTOCOLO DE MESA",
        "FICHA DO PACIENTE",
        "TABELA DE ROTAS",
        "A CRIATURA",
        "PROVA 01",
        "EDIÇÃO GRIMÓRIO",
    ):
        assert key in text, key
    for bad in ("> **↪ Rotas:", "um dos 60 mil", "978-65-01-23456-7"):
        assert bad not in text, bad
    fonts = subprocess.run(["pdffonts", str(PDF)], capture_output=True, text=True).stdout
    assert not [line for line in fonts.splitlines()[2:] if len(line.split()) >= 5 and line.split()[-5] == "no"]


def test_cover_is_a_single_160x230_typographic_page() -> None:
    fitz = pytest.importorskip("fitz")
    assert COVER.is_file()
    pdf = fitz.open(COVER)
    assert len(pdf) == 1
    assert abs(pdf[0].rect.width - 453.543) < 0.5
    assert abs(pdf[0].rect.height - 651.968) < 0.5
    text = re.sub(r"\s+", " ", pdf[0].get_text()).lower()
    for key in ("molambudos", "edição grimório", "marcelo dias"):
        assert key in text, key
    for bad in ("isbn", "978-65-01-23456-7", "62 anos"):
        assert bad not in text, bad
    source = (BOOK / "capa/capa_grimorio.tex").read_text(encoding="utf-8")
    assert "arte_frontal_original.png" in source
    assert "gothfamily" in source
    fonts = subprocess.run(["pdffonts", str(COVER)], capture_output=True, text=True).stdout
    assert not [line for line in fonts.splitlines()[2:] if len(line.split()) >= 5 and line.split()[-5] == "no"]


def test_report_documents_limits_and_no_overclaim() -> None:
    assert REPORT.is_file()
    text = REPORT.read_text(encoding="utf-8").lower()
    for key in ("não é um jogo completo", "aparato opcional", "não certifica", "10/10"):
        assert key in text, key
