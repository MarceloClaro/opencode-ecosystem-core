# -*- coding: utf-8 -*-
"""Trajectory — sinais operacionais conservadores (SPEC-935-R505).

Trajetória é dado de execução/avaliação, NÃO prova de afirmação de domínio.
Extrai apenas o que é conhecido: steps, failures, tool_calls, duration_s,
retries, retry_like, terminal_state. Falha de provisionamento de runner não
é contada como aprovação nem como falha de step.
"""
from __future__ import annotations

from hermes_bridge.contracts import TrajectoryEvent


def extract_trajectory_signals(event: TrajectoryEvent) -> dict:
    return {
        "steps": int(event.steps),
        "failures": int(event.failures),
        "tool_calls": int(event.tool_calls),
        "duration_s": float(event.duration_s),
        "retries": int(event.retries),
        "retry_like": int(event.retries) > 0,
        "terminal_state": event.terminal_state,
        "runner_provision_failed": False,
        "note": "dados de execucao/avaliacao; nao constituem evidencia de dominio",
    }