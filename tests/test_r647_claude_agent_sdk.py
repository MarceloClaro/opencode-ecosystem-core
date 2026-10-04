# -*- coding: utf-8 -*-
"""Testes TDD da ponte Claude Agent SDK (SPEC-935-R647) — mocks, sem rede."""

import json
import sys

import pytest

sys.path.insert(0, ".")

from integrations import claude_agent_sdk as sdk  # noqa: E402


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _which_map(monkeypatch, mapping):
    import shutil

    def fake_which(cmd, **kw):
        return mapping.get(cmd)

    monkeypatch.setattr(shutil, "which", fake_which)


def _dep(monkeypatch, present):
    import importlib.util

    monkeypatch.setattr(
        importlib.util, "find_spec",
        lambda *a, **k: object() if present else None,
    )


def test_claude_available(monkeypatch):
    _which_map(monkeypatch, {"claude": "/usr/bin/claude"})
    assert sdk.claude_available() is True
    _which_map(monkeypatch, {"claude": None})
    assert sdk.claude_available() is False


def test_cli_version(monkeypatch):
    _which_map(monkeypatch, {"claude": "/usr/bin/claude"})
    monkeypatch.setattr(
        sdk.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "2.1.257 (Claude Code)\n"),
    )
    assert sdk.cli_version() == "2.1.257"


def test_cli_version_sem_binario_nao_chama(monkeypatch):
    _which_map(monkeypatch, {"claude": None})
    chamadas = []
    monkeypatch.setattr(
        sdk.subprocess, "run",
        lambda *a, **k: chamadas.append(a) or _FakeProc(0, "x"),
    )
    assert sdk.cli_version() is None
    assert chamadas == []


def test_dep_status(monkeypatch):
    _dep(monkeypatch, True)
    assert sdk.sdk_dep_status() is True
    assert sdk.sdk_available() is True
    _dep(monkeypatch, False)
    assert sdk.sdk_available() is False


def test_options_validas():
    opts = sdk.build_query_options(
        "Explique o arquivo", system_prompt="Seja breve",
        allowed_tools=["Read"], max_turns=1, cwd="/tmp",
        permission_mode="acceptEdits",
    )
    assert opts["prompt"] == "Explique o arquivo"
    assert opts["allowed_tools"] == ["Read"]
    assert opts["max_turns"] == 1
    assert "disallowed_tools" not in opts


def test_options_invalidas():
    with pytest.raises(ValueError):
        sdk.build_query_options("   ")
    with pytest.raises(ValueError):
        sdk.build_query_options("ok", max_turns=0)


def test_doctor_pass(monkeypatch):
    _which_map(monkeypatch, {"claude": "/usr/bin/claude"})
    _dep(monkeypatch, True)
    monkeypatch.setattr(
        sdk.subprocess, "run", lambda *a, **k: _FakeProc(0, "2.1.257\n"),
    )
    check = sdk.doctor_check()
    assert check["status"] == "pass"


def test_doctor_warn_sem_dep(monkeypatch):
    _which_map(monkeypatch, {"claude": "/usr/bin/claude"})
    _dep(monkeypatch, False)
    check = sdk.doctor_check()
    assert check["status"] == "warn"
    assert "claude-agent-sdk" in check["detail"]


def test_doctor_warn_sem_cli(monkeypatch):
    _which_map(monkeypatch, {"claude": None})
    _dep(monkeypatch, True)
    check = sdk.doctor_check()
    assert check["status"] == "warn"
    assert "claude" in check["detail"].lower()


def test_install_contem_pip_e_termos():
    texto = sdk.install_instructions()
    assert "pip install claude-agent-sdk" in texto
    assert "commercial-terms" in texto
    assert "disallowed_tools" in texto


def test_main_status_options_help(monkeypatch, capsys):
    _which_map(monkeypatch, {"claude": None})
    _dep(monkeypatch, False)
    assert sdk.main(["status"]) == 0
    assert "SPEC-935-R647" in capsys.readouterr().out
    assert sdk.main(["options", "--prompt", "oi", "--max-turns", "2"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["max_turns"] == 2
    assert sdk.main(["options"]) == 2
    assert sdk.main(["--help"]) == 0
    assert sdk.main(["bogus"]) == 2
