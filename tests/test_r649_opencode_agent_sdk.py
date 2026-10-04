# -*- coding: utf-8 -*-
"""Testes TDD do OpenCode Agent SDK free (SPEC-935-R649) — HTTP mockado."""

import json
import sys

import pytest

sys.path.insert(0, ".")

from integrations import opencode_agent_sdk as sdk  # noqa: E402


@pytest.fixture(autouse=True)
def _limpa_tools():
    sdk._TOOLS.clear()
    yield
    sdk._TOOLS.clear()


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return json.dumps(self._payload).encode()


def _mock_urlopen(monkeypatch, routes):
    import urllib.request

    def fake(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req
        for prefix, payload in routes:
            if url.startswith(prefix):
                if isinstance(payload, Exception):
                    raise payload
                return _FakeResp(payload)
        raise OSError("rota nao mockada: " + url)

    monkeypatch.setattr(urllib.request, "urlopen", fake)


def _chat_msg(content="", calls=()):
    return {"choices": [{"message": {"content": content, "tool_calls": list(calls)}}]}


def test_build_options_valida():
    assert sdk.build_options("oi")["max_turns"] == 3
    with pytest.raises(ValueError):
        sdk.build_options("   ")
    with pytest.raises(ValueError):
        sdk.build_options("oi", max_turns=0)


def test_detect_primeiro_saudavel(monkeypatch):
    _mock_urlopen(monkeypatch, [
        ("http://localhost:9379", {"data": [{"id": "m"}]}),
    ])
    prov = sdk.detect_provider()
    assert prov and prov["id"] == "litert-lm"


def test_detect_pula_falho(monkeypatch):
    _mock_urlopen(monkeypatch, [
        ("http://localhost:9379", OSError("down")),
        ("http://localhost:11434", {"data": [{"id": "m"}]}),
    ])
    prov = sdk.detect_provider()
    assert prov and prov["id"] == "ollama"


def test_detect_nenhum(monkeypatch):
    _mock_urlopen(monkeypatch, [("http://", OSError("down"))])
    assert sdk.detect_provider() is None


def test_query_texto_simples(monkeypatch):
    _mock_urlopen(monkeypatch, [
        ("http://localhost:9379/v1/models", {"data": [{"id": "m"}]}),
        ("http://localhost:9379/v1/chat", _chat_msg("ola, mundo")),
    ])
    evs = list(sdk.query("diga oi", {"max_turns": 2}))
    tipos = [e["type"] for e in evs]
    assert "text" in tipos and evs[-1]["type"] == "result"
    assert any("ola" in e.get("text", "") for e in evs if e["type"] == "text")


def test_query_loop_com_tool(monkeypatch):
    @sdk.tool("somar", "Soma", {"a": {"type": "integer"}, "b": {"type": "integer"}})
    def somar(args):
        return args["a"] + args["b"]

    call = {"id": "c1", "type": "function",
            "function": {"name": "somar", "arguments": '{"a": 20, "b": 22}'}}
    _mock_urlopen(monkeypatch, [
        ("http://localhost:9379/v1/models", {"data": [{"id": "m"}]}),
        ("/chat/completions", _chat_msg("", [call])),
    ])
    # segunda chamada de chat devolve texto final
    import urllib.request
    orig = urllib.request.urlopen
    n = {"i": 0}

    def seq(req, timeout=None):
        url = req.full_url
        if url.endswith("/models"):
            return _FakeResp({"data": [{"id": "m"}]})
        n["i"] += 1
        if n["i"] == 1:
            return _FakeResp(_chat_msg("", [call]))
        return _FakeResp(_chat_msg("resultado: 42"))

    monkeypatch.setattr(urllib.request, "urlopen", seq)
    evs = list(sdk.query("some 20+22", {"allowed_tools": ["somar"], "max_turns": 3}))
    tipos = [e["type"] for e in evs]
    assert "tool_use" in tipos
    uso = [e for e in evs if e["type"] == "tool_use"][0]
    assert uso["output"] == 42
    assert evs[-1] == {"type": "result", "finish": "stop"}


def test_query_tool_fora_allowlist_negada(monkeypatch):
    call = {"id": "c1", "type": "function",
            "function": {"name": "apagar", "arguments": "{}"}}
    import urllib.request
    n = {"i": 0}

    def seq(req, timeout=None):
        if req.full_url.endswith("/models"):
            return _FakeResp({"data": [{"id": "m"}]})
        n["i"] += 1
        return _FakeResp(_chat_msg("", [call]) if n["i"] == 1 else _chat_msg("ok"))

    monkeypatch.setattr(urllib.request, "urlopen", seq)
    evs = list(sdk.query("x", {"allowed_tools": [], "max_turns": 2}))
    assert any(e["type"] == "tool_denied" for e in evs)


def test_query_hook_nega(monkeypatch):
    @sdk.tool("ler", "Le", {})
    def ler(args):
        return "segredo"

    call = {"id": "c1", "type": "function",
            "function": {"name": "ler", "arguments": "{}"}}
    import urllib.request
    n = {"i": 0}

    def seq(req, timeout=None):
        if req.full_url.endswith("/models"):
            return _FakeResp({"data": [{"id": "m"}]})
        n["i"] += 1
        return _FakeResp(_chat_msg("", [call]) if n["i"] == 1 else _chat_msg("fim"))

    monkeypatch.setattr(urllib.request, "urlopen", seq)
    evs = list(sdk.query("leia", {
        "allowed_tools": ["ler"], "max_turns": 2,
        "hooks": {"PreToolUse": [lambda n, a: {"permissionDecision": "deny"}]},
    }))
    neg = [e for e in evs if e["type"] == "tool_denied"]
    assert neg and "hook" in neg[0]["reason"].lower() or neg


def test_tool_server_local_executa():
    @sdk.tool("eco", "Ecoa", {"t": {"type": "string"}})
    def eco(args):
        return args["t"]

    srv = sdk.create_local_tool_server("demo", "1.0.0", [eco])
    assert sdk.dispatch(srv, "eco", {"t": "ping"}) == "ping"
    with pytest.raises(ValueError):
        sdk.dispatch(srv, "inexistente", {})


def test_doctor_e_main(monkeypatch, capsys):
    _mock_urlopen(monkeypatch, [("http://", {"data": [{"id": "m"}]})])
    assert sdk.doctor_check()["status"] == "pass"
    assert sdk.main(["status"]) == 0
    assert sdk.main(["--help"]) == 0
    assert sdk.main(["query"]) == 2
    assert sdk.main(["bogus"]) == 2
    assert "0,00" in sdk.install_instructions()
