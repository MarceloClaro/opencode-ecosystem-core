"""SPEC-935-R842: motores fechados sem invenção de caminhos; provas de host opcionais."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

import pytest

from integrations import rea_layers


def test_nothing_invented_when_no_artifacts(monkeypatch, tmp_path):
    monkeypatch.setattr(rea_layers, "NATIVE_ROOT", tmp_path)
    monkeypatch.setattr(rea_layers, "PLAYWRIGHT_HOME", tmp_path / "playwright")
    monkeypatch.setattr(rea_layers, "HOPPER_DEFAULT_LAUNCHERS", ())
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    monkeypatch.setenv("PATH", "")
    for name in list(os.environ):
        if name.startswith("REA_") or name == "CORE_BROWSER_HOME":
            monkeypatch.delenv(name, raising=False)
    environment = rea_layers.engine_environment()
    assert environment == {}


def test_operator_override_wins_over_discovery(monkeypatch, tmp_path):
    monkeypatch.setattr(rea_layers, "NATIVE_ROOT", tmp_path)
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    monkeypatch.setenv("REA_ADB_PATH", "/operator/adb")
    monkeypatch.setenv("REA_BROWSER_EXECUTABLE", "/operator/chrome")
    environment = rea_layers.engine_environment()
    assert "REA_ADB_PATH" not in environment  # descoberta nunca substitui override
    from integrations.rea_bridge import ReaBridge
    child = ReaBridge._child_environment()
    assert child["REA_ADB_PATH"] == "/operator/adb"
    assert child["REA_BROWSER_EXECUTABLE"] == "/operator/chrome"


def test_browser_executable_is_required(monkeypatch):
    browser = rea_layers._BY_ID["browser"]
    assert not browser["env"][0].get("optional")
    assert browser["env"][0]["name"] == "REA_BROWSER_EXECUTABLE"


def test_env_state_is_kind_aware(monkeypatch, tmp_path):
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    command = tmp_path / "adb"
    command.write_text("#!/bin/sh\nexit 0\n")
    command.chmod(0o755)
    monkeypatch.setenv("REA_ADB_PATH", str(command))
    state = rea_layers._env_state({"name": "REA_ADB_PATH", "kind": "command"})
    assert state["ok"] is True and state["resolved"] == str(command.resolve())
    monkeypatch.setenv("REA_PWNDBG_VENV_PATH", str(tmp_path))
    directory = rea_layers._env_state({"name": "REA_PWNDBG_VENV_PATH", "kind": "dir"})
    assert directory["ok"] is True
    monkeypatch.setenv("REA_PWNDBG_GDBINIT", str(tmp_path / "absent"))
    missing = rea_layers._env_state({"name": "REA_PWNDBG_GDBINIT", "kind": "path"})
    assert missing["ok"] is False


# --- verificações reais de host: pulam quando o artefato não existe -----------

def _discovered():
    return rea_layers.engine_environment()


@pytest.mark.skipif(not _discovered().get("REA_ADB_PATH"), reason="adb ausente no host")
def test_host_adb_ready():
    assert rea_layers.probe_layer("android_adb")["ready"] is True


@pytest.mark.skipif(not _discovered().get("REA_BROWSER_EXECUTABLE"), reason="chromium ausente no host")
def test_host_browser_ready():
    assert rea_layers.probe_layer("browser")["ready"] is True


def _pwntools_python():
    return _discovered().get("REA_PWNTOOLS_PYTHON")


@pytest.mark.skipif(not _pwntools_python(), reason="venv pwntools ausente no host")
def test_host_pwntools_imports():
    code = "import pwn, elftools, unicorn; print('pwntools-ok')"
    process = subprocess.run([_pwntools_python(), "-c", code],
                             capture_output=True, text=True, timeout=120)
    assert process.returncode == 0 and "pwntools-ok" in process.stdout
    assert _discovered()["REA_PWNTOOLS_PYTHON"] == _pwntools_python()


@pytest.mark.skipif(not (_discovered().get("REA_PWNDBG_GDBINIT")
                         and _discovered().get("REA_PWNDBG_VENV_PATH")),
                    reason="pwndbg ausente no host")
def test_host_core_crash_ready_when_all_four_present():
    environment = _discovered()
    required = ("REA_PWNTOOLS_PYTHON", "REA_PWNDBG_GDB", "REA_PWNDBG_GDBINIT", "REA_PWNDBG_VENV_PATH")
    if any(environment.get(name) is None for name in required):
        pytest.skip("algum motor de core crash ausente")
    assert rea_layers.probe_layer("native_core_crash")["ready"] is True


def test_receipts_and_live_evidence_present():
    root = Path(__file__).resolve().parents[1] / "outputs" / "core-r842"
    receipt = json.loads((root / "install-receipt.json").read_text())
    assert receipt["readiness"]["pending"] == 3
    assert receipt["flags"] == {"externally_validated": False, "confidence_promoted": False}
    pending = {item["id"] for item in receipt["pending"]}
    assert pending == {"native_ida", "native_hopper", "jeb"}
    live = json.loads((root / "live-evidence.json").read_text())
    assert set(live) == {"native_offline_elf", "evm", "firmware"}
    assert all(live[name]["success"] is True for name in live)
    assert all(live[name]["evidence_id"] and live[name]["response_sha256"] for name in live)