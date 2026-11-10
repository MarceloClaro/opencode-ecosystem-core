"""Twirl/frame, ruído 1q nas correções e pré-registro (R1130)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from qiskit.quantum_info import Pauli, Statevector

import quantum_mitigation.interleaved_cb as icb


def _rates():
    return {label: 0.001 + 0.0002 * index for index, label in enumerate(icb.PAULIS_2Q)}


def test_twirl_frames_and_ideal_equivalence():
    body, frames = icb.cycle_body_framed(("XX",), 2, twirl=True, seed=7)
    assert len(frames) == 2
    assert all(frame["twirls"] for frame in frames)
    value = Statevector.from_instruction(body).expectation_value(Pauli("XX")).real
    assert value == pytest.approx(1.0, abs=1e-10)
    plain = icb.cycle_body(("XX",), 2)
    assert plain.count_ops().get("cz", 0) == 2


def test_twirl_preserves_exact_recovery():
    payload = icb.audit(rates=_rates(), twirl=True, seed=3)
    assert payload["n_recovered"] == 13
    assert payload["max_absolute_error"] < 1e-10
    assert payload["twirl"] is True


def test_correction_noise_degrades_but_keeps_fit():
    clean = icb.recover_function(("XX",), _rates(), correction_rate=0.0)
    noisy = icb.recover_function(("XX",), _rates(), correction_rate=0.005)
    assert clean["absolute_error"] < 1e-10
    assert noisy["absolute_error"] > 1e-4
    assert noisy["fit"]["status"] == "fit"


def test_noise_audit_reports_two_settings():
    payload = icb.noise_audit(
        _rates(),
        correction_rates=(0.0, 0.005),
        twirl_values=(True,),
        seed=3,
    )
    assert len(payload["results"]) == 2
    clean, noisy = payload["results"]
    assert clean["max_absolute_error"] < 1e-10
    assert noisy["max_absolute_error"] > 1e-4
    assert clean["n_recovered"] == noisy["n_recovered"] == 13
    assert payload["hardware_executed"] is False


def test_preregistration_is_deterministic_and_fail_closed():
    first = icb.build_preregistration()
    second = icb.build_preregistration()
    assert first == second
    assert first["jobs"] == 13 * 5 * 5
    assert first["total_shots"] == first["jobs"] * first["shots"]
    assert first["hardware_submission_allowed"] is False
    assert first["analysis_allowed"] is False
    assert len(first["manifest_sha256"]) == 64
    icb.validate_preregistration(first)
    tampered = copy.deepcopy(first)
    tampered["shots"] = 8192
    with pytest.raises(ValueError):
        icb.validate_preregistration(tampered)


def test_harness_preregister_command(tmp_path):
    import importlib.util

    path = (
        Path(__file__).resolve().parents[1]
        / "harnesses/quantum-error-mitigation/cb_protocol.py"
    )
    spec = importlib.util.spec_from_file_location("cb_protocol_prereg", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    out = tmp_path / "prereg.json"
    assert module.main(["preregister", "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["hardware_submission_allowed"] is False
    assert module.main(["preregister", "--out", str(out)]) == 2


def test_no_hardware_or_secret_strings():
    text = Path(icb.__file__).read_text(encoding="utf-8")
    for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
        assert forbidden not in text
