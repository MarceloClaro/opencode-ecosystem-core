# -*- coding: utf-8 -*-
"""
Agent Evaluation Harness — Avaliação Quantitativa de Trajetórias de Agentes
============================================================================
Mede Taxa de Sucesso em Tarefas (TSR), Precisão de Chamadas de Ferramenta e
Eficiência de Trajetória (latência/tokens) com percentis estatísticos.
"""

from __future__ import annotations

import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class EvaluationRun:
    task_id: str
    agent_id: str
    success: bool
    tool_calls_count: int
    tool_calls_correct: int
    duration_seconds: float
    token_cost: int


class AgentEvalHarness:
    """Harness de benchmark e avaliação de trajetórias de agentes."""

    def __init__(self):
        self.runs: List[EvaluationRun] = []

    def record_run(
        self,
        task_id: str,
        agent_id: str,
        success: bool,
        tool_calls_count: int = 1,
        tool_calls_correct: int = 1,
        duration_seconds: float = 1.0,
        token_cost: int = 100,
    ) -> EvaluationRun:
        run = EvaluationRun(
            task_id=task_id,
            agent_id=agent_id,
            success=success,
            tool_calls_count=tool_calls_count,
            tool_calls_correct=tool_calls_correct,
            duration_seconds=duration_seconds,
            token_cost=token_cost,
        )
        self.runs.append(run)
        return run

    def calculate_tsr(self, agent_id: Optional[str] = None) -> float:
        """Calcula a Taxa de Sucesso de Tarefas (Task Success Rate - TSR)."""
        filtered = [r for r in self.runs if agent_id is None or r.agent_id == agent_id]
        if not filtered:
            return 0.0
        successes = sum(1 for r in filtered if r.success)
        return round((successes / len(filtered)) * 100.0, 2)

    def calculate_tool_accuracy(self, agent_id: Optional[str] = None) -> float:
        """Calcula a precisão de chamadas de ferramentas em %."""
        filtered = [r for r in self.runs if agent_id is None or r.agent_id == agent_id]
        total_calls = sum(r.tool_calls_count for r in filtered)
        if total_calls == 0:
            return 100.0
        correct_calls = sum(r.tool_calls_correct for r in filtered)
        return round((correct_calls / total_calls) * 100.0, 2)

    def calculate_percentiles(self, agent_id: Optional[str] = None) -> Dict[str, float]:
        """Calcula percentis P50, P90 e P99 de latência das trajetórias."""
        filtered = [r for r in self.runs if agent_id is None or r.agent_id == agent_id]
        if not filtered:
            return {"p50": 0.0, "p90": 0.0, "p99": 0.0}

        durations = sorted([r.duration_seconds for r in filtered])
        n = len(durations)

        def percentile(p: float) -> float:
            idx = max(0, min(n - 1, int(math.ceil(p * n) - 1)))
            return round(durations[idx], 3)

        return {
            "p50": percentile(0.50),
            "p90": percentile(0.90),
            "p99": percentile(0.99),
        }

    def generate_benchmark_report(self) -> Dict[str, Any]:
        """Gera relatório sintético consolidado de avaliação de desempenho."""
        agents = sorted(list({r.agent_id for r in self.runs}))
        report = {
            "total_runs": len(self.runs),
            "overall_tsr": self.calculate_tsr(),
            "overall_tool_accuracy": self.calculate_tool_accuracy(),
            "latency_percentiles": self.calculate_percentiles(),
            "by_agent": {},
        }
        for agent in agents:
            report["by_agent"][agent] = {
                "tsr": self.calculate_tsr(agent),
                "tool_accuracy": self.calculate_tool_accuracy(agent),
                "latency_percentiles": self.calculate_percentiles(agent),
            }
        return report


agent_eval_harness = AgentEvalHarness()
