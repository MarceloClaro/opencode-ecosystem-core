"""R1147 — correlações de erro, arranjos e contraprovas."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from quantum_mitigation import correlation_layout as cl

TABLE_A = {"00": 8000, "01": 500, "10": 500, "11": 1000}
TABLE_B = {"00": 7225, "01": 1275, "10": 1275, "11": 225}
PHI_A = (0.1 - 0.0225) / math.sqrt(0.15 * 0.85 * 0.15 * 0.85)


def test_calibration_detects_positive_correlation():
    result = cl.calibration_correlations(TABLE_A, [0, 1])
    assert result["marginals"] == pytest.approx([0.15, 0.15])
    pair = result["pairs"][0]
    assert pair["observed_joint"] == pytest.approx(0.1)
    assert pair["independent_joint"] == pytest.approx(0.0225)
    assert pair["phi"] == pytest.approx(PHI_A, rel=1e-6)
    assert result["any_error_probability"] == pytest.approx(0.2)
    assert result["independent_any_error"] == pytest.approx(0.2775)
    assert result["delta_any_error"] < 0
    assert result["all_zero_probability"] == pytest.approx(0.8)
    assert result["independent_no_error"] == pytest.approx(0.7225)
    assert result["delta_no_error"] > 0
    assert result["bounds"]["contain_observed"] is True
    assert result["correlation_class"] == "positive"
    assert result["hardware_executed"] is False


def test_same_marginals_different_joint():
    table_a = cl.calibration_correlations(TABLE_A, [0, 1])
    table_b = cl.calibration_correlations(TABLE_B, [0, 1])
    assert table_a["marginals"] == pytest.approx(table_b["marginals"])
    assert table_a["any_error_probability"] == pytest.approx(0.2)
    assert table_b["any_error_probability"] == pytest.approx(0.2775)
    assert table_a["pairs"][0]["phi"] > 0.5
    assert abs(table_b["pairs"][0]["phi"]) < 1e-9
    assert table_a["all_zero_probability"] > table_b["all_zero_probability"]


def test_simulated_readout_has_positive_phi():
    counts = cl.simulate_correlated_readout(
        n_qubits=4,
        marginals=[0.08] * 4,
        rho=0.6,
        shots=20000,
        seed=7,
    )
    result = cl.calibration_correlations(counts, [0, 1, 2, 3])
    assert result["max_abs_phi"] > 0.05
    assert result["bounds"]["contain_observed"] is True
    assert result["shots"] == 20000
    assert result["correlation_class"] == "positive"


def test_layout_cost_components():
    device = cl.make_device(
        n=3,
        edges=[(0, 1, 0.01), (1, 2, 0.01)],
        readout=[0.02, 0.03, 0.04],
        crosstalk=[(0, 1, 0.5)],
    )
    cost = cl.layout_cost((0, 1, 2), device, [(0, 1, 2.0)])
    assert cost["gate"] == pytest.approx(0.02)
    assert cost["readout"] == pytest.approx(0.09)
    assert cost["crosstalk"] == pytest.approx(1.0)
    assert cost["correlation"] == pytest.approx(0.0)
    assert cost["total"] == pytest.approx(
        cost["gate"] + cost["readout"] + cost["crosstalk"] + cost["correlation"]
    )


def test_greedy_and_exhaustive():
    device = cl.make_device(
        n=4,
        edges=[(0, 1, 0.01), (1, 2, 0.02), (2, 3, 0.01), (0, 3, 0.05)],
        readout=[0.01, 0.09, 0.02, 0.08],
    )
    interactions = [(0, 1, 3.0), (1, 2, 2.0), (2, 3, 1.0)]
    optimized = cl.optimize_layout(device, interactions)
    assert optimized["exhaustive"]["cost"] <= optimized["greedy"]["cost"] + 1e-9
    assert optimized["two_opt"]["cost"] <= optimized["greedy"]["cost"] + 1e-9


def test_greedy_counterexample_found():
    payload = cl.find_greedy_counterexample(n=5, trials=100, seed=0)
    assert payload["found"] is True
    assert payload["gap"] > 0
    assert payload["hardware_executed"] is False


def test_regime_reversal_found():
    payload = cl.find_regime_reversal(n=5, trials=50, seed=0)
    assert payload["found"] is True
    assert payload["gap"] > 0
    assert payload["gap_relative"] is not None


def test_correlation_blind_counterexample():
    payload = cl.correlation_blind_counterexample()
    assert payload["found"] is True
    assert payload["delta"] > 0
    assert payload["blind_cost"]["correlation"] > payload["aware_cost"]["correlation"]
    assert payload["blind_cost"]["gate"] == pytest.approx(
        payload["aware_cost"]["gate"]
    )
    assert payload["blind_cost"]["readout"] == pytest.approx(
        payload["aware_cost"]["readout"]
    )


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        cl.calibration_correlations({"0": 10}, [0])
    with pytest.raises(ValueError):
        cl.calibration_correlations({"00": -1}, [0, 1])
    with pytest.raises(ValueError):
        cl.simulate_correlated_readout(rho=1.5)
    with pytest.raises(ValueError):
        cl.layout_cost((0, 0), {"n": 2, "edges": [], "readout": [0.1, 0.1], "crosstalk": []}, [])


def test_module_has_no_hardware_calls():
    text = Path(cl.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "submit_optimized",
        "connect_gjq",
        "GJQ_API_KEY",
        "allow_hardware",
        "confirm=True",
    ):
        assert forbidden not in text
