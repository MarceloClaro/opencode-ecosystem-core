"""Testes da integração opcional do runai (SPEC-935-R464)."""

from __future__ import annotations

import subprocess

import pytest

from integrations.runai import RunAIProvisioner


def test_runai_is_available_false_when_absent(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    bridge = RunAIProvisioner(binary="runai")
    assert bridge.is_available() is False


def test_runai_doctor_structured_when_absent(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    bridge = RunAIProvisioner(binary="runai")
    result = bridge.doctor()
    assert result["ok"] is False
    assert result["exit_code"] == 127
    assert "install.sh" in result["stderr"]


def test_runai_doctor_success(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")

    class R:
        returncode = 0
        stdout = "doctor ok"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    bridge = RunAIProvisioner(binary="runai")
    result = bridge.doctor()
    assert result["ok"] is True
    assert result["exit_code"] == 0
    assert result["stdout"] == "doctor ok"


def test_runai_pull_calls_correct_command(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")
    captured = {}

    class R:
        returncode = 0
        stdout = "pulled"
        stderr = ""

    def fake_run(args, **kwargs):
        captured["args"] = args
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = RunAIProvisioner(binary="runai")
    result = bridge.pull("qwen3.5-4b")
    assert result["ok"] is True
    assert captured["args"] == ["runai", "pull", "qwen3.5-4b"]


def test_runai_run_launches_subprocess(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")

    class P:
        pid = 4321

    def fake_popen(args, **kwargs):
        assert args == ["runai", "run", "qwen3.5-4b"]
        return P()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    bridge = RunAIProvisioner(binary="runai")
    result = bridge.run("qwen3.5-4b")
    assert result["ok"] is True
    assert result["pid"] == 4321
    assert result["launched"] is True


def test_runai_timeout(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["runai", "doctor"], timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = RunAIProvisioner(binary="runai")
    result = bridge.doctor()
    assert result["ok"] is False
    assert result["exit_code"] == 124


def test_runai_model_info_known_and_unknown():
    bridge = RunAIProvisioner(binary="runai")
    known = bridge.model_info("qwen3.5-4b")
    assert known["known"] is True
    unknown = bridge.model_info("modelo-x")
    assert unknown["known"] is False


def test_doctor_check_runai_warn_when_absent(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    from marceloclaro import doctor as doctor_mod

    check = doctor_mod._check_runai()
    assert check.status == "warn"
    assert "install.sh" in check.detail


def test_doctor_check_runai_pass_when_available(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")

    class R:
        returncode = 0
        stdout = "doctor ok"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    from marceloclaro import doctor as doctor_mod

    check = doctor_mod._check_runai()
    assert check.status == "pass"
    assert "doctor OK" in check.detail


def test_orchestrator_runai_utilities(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")

    class R:
        returncode = 0
        stdout = "doctor ok"
        stderr = ""

    class P:
        pid = 999

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: P())

    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    status = orch.runai_status()
    assert status["available"] is True
    pull = orch.runai_pull_model("qwen3.5-4b")
    assert pull["ok"] is True
    launched = orch.runai_launch_model("qwen3.5-4b")
    assert launched["ok"] is True
    assert launched["pid"] == 999
