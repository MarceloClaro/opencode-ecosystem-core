"""Gates revisados e fail-closed (R1135)."""
from __future__ import annotations

from pathlib import Path

import quantum_mitigation.gate_policy as gates


def test_empty_evidence_blocks_all():
    payload = gates.evaluate({})
    for name in ("pec_2q", "zne", "layout", "cuts"):
        assert payload[name]["allowed"] is False
        assert payload[name]["reasons"]
    assert payload["hardware_executed"] is False


def test_pec_gate_pass_and_fail():
    passed = gates.pec_gate(
        gspn_model_validated=True,
        heldout_error=0.005,
        sampling_overhead=5.0,
    )
    assert passed["allowed"] is True
    assert passed["cuts_identified_required"] is False
    failed = gates.pec_gate(
        gspn_model_validated=False,
        heldout_error=0.02,
        sampling_overhead=20.0,
    )
    assert failed["allowed"] is False
    assert len(failed["reasons"]) == 3


def test_zne_gate_pass_and_fail():
    passed = gates.zne_gate(
        lre_configurations=27,
        residual=0.002,
        heldout_stable=True,
    )
    assert passed["allowed"] is True
    assert passed["monotonic_global_required"] is False
    failed = gates.zne_gate(
        lre_configurations=3,
        residual=0.02,
        heldout_stable=False,
    )
    assert failed["allowed"] is False


def test_layout_gate_pass_and_r1_fail():
    passed = gates.layout_gate(
        n_pairs=32,
        n_required=32,
        randomized=True,
        r1=0.04,
        drift_resolved=True,
        effect=0.02,
    )
    assert passed["allowed"] is True
    failed = gates.layout_gate(
        n_pairs=32,
        n_required=32,
        randomized=True,
        r1=0.08,
        drift_resolved=True,
        effect=0.02,
    )
    assert failed["allowed"] is False
    assert any("r1" in reason for reason in failed["reasons"])


def test_cuts_are_gauge_not_direct_identification():
    passed = gates.cut_gate(
        gspn_self_consistent=True,
        mlcb_applied=True,
    )
    assert passed["allowed"] is True
    assert passed["identified"] is False
    failed = gates.cut_gate(
        gspn_self_consistent=False,
        mlcb_applied=False,
    )
    assert failed["allowed"] is False


def test_no_hardware_strings():
    text = Path(gates.__file__).read_text(encoding="utf-8")
    for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
        assert forbidden not in text
