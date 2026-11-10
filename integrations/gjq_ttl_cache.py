"""Cache TTL local, thread-safe e sem dependências externas (R1106).

Guarda apenas respostas de configuração/calibração/lista de backends. Nunca
guarda API key, QASM, counts ou resultado de job.
"""
from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class _Item:
    value: Any
    created_at: float
    expires_at: float
    ttl: float


class TTLCache:
    def __init__(self, maxsize: int = 64, ttl: float = 300.0,
                 clock: Callable[[], float] | None = None):
        if maxsize < 1:
            raise ValueError("maxsize deve ser >= 1")
        if ttl <= 0:
            raise ValueError("ttl deve ser > 0")
        self.maxsize = int(maxsize)
        self.default_ttl = float(ttl)
        self._clock = clock or time.monotonic
        self._data: OrderedDict[Any, _Item] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def _now(self) -> float:
        return float(self._clock())

    def _purge(self, now: float) -> None:
        expirados = [key for key, item in self._data.items() if item.expires_at <= now]
        for key in expirados:
            self._data.pop(key, None)

    def get(self, key: Any) -> tuple[Any, dict[str, Any]]:
        with self._lock:
            now = self._now()
            self._purge(now)
            item = self._data.get(key)
            if item is None:
                self._misses += 1
                raise KeyError(key)
            self._data.move_to_end(key)
            self._hits += 1
            return item.value, self._meta(item, now, hit=True)

    def set(self, key: Any, value: Any, ttl: float | None = None) -> dict[str, Any]:
        ttl_value = float(ttl if ttl is not None else self.default_ttl)
        if ttl_value <= 0:
            raise ValueError("ttl deve ser > 0")
        with self._lock:
            now = self._now()
            self._purge(now)
            self._data[key] = _Item(value=value, created_at=now,
                                    expires_at=now + ttl_value, ttl=ttl_value)
            self._data.move_to_end(key)
            while len(self._data) > self.maxsize:
                self._data.popitem(last=False)
                self._evictions += 1
            return self._meta(self._data[key], now, hit=False)

    def get_or_set(self, key: Any, factory: Callable[[], Any],
                   ttl: float | None = None, force: bool = False) -> tuple[Any, dict[str, Any]]:
        if not force:
            try:
                return self.get(key)
            except KeyError:
                pass
        value = factory()
        meta = self.set(key, value, ttl=ttl)
        return value, meta

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "size": len(self._data),
                "maxsize": self.maxsize,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "ttl_default": self.default_ttl,
            }

    def _meta(self, item: _Item, now: float, hit: bool) -> dict[str, Any]:
        return {
            "hit": hit,
            "age_seconds": round(max(now - item.created_at, 0.0), 3),
            "ttl_seconds": item.ttl,
            "expires_in": round(max(item.expires_at - now, 0.0), 3),
        }
