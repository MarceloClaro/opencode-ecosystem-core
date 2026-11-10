"""R1145 — escala amostral, bootstrap, curva de aprendizado e ruído."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import quantum_research.classification as classification
import quantum_research.cooking as cooking


def test_bootstrap_ci_is_bounded_and_degenerate_when_perfect():
    perfect = {"tp": 8, "tn": 8, "fp": 0, "fn": 0}
    payload = classification.bootstrap_accuracy_ci(perfect, n_boot=500, seed=1)
    assert payload["ci_low"] == pytest.approx(1.0)
    assert payload["ci_high"] == pytest.approx(1.0)
    assert payload["n_test"] == 16

    mixed = {"tp": 6, "tn": 6, "fp": 2, "fn": 2}
    payload = classification.bootstrap_accuracy_ci(mixed, n_boot=2000, seed=1)
    assert 0.0 <= payload["ci_low"] <= payload["accuracy"] <= payload["ci_high"] <= 1.0
    assert payload["ci_high"] - payload["ci_low"] > 0.0
    with pytest.raises(ValueError):
        classification.bootstrap_accuracy_ci({"tp": 0, "tn": 0, "fp": 0, "fn": 0})
    with pytest.raises(ValueError):
        classification.bootstrap_accuracy_ci(mixed, confidence=1.5)


def test_improved_audit_reports_confusion():
    payload = classification.improved_audit(n_per_class=8, seed=3, noise=0.15)
    for name in ("quantum", "projected", "classical"):
        row = payload[name]
        total = sum(row["test_confusion"].values())
        assert total == payload["n_test"]
        assert 0.0 <= row["test_accuracy"] <= 1.0
    assert payload["selection"].startswith("validação")


def test_benchmark_improved_has_pooled_ci():
    payload = classification.benchmark_improved(
        n_per_class=6,
        noise=0.3,
        seeds=(42, 43),
        bootstrap=200,
    )
    assert payload["bootstrap"]["n_boot"] == 200
    for name in ("quantum", "projected", "classical"):
        summary = payload["summary"][name]
        assert summary["ci_low"] <= summary["pooled_accuracy"] <= summary["ci_high"]
        assert len(summary["cis"]) == 2
        assert summary["cis"][0]["n_test"] == summary["cis"][1]["n_test"]


def test_learning_curve_structure_and_exponent():
    payload = classification.learning_curve(
        per_class_sizes=(6, 12),
        seeds=(42,),
        noise=0.5,
        bootstrap=200,
    )
    assert payload["caro_prediction_exponent"] == pytest.approx(0.5)
    assert len(payload["points"]) == 2
    for point in payload["points"]:
        assert point["leakage"]["disjoint"] is True
        assert point["n_train"] > 0
        assert 0.0 <= point["quantum"]["pooled_accuracy"] <= 1.0
        assert 0.0 <= point["quantum"]["mean_test_accuracy"] <= 1.0
        assert point["quantum"]["ci_low"] <= point["quantum"]["pooled_accuracy"]
        assert point["quantum"]["pooled_accuracy"] <= point["quantum"]["ci_high"]
    assert "não valida" in payload["interpretation"]
    with pytest.raises(ValueError):
        classification.learning_curve(per_class_sizes=(4,), seeds=(42,), noise=0.1)


def test_noisy_kernel_audit_reports_degradation_and_model():
    payload = classification.noisy_kernel_audit(
        n_per_class=8,
        seed=3,
        noise=0.2,
        shots=256,
        readout_error=0.05,
        selection="exact",
    )
    assert payload["shots"] == 256
    assert payload["readout_model"]["symmetric"] is True
    assert payload["readout_model"]["e01"] == payload["readout_model"]["e10"] == 0.05
    assert 0.0 <= payload["exact_test_accuracy"] <= 1.0
    assert 0.0 <= payload["noisy_test_accuracy"] <= 1.0
    assert payload["mean_abs_kernel_error"] >= 0.0
    assert payload["hardware_executed"] is False
    assert payload["selection_basis"].startswith("kernel exato")


def test_noisy_kernel_converges_with_many_shots():
    payload = classification.noisy_kernel_audit(
        n_per_class=8,
        seed=5,
        noise=0.15,
        shots=100_000,
        readout_error=0.0,
        selection="exact",
    )
    assert payload["mean_abs_kernel_error"] < 0.02
    assert payload["noisy_test_accuracy"] == pytest.approx(
        payload["exact_test_accuracy"], abs=0.15
    )


def test_noisy_kernel_uses_noisy_selection():
    payload = classification.noisy_kernel_audit(
        n_per_class=8,
        seed=3,
        noise=0.2,
        shots=1024,
        readout_error=0.02,
    )
    assert payload["selection"] == "noisy"
    assert payload["selection_basis"].startswith("validação com kernel ruidoso")
    assert payload["config"]["ridge"] in (0.01, 0.1, 1.0)
    assert payload["ci_low"] <= payload["noisy_test_accuracy"] <= payload["ci_high"]


def test_noise_sweep_reuses_selection():
    payload = classification.noise_sweep(
        n_per_class=8,
        seeds=(42,),
        noise=0.15,
        shots=(256, 4096),
        readout_errors=(0.0, 0.05),
        bootstrap=200,
    )
    assert len(payload["rows"]) == 4
    assert payload["seeds"] == [42]
    assert payload["hardware_executed"] is False
    for row in payload["rows"]:
        assert row["seed"] == 42
        assert row["shots"] in (256, 4096)
        assert row["readout_model"]["e01"] == row["readout_model"]["e10"]
        assert row["ci_low"] <= row["noisy_test_accuracy"] <= row["ci_high"]


def test_qaoa_budget_and_exact_solver():
    exhausted = cooking.qaoa_audit(
        depths=(1,),
        restarts=1,
        maxiter=20,
        max_evaluations_per_depth=3,
    )
    assert exhausted["depths"][0]["status"] == "budget_exhausted"
    assert exhausted["completed_depths"] == []
    assert exhausted["qaoa_energy"] is None
    assert exhausted["exact_solver"]["method"].startswith("enumeração")
    assert exhausted["exact_solver"]["energy"] == pytest.approx(-2.6)

    payload = cooking.qaoa_audit(
        depths=(1, 4),
        restarts=1,
        maxiter=40,
        max_evaluations_per_depth=2000,
    )
    assert payload["completed_depths"] == [1, 4]
    p4 = payload["depths"][-1]
    assert p4["reps"] == 4
    assert p4["energy"] >= payload["exact_energy"] - 1e-9
    assert 0.0 <= p4["approximation_ratio"] <= 1.0
    assert payload["gap"] == pytest.approx(payload["qaoa_energy"] - payload["exact_energy"])
    assert "não demonstram escala" in payload["scale_limits"]


def test_new_code_has_no_hardware_calls():
    for path in (
        Path(classification.__file__),
        Path(cooking.__file__),
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in (
            "submit_optimized",
            "connect_gjq",
            "GJQ_API_KEY",
            "allow_hardware",
            "confirm=True",
        ):
            assert forbidden not in text
