# -*- coding: utf-8 -*-
"""
Testes da integração da CLI Goose (SPEC-935-R598).
Independentes do binário `goose` instalado — usam mocks de subprocess/shutil.
"""

import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrations import goose_cli  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_shutil_which(monkeypatch):
    """Isola goose_available/goose_version do ambiente real por padrão."""
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: None)


# ---------------------------------------------------------------- instalação

def test_external_clis_goose_registrado_no_doctor():
    from marceloclaro.doctor import EXTERNAL_CLIS
    assert "goose" in EXTERNAL_CLIS
    assert "aaif-goose/goose" in EXTERNAL_CLIS["goose"]
    assert EXTERNAL_CLIS["goose"].startswith("curl -fsSL")


def test_install_instructions_aponta_para_oficial():
    texto = goose_cli.install_instructions()
    assert "aaif-goose/goose/releases/download/stable/download_cli.sh" in texto
    assert "goose-docs.ai" in texto
    assert "Apache-2.0" not in goose_cli.GOOSE_INSTALL_CMD  # só instrução limpa
    assert "Ollama" in texto  # cita 15+ providers de exemplo


# ------------------------------------------------------------ disponibilidade

def test_goose_available_false_quando_ausente(monkeypatch):
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: None)
    assert goose_cli.goose_available() is False


def test_goose_available_true_quando_presente(monkeypatch):
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: "/usr/bin/goose")
    assert goose_cli.goose_available() is True


# ------------------------------------------------------------------- versão

def test_goose_version_ausente():
    assert goose_cli.goose_version() is None


def test_goose_version_parse(monkeypatch):
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: "/usr/bin/goose")

    class FakeProc:
        returncode = 0
        stdout = "goose 1.1.0 (stable)\n"

    monkeypatch.setattr(goose_cli.subprocess, "run", lambda *a, **k: FakeProc())
    assert goose_cli.goose_version() == "1.1.0"


# ---------------------------------------------------------------------- run

def _fake_proc(returncode=0, stdout="ok", stderr=""):
    return types.SimpleNamespace(
        returncode=returncode, stdout=stdout, stderr=stderr
    )


def test_goose_run_sucesso(monkeypatch):
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: "/usr/bin/goose")
    proc = _fake_proc(0, "Preparando minuta...\nConcluído.")
    monkeypatch.setattr(goose_cli.subprocess, "run", lambda *a, **k: proc)

    out = goose_cli.goose_run("revise este texto")
    assert out["ok"] is True
    assert out["returncode"] == 0
    assert "Preparando minuta" in out["stdout"]
    assert out["timeout"] is False


def test_goose_run_falha(monkeypatch):
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: "/usr/bin/goose")
    proc = _fake_proc(1, "", "erro de provider")
    monkeypatch.setattr(goose_cli.subprocess, "run", lambda *a, **k: proc)

    out = goose_cli.goose_run("prompt")
    assert out["ok"] is False
    assert out["returncode"] == 1
    assert "erro de provider" in out["stderr"]


def test_goose_run_ausente_retorna_ok_false():
    out = goose_cli.goose_run("prompt qualquer")
    assert out["ok"] is False
    assert out["returncode"] is None
    assert "não está instalado" in out["stderr"]
    assert "download_cli.sh" in out["stderr"]


def test_goose_run_timeout(monkeypatch):
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: "/usr/bin/goose")

    def _raise(*a, **k):
        raise subprocess.TimeoutExpired(cmd="goose", timeout=1)

    monkeypatch.setattr(goose_cli.subprocess, "run", _raise)
    out = goose_cli.goose_run("prompt", timeout=1)
    assert out["ok"] is False
    assert out["timeout"] is True
    assert "excedeu" in out["stderr"]


def test_goose_run_monta_comando_text_headless(monkeypatch):
    registros = {}

    def _capture(*args, **kwargs):
        # ignora a chamada interna de goose_version (--version)
        if args[0][1:] == ["--version"]:
            return _fake_proc(0, "goose 1.1.0\n")
        registros["cmd"] = args[0]
        return _fake_proc(0, "ok")

    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: "/usr/bin/goose")
    monkeypatch.setattr(goose_cli.subprocess, "run", _capture)

    goose_cli.goose_run("gere um relatório", provider="ollama", model="qwen3:8b")
    cmd = registros["cmd"]
    assert cmd[0] == "goose"
    assert cmd[1] == "run" and cmd[2] == "--text"
    assert "--provider" in cmd and "ollama" in cmd
    assert "--model" in cmd and "qwen3:8b" in cmd
    assert cmd[-1] == "gere um relatório"


# ------------------------------------------------------------------- doctor

def test_doctor_check_warn_quando_ausente():
    check = goose_cli.doctor_check()
    assert check["name"] == "goose"
    assert check["status"] == "warn"
    assert "SPEC-935-R598" in check["detail"]


def test_doctor_check_pass_quando_instalado(monkeypatch):
    monkeypatch.setattr(goose_cli.shutil, "which", lambda _name: "/usr/bin/goose")

    class FakeProc:
        returncode = 0
        stdout = "goose 1.1.0\n"

    monkeypatch.setattr(goose_cli.subprocess, "run", lambda *a, **k: FakeProc())
    check = goose_cli.doctor_check()
    assert check["status"] == "pass"
    assert "1.1.0" in check["detail"]


# ---------------------------------------------------------------- CLI module

def test_main_status_nao_falha_sem_goose(capsys):
    code = goose_cli.main(["status"])
    captured = capsys.readouterr().out
    assert code == 0
    assert '"disponivel": false' in captured
    assert "SPEC-935-R598" in captured


def test_main_doctor_retorna_1_sem_goose(capsys):
    code = goose_cli.main(["doctor"])
    captured = capsys.readouterr().out
    assert code == 1
    assert "goose: warn" in captured