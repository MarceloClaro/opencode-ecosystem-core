"""R1150 — N-of-1 unificado em core_cognition (validador + runner)."""
from __future__ import annotations

import core_cognition.n_of_1 as canonical
import mci.n_of_1 as compatibility


def test_compatibility_module_reexports_canonical_runner():
    assert compatibility.run_n_of_1 is canonical.run_n_of_1
    assert compatibility.lock_preregistration is canonical.lock_preregistration
    assert compatibility.verify_lock is canonical.verify_lock
    assert compatibility.nap is canonical.nap
    assert compatibility.pem is canonical.pem
    assert compatibility.tau_u is canonical.tau_u
    assert compatibility.permutation_test_nap is canonical.permutation_test_nap
    assert compatibility.LIMITS == canonical.LIMITS
    assert compatibility.SCED_LIMITS == canonical.SCED_LIMITS


def test_validator_and_runner_coexist_in_single_module():
    validated = canonical.validate_protocol(canonical.template())
    assert validated.duration_weeks == 12
    assert validated.randomization is True

    protocol = {
        "protocol_id": "n1-r1150",
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
    lock = canonical.lock_preregistration(protocol)
    observations = [
        {"phase": "baseline", "value": value} for value in (1, 2, 1, 2, 1)
    ] + [
        {"phase": "treatment", "value": value} for value in (4, 5, 4, 5, 4)
    ]
    report = canonical.run_n_of_1(
        protocol, observations, lock["hash"], n_permutations=300
    )
    assert report["status"] == "analyzed"
    assert report["metrics"]["nap"] == 1.0
