"""Rotas offline: LRE para ZNE, desenho de layouts e gauge/PEC (R1132-R1134)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import quantum_mitigation.lre as lre
import quantum_mitigation.layout_design as layout
import quantum_mitigation.solution_audit as solution


def test_lagrange_and_lre_design():
    coefficients = lre.lagrange_coefficients((1, 2, 3), 0.0)
    np.testing.assert_allclose(coefficients, [3.0, -3.0, 1.0], atol=1e-12)
    assert coefficients.sum() == pytest.approx(1.0)
    design = lre.lre_design(2, scales=(1, 2, 3))
    assert design["n_configurations"] == 9
    assert design["sum_coefficients"] == pytest.approx(1.0)
    assert len(design["configurations"]) == len(design["coefficients"]) == 9


def test_lre_exact_for_multilinear_model():
    payload = lre.synthetic_audit(3)
    assert payload["lre_error"] < 1e-12
    assert payload["global_error"] < 1e-12
    assert payload["hardware_executed"] is False


def test_lre_rejects_invalid_scales():
    with pytest.raises(ValueError):
        lre.lagrange_coefficients((1, 1), 0.0)
    with pytest.raises(ValueError):
        lre.lre_design(0)


def test_paired_sample_size_and_randomization():
    small = layout.paired_sample_size(0.01, 0.02)
    large = layout.paired_sample_size(0.005, 0.02)
    assert small["n_pairs"] > 0
    assert large["n_pairs"] > small["n_pairs"]
    assignment = layout.randomized_assignment(9, seed=7)
    assert len(assignment) == 9
    assert assignment.count("AB") + assignment.count("BA") == 9
    assert assignment == layout.randomized_assignment(9, seed=7)


def test_layout_confound_and_preregistration():
    assert layout.confound_audit((0, 1), (0, 1), randomized=False)["allowed"] is True
    assert layout.confound_audit((0, 1), (106, 107), randomized=False)["allowed"] is False
    assert layout.confound_audit((0, 1), (106, 107), randomized=True)["allowed"] is True
    payload = layout.build_preregistration(
        n_pairs=2, effect=0.01, sigma=0.02, randomized=True
    )
    assert payload["enough_pairs"] is False
    assert payload["confound"]["allowed"] is True
    assert payload["hardware_submission_allowed"] is False
    assert len(payload["assignment"]) == 2


def test_gauge_invariance_of_learnable_functions():
    rates = {label: 0.002 for label in solution.PAULIS_2Q}
    payload = solution.cut_invariance(rates)
    assert payload["invariant_learnable"] is True
    assert payload["learnable_change"] < 1e-12
    assert payload["fidelity_change"] > 1e-12
    assert payload["changed_fidelities"] > 0


def test_pec_readiness_does_not_overclaim():
    payload = solution.pec_readiness()
    assert payload["direct_15_rate_pec_allowed"] is False
    assert "GSPN" in payload["route"]
    assert any("corte" in item for item in payload["not_claimed"])
    audit = solution.audit()
    assert audit["hardware_executed"] is False
    assert audit["rates_measured"] is False
    for path in (
        Path(solution.__file__),
        Path(lre.__file__),
        Path(layout.__file__),
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
            assert forbidden not in text


def test_harness_solution_audit(tmp_path):
    import importlib.util
    import json

    path = (
        Path(__file__).resolve().parents[1]
        / "harnesses/quantum-error-mitigation/solution_audit.py"
    )
    spec = importlib.util.spec_from_file_location("solution_audit_harness", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    out = tmp_path / "solutions.json"
    assert module.main(["--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["hardware_executed"] is False
    assert payload["lre"]["lre_error"] < 1e-12
    assert payload["gauge_pec"]["pec"]["direct_15_rate_pec_allowed"] is False
    assert payload["gates"]["pec_2q"]["allowed"] is False
    assert module.main(["--out", str(out)]) == 2
