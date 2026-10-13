"""Contratos de identidade do primário; executores destes testes são simulados."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest


@pytest.fixture
def gateway(monkeypatch):
    from integrations import ecosystem_mcp as surface
    from marceloclaro import orchestrator, autonomous
    for name in ("_coordinator", "_workflow_coordinator", "_library_orchestrator"):
        monkeypatch.setattr(surface, name, None)
    created = []
    class Primary:
        def __init__(self, *, auto_load_agents):
            assert auto_load_agents is False
            self.loads = 0
            created.append(self)
        def ensure_agents_loaded(self):
            self.loads += 1
        def create_text_task_spec(self, task, criteria):
            return {"spec_id": "SPEC-TASK-CONTROLLED", "task": task, "criteria": criteria,
                    "verification": "criteria_only", "software_delivery": False}
    class Coordinator:
        def __init__(self, orchestrator=None):
            self.orchestrator = orchestrator or Primary(auto_load_agents=False)
    monkeypatch.setattr(orchestrator, "MarceloClaroOrchestrator", Primary)
    monkeypatch.setattr(autonomous, "AutonomousCoordinator", Coordinator)
    return SimpleNamespace(surface=surface, created=created)


def test_library_then_execution_preserves_primary(gateway):
    library = gateway.surface.get_library_orchestrator()
    assert library.loads == 0
    coordinator = gateway.surface.get_coordinator()
    assert coordinator.orchestrator is library
    assert gateway.surface.get_workflow_coordinator().coordinator is coordinator
    assert len(gateway.created) == 1


def test_execution_then_library_preserves_primary(gateway):
    coordinator = gateway.surface.get_coordinator()
    assert gateway.surface.get_library_orchestrator() is coordinator.orchestrator
    assert len(gateway.created) == 1


def test_concurrent_initialization_has_one_primary(gateway):
    def resolve(index):
        if index % 2:
            return gateway.surface.get_coordinator().orchestrator
        return gateway.surface.get_library_orchestrator()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(resolve, range(24)))
    assert all(item is results[0] for item in results)
    assert len(gateway.created) == 1


def test_catalog_is_loaded_once_on_same_primary(monkeypatch):
    from marceloclaro import orchestrator as module
    primary = module.MarceloClaroOrchestrator(auto_load_agents=False)
    calls = []
    monkeypatch.setattr(module, "register_all_agents", lambda bus: calls.append("base"))
    monkeypatch.setattr(module, "register_catalog_agents", lambda bus: calls.append("catalog") or 255)
    monkeypatch.setattr(primary, "register_mira_agent", lambda: calls.append("mira"))
    ensure = getattr(primary, "ensure_agents_loaded", None)
    assert callable(ensure), "O primário precisa carregar seu próprio catálogo idempotentemente."
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: ensure(), range(12)))
    assert calls == ["base", "catalog", "mira"]
    assert primary.catalog_size == 255


def test_text_spec_is_registered_before_executor(gateway):
    tool = getattr(gateway.surface, "ecosystem_text_spec", None)
    assert callable(tool), "A sessão precisa registrar contrato de texto antes de ecosystem_run."
    result = asyncio.run(tool("Revisar arquitetura", ["Declarar limites"]))
    assert result["spec_id"] == "SPEC-TASK-CONTROLLED"
    assert result["software_delivery"] is False
    assert result["verification"] == "criteria_only"
    assert gateway.surface._coordinator is None


def test_invalid_text_spec_does_not_construct_primary(gateway):
    tool = getattr(gateway.surface, "ecosystem_text_spec", None)
    assert callable(tool)
    for task, criteria in (("", ["Limites"]), ("Tarefa", []), ("Tarefa", [""])):
        with pytest.raises(ValueError):
            asyncio.run(tool(task, criteria))
    assert gateway.created == []


def test_actual_text_spec_is_registered_and_remains_text_only():
    from marceloclaro import orchestrator as module
    primary = module.MarceloClaroOrchestrator(auto_load_agents=False)
    result = primary.create_text_task_spec("Revisar arquitetura", ["Declarar limites"])
    spec = module.spec_registry.get(result["spec_id"])
    try:
        assert spec is not None
        assert spec.test_file == ""
        assert spec.requires_trusted_test_evidence is False
        assert primary.sdd_preflight(spec.spec_id) == {
            "ready": True, "red_history_required": False, "verification_scope": "criteria_only"}
        assert result["software_delivery"] is False
    finally:
        module.spec_registry.specs.pop(result["spec_id"], None)


def test_template_requires_spec_before_execution():
    from integrations.opencode_cli import build_config
    template = build_config()["command"]["ecosystem"]["template"]
    assert "ecosystem_text_spec" in template
    assert "spec_id" in template
    assert "RED" in template
