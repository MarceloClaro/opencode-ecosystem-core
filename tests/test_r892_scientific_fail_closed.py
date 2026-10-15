"""R892: falhas observadas não viram entrega científica nem decisão humana."""

import copy
import json
from types import SimpleNamespace

import pytest


@pytest.fixture
def primary(monkeypatch, tmp_path):
    import importlib

    bus_module = importlib.import_module("mci.metabus")
    module = importlib.import_module("marceloclaro.orchestrator")
    monkeypatch.setattr(bus_module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    monkeypatch.setattr(bus_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(module.metabus, "memory", bus_module.MetacognitiveMemory())
    # Exercita os métodos reais sem registrar agentes nem iniciar executores.
    orch = module.MarceloClaroOrchestrator.__new__(module.MarceloClaroOrchestrator)
    orch.id = "marceloclaro"
    orch.trust = SimpleNamespace(learn=lambda *args, **kwargs: pytest.fail("trust não deve ser premiado"))
    return orch


@pytest.fixture
def successful_stages(primary, monkeypatch):
    import agentic_science_v2.deep_research as research
    import agentic_science_v2.orchestrator as discovery
    import agentic_science_v2.revision_agent as revision
    import marceloclaro.orchestrator as module
    from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewPackage

    package = ReviewPackage(
        paper_title="Teste de estados", overall_score=0.8,
        dimension_scores={}, critiques=[], traceability=1.0, coverage=1.0,
        export_gate_passed=True, repair_plan=[],
    )
    monkeypatch.setattr(discovery, "run_agentic_science_v2", lambda **kwargs: {
        "history": [{"ideas": [{"id": "i1", "hypothesis": "Hipótese de teste",
                                  "scores": {"overall": 0.7}}]}],
    })
    # Resultado controlado para alcançar R104/R105; não é experimento científico real.
    monkeypatch.setattr(research, "run_deep_research", lambda **kwargs: {
        "status": "completed", "experiment_executed": True, "evidence_eligible": True,
        "reports": [{"summary": "Observação controlada para teste de fluxo.", "confidence": 0.7}],
        "plans": [], "evidence_graph": {},
    })
    monkeypatch.setattr(OrchestratorReviewer, "review", lambda self, paper: package)
    good_revision = {
        "status": "completed", "report": {"total_claims": 0, "traceability_pct": 100},
        "integrity": {"intact": True, "issues": []}, "revisions": [],
        "actions": [], "mappings": [], "proposals": [], "diff": "", "rebuttal_letter": "",
    }
    good_composition = {
        "status": "completed", "manuscript": "# Artigo\nTexto controlado.",
        "sections": {"Introduction": "Contexto controlado.", "Results": "Resultado controlado."},
        "outline": {}, "consistency_report": {"overall_score": 80}, "statistics": {},
    }
    monkeypatch.setattr(revision, "create_revision", lambda *args: copy.deepcopy(good_revision))
    monkeypatch.setattr(module, "compose_paper_core", lambda **kwargs: copy.deepcopy(good_composition))
    return primary, package, good_revision, good_composition


@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize("failed_output", [
    {"status": "error", "error": "Revisão indisponível"},
    {"status": "blocked", "reason": "Sem revisor"},
    {}, None,
    {"status": "completed", "report": {}, "integrity": {"intact": False}},
])
def test_failed_revision_never_reaches_composer(successful_stages, monkeypatch, strict, failed_output):
    import agentic_science_v2.revision_agent as revision
    import marceloclaro.orchestrator as module

    orch, *_ = successful_stages
    monkeypatch.setattr(revision, "create_revision", lambda *args: failed_output)
    monkeypatch.setattr(module, "compose_paper_core", lambda **kwargs: pytest.fail("Composição após revisão inválida"))
    result = orch.scientific_discovery_pipeline("Teste", strict_gates=strict)
    assert result["status"] == "blocked"
    assert result["failed_stage"] == "r104d"
    assert result["reason"]
    assert result["gate_decision"]["passed"] is False
    assert "r105" not in result["stages"]


@pytest.mark.parametrize("failed_output", [
    {"status": "error", "error": "Compositor indisponível"},
    {"status": "blocked", "reason": "Sem saída"},
    {"status": "completed", "sections": {}, "manuscript": ""},
    {}, None,
])
def test_failed_composer_is_not_completed(successful_stages, monkeypatch, failed_output):
    import marceloclaro.orchestrator as module

    orch, *_ = successful_stages
    monkeypatch.setattr(module, "compose_paper_core", lambda **kwargs: failed_output)
    result = orch.scientific_discovery_pipeline("Teste", strict_gates=False)
    assert result["status"] == "blocked"
    assert result["failed_stage"] == "r105"
    assert result["gate_decision"]["passed"] is False
    assert "r381" not in result["stages"]


def test_non_strict_review_only_produces_unapproved_draft(successful_stages):
    orch, package, *_ = successful_stages
    package.export_gate_passed = False
    result = orch.scientific_discovery_pipeline("Teste", strict_gates=False)
    assert "r105" in result["stages"]
    assert result["status"] == "blocked"
    assert result["gate_decision"]["passed"] is False
    assert result["scientific_acceptance"] is False


def test_completed_composition_remains_local_heuristic(successful_stages):
    import marceloclaro.orchestrator as module

    orch, *_ = successful_stages
    before = copy.deepcopy(module.metabus.memory.confidence_ledger)
    result = orch.scientific_discovery_pipeline("Teste")
    assert result["status"] == "completed"
    assert result["scientific_acceptance"] is False
    assert result["human_review_required"] is True
    assert module.metabus.memory.confidence_ledger == before


@pytest.mark.parametrize("state,reports", [
    ("failed", [{"summary": "Saída parcial"}]),
    ("pending", [{"summary": "Aguardando"}]),
    (None, [{"summary": "Estado ausente"}]),
    ("completed", []), ("completed", [None]),
    ("completed", [{"summary": "  "}]),
    ("completed", [{"summary": {"text": "Dado mal tipado"}}]),
])
def test_research_requires_completed_state_and_useful_report(successful_stages, monkeypatch, state, reports):
    import agentic_science_v2.deep_research as research
    from agentic_science_v2.review_agent import OrchestratorReviewer

    orch, *_ = successful_stages
    monkeypatch.setattr(research, "run_deep_research", lambda **kwargs: {
        "status": state, "experiment_executed": True, "evidence_eligible": True,
        "reports": reports, "plans": [], "evidence_graph": {},
    })
    monkeypatch.setattr(OrchestratorReviewer, "review", lambda *args: pytest.fail("Revisão sem pesquisa elegível"))
    result = orch.scientific_discovery_pipeline("Teste", strict_gates=False)
    assert result["status"] == "blocked"
    assert result["gate_decision"]["passed"] is False
    assert "r103" not in result["stages"]


@pytest.mark.parametrize("state,result,assigned", [
    ("open", None, None), ("assigned", None, "executor"),
    ("failed", "Saída parcial", "executor"), ("completed", None, "executor"),
    ("completed", "completed", "executor"),
    ("completed", {"status": "blocked", "output": "Aguardando"}, "executor"),
    ("completed", "failed", "executor"),
    ("completed", "blocked", "executor"),
    ("completed", {"status": "completed", "success": "false", "output": "Parcial"}, "executor"),
    ("completed", {"status": "pending", "success": True, "output": "Parcial"}, "executor"),
    ("completed", "Saída real", None),
])
def test_maswos_never_fabricates_completion(primary, monkeypatch, state, result, assigned):
    import marceloclaro.orchestrator as module
    from mci.blackboard import BlackboardTask

    task = BlackboardTask("r892", "Analisar", ["science"], {})
    task.status, task.assigned_to, task.result = state, assigned, result
    monkeypatch.setattr(module, "blackboard", SimpleNamespace(tasks={"r892": task}))
    primary.delegate = lambda *args, **kwargs: "r892"
    primary.report_completion = lambda *args, **kwargs: pytest.fail("Conclusão fabricada")
    with pytest.raises(RuntimeError):
        primary._maswos_delegate("sugerido", "science", "Analisar")
    assert task.status == state
    assert task.result == result


def test_maswos_reads_completed_blackboard_result_without_recompletion(primary, monkeypatch):
    import marceloclaro.orchestrator as module
    from mci.blackboard import BlackboardTask

    task = BlackboardTask("r892", "Analisar", ["science"], {})
    task.status, task.assigned_to = "completed", "executor"
    task.result = "Achado com referência ao artefato local"
    monkeypatch.setattr(module, "blackboard", SimpleNamespace(tasks={"r892": task}))
    primary.delegate = lambda *args, **kwargs: "r892"
    primary.report_completion = lambda *args, **kwargs: pytest.fail("Duplicação de conclusão")
    assert primary._maswos_delegate("sugerido", "science", "Analisar") == "Achado com referência ao artefato local"


def test_scientific_loop_does_not_reward_generated_content(primary, monkeypatch):
    import marceloclaro.orchestrator as module

    primary.scientific_discovery_pipeline = lambda *args, **kwargs: {
        "status": "completed", "gate_decision": {"passed": True}, "stages": {},
        "metacognitive_report": {},
    }
    before = copy.deepcopy(module.metabus.memory.confidence_ledger)
    result = primary.run_scientific_discovery_loop("Teste", max_iterations=1)
    assert result["terminal_state"] == "success"
    assert module.metabus.memory.confidence_ledger == before
    observation = module.metabus.memory.episodic[-1]["observation"]
    assert observation["externally_validated"] is False
    assert observation["confidence_promoted"] is False


def test_scientific_loop_cannot_accept_completed_with_failed_gate(primary):
    primary.scientific_discovery_pipeline = lambda *args, **kwargs: {
        "status": "completed", "gate_decision": {"passed": False}, "stages": {},
        "metacognitive_report": {},
    }
    result = primary.run_scientific_discovery_loop("Teste", max_iterations=1)
    assert result["terminal_state"] != "success"


@pytest.mark.parametrize("delegation", ["failed", "empty", "dry_run", "no_stages"])
def test_maswos_cannot_approve_incomplete_execution(delegation):
    from academic.maswos import MaswosPipeline

    def unavailable(*args):
        raise RuntimeError("Executor não executou")

    delegate = unavailable if delegation == "failed" else lambda *args: ""
    if delegation == "dry_run":
        delegate = None
    pipeline = MaswosPipeline(delegate_fn=delegate, score_fn=lambda text: 10.0)
    stages = [] if delegation == "no_stages" else ["diagnostico_escopo"]
    result = pipeline.run("Teste", "Texto com nota heurística alta", stages=stages)
    assert result.approved is False
    assert all(stage.status != "completed" for stage in result.stages)


def test_academic_primary_records_observation_without_confidence_promotion(primary):
    import marceloclaro.orchestrator as module
    from academic.maswos import MaswosPipeline

    primary.maswos = MaswosPipeline(delegate_fn=lambda *args: "Saída controlada", score_fn=lambda text: 10.0)
    before = copy.deepcopy(module.metabus.memory.confidence_ledger)
    result = primary.academic_pipeline("Teste", stages=["diagnostico_escopo"])
    assert result["stages_completed"] == 1
    assert module.metabus.memory.confidence_ledger == before
    assert module.metabus.memory.episodic[-1]["observation"]["confidence_promoted"] is False


def test_required_board_failure_revokes_local_approval(monkeypatch):
    from academic.maswos import MaswosPipeline
    from academic.rigorous_board import RigorousBoard

    def unavailable(*args, **kwargs):
        raise RuntimeError("Banca indisponível")

    monkeypatch.setattr(RigorousBoard, "correction_loop", unavailable)
    pipeline = MaswosPipeline(delegate_fn=lambda *args: "Saída controlada", score_fn=lambda text: 10.0)
    run = pipeline.run_with_rigorous_board("Teste", "Texto", stages=["diagnostico_escopo"])
    assert run.approved is False
    assert run.summary()["board_error"] == "Banca indisponível"


@pytest.mark.parametrize("human", ["false", "true", 1, [True], {"human": True}])
def test_verified_annotation_rejects_truthy_non_boolean(tmp_path, human):
    from scientific_lab.native.evidence import annotate

    source = tmp_path / "source.txt"
    source.write_text("Trecho de origem", encoding="utf-8")
    with pytest.raises(ValueError):
        annotate(tmp_path, "p", "c", "s", "supports", "p.1", "Trecho", "autor",
                 status="verified", source_file=source, human=human)
    assert not (tmp_path / "09_provenance/evidence_annotations").exists()


def test_annotation_preserves_pending_and_requires_explicit_human(tmp_path):
    from scientific_lab.native.evidence import annotate

    source = tmp_path / "source.txt"
    source.write_text("Trecho de origem", encoding="utf-8")
    pending = annotate(tmp_path, "p", "c", "s", "supports", "p.1", "Trecho", "autor")
    assert json.loads(pending.read_text())["verification_status"] == "candidate"
    with pytest.raises(ValueError):
        annotate(tmp_path, "p", "c", "s", "supports", "p.1", "Trecho", "autor",
                 status="verified", source_file=source, human=False)
    confirmed = annotate(tmp_path, "p", "c", "s", "supports", "p.1", "Trecho", "autor",
                         status="verified", source_file=source, human=True)
    saved = json.loads(confirmed.read_text())
    assert saved["verification_status"] == "verified"
    assert len(saved["source_sha256"]) == 64
