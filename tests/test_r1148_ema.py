"""R1148 — EMA com compliance, faltantes e transferência."""
from __future__ import annotations

import pytest

from mci import ema

PSY = {
    "instrument": "Core Self-Report",
    "version": "1.0",
    "scale": "Likert 1-7",
    "reliability": {"omega": 0.82, "alpha": 0.80},
    "validity": {
        "construct": "autonomia e offloading",
        "notes": "validade de construto relatada na fonte",
    },
    "provenance": "doi:10.0000/exemplo",
    "license": "CC-BY-4.0",
}


def test_schedule_is_deterministic_and_complete():
    first = ema.build_schedule(
        start_date="2026-11-10", days=3, prompts_per_day=4, seed=7
    )
    second = ema.build_schedule(
        start_date="2026-11-10", days=3, prompts_per_day=4, seed=7
    )
    assert first == second
    assert len(first) == 12
    assert len({slot["prompt_id"] for slot in first}) == 12
    assert all("scheduled_at" in slot for slot in first)
    with pytest.raises(ValueError):
        ema.build_schedule(start_date="2026-11-10", days=0, prompts_per_day=4)


def test_compliance_counts_missing_prompts():
    schedule = ema.build_schedule(
        start_date="2026-11-10", days=1, prompts_per_day=4, seed=1
    )
    responses = [
        {"prompt_id": schedule[0]["prompt_id"], "value": 5},
        {"prompt_id": schedule[1]["prompt_id"], "value": 4},
        {"prompt_id": schedule[2]["prompt_id"], "answered": False},
    ]
    report = ema.record_responses(schedule, responses)
    assert report["scheduled"] == 4
    assert report["answered"] == 2
    assert report["missing"] == 2
    assert report["compliance_rate"] == pytest.approx(0.5)
    assert report["imputation"] == "none"
    assert schedule[3]["prompt_id"] in report["missing_prompt_ids"]


def test_psychometric_metadata_is_mandatory():
    assert ema.validate_psychometrics(PSY)["valid"] is True
    missing = ema.validate_psychometrics({"instrument": "x"})
    assert missing["valid"] is False
    assert "reliability" in missing["missing"]
    weak = ema.validate_psychometrics({
        **PSY,
        "reliability": {"omega": 0.4},
    })
    assert weak["valid"] is True
    assert any("abaixo de 0,6" in warning for warning in weak["warnings"])


def test_transfer_test_distinguishes_dependent_and_autonomous():
    baseline = [
        {"offloading": value, "autonomy": 5.0}
        for value in (2, 3, 2, 3, 2)
    ]
    followup_dependent = [
        {"offloading": value, "autonomy": 2.0}
        for value in (6, 7, 6, 7, 6)
    ]
    dependent = ema.paired_transfer_test(
        baseline, followup_dependent, n_boot=500, seed=3
    )
    assert dependent["classification"] == "dependent"
    assert dependent["delta_offloading"]["mean"] > 0
    assert dependent["delta_autonomy"]["mean"] < 0

    followup_autonomous = [
        {"offloading": value, "autonomy": 6.0}
        for value in (1, 1, 2, 1, 1)
    ]
    autonomous = ema.paired_transfer_test(
        baseline, followup_autonomous, n_boot=500, seed=3
    )
    assert autonomous["classification"] == "autonomous"
    assert autonomous["delta_offloading"]["mean"] < 0
    assert autonomous["delta_autonomy"]["mean"] > 0


def test_ema_report_blocks_without_psychometrics():
    schedule = ema.build_schedule(
        start_date="2026-11-10", days=1, prompts_per_day=4, seed=1
    )
    responses = [
        {"prompt_id": slot["prompt_id"], "value": 4}
        for slot in schedule
    ]
    report = ema.ema_report(
        schedule=schedule,
        responses=responses,
        psychometrics=None,
    )
    assert report["status"] == "blocked"
    assert report["clinical_validation"] is False


def test_ema_report_ready_for_review():
    schedule = ema.build_schedule(
        start_date="2026-11-10", days=1, prompts_per_day=5, seed=1
    )
    responses = [
        {"prompt_id": slot["prompt_id"], "value": 4}
        for slot in schedule
    ]
    baseline = [{"offloading": 2, "autonomy": 5} for _ in range(5)]
    followup = [{"offloading": 1, "autonomy": 6} for _ in range(5)]
    report = ema.ema_report(
        schedule=schedule,
        responses=responses,
        psychometrics=PSY,
        baseline=baseline,
        followup=followup,
        n_boot=500,
    )
    assert report["status"] == "ready_for_review"
    assert report["compliance"]["compliance_rate"] == pytest.approx(1.0)
    assert report["transfer"]["classification"] == "autonomous"
    assert "não substitui validação clínica" in report["limits"]
