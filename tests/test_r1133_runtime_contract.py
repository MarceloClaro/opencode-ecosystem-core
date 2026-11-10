# -*- coding: utf-8 -*-
"""Testes do contrato de runtime e ativação das stop rules (R1133)."""

from __future__ import annotations

import pytest

from core_cognition.runtime_contract import (
    ActionClass,
    ActionRequest,
    ContractViolation,
    RuntimeContract,
    RuntimeState,
)
from marceloclaro.orchestrator import MarceloClaroOrchestrator


def _state(**overrides):
    payload = {
        "local_hour": 12,
        "session_minutes": 0,
        "consecutive_failures": 0,
    }
    payload.update(overrides)
    return RuntimeState(**payload)


def _request(action_class="reversible", **overrides):
    payload = {
        "action_id": "act-1",
        "actor_id": "agent-x",
        "tool": "test",
        "action_class": action_class,
    }
    payload.update(overrides)
    return ActionRequest(**payload)


def test_contract_allows_read_only_on_stop():
    contract = RuntimeContract()
    decision = contract.authorize(_request("read_only"), _state(session_minutes=130))
    assert decision.decision == "defer"
    assert decision.rule == "stop:session_budget"


def test_contract_blocks_reversible_on_stop():
    contract = RuntimeContract()
    decision = contract.authorize(_request("reversible"), _state(session_minutes=130))
    assert decision.decision == "block"
    assert decision.rule == "stop:session_budget"


def test_contract_asks_irreversible_without_human():
    contract = RuntimeContract()
    decision = contract.authorize(_request("irreversible"), _state())
    assert decision.decision == "ask"
    assert decision.rule == "irreversible_requires_human"
    assert decision.requires_human is True


def test_contract_allows_irreversible_with_human():
    contract = RuntimeContract()
    decision = contract.authorize(
        _request("irreversible", human_approved=True), _state()
    )
    assert decision.decision == "allow"


def test_contract_asks_high_risk_without_human():
    contract = RuntimeContract()
    decision = contract.authorize(_request("high_risk"), _state())
    assert decision.decision == "ask"
    assert decision.rule == "high_risk_requires_human"


def test_contract_high_risk_external_validation():
    contract = RuntimeContract(high_risk_requires_external_validation=True)
    decision = contract.authorize(
        _request("high_risk", human_approved=True, external_validation=False),
        _state(),
    )
    assert decision.decision == "ask"
    assert decision.rule == "high_risk_requires_external_validation"


def test_contract_unknown_class_fails_closed():
    contract = RuntimeContract()
    decision = contract.authorize(_request("nonsense"), _state())
    assert decision.action_class == ActionClass.HIGH_RISK.value
    assert decision.decision == "ask"
    assert decision.rule == "high_risk_requires_human"


def test_contract_quiet_hours_defers_reversible():
    contract = RuntimeContract()
    decision = contract.authorize(_request("reversible"), _state(local_hour=23))
    assert decision.decision == "defer"
    assert decision.rule == "defer:quiet_hours"


def test_contract_require_raises():
    contract = RuntimeContract()
    with pytest.raises(ContractViolation) as excinfo:
        contract.require(_request("reversible"), _state(session_minutes=130))
    assert excinfo.value.decision.decision == "block"


def test_runtime_state_records_outcomes():
    state = _state()
    state.record_outcome(False)
    state.record_outcome(False)
    state.record_outcome(False)
    assert state.total_failures == 3
    assert state.consecutive_failures == 3
    state.record_outcome(True)
    assert state.total_successes == 1
    assert state.consecutive_failures == 0


def test_contract_audit_bounded():
    contract = RuntimeContract(max_audit_events=3)
    for index in range(5):
        contract.authorize(
            _request("read_only", action_id=f"act-{index}"),
            _state(),
        )
    assert len(contract.audit_events(10)) == 3


def test_orchestrator_authorize_action_blocks_on_stop():
    orch = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
    orch.update_runtime_context(local_hour=12, session_minutes=130)
    blocked = orch.authorize_action("delegate:x", "reversible")
    assert blocked.decision == "block"
    read_only = orch.authorize_action("inspect:x", "read_only")
    assert read_only.decision == "defer"
    orch.update_runtime_context(session_minutes=0)
    allowed = orch.authorize_action("delegate:x", "reversible")
    assert allowed.decision == "allow"


def test_orchestrator_dispatch_blocks_when_stopped():
    orch = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
    graph = orch.nanogranulate("teste r1133", required_capabilities=["python"])
    graph_id = orch.submit_graph(graph)
    ready = list(orch.task_runtime.ready_tasks(graph_id))
    assert ready
    orch.update_runtime_context(local_hour=12, session_minutes=130)
    assert orch.dispatch_ready(graph_id) == ()
    assert list(orch.task_runtime.ready_tasks(graph_id)) == []
    explanation = orch.explain_assignment(graph_id, ready[0].task_id)
    assert "runtime_contract" in explanation["blocked_reason"]
    assert explanation["contract"]["decision"] == "block"


def test_orchestrator_report_completion_records_failure():
    orch = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
    orch.report_completion("task-x", "agent-x", {}, success=False)
    assert orch._runtime_state.total_failures == 1
    assert orch._runtime_state.consecutive_failures == 1
