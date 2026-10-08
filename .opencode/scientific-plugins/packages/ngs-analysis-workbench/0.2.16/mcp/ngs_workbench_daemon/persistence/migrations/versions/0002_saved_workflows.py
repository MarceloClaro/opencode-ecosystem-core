"""Index reusable workflow archives in the existing global registry.

Revision ID: 0002_saved_workflows
Revises: 0001_initial_registry
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_saved_workflows"
down_revision = "0001_initial_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflows",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("engine", sa.String(), nullable=False),
        sa.Column("entrypoint", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("archive_sha256", sa.String(), nullable=False),
        sa.Column("source_run_id", sa.String(), nullable=True),
        sa.Column("created_at_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("engine IN ('nextflow', 'snakemake')", name="ck_workflows_engine"),
        sa.CheckConstraint("json_valid(metadata_json)", name="ck_workflows_metadata_json"),
        sa.ForeignKeyConstraint(
            ["source_run_id"],
            ["runs.id"],
            name="fk_workflows_source_run_id_runs",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflows"),
    )


def downgrade() -> None:
    op.drop_table("workflows")
