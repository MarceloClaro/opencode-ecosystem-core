"""Roteador de gates bloqueados (R1138)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "harnesses/quantum-error-mitigation/gate_router.py"


def _module():
    spec = importlib.util.spec_from_file_location("gate_router", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_route_is_fail_closed_and_has_sources():
    payload = _module().route("pec_2q")
    assert payload["status"]["allowed"] is False
    assert "GSPN" in payload["route"]
    assert "gspn_model_validated" in payload["required_evidence"]
    assert payload["hardware_executed"] is False


def test_route_accepts_evidence(tmp_path):
    module = _module()
    evidence = tmp_path / "evidence.json"
    evidence.write_text(
        json.dumps(
            {
                "pec_2q": {
                    "gspn_model_validated": True,
                    "heldout_error": 0.005,
                    "sampling_overhead": 5.0,
                }
            }
        ),
        encoding="utf-8",
    )
    payload = module.route("pec_2q", json.loads(evidence.read_text(encoding="utf-8")))
    assert payload["status"]["allowed"] is True


def test_cli_writes_new_file(tmp_path):
    module = _module()
    out = tmp_path / "route.json"
    assert module.main(["--gate", "zne", "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["gate"] == "zne"
    assert payload["status"]["allowed"] is False
    assert module.main(["--gate", "zne", "--out", str(out)]) == 2


def test_invalid_gate():
    with pytest.raises(SystemExit):
        _module().main(["--gate", "unknown"])
