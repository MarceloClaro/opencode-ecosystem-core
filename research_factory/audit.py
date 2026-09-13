# -*- coding: utf-8 -*-
"""AuditLog — trilha de auditoria das etapas da fábrica de pesquisa.

Cada execução relevante de entrypoint registra uma entrada com estágio,
entrypoint, thread, timestamp UTC, hash SHA-256 do artefato e decisão.
A trilha é persistida em JSONL por thread; artefatos binários/texto são
guardados em subdiretório ``artifacts/`` com referência na entrada.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class AuditEntry:
    """Entrada individual da trilha de auditoria."""

    stage: str
    entrypoint: str
    thread_id: str
    artifact: Optional[bytes] = None
    decision: Optional[str] = None
    timestamp_utc: float = field(default_factory=time.time)
    artifact_ref: Optional[str] = None

    @property
    def hash_sha256(self) -> str:
        if self.artifact is not None:
            return _sha256_bytes(self.artifact)
        canonical = f"{self.stage}|{self.entrypoint}|{self.thread_id}".encode(
            "utf-8"
        )
        return _sha256_bytes(canonical)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "entrypoint": self.entrypoint,
            "thread_id": self.thread_id,
            "timestamp_utc": round(self.timestamp_utc, 3),
            "decision": self.decision,
            "artifact_ref": self.artifact_ref,
            "hash_sha256": self.hash_sha256,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        return cls(
            stage=data["stage"],
            entrypoint=data["entrypoint"],
            thread_id=data["thread_id"],
            artifact=None,
            decision=data.get("decision"),
            timestamp_utc=data.get("timestamp_utc", time.time()),
            artifact_ref=data.get("artifact_ref"),
        )


class AuditLog:
    """Registra e consulta entradas de auditoria por thread."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._art_root = self.root / "artifacts"
        self._art_root.mkdir(parents=True, exist_ok=True)

    def _path(self, thread_id: str) -> Path:
        return self.root / f"{thread_id}.jsonl"

    def record(self, stage: str, entrypoint: str, thread_id: str,
               artifact: Optional[bytes] = None,
               decision: Optional[str] = None) -> AuditEntry:
        artifact_ref = None
        if artifact is not None:
            artifact_ref = (
                f"{thread_id}-{uuid.uuid4().hex[:8]}-{stage}.bin"
            )
            (self._art_root / artifact_ref).write_bytes(artifact)
        entry = AuditEntry(
            stage=stage,
            entrypoint=entrypoint,
            thread_id=thread_id,
            artifact=artifact,
            decision=decision,
            artifact_ref=artifact_ref,
        )
        with self._path(thread_id).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        return entry

    def entries(self, thread_id: str) -> List[AuditEntry]:
        path = self._path(thread_id)
        if not path.exists():
            return []
        out: List[AuditEntry] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(AuditEntry.from_dict(json.loads(line)))
        return out

    def last_artifact(self, thread_id: str, stage: str) -> Optional[bytes]:
        """Recupera o artefato mais recente de um estágio (via ref em disco)."""
        for entry in reversed(self.entries(thread_id)):
            if entry.stage == stage and entry.artifact_ref:
                path = self._art_root / entry.artifact_ref
                if path.exists():
                    return path.read_bytes()
        return None

    def report(self, thread_id: str) -> Dict[str, Any]:
        entries = self.entries(thread_id)
        return {
            "thread_id": thread_id,
            "entry_count": len(entries),
            "entries": [e.to_dict() for e in entries],
        }