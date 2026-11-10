"""R1147 — gate de contraprovas de correlação."""
from __future__ import annotations

import os
import shutil

import pytest

from quantum_mitigation import correlation_gate as gate


def _compiled_stub(overrides=None):
    axioms = {
        name: ["propext", "Classical.choice", "Quot.sound"]
        for name in gate.CORRELATION_REQUIRED
    }
    if overrides:
        axioms.update(overrides)
    output = "\n".join(
        f"'CoreCorrelation.{name}' depends on axioms: [{', '.join(values)}]"
        for name, values in axioms.items()
    )
    return {
        "status": "compiled",
        "reason": None,
        "returncode": 0,
        "output": output,
        "elapsed_seconds": 0.0,
        "sha256": gate.base.sha256_file(gate.CORRELATION_FILE),
        "log_path": None,
    }


def test_scan_finds_theorems_and_counterproofs():
    scan = gate.base.scan_source(
        gate.CORRELATION_FILE.read_text(encoding="utf-8"),
        required_theorems=gate.CORRELATION_REQUIRED,
        counterproofs=gate.CORRELATION_COUNTERPROOFS,
    )
    assert scan["missing"] == []
    assert scan["forbidden"] == []
    assert scan["counterproofs_missing"] == []
    assert all(scan["counterproof_shape"].values())


def test_gate_accepts_correlation_claims_with_stubbed_compile():
    report = gate.audit(compilation=_compiled_stub(), run_compile=False)
    assert report["gate"]["accepted"] is True
    assert report["round"] == "R1147"
    assert report["gate"]["blocked_claims"] == 0
    assert report["hardware_executed"] is False


def test_gate_rejects_missing_counterproof():
    claims = [{
        "id": "x",
        "theorem": "no_error_A_gt_B",
        "counterproof": "nao_existe",
        "kind": "direction",
    }]
    report = gate.audit(
        claims=claims, compilation=_compiled_stub(), run_compile=False
    )
    assert report["gate"]["accepted"] is False
    reasons = report["claims"][0]["reasons"]
    assert any("counterproof ausente" in reason for reason in reasons)


def test_gate_rejects_sorry_axiom():
    stub = _compiled_stub(
        {"covariance_A_positive": ["propext", "sorryAx"]}
    )
    report = gate.audit(compilation=stub, run_compile=False)
    assert report["gate"]["accepted"] is False
    assert (
        report["axioms"]["covariance_A_positive"]["classification"]
        == "blocked"
    )


def test_gate_rejects_native_axiom():
    stub = _compiled_stub(
        {"any_error_A_lt_B": ["Lean.ofReduceBool"]}
    )
    report = gate.audit(compilation=stub, run_compile=False)
    assert report["gate"]["accepted"] is False
    assert report["axioms"]["any_error_A_lt_B"]["classification"] == "native"


@pytest.mark.skipif(
    os.environ.get("RUN_LEAN_CORRELATION") != "1"
    or shutil.which("lake") is None,
    reason="compilação Lean é job dedicado; defina RUN_LEAN_CORRELATION=1",
)
def test_correlation_proofs_compile_and_gate_accepts():
    report = gate.audit(run_compile=True)
    assert report["compile"]["status"] == "compiled", report["compile"]
    assert report["compile"]["returncode"] == 0
    assert report["gate"]["accepted"] is True
