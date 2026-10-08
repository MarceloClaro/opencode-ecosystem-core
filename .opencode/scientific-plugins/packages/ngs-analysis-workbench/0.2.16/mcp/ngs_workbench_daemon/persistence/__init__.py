"""Daemon-owned durable host-local run registry."""

from .database import RegistryDatabase, default_database
from .paths import (
    ensure_workspace_identity,
    read_workspace_identity,
    registry_path,
    workspace_identity_path,
)
from .repository import (
    InvalidRunTransition,
    NewRun,
    RegistryRepository,
    RunConflict,
    RunFilters,
    RunRecord,
    StaleRunRevision,
)
from .unit_of_work import SqlAlchemyUnitOfWork

__all__ = [
    "InvalidRunTransition",
    "NewRun",
    "RegistryDatabase",
    "RegistryRepository",
    "RunConflict",
    "RunFilters",
    "RunRecord",
    "SqlAlchemyUnitOfWork",
    "StaleRunRevision",
    "default_database",
    "ensure_workspace_identity",
    "read_workspace_identity",
    "registry_path",
    "workspace_identity_path",
]
