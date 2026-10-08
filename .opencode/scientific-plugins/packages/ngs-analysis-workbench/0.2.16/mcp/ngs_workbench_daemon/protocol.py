"""Small authenticated control-plane contracts shared by the local clients."""

from __future__ import annotations

import json
import os
import re
import uuid
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .hashing import sha256_bytes
from .state import state_root

PROTOCOL_VERSION = 5
_MCP_ROOT = Path(__file__).resolve().parents[1]
_PLUGIN_MANIFEST = json.loads(
    (_MCP_ROOT.parent / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
)
IMPLEMENTATION_ID = str(_PLUGIN_MANIFEST["version"])
MAX_REQUEST_BYTES = 40 * 1024 * 1024
LOCAL_TARGET_PAYLOAD = {
    "target_id": "local",
    "title": "This computer",
    "provider": "ngs-analysis-workbench",
    "controller_transport": "local_process",
    "executor": "local_process",
    "workspace_access": "local_filesystem",
    "description": "Run the workflow controller as a process on this computer.",
}
CONTROLLER_ENVIRONMENT_KEYS = frozenset(
    {
        "PATH",
        "HOME",
        "USER",
        "LOGNAME",
        "SHELL",
        "LANG",
        "TMPDIR",
        "TMP",
        "TEMP",
        "JAVA_HOME",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
        "SSL_CERT_FILE",
        "REQUESTS_CA_BUNDLE",
        "CURL_CA_BUNDLE",
    }
)
CONTROLLER_ENVIRONMENT_PREFIXES = (
    "APPTAINER_",
    "AWS_",
    "CONDA_",
    "DOCKER_",
    "LC_",
    "MAMBA_",
    "NXF_",
    "PIXI_",
    "PODMAN_",
    "SINGULARITY_",
    "SNAKEMAKE_",
    "XDG_",
)
_EPHEMERAL_READINESS_FIELDS = {
    "readiness_id",
    "snapshot_id",
    "observed_at",
    "expires_at",
    "controller_candidates",
}


def run_metadata_directory(
    target_id: str,
    run_dir: str,
) -> Path:
    """Derive the daemon-owned local metadata directory for one workflow run."""
    identity = uuid.uuid5(uuid.NAMESPACE_URL, json.dumps([target_id, run_dir]))
    return state_root() / "runs" / str(identity)


def execution_run_directory(request: dict[str, Any], local_directory: str) -> str | None:
    """Project the execution directory in the recorded target's namespace."""
    if request.get("target", {}).get("target_id", "local") == "local":
        return local_directory
    remote = request.get("remote")
    return remote["run_dir"] if remote is not None else None


def current_controller_environment() -> dict[str, str]:
    """Capture the current caller's relevant runtime without unrelated secrets."""
    return {
        key: value
        for key, value in os.environ.items()
        if key in CONTROLLER_ENVIRONMENT_KEYS or key.startswith(CONTROLLER_ENVIRONMENT_PREFIXES)
    }


class FileOperation(BaseModel):
    """One exact, native-authorized local execution file effect."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["write_json", "write_approved_plan", "copy_file", "copy_tree"]
    destination: str
    source: str | None = None
    source_sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    content: dict[str, Any] | None = None


class ExecutionRequest(BaseModel):
    """The full immutable approved plan and its native-authorized execution context."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    binding: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,95}$")
    plan_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    plan: dict[str, Any]
    files: list[FileOperation] = Field(default_factory=list)
    inputs: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    environment: dict[str, str] = Field(default_factory=dict)
    authorization: str | None = Field(default=None, min_length=32, max_length=128)

    @field_validator("environment")
    @classmethod
    def _validate_environment(cls, environment: dict[str, str]) -> dict[str, str]:
        if any(
            key not in CONTROLLER_ENVIRONMENT_KEYS
            and not key.startswith(CONTROLLER_ENVIRONMENT_PREFIXES)
            for key in environment
        ):
            raise ValueError("controller environment contains an unsupported variable")
        if any("\x00" in value for value in environment.values()):
            raise ValueError("controller environment values cannot contain null bytes")
        return environment


def execution_request_checksum(request: ExecutionRequest) -> str:
    """Bind every execution effect and metadata field to its native receipt."""
    payload = request.model_dump(mode="json", exclude={"authorization"})
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


class TargetConfiguration(BaseModel):
    """One complete, secret-free compute target persisted by the daemon."""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    target_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,95}$")
    title: str = Field(min_length=1, max_length=120)
    provider: Literal["ngs-compute"] = "ngs-compute"
    controller_transport: Literal["ssh"] = "ssh"
    workspace_access: Literal["remote_filesystem"] = "remote_filesystem"
    description: str
    host_access: dict[str, str | int]
    workspace_root: str = Field(min_length=1, max_length=1024)
    executor: Literal["local_process", "slurm"] = "local_process"
    executor_configuration: dict[str, str] = Field(default_factory=dict)
    config_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @field_validator("host_access")
    @classmethod
    def _validate_host_access(cls, value: dict[str, str | int]) -> dict[str, str | int]:
        if set(value) != {
            "alias",
            "host",
            "user",
            "port",
            "host_key_policy",
            "proxy_fingerprint",
        }:
            raise ValueError("SSH access contains unsupported or missing fields")
        alias = str(value["alias"])
        if ":" in str(value["user"]) or ("@" in alias and ":" in alias.split("@", 1)[0]):
            raise ValueError("SSH username must not contain embedded credentials")
        return value

    @field_validator("workspace_root")
    @classmethod
    def _validate_workspace(cls, value: str) -> str:
        path = PurePosixPath(value)
        if not path.is_absolute() or ".." in path.parts:
            raise ValueError("SSH workspace must be an absolute POSIX path")
        return path.as_posix()

    @field_validator("executor_configuration")
    @classmethod
    def _validate_executor_configuration(cls, value: dict[str, str]) -> dict[str, str]:
        if set(value) - {"partition", "account"}:
            raise ValueError("executor configuration contains an unsupported field")
        if any(
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}", item) is None
            for item in value.values()
        ):
            raise ValueError("executor configuration contains an invalid value")
        return value

    @model_validator(mode="after")
    def _validate_identity(self) -> TargetConfiguration:
        identity = self.model_dump(
            mode="json",
            include={"host_access", "workspace_root", "executor", "executor_configuration"},
        )
        encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
        if self.config_hash != sha256_bytes(encoded):
            raise ValueError("compute target configuration identity does not match its contents")
        return self


class TargetInspection(BaseModel):
    """Bounded, read-only executable observations on a configured SSH host."""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    target_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,95}$")
    executable_paths: list[str] = Field(default_factory=list, max_length=24)


def canonical_plan_checksum(plan: dict[str, Any]) -> str:
    """Hash the existing full-plan contract while excluding observation identities."""
    payload = deepcopy(plan)
    request = payload.get("request")
    readiness = payload.get("readiness")
    if not isinstance(request, dict) or not isinstance(readiness, dict):
        raise ValueError("approved plan is missing its request or readiness")

    request.pop("runtime_snapshot_id", None)
    for field in _EPHEMERAL_READINESS_FIELDS:
        readiness.pop(field, None)
    evidence = readiness.get("evidence")
    if isinstance(evidence, list):
        readiness["evidence"] = [
            item
            for item in evidence
            if not isinstance(item, dict) or item.get("kind") != "runtime_snapshot"
        ]

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)
