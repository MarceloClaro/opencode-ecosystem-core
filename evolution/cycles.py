# -*- coding: utf-8 -*-
"""
Evolution Cycles — Registro de Ciclos Evolutivos (R1..R46+)
===========================================================
Porta a disciplina de ciclos evolutivos documentados do OpenCode_Ecosystem
(evolution/evo-*.md, com scores por round) para um registro programático.

Cada ciclo (round) registra: objetivo, mudanças, score de qualidade (0-10),
lições aprendidas. O registro persiste em evolution/cycles.json e alimenta a
memória metacognitiva do ecossistema (lições viram reflexões no MetaBus).
"""

from __future__ import annotations

import glob
import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EVOLUTION_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(EVOLUTION_DIR, "cycles.json")


@dataclass
class EvolutionCycle:
    round_id: str                 # ex.: "R47"
    objective: str
    changes: List[str] = field(default_factory=list)
    score: Optional[float] = None  # 0-10
    lessons: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class EvolutionRegistry:
    """Registro persistente de ciclos evolutivos do ecossistema."""

    def __init__(self, state_path: str = STATE_PATH):
        self.state_path = state_path
        self.cycles: List[EvolutionCycle] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                allowed = {"round_id", "objective", "changes", "score", "lessons", "timestamp"}
                self.cycles = [
                    EvolutionCycle(**{key: value for key, value in cycle.items() if key in allowed})
                    for cycle in data.get("cycles", [])
                    if isinstance(cycle, dict)
                ]
            except (json.JSONDecodeError, TypeError, ValueError):
                self.cycles = []

    def save(self) -> None:
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump({"cycles": [asdict(c) for c in self.cycles]},
                      f, ensure_ascii=False, indent=2)

    def next_round_id(self) -> str:
        max_n = 46  # R1..R46 documentados no ecossistema original
        for c in self.cycles:
            m = re.match(r"R(\d+)", c.round_id)
            if m:
                max_n = max(max_n, int(m.group(1)))
        return f"R{max_n + 1}"

    def record(self, objective: str, changes: List[str],
               score: Optional[float] = None,
               lessons: Optional[List[str]] = None,
               round_id: Optional[str] = None) -> EvolutionCycle:
        cycle = EvolutionCycle(
            round_id=round_id or self.next_round_id(),
            objective=objective, changes=changes,
            score=score, lessons=lessons or [],
        )
        self.cycles.append(cycle)
        self.save()
        return cycle

    def history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [asdict(c) for c in self.cycles[-limit:]]

    def average_score(self) -> Optional[float]:
        scored = [c.score for c in self.cycles if c.score is not None]
        return round(sum(scored) / len(scored), 2) if scored else None

    def load_documented_cycles(self) -> List[Dict[str, str]]:
        """Indexa os ciclos documentados em evolution/evo-*.md (portados do original)."""
        docs = []
        for path in sorted(glob.glob(os.path.join(EVOLUTION_DIR, "evo-*.md"))):
            name = os.path.basename(path)
            title = ""
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("#"):
                            title = line.lstrip("# ").strip()
                            break
            except OSError:
                pass
            docs.append({"file": name, "title": title})
        return docs


# Singleton
evolution_registry = EvolutionRegistry()
