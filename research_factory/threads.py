# -*- coding: utf-8 -*-
"""Threads — estado durável de trabalho de pesquisa (SPEC-935-R471, M1).

Inspirado no modelo de threads do open-swe (langchain-ai/open-swe):
uma thread é um contexto de trabalho durável que pode conter múltiplas
invocações (execuções de entrypoints) e artefatos associados. A thread
persiste em JSON sob um diretório raiz, permitindo retomada entre
invocações — inclusive por diferentes etapas do ciclo de pesquisa.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now() -> float:
    return time.time()


@dataclass
class ResearchThread:
    """Contexto durável de um trabalho de pesquisa."""

    id: str
    topic: str
    created_at: float = field(default_factory=_utc_now)
    workspace: Optional[str] = None
    invocations: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)

    def add_invocation(self, entrypoint: str, status: str,
                       detail: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma execução de entrypoint nesta thread."""
        self.invocations.append({
            "entrypoint": entrypoint,
            "status": status,
            "timestamp_utc": _utc_now(),
            "detail": detail or {},
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "created_at": self.created_at,
            "workspace": self.workspace,
            "invocations": self.invocations,
            "artifacts": self.artifacts,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchThread":
        thread = cls(
            id=data["id"],
            topic=data["topic"],
            created_at=data.get("created_at", _utc_now()),
            workspace=data.get("workspace"),
            invocations=list(data.get("invocations", [])),
        )
        thread.artifacts = dict(data.get("artifacts", {}))
        return thread


class ThreadStore:
    """Persistência JSON de threads sob um diretório raiz."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, thread_id: str) -> Path:
        return self.root / f"{thread_id}.json"

    def create(self, topic: str, workspace: Optional[str] = None) -> ResearchThread:
        thread = ResearchThread(
            id=f"t-{uuid.uuid4().hex[:12]}",
            topic=topic,
            workspace=workspace,
        )
        self.save(thread)
        return thread

    def save(self, thread: ResearchThread) -> Dict[str, Any]:
        payload = json.dumps(thread.to_dict(), ensure_ascii=False, indent=2)
        self._path(thread.id).write_text(payload, encoding="utf-8")
        return thread.to_dict()

    def load(self, thread_id: str) -> ResearchThread:
        path = self._path(thread_id)
        if not path.exists():
            raise KeyError(thread_id)
        return ResearchThread.from_dict(
            json.loads(path.read_text(encoding="utf-8"))
        )

    def list_all(self) -> List[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))