"""R1074: gate do EPUB, preflight KDP e estado do PDF tagged do Molambudos."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1074"
EPUB_MANIFEST = REPORT / "epub_manifest.json"
PREFLIGHT = REPORT / "preflight_kdp.json"
TAGGED = REPORT / "tagged_pdf_status.json"
BOOK = ROOT / "literatura/molambudos"
RELEASE = BOOK / "release/2026-11-05"
CANONICAL_SHA = "3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_epub_manifest_completed():
    data = load(EPUB_MANIFEST)
    assert data["status"] == "completed"
    assert data["parts"] == 5
    assert data["fragments"] == 84
    validation = data["validation"]
    assert validation["zip_ok"] is True
    assert validation["opf_ok"] is True
    assert validation["nav_ok"] is True
    assert validation["fragment_links"] == 84
    assert validation["sections"] == 84
    assert validation["low_sections"] == []
    assert validation["nav_broken"] == []
    assert validation["raw_latex"] == []
    assert validation["missing_images"] == []
    assert validation["unresolved_refs"] == []
    assert 0.90 <= validation["word_ratio"] <= 1.10
    assert len(data["epub"]["sha256"]) == 64
    assert data["validation"]["metadata"]["title"].startswith("Molambudos")
    assert data["validation"]["metadata"]["language"] == "pt-BR"


def test_preflight_documents_kdp_blockers():
    data = load(PREFLIGHT)
    assert data["status"] == "fail"
    checks = {check["id"]: check for check in data["checks"]}
    for check_id in ("cover_resolution", "barcode_area_size", "barcode_position"):
        assert checks[check_id]["status"] == "fail", check_id
    for check_id in ("trim_custom", "cover_size", "cover_fonts", "interior_fonts",
                     "interior_margins", "cover_isbn"):
        assert checks[check_id]["status"] == "pass", check_id
    assert checks["interior_tagged"]["status"] == "warn"
    assert checks["interior_bleed"]["status"] == "warn"
    assert data["summary"]["fail"] == 3
    assert data["summary"]["warn"] >= 5


def test_tagged_pdf_is_blocked_with_evidence():
    data = load(TAGGED)
    assert data["status"] == "blocked"
    assert len(data["attempts"]) >= 2
    errors = " ".join(attempt["error"] for attempt in data["attempts"]).lower()
    assert "luaotfload" in errors
    assert "tagpdf" in errors
    for attempt in data["attempts"]:
        assert (ROOT / attempt["evidence"]).is_file(), attempt["evidence"]


def test_versioned_report_states_limits():
    readme = (REPORT / "README.md").read_text(encoding="utf-8")
    assert "EPUB" in readme
    assert "KDP" in readme
    assert "FAIL" in readme
    assert "bloqueado" in readme.lower()
    assert "EPUBCheck" in readme


def test_local_epub_and_release_if_present():
    if not RELEASE.is_dir():
        pytest.skip("conteúdo literário gitignored não está presente")

    epub = RELEASE / "epub/Molambudos_PT.epub"
    manifest = load(EPUB_MANIFEST)
    assert epub.is_file()
    assert sha256(epub) == manifest["epub"]["sha256"]
    assert (RELEASE / "epub/source/Molambudos_PT.md").is_file()
    assert (RELEASE / "preflight/preflight_kdp.json").is_file()
    assert (RELEASE / "epub/EPUB_MANIFEST.json").is_file()

    with zipfile.ZipFile(epub) as z:
        assert z.testzip() is None
        nav = ET.fromstring(z.read("EPUB/nav.xhtml"))
        links = [a.get("href") for a in nav.findall(".//{http://www.w3.org/1999/xhtml}a")]
        assert sum(1 for href in links if href and "#" in href) >= 84

    sums = (RELEASE / "SHA256SUMS.txt").read_text(encoding="utf-8")
    assert "epub/Molambudos_PT.epub" in sums
    assert "preflight/preflight_kdp.json" in sums

    canonical = BOOK / "Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf"
    assert canonical.is_file()
    assert sha256(canonical) == CANONICAL_SHA


def test_candidate_cover_improves_barcode_but_fails_resolution():
    data = load(REPORT / "preflight_kdp_candidate.json")
    assert data["status"] == "fail"
    assert data["summary"]["fail"] == 1
    checks = {check["id"]: check for check in data["checks"]}
    assert checks["barcode_area_size"]["status"] == "pass"
    assert checks["barcode_position"]["status"] == "pass"
    assert checks["barcode_fake_art"]["status"] == "pass"
    assert checks["cover_resolution"]["status"] == "fail"
    assert data["source_dimensions"] == [2000, 1405]
    assert len(data["candidate_sha256"]) == 64


def test_release_note_discloses_not_kdp_ready():
    if not RELEASE.is_dir():
        pytest.skip("conteúdo literário gitignored não está presente")
    note = (RELEASE / "RELEASE_NOTE.md").read_text(encoding="utf-8")
    lowered = note.lower()
    assert "não enviar" in lowered or "fail" in lowered
    assert "300 dpi" in lowered
    assert "epub" in lowered
    assert "pdf tagged" in lowered or "tagged" in lowered
