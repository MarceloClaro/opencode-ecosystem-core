"""Run one fixed, read-only observation program on a configured SSH host."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .hashing import sha256_bytes
from .protocol import TargetInspection


def effective_access(alias: str) -> dict[str, Any]:
    """Resolve the nonsecret effective identity of an SSH transport alias."""
    result = subprocess.run(
        ["ssh", "-G", "-o", "BatchMode=yes", "--", alias],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("SSH configuration cannot resolve the requested target")
    values = {
        key: value
        for line in result.stdout.splitlines()
        if " " in line
        for key, value in [line.split(" ", 1)]
    }
    proxy = f"{values.get('proxycommand', 'none')}\0{values.get('proxyjump', 'none')}"
    return {
        "alias": alias,
        "host": values["hostname"],
        "user": values["user"],
        "port": int(values["port"]),
        "host_key_policy": values.get("stricthostkeychecking", "unknown"),
        "proxy_fingerprint": sha256_bytes(proxy.encode()),
    }


_REMOTE_PROBE = Path(__file__).with_name("remote_probe.py").read_text(encoding="utf-8")


def inspect_target(target: dict[str, Any], request: TargetInspection) -> dict[str, Any]:
    """Inspect only daemon-owned target configuration with the fixed remote program."""
    if target.get("controller_transport") != "ssh":
        raise ValueError("bounded SSH inspection requires a configured SSH target")
    payload = {
        "workspace_root": target["workspace_root"],
        "executor": target["executor"],
        "executable_paths": request.executable_paths,
    }
    source = (
        f"{_REMOTE_PROBE}\n"
        f"print(json.dumps(inspect(json.loads({json.dumps(payload, separators=(',', ':'))!r})), "
        'separators=(",", ":")))\n'
    )
    argv = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8"]
    argv.extend([target["host_access"]["alias"], "python3", "-"])
    try:
        result = subprocess.run(
            argv,
            input=source,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("SSH host did not respond before the inspection timeout") from exc
    if result.returncode != 0:
        error = result.stderr.lower()
        if "permission denied" in error:
            raise ValueError("SSH access to the configured host was denied")
        if "python3" in error and "not found" in error:
            raise ValueError("SSH host does not provide the required Python 3 interpreter")
        raise ValueError("SSH host is unreachable or its inspection could not complete")
    try:
        observed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("SSH host returned invalid inspection results") from exc
    if not isinstance(observed, dict):
        raise ValueError("SSH host returned invalid inspection results")
    return {**observed, "target_id": target["target_id"], "config_hash": target["config_hash"]}
