"""Testes da integração opcional do runai (SPEC-935-R464/R465/R466/R467)."""

from __future__ import annotations

import json
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
    monkeypatch.setattr(RunAIProvisioner, "is_serving", lambda self: False)

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
    monkeypatch.setattr(RunAIProvisioner, "is_serving", lambda self: False)
    from integrations.model_router import ModelRouter

    router = ModelRouter()
    with pytest.raises(ValueError):
        router.route("coding", force_provider="runai", force_model="qwen3.5-4b")


def test_model_router_allows_runai_when_daemon_serving(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")
    monkeypatch.setattr(RunAIProvisioner, "is_serving", lambda self: True)
    monkeypatch.setattr(RunAIProvisioner, "is_available", lambda self: True)
    from integrations.model_router import ModelRouter

    router = ModelRouter()
    result = router.route("coding", force_provider="runai", force_model="auto")
    assert result.provider_id == "runai"
    assert result.authenticated is True
    assert result.mock_mode is False


def test_orchestrator_runai_http_utilities(monkeypatch):
    """Orquestrador expõe serve/stop/chat/complete/embed delegando à ponte."""
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    bridge = orch.runai
    assert bridge is not None

    monkeypatch.setattr(bridge, "is_serving", lambda: False)
    assert orch.runai_is_serving() is False
    chat_offline = orch.runai_chat([{"role": "user", "content": "oi"}])
    assert chat_offline["ok"] is False
    assert chat_offline["error"] == "daemon_offline"

    captured = {}
    monkeypatch.setattr(
        bridge,
        "is_serving",
        lambda: True,
    )

    def _fake_post(path, payload, timeout=120.0):
        captured["path"] = path
        captured["payload"] = payload
        return {"choices": [{"message": {"content": "resposta"}}]}

    monkeypatch.setattr(bridge, "_http_post_json", _fake_post)
    ok_chat = orch.runai_chat(
        [{"role": "user", "content": "oi"}],
        model="llama3.2-1b",
        max_tokens=32,
    )
    assert ok_chat["ok"] is True
    assert captured["path"] == "/v1/chat/completions"
    assert captured["payload"]["max_tokens"] == 32

    ok_comp = orch.runai_complete("hello", model="auto", max_tokens=8)
    assert ok_comp["ok"] is True
    assert captured["path"] == "/v1/completions"
    assert captured["payload"]["prompt"] == "hello"

    ok_emb = orch.runai_embed("hello world")
    assert ok_emb["ok"] is True
    assert captured["path"] == "/v1/embeddings"

    monkeypatch.setattr(bridge, "serve", lambda **kw: {"ok": True, "pid": 123})
    serve_res = orch.runai_serve(model="llama3.2-1b")
    assert serve_res["ok"] is True
    assert serve_res["pid"] == 123

    monkeypatch.setattr(bridge, "stop", lambda: {"ok": True})
    stop_res = orch.runai_stop()
    assert stop_res["ok"] is True


def test_runai_http_base_url_respects_env(monkeypatch):
    bridge = RunAIProvisioner(binary="runai")
    assert bridge.http_base_url() == "http://127.0.0.1:11435"
    monkeypatch.setenv("RUNAI_PORT", "9999")
    assert bridge.http_base_url() == "http://127.0.0.1:9999"
    assert bridge.http_base_url(port=7000) == "http://127.0.0.1:7000"


def test_runai_is_serving_false_when_http_unreachable(monkeypatch):
    def boom(*a, **k):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    bridge = RunAIProvisioner(binary="runai")
    assert bridge.is_serving() is False
    health = bridge.api_health()
    assert health["ok"] is False
    assert "connection refused" in health["detail"]


class _FakeHTTPResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_runai_chat_posts_payload_when_serving(monkeypatch):
    bridge = RunAIProvisioner(binary="runai")
    monkeypatch.setattr(bridge, "is_serving", lambda: True)

    captured = {}

    def fake_urlopen(req, timeout=120.0):
        captured["url"] = req.full_url
        captured["data"] = json.loads(req.data.decode("utf-8"))
        return _FakeHTTPResponse(
            {"choices": [{"message": {"content": "Paris"}}], "usage": {}}
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    result = bridge.chat([{"role": "user", "content": "Capital of France?"}], model="auto", max_tokens=16)
    assert result["ok"] is True
    assert result["response"]["choices"][0]["message"]["content"] == "Paris"
    assert captured["url"] == "http://127.0.0.1:11435/v1/chat/completions"
    assert captured["data"]["max_tokens"] == 16
    assert captured["data"]["messages"][0]["content"] == "Capital of France?"


def test_runai_complete_posts_payload_when_serving(monkeypatch):
    bridge = RunAIProvisioner(binary="runai")
    monkeypatch.setattr(bridge, "is_serving", lambda: True)
    captured = {}

    def fake_urlopen(req, timeout=120.0):
        captured["data"] = json.loads(req.data.decode("utf-8"))
        return _FakeHTTPResponse({"choices": [{"text": "Paris."}], "usage": {}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    result = bridge.complete("The capital of France is", temperature=0.4)
    assert result["ok"] is True
    assert result["response"]["choices"][0]["text"] == "Paris."
    assert captured["data"]["prompt"] == "The capital of France is"
    assert captured["data"]["temperature"] == 0.4


def test_runai_embed_posts_payload_when_serving(monkeypatch):
    bridge = RunAIProvisioner(binary="runai")
    monkeypatch.setattr(bridge, "is_serving", lambda: True)
    captured = {}

    def fake_urlopen(req, timeout=120.0):
        captured["data"] = json.loads(req.data.decode("utf-8"))
        return _FakeHTTPResponse({"data": [{"embedding": [1.0, 2.0]}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    result = bridge.embed("hello world")
    assert result["ok"] is True
    assert result["response"]["data"][0]["embedding"] == [1.0, 2.0]
    assert captured["data"]["input"] == "hello world"


def test_runai_list_server_models_when_serving(monkeypatch):
    bridge = RunAIProvisioner(binary="runai")
    monkeypatch.setattr(bridge, "is_serving", lambda: True)

    def fake_urlopen(*a, **k):
        return _FakeHTTPResponse({"object": "list", "data": [{"id": "auto"}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    result = bridge.list_server_models()
    assert result["ok"] is True
    assert result["response"]["data"][0]["id"] == "auto"


def test_runai_chat_returns_offline_when_daemon_down(monkeypatch):
    monkeypatch.setattr(RunAIProvisioner, "is_serving", lambda self: False)
    bridge = RunAIProvisioner(binary="runai")
    result = bridge.chat([{"role": "user", "content": "oi"}])
    assert result["ok"] is False
    assert result["error"] == "daemon_offline"
    assert "serve" in result["hint"]


def test_runai_serve_and_stop_commands(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/runai")
    captured = []

    class R:
        returncode = 0
        stdout = "daemon started"
        stderr = ""

    def fake_run(args, **kwargs):
        captured.append(args)
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = RunAIProvisioner(binary="runai")
    serve_res = bridge.serve(model="llama3.2-1b", detach=True)
    assert serve_res["ok"] is True
    assert captured[-1] == ["runai", "serve", "--detach", "--model", "llama3.2-1b"]
    stop_res = bridge.stop()
    assert stop_res["ok"] is True
    assert captured[-1] == ["runai", "stop"]


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


@pytest.mark.skipif(
    __import__("os").environ.get("RUNAI_REAL") != "1",
    reason="Smoke real HTTP só executa sob RUNAI_REAL=1",
)
def test_runai_real_http_inference_smoke():
    """Valida inferência real via daemon HTTP do runai (se disponível)."""
    bridge = RunAIProvisioner(binary="runai", timeout=120.0)
    if not bridge.is_serving():
        pytest.skip("daemon runai não está ativo em http://127.0.0.1:11435")
    models = bridge.list_server_models()
    assert models["ok"] is True
    ids = [m["id"] for m in models["response"]["data"]]
    # Pelo menos o alias "auto" deve existir
    assert "auto" in ids
    chat = bridge.chat(
        [{"role": "user", "content": "What is the capital of France? Answer in one word."}],
        model="auto",
        max_tokens=16,
    )
    assert chat["ok"] is True
    content = chat["response"]["choices"][0]["message"]["content"]
    assert isinstance(content, str) and len(content) > 0
    comp = bridge.complete("2+2=", model="auto", max_tokens=8)
    assert comp["ok"] is True
    assert isinstance(comp["response"]["choices"][0]["text"], str)
    emb = bridge.embed("hello world", model="auto")
    assert emb["ok"] is True
    assert len(emb["response"]["data"][0]["embedding"]) > 0
