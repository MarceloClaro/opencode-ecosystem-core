# -*- coding: utf-8 -*-
"""Testes TDD da integração Kaggle CLI (SPEC-935-R650) — mocks."""

import sys

import pytest

sys.path.insert(0, ".")

from integrations import kaggle_cli  # noqa: E402


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _com_kaggle(monkeypatch):
    import shutil

    def fake_which(cmd, **kw):
        if cmd == "kaggle":
            return "/usr/bin/kaggle"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)


@pytest.fixture(autouse=True)
def _limpa_cache():
    kaggle_cli._BIN_CACHE = None
    yield
    kaggle_cli._BIN_CACHE = None


def test_available(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    assert kaggle_cli.kaggle_available() is False
    _com_kaggle(monkeypatch)
    kaggle_cli._BIN_CACHE = None
    assert kaggle_cli.kaggle_available() is True


def test_version(monkeypatch):
    _com_kaggle(monkeypatch)
    monkeypatch.setattr(
        kaggle_cli.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "Kaggle CLI 2.2.4\n"),
    )
    assert kaggle_cli.kaggle_version() == "2.2.4"


def test_auth_check_formato(monkeypatch):
    r = kaggle_cli.auth_check()
    assert set(r) == {"present", "path", "hint"}
    assert r["path"].endswith("kaggle.json")


def test_run_args_ok_e_timeout(monkeypatch):
    import subprocess as sp
    _com_kaggle(monkeypatch)
    monkeypatch.setattr(
        kaggle_cli.subprocess, "run",
        lambda args, **kw: _FakeProc(0, "lista ok"),
    )
    monkeypatch.setattr(kaggle_cli, "kaggle_version", lambda **k: None)
    r = kaggle_cli.kaggle_run_args(["competitions", "list"])
    assert r["ok"] is True and "kaggle" in r["comando"]

    def boom(*a, **k):
        raise sp.TimeoutExpired(cmd="kaggle", timeout=5)

    monkeypatch.setattr(kaggle_cli.subprocess, "run", boom)
    r2 = kaggle_cli.kaggle_run_args(["x"], timeout=5)
    assert r2["ok"] is False and r2["timeout"] is True


def test_run_args_sem_binario(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    kaggle_cli._BIN_CACHE = None
    assert kaggle_cli.kaggle_run_args(["x"])["ok"] is False


def test_doctor_e_install(monkeypatch):
    _com_kaggle(monkeypatch)
    monkeypatch.setattr(
        kaggle_cli.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "Kaggle CLI 2.2.4\n"),
    )
    assert kaggle_cli.doctor_check()["status"] == "pass"
    assert "pip install kaggle" in kaggle_cli.install_instructions()
    assert "chmod 600" in kaggle_cli.install_instructions()


def test_main(monkeypatch, capsys):
    assert kaggle_cli.main(["--help"]) == 0
    assert kaggle_cli.main(["run"]) == 2
    assert kaggle_cli.main(["bogus"]) == 2
    _com_kaggle(monkeypatch)
    monkeypatch.setattr(
        kaggle_cli.subprocess, "run",
        lambda args, **kw: _FakeProc(0, "ok"),
    )
    monkeypatch.setattr(kaggle_cli, "kaggle_version", lambda **k: None)
    assert kaggle_cli.main(["run", "quota"]) == 0
    assert "ok" in capsys.readouterr().out
