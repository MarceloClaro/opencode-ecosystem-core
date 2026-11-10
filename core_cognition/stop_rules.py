# -*- coding: utf-8 -*-
"""Regras de parada e padrões humanos (SPEC-935-R1132).

Decide entre continuar, perguntar, adiar e parar. Toda decisão inclui
explicação, alternativa, contato humano e saída. As regras são deliberadamente
simples e auditáveis; não substituem julgamento clínico ou decisão do operador.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


def humane_default(rule: str) -> dict[str, str]:
    """Caminho humano para quando o sistema não deve insistir."""

    return {
        "explanation": (
            "A operação encontrou um limite explícito; o sistema não vai insistir "
            "automaticamente."
        ),
        "alternative": (
            "Reduza o escopo, tente uma rota mais simples ou peça revisão de outra pessoa."
        ),
        "human_contact": (
            "Se o bloqueio persistir, procure revisão humana antes de continuar."
        ),
        "exit": (
            "Você pode encerrar a sessão e retomar depois; o estado deve estar preservado."
        ),
        "rule": rule,
    }


@dataclass(frozen=True)
class StopDecision:
    action: str
    rule: str
    reason: str
    humane_default: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StopRules:
    max_session_minutes: int = 120
    max_consecutive_failures: int = 3
    max_open_specs: int = 25
    maintenance_ratio_threshold: float = 1.0
    quiet_hours: tuple[int, int] = (22, 7)
    max_context_switches: int = 20

    def evaluate(self, state: dict[str, Any]) -> StopDecision:
        if not isinstance(state, dict):
            raise ValueError("state deve ser um objeto")

        if state.get("user_requested_stop") is True:
            return self._decision("stop", "user_requested_stop", "O usuário pediu para parar.")

        failures = self._number(state.get("consecutive_failures", 0), "consecutive_failures")
        if failures >= self.max_consecutive_failures:
            return self._decision(
                "ask",
                "consecutive_failures",
                f"{int(failures)} falhas consecutivas; peça orientação antes de tentar de novo.",
            )

        minutes = self._number(state.get("session_minutes", 0), "session_minutes")
        if minutes >= self.max_session_minutes:
            return self._decision(
                "stop",
                "session_budget",
                f"Sessão de {minutes:g} minutos atingiu o orçamento de {self.max_session_minutes}.",
            )

        maintenance = self._number(state.get("maintenance_minutes", 0), "maintenance_minutes")
        productive = self._number(state.get("productive_minutes", 0), "productive_minutes")
        if productive > 0 and maintenance / productive >= self.maintenance_ratio_threshold:
            return self._decision(
                "ask",
                "maintenance_ratio",
                "O tempo de manutenção está maior ou igual ao tempo produtivo.",
            )

        open_specs = self._number(state.get("open_specs", 0), "open_specs")
        if open_specs >= self.max_open_specs:
            return self._decision(
                "ask",
                "open_specs",
                f"{int(open_specs)} especificações abertas; reduza o escopo antes de abrir novas.",
            )

        switches = self._number(state.get("context_switches", 0), "context_switches")
        if switches >= self.max_context_switches:
            return self._decision(
                "ask",
                "context_switches",
                f"{int(switches)} trocas de contexto; consolide antes de continuar.",
            )

        hour = self._number(state.get("local_hour", 12), "local_hour")
        if not 0 <= hour <= 23:
            raise ValueError("local_hour deve estar em [0, 23]")
        if self._in_quiet_hours(int(hour)):
            return self._decision(
                "defer",
                "quiet_hours",
                "Horário de silêncio; a decisão pode esperar.",
            )

        return self._decision("continue", "within_budget", "Dentro dos limites declarados.")

    @staticmethod
    def _number(value: Any, field: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} deve ser numérico")
        if value < 0:
            raise ValueError(f"{field} não pode ser negativo")
        return float(value)

    def _in_quiet_hours(self, hour: int) -> bool:
        start, end = self.quiet_hours
        if not (0 <= start <= 23 and 0 <= end <= 23):
            raise ValueError("quiet_hours deve conter horas em [0, 23]")
        if start == end:
            return False
        if start < end:
            return start <= hour < end
        return hour >= start or hour < end

    @staticmethod
    def _decision(action: str, rule: str, reason: str) -> StopDecision:
        if action not in {"continue", "ask", "defer", "stop"}:
            raise ValueError(f"ação inválida: {action}")
        return StopDecision(
            action=action,
            rule=rule,
            reason=reason,
            humane_default=humane_default(rule),
        )
