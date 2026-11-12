# -*- coding: utf-8 -*-
"""Testes do classificador de aplicabilidade do REA (mitigação R1112)."""

from __future__ import annotations

from pathlib import Path

import pytest

from integrations.rea_applicability import (
    classify_surface,
    should_run_javascript_analysis,
)


def test_python_only_is_not_applicable(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")
    result = classify_surface(tmp_path)
    assert result["recommended_layer"] == "not_applicable"
    assert result["counts"]["python"] == 1
    assert result["counts"]["javascript"] == 0
    assert should_run_javascript_analysis(tmp_path) is False


def test_markdown_only_is_not_applicable(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# doc\n", encoding="utf-8")
    result = classify_surface(tmp_path)
    assert result["recommended_layer"] == "not_applicable"
    assert result["counts"]["markdown"] == 1


def test_javascript_app_is_applicable(tmp_path: Path) -> None:
    (tmp_path / "index.js").write_text("console.log('ok')\n", encoding="utf-8")
    result = classify_surface(tmp_path)
    assert result["recommended_layer"] == "javascript"
    assert result["counts"]["javascript"] == 1
    assert should_run_javascript_analysis(tmp_path) is True


def test_asar_is_applicable(tmp_path: Path) -> None:
    (tmp_path / "app.asar").write_bytes(b"not-a-real-asar")
    result = classify_surface(tmp_path)
    assert result["recommended_layer"] == "javascript"
    assert result["counts"]["asar"] == 1


def test_mixed_python_and_javascript_prefers_javascript(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "renderer.js").write_text("console.log('ok')\n", encoding="utf-8")
    assert classify_surface(tmp_path)["recommended_layer"] == "javascript"


def test_empty_directory_is_unknown(tmp_path: Path) -> None:
    result = classify_surface(tmp_path)
    assert result["recommended_layer"] == "unknown"
    assert should_run_javascript_analysis(tmp_path) is False


def test_node_modules_is_skipped(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")
    dependency = tmp_path / "node_modules" / "left-pad"
    dependency.mkdir(parents=True)
    (dependency / "index.js").write_text("module.exports = 1\n", encoding="utf-8")
    result = classify_surface(tmp_path)
    assert result["recommended_layer"] == "not_applicable"
    assert result["counts"]["javascript"] == 0


def test_file_target(tmp_path: Path) -> None:
    script = tmp_path / "index.js"
    script.write_text("console.log('ok')\n", encoding="utf-8")
    assert classify_surface(script)["recommended_layer"] == "javascript"


def test_missing_path_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        classify_surface(tmp_path / "missing")
