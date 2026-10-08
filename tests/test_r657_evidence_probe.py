"""A evidência da prova real não pode ignorar gates em Python otimizado."""
import subprocess
import sys
from pathlib import Path


def test_failed_evidence_gate_remains_active_in_optimized_python():
    result = subprocess.run(
        [sys.executable, "-O", "-c",
         "from scripts.verify_book_library import _require; _require(False, 'gate recusado')"],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        timeout=15,
    )
    assert result.returncode != 0
    assert "RuntimeError: gate recusado" in result.stderr
