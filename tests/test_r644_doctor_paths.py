"""SPEC-935-R644: diagnóstico de instalações fora do PATH da sessão."""

import os
import sys
from pathlib import Path

import pytest

from marceloclaro import doctor


@pytest.fixture(autouse=True)
def isolated_installations(monkeypatch, tmp_path):
    """O diagnóstico não pode depender das CLIs instaladas pelo operador."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(sys, "executable", str(tmp_path / "venv" / "bin" / "python"))
    monkeypatch.setattr(doctor.shutil, "which", lambda name: None)
    for name in doctor.EXTERNAL_CLIS:
        key = "ANTIGRAVITY_BIN" if name == "agy" else f"{name.upper()}_BIN"
        monkeypatch.delenv(key, raising=False)
    return home


def executable(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)
    return path


@pytest.mark.parametrize("folder", [".local/bin", ".npm-global/bin", ".opencode/bin"])
def test_resolves_known_user_paths(isolated_installations, folder):
    cli = executable(isolated_installations / folder / "claude")
    assert doctor._resolve_external_cli("claude") == str(cli)


def test_resolves_running_python_environment(tmp_path):
    cli = executable(tmp_path / "venv" / "bin" / "nlm")
    assert doctor._resolve_external_cli("nlm") == str(cli)


@pytest.mark.skipif(os.name == "nt", reason="Permissão de execução POSIX.")
def test_running_python_environment_requires_execute_permission(tmp_path):
    cli = tmp_path / "venv" / "bin" / "nlm"
    cli.parent.mkdir(parents=True)
    cli.write_text("configuration only", encoding="utf-8")
    cli.chmod(0o644)
    assert doctor._resolve_external_cli("nlm") is None


def test_absent_installation_returns_none():
    assert doctor._resolve_external_cli("claude") is None


@pytest.mark.skipif(os.name == "nt", reason="Permissão de execução POSIX.")
@pytest.mark.parametrize("location", [".local/bin", ".npm-global/bin", ".opencode/bin"])
def test_configuration_file_without_execute_permission_is_not_cli(isolated_installations, location):
    path = isolated_installations / location / "claude"
    path.parent.mkdir(parents=True)
    path.write_text('{"installed": true}', encoding="utf-8")
    path.chmod(0o644)
    assert doctor._resolve_external_cli("claude") is None


def test_directory_is_not_cli(isolated_installations):
    (isolated_installations / ".local" / "bin" / "claude").mkdir(parents=True)
    assert doctor._resolve_external_cli("claude") is None


def test_path_resolution_keeps_which_contract(monkeypatch, isolated_installations):
    executable(isolated_installations / ".local" / "bin" / "claude")
    monkeypatch.setattr(doctor.shutil, "which", lambda name: f"/selected/{name}")
    assert doctor._resolve_external_cli("claude") == "/selected/claude"


def test_explicit_override_takes_precedence(monkeypatch, isolated_installations, tmp_path):
    executable(isolated_installations / ".local" / "bin" / "claude")
    cli = executable(tmp_path / "custom install" / "claude")
    monkeypatch.setenv("CLAUDE_BIN", str(cli))
    assert doctor._resolve_external_cli("claude") == str(cli)


def test_invalid_override_does_not_fall_back(monkeypatch, isolated_installations, tmp_path):
    executable(isolated_installations / ".local" / "bin" / "claude")
    executable(tmp_path / "venv" / "bin" / "claude")
    monkeypatch.setenv("CLAUDE_BIN", str(tmp_path / "missing"))
    assert doctor._resolve_external_cli("claude") is None


def test_doctor_finds_external_clis_without_login_shell(monkeypatch, isolated_installations):
    monkeypatch.setattr(doctor, "EXTERNAL_CLIS", {"opencode": "install", "agy": "install", "claude": "install"})
    for name, location in [("opencode", ".opencode/bin"), ("agy", ".local/bin"), ("claude", ".npm-global/bin")]:
        executable(isolated_installations / location / name)
    check = doctor._check_external_clis()
    assert check.status == "pass"
    assert "3 CLIs" in check.detail
    assert "autenticação" in check.detail.lower()
    assert "não verificadas" in check.detail


def test_doctor_reports_missing_optional_cli_as_warning(monkeypatch):
    monkeypatch.setattr(doctor, "EXTERNAL_CLIS", {"claude": "install-command"})
    check = doctor._check_external_clis()
    assert check.status == "warn"
    assert "1/1" in check.detail
    assert "claude -> install-command" in check.detail


def test_installation_check_never_invokes_model(monkeypatch, isolated_installations):
    import subprocess

    monkeypatch.setattr(doctor, "EXTERNAL_CLIS", {"claude": "install-command"})
    executable(isolated_installations / ".local" / "bin" / "claude")

    def forbidden(*args, **kwargs):
        raise AssertionError("O inventário não deve executar a CLI.")

    monkeypatch.setattr(subprocess, "run", forbidden)
    assert doctor._check_external_clis().status == "pass"
