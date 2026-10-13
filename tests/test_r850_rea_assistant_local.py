"""R850: contrapróvas funcionais e contratos do assistente local."""
from __future__ import annotations

import asyncio
import importlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys

import pytest

from integrations.rea_bridge import ReaBridge
from integrations import rea_layers
from marceloclaro.rea_cli import run_rea_cli

ROOT = Path(__file__).resolve().parents[1]


def assistant():
    # Bootstrap identificado à parte; nenhuma exceção de importação vale RED.
    assert importlib.util.find_spec("integrations.rea_assistant") is not None
    return importlib.import_module("integrations.rea_assistant")


def test_ida_rejeita_endpoint_remoto(tmp_path):
    path = tmp_path / "ida.json"
    path.write_text(json.dumps({"mode": "headless", "url": "https://remote.example/mcp"}))
    ok, _ = rea_layers._validate_ida_mcp_config(path)
    assert ok is False


@pytest.mark.parametrize("url", [
    "http://127.0.0.1:not-a-port/mcp", "http://127.0.0.1:70000/mcp",
    "http://127.0.0.1:0/mcp", "http://127.0.0.1:/mcp",
])
def test_url_local_rejeita_porta_invalida(url):
    ok, _ = rea_layers._validate_local_mcp_url(url)
    assert ok is False


def test_camada_rejeita_dict_sem_evidence():
    response = {"structuredContent": {"unrelated": "not evidence"}}
    assert ReaBridge._response_error(response, "layer") is not None


def test_descoberta_observa_instalacao_no_mesmo_processo(monkeypatch):
    value = {}
    monkeypatch.setattr(rea_layers, "_DISCOVERED", None)
    monkeypatch.setattr(rea_layers, "engine_environment", lambda: dict(value))
    assert rea_layers._discovered() == {}
    value["REA_ADB_PATH"] = "/local/new/adb"
    assert rea_layers._discovered().get("REA_ADB_PATH") == "/local/new/adb"


def test_ambiente_de_worker_nao_leva_credenciais():
    module = assistant()
    env = module.worker_environment({
        "PATH": "/usr/bin", "HOME": "/home/test", "LANG": "C.UTF-8",
        "OPENAI_API_KEY": "private", "FUTURE_PASSWORD": "private",
        "HTTP_PROXY": "https://proxy.example", "PYTHONPATH": "/external/code",
        "REA_SOURCE_DIR": "/local/rea", "REA_JEB_TOKEN": "private",
    }, root=ROOT)
    assert env["HOME"] == "/home/test"
    assert env["REA_SOURCE_DIR"] == "/local/rea"
    assert not any(k in env for k in (
        "OPENAI_API_KEY", "FUTURE_PASSWORD", "HTTP_PROXY", "REA_JEB_TOKEN"))
    assert env["PYTHONPATH"] == str(ROOT)


def test_namespace_real_isola_rede_do_host():
    module = assistant()
    if sys.platform != "linux":
        pytest.skip("isolamento Linux/WSL; ausência deve bloquear análise no produto")
    host = socket.socket()
    host.bind(("127.0.0.1", 0))
    host.listen()
    host.settimeout(0.2)
    try:
        report = module.run_isolated_worker({
            "operation": "probe", "probe_port": host.getsockname()[1]},
            root=ROOT, timeout_seconds=10)
        assert report["success"] is True
        privacy = report["privacy"]
        assert privacy["network_namespace"] != os.readlink("/proc/self/ns/net")
        assert privacy["interfaces"] == ["lo"]
        assert privacy["host_probe_connected"] is False
        assert privacy["external_route_available"] is False
        with pytest.raises(socket.timeout):
            host.accept()
    finally:
        host.close()


def test_detecta_tipos_sem_executar_alvo(tmp_path):
    module = assistant()
    cases = [("x.bin", b"\x7fELF" + b"\x00" * 64, "native"),
             ("bundle.js", b"export function sum(a,b){return a+b}", "javascript"),
             ("index.html", b"<!doctype html><title>Local</title>", "html")]
    for name, data, expected in cases:
        p = tmp_path / name
        p.write_bytes(data)
        assert module.detect_target_kind(p) == expected
    assert not (tmp_path / "executed").exists()


def test_explicacao_distingue_achados_e_limites():
    module = assistant()
    report = {"success": True, "target_kind": "dotnet",
              "findings": [{"description": "Metadados declaram duas classes.", "evidence_id": "ev-local"}],
              "limitations": ["Não executou a aplicação.", "Metadados não reconstruem o código-fonte."],
              "privacy": {"mode": "isolated_local_analysis"}, "externally_validated": False}
    text = module.explain_report(report)
    assert "duas classes" in text and "ev-local" in text
    assert "Não executou" in text and "não reconstruem" in text
    assert "certificado" not in text.lower()
    failure = module.explain_report({"success": False, "error": "provider indisponível"})
    assert "indisponível" in failure and "concluída" not in failure


@pytest.mark.parametrize("operation,extra", [
    ("setup", []), ("inspect", ["/local/app.js", "--kind", "javascript", "--format", "text"]),
])
def test_cli_encaminha_setup_e_inspect_ao_primario(operation, extra, capsys):
    calls = []

    class Primary:
        def rea_assistant_action(self, config):
            calls.append(config)
            return {"success": True, "operation": operation, "findings": [], "limitations": []}

    assert run_rea_cli([operation, *extra], lambda **kwargs: Primary()) == 0
    assert len(calls) == 1 and calls[0]["operation"] == operation
    if operation == "inspect":
        assert calls[0]["path"] == "/local/app.js" and calls[0]["kind"] == "javascript"
    assert capsys.readouterr().out


def test_setup_registra_perfil_local_sem_alterar_config_global(tmp_path):
    module = assistant()
    original = {"provider": {"cloud": {}}, "mcp": {
        "foreign": {"type": "remote", "url": "https://remote.example/mcp", "enabled": True}}}
    path = tmp_path / "opencode.json"
    path.write_text(json.dumps(original))
    before = path.read_bytes()
    report = module.setup_local_agent(root=tmp_path, model="local-test",
                                      model_endpoint="http://127.0.0.1:11434/v1")
    assert report["success"] is True
    profile = json.loads(Path(report["profile_path"]).read_text())
    assert profile["enabled_providers"] == ["rea_local"]
    assert profile["model"] == "rea_local/local-test"
    assert profile["mcp"]["foreign"]["enabled"] is False
    assert profile["provider"]["rea_local"]["options"]["baseURL"] == "http://127.0.0.1:11434/v1"
    assert profile["mcp"]["rea-local-assistant"]["enabled"] is True
    assert path.read_bytes() == before
    assert Path(report["mcp_windows_path"]).is_file()


def test_setup_rejeita_endpoint_de_modelo_remoto(tmp_path):
    module = assistant()
    with pytest.raises(ValueError):
        module.setup_local_agent(root=tmp_path, model="local-test",
                                model_endpoint="https://api.remote.example/v1")
    assert not (tmp_path / ".opencode/rea/local-assistant/opencode.json").exists()


def test_mcp_expoe_somente_interface_local():
    assert importlib.util.find_spec("integrations.rea_assistant_mcp") is not None
    module = importlib.import_module("integrations.rea_assistant_mcp")
    tools = asyncio.run(module.create_mcp_server().list_tools())
    assert {tool.name for tool in tools} == {
        "core_rea_status", "core_rea_inspect", "core_rea_explain", "core_rea_setup"}
    assert all(tool.annotations.openWorldHint is False for tool in tools)
