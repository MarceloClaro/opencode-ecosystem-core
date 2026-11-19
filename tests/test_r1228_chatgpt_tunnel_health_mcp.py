"""R1228: o status do túnel separa polling de observação MCP."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrations import chatgpt_tunnel_full_mcp as mod  # noqa: E402


def _health_mcp(*, state="not_observed", details=None):
    return {
        "schema_version": 1,
        "component": "mcp",
        "status": "unknown" if state == "not_observed" else "ok",
        "state": state,
        "limited": False,
        "details": details or {
            "initialize_epoch": 0,
            "initialize": {
                "ok": False,
                "identity_complete": False,
                "limited": False,
                "capability_names": [],
            },
            "tools_list": {
                "ok": False,
                "tool_names": [],
                "retained_count": 0,
                "complete": False,
                "partial": False,
                "limited": False,
            },
        },
    }


def _prepare_running_tunnel(tmp_path, monkeypatch):
    (tmp_path / "tunnel.pid").write_text(f"{os.getpid()}\n", encoding="ascii")
    (tmp_path / "health-url").write_text(
        "http://127.0.0.1:36135", encoding="ascii"
    )
    observed = datetime.now(timezone.utc).isoformat()
    monkeypatch.setattr(mod, "_alive", lambda _pid: True)
    return observed


def _install_health_responses(monkeypatch, *, mcp_response):
    observed = datetime.now(timezone.utc).isoformat()
    seen = []

    def fake_fetch(_base, path, *, json_body=False, require_success=False):
        seen.append((path, json_body, require_success))
        if path == "/readyz":
            return 200
        if path == "/health/control-plane":
            return {"details": {"observed_at": observed, "consecutive_failures": 0}}
        if path == "/health/mcp":
            return mcp_response
        raise AssertionError(f"endpoint inesperado: {path}")

    monkeypatch.setattr(mod, "_fetch", fake_fetch)
    return observed, seen


def test_status_preserva_polling_e_expoe_not_observed_separadamente(
    tmp_path, monkeypatch
):
    _prepare_running_tunnel(tmp_path, monkeypatch)
    mcp = _health_mcp()
    _observed, seen = _install_health_responses(monkeypatch, mcp_response=mcp)

    result = mod.status(tmp_path)

    assert result["tunel"] == "polling_confirmado"
    assert result["ultimo_poll_utc"]
    assert result["mcp"] == mod.MCP_MODULE
    assert result["mcp_discovery"] == {
        "available": True,
        "status": "unknown",
        "state": "not_observed",
        "initialize_epoch": 0,
        "initialize": {
            "ok": False,
            "identity_complete": False,
            "limited": False,
            "capability_names": [],
        },
        "tools_list": {
            "ok": False,
            "tool_names": [],
            "retained_count": 0,
            "complete": False,
            "partial": False,
            "limited": False,
        },
    }
    assert [entry[0] for entry in seen] == [
        "/readyz",
        "/health/control-plane",
        "/health/mcp",
    ]
    assert seen[-1] == ("/health/mcp", True, True)


def test_status_projeta_initialize_e_tools_list_sem_corpo_bruto(
    tmp_path, monkeypatch
):
    _prepare_running_tunnel(tmp_path, monkeypatch)
    response = _health_mcp(
        state="tools_list_observed",
        details={
            "initialize_epoch": 4,
            "initialize": {
                "ok": True,
                "identity_complete": True,
                "limited": False,
                "capability_names": ["tools", "resources"],
                "private_token": "must-not-escape",
            },
            "tools_list": {
                "ok": True,
                "tool_names": ["ecosystem_integration_status", "ecosystem_run"],
                "retained_count": 2,
                "complete": True,
                "partial": False,
                "limited": False,
                "private_header": "must-not-escape",
            },
            "private_detail": "must-not-escape",
        },
    )
    _install_health_responses(monkeypatch, mcp_response=response)

    result = mod.status(tmp_path)

    assert result["tunel"] == "polling_confirmado"
    assert result["mcp_discovery"] == {
        "available": True,
        "status": "ok",
        "state": "tools_list_observed",
        "initialize_epoch": 4,
        "initialize": {
            "ok": True,
            "identity_complete": True,
            "limited": False,
            "capability_names": ["tools", "resources"],
        },
        "tools_list": {
            "ok": True,
            "tool_names": ["ecosystem_integration_status", "ecosystem_run"],
            "retained_count": 2,
            "complete": True,
            "partial": False,
            "limited": False,
        },
    }
    assert "must-not-escape" not in repr(result)


@pytest.mark.parametrize(
    "response",
    [None, {}, {"component": "other", "state": "tools_list_observed"},
     {"component": "mcp", "state": 17, "details": {}}],
    ids=["endpoint-ausente", "json-vazio", "componente-divergente", "schema-invalido"],
)
def test_status_mcp_indisponivel_nao_rebaixa_polling(
    tmp_path, monkeypatch, response
):
    _prepare_running_tunnel(tmp_path, monkeypatch)
    _install_health_responses(monkeypatch, mcp_response=response)

    result = mod.status(tmp_path)

    assert result["tunel"] == "polling_confirmado"
    assert result["mcp_discovery"] == {
        "available": False,
        "status": "unavailable",
        "state": "unavailable",
        "initialize_epoch": None,
        "initialize": None,
        "tools_list": None,
    }


def test_status_endpoint_mcp_com_falha_de_transporte_nao_gera_excecao(
    tmp_path, monkeypatch
):
    _prepare_running_tunnel(tmp_path, monkeypatch)
    observed = datetime.now(timezone.utc).isoformat()

    def fake_fetch(_base, path, *, json_body=False, require_success=False):
        if path == "/readyz":
            return 200
        if path == "/health/control-plane":
            return {"details": {"observed_at": observed, "consecutive_failures": 0}}
        if path == "/health/mcp":
            raise OSError("listener MCP indisponível")
        raise AssertionError(f"endpoint inesperado: {path}")

    monkeypatch.setattr(mod, "_fetch", fake_fetch)

    result = mod.status(tmp_path)

    assert result["tunel"] == "polling_confirmado"
    assert result["mcp_discovery"]["state"] == "unavailable"


def test_fetch_rejeita_http_nao_2xx_quando_exigido(monkeypatch):
    class Response:
        status = 503

        @staticmethod
        def read(_limit):
            return b'{"component":"mcp","state":"tools_list_observed"}'

    class Connection:
        def __init__(self, *_args, **_kwargs):
            self.closed = False

        @staticmethod
        def request(*_args):
            pass

        @staticmethod
        def getresponse():
            return Response()

        def close(self):
            self.closed = True

    monkeypatch.setattr(mod.http.client, "HTTPConnection", Connection)

    assert mod._fetch(
        "http://127.0.0.1:36135",
        "/health/mcp",
        json_body=True,
        require_success=True,
    ) == {}


def test_status_sem_processo_nao_consulta_listener_e_mcp_fica_indisponivel(
    tmp_path, monkeypatch
):
    def unexpected(*_args, **_kwargs):
        raise AssertionError("status parado não deve consultar ou iniciar processos")

    monkeypatch.setattr(mod, "_fetch", unexpected)
    monkeypatch.setattr(mod.subprocess, "Popen", unexpected)

    result = mod.status(tmp_path)

    assert result["tunel"] == "parado"
    assert result["mcp_discovery"]["state"] == "unavailable"
