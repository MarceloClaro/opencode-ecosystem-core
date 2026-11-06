"""R1076: gate da direção visual e tipográfica do Molambudos."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1076"
MANIFEST = REPORT / "design_manifest.json"
EPUB_MANIFEST = ROOT / "reports/r1075/epub_manifest.json"
REV = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075"
CANON = ROOT / "literatura/molambudos/Molambudos_VictoriaRegia"
CANON_SHA = "3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rgb(hex_color: str):
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def luminance(hex_color: str) -> float:
    def channel(c: int) -> float:
        v = c / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_palette_contrast_and_families():
    data = load(MANIFEST)
    assert data["status"] == "completed"
    palette = data["palette"]
    paper = palette["paper"]["hex"]
    for family in ("mem", "doc", "luc", "cont", "epi"):
        assert palette[family]["contrast"] >= 4.5, family
        assert contrast(palette[family]["hex"], paper) >= 4.5, family
    assert palette["ink"]["contrast"] >= 7.0
    red = palette["sangueclaro"]
    assert red["contrast_on_black"] >= 4.5
    assert red["contrast"] < 4.5  # documentado como uso exclusivo em fundo preto
    assert data["fragments"]["total"] == data["fragments"]["fragtitle"] == 84
    assert data["fragments"]["families"] == {"MEM": 27, "DOC": 27, "LUC": 23, "CONT": 7}


def test_caderno_and_hashes():
    data = load(MANIFEST)
    assert data["plates"]["count"] == 6
    assert len(data["plates"]["files"]) == 6
    assert "não são provas históricas" in data["plates"]["note"].lower() or "não são provas" in data["plates"]["note"].lower()
    assert data["pdf"]["pages"] == 421
    assert data["epub"]["images"] == 13
    assert len(data["pdf"]["sha256"]) == 64
    assert len(data["epub"]["sha256"]) == 64


def test_epub_design_is_present():
    data = load(EPUB_MANIFEST)
    assert data["status"] == "completed"
    assert data["fragments"] == 84
    assert data["validation"]["sections"] == 84
    assert data["validation"]["images"] == 13
    assert data["validation"]["nav_broken"] == []
    assert data["validation"]["raw_latex"] == []
    assert data["validation"]["missing_images"] == []


def test_local_design_if_present():
    if not REV.is_dir():
        pytest.skip("conteúdo literário gitignored não está presente")

    active = [p for p in (REV / "fragmentos").rglob("*.tex") if "_removidos" not in str(p)]
    fragtitles = sum(p.read_text(encoding="utf-8").count("\\fragtitle{") for p in active)
    assert fragtitles == 84

    main = (REV / "main.tex").read_text(encoding="utf-8")
    for macro in ("\\fragfamily", "\\fragtitle", "\\fragcode", "\\fragcap"):
        assert macro in main, macro
    for path in ("frontmatter/legenda_codigos.tex", "frontmatter/caderno_iconografico.tex"):
        assert (REV / path).is_file(), path
    for i in range(6):
        assert (REV / f"figures/immersao/placa_0{i}.png").is_file(), i

    data = load(MANIFEST)
    pdf = REV / "main_kdp_pt_160x230mm.pdf"
    epub = REV / "release/Molambudos_PT_revisado.epub"
    assert sha256(pdf) == data["pdf"]["sha256"]
    assert sha256(epub) == data["epub"]["sha256"]
    with zipfile.ZipFile(epub) as z:
        assert z.testzip() is None
        nav = z.read("EPUB/nav.xhtml").decode("utf-8")
        assert "Legenda dos Códigos" in nav
        assert "Caderno de Provas Iconográficas" in nav
        assert len(re.findall(r">(?:MEM|DOC|LUC|CONT)-[^<]+", nav)) >= 84
    assert sha256(CANON / "main_kdp_pt_160x230mm.pdf") == CANON_SHA


def test_design_report_documents_limits():
    text = (REPORT / "README.md").read_text(encoding="utf-8").lower()
    for term in ("contraste", "capitular", "caderno", "não são provas históricas",
                 "10/10", "capa", "traduções"):
        assert term in text, term
