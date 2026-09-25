# -*- coding: utf-8 -*-
"""AuditLedger — hash-chain SHA-256 (SPEC-935-R504).

- dedupe por event_id;
- payload canonicalizado (json.dumps sort_keys);
- hash encadeado: H(sequence + previous_hash + payload_hash);
- verificação integral (detecta adulteração);
- snapshot somente leitura;
- export JSONL.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional


def _canon(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)


class AuditLedger:
    def __init__(self, genesis: str = "genesis"):
        self._genesis = genesis
        self._entries: List[Dict[str, Any]] = []
        self._by_event_id: Dict[str, int] = {}

    def append(self, event_type: str, payload: Dict[str, Any],
               event_id: Optional[str] = None) -> Dict[str, Any]:
        if event_id is not None and event_id in self._by_event_id:
            return self._entries[self._by_event_id[event_id]]  # dedupe
        seq = len(self._entries)
        previous_hash = self._entries[-1]["hash"] if self._entries else self._genesis
        payload_hash = hashlib.sha256(_canon(payload).encode()).hexdigest()
        entry = {
            "seq": seq,
            "event_id": event_id or f"{event_type}-{seq}-{int(time.time() * 1000)}",
            "type": event_type,
            "timestamp": time.time(),
            "payload": dict(payload),
            "payload_hash": payload_hash,
            "previous_hash": previous_hash,
            "hash": hashlib.sha256(
                f"{seq}|{previous_hash}|{payload_hash}".encode()
            ).hexdigest(),
        }
        self._entries.append(dict(entry))
        self._by_event_id[entry["event_id"]] = seq
        return entry

    def verify(self) -> bool:
        prev = self._genesis
        for entry in self._entries:
            if entry["previous_hash"] != prev:
                return False
            payload_hash = hashlib.sha256(_canon(entry["payload"]).encode()).hexdigest()
            if entry["payload_hash"] != payload_hash:
                return False
            expected = hashlib.sha256(
                f"{entry['seq']}|{entry['previous_hash']}|{entry['payload_hash']}".encode()
            ).hexdigest()
            if entry["hash"] != expected:
                return False
            prev = entry["hash"]
        return True

    def dedupe_count(self, event_type: str, payload: Dict[str, Any]) -> int:
        c = _canon(payload)
        return sum(
            1 for e in self._entries
            if e["type"] == event_type and _canon(e["payload"]) == c
        )

    def snapshot(self) -> List[Dict[str, Any]]:
        """Snapshot somente leitura (deep copy)."""
        return json.loads(json.dumps(self._entries))

    def export_jsonl(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for e in self._entries:
                f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")

    def __len__(self) -> int:
        return len(self._entries)