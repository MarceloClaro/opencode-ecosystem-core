"""Testes da integração opcional do runai (SPEC-935-R464)."""

from __future__ import annotations

import subprocess
import urllib.error

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
    aliased = bridge.model_info("gemma-4-E2B-it")
    assert aliased["known"] is True
    assert aliased["id"] == "gemma4-e2b-it"
    unknown = bridge.model_info("modelo-x")
    assert unknown["known"] is False


def test_runai_help_and_version(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")

    class RH:
        returncode = 0
        stdout = "usage: runai [doctor|pull|run]"
        stderr = ""

    class RV:
        returncode = 0
        stdout = "runai 1.2.3"
        stderr = ""

    calls = {"n": 0}

    def fake_run(args, **kwargs):
        calls["n"] += 1
        if "--help" in args:
            return RH()
        return RV()

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = RunAIProvisioner(binary="runai")
    help_res = bridge.help()
    assert help_res["ok"] is True
    assert "usage" in help_res["stdout"]
    ver_res = bridge.version()
    assert ver_res["ok"] is True
    assert ver_res["parsed_version"] == "1.2.3"


def test_doctor_check_runai_warn_when_absent(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    from marceloclaro import doctor as doctor_mod

    check = doctor_mod._check_runai()
    assert check.status == "warn"
    assert "runai" in check.detail


def test_runai_installer_diagnosis_404(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)

    def fake_urlopen(*args, **kwargs):
        raise urllib.error.HTTPError(
            url="https://registry.npmjs.org/@canirun%2Frunai",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    bridge = RunAIProvisioner(binary="runai")
    diag = bridge.installer_diagnosis()
    assert diag["ok"] is False
    assert diag["status_code"] == 404


def test_doctor_check_runai_warns_on_upstream_404(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)

    def fake_urlopen(*args, **kwargs):
        raise urllib.error.HTTPError(
            url="https://registry.npmjs.org/@canirun%2Frunai",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    from marceloclaro import doctor as doctor_mod

    check = doctor_mod._check_runai()
    assert check.status == "warn"
    assert "404" in check.detail or "inconsistência upstream" in check.detail


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
        def __init__(self, stdout="doctor ok"):
            self.returncode = 0
            self.stdout = stdout
            self.stderr = ""

    class P:
        pid = 999

    def fake_run(args, **kwargs):
        if "--help" in args:
            return R("usage: runai")
        if "--version" in args or "version" in args:
            return R("runai 1.2.3")
        return R("doctor ok")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: P())

    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    status = orch.runai_status()
    assert status["available"] is True
    help_res = orch.runai_help()
    assert help_res["ok"] is True
    version_res = orch.runai_version()
    assert version_res["ok"] is True
    pull = orch.runai_pull_model("qwen3.5-4b")
    assert pull["ok"] is True
    launched = orch.runai_launch_model("qwen3.5-4b")
    assert launched["ok"] is True
    assert launched["pid"] == 999


def test_model_router_status_inventories_runai(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")

    class R:
        returncode = 0
        stdout = "doctor ok"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    from integrations.model_router import ModelRouter

    router = ModelRouter()
    status = router.status()
    assert "runai" in status["providers"]
    assert status["providers"]["runai"]["scope"].startswith("provisionador local")
    assert status["providers"]["runai"]["provisioning_only"] is True


def test_model_router_refuses_runai_as_completion_provider(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")
    from integrations.model_router import ModelRouter

    router = ModelRouter()
    with pytest.raises(ValueError):
        router.route("coding", force_provider="runai", force_model="qwen3.5-4b")


@pytest.mark.skipif(
    __import__("os").environ.get("RUNAI_REAL") != "1",
    reason="Smoke real do runai só executa sob RUNAI_REAL=1",
)
def test_runai_real_doctor_smoke():
    bridge = RunAIProvisioner(binary="runai", timeout=120.0)
    if not bridge.is_available():
        pytest.skip("runai não instalado no ambiente real")
    result = bridge.doctor()
    assert result["exit_code"] in (0, 1)
    assert isinstance(result["stdout"], str)
    assert isinstance(result["stderr"], str)
