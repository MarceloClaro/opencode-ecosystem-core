"""SPEC-985 — dependências locais explícitas para a reprodução OdontoCA."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RUNTIME_PINS = {
    "numpy": "2.5.1",
    "pandas": "3.0.3",
    "scikit-learn": "1.9.0",
    "openpyxl": "3.1.5",
    "opencv-python-headless": "5.0.0.93",
    "joblib": "1.5.3",
}


def _pins(path: Path) -> dict[str, str]:
    result = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "==" in line:
            name, version = line.split("==", 1)
            result[name.strip().lower()] = version.strip()
    return result


def test_runtime_manifest_pins_model_environment_and_xlsx_engine():
    pins = _pins(ROOT / "requirements.txt")
    assert pins == EXPECTED_RUNTIME_PINS
    card = json.loads((ROOT.parent / "submission_package" / "odontoca_clinical_model_card.json").read_text(encoding="utf-8"))
    assert pins["numpy"] == card["versions"]["numpy"]
    assert pins["pandas"] == card["versions"]["pandas"]
    assert pins["scikit-learn"] == card["versions"]["scikit_learn"]


def test_development_manifest_reuses_runtime_pins_and_declares_pytest():
    lines = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
    assert "-r requirements.txt" in lines
    assert "pytest==9.1.1" in lines


def test_readme_explains_reproducible_setup_and_no_implicit_download():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "pip install -r requirements.txt" in text
    assert "não" in text and "download" in text
