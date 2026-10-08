"""Split stable workflow identities from immutable implementations.

Revision ID: 0004_workflow_versions
Revises: 0003_run_recovery_lineage
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_workflow_versions"
down_revision = "0003_run_recovery_lineage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_versions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("workflow_id", sa.String(), nullable=False),
        sa.Column("source_kind", sa.String(), nullable=False),
        sa.Column("local_root", sa.Text(), nullable=True),
        sa.Column("entrypoint", sa.Text(), nullable=True),
        sa.Column("source_sha256", sa.String(), nullable=True),
        sa.Column("remote_workflow", sa.Text(), nullable=True),
        sa.Column("revision", sa.Text(), nullable=True),
        sa.Column("execution_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at_ms", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_versions_workflow_id", "workflow_versions", ["workflow_id"])
    with op.batch_alter_table("workflows") as batch:
        batch.add_column(sa.Column("owner", sa.String(), nullable=True))
        batch.add_column(sa.Column("current_version_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("archived_at_ms", sa.Integer(), nullable=True))
    # The pre-version catalog only contained the retired ZIP save format.
    op.execute("DELETE FROM workflows")
    with op.batch_alter_table("workflows") as batch:
        batch.alter_column("owner", existing_type=sa.String(), nullable=False)
        batch.alter_column("current_version_id", existing_type=sa.String(), nullable=False)
        batch.create_check_constraint("ck_workflows_owner", "owner IN ('user', 'bundled')")
        batch.create_foreign_key(
            "fk_workflows_current_version_id_workflow_versions",
            "workflow_versions",
            ["current_version_id"],
            ["id"],
            ondelete="RESTRICT",
            deferrable=True,
            initially="DEFERRED",
        )
        batch.drop_column("entrypoint")
        batch.drop_column("archive_sha256")
        batch.drop_column("source_run_id")


def downgrade() -> None:
    with op.batch_alter_table("workflows") as batch:
        batch.drop_constraint(
            "fk_workflows_current_version_id_workflow_versions", type_="foreignkey"
        )
        batch.add_column(sa.Column("entrypoint", sa.Text(), nullable=True))
        batch.add_column(sa.Column("archive_sha256", sa.String(), nullable=True))
        batch.add_column(sa.Column("source_run_id", sa.String(), nullable=True))
    op.execute("DELETE FROM workflows")
    with op.batch_alter_table("workflows") as batch:
        batch.alter_column("entrypoint", existing_type=sa.Text(), nullable=False)
        batch.alter_column("archive_sha256", existing_type=sa.String(), nullable=False)
        batch.create_foreign_key(
            "fk_workflows_source_run_id_runs",
            "runs",
            ["source_run_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.drop_constraint("ck_workflows_owner", type_="check")
        batch.drop_column("archived_at_ms")
        batch.drop_column("current_version_id")
        batch.drop_column("owner")
    op.drop_index("ix_workflow_versions_workflow_id", table_name="workflow_versions")
    op.drop_table("workflow_versions")
