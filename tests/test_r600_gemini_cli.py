# -*- coding: utf-8 -*-
"""Testes TDD da integração Gemini CLI (SPEC-935-R600) — mocks."""

import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, ".")

from integrations import gemini_cli  # noqa: E402


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_proc(code, stdout="", stderr=""):
    return _FakeProc(code, stdout, stderr)


def _com_gemini(monkeypatch):
    """Disponibiliza o binário `gemini` sem depender da instalação real."""
    import shutil

    def fake_which(cmd, **kw):
        if cmd == "gemini":
            return "/usr/bin/gemini"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)


@pytest.fixture(autouse=True)
def _limpa_cache():
    gemini_cli._BIN_CACHE = None
    gemini_cli._AVAILABLE_CACHE = None
    yield
    gemini_cli._BIN_CACHE = None
    gemini_cli._AVAILABLE_CACHE = None


def test_gemini_available_sem_binario(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert gemini_cli._find_binary() is None
    assert gemini_cli.gemini_available() is False


def test_gemini_available_com_binario(monkeypatch):
    _com_gemini(monkeypatch)
    assert gemini_cli.gemini_available() is True


def test_gemini_version_com_rotulo(monkeypatch):
    _com_gemini(monkeypatch)
    monkeypatch.setattr(
        gemini_cli.subprocess, "run",
        lambda *a, **k: _fake_proc(0, "Gemini CLI v3.5.2 (build 2026)\n"),
    )
    assert gemini_cli.gemini_version() == "3.5.2"


def test_gemini_version_sem_binario(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert gemini_cli.gemini_version() is None


def test_gemini_run_monta_comando(monkeypatch):
    _com_gemini(monkeypatch)
    calls = {}

    def fake_run(args, **kw):
        calls["args"] = args
        return _fake_proc(0, "resposta do gemini\n")

    monkeypatch.setattr(gemini_cli.subprocess, "run", fake_run)
    resultado = gemini_cli.gemini_run(
        "explique o arquivo", model="gemini-2.5-flash", output_format="json"
    )
    assert resultado["ok"] is True
    assert resultado["returncode"] == 0
    args = calls["args"]
    assert args[0].endswith("gemini")
    assert "-p" in args
    assert "explique o arquivo" in args
    assert "-m" in args and "gemini-2.5-flash" in args
    assert "--output-format" in args and "json" in args
    assert resultado["stdout"] == "resposta do gemini\n"


def test_gemini_run_minimo(monkeypatch):
    _com_gemini(monkeypatch)
    monkeypatch.setattr(
        gemini_cli.subprocess, "run",
        lambda args, **kw: _fake_proc(0, "ok"),
    )
    resultado = gemini_cli.gemini_run("ola")
    assert resultado["ok"] is True
    assert "-p" in resultado["comando"] and "ola" in resultado["comando"]
    assert "--output-format" not in resultado["comando"]


def test_gemini_run_erro_nao_lanca(monkeypatch):
    _com_gemini(monkeypatch)

    def boom(*a, **k):
        raise FileNotFoundError("gemini ausente")

    monkeypatch.setattr(gemini_cli.subprocess, "run", boom)
    resultado = gemini_cli.gemini_run("x")
    assert resultado["ok"] is False
    assert resultado["returncode"] is None
    assert "gemini ausente" in resultado["stderr"]
    assert resultado["stdout"] == ""


def test_gemini_run_sem_binario(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    resultado = gemini_cli.gemini_run("x")
    assert resultado["ok"] is False
    assert "não instalado" in resultado["stderr"].lower() or "instalado" in resultado["stderr"].lower()


def test_doctor_pass_quando_instalado(monkeypatch):
    _com_gemini(monkeypatch)
    monkeypatch.setattr(
        gemini_cli.subprocess, "run",
        lambda *a, **k: _fake_proc(0, "Gemini CLI v3.5.2 (build 2026)\n"),
    )
    check = gemini_cli.doctor_check()
    assert check["status"] == "pass"
    assert "3.5.2" in check["detail"]


def test_doctor_warn_quando_ausente(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    check = gemini_cli.doctor_check()
    assert check["status"] == "warn"
    assert "não" in check["detail"].lower()


def test_install_instrucoes_contem_npm(monkeypatch):
    _com_gemini(monkeypatch)
    texto = gemini_cli.install_instructions()
    assert "npm install -g @google/gemini-cli" in texto
    assert "GEMINI_API_KEY" in texto
    assert "gemini -p" in texto


def test_main_help(monkeypatch):
    code = gemini_cli.main(["--help"])
    assert code == 0


def test_main_status(monkeypatch, capsys):
    _com_gemini(monkeypatch)
    assert gemini_cli.main(["status"]) == 0
    assert "gemini" in capsys.readouterr().out.lower()


def test_main_run_sem_prompt(monkeypatch):
    assert gemini_cli.main(["run"]) == 2


def test_main_run_com_flags(monkeypatch, capsys):
    _com_gemini(monkeypatch)
    monkeypatch.setattr(
        gemini_cli.subprocess, "run",
        lambda args, **kw: _fake_proc(0, "ok gemini"),
    )
    assert gemini_cli.main(["run", "tarefa X", "-m", "gemini-3-pro", "--timeout", "45"]) == 0
    capturado = capsys.readouterr().out
    assert "ok gemini" in capturado


def test_main_doctor_pass(monkeypatch, capsys):
    _com_gemini(monkeypatch)
    monkeypatch.setattr(
        gemini_cli.subprocess, "run",
        lambda *a, **k: _fake_proc(0, "Gemini CLI v3.5.2\n"),
    )
    assert gemini_cli.main(["doctor"]) == 0
    assert "pass" in capsys.readouterr().out


def test_main_comando_desconhecido(monkeypatch):
    assert gemini_cli.main(["bogus"]) == 2


def test_gemini_run_output_stream_json(monkeypatch):
    _com_gemini(monkeypatch)
    monkeypatch.setattr(
        gemini_cli.subprocess, "run",
        lambda args, **kw: _fake_proc(0, '{"type":"turn_complete"}'),
    )
    resultado = gemini_cli.gemini_run("deploy", output_format="stream-json")
    assert resultado["ok"] is True
    assert "stream-json" in resultado["comando"]