"""Fixtures compartilhadas para os 24 CTs do Round 17."""
import pytest
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


# ============================================================
# Data classes compartilhadas
# ============================================================

@dataclass
class APIService:
    name: str
    version: str
    endpoints: list[str] = field(default_factory=list)
    health: bool = True


@dataclass
class AuditEntry:
    agent_id: str
    service: str
    action: str
    params: dict
    result: str
    timestamp: str
    hash: str = ""


@dataclass
class StreamMessage:
    topic: str
    key: str
    value: dict
    offset: int = 0
    timestamp: str = ""


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"
