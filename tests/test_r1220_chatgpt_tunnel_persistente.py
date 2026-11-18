import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrations import chatgpt_tunnel_full_mcp as mod  # noqa: E402


SPEC = ROOT / "specs/SPEC-935-R1220-tunnel-mcp-persistente.md"


def test_spec_r1220_existe():
    assert SPEC.is_file()
    text = SPEC.read_text(encoding="utf-8")
    assert "SPEC-935-R1220" in text
    assert "ensure --confirm" in text
    assert "Startup" in text


def test_ensure_sem_confirm_falha_fechado(tmp_path, monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("ensure sem confirm não deve iniciar processo")

    monkeypatch.setattr(mod.subprocess, "Popen", explode)
    code = mod.main(["ensure", "--state-dir", str(tmp_path)])
    assert code == 2


def test_ensure_com_polling_confirmado_nao_duplica(tmp_path, monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("ensure não deve duplicar túnel ativo")

    monkeypatch.setattr(mod.subprocess, "Popen", explode)
    monkeypatch.setattr(mod, "status", lambda _state: {
        "tunel": "polling_confirmado", "pid": 4242, "mcp": mod.MCP_MODULE
    })
    monkeypatch.setattr(mod, "external_tunnel_pids", lambda exclude_pid=None: [])
    code = mod.main(["ensure", "--state-dir", str(tmp_path), "--confirm"])
    assert code == 0


def test_ensure_aguardando_polling_nao_duplica(tmp_path, monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("ensure não deve duplicar túnel em polling")

    monkeypatch.setattr(mod.subprocess, "Popen", explode)
    monkeypatch.setattr(mod, "status", lambda _state: {
        "tunel": "aguardando_polling", "pid": 4242, "mcp": mod.MCP_MODULE
    })
    monkeypatch.setattr(mod, "external_tunnel_pids", lambda exclude_pid=None: [])
    code = mod.main(["ensure", "--state-dir", str(tmp_path), "--confirm"])
    assert code == 0


def test_ensure_parado_com_confirm_inicia_uma_vez(tmp_path, monkeypatch):
    started = []

    def fake_start(args):
        started.append(args.state_dir)
        return 0

    monkeypatch.setattr(mod, "status", lambda _state: {"tunel": "parado", "mcp": mod.MCP_MODULE})
    monkeypatch.setattr(mod, "external_tunnel_pids", lambda exclude_pid=None: [])
    monkeypatch.setattr(mod, "start", fake_start)
    code = mod.main([
        "ensure", "--state-dir", str(tmp_path),
        "--core-dir", str(ROOT), "--key-file", str(tmp_path / "runtime.key"), "--confirm",
    ])
    assert code == 0
    assert started == [tmp_path]


def test_ensure_recusa_tunnel_externo(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "status", lambda _state: {"tunel": "parado", "mcp": mod.MCP_MODULE})
    monkeypatch.setattr(mod, "external_tunnel_pids", lambda exclude_pid=None: [999])
    with pytest.raises(mod.UserError):
        mod.ensure(type("Args", (), {
            "state_dir": tmp_path,
            "core_dir": ROOT,
            "key_file": tmp_path / "runtime.key",
            "bundle": mod.BUNDLE,
            "confirm": True,
        })())


def test_render_launcher_cmd_sanitizado():
    script = mod.render_launcher_cmd(ROOT)
    assert "wsl.exe" in script
    assert "--distribution Ubuntu" in script
    assert "-m integrations.chatgpt_tunnel_full_mcp ensure --confirm" in script
    assert "runtime.key" not in script
    assert "chatgpt_status_mcp" not in script


def test_render_ps1_cria_apenas_dois_atalhos():
    script = mod.render_shortcut_setup_ps1(
        r"C:\Users\marce\AppData\Local\OpenCodeEcosystemCore\Tunnel-v0.0.21\00-ATIVAR-MCP-COMPLETO.cmd",
        r"C:\Users\marce\OneDrive\Área de Trabalho\OpenCode Ecosystem Tunnel - MCP Completo (WSL).lnk",
        r"C:\Users\marce\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\OpenCode Ecosystem Tunnel - MCP Completo (WSL).lnk",
    )
    assert "WScript.Shell" in script
    assert script.count("CreateShortcut") == 2
    assert "WindowStyle = 7" in script
    for forbidden in ("config.toml", "app.asar", "auth", "chatgpt_status_mcp", "runtime.key"):
        assert forbidden not in script


def test_install_windows_dry_run_nao_chama_powershell(tmp_path, monkeypatch, capsys):
    def explode(*_args, **_kwargs):
        raise AssertionError("dry-run não deve chamar PowerShell")

    monkeypatch.setattr(mod.subprocess, "run", explode)
    code = mod.main([
        "install-windows", "--state-dir", str(tmp_path),
        "--windows-dir", str(tmp_path / "windows"),
        "--desktop-dir", str(tmp_path / "desktop"),
        "--startup-dir", str(tmp_path / "startup"),
    ])
    out = capsys.readouterr().out
    assert code == 0
    assert "dry-run" in out
    assert "00-ATIVAR-MCP-COMPLETO.cmd" in out
