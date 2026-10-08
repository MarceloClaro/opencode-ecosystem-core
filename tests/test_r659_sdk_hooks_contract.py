"""Regressões R659: provas herméticas, sem inferência nem efeitos externos."""
import json

import pytest

from hooks.engine import HookMatcher, run_hooks
from hooks.policy import audit_log, default_matchers
from integrations import opencode_agent_sdk as sdk


@pytest.fixture(autouse=True)
def registry():
    previous = dict(sdk._TOOLS)
    sdk._TOOLS.clear()
    yield
    sdk._TOOLS.clear()
    sdk._TOOLS.update(previous)


def setup_query(monkeypatch, raw='{"value": 42}', hooks=None, schema=None):
    executed, requests = [], []

    @sdk.tool("echo", "Ecoa", schema or {
        "type": "object", "properties": {"value": {"type": "integer"}},
        "required": ["value"], "additionalProperties": False,
    })
    def echo(args):
        executed.append(args)
        return {"value": args["value"]}

    def chat(messages, *args):
        requests.append(json.loads(json.dumps(messages)))
        if len(requests) == 1:
            return {"ok": True, "content": "", "tool_calls": [{
                "id": "call1", "type": "function", "function": {
                    "name": "echo", "arguments": raw,
                },
            }]}
        return {"ok": True, "content": "resultado: 42", "tool_calls": []}

    monkeypatch.setattr(sdk, "chat_once", chat)
    options = {"base_url": "http://localhost:11434/v1", "model": "local",
               "allowed_tools": ["echo"], "max_turns": 2, "hooks": hooks or {}}
    return executed, requests, options, echo


def test_global_matchers_deny(monkeypatch):
    executed, _, options, _ = setup_query(monkeypatch, hooks={
        "matchers": [HookMatcher("echo", [lambda *args: False])],
    })
    events = list(sdk.query("ecoar", options))
    assert executed == []
    assert any(e["type"] == "tool_denied" for e in events)


def test_signature_is_adapted_without_retrying_hook_body(monkeypatch):
    attempts = []

    def bad_hook(name, args, context=None):
        attempts.append(name)
        raise TypeError("erro interno")

    executed, _, options, _ = setup_query(monkeypatch, hooks={"PreToolUse": [bad_hook]})
    events = list(sdk.query("ecoar", options))
    assert attempts == ["echo"]
    assert executed == []
    assert "erro interno" in next(e for e in events if e["type"] == "tool_denied")["reason"]


def test_engine_accepts_legacy_callbacks_and_context_event():
    observed = []
    result = run_hooks("PreToolUse", "echo", {}, [HookMatcher("echo", [
        lambda name, args: observed.append(name),
        lambda name, args, context: observed.append(context["event"]),
    ])])
    assert result["allow"] is True
    assert observed == ["echo", "PreToolUse"]


def test_lifecycle_and_assistant_tool_history(monkeypatch):
    observed = []

    def hook(name, args, context):
        observed.append((context["event"], name, context.get("output")))

    executed, requests, options, _ = setup_query(monkeypatch, hooks={
        event: [hook] for event in ("SessionStart", "PreToolUse", "PostToolUse", "SessionEnd")
    })
    events = list(sdk.query("ecoar", options))
    assert executed == [{"value": 42}]
    assert [x[0] for x in observed] == ["SessionStart", "PreToolUse", "PostToolUse", "SessionEnd"]
    assert observed[2][2] == {"value": 42}
    assert [msg["role"] for msg in requests[1]] == ["user", "assistant", "tool"]
    assert requests[1][1]["tool_calls"][0]["id"] == requests[1][2]["tool_call_id"]
    assert json.loads(requests[1][2]["content"]) == {"value": 42}
    assert events[-1] == {"type": "result", "finish": "stop"}


@pytest.mark.parametrize("raw", ['{broken', '[]', 'null', '42', '"string"',
                                     '{}', '{"value":true}', '{"value":42,"extra":1}'])
def test_invalid_arguments_never_execute(monkeypatch, raw):
    executed, _, options, _ = setup_query(monkeypatch, raw=raw)
    events = list(sdk.query("ecoar", options))
    assert executed == []
    assert any(e["type"] == "tool_denied" and "argument" in e["reason"].lower() for e in events)


def test_full_schema_preserved_and_direct_dispatch_validates(monkeypatch):
    executed, _, _, echo = setup_query(monkeypatch)
    schema = sdk._openai_tools(["echo"])[0]["function"]["parameters"]
    assert schema == sdk._TOOLS["echo"]["parameters"]
    server = sdk.create_local_tool_server("test", tools=[echo])
    with pytest.raises(ValueError, match="argument"):
        sdk.dispatch(server, "echo", {"value": "42"})
    assert executed == []
    assert sdk.dispatch(server, "echo", {"value": 42}) == {"value": 42}


@pytest.mark.parametrize("finish", ["stop", "error", "max_turns"])
def test_session_end_even_on_errors_and_budget(monkeypatch, finish):
    observed = []
    _, _, options, _ = setup_query(monkeypatch, hooks={
        "SessionEnd": [lambda n, a, c: observed.append(c["finish"])],
    })
    if finish == "max_turns":
        options["max_turns"] = 1
    elif finish == "error":
        monkeypatch.setattr(sdk, "chat_once", lambda *args: {"ok": False, "error": "offline"})
    list(sdk.query("ecoar", options))
    assert observed == [finish]


def test_session_start_deny_blocks_provider(monkeypatch):
    _, requests, options, _ = setup_query(monkeypatch, hooks={"SessionStart": [lambda *args: False]})
    events = list(sdk.query("ecoar", options))
    assert requests == []
    assert any(e["type"] == "error" and "SessionStart" in e["error"] for e in events)


def test_post_hook_failure_reports_completed_side_effect(monkeypatch):
    executed, _, options, _ = setup_query(monkeypatch, hooks={"PostToolUse": [lambda *args: False]})
    events = list(sdk.query("ecoar", options))
    assert executed == [{"value": 42}]
    assert any(e["type"] == "tool_use" for e in events)
    assert any(e["type"] == "error" and "PostToolUse" in e["error"] for e in events)
    assert not any(e["type"] == "result" and e["finish"] == "stop" for e in events)


@pytest.mark.parametrize("value", [True, 0, -1, "1", 1.2])
def test_budget_validation_is_strict(value):
    with pytest.raises(ValueError, match="max_turns"):
        sdk.build_options("x", max_turns=value)


def test_raw_options_reject_invalid_budget_without_call(monkeypatch):
    _, requests, options, _ = setup_query(monkeypatch)
    options["max_turns"] = True
    events = list(sdk.query("ecoar", options))
    assert requests == []
    assert events[0]["type"] == "error"


def test_disallowed_tools_are_not_advertised(monkeypatch):
    _, _, options, _ = setup_query(monkeypatch)
    advertised = []

    def chat(messages, model, base_url, tools, timeout):
        advertised.extend(tools or [])
        return {"ok": True, "content": "fim", "tool_calls": []}

    monkeypatch.setattr(sdk, "chat_once", chat)
    options["disallowed_tools"] = ["echo"]
    list(sdk.query("ecoar", options))
    assert advertised == []


def test_cli_errors_and_invalid_arguments_return_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(sdk, "query", lambda *args: iter([{"type": "error", "error": "offline"}]))
    assert sdk.main(["query", "--prompt", "x"]) == 1
    assert sdk.main(["query", "--prompt", "x", "--max-turns", "0"]) == 2
    assert sdk.main(["query", "--prompt", "x", "--unknown"]) == 2


def test_audit_bash_logs_hash_instead_of_command(tmp_path, monkeypatch):
    dest = tmp_path / "audit.jsonl"
    monkeypatch.setenv("OPENCODE_HOOKS_AUDIT", str(dest))
    command = "curl -H 'Authorization: bearer SECRET_EXAMPLE' https://example.com"
    run_hooks("PreToolUse", "Bash", {"command": command}, default_matchers())
    raw = dest.read_text()
    record = json.loads(raw)
    assert "SECRET_EXAMPLE" not in raw and "Authorization" not in raw
    assert "command" not in record
    assert len(record["command_sha256"]) == 64


def test_audit_relative_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert audit_log("test", {"tool": "echo"}, path="audit.jsonl") is True
    assert (tmp_path / "audit.jsonl").exists()


def test_close_runs_post_and_session_end(monkeypatch):
    lifecycle = []
    _, _, options, _ = setup_query(monkeypatch, hooks={
        "PostToolUse": [lambda n, a, c: lifecycle.append(c["event"])],
        "SessionEnd": [lambda n, a, c: lifecycle.append(c["finish"])],
    })
    generator = sdk.query("ecoar", options)
    assert next(generator)["type"] == "tool_use"
    generator.close()
    assert lifecycle == ["PostToolUse", "cancelled"]


def test_pre_hook_cannot_bypass_argument_schema(monkeypatch):
    def mutate(name, args, context):
        args["value"] = "not-an-integer"

    executed, _, options, _ = setup_query(monkeypatch, hooks={"PreToolUse": [mutate]})
    events = list(sdk.query("ecoar", options))
    assert executed == []
    assert any(e["type"] == "tool_denied" for e in events)


def test_engine_rejects_unknown_event_and_nested_deny():
    assert run_hooks("Unknown")["allow"] is False
    hook = HookMatcher("*", [lambda *args: {"hookSpecificOutput": {
        "permissionDecision": "deny", "permissionDecisionReason": "regra aninhada",
    }}])
    assert run_hooks("PreToolUse", "echo", {}, [hook])["reason"] == "regra aninhada"


@pytest.mark.parametrize("calls", [[None], [{"id": "x", "function": {}}]])
def test_malformed_provider_calls_fail_without_tool(monkeypatch, calls):
    executed, _, options, _ = setup_query(monkeypatch)
    monkeypatch.setattr(sdk, "chat_once", lambda *args: {"ok": True, "tool_calls": calls})
    events = list(sdk.query("ecoar", options))
    assert executed == []
    assert events[0]["type"] == "error"


def test_cli_reports_failed_tool_and_exhausted_budget(monkeypatch, capsys):
    for event in ({"type": "tool_use", "is_error": True, "output": "failure"},
                  {"type": "result", "finish": "max_turns"}):
        monkeypatch.setattr(sdk, "query", lambda *args: iter([event]))
        assert sdk.main(["query", "--prompt", "x"]) == 1


def test_local_server_metadata_does_not_claim_mcp_export(monkeypatch):
    _, _, _, echo = setup_query(monkeypatch)
    server = sdk.create_local_tool_server("local", tools=[echo])
    assert server["fastmcp_export"] is False
    assert isinstance(server["mcp_available"], bool)


def test_local_server_retains_metadata_of_its_own_handler():
    @sdk.tool("same_name", "Inteiro", {"type": "object", "properties": {"value": {"type": "integer"}}})
    def integer(args):
        return args["value"]

    @sdk.tool("same_name", "Texto", {"type": "object", "properties": {"value": {"type": "string"}}})
    def text(args):
        return args["value"]

    server = sdk.create_local_tool_server("integer", tools=[integer])
    assert server["tools"]["same_name"]["description"] == "Inteiro"
    assert sdk.dispatch(server, "same_name", {"value": 42}) == 42


def test_generic_audit_redacts_nested_credentials_and_commands(tmp_path):
    dest = tmp_path / "generic.jsonl"
    assert audit_log("test", {"args": {"command": "echo TOKEN_SECRET",
                                     "api_key": "KEY_SECRET", "Authorization": "AUTH_SECRET"}},
                     path=str(dest))
    raw = dest.read_text()
    assert "TOKEN_SECRET" not in raw and "KEY_SECRET" not in raw and "AUTH_SECRET" not in raw
    record = json.loads(raw)
    assert len(record["args"]["command_sha256"]) == 64
    assert record["args"]["api_key"] == "[REDACTED]"


def test_audit_unserializable_values_does_not_raise(tmp_path):
    assert audit_log("test", {"value": object()}, path=str(tmp_path / "audit.jsonl")) is False


def test_http_deadline_is_not_renewed_by_provider_keepalives(monkeypatch):
    from types import SimpleNamespace
    import time
    import urllib.request
    elapsed = [0.0]
    reads = []

    class Response:
        fp = SimpleNamespace(raw=SimpleNamespace(_sock=SimpleNamespace(settimeout=lambda seconds: None)))
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"ok":true}'
        def read1(self, size):
            reads.append(1)
            elapsed[0] += 0.6
            return b' ' if len(reads) < 3 else b'{"ok":true}'

    monkeypatch.setattr(time, "monotonic", lambda: elapsed[0])
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: Response())
    assert sdk._http_json("GET", "http://localhost", timeout=1) is None
    assert len(reads) == 2
