# -*- coding: utf-8 -*-
"""
ReasoningVisualizer — Visualização Mermaid de cadeias de raciocínio
===================================================================
SPEC-917: transforma resultados e passos de raciocínio em diagramas
auditáveis (Mermaid flowchart).
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

from reasoning.engines import ReasoningResult


class ReasoningVisualizer:
    """Gera diagramas Mermaid para cadeias de raciocínio."""

    def chain_to_mermaid(self, query: str, steps: Iterable[str],
                         engine: str = "unknown",
                         conclusion: Optional[str] = None) -> str:
        """Converte uma cadeia de passos em `flowchart TD` Mermaid."""
        step_list = list(steps)
        lines: List[str] = ["flowchart TD"]
        lines.append(f"  Q[\"Consulta: {self._esc(query)}\"]")
        lines.append(f"  E[\"Motor: {self._esc(engine)}\"]")
        lines.append("  Q --> E")

        previous = "E"
        for idx, step in enumerate(step_list, start=1):
            node = f"S{idx}"
            lines.append(f"  {node}[\"{idx}. {self._esc(step)}\"]")
            lines.append(f"  {previous} --> {node}")
            previous = node

        if conclusion:
            lines.append(f"  C[\"Conclusão: {self._esc(conclusion)}\"]")
            lines.append(f"  {previous} --> C")

        return "\n".join(lines)

    def result_to_mermaid(self, result: ReasoningResult) -> str:
        """Converte `ReasoningResult` completo em diagrama Mermaid."""
        return self.chain_to_mermaid(
            query=result.query,
            steps=result.steps,
            engine=result.engine,
            conclusion=result.conclusion,
        )

    @staticmethod
    def _esc(text: str) -> str:
        """Escapa caracteres problemáticos para labels Mermaid."""
        text = str(text).replace("\n", " ").replace('"', "'")
        text = re.sub(r"\s+", " ", text).strip()
        return text[:180]


reasoning_visualizer = ReasoningVisualizer()
