from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from integrations import quantum_research as qr  # noqa: E402


def _complete_payload():
    return {
        "schema_version": 1,
        "question": "Comparar estratégias em instâncias pequenas.",
        "application_label": "CA",
        "problem_class": "constraint_optimization",
        "objective": "minimize_cost",
        "constraints": ["capacity"],
        "baseline_methods": ["enumeration"],
        "evaluation_metrics": ["objective", "runtime"],
        "evidence_refs": ["local:problem-contract-v1"],
        "candidate_methods": ["quantum_cellular_automata"],
        "method_inputs": {
            "quantum_cellular_automata": [
                "state_space",
                "local_rule",
                "boundary_conditions",
                "evolution_validity",
                "comparison_baseline",
            ]
        },
        "resource_limits": {
            "qubits": 8,
            "shots": 512,
            "simulator_memory_gib": 4,
            "runtime_seconds": 30,
        },
    }


def test_catalog_covers_nisq_methods_and_preserves_tiangong_labels():
    catalog = qr.research_catalog()
    method_ids = {row["id"] for row in catalog["methods"]}
    assert {
        "classical_baselines",
        "hybrid_variational",
        "classical_simulation",
        "quantum_annealing",
        "quantum_cellular_automata",
        "error_mitigation",
    } <= method_ids

    apps = qr.tiangong_application_catalog()
    assert [row["label"] for row in apps] == [
        "VRP", "WSA", "HDR", "QSS", "OPC", "PTO", "CA", "RSA", "ECC", "SDES"
    ]
    assert all(row["source_semantics"] == "unverified" for row in apps)
    assert next(row for row in apps if row["label"] == "CA")["label"] == "CA"
    assert next(row for row in apps if row["label"] == "VRP")["local_harness_status"] == "classical_only"
    assert next(row for row in apps if row["label"] == "HDR")["local_harness_status"] == "preprocessing_only"
    routes = {row["id"] for row in catalog["existing_local_routes"]}
    assert {"qubo_ising_qaoa_planning", "vrp_classical_baseline", "hdr_preprocessing"} <= routes


def test_user_supplied_tiangong_resources_are_unverified_and_non_executable():
    snapshot_fn = getattr(qr, "tiangong_resource_snapshot", None)
    assert callable(snapshot_fn), "snapshot de recursos declarado pelo usuário não foi integrado"
    if not callable(snapshot_fn):
        return
    snapshot = snapshot_fn()
    assert snapshot["provenance"] == "user_supplied"
    assert snapshot["verification"] == "not_independently_verified"
    assert snapshot["submission_authorized"] is False
    inventory = {row["backend"]: row for row in snapshot["inventory"]}
    assert len(inventory) == 19
    assert inventory["Guoji No.1"]["reported_status"] == "Maintenance"
    assert inventory["Guoji No.1"]["qubits"] == 20
    assert inventory["Baihua"]["t2_mean_us"] == pytest.approx(26.36)
    assert inventory["Guoji No.8（simulate）"]["resource_type"] == "simulator"
    assert inventory["MPS Simulator"]["qubits"] == 997
    assert inventory["MPS Simulator"]["jobs_reported"] == 51
    assert all(row["availability_assessed"] is False for row in inventory.values())


def test_plan_is_gap_aware_deterministic_and_never_claims_execution():
    payload = _complete_payload()
    first = qr.build_research_plan(payload)
    second = qr.build_research_plan(payload)
    assert first == second
    assert first["status"] == "plan_only"
    assert first["request_sha256"]
    assert first["application"]["label"] == "CA"
    assert first["application"]["source_semantics"] == "unverified"
    assert first["methods"][0]["status"] == "protocol_requirements_complete"
    assert first["methods"][0]["execution_status"] == "not_attempted"
    assert first["network"] is False
    assert first["execution_attempted"] is False
    assert first["jobs_submitted"] == 0
    assert first["quantum_advantage"] == "not_assessed"
    assert first["evidence_refs"] == ["local:problem-contract-v1"]
    assert first["limitations"]


def test_plan_reports_common_and_method_specific_gaps_without_recommendation():
    result = qr.build_research_plan({"schema_version": 1, "question": "Study"})
    assert result["status"] == "plan_only"
    assert {item["field"] for item in result["gaps"]} >= {
        "problem_class",
        "objective",
        "baseline_methods",
        "evaluation_metrics",
        "evidence_refs",
        "resource_limits",
    }
    qca = next(item for item in result["methods"] if item["id"] == "quantum_cellular_automata")
    assert qca["status"] == "blocked_on_gaps"
    assert {"state_space", "local_rule", "boundary_conditions", "evolution_validity"} <= set(qca["missing_inputs"])
    assert result["automatic_method_recommendation"] is None
    assert result["execution_authorized"] is False


def test_explicitly_declaring_no_constraints_is_not_a_gap():
    payload = _complete_payload()
    payload["constraints"] = []
    result = qr.build_research_plan(payload)
    assert "constraints" not in {item["field"] for item in result["gaps"]}


def test_cli_rejects_duplicate_json_keys():
    process = subprocess.run(
        [sys.executable, "-m", "integrations.quantum_research", "plan"],
        cwd=ROOT,
        input='{"schema_version":1,"schema_version":1,"question":"ambiguous"}',
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert process.returncode == 2
    assert json.loads(process.stdout)["code"] == "invalid_research_request"


def test_skill_and_managed_profiles_route_without_editing_cards():
    skill = (ROOT / ".opencode/skills/pesquisador-universal-marcelo-claro/SKILL.md").read_text()
    applicability = (ROOT / "agents/catalog/quantum-applicability-researcher.md").read_text()
    optimization = (ROOT / "agents/catalog/quantum-optimization-researcher.md").read_text()
    assert "integrations.quantum_research" in skill
    assert "quantum-applicability-researcher" in skill
    assert "quantum-optimization-researcher" in skill
    assert "allow_edit: false" in applicability
    assert "allow_edit: false" in optimization


@pytest.mark.parametrize("mutate", [
    lambda p: p.update(schema_version=True),
    lambda p: p.update(unknown_field="ignored?"),
    lambda p: p.update(candidate_methods=["invented_method"]),
    lambda p: p.update(candidate_methods=["quantum_annealing", "quantum_annealing"]),
    lambda p: p.update(resource_limits={"shots": True}),
    lambda p: p.update(resource_limits={"qubits": 0}),
    lambda p: p.update(method_inputs={"quantum_cellular_automata": ["unknown"]}),
    lambda p: p.update(application_label="UNKNOWN"),
])
def test_invalid_payloads_fail_closed(mutate):
    payload = _complete_payload()
    mutate(payload)
    with pytest.raises(qr.QuantumResearchContractError):
        qr.build_research_plan(payload)


def test_catalog_cli_and_plan_cli_are_local_json_only():
    env = dict(os.environ)
    env.pop("GJQ_API_KEY", None)
    catalog = subprocess.run(
        [sys.executable, "-m", "integrations.quantum_research", "catalog"],
        cwd=ROOT,
        env=env,
        input="",
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert catalog.returncode == 0, catalog.stderr
    assert json.loads(catalog.stdout)["network"] is False

    planned = subprocess.run(
        [sys.executable, "-m", "integrations.quantum_research", "plan"],
        cwd=ROOT,
        env=env,
        input=json.dumps(_complete_payload()),
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert planned.returncode == 0, planned.stderr
    output = json.loads(planned.stdout)
    assert output["execution_attempted"] is False
    assert output["jobs_submitted"] == 0
