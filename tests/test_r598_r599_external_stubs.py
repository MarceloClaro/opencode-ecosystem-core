# -*- coding: utf-8 -*-
"""
Testes de INTEGRAÇÃO reais das integrações Goose (R598) e Plandex (R599).

Executam o pipeline completo de subprocess com binários STUB gerados em
tmp_path (simulam o protocolo das CLIs oficiais) — validam o caminho de
sucesso sem exigir a instalação das CLIs oficiais. As CLIs verdadeiras
continuam sendo opcionais; estes testes não dependem delas.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrations import gemini_cli, goose_cli, plandex_cli, reasonix_cli  # noqa: E402

GOOSE_STUB = """#!/usr/bin/env bash
if [[ "$1" == "--version" ]]; then echo "goose 1.1.0 (stable)"; exit 0; fi
if [[ "$1" == "run" ]]; then
  shift
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --provider) shift ;; --model) shift ;; --text) ;;
      *) echo "[STUB-GOOSE] tarefa: $*"; exit 0 ;;
    esac
    shift
  done
fi
echo "desconhecido: $*"; exit 1
"""

PLANDEX_STUB = """#!/usr/bin/env bash
if [[ "$1" == "--version" ]]; then echo "plandex 2.1.0"; exit 0; fi
case "$1" in
  plans) echo "1  refactor-auth  main  12.3k  4.1k"; exit 0 ;;
  new) echo "[STUB] plano: ${2:-default} ${3:-}"; exit 0 ;;
  tell)
    shift; flags=""; prompt=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --apply|--commit|--skip-menu|--auto-load-context) flags="$flags $1" ;;
        *) prompt="$*"; break ;;
      esac
      shift
    done
    echo "[STUB] tell: ${prompt:-sem-prompt} | flags:$flags"; exit 0 ;;
  chat) shift; echo "[STUB] chat: $*"; exit 0 ;;
  diff) printf '[STUB] diff --plain:\\n--- a/src/x.ts\\n+++ b/src/x.ts\\n+linha nova\\n'; exit 0 ;;
  apply) shift; echo "[STUB] apply ok${1:+ $1}"; exit 0 ;;
  *) echo "desconhecido: $*"; exit 1 ;;
esac
"""


@pytest.fixture()
def stub_path(tmp_path, monkeypatch):
    """Cria os stubs executáveis e os coloca no PATH (subprocess REAL)."""
    goose_bin = tmp_path / "goose_bin"
    plandex_bin = tmp_path / "plandex_bin"
    goose_bin.mkdir()
    plandex_bin.mkdir()
    (goose_bin / "goose").write_text(GOOSE_STUB, encoding="utf-8")
    (plandex_bin / "plandex").write_text(PLANDEX_STUB, encoding="utf-8")
    (goose_bin / "goose").chmod(0o755)
    (plandex_bin / "plandex").chmod(0o755)
    monkeypatch.setenv(
        "PATH",
        f"{goose_bin}:{plandex_bin}:{Path('/usr/bin')}:{Path('/bin')}",
    )
    return tmp_path


# ------------------------------------------------------------------- goose

def test_integracao_goose_version_real(stub_path):
    assert goose_cli.goose_available() is True
    assert goose_cli.goose_version() == "1.1.0"


def test_integracao_goose_run_real(stub_path):
    resultado = goose_cli.goose_run(
        "implemente o modulo X", provider="ollama", model="qwen3:8b"
    )
    assert resultado["ok"] is True
    assert resultado["returncode"] == 0
    assert "implemente o modulo X" in resultado["stdout"]
    assert "--text" in resultado["comando"]
    assert "--provider ollama" in resultado["comando"]
    assert "qwen3:8b" in resultado["comando"]


def test_integracao_goose_doctor_pass(stub_path):
    check = goose_cli.doctor_check()
    assert check["status"] == "pass"
    assert "1.1.0" in check["detail"]


def test_integracao_goose_cli_main_flags(stub_path, capsys):
    code = goose_cli.main(["run", "ajude com X", "--model", "gpt-5.1", "--timeout", "30"])
    captured = capsys.readouterr().out
    assert code == 0
    assert "ajude com X" in captured


# ---------------------------------------------------------------- plandex

def test_integracao_plandex_version_real(stub_path):
    assert plandex_cli.plandex_available() is True
    assert plandex_cli.plandex_version() == "2.1.0"


def test_integracao_plandex_plans_real(stub_path):
    resultado = plandex_cli.plandex_plans()
    assert resultado["ok"] is True
    assert "refactor-auth" in resultado["stdout"]


def test_integracao_plandex_new_tell_diff_apply(stub_path):
    novo = plandex_cli.plandex_new(name="feature-x", auto="semi")
    assert novo["ok"] is True and "feature-x" in novo["comando"] and "--semi" in novo["comando"]

    tell = plandex_cli.plandex_tell("implemente a feature X", apply=True, commit=True)
    assert tell["ok"] is True
    assert "implemente a feature X" in tell["stdout"]
    assert "--apply" in tell["comando"] and "--commit" in tell["comando"]

    diff = plandex_cli.plandex_diff()
    assert diff["ok"] is True and "+linha nova" in diff["stdout"]

    apply = plandex_cli.plandex_apply(commit=True)
    assert apply["ok"] is True and "--commit" in apply["comando"]


def test_integracao_plandex_cli_main_auto(stub_path, capsys):
    code = plandex_cli.main(["new", "feature-z", "--auto", "full"])
    captured = capsys.readouterr().out
    assert code == 0
    assert "feature-z" in captured


def test_integracao_plandex_doctor_pass(stub_path):
    check = plandex_cli.doctor_check()
    assert check["status"] == "pass"
    assert "2.1.0" in check["detail"]

# ------------------------------------------------------------------- gemini (R600)

GEMINI_STUB = """#!/usr/bin/env bash
if [[ "$1" == "--version" ]]; then echo "Gemini CLI v3.5.2 (build 2026)"; exit 0; fi
if [[ "$1" == "-p" ]]; then
  shift
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -m|--model) shift ;; --output-format) shift ;; --timeout) shift ;;
      *) echo "[STUB-GEMINI] resposta para: $*"; exit 0 ;;
    esac
    shift
  done
fi
echo "desconhecido: $*"; exit 1
"""


@pytest.fixture()
def stub_path_gemini(tmp_path, monkeypatch):
    gemini_bin = tmp_path / "gemini_bin"
    gemini_bin.mkdir()
    (gemini_bin / "gemini").write_text(GEMINI_STUB, encoding="utf-8")
    (gemini_bin / "gemini").chmod(0o755)
    monkeypatch.setenv("PATH", f"{gemini_bin}:{Path('/usr/bin')}:{Path('/bin')}")
    gemini_cli._BIN_CACHE = None
    gemini_cli._AVAILABLE_CACHE = None
    return tmp_path


def test_integracao_gemini_version_real(stub_path_gemini):
    assert gemini_cli.gemini_available() is True
    assert gemini_cli.gemini_version() == "3.5.2"


def test_integracao_gemini_run_real(stub_path_gemini):
    resultado = gemini_cli.gemini_run(
        "explique o modulo", model="gemini-2.5-flash", output_format="json"
    )
    assert resultado["ok"] is True
    assert "explique o modulo" in resultado["stdout"]
    assert "-m" in resultado["comando"] and "gemini-2.5-flash" in resultado["comando"]
    assert "--output-format" in resultado["comando"] and "json" in resultado["comando"]


def test_integracao_gemini_doctor_pass(stub_path_gemini):
    check = gemini_cli.doctor_check()
    assert check["status"] == "pass"
    assert "3.5.2" in check["detail"]


def test_integracao_gemini_cli_main(stub_path_gemini, capsys):
    code = gemini_cli.main(["run", "resuma T", "-m", "gemini-3-pro", "--output-format", "json"])
    assert code == 0
    assert "resuma T" in capsys.readouterr().out

# ----------------------------------------------------------------- reasonix (R602)

REASONIX_STUB = """#!/usr/bin/env bash
if [[ "$1" == "--version" ]]; then echo "Reasonix 1.4.2 (go)"; exit 0; fi
if [[ "$1" == "--dir" ]]; then shift; shift; fi
case "$1" in
  run) shift; echo "[STUB-REASONIX] tarefa: $*"; exit 0 ;;
  doctor) echo "[STUB] reasonix doctor: ok"; exit 0 ;;
  *) echo "desconhecido: $*"; exit 1 ;;
esac
"""


@pytest.fixture()
def stub_path_reasonix(tmp_path, monkeypatch):
    reasonix_bin = tmp_path / "reasonix_bin"
    reasonix_bin.mkdir()
    (reasonix_bin / "reasonix").write_text(REASONIX_STUB, encoding="utf-8")
    (reasonix_bin / "reasonix").chmod(0o755)
    monkeypatch.setenv("PATH", f"{reasonix_bin}:{Path('/usr/bin')}:{Path('/bin')}")
    reasonix_cli._BIN_CACHE = None
    reasonix_cli._AVAILABLE_CACHE = None
    return tmp_path


def test_integracao_reasonix_version_real(stub_path_reasonix):
    assert reasonix_cli.reasonix_available() is True
    assert reasonix_cli.reasonix_version() == "1.4.2"


def test_integracao_reasonix_run_real(stub_path_reasonix):
    resultado = reasonix_cli.reasonix_run("implemente os TODOs do main.go")
    assert resultado["ok"] is True
    assert resultado["returncode"] == 0
    assert "implemente os TODOs do main.go" in resultado["stdout"]
    assert resultado["comando"][1] == "run"


def test_integracao_reasonix_run_dir_real(stub_path_reasonix):
    resultado = reasonix_cli.reasonix_run("tarefa", directory="/tmp/work")
    assert resultado["ok"] is True
    assert "--dir" in resultado["comando"] and "/tmp/work" in resultado["comando"]


def test_integracao_reasonix_doctor_pass(stub_path_reasonix):
    check = reasonix_cli.doctor_check()
    assert check["status"] == "pass"
    assert "1.4.2" in check["detail"]


def test_integracao_reasonix_cli_main(stub_path_reasonix, capsys):
    code = reasonix_cli.main(["run", "refatore X", "--timeout", "60"])
    assert code == 0
    assert "refatore X" in capsys.readouterr().out
