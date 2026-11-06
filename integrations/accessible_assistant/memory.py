"""R1063 — memória de atividade local, criptografada e com TTL de 24 h."""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from integrations.desktop_operator import runtime

DEFAULT_STATE = Path("~/.local/state/opencode-accessible-assistant").expanduser()


class MemoryError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ActivityMemory:
    def __init__(self, state_dir: str | Path | None = None, ttl_hours: int = 24,
                 now: float | None = None):
        self.state_dir = Path(state_dir or DEFAULT_STATE).expanduser()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.state_dir.chmod(0o700)
        except OSError:
            pass
        self.ttl_seconds = max(1, min(int(ttl_hours), 24 * 7)) * 3600
        self.now = now
        self.log = self.state_dir / "activity.jsonl"
        self.key = self.state_dir / "key"
        self._fernet = Fernet(self._load_key())

    def _load_key(self) -> bytes:
        if self.key.is_file():
            return self.key.read_bytes().strip()
        key = Fernet.generate_key()
        descriptor = os.open(self.key, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(key)
        return key

    def _timestamp(self) -> float:
        return float(self.now if self.now is not None else time.time())

    def append(self, kind: str, text: str = "", **meta) -> dict:
        safe_text = runtime.redact_payload(str(text or ""))[:4000]
        entry = {"ts": self._timestamp(), "kind": str(kind)[:80],
                 "text": safe_text, "meta": runtime.redact_payload(meta)}
        payload = json.dumps(entry, ensure_ascii=False).encode("utf-8")
        token = self._fernet.encrypt(payload)
        with self.log.open("ab") as stream:
            stream.write(base64.urlsafe_b64encode(token) + b"\n")
        return entry

    def entries(self) -> list[dict]:
        if not self.log.is_file():
            return []
        result = []
        for line in self.log.read_bytes().splitlines():
            try:
                token = base64.urlsafe_b64decode(line)
                result.append(json.loads(self._fernet.decrypt(token)))
            except (InvalidToken, ValueError, json.JSONDecodeError):
                continue
        return result

    def prune(self) -> int:
        cutoff = self._timestamp() - self.ttl_seconds
        kept = [entry for entry in self.entries() if entry.get("ts", 0) >= cutoff]
        with self.log.open("wb") as stream:
            for entry in kept:
                token = self._fernet.encrypt(json.dumps(entry, ensure_ascii=False).encode("utf-8"))
                stream.write(base64.urlsafe_b64encode(token) + b"\n")
        return len(kept)

    def summary(self, limit: int = 20) -> dict:
        entries = [e for e in self.entries() if e.get("ts", 0) >= self._timestamp() - self.ttl_seconds]
        counts: dict[str, int] = {}
        for entry in entries:
            counts[entry.get("kind", "?")] = counts.get(entry.get("kind", "?"), 0) + 1
        return {"ok": True, "ttl_hours": self.ttl_seconds // 3600,
                "entries": len(entries), "counts": counts,
                "recent": entries[-max(1, min(limit, 100)):],
                "encrypted": True, "external_validation": False}

    def forget(self) -> dict:
        if self.log.is_file():
            self.log.unlink()
        return {"ok": True, "forgotten": True}
