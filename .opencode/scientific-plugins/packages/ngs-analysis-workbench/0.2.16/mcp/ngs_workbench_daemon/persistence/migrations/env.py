"""Alembic environment for the daemon-owned host-local registry."""

from __future__ import annotations

from alembic import context
from ngs_workbench_daemon.persistence.orm import Base

config = context.config
connection = config.attributes.get("connection")
if connection is None:
    raise RuntimeError("registry migrations require a caller-provided connection")

# SQLite cannot disable foreign keys inside a transaction. Table rebuilds must
# not cascade into events or saved-workflow references, including on downgrade.
connection.exec_driver_sql("PRAGMA foreign_keys = OFF")
connection.commit()
try:
    connection.exec_driver_sql("BEGIN IMMEDIATE")
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        render_as_batch=True,
        compare_type=True,
    )
    context.run_migrations()
    if connection.exec_driver_sql("PRAGMA foreign_key_check").first() is not None:
        raise RuntimeError("registry migration would leave invalid foreign-key references")
    connection.commit()
except BaseException:
    connection.rollback()
    raise
finally:
    connection.exec_driver_sql("PRAGMA foreign_keys = ON")
    connection.commit()
