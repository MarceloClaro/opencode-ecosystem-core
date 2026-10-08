"""R644: DAG e retomada com coordenadores simulados, sem chamar LLMs."""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import importlib

import pytest

from marceloclaro.workflow import WorkflowCoordinator
from marceloclaro.workflow_store import WorkflowBusyError, WorkflowStore


class MemoryStore:
    def __init__(self):
        self.records = {}
        self.saves = []
        self.locked = False

    def create(self, workflow_id, definition):
        if workflow_id in self.records:
            raise ValueError("Workflow já existe")
        self.records[workflow_id] = {"definition": deepcopy(definition)}
        return deepcopy(self.records[workflow_id])

    def load(self, workflow_id):
        if workflow_id not in self.records:
            raise ValueError("Workflow não encontrado")
        return deepcopy(self.records[workflow_id])

    def save(self, workflow_id, record):
        self.records[workflow_id] = deepcopy(record)
        self.saves.append(deepcopy(record))
        return deepcopy(record)

    @contextmanager
    def claim(self, workflow_id, timeout=0):
        assert not self.locked
        self.locked = True
        try:
            yield
        finally:
            self.locked = False


class CoordinatorDouble:
    def __init__(self, store, responses=None):
        self.store = store
        self.responses = list(responses or [])
        self.calls = []

    def run(self, task, required_capabilities=None, max_steps=1, timeout=120, ecosystem=None):
        assert self.store.locked
        self.calls.append({"task": task, "required_capabilities": required_capabilities,
                           "max_steps": max_steps, "timeout": timeout, "ecosystem": ecosystem})
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, BaseException):
                raise response
            if callable(response):
                return response()
            return response
        return {"status": "completed", "success": True, "steps": 1,
                "task_id": f"task-{len(self.calls)}", "ecosystem": ecosystem or "codex",
                "output": f"Entrega {len(self.calls)}"}


@pytest.fixture()
def setup():
    store = MemoryStore()
    coordinator = CoordinatorDouble(store)
    return WorkflowCoordinator(coordinator=coordinator, store=store), coordinator, store


@pytest.mark.parametrize("nodes", [
    [], [{"id": "a", "task": ""}],
    [{"id": "a", "task": "A"}, {"id": "a", "task": "B"}],
    [{"id": "a", "task": "A", "dependencies": ["missing"]}],
    [{"id": "a", "task": "A", "dependencies": ["b"]},
     {"id": "b", "task": "B", "dependencies": ["a"]}],
    [{"id": "bad/id", "task": "A"}],
    [{"id": "a", "task": "A", "required_capabilities": "review"}],
    [{"id": "a", "task": "A", "ecosystem": "unknown"}],
    [{"id": str(i), "task": "A"} for i in range(9)],
])
def test_invalid_dag_is_rejected_before_persistence_or_execution(setup, nodes):
    workflow, coordinator, store = setup
    with pytest.raises(ValueError):
        workflow.run(nodes)
    assert coordinator.calls == [] and store.records == {}


@pytest.mark.parametrize("options", [
    {"max_steps": 0}, {"max_steps": True}, {"max_steps": 25},
    {"timeout": 0}, {"timeout": float("nan")}, {"timeout": True},
    {"max_parallel": 2}, {"resume": True}, {"retry_failed": True},
])
def test_invalid_limits_have_no_effect(setup, options):
    workflow, coordinator, store = setup
    with pytest.raises(ValueError):
        workflow.run([{"id": "a", "task": "A"}], **options)
    assert coordinator.calls == [] and store.records == {}


def test_deterministic_dag_passes_dependency_output_and_origin(setup):
    workflow, coordinator, store = setup
    nodes = [
        {"id": "review", "task": "Revise a entrega", "dependencies": ["draft"],
         "required_capabilities": ["code_review"], "ecosystem": "antigravity"},
        {"id": "draft", "task": "Analise o código", "ecosystem": "codex"},
    ]
    result = workflow.run(nodes, workflow_id="review-dag")
    assert result["status"] == "completed" and result["success"]
    assert result["order"] == ["draft", "review"]
    assert result["execution_strategy"] == "sequential_shared_blackboard"
    assert result["max_parallel"] == 1 and result["steps"] == 2
    prompt = coordinator.calls[1]["task"]
    assert "Entrega 1" in prompt and "draft" in prompt and "task-1" in prompt and "codex" in prompt
    assert coordinator.calls[1]["required_capabilities"] == ["code_review"]
    assert coordinator.calls[1]["ecosystem"] == "antigravity"
    running = [record for record in store.saves if record["nodes"]["draft"]["status"] == "running"]
    assert running and running[0]["steps"] == 1
    assert result["nodes"]["draft"]["task_id"] == "task-1"


def test_failed_parent_blocks_child_and_independent_branch_runs(setup):
    workflow, coordinator, _ = setup
    coordinator.responses = [{"status": "failed", "success": False, "steps": 1,
                              "task_id": "bad-task", "output": "", "error": "Executor falhou"}]
    result = workflow.run([
        {"id": "a", "task": "Falha"},
        {"id": "b", "task": "Dependente", "dependencies": ["a"]},
        {"id": "c", "task": "Independente"},
    ])
    assert result["status"] == "failed" and not result["success"]
    assert result["nodes"]["a"]["status"] == "failed"
    assert result["nodes"]["b"]["status"] == "blocked"
    assert result["nodes"]["b"]["blocked_by"] == ["a"]
    assert result["nodes"]["c"]["status"] == "completed"
    assert len(coordinator.calls) == 2 and result["steps"] == 2


def test_global_attempt_budget_uses_actual_steps_and_limits_each_node(setup):
    workflow, coordinator, _ = setup
    coordinator.responses = [{"status": "completed", "success": True, "steps": 2,
                              "task_id": "two-attempts", "output": "A"}]
    result = workflow.run([
        {"id": "a", "task": "A", "per_node_max_steps": 3},
        {"id": "b", "task": "B", "per_node_max_steps": 3},
        {"id": "c", "task": "C"},
    ], max_steps=3)
    assert result["steps"] == 3 and result["status"] == "exhausted"
    assert [call["max_steps"] for call in coordinator.calls] == [3, 1]
    assert result["nodes"]["c"]["status"] == "exhausted"


def test_time_budget_is_global_and_independent_unstarted_nodes_exhaust(setup, monkeypatch):
    workflow, coordinator, _ = setup
    module = importlib.import_module("marceloclaro.workflow")
    clock = [0.0]
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    def delayed():
        clock[0] = 181.0
        return {"status": "completed", "success": True, "steps": 1, "output": "Tardia", "task_id": "slow"}
    coordinator.responses = [delayed]
    result = workflow.run([{"id": "a", "task": "A"}, {"id": "b", "task": "B"}])
    assert result["status"] == "exhausted" and not result["success"]
    assert len(coordinator.calls) == 1
    assert result["nodes"]["a"]["output"] == "Tardia"
    assert result["nodes"]["a"]["status"] == "exhausted"
    assert result["nodes"]["b"]["status"] == "exhausted"


def test_resume_reuses_completed_output_and_refuses_changed_definition(setup):
    workflow, coordinator, store = setup
    nodes = [{"id": "a", "task": "A"}, {"id": "b", "task": "B", "dependencies": ["a"]}]
    first = workflow.run(nodes, max_steps=1, workflow_id="resume-dag")
    assert first["nodes"]["a"]["status"] == "completed"
    second = workflow.run(list(reversed(nodes)), max_steps=2, workflow_id="resume-dag", resume=True)
    assert second["status"] == "completed" and second["steps"] == 2
    assert len(coordinator.calls) == 2
    assert second["nodes"]["a"]["task_id"] == first["nodes"]["a"]["task_id"]
    with pytest.raises(ValueError, match="definição"):
        workflow.run([{"id": "a", "task": "Outra tarefa"}], workflow_id="resume-dag", resume=True)
    assert len(coordinator.calls) == 2
    assert workflow.status("resume-dag") == store.records["resume-dag"]


def test_interrupted_execution_reservation_is_not_automatically_repeated(setup):
    workflow, coordinator, store = setup
    nodes = [{"id": "a", "task": "A", "per_node_max_steps": 2}]
    workflow.run(nodes, workflow_id="interrupted")
    record = store.records["interrupted"]
    record["status"] = "running"
    record["nodes"]["a"].update(status="running", reserved_steps=2)
    record["steps"] = 2
    result = workflow.run(nodes, max_steps=4, workflow_id="interrupted", resume=True)
    assert len(coordinator.calls) == 1
    assert result["nodes"]["a"]["status"] == "failed"
    assert result["nodes"]["a"]["execution_uncertain"] is True
    assert result["steps"] == 2
    retried = workflow.run(nodes, max_steps=4, workflow_id="interrupted", resume=True, retry_failed=True)
    assert len(coordinator.calls) == 2 and retried["status"] == "completed"
    assert retried["steps"] == 3 and retried["nodes"]["a"]["history"]


def test_unexpected_child_exception_is_persisted_and_does_not_abandon_independent_nodes(setup):
    workflow, coordinator, store = setup
    coordinator.responses = [OSError("Falha externa")]
    result = workflow.run([{"id": "a", "task": "A", "per_node_max_steps": 2},
                           {"id": "b", "task": "B"}])
    assert result["nodes"]["a"]["status"] == "failed"
    assert result["nodes"]["a"]["execution_uncertain"]
    assert result["nodes"]["b"]["status"] == "completed"
    assert result["steps"] == 3 and store.records[result["workflow_id"]] == result


def test_checkpoint_failure_prevents_executor_launch(setup, monkeypatch):
    workflow, coordinator, store = setup
    original = store.save
    def fail_running(workflow_id, record):
        if any(node["status"] == "running" for node in record["nodes"].values()):
            raise OSError("Não foi possível salvar")
        return original(workflow_id, record)
    monkeypatch.setattr(store, "save", fail_running)
    with pytest.raises(OSError):
        workflow.run([{"id": "a", "task": "A"}])
    assert coordinator.calls == []


def test_queued_and_empty_child_results_are_not_completed(setup):
    workflow, coordinator, _ = setup
    coordinator.responses = [
        {"status": "queued", "success": True, "steps": 1, "output": "Não terminou"},
        {"status": "completed", "success": True, "steps": 1, "output": ""},
    ]
    result = workflow.run([{"id": "a", "task": "A"}, {"id": "b", "task": "B"}])
    assert not result["success"]
    assert all(node["status"] == "failed" for node in result["nodes"].values())


def test_dependency_context_has_bounded_size_and_explicit_origin(setup):
    workflow, coordinator, _ = setup
    coordinator.responses = [{"status": "completed", "success": True, "steps": 1,
                              "output": "X" * 50000, "task_id": "large", "ecosystem": "codex"}]
    workflow.run([{"id": "a", "task": "A"}, {"id": "b", "task": "B", "dependencies": ["a"]}])
    assert len(coordinator.calls[1]["task"]) < 12500
    assert "truncado" in coordinator.calls[1]["task"]


@pytest.mark.parametrize("corrupt", [
    lambda record: record["nodes"]["a"].update(task="Outra tarefa"),
    lambda record: record.update(order=["missing"]),
    lambda record: record["nodes"]["a"].update(status="unexpected"),
    lambda record: record["nodes"]["a"].update(output="Entrega adulterada"),
    lambda record: record["nodes"]["a"].pop("steps"),
])
def test_corrupt_execution_checkpoint_is_rejected_before_reuse(setup, corrupt):
    workflow, coordinator, store = setup
    nodes = [{"id": "a", "task": "A"}]
    workflow.run(nodes, workflow_id="corrupt")
    corrupt(store.records["corrupt"])
    with pytest.raises(ValueError, match="Checkpoint"):
        workflow.run(nodes, workflow_id="corrupt", resume=True)
    assert len(coordinator.calls) == 1


def test_real_store_persists_roundtrip_and_resume_in_temporary_directory(tmp_path):
    store = WorkflowStore(tmp_path / "workflows")
    class ImmediateCoordinator:
        def __init__(self):
            self.calls = []
        def run(self, task, **kwargs):
            self.calls.append(task)
            return {"status": "completed", "success": True, "steps": 1,
                    "output": "Análise simulada para o gate hermético.", "task_id": f"task-{len(self.calls)}"}
    child = ImmediateCoordinator()
    workflow = WorkflowCoordinator(child, store)
    nodes = [{"id": "a", "task": "A"}, {"id": "b", "task": "B", "dependencies": ["a"]}]
    workflow.run(nodes, max_steps=1, workflow_id="persistent")
    result = workflow.run(nodes, max_steps=2, workflow_id="persistent", resume=True)
    assert result["status"] == "completed" and len(child.calls) == 2
    assert store.load("persistent") == result
    assert len(list((tmp_path / "workflows").glob("*.json"))) == 1


def test_initial_checkpoint_is_complete_even_if_first_save_fails(tmp_path, monkeypatch):
    from types import SimpleNamespace
    store = WorkflowStore(tmp_path)
    calls = []
    def execute(task, **kwargs):
        calls.append(task)
        return {"status": "completed", "success": True, "steps": 1,
                "output": "Simulado", "task_id": "after-resume"}
    workflow = WorkflowCoordinator(SimpleNamespace(run=execute), store)
    save = store.save
    monkeypatch.setattr(store, "save", lambda *args: (_ for _ in ()).throw(OSError("Falha inicial")))
    nodes = [{"id": "a", "task": "A"}]
    with pytest.raises(OSError, match="Falha inicial"):
        workflow.run(nodes, workflow_id="initial")
    checkpoint = store.load("initial")
    assert checkpoint["version"] == 1
    assert checkpoint["nodes"]["a"]["status"] == "queued"
    assert calls == []
    monkeypatch.setattr(store, "save", save)
    resumed = workflow.run(nodes, workflow_id="initial", resume=True)
    assert resumed["status"] == "completed" and len(calls) == 1


@pytest.mark.parametrize("invalid_trace", [object(), float("nan")])
def test_non_serializable_outcome_does_not_abandon_independent_branch(tmp_path, invalid_trace):
    from types import SimpleNamespace
    responses = iter([
        {"status": "completed", "success": True, "steps": 1,
         "output": "Simulado", "task_id": "bad-trace", "trace": invalid_trace},
        {"status": "completed", "success": True, "steps": 1,
         "output": "Simulado", "task_id": "good-trace"},
    ])
    store = WorkflowStore(tmp_path)
    workflow = WorkflowCoordinator(SimpleNamespace(run=lambda *args, **kwargs: next(responses)), store)
    result = workflow.run([{"id": "a", "task": "A"}, {"id": "b", "task": "B"}])
    assert result["nodes"]["a"]["status"] == "failed"
    assert result["nodes"]["a"]["execution_uncertain"]
    assert result["nodes"]["b"]["status"] == "completed"
    assert result["steps"] == 2 and store.load(result["workflow_id"]) == result


def test_different_workflow_ids_cannot_overlap_shared_blackboard_in_one_process(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    entered, release = Event(), Event()
    class GatedCoordinator:
        def run(self, task, **kwargs):
            entered.set()
            assert release.wait(timeout=5)
            return {"status": "completed", "success": True, "steps": 1,
                    "output": "Simulado", "task_id": "gated"}
    store = WorkflowStore(tmp_path)
    first = WorkflowCoordinator(GatedCoordinator(), store)
    second = WorkflowCoordinator(GatedCoordinator(), store)
    with ThreadPoolExecutor(max_workers=1) as pool:
        running = pool.submit(first.run, [{"id": "a", "task": "A"}], workflow_id="one")
        try:
            assert entered.wait(timeout=5)
            with pytest.raises(WorkflowBusyError):
                second.run([{"id": "a", "task": "A"}], workflow_id="two")
            assert not (tmp_path / "two.json").exists()
        finally:
            release.set()
        assert running.result(timeout=5)["status"] == "completed"


def test_workflow_reuses_real_autonomous_a2a_lifecycle_with_mocked_executor(tmp_path, monkeypatch):
    # Reutiliza os fixtures herméticos R640; não executa CLIs ou modelos reais.
    from types import SimpleNamespace
    import importlib
    from marceloclaro.autonomous import AutonomousCoordinator
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from mci.blackboard import AgentCard, blackboard
    from mci.metabus import metabus
    from mci.reflexion import reflexion_engine
    from sdd.loop_spec import loop_spec_registry
    from transformer.harness_head import HarnessRegistry
    from test_r640_autonomous import RuntimeDouble

    metabus_module = importlib.import_module("mci.metabus")
    for obj, attr, value in (
        (metabus, "subscribers", {}), (blackboard, "registry", {}),
        (blackboard, "tasks", {}), (metabus.memory, "episodic", []),
        (metabus.memory, "semantic", {}), (metabus.memory, "confidence_ledger", {}),
        (loop_spec_registry, "loops", {}),
    ):
        monkeypatch.setattr(obj, attr, value)
    monkeypatch.setattr(metabus_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(metabus.memory, "_save", lambda: None)
    metabus.subscribe("agent.register", blackboard._handle_registration)
    metabus.subscribe("task.post", blackboard._handle_task_post)
    metabus.subscribe("task.volunteer", blackboard._handle_volunteer)
    metabus.subscribe("task.complete", blackboard._handle_completion)
    metabus.subscribe("metacognition.reflect_request", reflexion_engine._handle_reflection)
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
    orchestrator.attention_router._semantic_matcher = False
    orchestrator.reduction_layer = SimpleNamespace(route=lambda _: {"confidence": 0.0})
    orchestrator.trust = SimpleNamespace(execute=lambda _: SimpleNamespace(allowed=True, reason="local", trust_score=0.8),
                                        learn=lambda *args, **kwargs: None)
    blackboard.registry["code-reviewer"] = AgentCard(agent_id="code-reviewer", name="Revisor",
        description="Revisar código", capabilities=["code_review"], schema={})
    registry = HarnessRegistry(repo_root=str(tmp_path))
    registry._artifacts = []
    registry._harvester = SimpleNamespace(inventory=lambda: {"discovered": 0})
    runtime = RuntimeDouble(available=("codex",))
    autonomous = AutonomousCoordinator(orchestrator, runtime, registry)
    result = WorkflowCoordinator(autonomous, WorkflowStore(tmp_path / "workflows")).run([
        {"id": "analysis", "task": "Revisar código", "required_capabilities": ["code_review"]},
        {"id": "review", "task": "Revise a análise", "required_capabilities": ["code_review"],
         "dependencies": ["analysis"]},
    ])
    assert result["status"] == "completed" and len(runtime.calls) == 2
    assert len(blackboard.tasks) == 2
    assert all(task.status == "completed" for task in blackboard.tasks.values())
    assert blackboard.registry["code-reviewer"].status == "available"
    assert len(metabus.memory.episodic) >= 2
    assert "ENTREGAS DAS DEPENDÊNCIAS" in runtime.calls[1][1]
