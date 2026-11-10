# -*- coding: utf-8 -*-
"""Contrato de runtime e ativação das stop rules (SPEC-935-R1133).

Classifica ações por reversibilidade/risco, avalia o contrato antes da ação e
produz uma decisão auditável: allow, ask, defer ou block. Ações irreversíveis e
de alto risco exigem aprovação humana; o desconhecido falha fechado.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .stop_rules import StopDecision, StopRules, humane_default


class ActionClass(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    IRREVERSIBLE = "irreversible"
    HIGH_RISK = "high_risk"

    @classmethod
    def parse(cls, value: str | "ActionClass") -> "ActionClass":
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError("action_class deve ser texto")
        normalized = value.strip().lower().replace("-", "_")
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError(f"action_class inválida: {value}") from exc


@dataclass(frozen=True)
class ActionRequest:
    action_id: str
    actor_id: str
    tool: str
    action_class: str = "reversible"
    description: str = ""
    human_approved: bool = False
    external_validation: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class RuntimeState:
    session_started_at: float = field(default_factory=time.time)
    session_minutes: float = 0.0
    consecutive_failures: int = 0
    total_failures: int = 0
    total_successes: int = 0
    violations: int = 0
    blocked: int = 0
    asked: int = 0
    deferred: int = 0
    allowed: int = 0
    open_specs: int = 0
    maintenance_minutes: float = 0.0
    productive_minutes: float = 0.0
    context_switches: int = 0
    local_hour: int | None = None
    user_requested_stop: bool = False
    human_approved: bool = False
    forced_stop: bool = False

    def snapshot(self) -> dict[str, Any]:
        hour = self.local_hour if self.local_hour is not None else time.localtime().tm_hour
        return {
            "session_minutes": self.session_minutes,
            "consecutive_failures": self.consecutive_failures,
            "open_specs": self.open_specs,
            "maintenance_minutes": self.maintenance_minutes,
            "productive_minutes": self.productive_minutes,
            "context_switches": self.context_switches,
            "local_hour": hour,
            "user_requested_stop": self.user_requested_stop,
        }

    def record_outcome(self, success: bool) -> None:
        if success:
            self.total_successes += 1
            self.consecutive_failures = 0
        else:
            self.total_failures += 1
            self.consecutive_failures += 1

    def record_decision(self, decision: str) -> None:
        if decision == "allow":
            self.allowed += 1
        elif decision == "ask":
            self.asked += 1
        elif decision == "defer":
            self.deferred += 1
        elif decision == "block":
            self.blocked += 1
            self.violations += 1
        else:
            raise ValueError(f"decisão inválida: {decision}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContractDecision:
    action_id: str
    action_class: str
    decision: str
    rule: str
    reason: str
    requires_human: bool
    requires_external_validation: bool
    humane_default: dict[str, str]
    fingerprint: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContractViolation(RuntimeError):
    """Ação recusada pelo contrato de runtime."""

    def __init__(self, decision: ContractDecision):
        super().__init__(
            f"runtime_contract:{decision.decision}:{decision.rule}:{decision.reason}"
        )
        self.decision = decision


class RuntimeContract:
    """Contrato antes/depois de ações de agente."""

    def __init__(
        self,
        stop_rules: StopRules | None = None,
        *,
        high_risk_requires_human: bool = True,
        high_risk_requires_external_validation: bool = False,
        max_audit_events: int = 1000,
    ) -> None:
        self.stop_rules = stop_rules or StopRules()
        self.high_risk_requires_human = high_risk_requires_human
        self.high_risk_requires_external_validation = high_risk_requires_external_validation
        self.max_audit_events = max_audit_events
        self._audit: list[dict[str, Any]] = []

    def policy(self) -> dict[str, Any]:
        return {
            "action_classes": [item.value for item in ActionClass],
            "high_risk_requires_human": self.high_risk_requires_human,
            "high_risk_requires_external_validation": self.high_risk_requires_external_validation,
            "stop_rules": {
                "max_session_minutes": self.stop_rules.max_session_minutes,
                "max_consecutive_failures": self.stop_rules.max_consecutive_failures,
                "max_open_specs": self.stop_rules.max_open_specs,
                "maintenance_ratio_threshold": self.stop_rules.maintenance_ratio_threshold,
                "quiet_hours": list(self.stop_rules.quiet_hours),
                "max_context_switches": self.stop_rules.max_context_switches,
            },
        }

    def check_state(self, state: RuntimeState) -> StopDecision:
        return self.stop_rules.evaluate(state.snapshot())

    def evaluate(self, request: ActionRequest, state: RuntimeState) -> ContractDecision:
        if not isinstance(request, ActionRequest):
            raise ValueError("request deve ser ActionRequest")
        if not isinstance(state, RuntimeState):
            raise ValueError("state deve ser RuntimeState")

        try:
            action_class = ActionClass.parse(request.action_class)
        except ValueError:
            action_class = ActionClass.HIGH_RISK

        stop = self.check_state(state)
        human = request.human_approved or state.human_approved

        if stop.action == "stop":
            decision = "defer" if action_class is ActionClass.READ_ONLY else "block"
            return self._decision(
                request,
                action_class,
                decision,
                f"stop:{stop.rule}",
                stop.reason,
                requires_human=False,
            )

        if stop.action == "ask" and action_class is not ActionClass.READ_ONLY:
            return self._decision(
                request,
                action_class,
                "ask",
                f"ask:{stop.rule}",
                stop.reason,
                requires_human=True,
            )

        if stop.action == "defer" and action_class is not ActionClass.READ_ONLY:
            return self._decision(
                request,
                action_class,
                "defer",
                f"defer:{stop.rule}",
                stop.reason,
                requires_human=False,
            )

        if action_class is ActionClass.HIGH_RISK:
            if self.high_risk_requires_human and not human:
                return self._decision(
                    request,
                    action_class,
                    "ask",
                    "high_risk_requires_human",
                    "Ação de alto risco exige aprovação humana explícita.",
                    requires_human=True,
                )
            if self.high_risk_requires_external_validation and not request.external_validation:
                return self._decision(
                    request,
                    action_class,
                    "ask",
                    "high_risk_requires_external_validation",
                    "Ação de alto risco exige validação externa explícita.",
                    requires_human=True,
                    requires_external_validation=True,
                )

        if action_class is ActionClass.IRREVERSIBLE and not human:
            return self._decision(
                request,
                action_class,
                "ask",
                "irreversible_requires_human",
                "Ação irreversível exige aprovação humana explícita.",
                requires_human=True,
            )

        return self._decision(
            request,
            action_class,
            "allow",
            "within_policy",
            "Ação permitida pelo contrato.",
            requires_human=False,
        )

    def authorize(self, request: ActionRequest, state: RuntimeState) -> ContractDecision:
        decision = self.evaluate(request, state)
        state.record_decision(decision.decision)
        self._audit.append(decision.to_dict())
        if len(self._audit) > self.max_audit_events:
            self._audit = self._audit[-self.max_audit_events :]
        return decision

    def require(self, request: ActionRequest, state: RuntimeState) -> ContractDecision:
        decision = self.authorize(request, state)
        if decision.decision != "allow":
            raise ContractViolation(decision)
        return decision

    def audit_events(self, limit: int = 50) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        return list(self._audit[-limit:])

    def status(self, state: RuntimeState) -> dict[str, Any]:
        last = self._audit[-1] if self._audit else None
        return {
            "policy": self.policy(),
            "state": state.to_dict(),
            "last_decision": last,
            "audit_events": len(self._audit),
        }

    @staticmethod
    def _decision(
        request: ActionRequest,
        action_class: ActionClass,
        decision: str,
        rule: str,
        reason: str,
        *,
        requires_human: bool,
        requires_external_validation: bool = False,
    ) -> ContractDecision:
        if decision not in {"allow", "ask", "defer", "block"}:
            raise ValueError(f"decisão inválida: {decision}")
        default = humane_default(rule)
        if decision == "allow":
            default = {
                "explanation": "Ação permitida pelo contrato; nenhum limite foi acionado.",
                "alternative": "Nenhuma alternativa necessária.",
                "human_contact": "Revisão humana disponível se solicitada.",
                "exit": "A sessão pode continuar ou ser encerrada a qualquer momento.",
                "rule": rule,
            }
        return ContractDecision(
            action_id=request.action_id,
            action_class=action_class.value,
            decision=decision,
            rule=rule,
            reason=reason,
            requires_human=requires_human or decision == "ask",
            requires_external_validation=requires_external_validation,
            humane_default=default,
            fingerprint=request.fingerprint(),
        )
