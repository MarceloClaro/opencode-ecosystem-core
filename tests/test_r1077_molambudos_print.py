"""R1077: gate da variante print-safe do Molambudos."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1077"
MANIFEST = REPORT / "print_manifest.json"
PRINT = ROOT / "literatura/molambudos/Molambudos_Print_R1077"
DIGITAL = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075"
DIGITAL_SHA = "9ee4c4679fe7d42b1c30605f3bebaae5dfe42cfb18567cf93f96444f5cb955be"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_manifest_print_safe_metrics():
    data = load(MANIFEST)
    assert data["status"] == "completed"
    assert data["pdf"]["pages"] == 422
    assert data["images"]["count"] == 20
    assert data["images"]["min_xppi"] >= 300
    assert data["images"]["below_300"] == []
    assert data["fonts"]["not_embedded"] == []
    assert max(v["tac"] for v in data["palette_cmyk"].values()) <= 210
    assert data["ink_coverage"]["r1077"]["avg_tac"] < 0.50
    assert data["ink_coverage"]["r1077"]["max_tac"] < 3.00
    assert len(data["pdf"]["sha256"]) == 64


def test_print_source_uses_safe_paths():
    if not PRINT.is_dir():
        pytest.skip("conteúdo literário gitignored não está presente")

    main = (PRINT / "main.tex").read_text(encoding="utf-8")
    assert "\\ifdefined\\PRINTSAFE" in main
    assert "\\pagecolor{white}" in main
    assert "\\input{frontmatter/cuidado_print}" in main
    assert "\\input{frontmatter/titlepage_print}" in main
    assert "\\input{frontmatter/backpage_print}" in main
    assert main.count("\\partopener{") >= 5

    fragments = [p for p in (PRINT / "fragmentos").rglob("*.tex") if "_removidos" not in str(p)]
    text = "\n".join(p.read_text(encoding="utf-8") for p in fragments)
    assert text.count("width=0.54\\textwidth") == 4
    assert text.count("width=0.40\\textwidth") == 1
    assert "width=0.55\\textwidth" not in text

    data = load(MANIFEST)
    pdf = PRINT / "main_kdp_print_r1077.pdf"
    assert pdf.is_file()
    assert sha256(pdf) == data["pdf"]["sha256"]

    out = subprocess.run(["pdfimages", "-list", str(pdf)], capture_output=True, text=True).stdout
    for line in out.splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 14 and parts[2] == "image":
            assert int(parts[-4]) >= 300, line

    assert sha256(DIGITAL / "main_kdp_pt_160x230mm.pdf") == DIGITAL_SHA


def test_report_documents_tradeoff_and_limits():
    text = (REPORT / "README.md").read_text(encoding="utf-8").lower()
    for term in ("print-safe", "tac", "300 dpi", "capa", "lombada", "10/10"):
        assert term in text, term
