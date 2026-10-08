"""Expose bounded compute configuration through the shared local daemon."""

from __future__ import annotations

import json
from pathlib import PurePosixPath
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from ngs_workbench_daemon import client, inspection
from ngs_workbench_daemon.hashing import sha256_bytes
from ngs_workbench_daemon.protocol import LOCAL_TARGET_PAYLOAD, TargetConfiguration
from ngs_workbench_daemon.state import daemon_directory

mcp = FastMCP(
    "ngs-compute",
    instructions=(
        "Configure existing local or SSH-accessible compute targets without installing software, "
        "launching scientific workflows, or claiming workflow readiness."
    ),
)


@mcp.tool(
    title="List configured compute targets",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    structured_output=True,
)
def list_compute_targets() -> dict[str, Any]:
    """List registered infrastructure without claiming scientific readiness."""
    if (
        client.healthy_daemon() is None
        and not (daemon_directory(create=False) / "targets.json").is_file()
    ):
        return {"count": 1, "targets": [LOCAL_TARGET_PAYLOAD]}
    return client.request("/targets", {}, role="compute")


@mcp.tool(
    title="Configure an existing SSH compute target",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    structured_output=True,
)
def configure_ssh_target(
    target_id: str,
    title: str,
    ssh_alias: str,
    workspace_root: str,
    executor: Literal["local_process", "slurm"] = "local_process",
    partition: str | None = None,
    account: str | None = None,
) -> dict[str, Any]:
    """Register nonsecret SSH and Slurm references in the local daemon."""
    identity = {
        "host_access": inspection.effective_access(ssh_alias),
        "workspace_root": PurePosixPath(workspace_root).as_posix(),
        "executor": executor,
        "executor_configuration": {
            key: value
            for key, value in {"partition": partition, "account": account}.items()
            if value is not None
        },
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    configuration = TargetConfiguration(
        target_id=target_id,
        title=title,
        description=f"Run a workflow controller through SSH alias {ssh_alias}.",
        config_hash=sha256_bytes(encoded),
        **identity,
    )
    return client.request(
        "/targets/configure", configuration.model_dump(mode="json"), role="compute"
    )


@mcp.tool(
    title="Inspect an existing SSH compute target",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    structured_output=True,
)
def inspect_compute_target(
    target_id: str,
    executable_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Observe bounded host, workspace, executable, and Slurm facts without changing them."""
    return client.request(
        "/targets/inspect",
        {"target_id": target_id, "executable_paths": executable_paths or []},
        role="compute",
        timeout=25,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
