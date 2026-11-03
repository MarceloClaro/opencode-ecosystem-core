"""R931: integridade do protocolo; não ensaia pesquisa nem produção."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/piloto-pesquisa-r931/contrato.json"
DOCUMENT = ROOT / "docs/PILOTO_PESQUISA_SUPERVISIONADO_R931.md"


def contract():
    assert CONTRACT.is_file(), "Contrato do piloto ainda não entregue"
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_protocol_is_not_execution_or_release():
    plan = contract()
    assert plan["spec_id"] == "SPEC-935-R931"
    assert plan["status"] == "protocol_with_pending_inputs"
    assert plan["validation_scope"] == "document_contract_only"
    for flag in ("pilot_executed", "production_ready", "production_release_approved",
                 "externally_validated", "scientific_results_generated"):
        assert plan[flag] is False
    assert plan["automatic_authorization"] is False


def test_missing_human_inputs_are_explicit():
    plan = contract()
    required = {"research_question", "corpus", "operator", "reviewer", "provider",
                "external_services", "runtime_budget_seconds", "cost_budget_brl",
                "retention_days", "publication_destination", "human_approval"}
    assert set(plan["pending_inputs"]) == required
    for item in plan["pending_inputs"].values():
        assert item["value"] is None
        assert item["status"] == "pending_human_decision"
    assert plan["bibliographic_records"] == []


def test_permissions_remain_closed():
    permissions = contract()["permissions"]
    assert permissions["policy_modified"] is False
    assert permissions["current_stage"] == "planning_and_local_contract_checks"
    required = {"source_lookup", "pdf_download", "model_download", "training",
                "deployment", "personal_data_access", "policy_change"}
    assert set(permissions["authorized_effects"]) == required
    assert all(value is False for value in permissions["authorized_effects"].values())


def test_proposed_limits_are_not_measured_or_authorized():
    limits = contract()["pilot_limits"]
    assert limits["status"] == "proposed_not_frozen"
    assert limits["max_operators"] == 1
    assert limits["max_concurrent_jobs"] == 1
    assert limits["max_included_references"] == 20
    assert limits["runtime_budget_seconds"] is None
    assert limits["cost_budget_brl"] is None
    assert limits["external_call_budget"] is None
    assert limits["capacity_measured"] is False
    assert limits["enforcement_implemented_by_this_delivery"] is False


def test_metrics_have_denominators_and_no_results():
    metrics = contract()["metrics"]
    assert {row["id"] for row in metrics} == {
        "reference_metadata_coverage", "claim_traceability", "unsupported_claims",
        "screening_documentation", "latency_p95", "peak_memory", "total_cost"}
    for metric in metrics:
        assert metric["status"] == "proposed_not_frozen"
        assert metric["unit"] and metric["population"]
        assert metric["measurement"] is None
        assert metric["sample_size"] is None
        assert metric["empty_population_passes"] is False
        assert metric["reviewer_required"] is True
    rows = {row["id"]: row for row in metrics}
    for name in ("reference_metadata_coverage", "claim_traceability", "screening_documentation"):
        assert rows[name]["proposed_target"] == 1.0
        assert rows[name]["numerator"] and rows[name]["denominator"]
    assert rows["unsupported_claims"]["proposed_target"] == 0
    for name in ("latency_p95", "peak_memory", "total_cost"):
        assert rows[name]["proposed_target"] is None


def test_bibliographic_audit_requires_source_support_and_legal_access():
    audit = contract()["bibliographic_audit"]
    assert set(audit["required_fields"]) >= {
        "identifier", "primary_metadata_url", "verified_at", "metadata_status",
        "license_or_access_basis", "text_access_level", "claim_id", "source_locator",
        "support_status", "limitations", "screening_decision", "screening_reason",
        "human_reviewer", "review_status"}
    assert audit["unverified_reference_label"] == "[NÃO VERIFICADA]"
    assert audit["metadata_implies_claim_support"] is False
    assert audit["abstract_implies_full_text_read"] is False
    assert audit["automatic_scientific_approval"] is False
    assert "sci-hub" in audit["forbidden_acquisition"]


def test_gates_require_evidence_and_human_acceptance():
    gates = contract()["gates"]
    assert [gate["id"] for gate in gates] == ["G0", "G1", "G2", "G3", "G4", "G5"]
    previous = []
    for gate in gates:
        assert gate["status"] == "pending"
        assert gate["depends_on"] == previous[-1:]
        assert gate["owner_role"] and gate["acceptance"] and gate["required_artifacts"]
        assert gate["evidence"] == []
        assert gate["human_accepted"] is False
        assert gate["accepted_by"] is None
        previous.append(gate["id"])
    assert contract()["production_requires_separate_release_contract"] is True


def test_stop_and_recovery_are_planned_not_claimed():
    operations = contract()["operations"]
    assert operations["status"] == "planned_not_exercised"
    assert operations["end_to_end_controls_verified"] is False
    assert set(operations["stop_triggers"]) >= {
        "budget_exceeded", "unlicensed_access", "secret_or_personal_data",
        "unverified_central_claim", "artifact_hash_mismatch", "cleanup_uncertain"}
    assert set(operations["required_drills"]) >= {
        "cancel_and_close_processes", "worker_crash_without_false_success",
        "backup_restore_hashes", "resume_without_duplicate_outputs",
        "authenticated_access_and_audit_logs"}


def test_historical_evidence_is_separate_and_matches_receipts():
    history = contract()["historical_evidence"]
    assert set(history) == {"R928", "R929"}
    expected = {
        "R928": "outputs/core-r928/final-gates.json",
        "R929": "docs/evidence/r929/receipt.json",
    }
    for round_id, path in expected.items():
        row = history[round_id]
        assert row["path"] == path
        assert row["scope"] == "historical_selected_tests"
        assert row["current_tree_revalidated"] is False
        assert row["production_approval"] is False
        receipt = json.loads((ROOT / path).read_text(encoding="utf-8"))
        if round_id == "R928":
            assert row["tests_passed"] == receipt["tests"]["counts"]["tests"] == 469
            assert receipt["tests"]["whole_repository_suite_run"] is False
        else:
            assert row["tests_passed"] == receipt["final_selection"]["passed"] == 643
            assert receipt["production_release_approved"] is False
    assert contract()["test_counts_additive"] is False
    assert contract()["limitations"]["unmodeled_history_entries"] == 78


def test_document_explains_scope_and_next_decision():
    contract()
    assert DOCUMENT.is_file(), "Documento operacional ainda não entregue"
    text = DOCUMENT.read_text(encoding="utf-8")
    for anchor in ("protocolo com pendências", "G0", "G5", "469", "643", "78",
                   "não foram somados", "denominador", "treinamento em GPU",
                   "suíte upstream", "contrato.json", "não concede autorização",
                   "Pergunta necessária", "não foram revalidados"):
        assert anchor in text, anchor
