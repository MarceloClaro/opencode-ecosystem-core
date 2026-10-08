"""Collect bounded, read-only runtime observations on an SSH controller host."""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _managed_environments(
    commands: list[dict[str, Any]], requested_executables: list[str], deadline: float
) -> dict[str, Any]:
    managers = [
        item
        for item in commands
        if item["executable"] in {"conda", "mamba", "micromamba"}
        and item["state"] == "ready"
        and item["path"]
    ]
    paths: dict[str, list[dict[str, str]]] = {}
    warnings: list[str] = []
    incomplete = False
    for manager in managers:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            warnings.append("managed environment inspection exceeded its remaining time budget")
            incomplete = True
            break
        try:
            result = subprocess.run(
                [manager["path"], "env", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=min(5, remaining),
                check=False,
                env={**os.environ, "CONDA_OFFLINE": "true", "CONDA_NO_PLUGINS": "true"},
            )
            if result.returncode != 0:
                raise ValueError(f"environment listing exited with status {result.returncode}")
            payload = json.loads(result.stdout)
            if not isinstance(payload, dict):
                raise ValueError("managed environment list is invalid")
            candidates = payload.get("envs", [])
            if not isinstance(candidates, list):
                raise ValueError("managed environment list is invalid")
            for path in candidates:
                if isinstance(path, str) and os.path.isabs(path):
                    paths.setdefault(path, []).append(
                        {"name": manager["executable"], "path": manager["path"]}
                    )
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            warnings.append(f"{manager['executable']} environments could not be inspected: {exc}")
            incomplete = True

    environments = []
    for path, available_managers in list(paths.items())[:50]:
        root = Path(path)
        observed_commands = []
        candidates = dict.fromkeys(("nextflow", "snakemake", *requested_executables))
        for name in candidates:
            if not isinstance(name, str) or Path(name).name != name:
                continue
            executable = root / "bin" / name
            if executable.is_file() and os.access(executable, os.X_OK):
                observed_commands.append({"name": name, "path": str(executable), "state": "ready"})
        if any(item["name"] in {"nextflow", "snakemake"} for item in observed_commands):
            environments.append(
                {
                    "name": root.name,
                    "path": path,
                    "active": path == os.environ.get("CONDA_PREFIX"),
                    "discovered_by": [item["name"] for item in available_managers],
                    "managers": available_managers,
                    "commands": observed_commands,
                }
            )
    if len(paths) > 50:
        warnings.append("managed environment discovery was limited to 50 paths")
    return {
        "environments_scanned": min(len(paths), 50),
        "environments": environments,
        "truncated": incomplete or len(paths) > 50,
        "warnings": warnings,
    }


def inspect(request: dict[str, Any]) -> dict[str, Any]:
    deadline = time.monotonic() + 10
    os.environ["NXF_OFFLINE"] = "true"
    versions = {
        name: ["--version"]
        for name in (
            "python3",
            "java",
            "nextflow",
            "snakemake",
            "docker",
            "podman",
            "apptainer",
            "singularity",
            "conda",
            "mamba",
            "micromamba",
            "pixi",
            "sbatch",
            "squeue",
        )
    }
    versions["java"] = versions["nextflow"] = ["-version"]
    names = dict.fromkeys([*versions, *request["executable_paths"]])
    commands = []
    for executable in names:
        path = (
            executable
            if os.path.isabs(executable)
            and os.path.isfile(executable)
            and os.access(executable, os.X_OK)
            else shutil.which(executable)
            if not os.path.isabs(executable)
            else None
        )
        observation = {
            "executable": executable,
            "path": path,
            "state": "ready" if path else "missing",
        }
        arguments = versions.get(executable)
        if path and arguments:
            try:
                result = subprocess.run(
                    [path, *arguments], capture_output=True, text=True, timeout=3, check=False
                )
                lines = [
                    line for line in (result.stdout + "\n" + result.stderr).splitlines() if line
                ]
                if result.returncode != 0:
                    observation["state"] = "broken"
                    observation["message"] = "version probe failed"
                elif lines:
                    observation["version"] = lines[0][:200]
            except (OSError, subprocess.TimeoutExpired):
                observation["state"] = "broken"
                observation["message"] = "version probe failed"
        commands.append(observation)

    workspace = request["workspace_root"]
    exists = os.path.isdir(workspace)
    docker_path = next((item["path"] for item in commands if item["executable"] == "docker"), None)
    docker = {"path": docker_path, "daemon_reachable": False, "message": "Docker CLI is missing"}
    if docker_path:
        try:
            context = os.environ.get("DOCKER_CONTEXT", "").strip()
            endpoint = os.environ.get("DOCKER_HOST", "").strip() if not context else ""
            if not endpoint:
                selected = subprocess.run(
                    [
                        docker_path,
                        "context",
                        "inspect",
                        "--format",
                        "{{json .Endpoints.docker.Host}}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    check=False,
                )
                if selected.returncode == 0:
                    endpoint = json.loads(selected.stdout)
            local = isinstance(endpoint, str) and endpoint.lower().startswith(
                ("unix://", "npipe://")
            )
            docker.update(
                {
                    "context": context or None,
                    "endpoint": endpoint or None,
                    "endpoint_is_local": local if endpoint else None,
                }
            )
            if not local:
                docker["message"] = (
                    "remote Docker endpoint was not contacted"
                    if endpoint
                    else "Docker endpoint locality could not be verified"
                )
            else:
                details = subprocess.run(
                    [docker_path, "info", "--format", "{{json .}}"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    check=False,
                )
                if details.returncode == 0:
                    observed = json.loads(details.stdout)
                    docker.update(
                        {
                            "daemon_reachable": True,
                            "server_version": observed.get("ServerVersion"),
                            "server_os": observed.get("OSType"),
                            "server_arch": observed.get("Architecture"),
                            "message": None,
                        }
                    )
                else:
                    docker["message"] = "Docker daemon is not reachable on the controller host"
        except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
            docker["message"] = "Docker daemon could not be inspected on the controller host"

    scheduler = None
    if request["executor"] == "slurm":
        submit = shutil.which("sbatch")
        queue = shutil.which("squeue")
        control = "unknown"
        if submit and queue:
            try:
                result = subprocess.run(
                    [queue, "--noheader", "--me"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    check=False,
                )
                control = "available" if result.returncode == 0 else "unavailable"
            except (OSError, subprocess.TimeoutExpired):
                control = "unavailable"
        scheduler = {
            "kind": "slurm",
            "submit_command": submit,
            "queue_command": queue,
            "control_plane": control,
            "worker_readiness": "unknown",
            "shared_filesystem": "unknown",
        }

    return {
        "host": {
            "hostname": socket.gethostname(),
            "os": platform.system().lower(),
            "arch": platform.machine(),
        },
        "workspace": {
            "path": workspace,
            "exists": exists,
            "readable": exists and os.access(workspace, os.R_OK),
            "writable": exists and os.access(workspace, os.W_OK),
        },
        "commands": commands,
        "managed_environments": _managed_environments(
            commands, request["executable_paths"], deadline
        ),
        "docker": docker,
        "scheduler": scheduler,
    }


if __name__ == "__main__" and len(sys.argv) > 1:
    sys.stdout.write(json.dumps(inspect(json.loads(sys.argv[1])), separators=(",", ":")) + "\n")
