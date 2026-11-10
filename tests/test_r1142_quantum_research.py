"""Classificação quântica e cozimento como otimização (R1142-R1143)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import quantum_research.classification as classification
import quantum_research.cooking as cooking


def test_circles_and_kernel():
    X, y = classification.make_circles(n_per_class=6, seed=3)
    assert X.shape == (12, 2)
    assert set(y) == {0, 1}
    qc = classification.feature_map(X[0])
    assert qc.num_qubits == 2
    assert classification.quantum_kernel_entry(X[0], X[0]) == pytest.approx(1.0, abs=1e-9)
    assert classification.quantum_kernel_entry(X[0], X[1]) == pytest.approx(
        classification.quantum_kernel_entry(X[1], X[0]), abs=1e-12
    )


def test_classification_audit_and_leakage():
    payload = classification.audit(n_per_class=8, seed=5)
    assert 0.0 <= payload["quantum_accuracy"] <= 1.0
    assert 0.0 <= payload["classical_accuracy"] <= 1.0
    assert payload["leakage"]["disjoint"] is True
    assert payload["hardware_executed"] is False
    overlap = classification.leakage_audit(np.array([[0.0, 0.0]]), np.array([[0.0, 0.0]]))
    assert overlap["disjoint"] is False


def test_cooking_qubo_and_bruteforce():
    assert cooking.energy((0, 0, 0, 0)) == pytest.approx(0.0)
    exact = cooking.brute_force()
    assert exact["energy"] < 0
    assert len(exact["bits"]) == 4
    assert cooking.energy(exact["bits"]) == pytest.approx(exact["energy"])


def test_qaoa_audit_is_synthetic_and_bounded():
    payload = cooking.qaoa_audit(
        maxiter=80, seed=7, depths=(1, 2), restarts=2
    )
    assert payload["synthetic"] is True
    assert payload["hardware_executed"] is False
    assert payload["qaoa_energy"] >= payload["exact_energy"] - 1e-9
    assert len(payload["qaoa_bits"]) == 4
    assert payload["qaoa_reps"] in (1, 2)
    assert 0.0 <= payload["approximation_ratio"] <= 1.0
    assert "não prova vantagem" in payload["limits"]


def test_improved_classification_uses_validation_selection():
    payload = classification.improved_audit(
        n_per_class=8, seed=3, noise=0.15
    )
    assert payload["selection"] == "validação; teste não participa da escolha"
    assert 0.0 <= payload["quantum"]["test_accuracy"] <= 1.0
    assert 0.0 <= payload["projected"]["test_accuracy"] <= 1.0
    assert 0.0 <= payload["classical"]["test_accuracy"] <= 1.0
    assert payload["hardware_executed"] is False


def test_no_hardware_strings():
    for path in (Path(classification.__file__), Path(cooking.__file__)):
        text = path.read_text(encoding="utf-8")
        for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
            assert forbidden not in text
