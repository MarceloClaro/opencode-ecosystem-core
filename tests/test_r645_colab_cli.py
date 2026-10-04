# -*- coding: utf-8 -*-
"""Testes TDD da integração Colab CLI (SPEC-935-R645) — mocks."""

import sys
from types import SimpleNamespace  # noqa: F401

import pytest

sys.path.insert(0, ".")

from integrations import colab_cli  # noqa: E402


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_proc(code, stdout="", stderr=""):
    return _FakeProc(code, stdout, stderr)


def _com_colab(monkeypatch):
    import shutil

    def fake_which(cmd, **kw):
        if cmd == "colab":
            return "/usr/bin/colab"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)


@pytest.fixture(autouse=True)
def _limpa_cache():
    colab_cli._BIN_CACHE = None
    colab_cli._AVAILABLE_CACHE = None
    yield
    colab_cli._BIN_CACHE = None
    colab_cli._AVAILABLE_CACHE = None


def test_available_sem_binario(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert colab_cli._find_binary() is None
    assert colab_cli.colab_available() is False


def test_available_com_binario(monkeypatch):
    _com_colab(monkeypatch)
    assert colab_cli.colab_available() is True


def test_version_com_rotulo(monkeypatch):
    _com_colab(monkeypatch)
    monkeypatch.setattr(
        colab_cli.subprocess, "run",
        lambda *a, **k: _fake_proc(0, "colab, version 0.3.1\n"),
    )
    assert colab_cli.colab_version() == "0.3.1"


def test_version_sem_binario(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert colab_cli.colab_version() is None


def test_run_args_monta_comando(monkeypatch):
    _com_colab(monkeypatch)
    calls = {}

    def fake_run(args, **kw):
        calls["args"] = args
        calls["input"] = kw.get("input")
        return _fake_proc(0, "ok sessions\n")

    monkeypatch.setattr(colab_cli.subprocess, "run", fake_run)
    # evita segunda chamada de version() dentro do runner
    monkeypatch.setattr(colab_cli, "colab_version", lambda: "0.3.1")
    resultado = colab_cli.colab_run_args(["sessions"])
    assert resultado["ok"] is True
    assert resultado["returncode"] == 0
    assert calls["args"][0].endswith("colab")
    assert "sessions" in calls["args"]
    assert resultado["stdout"] == "ok sessions\n"
    assert resultado["timeout"] is False


def test_run_args_com_stdin(monkeypatch):
    _com_colab(monkeypatch)
    calls = {}

    def fake_run(args, **kw):
        calls["input"] = kw.get("input")
        return _fake_proc(0, "1\n")

    monkeypatch.setattr(colab_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(colab_cli, "colab_version", lambda: None)
    resultado = colab_cli.colab_run_args(["exec"], stdin_text='print(1)')
    assert resultado["ok"] is True
    assert calls["input"] == 'print(1)'


def test_run_args_erro_nao_lanca(monkeypatch):
    _com_colab(monkeypatch)

    def boom(*a, **k):
        raise FileNotFoundError("colab ausente")

    monkeypatch.setattr(colab_cli.subprocess, "run", boom)
    resultado = colab_cli.colab_run_args(["sessions"])
    assert resultado["ok"] is False
    assert resultado["returncode"] is None
    assert "colab ausente" in resultado["stderr"]


def test_run_args_timeout(monkeypatch):
    import subprocess as sp

    _com_colab(monkeypatch)

    def boom(*a, **k):
        raise sp.TimeoutExpired(cmd="colab", timeout=5)

    monkeypatch.setattr(colab_cli.subprocess, "run", boom)
    monkeypatch.setattr(colab_cli, "colab_version", lambda: None)
    resultado = colab_cli.colab_run_args(["sessions"], timeout=5)
    assert resultado["ok"] is False
    assert resultado["timeout"] is True


def test_run_args_sem_binario(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    resultado = colab_cli.colab_run_args(["sessions"])
    assert resultado["ok"] is False
    assert "não instalado" in resultado["stderr"].lower()


def test_new_monta_args(monkeypatch):
    _com_colab(monkeypatch)
    calls = {}

    def fake_run(args, **kw):
        calls["args"] = args
        return _fake_proc(0, "ok")

    monkeypatch.setattr(colab_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(colab_cli, "colab_version", lambda: None)
    r = colab_cli.colab_new("trainer", gpu="A100", high_mem=True)
    assert r["ok"] is True
    assert calls["args"][:2] == [calls["args"][0], "new"]
    assert "-s" in calls["args"] and "trainer" in calls["args"]
    assert "--gpu" in calls["args"] and "A100" in calls["args"]
    assert "--high-mem" in calls["args"]


def test_exec_monta_args(monkeypatch):
    _com_colab(monkeypatch)
    calls = {}

    def fake_run(args, **kw):
        calls["args"] = args
        return _fake_proc(0, "ok")

    monkeypatch.setattr(colab_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(colab_cli, "colab_version", lambda: None)
    r = colab_cli.colab_exec(session="a", file="t.py")
    assert r["ok"] is True
    assert "exec" in calls["args"] and "-f" in calls["args"] and "t.py" in calls["args"]


def test_run_script_monta_args(monkeypatch):
    _com_colab(monkeypatch)
    calls = {}

    def fake_run(args, **kw):
        calls["args"] = args
        return _fake_proc(0, "ok")

    monkeypatch.setattr(colab_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(colab_cli, "colab_version", lambda: None)
    r = colab_cli.colab_run_script("train.py", script_args=["--epochs", "2"],
                                   gpu="T4", keep=True)
    assert r["ok"] is True
    assert "run" in calls["args"] and "train.py" in calls["args"]
    assert "--gpu" in calls["args"] and "--keep" in calls["args"]


def test_stop_e_sessions(monkeypatch):
    _com_colab(monkeypatch)
    calls = []

    def fake_run(args, **kw):
        calls.append(args)
        return _fake_proc(0, "ok")

    monkeypatch.setattr(colab_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(colab_cli, "colab_version", lambda: None)
    assert colab_cli.colab_stop("x")["ok"] is True
    assert colab_cli.colab_sessions()["ok"] is True
    assert calls[0][1] == "stop" and calls[1][1] == "sessions"


def test_doctor_pass_e_warn(monkeypatch):
    _com_colab(monkeypatch)
    monkeypatch.setattr(colab_cli.subprocess, "run",
                        lambda *a, **k: _fake_proc(0, "colab, version 0.3.1\n"))
    check = colab_cli.doctor_check()
    assert check["status"] == "pass"
    assert "0.3.1" in check["detail"]

    import shutil
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    colab_cli._BIN_CACHE = None
    colab_cli._AVAILABLE_CACHE = None
    check2 = colab_cli.doctor_check()
    assert check2["status"] == "warn"


def test_install_contem_uv(monkeypatch):
    texto = colab_cli.install_instructions()
    assert "uv tool install google-colab-cli" in texto
    assert "pip install google-colab-cli" in texto
    assert "Linux" in texto


def test_main_help_status_e_erros(monkeypatch, capsys):
    assert colab_cli.main(["--help"]) == 0
    _com_colab(monkeypatch)
    monkeypatch.setattr(colab_cli.subprocess, "run",
                        lambda *a, **k: _fake_proc(0, "colab, version 0.3.1\n"))
    assert colab_cli.main(["status"]) == 0
    assert "colab" in capsys.readouterr().out.lower()
    assert colab_cli.main(["run"]) == 2
    assert colab_cli.main(["bogus"]) == 2


def test_main_run_passthrough(monkeypatch, capsys):
    _com_colab(monkeypatch)
    monkeypatch.setattr(colab_cli.subprocess, "run",
                        lambda args, **kw: _fake_proc(0, "sessao ok"))
    monkeypatch.setattr(colab_cli, "colab_version", lambda: None)
    assert colab_cli.main(["run", "sessions"]) == 0
    assert "sessao ok" in capsys.readouterr().out
