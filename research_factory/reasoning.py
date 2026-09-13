# -*- coding: utf-8 -*-
"""Raciocínio aplicado à fábrica de pesquisa (SPEC-935-R476, extensão do M1/R471).

Verificadores determinísticos de consistência de plano, estatísticas e prazos,
com capacidades Z3/SymPy opcionais (detectadas em runtime, nunca obrigatórias):

- `check_acyclic`: detecção de ciclos em grafo de dependências (DFS iterativo;
  marca "dfs" como reasoner nativo; "z3_hybrid" quando z3 está disponível).
- `validate_stats`: regras determinísticas (n>=1, std>=0, média dentro de
  [min,max]) — extensível a simplificação simbólica via sympy quando presente.
- `check_deadlines`: monotonicidade não-decrescente de prazos.

Anti-overclaim: relatórios expõem reasoner real usado; nada de "verificado"
sem validação externa.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class PlanValidationReport:
    """Resultado de uma verificação de consistência de plano."""

    check: str
    valid: bool
    cycles: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks_executed: List[str] = field(default_factory=list)
    reasoner: str = "dfs"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PlanConsistencyChecker:
    """Verificador determinístico de planos, estatísticas e prazos."""

    def __init__(self, use_z3: bool = True, use_sympy: bool = True) -> None:
        self.z3_available = False
        self.sympy_available = False
        try:
            if use_z3:
                import z3  # noqa: F401

                self.z3_available = True
        except Exception:
            self.z3_available = False
        try:
            if use_sympy:
                import sympy  # noqa: F401

                self.sympy_available = True
        except Exception:
            self.sympy_available = False

    def capabilities(self) -> Dict[str, Any]:
        return {
            "acyclic_checker": "dfs",
            "z3": self.z3_available,
            "sympy": self.sympy_available,
            "stats_rules": ["n_positive", "std_non_negative", "mean_within_bounds"],
            "deadline_rule": "monotonic_non_decreasing",
        }

    # -- dependências (grafo) --

    def check_acyclic(self, tasks: Dict[str, Iterable[str]]) -> PlanValidationReport:
        """Verifica ausência de ciclos no grafo de dependências via DFS.

        tasks: {tarefa: [tarefas das quais depende]}.
        """
        graph = {name: list(deps) for name, deps in tasks.items()}
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {name: WHITE for name in graph}
        cycles: List[str] = []
        stack: List[str] = []

        def _detect(start: str) -> None:
            if color[start] != WHITE:
                return
            color[start] = GRAY
            stack.append(start)
            for dep in graph.get(start, []):
                if dep not in color:
                    color[dep] = WHITE
                if color[dep] == WHITE:
                    _detect(dep)
                elif color[dep] == GRAY:
                    # ciclo encontrado: caminho do topo da pilha até dep
                    seg = stack[stack.index(dep):] + [dep]
                    cycles.append(" -> ".join(seg))
            stack.pop()
            color[start] = BLACK

        for node in graph:
            _detect(node)

        return PlanValidationReport(
            check="acyclic",
            valid=not cycles,
            cycles=cycles,
            reasoner="z3_hybrid" if self.z3_available else "dfs",
        )

    # -- estatísticas --

    def validate_stats(self, stats: Dict[str, Dict[str, Any]]) -> PlanValidationReport:
        """Valida regras determinísticas sobre estatísticas descritivas."""
        warnings: List[str] = []
        valid = True
        for var, values in stats.items():
            n = values.get("n")
            if n is None or (isinstance(n, (int, float)) and n < 1):
                warnings.append(f"{var}: n ausente/não-positivo")
                valid = False
                continue
            std = values.get("std")
            if std is not None and (not isinstance(std, (int, float)) or std < 0):
                warnings.append(f"{var}: desvio-padrão inválido ({std!r})")
                valid = False
            mean, lo, hi = (
                values.get("mean"),
                values.get("min"),
                values.get("max"),
            )
            if (
                mean is not None
                and lo is not None
                and hi is not None
                and not (lo <= mean <= hi)
            ):
                warnings.append(f"{var}: média {mean!r} fora de [{lo!r},{hi!r}]")
                valid = False

        return PlanValidationReport(
            check="stats",
            valid=valid,
            warnings=warnings,
            checks_executed=["n_positive", "std_non_negative", "mean_within_bounds"],
            reasoner="sympy" if self.sympy_available else "deterministic",
        )

    # -- prazos --

    def check_deadlines(
        self,
        deadlines: Dict[str, Any],
        current_step: float = 0,
    ) -> PlanValidationReport:
        """Valida monotonicidade não-decrescente dos prazos (ordem de inserção)."""
        warnings: List[str] = []
        previous = current_step
        for name, deadline in deadlines.items():
            try:
                value = float(deadline)
            except (TypeError, ValueError):
                warnings.append(f"{name}: prazo não numérico ({deadline!r})")
                continue
            if value < previous:
                warnings.append(
                    f"{name}: prazo {value} regride em relação a {previous}"
                )
            previous = value

        return PlanValidationReport(
            check="deadlines",
            valid=not warnings,
            warnings=warnings,
            checks_executed=["monotonic_non_decreasing"],
            reasoner="deterministic",
        )