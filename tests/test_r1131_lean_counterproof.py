"""Contraprova Lean 4 dos invariantes finitos do CB (R1131)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "lean" / "quantum-cb"
LEAN_FILE = LEAN_DIR / "QuantumCB.lean"
README = LEAN_DIR / "README.md"
LOG = LEAN_DIR / "compile.log"


def test_files_exist():
    for path in (LEAN_FILE, README):
        assert path.exists(), path


def test_theorems_and_no_sorry():
    text = LEAN_FILE.read_text(encoding="utf-8")
    for name in (
        "D_mul_R",
        "B_mul_D_transpose",
        "C_mul_D_transpose",
        "C_independent",
        "design_rows",
        "cycle_rank",
        "cut_rank",
    ):
        assert f"theorem {name}" in text
    assert "sorry" not in text
    assert "admit" not in text
    assert "axiom " not in text


def test_readme_declares_scope_and_axioms():
    text = README.read_text(encoding="utf-8")
    assert "não é uma prova kernel-only" in text
    assert "native_decide" in text
    assert "hardware" in text.lower()


@pytest.mark.skipif(shutil.which("lean") is None, reason="Lean não instalado")
def test_lean_compiles():
    result = subprocess.run(
        ["lean", "QuantumCB.lean"],
        cwd=LEAN_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr[-4000:]
