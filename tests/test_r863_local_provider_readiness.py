"""Contraprovas de prontidão e estrutura R863; HTTP real local, sem inferência."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
from threading import Thread
from types import SimpleNamespace

import pytest

from marceloclaro import doctor


@contextmanager
def catalog_server(payload=None, *, raw=None, redirect=None):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.command, self.path))
            self.send_response(302 if redirect else 200)
            if redirect:
                self.send_header("Location", redirect)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            body = raw if raw is not None else json.dumps(payload).encode()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_binario_presente_nao_aprova_daemon_parado(monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda _: "/fake/ollama")
    with socket.socket() as bound_without_listener:
        bound_without_listener.bind(("127.0.0.1", 0))
        monkeypatch.setenv("OLLAMA_HOST", f"http://127.0.0.1:{bound_without_listener.getsockname()[1]}")
        assert doctor._ollama_live_available() is False


def test_sonda_real_get_modelos_sem_inferencia(monkeypatch):
    with catalog_server({"models": [{"name": "owned-test:latest"}]}) as (endpoint, requests):
        monkeypatch.setenv("OLLAMA_HOST", endpoint)
        report = doctor._ollama_live_probe()
    assert report["available"] is True
    assert report["models_count"] == 1
    assert report["verification"] == "http_model_catalog_only"
    assert report["inference_verified"] is False
    assert requests == [("GET", "/api/tags")]


@pytest.mark.parametrize("payload", [{"models": []}, {"models": "installed"}, {"models": [{}]}, {"models": ["model"]}, {"data": []}])
def test_sonda_recusa_catalogo_invalido(monkeypatch, payload):
    with catalog_server(payload) as (endpoint, _):
        monkeypatch.setenv("OLLAMA_HOST", endpoint)
        report = doctor._ollama_live_probe()
    assert report["available"] is False
    assert report["error"] in {"invalid_catalog", "no_models"}
    assert report["inference_verified"] is False


def test_sonda_recusa_redirect_sem_visitar_destino(monkeypatch):
    with catalog_server({"models": [{"name": "unvisited"}]}) as (destination, visits):
        with catalog_server({}, redirect=destination + "/api/tags") as (endpoint, requests):
            monkeypatch.setenv("OLLAMA_HOST", endpoint)
            report = doctor._ollama_live_probe()
    assert report["available"] is False
    assert report["error"] == "http_error"
    assert visits == []
    assert requests == [("GET", "/api/tags")]


@pytest.mark.parametrize("endpoint", ["http://example.org:11434", "http://secret:password@127.0.0.1:11434", "http://127.0.0.1:11434/?token=secret", "http://127.0.0.1:11434/#secret", "ftp://127.0.0.1:11434", "http://127.0.0.1:invalid"])
def test_sonda_recusa_endpoint_nao_local_ou_com_segredo(monkeypatch, endpoint):
    monkeypatch.setenv("OLLAMA_HOST", endpoint)
    report = doctor._ollama_live_probe()
    assert report["available"] is False
    assert report["error"] == "invalid_endpoint"
    assert "secret" not in json.dumps(report)
    assert endpoint not in json.dumps(report)


def test_sonda_ignora_proxy_herdado(monkeypatch):
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:1")
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:1")
    monkeypatch.setenv("NO_PROXY", "")
    monkeypatch.setenv("no_proxy", "")
    with catalog_server({"models": [{"name": "local"}]}) as (endpoint, requests):
        monkeypatch.setenv("OLLAMA_HOST", endpoint)
        report = doctor._ollama_live_probe()
    assert report["available"] is True
    assert requests == [("GET", "/api/tags")]


def test_sonda_recusa_resposta_acima_do_limite(monkeypatch):
    with catalog_server(raw=b"x" * (128 * 1024 + 1)) as (endpoint, _):
        monkeypatch.setenv("OLLAMA_HOST", endpoint)
        report = doctor._ollama_live_probe()
    assert report["available"] is False
    assert report["error"] == "response_too_large"


def test_timeout_de_sonda_e_finito(monkeypatch):
    import urllib.request
    observed = []

    class Opener:
        def open(self, request, *, timeout):
            observed.append(timeout)
            raise TimeoutError("secret server details")

    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    monkeypatch.setattr(urllib.request, "build_opener", lambda *args: Opener())
    report = doctor._ollama_live_probe()
    assert observed and 0 < observed[0] <= 1
    assert report["error"] == "timeout"
    assert "secret" not in json.dumps(report)


def test_modo_estrutural_nao_sonda_http(monkeypatch):
    monkeypatch.setattr(doctor, "_ollama_available", lambda: True)
    monkeypatch.setattr(doctor, "_ollama_live_probe", lambda: pytest.fail("HTTP não permitido no modo estrutural"), raising=False)
    assert doctor._check_llm_providers(live=False).status == "pass"


def test_check_live_relata_prontidao_sem_inferencia(monkeypatch):
    with catalog_server({"models": [{"name": "local"}]}) as (endpoint, requests):
        monkeypatch.setenv("OLLAMA_HOST", endpoint)
        check = doctor._check_llm_providers(live=True)
    assert check.status == "pass"
    assert "prontidão HTTP/modelos" in check.detail
    assert "não comprova inferência" in check.detail
    assert requests == [("GET", "/api/tags")]


def test_check_live_indisponivel_avisa_sem_vazar_endpoint(monkeypatch):
    import research_factory.pair_router as pair
    monkeypatch.setattr(pair, "pair_provider_status", lambda: "")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_HOST", "http://secret:password@127.0.0.1:11434")
    monkeypatch.setattr(doctor.shutil, "which", lambda _: "/fake/ollama")
    check = doctor._check_llm_providers(live=True)
    assert check.status == "warn"
    assert "invalid_endpoint" in check.detail
    assert "secret" not in check.detail and "password" not in check.detail


def test_specs_ambiguas_falham_mesmo_com_specs_unicas(monkeypatch):
    import sdd.spec_engine as engine
    monkeypatch.setattr(engine, "SpecRegistry", lambda: SimpleNamespace(
        load_formal_specs=lambda: 3,
        ambiguous_spec_sources={"DUPLICATE": ("first.md", "second.md")},
    ))
    check = doctor._check_formal_specs()
    assert check.status == "fail"
    assert "DUPLICATE" in check.detail


@pytest.mark.parametrize("config", [
    {"agent": {"marceloclaro": {"mode": "subagent"}}, "default_agent": "marceloclaro"},
    {"agent": {"marceloclaro": {"mode": "primary"}}, "default_agent": "other"},
    {"agent": {"marceloclaro": {"mode": "primary"}}},
    {"agent": {"marceloclaro": {}}, "default_agent": "marceloclaro"},
])
def test_config_exige_primario_e_default_agent_corretos(monkeypatch, tmp_path, config):
    (tmp_path / "opencode.json").write_text(json.dumps(config))
    monkeypatch.setattr(doctor, "REPO_ROOT", str(tmp_path))
    assert doctor._check_opencode_config().status == "fail"


def test_config_primario_valido_passa(monkeypatch, tmp_path):
    (tmp_path / "opencode.json").write_text(json.dumps({
        "agent": {"marceloclaro": {"mode": "primary"}}, "default_agent": "marceloclaro"}))
    monkeypatch.setattr(doctor, "REPO_ROOT", str(tmp_path))
    assert doctor._check_opencode_config().status == "pass"
