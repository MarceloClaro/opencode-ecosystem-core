# -*- coding: utf-8 -*-
"""Testes TDD da ponte Colab MCP Server (SPEC-935-R645) — mocks."""

import json
import sys

import pytest

sys.path.insert(0, ".")

from integrations import colab_mcp  # noqa: E402


def _which_map(monkeypatch, mapping):
    import shutil

    def fake_which(cmd, **kw):
        return mapping.get(cmd)

    monkeypatch.setattr(shutil, "which", fake_which)


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_available_binario(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": "/usr/bin/colab-mcp", "uvx": None})
    assert colab_mcp.mcp_available() is True


def test_available_via_uvx(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": None, "uvx": "/usr/bin/uvx"})
    assert colab_mcp.mcp_available() is True


def test_available_ausente(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": None, "uvx": None})
    assert colab_mcp.mcp_available() is False


def test_version_com_binario(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": "/usr/bin/colab-mcp", "uvx": None})
    monkeypatch.setattr(
        colab_mcp.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "colab-mcp 1.2.0\n"),
    )
    assert colab_mcp.mcp_version() == "1.2.0"


def test_version_sem_binario_nao_chama_rede(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": None, "uvx": "/usr/bin/uvx"})
    chamadas = []
    monkeypatch.setattr(
        colab_mcp.subprocess, "run",
        lambda *a, **k: chamadas.append(a) or _FakeProc(0, "x"),
    )
    assert colab_mcp.mcp_version() is None
    assert chamadas == []


def test_config_prefere_uvx(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": "/usr/bin/colab-mcp", "uvx": "/usr/bin/uvx"})
    cfg = colab_mcp.mcp_config(prefer_uvx=True)
    assert cfg["command"] == ["uvx", "colab-mcp"]
    assert cfg["type"] == "local" and cfg["enabled"] is True


def test_config_binario_local(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": "/usr/bin/colab-mcp", "uvx": None})
    cfg = colab_mcp.mcp_config(prefer_uvx=True)
    assert cfg["command"] == ["/usr/bin/colab-mcp"]


def test_doctor_pass_com_versao(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": "/usr/bin/colab-mcp", "uvx": None})
    monkeypatch.setattr(
        colab_mcp.subprocess, "run",
        lambda *a, **k: _FakeProc(0, "colab-mcp 1.2.0\n"),
    )
    check = colab_mcp.doctor_check()
    assert check["status"] == "pass"
    assert "1.2.0" in check["detail"]


def test_doctor_pass_via_uvx(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": None, "uvx": "/usr/bin/uvx"})
    check = colab_mcp.doctor_check()
    assert check["status"] == "pass"
    assert "uvx" in check["detail"]


def test_doctor_warn_ausente(monkeypatch):
    _which_map(monkeypatch, {"colab-mcp": None, "uvx": None})
    check = colab_mcp.doctor_check()
    assert check["status"] == "warn"


def test_install_contem_uvx(monkeypatch):
    texto = colab_mcp.install_instructions()
    assert "uvx colab-mcp" in texto
    assert "pip install colab-mcp" in texto


def test_main_status_config_help(monkeypatch, capsys):
    _which_map(monkeypatch, {"colab-mcp": None, "uvx": "/usr/bin/uvx"})
    monkeypatch.setattr(colab_mcp, "mcp_version", lambda **k: None)
    assert colab_mcp.main(["status"]) == 0
    assert "SPEC-935-R645" in capsys.readouterr().out
    assert colab_mcp.main(["config"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["colab-mcp"]["command"] == ["uvx", "colab-mcp"]
    assert colab_mcp.main(["--help"]) == 0
    assert colab_mcp.main(["bogus"]) == 2


def test_list_tools_ok(monkeypatch):
    from integrations import colab_mcp as m
    monkeypatch.setattr(
        m, "_run_colab_stdio",
        lambda *a, **k: {"ok": True, "tools": [{"name": "open_colab_browser_connection"}]},
    )
    r = m.list_tools_via_server()
    assert r["ok"] is True and r["tools"][0]["name"] == "open_colab_browser_connection"


def test_materialize_ok(monkeypatch):
    from integrations import colab_mcp as m
    monkeypatch.setattr(
        m, "_run_colab_stdio",
        lambda *a, **k: {"ok": True, "texts": ['{"path": "/tmp/x.ipynb", "cell_count": 1}']},
    )
    r = m.materialize_qcaf('{"nbformat": 4}', filename="x.ipynb", output_dir="/tmp")
    assert r["ok"] is True and r["result"]["cell_count"] == 1


def test_materialize_json_vazio():
    from integrations import colab_mcp as m
    assert m.materialize_qcaf(" ")["ok"] is False


def test_materialize_erro_protocolo(monkeypatch):
    from integrations import colab_mcp as m
    monkeypatch.setattr(m, "_run_colab_stdio", lambda *a, **k: {"ok": False, "error": " Caiu"})
    assert m.materialize_qcaf('{"a": 1}')['ok'] is False


def test_main_list_materialize(monkeypatch, capsys):
    import json as _json
    from integrations import colab_mcp as m
    monkeypatch.setattr(m, "list_tools_via_server", lambda **k: {"ok": True, "tools": []})
    assert m.main(["list"]) == 0
    assert _json.loads(capsys.readouterr().out)["ok"] is True
    assert m.main(["materialize"]) == 2
