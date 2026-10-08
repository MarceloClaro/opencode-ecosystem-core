"""Create the daemon-owned workspace, run, and event registry.

Revision ID: 0001_initial_registry
Revises:
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_registry"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("canonical_path", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("created_at_ms", sa.Integer(), nullable=False),
        sa.Column("last_seen_at_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "state IN ('available', 'missing', 'archived')",
            name="ck_workspaces_state",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workspaces"),
        sa.UniqueConstraint("canonical_path", name="uq_workspaces_canonical_path"),
    )
    op.create_table(
        "runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("workspace_id", sa.String(), nullable=False),
        sa.Column("external_run_id", sa.String(), nullable=False),
        sa.Column("binding", sa.String(), nullable=False),
        sa.Column("pipeline", sa.String(), nullable=False),
        sa.Column("workflow", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("plan_checksum", sa.String(), nullable=False),
        sa.Column("request_json", sa.Text(), nullable=False),
        sa.Column("command_json", sa.Text(), nullable=False),
        sa.Column("run_relative_path", sa.Text(), nullable=False),
        sa.Column("approved_plan_relative_path", sa.Text(), nullable=False),
        sa.Column("launch_log_relative_path", sa.Text(), nullable=False),
        sa.Column("pid", sa.Integer(), nullable=True),
        sa.Column("started_at_ms", sa.Integer(), nullable=True),
        sa.Column("completed_at_ms", sa.Integer(), nullable=True),
        sa.Column("return_code", sa.Integer(), nullable=True),
        sa.Column("failure_summary", sa.Text(), nullable=True),
        sa.Column("cancel_requested_at_ms", sa.Integer(), nullable=True),
        sa.Column("created_at_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("json_valid(command_json)", name="ck_runs_command_json"),
        sa.CheckConstraint("json_valid(request_json)", name="ck_runs_request_json"),
        sa.CheckConstraint("revision >= 1", name="ck_runs_revision"),
        sa.CheckConstraint(
            "status IN ('starting', 'running', 'cancel_requested', 'canceling', "
            "'completed', 'failed', 'canceled', 'orphaned')",
            name="ck_runs_status",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_runs_workspace_id_workspaces",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_runs"),
        sa.UniqueConstraint(
            "workspace_id",
            "binding",
            "external_run_id",
            name="uq_runs_workspace_id",
        ),
    )
    op.create_index("runs_recent_idx", "runs", ["updated_at_ms", "id"])
    op.create_index(
        "runs_workspace_recent_idx",
        "runs",
        ["workspace_id", "updated_at_ms", "id"],
    )
    op.create_index(
        "runs_status_recent_idx",
        "runs",
        ["status", "updated_at_ms", "id"],
    )
    op.create_index(
        "runs_binding_pipeline_recent_idx",
        "runs",
        ["binding", "pipeline", "updated_at_ms", "id"],
    )
    op.create_table(
        "run_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("from_status", sa.String(), nullable=True),
        sa.Column("to_status", sa.String(), nullable=True),
        sa.Column("actor_type", sa.String(), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=False),
        sa.Column("created_at_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("json_valid(details_json)", name="ck_run_events_details_json"),
        sa.CheckConstraint("sequence >= 1", name="ck_run_events_sequence"),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["runs.id"],
            name="fk_run_events_run_id_runs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_run_events"),
        sa.UniqueConstraint("run_id", "sequence", name="uq_run_events_run_id"),
    )
    op.create_index(
        "run_events_timeline_idx",
        "run_events",
        ["run_id", "sequence"],
    )
