"""Select a replaceable execution evidence adapter by execution binding."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Protocol, runtime_checkable

from .base import ExecutionObserver
from .models import ExecutionObservation, empty_observation
from .nextflow_trace import NextflowTraceObserver
from .snakemake_log import SnakemakeLogObserver


@runtime_checkable
class FileExecutionObserver(Protocol):
    """The file-input capability; other adapters may still implement only observe()."""

    evidence_kind: str
    file_patterns: tuple[str, ...]

    def observe_lines(
        self, lines: Iterable[str], *, evidence_path: str, workflow_status: str
    ) -> ExecutionObservation: ...


@dataclass(frozen=True)
class ObserverRegistry:
    """Immutable binding-to-adapter registry suitable for dependency injection."""

    observers: Mapping[str, ExecutionObserver]

    def file_observer(self, binding: str) -> FileExecutionObserver:
        observer = self.observers.get(binding)
        if not isinstance(observer, FileExecutionObserver):
            raise ValueError(f"no file execution evidence adapter for binding: {binding}")
        return observer

    def observe(
        self,
        run_dir: Path,
        binding: str,
        workflow_status: str,
    ) -> ExecutionObservation:
        observer = self.observers.get(binding)
        if observer is None:
            return empty_observation(
                engine=binding,
                evidence_kind="unsupported",
                evidence_path=None,
                reason=f"no execution evidence adapter for binding: {binding}",
            )
        return observer.observe(run_dir, workflow_status)


DEFAULT_OBSERVER_REGISTRY = ObserverRegistry(
    MappingProxyType(
        {
            NextflowTraceObserver.binding: NextflowTraceObserver(),
            SnakemakeLogObserver.binding: SnakemakeLogObserver(),
        }
    )
)
