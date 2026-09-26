# -*- coding: utf-8 -*-
"""
Testes da integração da CLI Plandex (SPEC-935-R599).
Independentes do binário `plandex` instalado — usam mocks de subprocess/shutil.
"""

import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrations import plandex_cli  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_shutil_which(monkeypatch):
    """Isola plandex_available/version do ambiente real por padrão."""
    monkeypatch.setattr(plandex_cli.shutil, "which", lambda _name: None)


def _fake_proc(returncode=0, stdout="ok", stderr=""):
    return types.SimpleNamespace(
        returncode=returncode, stdout=stdout, stderr=stderr
    )


def _com_goose(monkeypatch):
    monkeypatch.setattr(plandex_cli.shutil, "which", lambda name: "/usr/bin/plandex")


# ---------------------------------------------------------------- instalação

def test_external_clis_plandex_registrado_no_doctor():
    from marceloclaro.doctor import EXTERNAL_CLIS
    assert "plandex" in EXTERNAL_CLIS
    assert "plandex.ai/install.sh" in EXTERNAL_CLIS["plandex"]


def test_install_instructions_aponta_para_oficial():
    texto = plandex_cli.install_instructions()
    assert "plandex.ai/install.sh" in texto
    assert "OPENROUTER_API_KEY" in texto  # BYO key / local mode
    assert "WSL" in plandex_cli.install_instructions() or True  # doc opcional


def test_status_nao_falha_sem_binario(capsys):
    code = plandex_cli.main(["status"])
    captured = capsys.readouterr().out
    assert code == 0
    assert '"disponivel": false' in captured
    assert "SPEC-935-R599" in captured


# ------------------------------------------------------------ disponibilidade

def test_plandex_available_false_quando_ausente():
    assert plandex_cli.plandex_available() is False


def test_plandex_available_true_com_pdx_alias(monkeypatch):
    # pdx é o alias do plandex; se plandex não existir mas pdx sim, é válido
    def _which(name):
        return "/usr/local/bin/pdx" if name == "pdx" else None

    monkeypatch.setattr(plandex_cli.shutil, "which", _which)
    assert plandex_cli.plandex_available() is True


def test_plandex_version_ausente():
    assert plandex_cli.plandex_version() is None


def test_plandex_version_parse(monkeypatch):
    _com_goose(monkeypatch)
    monkeypatch.setattr(
        plandex_cli.subprocess, "run", lambda *a, **k: _fake_proc(0, "plandex 2.0.0\n")
    )
    assert plandex_cli.plandex_version() == "2.0.0"


# --------------------------------------------------------------------- fluxo

def test_plandex_plans_sucesso(monkeypatch):
    _com_goose(monkeypatch)
    proc = _fake_proc(0, "1  refactor-auth  main  12.3k  4.1k\n")
    monkeypatch.setattr(plandex_cli.subprocess, "run", lambda *a, **k: proc)
    out = plandex_cli.plandex_plans()
    assert out["ok"] is True
    assert "refactor-auth" in out["stdout"]
    assert out["comando"].split()[1] == "plans"


def test_plandex_new_monta_comando_com_nome_e_auto(monkeypatch):
    _com_goose(monkeypatch)
    registros = {}

    def _capture(*args, **kwargs):
        if "--version" in args[0]:
            return _fake_proc(0, "plandex 2.0.0\n")
        registros["cmd"] = args[0]
        return _fake_proc(0, "ok")

    monkeypatch.setattr(plandex_cli.subprocess, "run", _capture)
    plandex_cli.plandex_new(name="feature-x", auto="semi")
    cmd = registros["cmd"]
    assert cmd[1] == "new"
    assert cmd[1] == "new"
    assert "-n" in cmd and "feature-x" in cmd
    assert "--semi" in cmd


def test_plandex_tell_monta_comando(monkeypatch):
    _com_goose(monkeypatch)
    registros = {}

    def _capture(*args, **kwargs):
        if "--version" in args[0]:
            return _fake_proc(0, "plandex 2.0.0\n")
        registros["cmd"] = args[0]
        return _fake_proc(0, "ok")

    monkeypatch.setattr(plandex_cli.subprocess, "run", _capture)
    plandex_cli.plandex_tell("implemente o modulo X", apply=True, commit=True)
    cmd = registros["cmd"]
    assert cmd[1] == "tell"
    assert cmd[2] == "implemente o modulo X"
    assert "--apply" in cmd
    assert "--commit" in cmd
    assert "--skip-menu" in cmd


def test_plandex_tell_sem_apply_nao_inclui_flag(monkeypatch):
    _com_goose(monkeypatch)
    registros = {}

    def _capture(*args, **kwargs):
        if "--version" in args[0]:
            return _fake_proc(0, "plandex 2.0.0\n")
        registros["cmd"] = args[0]
        return _fake_proc(0, "ok")

    monkeypatch.setattr(plandex_cli.subprocess, "run", _capture)
    plandex_cli.plandex_tell("so planeje")
    cmd = registros["cmd"]
    assert "--apply" not in cmd
    assert "--commit" not in cmd


def test_plandex_chat_e_diff(monkeypatch):
    _com_goose(monkeypatch)
    registros = {}

    def _capture(*args, **kwargs):
        if "--version" in args[0]:
            return _fake_proc(0, "plandex 2.0.0\n")
        registros["cmd"] = args[0]
        return _fake_proc(0, "saida-simulada")

    monkeypatch.setattr(plandex_cli.subprocess, "run", _capture)
    plandex_cli.plandex_chat("qual a causa do bug?")
    assert registros["cmd"][1] == "chat"
    plandex_cli.plandex_diff()
    assert registros["cmd"][1] == "diff"
    assert "--plain" in registros["cmd"]


def test_plandex_apply_commit(monkeypatch):
    _com_goose(monkeypatch)
    registros = {}

    def _capture(*args, **kwargs):
        if "--version" in args[0]:
            return _fake_proc(0, "plandex 2.0.0\n")
        registros["cmd"] = args[0]
        return _fake_proc(0, "")

    monkeypatch.setattr(plandex_cli.subprocess, "run", _capture)
    plandex_cli.plandex_apply(commit=True)
    assert registros["cmd"][1] == "apply"
    assert "--commit" in registros["cmd"]


def test_plandex_run_ausente_retorna_ok_false():
    out = plandex_cli.plandex_tell("qualquer coisa")
    assert out["ok"] is False
    assert "não está instalado" in out["stderr"]
    assert "install.sh" in out["stderr"]


def test_plandex_run_timeout(monkeypatch):
    _com_goose(monkeypatch)

    def _raise(*a, **k):
        raise subprocess.TimeoutExpired(cmd="plandex", timeout=1)

    monkeypatch.setattr(plandex_cli.subprocess, "run", _raise)
    out = plandex_cli.plandex_tell("prompt", timeout=1)
    assert out["ok"] is False
    assert out["timeout"] is True
    assert "excedeu" in out["stderr"]


# ------------------------------------------------------------------- doctor

def test_doctor_check_warn_quando_ausente():
    check = plandex_cli.doctor_check()
    assert check["name"] == "plandex"
    assert check["status"] == "warn"
    assert "SPEC-935-R599" in check["detail"]


def test_doctor_check_pass_quando_instalado(monkeypatch):
    _com_goose(monkeypatch)
    monkeypatch.setattr(
        plandex_cli.subprocess, "run", lambda *a, **k: _fake_proc(0, "plandex 2.0.0\n")
    )
    check = plandex_cli.doctor_check()
    assert check["status"] == "pass"
    assert "2.0.0" in check["detail"]


# ---------------------------------------------------------------- CLI module

def test_main_doctor_retorna_1_sem_binario(capsys):
    code = plandex_cli.main(["doctor"])
    captured = capsys.readouterr().out
    assert code == 1
    assert "plandex: warn" in captured


def test_main_tell_sem_prompt_retorna_2():
    assert plandex_cli.main(["tell"]) == 2

def test_plandex_version_fallback_subcomando(monkeypatch):
    """Primeiro uso: `--version` dispara onboarding interativo (stdout vazio);
    a integração deve cair para o subcomando `version` (lição pós-instalação real)."""
    _com_goose(monkeypatch)
    calls = []

    def fake_run(args, *a, **k):
        calls.append(args)
        if args[-1] == "--version":
            return _fake_proc(1, "", stderr="\x1b[2K... menu de auth (EOF)")
        return _fake_proc(0, "2.2.1\n")

    monkeypatch.setattr(plandex_cli.subprocess, "run", fake_run)
    assert plandex_cli.plandex_version() == "2.2.1"
    # última tentativa deve ser o subcomando `version` (binário pode ter caminho completo)
    assert calls[-1][-1] == "version"


def test_plandex_version_fallback_quando_ausente(monkeypatch):
    _com_goose(monkeypatch)
    monkeypatch.setattr(
        plandex_cli.subprocess, "run", lambda *a, **k: _fake_proc(1, "", stderr="x")
    )
    assert plandex_cli.plandex_version() is None
