"""Private SQLAlchemy mappings for the daemon-owned registry schema."""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class WorkspaceRow(Base):
    __tablename__ = "workspaces"
    __table_args__ = (
        CheckConstraint(
            "state IN ('available', 'missing', 'archived')",
            name="state",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    canonical_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False, default="available")
    created_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    last_seen_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)


class RunRow(Base):
    __tablename__ = "runs"
    __table_args__ = (
        UniqueConstraint("external_run_id"),
        UniqueConstraint("first_run_id", "attempt_number", name="uq_runs_recovery_attempt"),
        CheckConstraint(
            "status IN ('starting', 'running', 'cancel_requested', 'canceling', "
            "'completed', 'failed', 'canceled', 'orphaned')",
            name="status",
        ),
        CheckConstraint("revision >= 1", name="revision"),
        CheckConstraint("attempt_number >= 1", name="attempt_number"),
        CheckConstraint("json_valid(request_json)", name="request_json"),
        CheckConstraint("json_valid(command_json)", name="command_json"),
        Index("runs_recent_idx", "updated_at_ms", "id"),
        Index("runs_workspace_recent_idx", "workspace_id", "updated_at_ms", "id"),
        Index("runs_status_recent_idx", "status", "updated_at_ms", "id"),
        Index("runs_binding_pipeline_recent_idx", "binding", "pipeline", "updated_at_ms", "id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    external_run_id: Mapped[str] = mapped_column(String, nullable=False)
    first_run_id: Mapped[str] = mapped_column(String, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    binding: Mapped[str] = mapped_column(String, nullable=False)
    pipeline: Mapped[str] = mapped_column(String, nullable=False)
    workflow: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    plan_checksum: Mapped[str] = mapped_column(String, nullable=False)
    request_json: Mapped[str] = mapped_column(Text, nullable=False)
    command_json: Mapped[str] = mapped_column(Text, nullable=False)
    run_relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    approved_plan_relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    launch_log_relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    pid: Mapped[int | None] = mapped_column(Integer)
    started_at_ms: Mapped[int | None] = mapped_column(Integer)
    completed_at_ms: Mapped[int | None] = mapped_column(Integer)
    return_code: Mapped[int | None] = mapped_column(Integer)
    failure_summary: Mapped[str | None] = mapped_column(Text)
    cancel_requested_at_ms: Mapped[int | None] = mapped_column(Integer)
    created_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)


class RunEventRow(Base):
    __tablename__ = "run_events"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence"),
        CheckConstraint("sequence >= 1", name="sequence"),
        CheckConstraint("json_valid(details_json)", name="details_json"),
        Index("run_events_timeline_idx", "run_id", "sequence"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String)
    to_status: Mapped[str | None] = mapped_column(String)
    actor_type: Mapped[str] = mapped_column(String, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)


class WorkflowRow(Base):
    """One stable workflow catalog identity."""

    __tablename__ = "workflows"
    __table_args__ = (
        CheckConstraint("engine IN ('nextflow', 'snakemake')", name="engine"),
        CheckConstraint("json_valid(metadata_json)", name="metadata_json"),
        CheckConstraint("owner IN ('user', 'bundled')", name="owner"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    engine: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    owner: Mapped[str] = mapped_column(String, nullable=False, default="user")
    current_version_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workflow_versions.id",
            ondelete="RESTRICT",
            deferrable=True,
            initially="DEFERRED",
        ),
        nullable=False,
    )
    archived_at_ms: Mapped[int | None] = mapped_column(Integer)
    created_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)


class WorkflowVersionRow(Base):
    """One immutable implementation of a workflow catalog identity."""

    __tablename__ = "workflow_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_kind: Mapped[str] = mapped_column(String, nullable=False)
    local_root: Mapped[str | None] = mapped_column(Text)
    entrypoint: Mapped[str | None] = mapped_column(Text)
    source_sha256: Mapped[str | None] = mapped_column(String)
    remote_workflow: Mapped[str | None] = mapped_column(Text)
    revision: Mapped[str | None] = mapped_column(Text)
    execution_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)
