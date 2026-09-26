# -*- coding: utf-8 -*-
"""Testes TDD da integração Reasonix/DeepSeek-Reasonix (SPEC-935-R602) — mocks."""

import shutil
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, ".")

from integrations import reasonix_cli  # noqa: E402


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_proc(code, stdout="", stderr=""):
    return _FakeProc(code, stdout, stderr)


def _com_reasonix(monkeypatch):
    def fake_which(cmd, **kw):
        if cmd in ("reasonix", "dsnix"):
            return "/usr/bin/reasonix"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)


@pytest.fixture(autouse=True)
def _limpa_cache():
    reasonix_cli._BIN_CACHE = None
    reasonix_cli._AVAILABLE_CACHE = None
    yield
    reasonix_cli._BIN_CACHE = None
    reasonix_cli._AVAILABLE_CACHE = None


def test_available_sem_binario(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert reasonix_cli._find_binary() is None
    assert reasonix_cli.reasonix_available() is False


def test_available_com_binario(monkeypatch):
    _com_reasonix(monkeypatch)
    assert reasonix_cli.reasonix_available() is True


def test_version_com_rotulo(monkeypatch):
    _com_reasonix(monkeypatch)
    monkeypatch.setattr(
        reasonix_cli.subprocess, "run",
        lambda *a, **k: _fake_proc(0, "Reasonix 1.4.2 (go)\n"),
    )
    assert reasonix_cli.reasonix_version() == "1.4.2"


def test_version_sem_binario(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert reasonix_cli.reasonix_version() is None


def test_run_monta_comando(monkeypatch):
    _com_reasonix(monkeypatch)
    calls = {}

    def fake_run(args, **kw):
        calls["args"] = args
        return _fake_proc(0, "implementado!\n")

    monkeypatch.setattr(reasonix_cli.subprocess, "run", fake_run)
    resultado = reasonix_cli.reasonix_run("implemente o modulo X")
    assert resultado["ok"] is True
    assert resultado["returncode"] == 0
    args = calls["args"]
    assert args[0].endswith("reasonix")
    assert args[1] == "run"
    assert "implemente o modulo X" in args
    assert resultado["stdout"] == "implementado!\n"


def test_run_aceita_dir(monkeypatch):
    _com_reasonix(monkeypatch)
    monkeypatch.setattr(
        reasonix_cli.subprocess, "run",
        lambda args, **kw: _fake_proc(0, "ok"),
    )
    resultado = reasonix_cli.reasonix_run("tarefa", directory="/tmp/x")
    assert resultado["ok"] is True
    assert "--dir" in resultado["comando"] and "/tmp/x" in resultado["comando"]


def test_run_erro_nao_lanca(monkeypatch):
    _com_reasonix(monkeypatch)

    def boom(*a, **k):
        raise FileNotFoundError("reasonix ausente")

    monkeypatch.setattr(reasonix_cli.subprocess, "run", boom)
    resultado = reasonix_cli.reasonix_run("x")
    assert resultado["ok"] is False
    assert "reasonix ausente" in resultado["stderr"]


def test_run_sem_binario(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    resultado = reasonix_cli.reasonix_run("x")
    assert resultado["ok"] is False
    assert "instalado" in resultado["stderr"].lower()


def test_doctor_pass(monkeypatch):
    _com_reasonix(monkeypatch)
    monkeypatch.setattr(
        reasonix_cli.subprocess, "run",
        lambda args, **kw: _fake_proc(0, "reasonix doctor: ok\n"),
    )
    check = reasonix_cli.doctor_check()
    assert check["status"] == "pass"
    assert "1.4.2" in check["detail"] or "ok" in check["detail"].lower()


def test_doctor_warn(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    check = reasonix_cli.doctor_check()
    assert check["status"] == "warn"


def test_install_instrucoes(monkeypatch):
    texto = reasonix_cli.install_instructions()
    assert "npm install -g reasonix" in texto
    assert "platform.deepseek.com/api_keys" in texto
    assert "reasonix run" in texto


def test_main_help():
    assert reasonix_cli.main(["--help"]) == 0


def test_main_status(monkeypatch, capsys):
    _com_reasonix(monkeypatch)
    monkeypatch.setattr(
        reasonix_cli.subprocess, "run",
        lambda *a, **k: _fake_proc(0, "Reasonix 1.4.2 (go)\n"),
    )
    assert reasonix_cli.main(["status"]) == 0
    assert "reasonix" in capsys.readouterr().out.lower()


def test_main_run_sem_prompt():
    assert reasonix_cli.main(["run"]) == 2


def test_main_run_com_flags(monkeypatch, capsys):
    _com_reasonix(monkeypatch)
    monkeypatch.setattr(
        reasonix_cli.subprocess, "run",
        lambda args, **kw: _fake_proc(0, "stream ok"),
    )
    assert reasonix_cli.main(["run", "tarefa Y", "--timeout", "60"]) == 0
    assert "stream ok" in capsys.readouterr().out


def test_main_doctor_pass(monkeypatch, capsys):
    _com_reasonix(monkeypatch)
    monkeypatch.setattr(
        reasonix_cli.subprocess, "run",
        lambda args, **kw: _fake_proc(0, "ok\n"),
    )
    assert reasonix_cli.main(["doctor"]) == 0
    assert "pass" in capsys.readouterr().out


def test_main_comando_desconhecido():
    assert reasonix_cli.main(["bogus"]) == 2