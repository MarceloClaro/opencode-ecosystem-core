"""Cross the host-owned approval boundary and dispatch one registered plan."""

from __future__ import annotations

import secrets
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from ngs_workbench_daemon import client as daemon_client
from ngs_workbench_daemon.protocol import ExecutionRequest, execution_request_checksum
from ngs_workbench_daemon.state import (
    daemon_directory,
    execution_authorization_path,
    write_private_json,
)

from .plan_registry import load_approved_plan
from .plans import NextflowRunPlan, SnakemakeRunPlan
from .workflows import nextflow, snakemake


@contextmanager
def _native_authorization(request: ExecutionRequest) -> Iterator[ExecutionRequest]:
    """Issue one short-lived receipt only from the native-approved callback."""
    authorization = secrets.token_urlsafe(32)
    path = execution_authorization_path(daemon_directory(), authorization)
    approved = request.plan["request"]
    write_private_json(
        path,
        {
            "binding": request.binding,
            "plan_checksum": request.plan_checksum,
            "plan_name": approved["display_name"],
            "run_id": approved["run_id"],
            "execution_checksum": execution_request_checksum(request),
        },
    )
    try:
        yield request.model_copy(update={"authorization": authorization})
    finally:
        path.unlink(missing_ok=True)


def execute_registered_plan(
    plan_name: str,
    plan_id: str,
    plan_checksum: str,
) -> dict[str, Any]:
    """Revalidate and execute only the immutable plan identity approved by the host."""
    binding, plan = load_approved_plan(plan_name, plan_id, plan_checksum)
    if not plan.runnable:
        return {
            "ok": False,
            "kind": "run",
            "status": "blocked",
            "binding": binding,
            "plan_name": plan_name,
            "plan_id": plan_id,
            "plan_checksum": plan_checksum,
            "errors": list(plan.blockers) or ["registered plan is not runnable"],
        }

    if (
        binding == "nextflow"
        and isinstance(plan, NextflowRunPlan)
        and plan.request.workflow_source is not None
    ):
        request = nextflow.approved_execution_request(plan, plan_checksum)
    elif isinstance(plan, NextflowRunPlan):
        request = nextflow.approved_nfcore_execution_request(plan, plan_checksum)
    elif isinstance(plan, SnakemakeRunPlan):
        request = snakemake.approved_execution_request(plan, plan_checksum)
    else:  # pragma: no cover - guarded by the registry model loader.
        raise TypeError(f"unsupported registered plan: {type(plan).__name__}")

    if isinstance(request, dict):
        result = request
    else:
        with _native_authorization(request) as authorized:
            result = daemon_client.execute(authorized)
    return {
        **result,
        "target": plan.request.target.model_dump(mode="json"),
        "run_dir": (
            plan.request.remote.run_dir if plan.request.remote is not None else plan.effects.run_dir
        ),
        "kind": "run",
        "binding": binding,
        "plan_name": plan_name,
        "plan_id": plan_id,
        "plan_checksum": plan_checksum,
    }
