"""R1078: contratos, KDP, design tokens, licença e release."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from marceloclaro.book_studio import BookManifest
from marceloclaro.bookstudio import (
    BookProject,
    DesignTokens,
    InkType,
    KDPError,
    PaperStock,
    ReleaseError,
    ReleaseManifest,
    classify_license,
    contrast_ratio,
    default_tokens,
    evaluate,
    kdp_cover_spec,
    parse_trim,
    validate_isbn,
    validate_landscape,
)
from marceloclaro.bookstudio.epub import audit_epub

ROOT = Path(__file__).resolve().parents[1]
LANDSCAPE = ROOT / "reports/r1078/github_landscape.json"


def _manifest() -> BookManifest:
    return BookManifest(
        title="Molambudos — teste", author="Marcelo", language="pt-BR",
        trim="160x230mm", engine="latex", source="main.tex", chapters=(),
        output_formats=("pdf",),
    )


def test_kdp_spine_and_full_cover_160x230():
    spec = kdp_cover_spec("160x230mm", 422, paper="white", ink="premium_color")
    assert spec.paper is PaperStock.WHITE
    assert spec.ink is InkType.PREMIUM_COLOR
    assert spec.spine_in == pytest.approx(0.990434, abs=1e-5)
    assert spec.full_cover_width_in == pytest.approx(13.8388, abs=1e-3)
    assert spec.full_cover_height_in == pytest.approx(9.3051, abs=1e-3)
    assert spec.cover_pixels_300dpi == (4152, 2792)
    assert spec.trim_supported is False
    assert any("KDP" in warning for warning in spec.warnings)


def test_kdp_6x9_cream_bw_is_standard():
    spec = kdp_cover_spec("6x9in", 300, paper="cream", ink="bw")
    assert spec.spine_in == pytest.approx(0.75)
    assert spec.full_cover_width_in == pytest.approx(13.0)
    assert spec.full_cover_height_in == pytest.approx(9.25)
    assert spec.trim_supported is True
    assert spec.spine_text_allowed is True


def test_kdp_rejects_invalid_combinations_and_page_count():
    with pytest.raises(KDPError):
        kdp_cover_spec("6x9in", 300, paper="cream", ink="premium_color")
    with pytest.raises(KDPError):
        kdp_cover_spec("6x9in", 10)
    with pytest.raises(KDPError):
        kdp_cover_spec("6x9in", 300, bleed_in=0.05)
    assert parse_trim("160x230mm")[0] == pytest.approx(6.2992, abs=1e-3)


def test_design_tokens_contrast_and_tac():
    tokens = default_tokens()
    assert tokens.valid is True
    assert tokens.errors == []
    assert tokens.contrast("mem") >= 4.5
    assert tokens.contrast("doc") >= 4.5
    assert tokens.contrast("luc") >= 4.5
    assert tokens.contrast("cont") >= 4.5
    assert tokens.contrast("epi") >= 4.5
    assert tokens.contrast("ink") >= 7.0
    assert tokens.palette["cont"].tac == pytest.approx(205.0)
    assert tokens.palette["cuidado"].tac == pytest.approx(140.0)


def test_cuidado_is_restricted_to_black():
    tokens = default_tokens()
    assert tokens.contrast("cuidado", tokens.black_hex) >= 4.5
    assert tokens.contrast("cuidado", tokens.paper_hex) < 4.5
    assert contrast_ratio("#FF4D4D", "#000000") >= 4.5


def test_license_gate_blocks_copyleft_library_and_allows_cli():
    blocked = evaluate("pymupdf/PyMuPDF", "AGPL-3.0", "library")
    assert blocked.allowed is False
    assert blocked.license_class.value == "strong_copyleft"

    allowed = evaluate("jgm/pandoc", "GPL-2.0", "adapter")
    assert allowed.allowed is True
    assert allowed.review_required is False

    weak = evaluate("languagetool-org/languagetool", "LGPL-2.1", "library")
    assert weak.allowed is True
    assert weak.review_required is True

    source = evaluate("remotion-dev/remotion", "Remotion License (não OSI)", "library")
    assert source.allowed is False

    unknown = evaluate("x/y", "Proprietary Custom", "library")
    assert unknown.allowed is False


def test_landscape_has_no_license_violations():
    result = validate_landscape(LANDSCAPE)
    assert result["status"] == "ok", result["violations"]
    assert result["count"] >= 100
    assert result["by_class"]["strong_copyleft"] >= 10


def test_release_manifest_roundtrip_and_tamper(tmp_path: Path):
    first = tmp_path / "a.bin"
    second = tmp_path / "b.bin"
    first.write_bytes(b"alpha")
    second.write_bytes(b"beta")
    manifest = ReleaseManifest.build("R-TEST", [first, second], root=tmp_path)
    assert manifest.verify(tmp_path)["ok"] is True

    saved = manifest.save(tmp_path / "release.json")
    loaded = ReleaseManifest.load(saved)
    assert loaded.verify(tmp_path)["ok"] is True

    first.write_bytes(b"tampered")
    result = loaded.verify(tmp_path)
    assert result["ok"] is False
    assert result["mismatched"][0]["path"] == "a.bin"

    second.unlink()
    result = loaded.verify(tmp_path)
    assert result["ok"] is False
    assert "b.bin" in result["missing"]


def test_release_manifest_rejects_duplicates(tmp_path: Path):
    first = tmp_path / "a.bin"
    first.write_bytes(b"alpha")
    with pytest.raises(ReleaseError):
        ReleaseManifest.build("R-DUP", [first, first], root=tmp_path)


def test_isbn_validation():
    assert validate_isbn("978-3-16-148410-0") is True
    assert validate_isbn("0-306-40615-2") is True
    assert validate_isbn("978-3-16-148410-1") is False
    assert validate_isbn("") is False


def test_book_project_validation():
    good = BookProject(
        manifest=_manifest(), page_count=422, isbn="978-3-16-148410-0",
        paper="white", ink="premium_color", cover_art_dpi=300,
    )
    assert good.ok is True
    assert any(issue["id"] == "kdp:trim" and issue["status"] == "warn"
               for issue in good.validate())

    low_dpi = BookProject(
        manifest=_manifest(), page_count=422, cover_art_dpi=163,
        paper="white", ink="premium_color",
    )
    assert low_dpi.ok is False
    assert any(issue["id"] == "cover:dpi" and issue["status"] == "fail"
               for issue in low_dpi.validate())

    bad_isbn = BookProject(
        manifest=_manifest(), page_count=422, isbn="978-3-16-148410-1",
        cover_art_dpi=300, paper="white", ink="premium_color",
    )
    assert bad_isbn.ok is False


def test_cli_kdp_and_license():
    kdp = subprocess.run(
        [sys.executable, "-m", "marceloclaro.bookstudio", "kdp",
         "--pages", "300", "--trim", "6x9in", "--paper", "cream", "--ink", "bw"],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert kdp.returncode == 0, kdp.stderr
    payload = json.loads(kdp.stdout)
    assert payload["spine_in"] == pytest.approx(0.75)

    lic = subprocess.run(
        [sys.executable, "-m", "marceloclaro.bookstudio", "license", str(LANDSCAPE)],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert lic.returncode == 0, lic.stdout + lic.stderr
    assert json.loads(lic.stdout)["status"] == "ok"


def test_release_epub_has_accessibility_summary():
    epub = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075/release/Molambudos_PT_revisado.epub"
    if not epub.is_file():
        pytest.skip("conteúdo literário gitignored não está presente")
    audit = audit_epub(epub)
    assert audit["mimetype_first"] is True
    assert audit["mimetype_stored"] is True
    assert audit["accessibility_summary"] is True
    assert audit["language"] == "pt-BR"
    assert audit["img_tags"] == audit["img_with_alt"]
    assert audit["images"] >= 13
    assert audit["spine_items"] >= 20
