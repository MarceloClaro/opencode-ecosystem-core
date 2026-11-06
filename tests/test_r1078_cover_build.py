"""R1078: build reprodutível da capa print-safe."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT / "Molambudos_Capa_Frente_Corrigida.svg"
BACK = ROOT / "Molambudos_Contracapa_Corrigida.svg"
SCRIPT = ROOT / "reports/r1078/cover/build_cover.py"


def test_build_cover_reproducible(tmp_path: Path):
    if not FRONT.is_file() or not BACK.is_file():
        pytest.skip("SVGs de capa não estão presentes")
    for module in ("weasyprint", "cairosvg", "pypdf", "PIL"):
        if importlib.util.find_spec(module) is None:
            pytest.skip(f"{module} ausente")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--outdir", str(tmp_path), "--pages", "422"],
        cwd=ROOT, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stderr

    pdf = tmp_path / "molambudos_cover_422pp.pdf"
    guides = tmp_path / "molambudos_cover_422pp_guides.pdf"
    front = tmp_path / "front_300dpi.png"
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))

    assert pdf.is_file() and guides.is_file() and front.is_file()
    assert manifest["status"] == "generated"
    assert manifest["pdf"]["pages"] == 1
    assert manifest["pdf"]["page_in"] == pytest.approx([13.8389, 9.3051], abs=1e-3)
    assert manifest["pdf"]["fonts_not_embedded"] == []
    assert manifest["guides_pdf"]["bytes"] > 0

    from PIL import Image
    assert Image.open(front).size == (1890, 2717)

    check = subprocess.run(
        ["sha256sum", "-c", "SHA256SUMS.txt"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert check.returncode == 0, check.stdout + check.stderr
