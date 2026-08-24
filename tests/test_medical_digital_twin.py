# -*- coding: utf-8 -*-
from __future__ import annotations

from skills.medico_virtual_supremo.digital_twin import (
    MedicalDigitalTwinEngine,
    attach_digital_twin_to_simulation,
)


class FakeSwarm:
    def predict(self, question, signal=0.5, noise=0.12):
        return {
            "prediction_id": "pred-fixed",
            "aggregate": round(signal, 4),
            "consensus": 0.82,
            "n_agents": 15,
        }


def _engine():
    return MedicalDigitalTwinEngine(swarm=FakeSwarm(), seed=7)


def test_build_creates_versioned_simulation_twin():
    twin = _engine().build(
        run_id="run-1",
        request="Caso fictício com febre e tosse há 2 dias",
        patient={"age_years": 35, "sex_at_birth": "F"},
        clinical_data={"history": ["asma"], "vital_signs": {"temp": 38.1}, "lab_results": []},
        hypotheses=[{"name": "infecção respiratória", "status": "provável"}],
    ).to_dict()
    assert twin["simulation_only"] is True
    assert twin["model_contract"] == "medical-digital-twin/1.0"
    assert len(twin["trajectories"]) == 4
    assert twin["mirofish"]["engine"] == "MiroFishSwarm"
    assert twin["reversa_review"]["reviewer"] == "reversa-medical-adversarial"


def test_safety_blocks_clinical_use_and_prescription():
    twin = _engine().build(
        run_id="run-2",
        request="Caso simulado",
        patient={},
        clinical_data={},
        hypotheses=[],
    ).to_dict()
    assert twin["safety"]["clinical_use_allowed"] is False
    assert twin["safety"]["prescription_allowed"] is False
    assert twin["safety"]["diagnostic_claim_allowed"] is False
    assert twin["safety"]["human_review_required"] is True


def test_reversa_blocks_low_completeness():
    twin = _engine().build(
        run_id="run-3",
        request="Caso simulado incompleto",
        patient={},
        clinical_data={},
        hypotheses=[],
    ).to_dict()
    assert twin["reversa_review"]["decision"] == "block_clinical_use"
    assert any(f["code"] == "REV-DATA-001" for f in twin["reversa_review"]["findings"])


def test_source_hash_is_stable_for_same_payload():
    kwargs = dict(
        run_id="run-stable",
        request="Caso fictício estável",
        patient={"age_years": 50},
        clinical_data={"history": ["hipertensão"]},
        hypotheses=[{"name": "hipótese", "status": "alternativa"}],
    )
    assert _engine().build(**kwargs).source_hash == _engine().build(**kwargs).source_hash


def test_horizon_is_bounded():
    try:
        _engine().build(
            run_id="run-x", request="x", patient={}, clinical_data={}, hypotheses=[], horizon_steps=30
        )
    except ValueError as exc:
        assert "entre 2 e 12" in str(exc)
    else:
        raise AssertionError("horizon_steps inválido deveria falhar")


def test_attach_only_modifies_simulation_results():
    professional = {"resposta_medico_virtual_supremo": {"meta": {"mode": "professional_cds"}}}
    assert attach_digital_twin_to_simulation(
        professional, request="x", patient={}, clinical_data={}, engine=_engine()
    ) == professional


def test_attach_adds_twin_to_simulation():
    simulation = {
        "resposta_medico_virtual_supremo": {
            "meta": {"mode": "simulation", "run_id": "run-4"},
            "assessment": {"hypotheses": []},
        }
    }
    attached = attach_digital_twin_to_simulation(
        simulation, request="caso fictício", patient={}, clinical_data={}, engine=_engine()
    )
    assert attached["resposta_medico_virtual_supremo"]["digital_twin"]["run_id"] == "run-4"
