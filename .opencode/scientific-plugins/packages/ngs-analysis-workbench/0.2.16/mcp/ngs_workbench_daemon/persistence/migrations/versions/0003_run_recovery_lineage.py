"""Add root-based recovery lineage to workflow runs.

Revision ID: 0003_run_recovery_lineage
Revises: 0002_saved_workflows
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_run_recovery_lineage"
down_revision = "0002_saved_workflows"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    # LEGACY_CLEANUP(2026-09-07): Some old rows store a metadata UUID instead of the public run ID.
    # Recover it from the saved request; rows without that field retain external_run_id.
    # Retire only when pre-0003 upgrades are unsupported and this migration is squashed.
    rows = (
        connection.execute(
            sa.text(
                "SELECT id, CASE WHEN json_type(request_json, '$.plan_request.run_id') IS NULL "
                "THEN external_run_id ELSE json_extract(request_json, '$.plan_request.run_id') END "
                "AS canonical_id FROM runs"
            )
        )
        .mappings()
        .all()
    )
    owners: dict[str, str] = {}
    for row in rows:
        canonical_id = row["canonical_id"]
        if not isinstance(canonical_id, str) or not canonical_id.strip():
            raise ValueError(f"invalid canonical run ID for registry row {row['id']}")
        if canonical_id in owners:
            raise ValueError(
                f"duplicate canonical run ID {canonical_id!r}: registry rows "
                f"{owners[canonical_id]} and {row['id']}; resolve before upgrading"
            )
        owners[canonical_id] = row["id"]

    # Remove the old constraint first: valid ID swaps must not collide during
    # normalization. The enclosing migration transaction protects both rebuilds.
    with op.batch_alter_table("runs", recreate="always") as batch:
        batch.drop_constraint("uq_runs_workspace_id", type_="unique")
        batch.add_column(sa.Column("first_run_id", sa.String(), nullable=True))
        batch.add_column(
            sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1")
        )
    if rows:
        connection.execute(
            sa.text(
                "UPDATE runs SET external_run_id = :canonical_id, first_run_id = :canonical_id WHERE id = :id"
            ),
            [dict(row) for row in rows],
        )
    with op.batch_alter_table("runs", recreate="always") as batch:
        batch.alter_column("first_run_id", nullable=False)
        batch.alter_column("attempt_number", server_default=None)
        batch.create_check_constraint("ck_runs_attempt_number", "attempt_number >= 1")
        batch.create_unique_constraint(
            "uq_runs_recovery_attempt",
            ["first_run_id", "attempt_number"],
        )
        batch.create_unique_constraint("uq_runs_external_run_id", ["external_run_id"])


def downgrade() -> None:
    with op.batch_alter_table("runs", recreate="always") as batch:
        batch.drop_constraint("uq_runs_external_run_id", type_="unique")
        batch.drop_constraint("uq_runs_recovery_attempt", type_="unique")
        batch.drop_constraint("ck_runs_attempt_number", type_="check")
        batch.drop_column("attempt_number")
        batch.drop_column("first_run_id")
        batch.create_unique_constraint(
            "uq_runs_workspace_id", ["workspace_id", "binding", "external_run_id"]
        )
