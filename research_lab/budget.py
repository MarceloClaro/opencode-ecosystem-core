"""Budget determinístico para uma execução de pesquisa local."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import math


class BudgetExceeded(RuntimeError):
    """O consumo ultrapassaria um limite declarado."""


@dataclass
class Budget:
    max_steps: int = 8
    max_seconds: float = 60.0
    max_cost_usd: float = 0.0
    max_external_calls: int = 0
    used_steps: int = 0
    used_seconds: float = 0.0
    used_cost_usd: float = 0.0
    used_external_calls: int = 0

    def __post_init__(self):
        for name in ("max_steps", "max_external_calls"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} deve ser inteiro não negativo")
        for name in ("max_seconds", "max_cost_usd"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float))                     or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} deve ser finito e não negativo")

    def consume(self, *, step_seconds: float = 0.0, cost_usd: float = 0.0,
                external_calls: int = 0) -> dict:
        if isinstance(step_seconds, bool) or not isinstance(step_seconds, (int, float))                 or not math.isfinite(step_seconds) or step_seconds < 0:
            raise ValueError("step_seconds inválido")
        if isinstance(cost_usd, bool) or not isinstance(cost_usd, (int, float))                 or not math.isfinite(cost_usd) or cost_usd < 0:
            raise ValueError("cost_usd inválido")
        if type(external_calls) is not int or external_calls < 0:
            raise ValueError("external_calls inválido")
        if self.used_steps + 1 > self.max_steps:
            raise BudgetExceeded("limite de passos")
        if self.used_seconds + step_seconds > self.max_seconds + 1e-9:
            raise BudgetExceeded("limite de tempo")
        if self.used_cost_usd + cost_usd > self.max_cost_usd + 1e-12:
            raise BudgetExceeded("limite de custo")
        if self.used_external_calls + external_calls > self.max_external_calls:
            raise BudgetExceeded("limite de chamadas externas")
        self.used_steps += 1
        self.used_seconds += step_seconds
        self.used_cost_usd += cost_usd
        self.used_external_calls += external_calls
        return self.snapshot()

    def snapshot(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        if not isinstance(data, dict):
            raise ValueError("budget inválido")
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in allowed})
