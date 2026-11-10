"""R1146 — gate de prova/contraprova complexa em Lean 4 + Mathlib."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from quantum_mitigation import complex_proof_gate as gate


def _compiled_stub(overrides=None):
    axioms = {
        name: ["propext", "Classical.choice", "Quot.sound"]
        for name in gate.REQUIRED_THEOREMS
    }
    if overrides:
        axioms.update(overrides)
    output = "\n".join(
        f"'CoreComplex.{name}' depends on axioms: [{', '.join(values)}]"
        for name, values in axioms.items()
    )
    return {
        "status": "compiled",
        "reason": None,
        "returncode": 0,
        "output": output,
        "elapsed_seconds": 0.0,
        "sha256": gate.sha256_file(gate.LEAN_FILE),
        "log_path": None,
    }


def test_scan_finds_theorems_and_counterproofs():
    source = gate.LEAN_FILE.read_text(encoding="utf-8")
    scan = gate.scan_source(source)
    assert scan["missing"] == []
    assert scan["forbidden"] == []
    assert set(gate.REQUIRED_THEOREMS) <= set(scan["theorems"])
    assert scan["counterproofs_missing"] == []
    assert all(scan["counterproof_shape"].values())


def test_parse_axioms_and_classification():
    output = "\n".join([
        "'CoreComplex.A' depends on axioms: [propext, Classical.choice, Quot.sound]",
        "'CoreComplex.B' depends on axioms: [propext, sorryAx]",
        "'CoreComplex.C' depends on axioms: [Lean.ofReduceBool]",
        "'CoreComplex.D' does not depend on any axioms",
    ])
    parsed = gate.parse_axioms(output)
    assert parsed["A"] == ["propext", "Classical.choice", "Quot.sound"]
    assert gate.classify_axioms(parsed["A"]) == "kernel_checked"
    assert gate.classify_axioms(parsed["B"]) == "blocked"
    assert gate.classify_axioms(parsed["C"]) == "native"
    assert gate.classify_axioms(parsed["D"]) == "kernel_checked"
    assert gate.classify_axioms(["Unknown.axiom"]) == "review_required"


def test_gate_accepts_consistent_claims_with_stubbed_compile():
    report = gate.audit(compilation=_compiled_stub(), run_compile=False)
    assert report["gate"]["accepted"] is True
    assert report["gate"]["blocked_claims"] == 0
    assert report["gate"]["unreported_theorems"] == []
    assert report["hardware_executed"] is False
    assert report["externally_validated"] is False
    assert report["confidence_promoted"] is False


def test_gate_rejects_missing_counterproof():
    claims = [{
        "id": "x",
        "theorem": "born_nonneg",
        "counterproof": "nao_existe",
        "kind": "probability",
    }]
    report = gate.audit(
        claims=claims, compilation=_compiled_stub(), run_compile=False
    )
    assert report["gate"]["accepted"] is False
    reasons = report["claims"][0]["reasons"]
    assert any("counterproof ausente" in reason for reason in reasons)


def test_gate_rejects_theorem_without_counterproof_field():
    claims = [{"id": "x", "theorem": "born_nonneg", "kind": "probability"}]
    report = gate.audit(
        claims=claims, compilation=_compiled_stub(), run_compile=False
    )
    assert report["gate"]["accepted"] is False
    assert any(
        "counterproof não declarada" in reason
        for reason in report["claims"][0]["reasons"]
    )


def test_gate_rejects_sorry_axiom():
    stub = _compiled_stub({"born_nonneg": ["propext", "sorryAx"]})
    report = gate.audit(compilation=stub, run_compile=False)
    assert report["gate"]["accepted"] is False
    assert report["axioms"]["born_nonneg"]["classification"] == "blocked"


def test_gate_rejects_native_axiom():
    stub = _compiled_stub({"phaseGate_unitary": ["Lean.ofReduceBool"]})
    report = gate.audit(compilation=stub, run_compile=False)
    assert report["gate"]["accepted"] is False
    assert report["axioms"]["phaseGate_unitary"]["classification"] == "native"


def test_gate_rejects_unreported_theorem():
    stub = _compiled_stub()
    lines = [
        line for line in stub["output"].splitlines()
        if "born_le_one" not in line
    ]
    stub["output"] = "\n".join(lines)
    report = gate.audit(compilation=stub, run_compile=False)
    assert report["gate"]["accepted"] is False
    assert "born_le_one" in report["gate"]["unreported_theorems"]


def test_gate_rejects_source_without_counterproof_shape():
    source = gate.LEAN_FILE.read_text(encoding="utf-8")
    broken = source.replace(
        "theorem no_negative_normSq :\n    ¬ ∃ z : ℂ, Complex.normSq z = -1",
        "theorem no_negative_normSq :\n    True",
    )
    scan = gate.scan_source(broken)
    assert scan["counterproof_shape"]["no_negative_normSq"] is False


@pytest.mark.skipif(
    os.environ.get("RUN_LEAN_COMPLEX") != "1" or shutil.which("lake") is None,
    reason="compilação Lean é job dedicado; defina RUN_LEAN_COMPLEX=1",
)
def test_complex_proofs_compile_and_gate_accepts():
    report = gate.audit(run_compile=True)
    assert report["compile"]["status"] == "compiled", report["compile"]
    assert report["compile"]["returncode"] == 0
    assert report["gate"]["accepted"] is True
