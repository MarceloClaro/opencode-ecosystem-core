"""Gates do smoke test PyPI para o SDK Tiangong em ambiente isolado."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


VENV = Path("/tmp/opencode/gjq-client-venv")
PYTHON = VENV / "bin" / "python"
EXPECTED_VERSION = "0.2.2"


def _inspect_isolated_install() -> dict:
    assert PYTHON.is_file(), f"interpretador isolado ausente: {PYTHON}"
    script = r'''
import importlib.metadata as metadata
import json
import pathlib
import sys
import gjq_client
from gjq_client import LocalSimulator, Sampler

distribution = metadata.distribution("gjq-client")
print(json.dumps({
    "version": distribution.version,
    "prefix": str(pathlib.Path(sys.prefix).resolve()),
    "module_path": str(pathlib.Path(gjq_client.__file__).resolve()),
    "direct_url": distribution.read_text("direct_url.json"),
    "local_simulator_importable": callable(LocalSimulator),
    "sampler_importable": callable(Sampler),
    "api_key_present": bool(__import__("os").environ.get("GJQ_API_KEY")),
}))
'''
    child_env = os.environ.copy()
    child_env.pop("GJQ_API_KEY", None)
    child_env.pop("PYTHONPATH", None)
    child_env.pop("PYTHONHOME", None)
    child_env["PYTHONNOUSERSITE"] = "1"
    child_env["HOME"] = "/tmp/opencode/gjq-client-home"
    completed = subprocess.run(
        [str(PYTHON), "-c", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=45,
        env=child_env,
    )
    assert completed.returncode == 0, completed.stderr[-4000:]
    return json.loads(completed.stdout)


def test_official_release_is_importable_only_from_isolated_venv():
    result = _inspect_isolated_install()
    assert result["version"] == EXPECTED_VERSION
    assert result["prefix"] == str(VENV.resolve())
    assert Path(result["module_path"]).is_relative_to(VENV.resolve())


def test_local_sdk_symbols_import_without_cloud_authentication():
    result = _inspect_isolated_install()
    assert result["local_simulator_importable"] is True
    assert result["sampler_importable"] is True
    assert result["api_key_present"] is False


def test_isolated_python_environment_and_distribution_origin():
    result = _inspect_isolated_install()
    assert result["prefix"] == str(VENV.resolve())
    assert result["version"] == EXPECTED_VERSION
    assert result["direct_url"] is None


def test_smoke_does_not_construct_cloud_client_or_submit_jobs():
    # The subprocess imports only package metadata and local classes. It never
    # constructs GJQRuntimeService, chooses a backend, or calls a job API.
    result = _inspect_isolated_install()
    assert result["api_key_present"] is False
    assert result["local_simulator_importable"] is True
