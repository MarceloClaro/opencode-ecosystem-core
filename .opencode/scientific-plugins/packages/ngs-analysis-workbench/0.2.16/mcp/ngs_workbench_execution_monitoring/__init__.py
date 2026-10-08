"""Shared adapters for engine-owned execution evidence."""

from .base import ExecutionObserver
from .models import ExecutionObservation
from .registry import DEFAULT_OBSERVER_REGISTRY, ObserverRegistry

__all__ = [
    "DEFAULT_OBSERVER_REGISTRY",
    "ExecutionObservation",
    "ExecutionObserver",
    "ObserverRegistry",
]
