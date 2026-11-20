"""R1254: preflight fail-closed e contrato MCP explícito para delegação."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from marceloclaro.autonomous import AutonomousCoordinator
from marceloclaro.workflow import WorkflowCoordinator


class MemoryStore:
    def __init__(self):
        self.records = {}
        self.locked = False

    def create(self, workflow_id, definition):
        self.records[workflow_id] = {"definition": definition}

    def save(self, workflow_id, record):
        self.records[workflow_id] = record

    def load(self, workflow_id):
        return self.records[workflow_id]


class SddCoordinator:
    def __init__(self, store, decisions):
        self.store = store
        self.decisions = decisions
        self.preflight_calls = []
        self.run_calls = []

    def preflight_spec(self, spec_id=None):
        self.preflight_calls.append(spec_id)
        return self.decisions.get(spec_id, {"ready": True, "verification_scope": "fixture"})

    def run(self, task, required_capabilities=None, max_steps=1, timeout=120,
            ecosystem=None, spec_id=None):
        self.run_calls.append({"task": task, "spec_id": spec_id})
        return {"status": "completed", "success": True, "steps": 1,
                "task_id": f"task-{len(self.run_calls)}", "output": "Saída local simulada."}


def test_missing_or_unknown_spec_blocks_before_checkpoint_and_dispatch():
    for spec_id, reason in ((None, "spec_id_required"),
                            ("SPEC-NOT-REGISTERED", "spec_not_found")):
        store = MemoryStore()
        coordinator = SddCoordinator(store, {
            spec_id: {"ready": False, "error": reason, "red_history_required": True}
        })
        node = {"id": "review", "task": "Revisar a entrega"}
        if spec_id is not None:
            node["spec_id"] = spec_id

        result = WorkflowCoordinator(coordinator, store).run([node], workflow_id="blocked-review")

        assert result["status"] == "blocked" and result["success"] is False
        assert result["error"] == "sdd_preflight_failed"
        assert result["steps"] == 0 and result["checkpoint_created"] is False
        assert result["workflow_id"] is None
        assert result["sdd_preflight"]["failed_nodes"] == [
            {"node_id": "review", "spec_id": spec_id, "error": reason}
        ]
        assert store.records == {}
        assert coordinator.run_calls == []
        assert coordinator.preflight_calls == [spec_id]


def test_invalid_node_blocks_entire_workflow_before_any_dispatch():
    store = MemoryStore()
    coordinator = SddCoordinator(store, {
        "SPEC-INVALID": {"ready": False, "error": "spec_not_found"},
    })
    result = WorkflowCoordinator(coordinator, store).run([
        {"id": "valid", "task": "Analisar", "spec_id": "SPEC-VALID"},
        {"id": "invalid", "task": "Revisar", "spec_id": "SPEC-INVALID"},
    ], workflow_id="all-or-nothing")

    assert result["status"] == "blocked"
    assert result["sdd_preflight"]["failed_nodes"] == [
        {"node_id": "invalid", "spec_id": "SPEC-INVALID", "error": "spec_not_found"}
    ]
    assert coordinator.preflight_calls == ["SPEC-VALID", "SPEC-INVALID"]
    assert coordinator.run_calls == [] and store.records == {}


def test_valid_spec_is_preflighted_and_forwarded_to_node():
    store = MemoryStore()
    coordinator = SddCoordinator(store, {})
    result = WorkflowCoordinator(coordinator, store).run([
        {"id": "review", "task": "Revisar", "spec_id": "TSPEC-valid"}
    ])

    assert result["status"] == "completed"
    assert coordinator.preflight_calls == ["TSPEC-valid"]
    assert coordinator.run_calls == [{"task": "Revisar", "spec_id": "TSPEC-valid"}]


def test_mcp_workflow_schema_documents_spec_id_and_node_budget():
    from integrations import ecosystem_mcp

    async def get_tool():
        return next(tool for tool in await ecosystem_mcp.mcp.list_tools()
                    if tool.name == "ecosystem_workflow")

    tool = asyncio.run(get_tool())
    node_schema = tool.inputSchema["properties"]["nodes"]["items"]
    node_properties = node_schema["properties"]
    assert "spec_id" in node_properties
    assert "per_node_max_steps" in node_properties
    assert "spec_id" in tool.description
    assert "SDD estrito" in tool.description


def test_non_strict_mode_keeps_legacy_workflow_without_spec_id():
    orchestrator = SimpleNamespace(strict_sdd=False, sdd_preflight=lambda _spec_id: None)
    autonomous = AutonomousCoordinator(orchestrator=orchestrator)

    result = autonomous.preflight_spec(None)

    assert result["ready"] is True
    assert result["verification_scope"] == "legacy_compatible"


def test_spec_preflight_delegates_known_and_unknown_ids():
    calls = []

    def sdd_preflight(spec_id):
        calls.append(spec_id)
        return {"ready": spec_id == "SPEC-KNOWN", "error": None if spec_id == "SPEC-KNOWN" else "spec_not_found"}

    autonomous = AutonomousCoordinator(orchestrator=SimpleNamespace(strict_sdd=True, sdd_preflight=sdd_preflight))

    assert autonomous.preflight_spec("SPEC-KNOWN")["ready"] is True
    assert autonomous.preflight_spec("SPEC-UNKNOWN")["error"] == "spec_not_found"
    assert calls == ["SPEC-KNOWN", "SPEC-UNKNOWN"]
