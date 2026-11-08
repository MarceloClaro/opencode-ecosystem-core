"""Contraprovas de integração R917; verificações locais não fingem execução A2A."""
from __future__ import annotations

import uuid
import pytest


@pytest.fixture
def research(tmp_path):
    from academic.adversarial_research.service import AdversarialResearchService
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    artifact = tmp_path / "paper.md"
    artifact.write_text(
        "Estudo antes/depois sobre letramento com dez participantes. "
        "Sem grupo de controle; a conclusão relata eficácia.",
        encoding="utf-8",
    )
    project = {
        "research_id": "study-r917-1",
        "spec_id": "SPEC-935-R917",
        "artifact_path": str(artifact),
        "problem": "Como avaliar letramento?",
        "objectives": ["Descrever a mudança observada"],
        "study_type": "before_after",
        "context": {"control_group": False, "humans": True},
        "sources": [],
        "claims": [{
            "claim_id": "c1",
            "statement": "O método é eficaz para elevar o letramento.",
            "claim_type": "inferential",
            "source_refs": [],
            "evidence_status": "reported",
            "limitations": [],
            "reviewer_agent_ids": [],
            "attributes": {"causal_claim": True},
        }],
    }
    primary = MarceloClaroOrchestrator()
    primary._academic_rigor = AdversarialResearchService(primary, state_dir=tmp_path / "rigor-state")
    return primary, project


def test_primary_orchestrates_local_review_and_persists_receipt(research):
    primary, project = research
    report = primary.run_academic_adversarial_review(project, max_steps=3)

    assert report["review_id"].startswith("review-")
    assert report["reviewed_artifact_hash"]
    assert report["specification_loaded"] is True
    assert report["dispatch_scope"] == "local_checks"
    assert report["agent_inference_executed"] is False
    assert report["scientifically_approved"] is False
    assert report["human_review_required"] is True
    assert report["metacognition"]["persisted"] is True
    assert report["metacognition"]["confidence_promoted"] is False
    assert primary.academic_rigor_action({"operation": "report", "review_id": report["review_id"]})["report_sha256"] == report["report_sha256"]


def test_managed_dispatch_does_not_fabricate_inference_or_close_tasks(research):
    from marceloclaro.orchestrator import blackboard

    primary, project = research
    before = set(blackboard.tasks)
    report = primary.run_academic_adversarial_review(
        project, max_steps=2, profile_scope="managed_profiles"
    )

    assert report["agent_inference_executed"] is False
    assert all(not result["orchestration"]["inference_executed"]
               for result in report["specialist_results"])
    # Perfis research-* foram removidos do catálogo local; ausência explícita
    # não deve ser substituída por tarefa ou conclusão inventada.
    assert all(result["orchestration"]["dispatch_status"] == "profile_unavailable"
               for result in report["specialist_results"])
    assert set(blackboard.tasks) == before


def test_managed_task_stays_pending_after_local_checker_runs(research, monkeypatch):
    from agents.lifecycle import AgentLifecycleService
    from mci.blackboard import BlackboardTask, blackboard

    primary, project = research
    agent_id = "research-intake-auditor"
    monkeypatch.setattr(AgentLifecycleService, "validate", lambda self, _aid: {
        "definition_validated": True, "source_sha256": "test-profile-hash"
    })

    def fake_activate(_request):
        task_id = "task-r917-" + uuid.uuid4().hex
        task = BlackboardTask(task_id, "Test double: tarefa A2A aguardando executor", [], {})
        task.status = "assigned"
        task.assigned_to = agent_id
        blackboard.tasks[task_id] = task
        return {"definition_validated": True, "registered": True, "status": "assigned",
                "task_id": task_id, "assigned_to": agent_id}

    monkeypatch.setattr(primary, "agent_profile_action", fake_activate)
    report = primary.run_academic_adversarial_review(
        project, max_steps=1, profile_scope="managed_profiles"
    )

    task = next(task for task_id, task in blackboard.tasks.items()
                if task_id.startswith("task-r917-") and task.description == "Test double: tarefa A2A aguardando executor")
    orchestration = report["specialist_results"][0]["orchestration"]
    assert task.status == "assigned"
    assert orchestration["dispatch_status"] == "awaiting_executor"
    assert orchestration["local_check_executed"] is True
    assert orchestration["inference_executed"] is False
    assert report["agent_inference_executed"] is False


def test_inventory_does_not_claim_missing_profiles_are_validated(research):
    primary, _ = research
    inventory = primary.academic_rigor_action({"operation": "inventory"})

    assert inventory["status"] == "profiles_missing_or_unvalidated"
    assert inventory["count"] == 36
    assert inventory["scientific_validation"] is False
    by_id = {row["agent_id"]: row for row in inventory["profiles"]}
    assert by_id["david-bohm-wholeness"]["definition_validated"] is True
    assert by_id["richard-feynman-explainer"]["definition_validated"] is True
    research_rows = [row for row in inventory["profiles"]
                     if row["agent_id"].startswith("research-")]
    assert research_rows
    assert all(row["definition_validated"] is False for row in research_rows)


def test_preflight_requires_explicit_claim_intake(research):
    primary, _ = research
    result = primary._academic_preflight("Rascunho sem alegações mapeadas", "Eficácia")

    assert result["status"] == "needs_explicit_intake"
    assert result["claims_extracted"] is False
    assert result["scientifically_approved"] is False
    assert result["human_review_required"] is True


def test_invalid_profile_scope_is_rejected(research):
    primary, project = research
    with pytest.raises(ValueError, match="profile_scope"):
        primary.academic_rigor_action({
            "operation": "review", "project": project, "profile_scope": "automatic_magic"
        })


def test_cancellation_and_step_budget_remain_explicit(research):
    primary, project = research
    partial = primary.run_academic_adversarial_review(project, max_steps=1)
    cancelled = primary.run_academic_adversarial_review(project, cancelled=True)

    assert partial["execution_complete"] is False
    assert partial["unresolved_gaps"]
    assert cancelled["review_status"] == "cancelled"
    assert cancelled["agent_inference_executed"] is False
