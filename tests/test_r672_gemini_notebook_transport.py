"""R672: transporte real de subprocessos; servidor fixture sem rede."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys

import jsonschema
import pytest

from integrations.gemini_notebook_transport import (
    GeminiNotebookTransport,
    classify_tool_result,
    sanitize_output,
)


SERVER = r'''import json, os, sys, time
log = os.environ.get("R672_PROTOCOL_LOG")
jobs = {}
for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    if log:
        with open(log, "a") as f: f.write(method + "\n")
    if "id" not in request:
        continue
    if method == "initialize":
        result = {"protocolVersion":"2025-03-26", "capabilities":{"tools":{}},
                  "serverInfo":{"name":"hermetic-notebook-fixture","version":"0.1"}}
        if os.environ.get("R672_FIXTURE_MODE") == "environment":
            result["serverInfo"]["version"] = os.environ.get("NOTEBOOKLM_DOWNLOAD_DIR", "absent")
    elif method == "tools/list":
        result = {"tools":[{"name":"notebook_list", "description":"Fixture sem rede",
                 "annotations":{"readOnlyHint":True}, "inputSchema":{"type":"object",
                   "properties":{"limit":{"type":"integer", "minimum":1, "maximum":10},
                     "options":{"type":"object", "properties":{"label":{"type":"string"}}}}}}]}
        result["tools"].extend([
          {"name":"notebook_query_start","inputSchema":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}},
          {"name":"notebook_query_status","inputSchema":{"type":"object","properties":{"query_id":{"type":"string"}},"required":["query_id"]}}])
        if os.environ.get("R672_FIXTURE_SCHEMA") == "external_ref":
            result["tools"][0]["inputSchema"] = {"$ref":"https://invalid.example/private-schema.json"}
        if os.environ.get("R672_FIXTURE_SCHEMA") == "local_ref":
            result["tools"][0]["inputSchema"] = {"type":"object", "properties":{"options":{"$ref":"#/$defs/options"}},
              "$defs":{"options":{"type":"object","properties":{"label":{"type":"string"}}}}}
        if os.environ.get("R672_FIXTURE_SCHEMA") == "public_catalog":
            result = {"tools":json.load(open(os.environ["R672_PUBLIC_CATALOG"]))["tools"]}
    elif method == "tools/call":
        if request["params"]["name"] == "notebook_query_start":
            jobs["job-1"] = request["params"]["arguments"]["query"]
            result = {"isError":False,"structuredContent":{"status":"pending","query_id":"job-1"}}
            print(json.dumps({"jsonrpc":"2.0","id":request["id"],"result":result}),flush=True)
            continue
        if request["params"]["name"] == "notebook_query_status":
            job = request["params"]["arguments"]["query_id"]
            result = {"isError":False,"structuredContent":{"status":"completed" if job in jobs else "error","answer":jobs.get(job)}}
            print(json.dumps({"jsonrpc":"2.0","id":request["id"],"result":result}),flush=True)
            continue
        mode = os.environ.get("R672_FIXTURE_MODE", "ok")
        if mode == "sleep": time.sleep(5)
        if mode == "oversize":
            sys.stdout.write("x" * (1048576 + 1) + "\n"); sys.stdout.flush(); continue
        if mode == "oversize_stderr":
            sys.stderr.write("x" * (1048576 + 1)); sys.stderr.flush(); time.sleep(5)
        if mode == "business_error":
            result = {"isError":False,"content":[{"type":"text","text":json.dumps({"status":"error","message":"Sessão ausente"})}]}
        elif mode in {"pending","running","generating","partial"}:
            result = {"isError":False,"structuredContent":{"status":mode,"job_id":"hermetic-job"},
              "content":[{"type":"text","text":json.dumps({"status":mode,"job_id":"hermetic-job"})}]}
        else:
            result = {"isError":False,"content":[{"type":"text","text":json.dumps({"status":"success","notebooks":[]})}]}
    else:
        result = {}
    print(json.dumps({"jsonrpc":"2.0", "id":request["id"], "result":result}), flush=True)
'''


@pytest.fixture
def transport(tmp_path, monkeypatch):
    bin_dir = tmp_path / ".venv" / "bin"
    bin_dir.mkdir(parents=True)
    program = bin_dir / "notebooklm-mcp"
    program.write_text("#!" + sys.executable + "\n" + SERVER)
    program.chmod(0o755)
    log = tmp_path / "protocol.log"
    monkeypatch.setenv("R672_PROTOCOL_LOG", str(log))
    return GeminiNotebookTransport(tmp_path), log


def test_resolves_virtual_environment_outside_path(tmp_path, monkeypatch):
    executable = tmp_path / ".venv" / "bin" / "nlm"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", "")
    monkeypatch.delenv("NLM_BIN", raising=False)
    assert GeminiNotebookTransport(tmp_path).resolve_binary("nlm") == executable.resolve()


def test_explicit_nlm_bin_is_resolved(tmp_path, monkeypatch):
    executable = tmp_path / "custom-nlm"
    executable.write_text("#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    monkeypatch.setenv("NLM_BIN", str(executable))
    assert GeminiNotebookTransport(tmp_path).resolve_binary("nlm") == executable.resolve()


def test_unrelated_binary_is_not_executable(transport):
    client, _ = transport
    with pytest.raises(ValueError):
        client.resolve_binary("bash")


def test_missing_server_is_blocked_without_process(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "")
    result = asyncio.run(GeminiNotebookTransport(tmp_path).discover_mcp())
    assert result["status"] == "blocked"
    assert result["process_executed"] is False


def test_discovery_uses_handshake_and_preserves_schemas(transport):
    client, log = transport
    result = asyncio.run(client.discover_mcp())
    assert result["status"] == "completed"
    assert result["process_executed"] is True
    assert result["name"] == "hermetic-notebook-fixture"
    assert result["version"] == "0.1"
    assert result["tools"][0]["annotations"]["readOnlyHint"] is True
    assert "limit" in result["tools"][0]["inputSchema"]["properties"]
    assert log.read_text().splitlines() == ["initialize", "notifications/initialized", "tools/list"]


def test_all_49_public_schemas_are_valid_and_preserved_without_redaction(transport, monkeypatch):
    client, _ = transport
    catalog = Path(__file__).resolve().parents[1] / "docs/evidence/R672_PUBLIC_MCP_CATALOG.json"
    monkeypatch.setenv("R672_FIXTURE_SCHEMA", "public_catalog")
    monkeypatch.setenv("R672_PUBLIC_CATALOG", str(catalog))
    expected = json.loads(catalog.read_text())["tools"]
    assert len(expected) == 49
    discovery = asyncio.run(client.discover_mcp())
    assert discovery["status"] == "completed"
    invalid = []
    for tool in discovery["tools"]:
        try:
            jsonschema.validators.validator_for(tool["inputSchema"]).check_schema(tool["inputSchema"])
        except jsonschema.SchemaError:
            invalid.append(tool["name"])
    assert invalid == []
    assert discovery["tools"] == expected


def test_calls_discovered_tool_after_validating_schema(transport):
    client, log = transport
    result = asyncio.run(client.call_mcp("notebook_list", {"limit":2}))
    assert result["status"] == "completed"
    assert result["transport_success"] is True
    assert log.read_text().splitlines()[-1] == "tools/call"


@pytest.mark.parametrize("arguments", [{"limit":0}, {"limit":"two"},
    {"limit":True}, {"surprise":1}, {"options":{"injected":True}}])
def test_invalid_schema_never_calls_tool(transport, arguments):
    client, log = transport
    result = asyncio.run(client.call_mcp("notebook_list", arguments))
    assert result["status"] == "blocked"
    assert "tools/call" not in log.read_text().splitlines()


def test_unknown_operation_never_calls_tool(transport):
    client, log = transport
    result = asyncio.run(client.call_mcp("unregistered_action", {}))
    assert result["status"] == "blocked"
    assert "tools/call" not in log.read_text().splitlines()


def test_external_schema_references_are_blocked_without_fetching(transport, monkeypatch):
    client, log = transport
    monkeypatch.setenv("R672_FIXTURE_SCHEMA", "external_ref")
    result = asyncio.run(client.call_mcp("notebook_list", {}))
    assert result["status"] == "blocked"
    assert "tools/call" not in log.read_text().splitlines()


def test_local_schema_references_validate_nested_unknown_fields(transport, monkeypatch):
    client, log = transport
    monkeypatch.setenv("R672_FIXTURE_SCHEMA", "local_ref")
    result = asyncio.run(client.call_mcp("notebook_list", {"options":{"label":"allowed"}}))
    assert result["status"] == "completed"
    log.unlink()
    rejected = asyncio.run(client.call_mcp("notebook_list", {"options":{"injected":True}}))
    assert rejected["status"] == "blocked"
    assert "tools/call" not in log.read_text().splitlines()


@pytest.mark.parametrize("arguments", [{"limit":float("nan")}, {"large":"x"*131073}, []])
def test_unbounded_or_nonobject_arguments_do_not_start_process(transport, arguments):
    client, log = transport
    result = asyncio.run(client.call_mcp("notebook_list", arguments))
    assert result["status"] == "blocked"
    assert result["process_executed"] is False
    assert not log.exists()


@pytest.mark.parametrize("payload", [
    {"isError":True,"content":[]},
    {"isError":False,"structuredContent":{"success":False}},
    {"isError":False,"structuredContent":{"ok":False}},
    {"isError":False,"content":[{"type":"text","text":'{"status":"error","message":"auth"}'}]},
    {"isError":False,"content":[{"type":"text","text":'{"result":{"status":"failed"}}'}]},
])
def test_business_failures_are_not_completed(payload):
    assert classify_tool_result(payload)["status"] == "failed"


def test_successful_plain_text_is_not_fabricated_business_confirmation():
    result = classify_tool_result({"isError":False,"content":[{"type":"text","text":"answer"}]})
    assert result["status"] == "completed"
    assert result["business_success"] is None


@pytest.mark.parametrize("state", ["pending","running","generating","partial"])
def test_async_business_states_are_preserved(state):
    payload = {"isError":False,"content":[{"type":"text","text":json.dumps({"status":state,"job_id":"hermetic"})}]}
    result = classify_tool_result(payload)
    assert result["status"] == state
    assert result["business_success"] is not True


@pytest.mark.parametrize("counts, expected", [
    ({"failed":1,"succeeded":2,"total_steps":3},"partial"),
    ({"succeeded":2,"total_steps":3},"partial"),
    ({"failed":3,"succeeded":0,"total_steps":3},"failed"),
    ({"succeeded":0,"total_steps":3},"pending"),
    ({"succeeded":3,"total_steps":3},"completed"),
])
def test_nested_batch_counts_override_outer_success(counts, expected):
    result = classify_tool_result({"isError":False,"structuredContent":{"status":"success", "summary":counts}})
    assert result["status"] == expected
    assert result["business_success"] is (True if expected == "completed" else False if expected in {"failed","partial"} else None)


@pytest.mark.parametrize("state", ["pending","running","generating","partial"])
def test_mcp_async_states_survive_transport(transport, monkeypatch, state):
    client, _ = transport
    monkeypatch.setenv("R672_FIXTURE_MODE", state)
    result = asyncio.run(client.call_mcp("notebook_list", {}))
    assert result["status"] == state
    assert result["transport_success"] is True
    assert result["business_success"] is not True


@pytest.mark.parametrize("state", ["pending","running","generating","partial"])
def test_cli_async_states_survive_exit_zero(tmp_path, monkeypatch, state):
    exe = tmp_path / "nlm-state"
    exe.write_text("#!"+sys.executable+"\nprint("+repr(json.dumps({"status":state,"job_id":"hermetic"}))+ ")\n")
    exe.chmod(0o755)
    monkeypatch.setenv("NLM_BIN", str(exe))
    result = asyncio.run(GeminiNotebookTransport(tmp_path).run_cli(["nlm", "notebook", "query"]))
    assert result["status"] == state
    assert result["exit_code"] == 0
    assert result["business_success"] is not True


def test_tool_result_error_is_preserved_as_failure(transport, monkeypatch):
    client, _ = transport
    monkeypatch.setenv("R672_FIXTURE_MODE", "business_error")
    result = asyncio.run(client.call_mcp("notebook_list", {}))
    assert result["status"] == "failed"
    assert result["transport_success"] is True


def test_timeout_ends_child_process(transport, monkeypatch):
    client, _ = transport
    monkeypatch.setenv("R672_FIXTURE_MODE", "sleep")
    result = asyncio.run(client.call_mcp("notebook_list", {}, timeout_seconds=0.15))
    assert result["status"] == "failed"
    assert result["reason"] == "timeout"
    assert result["process_executed"] is True


@pytest.mark.parametrize("mode", ["oversize", "oversize_stderr"])
def test_output_limits_end_process(transport, monkeypatch, mode):
    client, _ = transport
    monkeypatch.setenv("R672_FIXTURE_MODE", mode)
    result = asyncio.run(client.call_mcp("notebook_list", {}, timeout_seconds=2))
    assert result["status"] == "failed"
    assert result["reason"] == "output_limit"


def test_sanitizes_credentials_recursively_and_in_text():
    raw = {"access_token":"secret123", "nested":{"Cookie":"SID=private"},
           "description":"Authorization: Bearer sensitive\nCookie: SID=private\nUseful status"}
    rendered = json.dumps(sanitize_output(raw))
    assert "secret123" not in rendered
    assert "sensitive" not in rendered
    assert "private" not in rendered
    assert "Useful status" in rendered


def test_internal_environment_overrides_preserve_other_environment(transport, monkeypatch):
    client, log = transport
    monkeypatch.setenv("R672_FIXTURE_MODE", "environment")
    configured = GeminiNotebookTransport(client.repo_root, env_overrides={"NOTEBOOKLM_DOWNLOAD_DIR":"/workspace/downloads"})
    result = asyncio.run(configured.discover_mcp())
    assert result["status"] == "completed"
    assert result["version"] == "/workspace/downloads"
    assert log.exists()


def test_mcp_forces_stdio_and_disables_debug_environment(transport, monkeypatch):
    client, _ = transport
    monkeypatch.setenv("NOTEBOOKLM_MCP_TRANSPORT", "http")
    monkeypatch.setenv("NOTEBOOKLM_MCP_DEBUG", "true")
    original = asyncio.create_subprocess_exec
    captured = {}

    async def inspect(*args, **kwargs):
        captured["argv"] = args
        captured["env"] = kwargs["env"]
        return await original(*args, **kwargs)
    monkeypatch.setattr(asyncio, "create_subprocess_exec", inspect)
    result = asyncio.run(client.discover_mcp())
    assert result["status"] == "completed"
    assert captured["argv"][1:] == ("--transport", "stdio", "--no-debug")
    assert captured["env"]["NOTEBOOKLM_MCP_DEBUG"] == "false"


def test_cli_uses_argument_vector_and_noninteractive_input(tmp_path, monkeypatch):
    exe = tmp_path / "nlm-test"
    exe.write_text("#!"+sys.executable+"\nimport json,sys\nprint(json.dumps({'args':sys.argv[1:],'stdin':sys.stdin.read()}))\n")
    exe.chmod(0o755)
    monkeypatch.setenv("NLM_BIN", str(exe))
    result = asyncio.run(GeminiNotebookTransport(tmp_path).run_cli(["nlm", "--help", "a; touch /tmp/no"]))
    assert result["status"] == "completed"
    assert result["result"]["args"] == ["--help", "a; touch /tmp/no"]
    assert result["result"]["stdin"] == ""


def test_cli_exit_zero_json_error_is_failure(tmp_path, monkeypatch):
    exe = tmp_path / "nlm-error"
    exe.write_text("#!"+sys.executable+"\nprint('{\"status\":\"error\",\"message\":\"session missing\"}')\n")
    exe.chmod(0o755)
    monkeypatch.setenv("NLM_BIN", str(exe))
    result = asyncio.run(GeminiNotebookTransport(tmp_path).run_cli(["nlm", "auth", "status"]))
    assert result["status"] == "failed"
    assert result["exit_code"] == 0


@pytest.mark.parametrize("argv", [["bash","-c","true"], ["nlm","x\x00y"], ["nlm",*(["x"]*101)]])
def test_cli_rejects_wrong_binary_or_unbounded_arguments(tmp_path, argv):
    result = asyncio.run(GeminiNotebookTransport(tmp_path).run_cli(argv))
    assert result["status"] == "blocked"
    assert result["process_executed"] is False
