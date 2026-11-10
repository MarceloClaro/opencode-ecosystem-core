"""R1148 — coordenação vs. warrant, Brier/ECE e abstenção."""
from __future__ import annotations

import pytest

from mci import trust_warrant


def test_brier_score_known_value():
    score = trust_warrant.brier_score(
        [0.9, 0.8, 0.7, 0.6], [1, 1, 0, 0]
    )
    assert score == pytest.approx(0.225)


def test_ece_detects_overconfidence():
    low = trust_warrant.expected_calibration_error(
        [0.05] * 10, [0] * 10
    )
    assert low["ece"] == pytest.approx(0.05)
    high = trust_warrant.expected_calibration_error(
        [0.95] * 10, [0] * 10
    )
    assert high["ece"] == pytest.approx(0.95)
    assert high["bins"][0]["gap"] == pytest.approx(0.95)


def test_coordination_score_is_separate():
    history = [
        {"prediction": 0.9, "outcome": 1 if index < 9 else 0}
        for index in range(10)
    ]
    coordination = trust_warrant.coordination_score(history)
    assert coordination["success_rate"] == pytest.approx(0.9)
    assert 0.7 < coordination["coordination_score"] < 0.9
    assert coordination["n"] == 10


def test_insufficient_data_forces_abstention():
    history = [
        {"prediction": 0.8, "outcome": 1} for _ in range(5)
    ]
    warrant = trust_warrant.epistemic_warrant(history, min_samples=20)
    assert warrant["status"] == "calibration_insufficient_data"
    assert warrant["warrant"] is None
    assert warrant["abstain"] is True


def test_calibrated_history_is_accepted():
    history = (
        [{"prediction": 0.7, "outcome": 1} for _ in range(28)]
        + [{"prediction": 0.7, "outcome": 0} for _ in range(12)]
    )
    warrant = trust_warrant.epistemic_warrant(history, min_samples=20)
    assert warrant["status"] == "calibrated"
    assert warrant["abstain"] is False
    assert warrant["warrant"] > 0.8
    assert warrant["ece"] < 0.05


def test_overconfident_history_abstains():
    history = (
        [{"prediction": 0.9, "outcome": 1} for _ in range(21)]
        + [{"prediction": 0.9, "outcome": 0} for _ in range(9)]
    )
    warrant = trust_warrant.epistemic_warrant(history, min_samples=20)
    assert warrant["status"] == "overconfident"
    assert warrant["abstain"] is True
    assert warrant["ece"] > 0.15
    assert warrant["bias"] > 0.1


def test_trust_report_keeps_both_scores():
    history = [
        {"prediction": 0.9, "outcome": 1 if index < 7 else 0}
        for index in range(30)
    ]
    report = trust_warrant.trust_report(history, min_samples=20)
    assert "coordination" in report
    assert "epistemic_warrant" in report
    assert report["coordination"]["n"] == 30
    assert report["epistemic_warrant"]["n"] == 30
    assert "não implica warrant" in report["separation_note"]


def test_empty_history_abstains():
    report = trust_warrant.trust_report([])
    assert report["coordination"]["coordination_score"] == 0.0
    assert report["epistemic_warrant"]["status"] == "calibration_insufficient_data"
    assert report["epistemic_warrant"]["abstain"] is True
