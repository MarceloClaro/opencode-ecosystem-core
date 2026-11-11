"""R1148 — integração das cinco camadas metacognitivas."""
from __future__ import annotations

import json

from mci import claims_graph, ema, n_of_1, runtime_contract, trust_warrant

PSY = {
    "instrument": "Core Self-Report",
    "version": "1.0",
    "scale": "Likert 1-7",
    "reliability": {"omega": 0.82},
    "validity": {"construct": "autonomia", "notes": "fonte declarada"},
    "provenance": "doi:10.0000/exemplo",
    "license": "CC-BY-4.0",
}


def _certificate(tmp_path):
    payload = {
        "gate": {"accepted": True},
        "axioms": {
            "interference": {"classification": "kernel_checked"},
            "relative_phase_not_one": {"classification": "kernel_checked"},
        },
        "lean_file": {"sha256": "lean-hash"},
    }
    path = tmp_path / "certificate.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_five_layers_work_together(tmp_path):
    # 1. EMA
    schedule = ema.build_schedule(
        start_date="2026-11-10", days=1, prompts_per_day=5, seed=2
    )
    responses = [
        {"prompt_id": slot["prompt_id"], "value": 4} for slot in schedule
    ]
    ema_payload = ema.ema_report(
        schedule=schedule,
        responses=responses,
        psychometrics=PSY,
        baseline=[{"offloading": 2, "autonomy": 5} for _ in range(5)],
        followup=[{"offloading": 1, "autonomy": 6} for _ in range(5)],
        n_boot=300,
    )
    assert ema_payload["status"] == "ready_for_review"

    # 2. N-of-1
    protocol = {
        "protocol_id": "n1",
        "phases": [
            {"name": "baseline", "n": 5},
            {"name": "treatment", "n": 5},
        ],
        "primary_outcome": "offloading",
        "randomization": "blocked",
        "seed": 1,
        "analysis_plan": "NAP/PEM/Tau-U",
        "stopping_rule": "evento grave",
        "ethics": "consentimento",
    }
    lock = n_of_1.lock_preregistration(protocol)
    observations = [
        {"phase": "baseline", "value": value} for value in (1, 2, 1, 2, 1)
    ] + [
        {"phase": "treatment", "value": value} for value in (4, 5, 4, 5, 4)
    ]
    n1 = n_of_1.run_n_of_1(
        protocol, observations, lock["hash"], n_permutations=300
    )
    assert n1["status"] == "analyzed"
    assert n1["metrics"]["nap"] == 1.0

    # 3. Claims graph with formal, empirical, subjective and irreal nodes
    graph = claims_graph.ClaimsGraph()
    graph.add_claim("formal", "Interferência de duas fases.", kind="lemma")
    graph.add_formal_link(
        "formal",
        theorem_id="interference",
        counterproof_id="relative_phase_not_one",
        certificate_path=_certificate(tmp_path),
    )
    graph.add_claim("empirical", "A intervenção reduz offloading.", kind="empirical")
    graph.add_evidence("ev-real", domain="real", value=0.8)
    graph.add_edge("ev-real", "empirical", "supports", weight=0.9)
    graph.add_claim("subjective", "Sinto mais autonomia.", kind="subjective")
    graph.add_psychometric("subjective", PSY)
    graph.add_evidence("ev-subj", domain="real", value=0.7)
    graph.add_edge("ev-subj", "subjective", "supports", weight=0.9)
    graph.add_claim("irreal", "Simulação prevê ganho.", kind="empirical")
    graph.add_evidence(
        "ev-irreal",
        domain="irreal",
        value=0.9,
        synthetic=True,
        scenario="mundo A",
    )
    graph.add_edge("ev-irreal", "irreal", "supports", weight=0.9)

    assert graph.warrant("formal")["status"] == "formal_only"
    assert graph.warrant("empirical")["status"] == "supported"
    assert graph.warrant("subjective")["status"] == "subjective_review"
    assert graph.warrant("subjective")["abstain"] is True
    assert graph.warrant("irreal")["status"] == "simulation_only"

    # 4. Trust warrant: overconfident history abstains
    history = (
        [{"prediction": 0.9, "outcome": 1} for _ in range(21)]
        + [{"prediction": 0.9, "outcome": 0} for _ in range(9)]
    )
    trust = trust_warrant.trust_report(history, min_samples=20)
    assert trust["epistemic_warrant"]["status"] == "overconfident"
    assert trust["epistemic_warrant"]["abstain"] is True
    assert trust["coordination"]["n"] == 30

    # 5. Runtime contract: irreversible escalates; read_only executes
    contract = runtime_contract.RuntimeContract()
    contract.core_state.local_hour = 14
    escalated = contract.execute(
        {"action_id": "delete", "action_class": "irreversible"},
        lambda payload: "never",
    )
    assert escalated["status"] == "escalated"
    executed = contract.execute(
        {"action_id": "read", "action_class": "read_only"},
        lambda payload: 42,
    )
    assert executed["status"] == "executed"
    assert executed["result"] == 42
