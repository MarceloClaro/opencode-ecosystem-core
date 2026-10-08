"""Registered destinations for workflow-controller execution."""

from __future__ import annotations

from ngs_workbench_daemon import client as daemon_client
from ngs_workbench_daemon.protocol import LOCAL_TARGET_PAYLOAD
from ngs_workbench_daemon.state import daemon_directory
from pydantic import BaseModel, ConfigDict, Field


class ComputeTargetRef(BaseModel):
    """Stable identity embedded in runtime snapshots and approved plans."""

    model_config = ConfigDict(frozen=True)

    target_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,95}$")
    provider: str = Field(min_length=1, max_length=120)


class ComputeTarget(BaseModel):
    """One provider-owned destination available to the workbench."""

    model_config = ConfigDict(frozen=True)

    target_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,95}$")
    title: str = Field(min_length=1, max_length=120)
    provider: str = Field(min_length=1, max_length=120)
    controller_transport: str = Field(min_length=1, max_length=80)
    executor: str = Field(min_length=1, max_length=80)
    workspace_access: str = Field(min_length=1, max_length=80)
    description: str
    config_hash: str | None = None
    host_access: dict[str, str | int] | None = None
    workspace_root: str | None = None
    executor_configuration: dict[str, str] = Field(default_factory=dict)

    def ref(self) -> ComputeTargetRef:
        """Return the stable subset bound by runtime snapshots and plans."""
        return ComputeTargetRef(target_id=self.target_id, provider=self.provider)


def resolve_compute_target(target_id: str) -> ComputeTarget:
    """Resolve one registered target for a workflow without owning its catalog."""
    if target_id == "local":
        return ComputeTarget.model_validate(LOCAL_TARGET_PAYLOAD)
    if (
        daemon_client.healthy_daemon() is None
        and not (daemon_directory(create=False) / "targets.json").is_file()
    ):
        raise ValueError(f"compute target is not registered: {target_id}")
    for target in daemon_client.request("/targets", {})["targets"]:
        if target["target_id"] == target_id:
            return ComputeTarget.model_validate(target)
    raise ValueError(f"compute target is not registered: {target_id}")
