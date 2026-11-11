"""R1148 — contrato de runtime, hooks e circuit breaker."""
from __future__ import annotations

import json

import pytest

from core_cognition.runtime_contract import (
    RuntimeContract as CoreRuntimeContract,
)
from mci import runtime_contract


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _contract(**kwargs):
    contract = runtime_contract.RuntimeContract(**kwargs)
    # Fixa horário produtivo para não depender de quiet_hours do relógio local.
    contract.core_state.local_hour = 14
    return contract


def test_read_only_action_executes():
    contract = _contract()
    result = contract.execute(
        {"action_id": "read", "action_class": "read_only"},
        lambda payload: 42,
    )
    assert result["status"] == "executed"
    assert result["result"] == 42
    assert result["breaker"]["state"] == "closed"


def test_irreversible_requires_approval_and_token():
    called = []
    contract = _contract()
    request = {"action_id": "delete", "action_class": "irreversible"}
    blocked = contract.execute(request, lambda payload: called.append(1))
    assert blocked["status"] == "escalated"
    assert blocked["human_escalation"] is True
    assert called == []

    no_token = contract.execute(
        {**request, "approved": True}, lambda payload: called.append(1)
    )
    assert no_token["status"] == "escalated"
    assert no_token["reason"] == "approval_token_required"
    assert called == []

    executed = contract.execute(
        {**request, "approved": True, "approval_token": "tok-1"},
        lambda payload: "ok",
    )
    assert executed["status"] == "executed"
    assert executed["result"] == "ok"


def test_before_hook_can_deny():
    contract = _contract()
    contract.register_hook(
        "before",
        lambda request: {"allow": False, "reason": "budget_exceeded"},
    )
    result = contract.execute(
        {"action_id": "x", "action_class": "read_only"},
        lambda payload: "never",
    )
    assert result["status"] == "blocked"
    assert result["reason"] == "budget_exceeded"


def test_after_hook_sees_outcome():
    seen = []
    contract = _contract()
    contract.register_hook("after", lambda request, outcome: seen.append(outcome))
    contract.execute(
        {"action_id": "x", "action_class": "reversible"},
        lambda payload: 7,
    )
    assert seen[0]["status"] == "executed"
    assert seen[0]["result"] == 7


def test_circuit_breaker_opens_and_recovers():
    clock = FakeClock()
    breaker = runtime_contract.CircuitBreaker(
        failure_threshold=3, cooldown_seconds=60, clock=clock
    )
    contract = _contract(breaker=breaker, clock=clock)

    def fail(payload):
        raise RuntimeError("falha")

    for _ in range(3):
        result = contract.execute(
            {"action_id": "x", "action_class": "read_only"}, fail
        )
        assert result["status"] == "failed"
    assert breaker.state == "open"
    blocked = contract.execute(
        {"action_id": "x", "action_class": "read_only"}, lambda payload: 1
    )
    assert blocked["status"] == "blocked"
    assert blocked["reason"] == "circuit_open"

    clock.advance(61)
    recovered = contract.execute(
        {"action_id": "x", "action_class": "read_only"}, lambda payload: 1
    )
    assert recovered["status"] == "executed"
    assert breaker.state == "closed"


def test_audit_jsonl_is_written(tmp_path):
    path = tmp_path / "audit.jsonl"
    contract = _contract(audit_path=path)
    contract.execute(
        {"action_id": "x", "action_class": "read_only"},
        lambda payload: 1,
    )
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["action_id"] == "x"
    assert record["status"] == "executed"


def test_invalid_action_class_is_rejected():
    contract = _contract()
    with pytest.raises(ValueError):
        contract.execute(
            {"action_id": "x", "action_class": "unknown"}, lambda payload: 1
        )


def test_adapter_uses_core_runtime_contract():
    contract = _contract()
    assert isinstance(contract.core_contract, CoreRuntimeContract)
    result = contract.execute(
        {"action_id": "read", "action_class": "read_only"},
        lambda payload: 1,
    )
    assert result["status"] == "executed"
    assert contract.core_state.allowed == 1
    assert contract.core_contract.audit_events(limit=1)
    assert result["core_decision"]["decision"] == "allow"


def test_core_stop_state_blocks_action():
    contract = _contract()
    contract.core_state.user_requested_stop = True
    result = contract.execute(
        {"action_id": "read", "action_class": "read_only"},
        lambda payload: 1,
    )
    assert result["status"] == "blocked"
    assert result["reason"].startswith("runtime_contract:stop:")
    assert result["core_decision"]["decision"] in {"defer", "block"}


def test_quiet_hours_blocks_non_read_only():
    contract = _contract()
    contract.core_state.local_hour = 23
    result = contract.execute(
        {"action_id": "x", "action_class": "reversible"},
        lambda payload: 1,
    )
    assert result["status"] == "blocked"
    assert "quiet_hours" in result["reason"]


def test_core_ask_escalates_irreversible():
    contract = _contract()
    result = contract.execute(
        {"action_id": "delete", "action_class": "irreversible"},
        lambda payload: "never",
    )
    assert result["status"] == "escalated"
    assert result["reason"] == "approval_required"
    assert result["core_decision"]["rule"] == "irreversible_requires_human"


def test_core_state_tracks_failures():
    contract = _contract()

    def fail(payload):
        raise RuntimeError("falha")

    contract.execute(
        {"action_id": "x", "action_class": "read_only"}, fail
    )
    assert contract.core_state.consecutive_failures == 1
    assert contract.core_state.total_failures == 1
