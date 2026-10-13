"""Orientação que continua útil quando o instalador npm está indisponível."""

from integrations import runai
from marceloclaro import doctor
import pytest


def test_missing_cli_explains_source_installation(monkeypatch):
    monkeypatch.setattr(runai.shutil, "which", lambda _: None)
    bridge = runai.RunAIProvisioner(source_dir="")
    result = bridge.doctor()
    assert result["exit_code"] == 127
    assert "curl" not in result["stderr"]
    assert runai.SOURCE_REPOSITORY_URL in result["stderr"]
    assert "pnpm packages:build" in result["stderr"]
    assert "RUNAI_SOURCE_DIR" in result["stderr"]


def test_inventory_install_hint_matches_bridge():
    assert doctor.EXTERNAL_CLIS["runai"] == runai.INSTALLATION_HINT


def test_live_missing_cli_does_not_recommend_unavailable_installer(monkeypatch):
    monkeypatch.setattr(runai.runai_provisioner, "is_available", lambda: False)
    monkeypatch.setattr(runai.runai_provisioner, "installer_diagnosis", lambda: {"status_code": 503})
    result = doctor._check_runai(live=True)
    assert result.status == "warn"
    assert "curl" not in result.detail
    assert "RUNAI_SOURCE_DIR" in result.detail


def test_structural_missing_cli_never_queries_package(monkeypatch):
    monkeypatch.setattr(runai.runai_provisioner, "is_available", lambda: False)
    def forbidden():
        raise AssertionError("diagnóstico estrutural tentou acessar a rede")
    monkeypatch.setattr(runai.runai_provisioner, "installer_diagnosis", forbidden)
    result = doctor._check_runai()
    assert result.status == "warn"
    assert "não consultado" in result.detail


def test_project_venv_cli_is_found_outside_active_interpreter(monkeypatch, tmp_path):
    from integrations.harness_runtime import HarnessRuntime
    monkeypatch.setattr(doctor, "REPO_ROOT", str(tmp_path))
    monkeypatch.setattr(HarnessRuntime, "resolve_cli_path", lambda self, name: None)
    monkeypatch.delenv("NLM_BIN", raising=False)
    monkeypatch.setattr(doctor.sys, "executable", str(tmp_path / "other/bin/python"))
    binary = tmp_path / ".venv" / "bin" / "nlm"
    binary.parent.mkdir(parents=True)
    binary.write_text("#!/bin/sh\nexit 0\n")
    binary.chmod(0o755)
    assert doctor._resolve_external_cli("nlm") == str(binary)
    monkeypatch.setenv("NLM_BIN", str(tmp_path / "missing"))
    assert doctor._resolve_external_cli("nlm") is None


def test_project_venv_nonexecutable_is_not_installation(monkeypatch, tmp_path):
    from integrations.harness_runtime import HarnessRuntime
    monkeypatch.setattr(doctor, "REPO_ROOT", str(tmp_path))
    monkeypatch.setattr(HarnessRuntime, "resolve_cli_path", lambda self, name: None)
    monkeypatch.delenv("NLM_BIN", raising=False)
    monkeypatch.setattr(doctor.sys, "executable", str(tmp_path / "other/bin/python"))
    binary = tmp_path / ".venv" / "bin" / "nlm"
    binary.parent.mkdir(parents=True)
    binary.write_text("incompleto")
    binary.chmod(0o644)
    assert doctor._resolve_external_cli("nlm") is None


@pytest.mark.parametrize("body", [
    {}, {"ok": True}, {"ok": True, "service": "other", "pid": 7},
    {"ok": True, "service": "runai", "pid": True},
    {"ok": True, "service": "runai", "pid": 0},
    {"ok": "true", "service": "runai", "pid": 7}, [], "healthy",
])
def test_health_rejects_unidentified_or_malformed_service(monkeypatch, body):
    bridge = runai.RunAIProvisioner()
    monkeypatch.setattr(bridge, "_http_get_json", lambda *a, **kw: body)
    result = bridge.api_health()
    assert result["ok"] is False
    assert result["error"] == "invalid_server_identity"
    assert bridge.is_serving() is False


def test_health_preserves_verified_server_identity(monkeypatch):
    bridge = runai.RunAIProvisioner()
    body = {"ok": True, "service": "runai", "pid": 7, "model": "llama3.2-1b"}
    monkeypatch.setattr(bridge, "_http_get_json", lambda *a, **kw: body)
    assert bridge.api_health() == body
    assert bridge.is_serving() is True


def test_stop_cannot_claim_success_while_verified_server_remains(monkeypatch):
    bridge = runai.RunAIProvisioner()
    monkeypatch.setattr(bridge, "_run_cli", lambda *a, **kw: {"ok": True, "exit_code": 0, "stdout": "warning"})
    monkeypatch.setattr(bridge, "api_health", lambda: {"ok": True, "service": "runai", "pid": 7})
    result = bridge.stop()
    assert result["ok"] is False
    assert result["error"] == "server_still_serving"
    assert result["exit_code"] == 0


def test_stop_confirms_termination_without_erasing_cli_failure(monkeypatch):
    bridge = runai.RunAIProvisioner()
    monkeypatch.setattr(bridge, "api_health", lambda: {"ok": False, "server_state": "absent"})
    for cli_result in ({"ok": True, "exit_code": 0}, {"ok": False, "exit_code": 124}):
        monkeypatch.setattr(bridge, "_run_cli", lambda *a, **kw: cli_result.copy())
        result = bridge.stop()
        assert result["ok"] == cli_result["ok"]
        assert result["exit_code"] == cli_result["exit_code"]


@pytest.mark.parametrize("body", [{"ok": False}, {"ok": False, "server_state": "unknown"}])
def test_stop_does_not_convert_unknown_health_to_confirmed_termination(monkeypatch, body):
    bridge = runai.RunAIProvisioner()
    monkeypatch.setattr(bridge, "_run_cli", lambda *a, **kw: {"ok": True, "exit_code": 0})
    monkeypatch.setattr(bridge, "api_health", lambda: body)
    result = bridge.stop()
    assert result["ok"] is False
    assert result["error"] == "termination_unconfirmed"
    assert result["termination_confirmed"] is False


@pytest.mark.parametrize("error", [TimeoutError("prazo"), runai.urllib.error.HTTPError("http://localhost", 503, "unavailable", {}, None)])
def test_health_transport_failures_are_unknown_not_absent(monkeypatch, error):
    bridge = runai.RunAIProvisioner()
    def failed(*a, **kw):
        raise error
    monkeypatch.setattr(bridge, "_http_get_json", failed)
    assert bridge.api_health()["server_state"] == "unknown"


def test_connection_refused_is_confirmed_absence(monkeypatch):
    bridge = runai.RunAIProvisioner()
    def refused(*a, **kw):
        raise runai.urllib.error.URLError(ConnectionRefusedError(111, "refused"))
    monkeypatch.setattr(bridge, "_http_get_json", refused)
    assert bridge.api_health()["server_state"] == "absent"
