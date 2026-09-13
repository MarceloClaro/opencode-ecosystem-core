# -*- coding: utf-8 -*-
"""ResearchScheduler — execução recorrente de tarefas de pesquisa.

Inspirado no entrypoint Scheduler do open-swe (langchain-ai/open-swe):
tarefas recorrentes (ex.: revisão semanal de literatura) são agendadas com
intervalo e executadas quando vencidas. Metadados persistem em JSON;
funções permanecem em memória (não serializáveis) e devem ser reinseridas
após reload quando houver execução.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class ResearchScheduler:
    """Agendador persistente de tarefas recorrentes."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._fns: Dict[str, Callable[[], Any]] = {}
        self._jobs = self._load()

    # ---- persistência ----

    def _path(self) -> Path:
        return self.root / "jobs.json"

    def _load(self) -> List[Dict[str, Any]]:
        path = self._path()
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []

    def _save(self) -> None:
        self._path().write_text(
            json.dumps(self._jobs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ---- operação ----

    def add(self, name: str, fn: Callable[[], Any],
            interval_seconds: float,
            extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        job = {
            "id": f"j-{uuid.uuid4().hex[:8]}",
            "name": name,
            "interval_seconds": float(interval_seconds),
            "next_run": 0.0,
            "created_at": time.time(),
            "extra": extra or {},
        }
        self._jobs.append(job)
        self._fns[job["id"]] = fn
        self._save()
        return job

    def jobs(self) -> List[Dict[str, Any]]:
        return list(self._jobs)

    def run_due(self, now: float) -> int:
        ran = 0
        for job in self._jobs:
            if job["next_run"] <= now and job["id"] in self._fns:
                self._fns[job["id"]]()
                job["next_run"] = now + job["interval_seconds"]
                ran += 1
        if ran:
            self._save()
        return ran