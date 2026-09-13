# -*- coding: utf-8 -*-
"""Autonomia da fábrica de pesquisa (SPEC-935-R476, extensão do M1/R471).

Ciclo de auto-supervisão (Reflexion) e despacho trust-aware:
- `self_supervise`: após uma execução, consulta lições do MetaBus (memória
  metacognitiva injetável), deriva plano de próximas ações e pontua o quão
  acionável é a reflexão.
- `rank_agents`: ordena candidatos por trust score (Trust Engine); agentes
  sem score usam `default_trust`. Com `prefer_trust=False`, preserva a
  ordem de entrada (ordem neutra).

Anti-overclaim: o relatório nunca declara mérito qualitativo de topo; apenas
estrutura de reflexão, contagem de lições e plano acionável.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class SelfSupervisionReport:
    """Estrutura de reflexão pós-execução (Reflexion, R476)."""

    round_id: str
    timestamp_utc: str
    executed_actions: List[str]
    lessons_found: int
    next_action_plan: List[str]
    actionable: float
    orchestrator: str = "marceloclaro"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutonomyCore:
    """Núcleo de auto-supervisão e despacho trust-aware da fábrica."""

    def __init__(
        self,
        memory: Optional[object] = None,
        trust_scores: Optional[Dict[str, float]] = None,
        default_trust: float = 0.5,
        round_tag: str = "R476",
    ) -> None:
        # memory: objeto opcional com search_memory(topic=None, limit=None)
        self.memory = memory
        self.trust_scores = dict(trust_scores or {})
        self.default_trust = default_trust
        self.round_tag = round_tag
        self._counter = 0

    def self_supervise(
        self,
        executed_actions: Iterable[str],
        topic: Optional[str] = None,
    ) -> SelfSupervisionReport:
        """Registra reflexão pós-execução: lições encontradas -> plano de ação.

        Acionabilidade (0..1):
        - sem lições => 0.0 (nada acionável derivado);
        - com lições => 0.4 base + 0.3 se gerou plano + 0.3 se houve execução.
        """
        actions = list(executed_actions)
        lessons: List[Dict[str, str]] = []
        if self.memory is not None:
            try:
                lessons = list(
                    self.memory.search_memory(topic=topic or "lessons", limit=5)
                )
            except Exception:
                lessons = []

        plan = [
            f"aplicar: {lesson.get('content', str(lesson))}"
            for lesson in lessons[:3]
        ]
        if not lessons:
            actionable = 0.0
        else:
            actionable = min(
                1.0,
                0.4 + (0.3 if plan else 0.0) + (0.3 if actions else 0.0),
            )

        self._counter += 1
        return SelfSupervisionReport(
            round_id=f"{self.round_tag}.{self._counter}",
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            executed_actions=actions,
            lessons_found=len(lessons),
            next_action_plan=plan,
            actionable=round(actionable, 2),
        )

    def rank_agents(
        self,
        candidates: Iterable[str],
        prefer_trust: bool = True,
    ) -> List[str]:
        """Ordena candidatos por trust desc (padrão) ou preserva a ordem."""
        members = list(candidates)
        if not prefer_trust:
            return members
        return sorted(
            members,
            key=lambda agent: -self.trust_scores.get(agent, self.default_trust),
        )