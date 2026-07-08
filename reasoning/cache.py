# -*- coding: utf-8 -*-
"""
ReasoningCache — Cache LRU para resultados de raciocínio
=========================================================
SPEC-917: Reduz latência em consultas repetidas.

Estratégia:
- Cache LRU (Least Recently Used) com limite configurável
- TTL (Time To Live) por motor
- Hit ratio tracking para avaliação de eficácia
- Thread-safe via threading.Lock
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass
class CacheEntry:
    """Entrada individual do cache."""
    key: str
    result: Dict[str, Any]
    engine: str
    timestamp: float
    ttl: float
    size_bytes: int = 0

    @property
    def expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl


class ReasoningCache:
    """Cache LRU com TTL para resultados de raciocínio.

    Args:
        max_size: número máximo de entradas no cache
        default_ttl: TTL padrão em segundos (padrão: 300s = 5min)
    """

    def __init__(self, max_size: int = 256, default_ttl: float = 300.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    # ── API principal ─────────────────────────────────────────────────────

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera entrada do cache. Retorna None se não encontrado ou expirado."""
        with self._lock:
            self._evict_expired()
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            if entry.expired:
                del self._cache[key]
                self._misses += 1
                return None
            # Move ao final (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return dict(entry.result)  # cópia defensiva

    def set(self, key: str, result: Dict[str, Any],
            engine: str = "unknown", ttl: Optional[float] = None) -> None:
        """Armazena resultado no cache."""
        with self._lock:
            self._evict_expired()
            # Se já existe, atualiza
            if key in self._cache:
                self._cache.move_to_end(key)
            # Evicção LRU se necessário
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
                self._evictions += 1
            self._cache[key] = CacheEntry(
                key=key,
                result=result,
                engine=engine,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl,
                size_bytes=len(json.dumps(result, default=str)),
            )

    def make_key(self, query: str, engine: str, **kwargs) -> str:
        """Gera chave única para consulta + parâmetros."""
        canonical = f"{engine}::{query.strip().lower()}::"
        if kwargs:
            canonical += json.dumps(kwargs, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def invalidate(self, engine: Optional[str] = None) -> int:
        """Invalida entradas de um motor específico (ou todas se None).
        Retorna número de entradas removidas."""
        with self._lock:
            if engine is None:
                count = len(self._cache)
                self._cache.clear()
                return count
            to_remove = [k for k, v in self._cache.items() if v.engine == engine]
            for k in to_remove:
                del self._cache[k]
            return len(to_remove)

    # ── Métricas ──────────────────────────────────────────────────────────

    @property
    def hit_ratio(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_ratio": round(self.hit_ratio, 4),
                "default_ttl": self.default_ttl,
                "entries_by_engine": self._entries_by_engine(),
            }

    def _entries_by_engine(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for entry in self._cache.values():
            counts[entry.engine] = counts.get(entry.engine, 0) + 1
        return counts

    # ── Internos ──────────────────────────────────────────────────────────

    def _evict_expired(self) -> int:
        """Remove entradas expiradas. Retorna quantidade removida."""
        now = time.time()
        expired = [k for k, v in self._cache.items()
                   if (now - v.timestamp) > v.ttl]
        for k in expired:
            del self._cache[k]
        return len(expired)

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return key in self._cache


# Singleton global
reasoning_cache = ReasoningCache()
