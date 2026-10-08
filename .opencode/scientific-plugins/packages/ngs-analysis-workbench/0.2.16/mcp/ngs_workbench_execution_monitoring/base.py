"""Protocol implemented by replaceable execution evidence adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import ExecutionObservation


class ExecutionObserver(Protocol):
    """Read engine evidence without mutating the run or its registry record."""

    binding: str

    def observe(self, run_dir: Path, workflow_status: str) -> ExecutionObservation:
        """Return one engine-neutral snapshot for a run directory."""
