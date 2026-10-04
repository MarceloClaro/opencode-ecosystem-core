# -*- coding: utf-8 -*-
"""Testes TDD do runner Antigravity CLI (SPEC-935-R651) — mocks."""

import sys

import pytest

sys.path.insert(0, ".")

from integrations import antigravity_cli as agy  # noqa: E402


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _com_agy(monkeypatch):
    import shutil

    def fake_which(cmd, **kw):
        if cmd == "agy":
            return "/usr/bin/agy"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)


@pytest.fixture(autouse=True)
def _limpa_cache():
    agy._BIN_CACHE = None
    yield
    agy._BIN_CACHE = None


def test_available_e_version(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert agy.agy_available() is False
    assert agy.agy_version() is None
    _com_agy(monkeypatch)
    assert agy.agy_available() is True
    monkeypatch.setattr(
        agy.subprocess, "run", lambda *a, **k: _FakeProc(0, "1.2.16\n"),
    )
    assert agy.agy_version() == "1.2.16"


def test_run_forma_canonica(monkeypatch):
    _com_agy(monkeypatch)
    chamadas = {}

    def fake_run(args, **kw):
        chamadas["args"] = args
        chamadas["stdin"] = kw.get("stdin")
        return _FakeProc(0, "resposta do agy")

    monkeypatch.setattr(agy.subprocess, "run", fake_run)
    monkeypatch.setattr(agy, "agy_version", lambda **k: None)
    r = agy.agy_run("explique", agent="code", output_format="json")
    assert r["ok"] is True
    args = chamadas["args"]
    assert args[:6] == [args[0], "--agent", "code", "--print", "explique", "--output-format"]
    assert args[6] == "json"
    assert chamadas["stdin"] is not None  # DEVNULL, nunca TTY


def test_run_falha_silenciosa(monkeypatch):
    _com_agy(monkeypatch)
    monkeypatch.setattr(
        agy.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "CLI error: algo quebrou"),
    )
    monkeypatch.setattr(agy, "agy_version", lambda **k: None)
    r = agy.agy_run("x")
    assert r["ok"] is False  # rc 0 mas stdout de erro


def test_run_prompt_vazio_e_timeout(monkeypatch):
    import subprocess as sp
    _com_agy(monkeypatch)
    assert agy.agy_run("   ")["ok"] is False

    def boom(*a, **k):
        raise sp.TimeoutExpired(cmd="agy", timeout=5)

    monkeypatch.setattr(agy.subprocess, "run", boom)
    monkeypatch.setattr(agy, "agy_version", lambda **k: None)
    r = agy.agy_run("x", timeout=5)
    assert r["ok"] is False and r["timeout"] is True


def test_doctor_install_main(monkeypatch, capsys):
    _com_agy(monkeypatch)
    monkeypatch.setattr(
        agy.subprocess, "run", lambda *a, **k: _FakeProc(0, "1.2.16\n"),
    )
    assert agy.doctor_check()["status"] == "pass"
    assert "antigravity.google" in agy.install_instructions()
    assert agy.main(["--help"]) == 0
    assert agy.main(["run"]) == 2
    assert agy.main(["bogus"]) == 2
    monkeypatch.setattr(
        agy.subprocess, "run", lambda args, **kw: _FakeProc(0, "ok agy"),
    )
    monkeypatch.setattr(agy, "agy_version", lambda **k: None)
    assert agy.main(["run", "tarefa", "--agent", "dev"]) == 0
    assert "ok agy" in capsys.readouterr().out
