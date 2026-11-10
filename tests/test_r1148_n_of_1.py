"""R1148 — N-of-1, lock de pré-registro e SCED."""
from __future__ import annotations

import pytest

from mci import n_of_1

PROTOCOL = {
    "protocol_id": "n1-001",
    "phases": [
        {"name": "baseline", "n": 5},
        {"name": "treatment", "n": 5},
    ],
    "primary_outcome": "offloading",
    "randomization": "blocked",
    "seed": 7,
    "analysis_plan": "NAP, PEM, Tau-U, permutação",
    "stopping_rule": "parar em evento adverso grave",
    "ethics": "consentimento aprovado",
}
OBSERVATIONS = [
    {"phase": "baseline", "value": 1},
    {"phase": "baseline", "value": 2},
    {"phase": "baseline", "value": 1},
    {"phase": "baseline", "value": 2},
    {"phase": "baseline", "value": 1},
    {"phase": "treatment", "value": 4},
    {"phase": "treatment", "value": 5},
    {"phase": "treatment", "value": 4},
    {"phase": "treatment", "value": 5},
    {"phase": "treatment", "value": 4},
]


def test_lock_is_deterministic_and_verifiable():
    first = n_of_1.lock_preregistration(PROTOCOL)
    second = n_of_1.lock_preregistration(PROTOCOL)
    assert first["hash"] == second["hash"]
    assert n_of_1.verify_lock(PROTOCOL, first["hash"]) is True
    assert n_of_1.verify_lock({**PROTOCOL, "seed": 8}, first["hash"]) is False
    with pytest.raises(ValueError):
        n_of_1.lock_preregistration({"protocol_id": "x"})


def test_sequence_is_balanced_and_deterministic():
    first = n_of_1.generate_sequence(PROTOCOL["phases"], seed=7)
    second = n_of_1.generate_sequence(PROTOCOL["phases"], seed=7)
    assert first == second
    assert first.count("baseline") == 5
    assert first.count("treatment") == 5


def test_clear_effect_is_detected():
    lock = n_of_1.lock_preregistration(PROTOCOL)
    report = n_of_1.run_n_of_1(
        PROTOCOL,
        OBSERVATIONS,
        lock["hash"],
        n_permutations=500,
        seed=3,
    )
    assert report["status"] == "analyzed"
    assert report["metrics"]["nap"] == pytest.approx(1.0)
    assert report["metrics"]["pem"] == pytest.approx(1.0)
    assert report["metrics"]["tau_u"]["tau_u"] == pytest.approx(1.0)
    assert report["metrics"]["permutation"]["p_value_one_sided"] < 0.05
    assert "não prova eficácia populacional" in report["limits"]


def test_tau_u_corrects_baseline_trend():
    result = n_of_1.tau_u([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
    assert result["tau_ab"] == pytest.approx(1.0)
    assert result["tau_baseline_trend"] == pytest.approx(1.0)
    assert result["tau_u"] == pytest.approx(0.0)


def test_decreasing_direction_inverts_pem_and_nap():
    baseline = [5, 5, 5, 5]
    treatment = [1, 2, 2, 1]
    assert n_of_1.nap(baseline, treatment, direction="decrease") == pytest.approx(1.0)
    assert n_of_1.pem(baseline, treatment, direction="decrease") == pytest.approx(1.0)
    assert n_of_1.pem(baseline, treatment, direction="increase") == pytest.approx(0.0)


def test_severe_adverse_event_halts_analysis():
    lock = n_of_1.lock_preregistration(PROTOCOL)
    observations = list(OBSERVATIONS)
    observations[5] = {
        "phase": "treatment",
        "value": 4,
        "adverse_event": {"severity": "severe", "description": "evento"},
    }
    report = n_of_1.run_n_of_1(
        PROTOCOL, observations, lock["hash"], n_permutations=200
    )
    assert report["status"] == "halted_adverse_event"
    assert report["analyzed"] is False


def test_lock_mismatch_blocks_analysis():
    report = n_of_1.run_n_of_1(
        PROTOCOL, OBSERVATIONS, "hash-errado", n_permutations=200
    )
    assert report["status"] == "lock_mismatch"
    assert report["analyzed"] is False


def test_insufficient_data_is_reported():
    lock = n_of_1.lock_preregistration(PROTOCOL)
    observations = OBSERVATIONS[:5]
    report = n_of_1.run_n_of_1(
        PROTOCOL, observations, lock["hash"], n_permutations=200
    )
    assert report["status"] == "insufficient_data"
    assert report["n_treatment"] == 0


def test_autocorrelation_is_flagged():
    values = [1, 2, 1, 2, 1, 2, 1, 2]
    assert abs(n_of_1.lag1_autocorrelation(values)) > 0.8
