"""SPEC-935-R843: gates fail-closed das 3 camadas de licença comercial (IDA, Hopper, JEB).

Sem licença do operador, as camadas permanecem pendentes — nunca são falsificadas.
Os validadores exigem o formato documentado pelo REA 6.4.0; configuração ausente,
malformada ou um caminho existente porém inválido NÃO marca a camada como pronta.
"""

from __future__ import annotations

import json

import pytest

from integrations import rea_layers


# --- REA_IDA_MCP_CONFIG: formatos documentados em docs/ida-provider.md --------

def test_ida_accepts_stdio_registration(tmp_path):
    config = tmp_path / "ida.json"
    config.write_text(json.dumps({"command": "python", "args": ["server.py", "--ida-rpc",
                                                               "http://127.0.0.1:13337"]}))
    assert rea_layers._validate_ida_mcp_config(config) == (True, "registro stdio/headless válido")


def test_ida_accepts_headless_supervisor_with_env(tmp_path):
    config = tmp_path / "ida.json"
    config.write_text(json.dumps({"command": "idalib-mcp", "args": ["--stdio", "--max-workers", "1"],
                                  "mode": "headless", "env": {"IDADIR": "/opt/ida"}}))
    assert rea_layers._validate_ida_mcp_config(config)[0] is True


def test_ida_accepts_local_url_supervisor(tmp_path):
    config = tmp_path / "ida.json"
    config.write_text(json.dumps({"url": "http://127.0.0.1:8745/mcp", "mode": "headless"}))
    assert rea_layers._validate_ida_mcp_config(config)[0] is True


def test_ida_accepts_mcp_servers_entry(tmp_path):
    config = tmp_path / "ida.json"
    config.write_text(json.dumps({"mcpServers": {"ida-pro-mcp": {"command": "python",
                                                                 "args": ["server.py"]}}}))
    assert rea_layers._validate_ida_mcp_config(config)[0] is True


@pytest.mark.parametrize("payload", [
    "[]", "{}", '{"command":"python"}', '{"command":"python","args":"x"}',
    '{"command":"python","args":[1]}', '{"command":"python","args":[],"mode":"gui"}',
    '{"url":"ftp://127.0.0.1/x"}', '{"mcpServers":{}}', '{"mcpServers":{"other":{"command":"x","args":[]}}}',
])
def test_ida_rejects_malformed_config(tmp_path, payload):
    config = tmp_path / "ida.json"
    config.write_text(payload)
    assert rea_layers._validate_ida_mcp_config(config)[0] is False


def test_ida_rejects_invalid_json(tmp_path):
    config = tmp_path / "ida.json"
    config.write_text("{not json")
    ok, reason = rea_layers._validate_ida_mcp_config(config)
    assert ok is False and "JSON inválido" in reason


# --- REA_JEB_MCP_URL: restrições de docs/jeb-analysis.md ----------------------

def test_jeb_accepts_default_local_endpoint():
    assert rea_layers._validate_local_mcp_url("http://127.0.0.1:8425/mcp")[0] is True
    assert rea_layers._validate_local_mcp_url("https://[::1]:9000/mcp")[0] is True


@pytest.mark.parametrize("url", [
    "http://example.com:8425/mcp", "http://localhost:8425/mcp", "http://192.168.0.5:8425/mcp",
    "ftp://127.0.0.1:8425/mcp", "http://user:pass@127.0.0.1:8425/mcp",
    "http://127.0.0.1:8425/mcp?x=1", "http://127.0.0.1:8425/mcp#frag", "127.0.0.1:8425",
])
def test_jeb_rejects_non_local_or_unsafe_url(url):
    assert rea_layers._validate_local_mcp_url(url)[0] is False


def test_jeb_requires_explicit_configuration(monkeypatch, tmp_path):
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    monkeypatch.delenv("REA_JEB_MCP_URL", raising=False)
    layer = rea_layers.probe_layer("jeb")
    assert layer["ready"] is False and layer["env"][0]["ok"] is False
    monkeypatch.setenv("REA_JEB_MCP_URL", "http://10.0.0.9:8425/mcp")  # remoto: rejeitado
    assert rea_layers.probe_layer("jeb")["ready"] is False
    monkeypatch.setenv("REA_JEB_MCP_URL", "http://127.0.0.1:8425/mcp")
    assert rea_layers.probe_layer("jeb")["ready"] is True


# --- HOPPER_LAUNCHER_PATH: launcher real, sem env inventada -------------------

def test_hopper_uses_documented_launcher_variable():
    layer = rea_layers.layer("native_hopper")
    assert layer["env"][0]["name"] == "HOPPER_LAUNCHER_PATH"
    assert all(item["name"] != "REA_HOPPER_CONFORMANCE_MANIFEST_PATH" for item in layer["env"])
    assert "conformidade" not in (rea_layers.REQUIREMENTS["native_hopper"] or "")


def test_hopper_pending_without_launcher_and_ready_with_one(monkeypatch, tmp_path):
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    monkeypatch.setattr(rea_layers, "HOPPER_DEFAULT_LAUNCHERS", ())
    monkeypatch.delenv("HOPPER_LAUNCHER_PATH", raising=False)
    assert rea_layers.probe_layer("native_hopper")["ready"] is False
    launcher = tmp_path / "Hopper"
    launcher.write_text("#!/bin/sh\nexit 0\n")
    launcher.chmod(0o755)
    monkeypatch.setenv("HOPPER_LAUNCHER_PATH", str(launcher))
    assert rea_layers.probe_layer("native_hopper")["ready"] is True


def test_hopper_launcher_discovery_covers_documented_defaults(monkeypatch, tmp_path):
    default = tmp_path / "home" / ".local/share/rea/hopper/bin/Hopper"
    default.parent.mkdir(parents=True)
    default.write_text("#!/bin/sh\nexit 0\n")
    default.chmod(0o755)
    monkeypatch.setattr(rea_layers, "NATIVE_ROOT", tmp_path / "native")
    monkeypatch.setattr(rea_layers, "HOPPER_DEFAULT_LAUNCHERS", (default,))
    monkeypatch.delenv("HOPPER_LAUNCHER_PATH", raising=False)
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    assert rea_layers.engine_environment()["HOPPER_LAUNCHER_PATH"] == str(default)


def test_receipt_lists_only_commercial_layers_as_pending():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "outputs" / "core-r843"
    receipt = json.loads((root / "config-gates.json").read_text())
    commercial = {"native_ida", "native_hopper", "jeb"}
    # fail-closed: só camadas de licença/serviço comercial podem ficar pendentes
    assert set(receipt["pending"]) <= commercial
    # IDA e JEB não têm caminho de instalação automatizável neste host
    assert {"native_ida", "jeb"} <= set(receipt["pending"])
    assert set(receipt["gates"]) == commercial
    assert receipt["flags"] == {"externally_validated": False, "confidence_promoted": False}
