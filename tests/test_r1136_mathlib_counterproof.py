"""Prova Mathlib dedicada dos invariantes do CB (R1136)."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "lean" / "quantum-cb"
FILE = LEAN_DIR / "MathlibCounterproof.lean"
LOG = LEAN_DIR / "mathlib_compile.log"
README = LEAN_DIR / "README.md"


def test_files_and_scope():
    for path in (FILE, LOG, README):
        assert path.exists(), path
    text = FILE.read_text(encoding="utf-8")
    for name in ("D_mul_R", "rank_D", "B_mul_D_transpose", "C_mul_D_transpose", "C_independent"):
        assert f"theorem {name}" in text
    assert "sorry" not in text
    assert "admit" not in text
    log = LOG.read_text(encoding="utf-8")
    assert "'rank_D' depends on axioms" in log
    assert "does not prove the quantum channel" in text.lower() or "does not prove" in text.lower()


@pytest.mark.skipif(
    os.environ.get("RUN_MATHLIB_PROOF") != "1" or shutil.which("lake") is None,
    reason="prova Mathlib é job dedicado; defina RUN_MATHLIB_PROOF=1",
)
def test_mathlib_compiles():
    result = subprocess.run(
        [
            "lake",
            "env",
            "lean",
            "../../lean/quantum-cb/MathlibCounterproof.lean",
        ],
        cwd=ROOT / "livro-core" / "lean",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stderr[-4000:]
