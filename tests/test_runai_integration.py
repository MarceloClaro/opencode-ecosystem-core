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


def test_runai_source_mode_detection(monkeypatch, tmp_path):
    root = tmp_path / "canirun"
    (root / "packages" / "runai").mkdir(parents=True)
    (root / "packages" / "runai" / "package.json").write_text("{}")
    (root / "node_modules").mkdir()
    (root / "packages" / "compatibility" / "dist").mkdir(parents=True)
    (root / "packages" / "models" / "dist").mkdir(parents=True)

    monkeypatch.setattr("shutil.which", lambda name: None if name == "runai" else f"/usr/bin/{name}")
    bridge = RunAIProvisioner(binary="runai", source_dir=str(root), bun_binary="bun", pnpm_binary="pnpm")
    assert bridge.is_binary_available() is False
    assert bridge.has_source_checkout() is True
    assert bridge.is_source_available() is True
    assert bridge.runtime_mode() == "source"


def test_runai_source_cli_executes_pnpm_dev(monkeypatch, tmp_path):
    root = tmp_path / "canirun"
    (root / "packages" / "runai").mkdir(parents=True)
    (root / "packages" / "runai" / "package.json").write_text("{}")
    (root / "node_modules").mkdir()
    (root / "packages" / "compatibility" / "dist").mkdir(parents=True)
    (root / "packages" / "models" / "dist").mkdir(parents=True)

    monkeypatch.setattr("shutil.which", lambda name: None if name == "runai" else f"/usr/bin/{name}")
    captured = {}

    class R:
        returncode = 0
        stdout = "doctor ok"
        stderr = ""

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["cwd"] = kwargs.get("cwd")
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = RunAIProvisioner(binary="runai", source_dir=str(root), bun_binary="bun", pnpm_binary="pnpm")
    result = bridge.doctor()
    assert result["ok"] is True
    assert result["mode"] == "source"
    assert captured["args"][:5] == ["/usr/bin/pnpm", "--filter", "@canirun/runai", "run", "dev"]
    assert captured["cwd"] == str(root)


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


def test_runai_browse_recommend_list_show(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")
    calls = []

    class R:
        returncode = 0
        stdout = "{}"
        stderr = ""

    def fake_run(args, **kwargs):
        calls.append(args)
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = RunAIProvisioner(binary="runai")
    assert bridge.doctor(json_mode=True)["ok"] is True
    assert bridge.browse("qwen", limit=3, json_mode=True)["ok"] is True
    assert bridge.recommend(top=2, json_mode=True)["ok"] is True
    assert bridge.list_installed(json_mode=True)["ok"] is True
    assert bridge.show("qwen3.5-4b", json_mode=True)["ok"] is True
    assert calls[0] == ["runai", "doctor", "--json"]
    assert calls[1] == ["runai", "browse", "qwen", "--limit", "3", "--json"]
    assert calls[2] == ["runai", "recommend", "--top", "2", "--json"]
    assert calls[3] == ["runai", "list", "--json"]
    assert calls[4] == ["runai", "show", "qwen3.5-4b", "--json"]


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


def test_runai_source_diagnosis(monkeypatch, tmp_path):
    root = tmp_path / "canirun"
    (root / "packages" / "runai").mkdir(parents=True)
    (root / "packages" / "runai" / "package.json").write_text("{}")
    (root / "node_modules").mkdir()
    monkeypatch.setattr("shutil.which", lambda name: None if name == "runai" else f"/usr/bin/{name}")
    bridge = RunAIProvisioner(binary="runai", source_dir=str(root), bun_binary="bun", pnpm_binary="pnpm")
    diag = bridge.source_diagnosis()
    assert diag["detected"] is True
    assert diag["dependencies_installed"] is True


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


def test_external_clis_treats_runai_source_mode_as_available(monkeypatch, tmp_path):
    root = tmp_path / "canirun"
    (root / "packages" / "runai").mkdir(parents=True)
    (root / "packages" / "runai" / "package.json").write_text("{}")
    (root / "node_modules").mkdir()
    (root / "packages" / "compatibility" / "dist").mkdir(parents=True)
    (root / "packages" / "models" / "dist").mkdir(parents=True)

    def fake_which(name):
        if name == "runai":
            return None
        if name in {"bun", "pnpm", "opencode", "agy", "claude", "ollama"}:
            return f"/usr/bin/{name}"
        return None

    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setenv("RUNAI_SOURCE_DIR", str(root))
    monkeypatch.setenv("RUNAI_BUN_BIN", "bun")
    monkeypatch.setenv("RUNAI_PNPM_BIN", "pnpm")
    from marceloclaro import doctor as doctor_mod
    import integrations.runai as runai_mod

    monkeypatch.setattr(
        runai_mod,
        "runai_provisioner",
        RunAIProvisioner(binary="runai", source_dir=str(root), bun_binary="bun", pnpm_binary="pnpm"),
    )

    check = doctor_mod._check_external_clis()
    assert "runai" not in check.detail


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
    doctor_res = orch.runai_doctor(json_mode=True)
    assert doctor_res["ok"] is True
    help_res = orch.runai_help()
    assert help_res["ok"] is True
    version_res = orch.runai_version()
    assert version_res["ok"] is True
    browse_res = orch.runai_browse("qwen", limit=2, json_mode=True)
    assert browse_res["ok"] is True
    recommend_res = orch.runai_recommend(top=2, json_mode=True)
    assert recommend_res["ok"] is True
    list_res = orch.runai_list_installed(json_mode=True)
    assert list_res["ok"] is True
    show_res = orch.runai_show("qwen3.5-4b", json_mode=True)
    assert show_res["ok"] is True
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
