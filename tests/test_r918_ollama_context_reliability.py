"""Contraprovas R918: contexto, erros e uso em providers locais/mockados."""
from __future__ import annotations

import json
import urllib.error

import pytest

from integrations import opencode_agent_sdk as sdk


class FakeResponse:
    status = 200
    headers = {}

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size=-1):
        return json.dumps(self.payload).encode()


def make_response(content="ok", usage=None):
    body = {"choices": [{"message": {"content": content, "tool_calls": []}}]}
    if usage is not None:
        body["usage"] = usage
    return FakeResponse(body)


def test_options_validate_context_and_output_budget():
    opts = sdk.build_options("short task", context_window=8192,
        max_output_tokens=512, context_safety_tokens=128)
    assert opts["context_window"] == 8192
    assert opts["max_output_tokens"] == 512
    with pytest.raises(ValueError, match="context_window"):
        sdk.build_options("x", context_window=1)
    with pytest.raises(ValueError, match="max_output_tokens"):
        sdk.build_options("x", max_output_tokens=0)


def test_context_budget_blocks_before_http_without_truncating(monkeypatch):
    calls = []
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": True, "context_window": 512, "source": "test_modelfile_num_ctx"
    })
    monkeypatch.setattr(sdk.urllib.request, "urlopen", lambda *a, **k: calls.append(a))
    prompt = "A" * 6000
    events = list(sdk.query(prompt, {
        "base_url": "http://localhost:11434/v1", "model": "llama3.2",
        "context_window": 512, "max_output_tokens": 128,
        "context_safety_tokens": 64,
    }))
    errors = [event for event in events if event["type"] == "error"]
    assert errors and errors[0]["code"] == "context_budget_exceeded"
    assert not calls
    assert prompt not in errors[0].get("error", "")


def test_provider_usage_is_preserved_in_usage_event(monkeypatch):
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": True, "context_window": 8192, "source": "test_modelfile_num_ctx"
    })
    def fake(_request, timeout=None):
        return make_response("answer", {"prompt_tokens": 21, "completion_tokens": 4,
                                         "total_tokens": 25})
    monkeypatch.setattr(sdk.urllib.request, "urlopen", fake)
    events = list(sdk.query("question", {"base_url": "http://localhost:11434/v1",
        "model": "llama3.2", "context_window": 8192}))
    usage = next(event for event in events if event["type"] == "usage")
    assert usage["input_tokens"] == 21
    assert usage["output_tokens"] == 4
    assert usage["token_count_source"] == "provider"
    assert usage["token_counts_exact"] is True
    assert usage["query_id"].startswith("query-")
    assert events[-1] == {"type": "result", "finish": "stop"}


@pytest.mark.parametrize(
    "status,message,expected",
    [
        (400, "prompt is too long for this model context length", "context_window_exceeded"),
        (429, "Quota exceeded; retry after 40 seconds", "quota_exceeded"),
        (401, "invalid api key", "authentication_failed"),
        (503, "server overloaded", "provider_unavailable"),
    ],
)
def test_http_provider_errors_are_classified_without_retry(monkeypatch, status, message, expected):
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": True, "context_window": 8192, "source": "test_modelfile_num_ctx"
    })
    attempts = []
    error = urllib.error.HTTPError(
        "http://localhost:11434/v1/chat/completions", status, "provider error",
        {"Retry-After": "40"}, __import__("io").BytesIO(
            json.dumps({"error": message if status == 400 else {"message": message}}).encode()),
    )

    def fail(*_args, **_kwargs):
        attempts.append(1)
        raise error

    monkeypatch.setattr(sdk.urllib.request, "urlopen", fail)
    events = list(sdk.query("short question", {"base_url": "http://localhost:11434/v1",
        "model": "llama3.2", "context_window": 8192}))
    response = next(event for event in events if event["type"] == "error")
    assert response["code"] == expected
    assert message not in response["error"]
    assert len(attempts) == 1
    if status == 429:
        assert response["retry_after_seconds"] == 40


def test_missing_provider_usage_is_estimated_and_labeled(monkeypatch):
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": True, "context_window": 8192, "source": "test_modelfile_num_ctx"
    })
    monkeypatch.setattr(sdk.urllib.request, "urlopen", lambda *_a, **_k: make_response("answer"))
    events = list(sdk.query("question", {"base_url": "http://localhost:11434/v1",
        "model": "llama3.2", "context_window": 8192}))
    usage = next(event for event in events if event["type"] == "usage")
    assert usage["token_count_source"] == "estimated_utf8_bytes_div_3"
    assert usage["token_counts_exact"] is False


def test_quota_retry_hint_in_provider_body_is_preserved_without_retry(monkeypatch):
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": True, "context_window": 8192, "source": "test_modelfile_num_ctx"
    })
    attempts = []
    error = urllib.error.HTTPError(
        "http://localhost:11434/v1/chat/completions", 429, "quota",
        {}, __import__("io").BytesIO(json.dumps({
            "error": "Quota exceeded. Please retry in 40.013107556s."
        }).encode()),
    )

    def fail(*_args, **_kwargs):
        attempts.append(1)
        raise error

    monkeypatch.setattr(sdk.urllib.request, "urlopen", fail)
    events = list(sdk.query("short", {"base_url": "http://localhost:11434/v1",
        "model": "llama3.2", "context_window": 8192}))
    result = next(event for event in events if event["type"] == "error")
    assert result["code"] == "quota_exceeded"
    assert result["retry_after_seconds"] == pytest.approx(40.013107556)
    assert len(attempts) == 1


def test_no_automatic_context_truncation_or_provider_fallback(monkeypatch):
    calls = []
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": True, "context_window": 1024, "source": "test_modelfile_num_ctx"
    })
    monkeypatch.setattr(sdk.urllib.request, "urlopen", lambda *a, **k: calls.append(a))
    prompt = "meaningful-user-content " * 1000
    events = list(sdk.query(prompt, {"base_url": "http://localhost:11434/v1",
        "model": "gemma4:e2b-tuned", "context_window": 1024,
        "max_output_tokens": 256, "context_safety_tokens": 128}))
    error = next(event for event in events if event["type"] == "error")
    assert error["code"] == "context_budget_exceeded"
    assert not calls
    assert all(event.get("provider") != "openai" for event in events)


def test_ollama_runtime_num_ctx_overrides_catalog_declaration(monkeypatch):
    monkeypatch.setattr(sdk.urllib.request, "urlopen", lambda *_a, **_k: FakeResponse({
        "modelfile": "FROM llama3.2:latest\nPARAMETER temperature 0.7\n"
    }))
    probe = sdk._probe_ollama_context("http://localhost:11434/v1", "llama3.2")
    assert probe == {"ok": True, "context_window": 2048,
                     "source": "ollama_api_show_documented_default_num_ctx"}


def test_ollama_modelfile_num_ctx_is_observed_without_inference(monkeypatch):
    calls = []
    def fake(request, timeout=None):
        calls.append(request.full_url)
        return FakeResponse({"modelfile": "FROM gemma4:e2b\nPARAMETER num_ctx 24576\n"})
    monkeypatch.setattr(sdk.urllib.request, "urlopen", fake)
    probe = sdk._probe_ollama_context("http://localhost:11434/v1", "gemma4:e2b-tuned")
    assert probe == {"ok": True, "context_window": 24576,
                     "source": "ollama_api_show_modelfile_num_ctx"}
    assert calls == ["http://localhost:11434/api/show"]


def test_preflight_uses_ollama_num_ctx_instead_of_larger_catalog_limit(monkeypatch):
    urls = []
    def fake(request, timeout=None):
        urls.append(request.full_url)
        if request.full_url.endswith("/api/show"):
            return FakeResponse({"modelfile": "FROM llama3.2:latest\n"})
        pytest.fail("context preflight should block before chat/completions")
    monkeypatch.setattr(sdk.urllib.request, "urlopen", fake)
    events = list(sdk.query("x" * 9000, {"base_url": "http://localhost:11434/v1",
        "model": "llama3.2", "context_window": 32768,
        "max_output_tokens": 512, "context_safety_tokens": 128}))
    error = next(event for event in events if event["type"] == "error")
    assert error["code"] == "context_budget_exceeded"
    assert error["context_window"] == 2048
    assert error["context_window_source"] == "min_operator_cap_and_ollama_api_show_documented_default_num_ctx"
    assert urls == ["http://localhost:11434/api/show"]


def test_ollama_probe_failure_abstains_without_explicit_window(monkeypatch):
    calls = []
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": False, "code": "provider_unavailable"
    })
    monkeypatch.setattr(sdk.urllib.request, "urlopen", lambda *a, **k: calls.append(a))
    events = list(sdk.query("question", {"base_url": "http://localhost:11434/v1",
        "model": "llama3.2"}))
    error = next(event for event in events if event["type"] == "error")
    assert error["code"] == "ollama_context_probe_failed"
    assert error["context_window_verified"] is False
    assert not calls


def test_explicit_window_after_probe_failure_is_never_marked_verified(monkeypatch):
    monkeypatch.setattr(sdk, "_probe_ollama_context", lambda *_a, **_k: {
        "ok": False, "code": "provider_unavailable"
    })
    monkeypatch.setattr(sdk.urllib.request, "urlopen", lambda *_a, **_k: make_response("ok", {
        "prompt_tokens": 4, "completion_tokens": 1, "total_tokens": 5
    }))
    events = list(sdk.query("short", {"base_url": "http://localhost:11434/v1",
        "model": "llama3.2", "context_window": 8192}))
    usage = next(event for event in events if event["type"] == "usage")
    assert usage["context_window_source"] == "operator_declared_unverified_after_probe_failure"
    assert usage["context_window_verified"] is False


def test_r918_does_not_change_opencode_default_model():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
    assert config["model"] == "ollama-local/llama3.2"
