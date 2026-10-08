"""Checkpoints locais atômicos e exclusão de execução entre processos."""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import tempfile
import time


class WorkflowBusyError(ValueError):
    """Outra execução já possui este workflow."""


class WorkflowStore:
    ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")

    def __init__(self, root=None):
        self.root = Path(root) if root is not None else Path(__file__).resolve().parents[1] / ".mci_state" / "workflows"

    @classmethod
    def validate_id(cls, workflow_id):
        if not isinstance(workflow_id, str) or not cls.ID_PATTERN.fullmatch(workflow_id):
            raise ValueError("Identificador inválido: use até 64 letras, números, hífen ou sublinhado.")
        return workflow_id

    def _path(self, workflow_id, suffix=".json"):
        self.validate_id(workflow_id)
        path = self.root / (workflow_id + suffix)
        if path.is_symlink():
            raise ValueError("Checkpoint inválido: links simbólicos não são permitidos.")
        return path

    def _prepare(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def create(self, workflow_id, definition):
        now = time.time()
        record = {"schema_version": 1, "workflow_id": workflow_id, "definition": definition,
                  "status": "queued", "steps": 0, "created_at": now, "updated_at": now}
        self.create_record(workflow_id, record)
        return record

    def create_record(self, workflow_id, record):
        """Publica o checkpoint inicial completo; leitores nunca veem JSON parcial."""
        self._publish(workflow_id, record, exclusive=True)

    def load(self, workflow_id):
        path = self._path(workflow_id)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise ValueError(f"Checkpoint inválido para {workflow_id}.") from exc
        if not isinstance(record, dict) or record.get("workflow_id") != workflow_id:
            raise ValueError(f"Checkpoint inválido para {workflow_id}: identidade divergente.")
        return record

    def save(self, workflow_id, record):
        self._publish(workflow_id, record, exclusive=False)

    def _publish(self, workflow_id, record, *, exclusive):
        path = self._path(workflow_id)
        if not isinstance(record, dict) or record.get("workflow_id") != workflow_id:
            raise ValueError("O registro deve preservar o identificador do workflow.")
        data = json.dumps(record, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self._prepare()
        fd, temporary = tempfile.mkstemp(prefix=workflow_id + "-", suffix=".tmp", dir=self.root)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if exclusive:
                # Hardlink publica de uma vez e recusa sobrescrever outro criador.
                os.link(temporary, path)
            else:
                os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)

    @contextmanager
    def claim(self, workflow_id, timeout=None):
        """Aquisição imediata; timeout mantido por compatibilidade, sem fila oculta."""
        path = self._path(workflow_id, ".lock")
        self._prepare()
        fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        handle = os.fdopen(fd, "r+b")
        acquired = False
        try:
            try:
                if os.name == "nt":
                    import msvcrt
                    if path.stat().st_size == 0:
                        handle.write(b"0")
                        handle.flush()
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except OSError as exc:
                raise WorkflowBusyError(f"Workflow {workflow_id} já está em execução.") from exc
            yield
        finally:
            if acquired:
                if os.name == "nt":
                    import msvcrt
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()
