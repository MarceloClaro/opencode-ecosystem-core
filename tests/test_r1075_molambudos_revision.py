"""R1075: gate da edição revista do Molambudos."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reports/r1075/revision_manifest.json"
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


def test_manifest_records_revision_counts():
    data = load(MANIFEST)
    assert data["status"] == "completed"
    canonical = data["canonical"]
    revised = data["revised"]
    assert canonical["groups"]["MEM"]["sections"] == 27
    assert canonical["groups"]["DOC"]["sections"] == 27
    assert canonical["groups"]["LUC"]["sections"] == 17
    assert canonical["groups"]["CONT"]["sections"] == 13
    assert revised["groups"]["MEM"]["sections"] == 27
    assert revised["groups"]["DOC"]["sections"] == 27
    assert revised["groups"]["LUC"]["sections"] == 23
    assert revised["groups"]["CONT"]["sections"] == 7
    assert 15 <= data["changes"]["doc_cut_percent"] <= 20
    assert data["changes"]["cont_cut_percent"] >= 30
    assert data["changes"]["luc_growth_percent"] >= 30
    assert data["changes"]["removed_cont"] == [
        "CONT-02", "CONT-06", "CONT-08", "CONT-10", "CONT-11", "CONT-12"
    ]
    assert data["changes"]["added_luc"] == [
        "LUC-15", "LUC-16", "LUC-17", "LUC-18", "LUC-19", "LUC-20"
    ]
    assert len(revised["pdf_sha256"]) == 64
    assert len(revised["epub_sha256"]) == 64


def test_epub_revision_is_structurally_valid():
    data = load(EPUB_MANIFEST)
    assert data["status"] == "completed"
    assert data["fragments"] == 84
    assert data["parts"] == 5
    v = data["validation"]
    assert v["fragment_links"] == 84
    assert v["sections"] == 84
    assert v["nav_links"] >= 84
    assert v["nav_broken"] == []
    assert v["raw_latex"] == []
    assert v["missing_images"] == []
    assert v["unresolved_refs"] == []
    assert v["low_sections"] == []
    assert 0.90 <= v["word_ratio"] <= 1.10


def test_local_revision_if_present():
    if not REV.is_dir():
        pytest.skip("conteúdo literário gitignored não está presente")

    main = (REV / "main.tex").read_text(encoding="utf-8")
    assert len(re.findall(r"\\fragdef\{CONT-[^}]*\}", main)) == 7
    assert len(re.findall(r"\\fragdef\{LUC-[^}]*\}", main)) == 23
    for removed in ("CONT-02", "CONT-06", "CONT-08", "CONT-10", "CONT-11", "CONT-12"):
        assert f"\\fragdef{{{removed}}}" not in main
    for added in ("LUC-15", "LUC-16", "LUC-17", "LUC-18", "LUC-19", "LUC-20"):
        assert (REV / f"fragmentos/luc/{added}.tex").is_file()

    data = load(MANIFEST)
    pdf = REV / "main_kdp_pt_160x230mm.pdf"
    epub = REV / "release/Molambudos_PT_revisado.epub"
    assert pdf.is_file()
    assert epub.is_file()
    assert sha256(pdf) == data["revised"]["pdf_sha256"]
    assert sha256(epub) == data["revised"]["epub_sha256"]

    with zipfile.ZipFile(epub) as z:
        assert z.testzip() is None
        nav = z.read("EPUB/nav.xhtml").decode("utf-8")
        assert len(re.findall(r">(?:MEM|DOC|LUC|CONT)-[^<]+", nav)) >= 84

    assert sha256(CANON / "main_kdp_pt_160x230mm.pdf") == CANON_SHA


def test_report_documents_limits_and_techniques():
    text = (ROOT / "reports/r1075/README.md").read_text(encoding="utf-8").lower()
    for term in ("ontológica", "técnicas", "não é publicação", "nova isbn",
                 "capa", "traduções", "tagged"):
        assert term in text, term
    assert "10/10" in text
