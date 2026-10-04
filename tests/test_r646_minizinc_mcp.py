# -*- coding: utf-8 -*-
"""Testes TDD da ponte MiniZinc MCP (SPEC-935-R646) — mocks, sem rede/binário."""

import json
import sys

import pytest

sys.path.insert(0, ".")

from integrations import minizinc_mcp  # noqa: E402


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


def _deps_map(monkeypatch, mapping):
    import importlib.util

    def fake_find_spec(name, *a, **k):
        return object() if mapping.get(name) else None

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)


def test_minizinc_available(monkeypatch):
    _which_map(monkeypatch, {"minizinc": "/usr/bin/minizinc"})
    assert minizinc_mcp.minizinc_available() is True
    _which_map(monkeypatch, {"minizinc": None})
    assert minizinc_mcp.minizinc_available() is False


def test_minizinc_version(monkeypatch):
    _which_map(monkeypatch, {"minizinc": "/usr/bin/minizinc"})
    monkeypatch.setattr(
        minizinc_mcp.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "MiniZinc 2.8.3\n"),
    )
    assert minizinc_mcp.minizinc_version() == "2.8.3"


def test_minizinc_version_sem_binario_nao_chama(monkeypatch):
    _which_map(monkeypatch, {"minizinc": None})
    chamadas = []
    monkeypatch.setattr(
        minizinc_mcp.subprocess, "run",
        lambda *a, **k: chamadas.append(a) or _FakeProc(0, "x"),
    )
    assert minizinc_mcp.minizinc_version() is None
    assert chamadas == []


def test_deps_status(monkeypatch):
    _deps_map(monkeypatch, {"mcp": True, "pydantic": True, "minizinc": False})
    status = minizinc_mcp.python_deps_status()
    assert status == {"mcp": True, "pydantic": True, "minizinc": False}
    assert minizinc_mcp.mcp_available() is False
    _deps_map(monkeypatch, {"mcp": True, "pydantic": True, "minizinc": True})
    assert minizinc_mcp.mcp_available() is True


def test_payload_valido():
    payload = minizinc_mcp.build_solve_payload(
        "var 1..4: q; solve satisfy;", solver="gecode", timeout=30,
    )
    assert payload["model"].startswith("var 1..4")
    assert payload["solver"] == "gecode"
    assert payload["timeout"] == 30
    assert payload["all_solutions"] is False


def test_payload_com_data_e_all():
    payload = minizinc_mcp.build_solve_payload(
        "solve satisfy;", data={"n": 4}, all_solutions=True,
    )
    assert payload["data"] == {"n": 4}
    assert payload["all_solutions"] is True
    assert "timeout" not in payload


def test_payload_invalido():
    with pytest.raises(ValueError):
        minizinc_mcp.build_solve_payload("   ")
    with pytest.raises(ValueError):
        minizinc_mcp.build_solve_payload("solve satisfy;", data="nao-dict")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        minizinc_mcp.build_solve_payload("solve satisfy;", timeout=-1)


def test_hosted_e_config():
    assert minizinc_mcp.hosted_sse().startswith("https://")
    assert "railway" in minizinc_mcp.hosted_sse()
    cfg = minizinc_mcp.mcp_config()
    assert cfg["type"] == "local" and cfg["enabled"] is True
    assert isinstance(cfg["command"], list)


def test_doctor_full_pass(monkeypatch):
    _which_map(monkeypatch, {"minizinc": "/usr/bin/minizinc"})
    _deps_map(monkeypatch, {"mcp": True, "pydantic": True, "minizinc": True})
    monkeypatch.setattr(
        minizinc_mcp.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "MiniZinc 2.8.3\n"),
    )
    check = minizinc_mcp.doctor_check()
    assert check["status"] == "pass"


def test_doctor_warn_sem_solver(monkeypatch):
    _which_map(monkeypatch, {"minizinc": None})
    _deps_map(monkeypatch, {"mcp": True, "pydantic": True, "minizinc": True})
    check = minizinc_mcp.doctor_check()
    assert check["status"] == "warn"
    assert "minizinc" in check["detail"].lower()


def test_doctor_warn_sem_deps(monkeypatch):
    _which_map(monkeypatch, {"minizinc": None})
    _deps_map(monkeypatch, {"mcp": False, "pydantic": True, "minizinc": False})
    check = minizinc_mcp.doctor_check()
    assert check["status"] == "warn"
    assert "mcp" in check["detail"].lower()


def test_install_contem_modos():
    texto = minizinc_mcp.install_instructions()
    assert "railway" in texto
    assert "pip install -r requirements.txt" in texto
    assert "docker" in texto.lower()
    assert "claude mcp add" in texto


def test_main_status_config_help(monkeypatch, capsys):
    _which_map(monkeypatch, {"minizinc": None})
    _deps_map(monkeypatch, {"mcp": False, "pydantic": False, "minizinc": False})
    assert minizinc_mcp.main(["status"]) == 0
    assert "SPEC-935-R646" in capsys.readouterr().out
    assert minizinc_mcp.main(["config", "--hosted"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "railway" in payload["minizinc-mcp"]["url"]
    assert minizinc_mcp.main(["--help"]) == 0
    assert minizinc_mcp.main(["bogus"]) == 2


def test_main_payload_texto(monkeypatch, capsys):
    assert minizinc_mcp.main(["payload", "--model-text", "solve satisfy;"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["solver"] == "gecode"


def test_main_payload_sem_modelo():
    assert minizinc_mcp.main(["payload"]) == 2


def test_main_solvers_sem_binario(monkeypatch, capsys):
    _which_map(monkeypatch, {"minizinc": None})
    assert minizinc_mcp.main(["solvers"]) == 1
    assert "minizinc" in capsys.readouterr().out.lower()
