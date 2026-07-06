# -*- coding: utf-8 -*-

from pathlib import Path


def test_executive_changelog_artifact_exists_and_has_core_sections():
    path = Path("CHANGELOG_EXECUTIVO_2026-07-06.md")
    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert "# CHANGELOG Executivo Consolidado" in text
    assert "f570e63" in text
    assert "aebe0e7" in text
    assert "dc23c30" in text
    assert "0ede174" in text
    assert "b82cda9" in text
    assert "8/8 implemented" in text
    assert "working tree limpo" in text
