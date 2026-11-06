"""R1082: gate das 6 pranchas de prova e do caderno preflightado."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1082"
PROOF = REPORT / "plate_proof"
PLATES = PROOF / "plates"
MANIFEST = PROOF / "plates_manifest.json"
PREFLIGHT = PROOF / "preflight.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_six_plates_manifest_and_hashes():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert len(data["items"]) == 6
    assert data["status"] == "proof_only"
    assert data["two_x_300dpi"] is False
    for item in data["items"]:
        target = PLATES / item["output"]
        assert target.is_file(), item["output"]
        assert sha256(target) == item["output_sha256"], item["output"]
        assert item["effective_dpi"] >= 300, item["id"]
        assert item["two_x_effective_dpi"] < 300, item["id"]
        assert item["required_width_px_for_2x_300dpi"] == 2032, item["id"]


def test_preflight_checks_and_pdf_hash():
    data = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    checks = data["checks"]
    assert checks["page_size_160x230"]["status"] == "pass"
    assert checks["pages"]["value"] == "8"
    assert checks["fonts_embedded"]["status"] == "pass"
    assert checks["images_min_300dpi"]["status"] == "pass"
    assert checks["two_x_300dpi"]["status"] == "fail"
    assert checks["ink_coverage"]["value"]["max_tac"] < 3.0
    pdf = Path(data["pdf"]["path"])
    assert pdf.is_file()
    assert sha256(pdf) == data["pdf"]["sha256"]


def test_review_and_readme_document_limits():
    review = (REPORT / "plate_review.md").read_text(encoding="utf-8").lower()
    for term in ("rosto", "mãos", "arquitetura", "anacronismo", "piranesi", "pencz"):
        assert term in review, term
    readme = re.sub(r"\s+", " ", (REPORT / "README.md").read_text(encoding="utf-8").lower())
    for term in ("2×", "2032", "nenhum fallback", "não é publicação", "não foi comprovada"):
        assert term in readme, term
