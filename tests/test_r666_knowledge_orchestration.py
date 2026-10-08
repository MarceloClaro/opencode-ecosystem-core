"""R666: coordenação real e metacognição sem promoção de hipóteses."""
import asyncio
import json

import pytest


def modules():
    return {"source": [{"id": "sources", "state": "executed",
                        "outputs": ["records"],
                        "evidence": [{"kind": "execution", "ref": "run:source", "success": True}]}],
            "analysis": [{"id": "analysis", "state": "declared", "inputs": ["records"],
                          "outputs": ["results"], "requires": ["sources"]}]}


def test_plan_keeps_declarations_out_of_observed_and_explains_gaps():
    from marceloclaro.knowledge_evolution import KnowledgeEvolutionService
    result = KnowledgeEvolutionService().plan(problem="Analisar dados", target_state=["analysis"],
                                             modules=modules())
    assert result["executed"] is False
    assert result["externally_validated"] is False
    assert result["observed_capabilities"] == ["sources"]
    assert "analysis" in result["evolution_gap"]
    assert result["composition"]
    assert result["sequencing"]["phases"]
    assert result["score_kind"] == "heuristic"
    assert result == KnowledgeEvolutionService().plan(problem="Analisar dados", target_state=["analysis"],
                                                    modules=modules())


def test_unknown_prerequisite_is_not_silently_removed():
    from marceloclaro.knowledge_evolution import KnowledgeEvolutionService
    current = modules()
    current["analysis"][0]["requires"] = ["missing_dataset"]
    result = KnowledgeEvolutionService().plan(problem="Analisar", target_state=["analysis"], modules=current)
    assert result["status"] == "blocked"
    assert result["sequencing"]["missing_dependencies"]


def test_emergent_candidate_receives_composition_and_conditional_roadmap():
    from marceloclaro.knowledge_evolution import KnowledgeEvolutionService
    result = KnowledgeEvolutionService().plan(
        problem="Compor fontes e análise", target_state=["new_science"], modules=modules(),
        candidates=[{"id": "new_science", "description": "Combinar fontes e análise",
                     "requires": ["sources", "analysis"]}])
    assert result["status"] == "planned"
    assert "new_science" not in result["observed_capabilities"]
    assert result["potential_successors"][0]["executed"] is False
    assert result["potential_successors"][0]["hypothesis"] is True
    assert result["dna"]["capability_map"]["new_science"]["state"] == "declared"
    assert result["potential_successors"][0]["composition"]["dependencies"]
    assert result["sequencing"]["phases"]


@pytest.mark.parametrize("config", [[], {"problem": "", "target_state": ["x"]},
                                    {"problem": "x", "target_state": "x"},
                                    {"problem": "x", "target_state": ["x"], "max_candidates": True},
                                    {"problem": "x", "target_state": ["x"], "execute": True}])
def test_invalid_plan_rejected(config):
    from marceloclaro.knowledge_evolution import validate_plan_config
    with pytest.raises(ValueError):
        validate_plan_config(config)


def test_observation_preserves_confidence_and_copies_input(tmp_path, monkeypatch):
    import importlib
    module = importlib.import_module("mci.metabus")
    monkeypatch.setattr(module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    memory = module.MetacognitiveMemory()
    memory.confidence_ledger["marceloclaro"] = 0.37
    observation = {"status": "planned", "executed": False, "gaps": ["analysis"]}
    memory.record_observation("marceloclaro", "planejamento", observation)
    observation["gaps"].clear()
    assert memory.confidence_ledger["marceloclaro"] == 0.37
    assert memory.episodic[-1]["observation"]["gaps"] == ["analysis"]
    assert memory.episodic[-1]["type"] == "observation"


def test_observation_cannot_return_persisted_receipt_after_write_failure(tmp_path, monkeypatch):
    import importlib
    module = importlib.import_module("mci.metabus")
    monkeypatch.setattr(module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    memory = module.MetacognitiveMemory()
    def fail_replace(*args):
        raise OSError("disk failure")
    monkeypatch.setattr(module.os, "replace", fail_replace)
    with pytest.raises(RuntimeError, match="persist"):
        memory.record_observation("marceloclaro", "plano", {"executed": False})
    assert not memory.episodic


def test_diagnose_rejects_invalid_capability_before_diagnostic_effects(monkeypatch):
    from marceloclaro import orchestrator
    current = modules()
    current["analysis"][0]["state"] = "invented"
    monkeypatch.setattr(orchestrator.diagnostic_pipeline, "run", lambda *a, **kw: pytest.fail("late validation"))
    orch = orchestrator.MarceloClaroOrchestrator(auto_load_agents=False)
    with pytest.raises(ValueError):
        orch.diagnose("corpus", knowledge_config={"problem": "x", "target_state": ["analysis"], "modules": current})


def test_science_rejects_invalid_method_columns_before_orchestrator(monkeypatch):
    from integrations import ecosystem_mcp
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: pytest.fail("late validation"))
    config = {"question": "x", "dataset_csv": "x.csv", "output_dir": "out",
              "dataset_provenance": {}, "method": "pearson", "variables": {}}
    with pytest.raises(ValueError):
        asyncio.run(ecosystem_mcp.ecosystem_scientific_run(config))


def test_completed_target_does_not_reopen_historical_prerequisites():
    from marceloclaro.knowledge_evolution import KnowledgeEvolutionService
    current = {"history": [{"id": "completed", "requires": ["historical_input"],
                           "state": "executed", "evidence": [{"kind": "execution", "ref": "run:1", "success": True}]}]}
    result = KnowledgeEvolutionService().plan(problem="x", target_state=["completed"], modules=current, candidates=[])
    assert result["evolution_gap"] == []
    assert "historical_input" in result["structural_closure"]


def test_metacognition_links_same_scope_without_confidence_promotion():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator, metabus
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    confidence = dict(metabus.memory.confidence_ledger)
    config = {"problem": "Escopo único R666", "target_state": ["analysis"], "modules": modules(), "candidates": []}
    first = orch.knowledge_evolution_plan(**config)
    second = orch.knowledge_evolution_plan(**config)
    assert second["metacognition"]["previous_observation_id"] == first["metacognition"]["observation_id"]
    assert second["metacognition"]["persisted"] is True
    assert metabus.memory.confidence_ledger == confidence


def test_mcp_mutating_operations_do_not_overlap(monkeypatch):
    import threading
    import time
    from integrations import ecosystem_mcp
    active = 0
    maximum = 0
    lock = threading.Lock()
    class ConcurrentSpy(OrchestratorSpy):
        def knowledge_evolution_plan(self, **config):
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            time.sleep(0.02)
            with lock:
                active -= 1
            return {"status": "planned"}
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", ConcurrentSpy)
    config = {"problem": "x", "target_state": ["analysis"], "modules": modules(), "candidates": []}
    async def run():
        return await asyncio.gather(ecosystem_mcp.ecosystem_knowledge_plan(config),
                                    ecosystem_mcp.ecosystem_knowledge_plan(config))
    assert len(asyncio.run(run())) == 2
    assert maximum == 1


class OrchestratorSpy:
    def __init__(self):
        self.calls = []

    def knowledge_evolution_plan(self, **config):
        self.calls.append(("plan", config))
        return {"status": "planned", "executed": False}

    def scientific_reproducible_run(self, **config):
        self.calls.append(("run", config))
        return {"status": "blocked", "executed": False}


def test_cli_mcp_share_central_orchestrator(tmp_path, monkeypatch, capsys):
    from marceloclaro.science_cli import run_science_cli
    from integrations import ecosystem_mcp
    orch = OrchestratorSpy()
    config = {"problem": "analisar", "target_state": ["analysis"], "modules": modules()}
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: orch)
    assert run_science_cli(["planejar", "--config", str(path)], orchestrator=orch) == 0
    assert json.loads(capsys.readouterr().out)["executed"] is False
    assert asyncio.run(ecosystem_mcp.ecosystem_knowledge_plan(config))["status"] == "planned"
    assert orch.calls == [("plan", config), ("plan", config)]


def test_cli_rejects_unknown_options_before_construction(capsys):
    from marceloclaro.science_cli import run_science_cli
    assert run_science_cli(["planejar", "--execute"]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "error"


@pytest.mark.parametrize("strict", [True, False])
def test_simulated_deep_research_never_reaches_review_or_export(monkeypatch, strict):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from agentic_science_v2 import orchestrator as ideas, deep_research, review_agent
    monkeypatch.setattr(ideas, "run_agentic_science_v2", lambda **kw: {"history": []})
    monkeypatch.setattr(deep_research, "run_deep_research", lambda **kw: {
        "status": "simulation", "evidence_eligible": False, "reports": []})
    monkeypatch.setattr(review_agent.OrchestratorReviewer, "review", lambda *a, **kw: pytest.fail("review of simulation"))
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    result = orch.scientific_discovery_pipeline("biologia", max_rounds=1, strict_gates=strict)
    assert result["status"] == "blocked"
    assert result["gate_decision"]["passed"] is False
    assert "r103" not in result["stages"]
