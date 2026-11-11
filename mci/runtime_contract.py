"""R1148 — contrato de runtime com classes de ação, hooks e circuit breaker.

Toda ação passa por:

1. classe de risco (`read_only`, `reversible`, `irreversible`, `high_risk`);
2. hooks `before` (podem negar) e `after` (observam o outcome);
3. aprovação humana explícita para ações irreversíveis/altíssimo risco;
4. circuit breaker por falhas consecutivas;
5. auditoria JSONL opcional.

Não executa hardware, rede ou ferramenta externa por si só; envolve um callable
fornecido pelo operador. A aprovação não é inferida de texto.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from core_cognition.runtime_contract import (
    ActionClass as CoreActionClass,
    ActionRequest as CoreActionRequest,
    RuntimeContract as CoreRuntimeContract,
    RuntimeState as CoreRuntimeState,
)

LIMITS = (
    "Adaptador de execução sobre core_cognition.runtime_contract. Não prova "
    "segurança, autorização legal ou ausência de efeitos colaterais. Aprovação "
    "humana é explícita e auditada; o circuit breaker reduz repetição, não "
    "elimina risco."
)
ACTION_CLASSES = {
    CoreActionClass.READ_ONLY.value: {"risk": 0.0, "requires_approval": False},
    CoreActionClass.REVERSIBLE.value: {"risk": 0.3, "requires_approval": False},
    CoreActionClass.IRREVERSIBLE.value: {"risk": 0.7, "requires_approval": True},
    CoreActionClass.HIGH_RISK.value: {"risk": 1.0, "requires_approval": True},
}


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        cooldown_seconds: float = 60.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if int(failure_threshold) < 1:
            raise ValueError("failure_threshold deve ser >= 1")
        if float(cooldown_seconds) < 0:
            raise ValueError("cooldown_seconds deve ser >= 0")
        self.failure_threshold = int(failure_threshold)
        self.cooldown_seconds = float(cooldown_seconds)
        self._clock = clock or time.monotonic
        self._failures = 0
        self._state = "closed"
        self._opened_at = None

    @property
    def state(self) -> str:
        return self._state

    def allow(self) -> bool:
        if self._state == "closed":
            return True
        if self._state == "open":
            if self._clock() - float(self._opened_at or 0.0) >= self.cooldown_seconds:
                self._state = "half_open"
                return True
            return False
        return True

    def record_success(self) -> None:
        self._failures = 0
        self._state = "closed"
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._state = "open"
            self._opened_at = self._clock()

    def status(self) -> dict:
        return {
            "state": self._state,
            "failures": self._failures,
            "failure_threshold": self.failure_threshold,
            "cooldown_seconds": self.cooldown_seconds,
        }


@dataclass
class ExecutionRecord:
    action_id: str
    action_class: str
    status: str
    elapsed_seconds: float
    reasons: list[str] = field(default_factory=list)
    error: str | None = None
    core_decision: dict | None = None

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "action_class": self.action_class,
            "status": self.status,
            "elapsed_seconds": self.elapsed_seconds,
            "reasons": self.reasons,
            "error": self.error,
            "core_decision": self.core_decision,
        }


class RuntimeContract:
    def __init__(
        self,
        *,
        hooks: dict | None = None,
        breaker: CircuitBreaker | None = None,
        audit_path: str | Path | None = None,
        clock: Callable[[], float] | None = None,
        core_contract: CoreRuntimeContract | None = None,
        core_state: CoreRuntimeState | None = None,
    ) -> None:
        self.hooks = {"before": [], "after": []}
        for event, callbacks in (hooks or {}).items():
            if event not in self.hooks:
                raise ValueError(f"evento de hook inválido: {event}")
            for callback in callbacks:
                self.register_hook(event, callback)
        self.breaker = breaker or CircuitBreaker(clock=clock)
        self.audit_path = Path(audit_path) if audit_path else None
        self._clock = clock or time.monotonic
        self.core_contract = core_contract or CoreRuntimeContract()
        self.core_state = core_state or CoreRuntimeState()

    def register_hook(self, event: str, callback: Callable) -> None:
        if event not in self.hooks:
            raise ValueError(f"evento de hook inválido: {event}")
        if not callable(callback):
            raise ValueError("hook deve ser callable")
        self.hooks[event].append(callback)

    def _audit(self, record: dict) -> None:
        if self.audit_path is None:
            return
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def execute(self, request: dict, action: Callable) -> dict:
        action_class = str(request.get("action_class", "")).strip()
        if action_class not in ACTION_CLASSES:
            raise ValueError(f"action_class inválida: {action_class}")
        if not callable(action):
            raise ValueError("action deve ser callable")
        action_id = str(request.get("action_id", "")).strip()
        if not action_id:
            raise ValueError("action_id obrigatório")
        policy = ACTION_CLASSES[action_class]
        started = self._clock()
        reasons = []
        if not self.breaker.allow():
            record = ExecutionRecord(
                action_id, action_class, "blocked", 0.0,
                reasons=["circuit_open"],
            )
            self._audit(record.to_dict())
            return {
                "status": "blocked",
                "action_id": action_id,
                "action_class": action_class,
                "reason": "circuit_open",
                "breaker": self.breaker.status(),
            }
        for hook in self.hooks["before"]:
            decision = hook(request)
            if isinstance(decision, dict) and decision.get("allow") is False:
                reasons.append(str(decision.get("reason", "hook_denied")))
                record = ExecutionRecord(
                    action_id, action_class, "blocked", 0.0, reasons=reasons
                )
                self._audit(record.to_dict())
                return {
                    "status": "blocked",
                    "action_id": action_id,
                    "action_class": action_class,
                    "reason": reasons[-1],
                }
        core_request = CoreActionRequest(
            action_id=action_id,
            actor_id=str(request.get("actor_id", "marceloclaro")),
            tool=str(request.get("tool", action_id)),
            action_class=action_class,
            description=str(request.get("description", "")),
            human_approved=bool(request.get("approved")),
            metadata={"source": "mci.runtime_contract"},
        )
        core_decision = self.core_contract.authorize(core_request, self.core_state)
        core_payload = core_decision.to_dict()
        if core_decision.decision == "ask":
            reasons.append(f"runtime_contract:{core_decision.rule}")
            record = ExecutionRecord(
                action_id, action_class, "escalated", 0.0,
                reasons=reasons, core_decision=core_payload,
            )
            self._audit(record.to_dict())
            return {
                "status": "escalated",
                "action_id": action_id,
                "action_class": action_class,
                "reason": "approval_required",
                "human_escalation": True,
                "core_decision": core_payload,
            }
        if core_decision.decision in {"defer", "block"}:
            reasons.append(f"runtime_contract:{core_decision.rule}")
            record = ExecutionRecord(
                action_id, action_class, "blocked", 0.0,
                reasons=reasons, core_decision=core_payload,
            )
            self._audit(record.to_dict())
            return {
                "status": "blocked",
                "action_id": action_id,
                "action_class": action_class,
                "reason": f"runtime_contract:{core_decision.rule}",
                "core_decision": core_payload,
            }
        if policy["requires_approval"] and not str(
            request.get("approval_token", "")
        ).strip():
            reasons.append("approval_token_required")
            record = ExecutionRecord(
                action_id, action_class, "escalated", 0.0,
                reasons=reasons, core_decision=core_payload,
            )
            self._audit(record.to_dict())
            return {
                "status": "escalated",
                "action_id": action_id,
                "action_class": action_class,
                "reason": "approval_token_required",
                "human_escalation": True,
                "core_decision": core_payload,
            }
        try:
            result = action(request.get("payload", {}))
        except Exception as exc:  # noqa: BLE001 - contrato registra a falha
            elapsed = self._clock() - started
            self.breaker.record_failure()
            self.core_state.record_outcome(False)
            outcome = {
                "status": "failed",
                "action_id": action_id,
                "action_class": action_class,
                "error": repr(exc),
                "elapsed_seconds": elapsed,
                "breaker": self.breaker.status(),
                "core_decision": core_payload,
            }
            for hook in self.hooks["after"]:
                hook(request, outcome)
            record = ExecutionRecord(
                action_id, action_class, "failed", elapsed,
                reasons=reasons, error=repr(exc), core_decision=core_payload,
            )
            self._audit(record.to_dict())
            return outcome
        elapsed = self._clock() - started
        self.breaker.record_success()
        self.core_state.record_outcome(True)
        outcome = {
            "status": "executed",
            "action_id": action_id,
            "action_class": action_class,
            "result": result,
            "elapsed_seconds": elapsed,
            "breaker": self.breaker.status(),
            "core_decision": core_payload,
        }
        for hook in self.hooks["after"]:
            hook(request, outcome)
        record = ExecutionRecord(
            action_id, action_class, "executed", elapsed,
            reasons=reasons, core_decision=core_payload,
        )
        self._audit(record.to_dict())
        return outcome
