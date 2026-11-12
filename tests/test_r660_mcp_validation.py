"""R660: validação completa e ausência de efeitos em entradas MCP inválidas."""

import asyncio
import json
from unittest.mock import Mock, patch

import pytest


SCHEMA = {
    "type": "object",
    "properties": {
        "items": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "count": {"type": "integer", "minimum": 1, "maximum": 3},
        "mode": {"type": "string", "enum": ["safe", "fast"]},
        "nested": {
            "type": "object", "properties": {"label": {"type": "string", "minLength": 2}},
            "required": ["label"], "additionalProperties": False,
        },
    },
    "required": ["items"],
    "additionalProperties": False,
}

INVALID_ARGUMENTS = [
    {}, {"items": [1]}, {"items": []}, {"items": ["ok"], "count": 0},
    {"items": ["ok"], "count": 4}, {"items": ["ok"], "count": True},
    {"items": ["ok"], "mode": "secret-value"},
    {"items": ["ok"], "nested": {}}, {"items": ["ok"], "nested": {"label": None}},
    {"items": ["ok"], "nested": {"label": "x"}},
    {"items": ["ok"], "extra": "secret-value"},
]


@pytest.mark.parametrize("arguments", INVALID_ARGUMENTS)
def test_guard_validates_entire_schema(arguments):
    from synthetic_university.mcp_security import MCPGuard
    result = MCPGuard.validate("probe", arguments, SCHEMA)
    assert result["valid"] is False
    assert result["errors"]
    assert "secret-value" not in str(result["errors"])


def test_common_helper_accepts_local_reference_and_integral_float():
    from integrations.mcp_validation import validate_arguments
    schema = {"type": "object", "$defs": {"count": {"type": "integer", "minimum": 1}},
              "properties": {"count": {"$ref": "#/$defs/count"}}}
    result = validate_arguments("probe", {"count": 1.0}, schema)
    assert result == {"valid": True, "errors": [], "tool": "probe", "args": {"count": 1.0}}


def test_reference_word_in_literal_data_is_not_an_external_schema_reference():
    from integrations.mcp_validation import validate_arguments
    schema = {"type": "object", "properties": {"literal": {"const": {"$ref": "https://example.invalid"}}}}
    assert validate_arguments("probe", {"literal": {"$ref": "https://example.invalid"}}, schema)["valid"] is True


@pytest.mark.parametrize("schema", [
    {"type": "unknown"},
    {"type": "object", "properties": {"item": {"$ref": "https://invalid.example/schema"}}},
    {"type": "object", "properties": {"item": {"$ref": "other.json#/item"}}},
    {"type": "object", "$dynamicRef": "https://invalid.example/schema"},
    {"type": "object", "properties": {"count": {"type": "number", "maximum": float("inf")}}},
])
def test_schema_errors_fail_closed_without_network(schema):
    from integrations.mcp_validation import validate_arguments
    with patch("urllib.request.urlopen", side_effect=AssertionError("network forbidden")) as network:
        result = validate_arguments("probe", {}, schema)
    assert result["valid"] is False
    network.assert_not_called()


@pytest.mark.parametrize("number", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_numbers_rejected_even_without_schema(number):
    from integrations.mcp_validation import validate_arguments
    assert validate_arguments("probe", {"nested": [number]}, None)["valid"] is False


@pytest.mark.parametrize("kind", ["mci", "su", "su_guard"])
@pytest.mark.parametrize("arguments", INVALID_ARGUMENTS)
def test_simple_servers_reject_before_handler(kind, arguments):
    from mci.mcp_server import SimpleMCPServer as MciServer
    from synthetic_university.mcp_server import SimpleMCPServer as SuServer
    from synthetic_university.mcp_security import MCPGuard
    server = MciServer("probe") if kind == "mci" else SuServer(
        "probe", security={"guard": MCPGuard()} if kind == "su_guard" else None,
    )
    handler = Mock(return_value={"ok": True})
    server.register_tool("probe", "Probe", SCHEMA, handler)
    request = {"method": "tools/call", "params": {"name": "probe", "arguments": arguments}}
    result = asyncio.run(server.handle_request(request)) if kind == "mci" else server.handle_sync(request)
    assert result["isError"] is True
    handler.assert_not_called()


def test_su_invalid_schema_does_not_consume_limiter():
    from synthetic_university.mcp_server import SimpleMCPServer
    limiter = Mock()
    server = SimpleMCPServer("probe", security={"limiter": limiter})
    handler = Mock(return_value={"ok": True})
    server.register_tool("probe", "Probe", SCHEMA, handler)
    result = server.handle_sync({"method": "tools/call", "params": {"name": "probe", "arguments": {}}})
    assert result["isError"] is True
    limiter.allow.assert_not_called()
    handler.assert_not_called()


@pytest.mark.parametrize("variant", ["async", "sync"])
def test_scanners_required_field_rejected_before_audit(variant):
    from scanners.scanners_mcp_server import call_tool, ScannersMcpServer
    with patch("scanners.scanners_mcp_server.super_rigor_pipeline.audit_production") as audit:
        result = asyncio.run(call_tool("super_rigor_audit", {})) if variant == "async" else ScannersMcpServer().call_tool("super_rigor_audit", {})
    assert result.isError if variant == "async" else result["ok"] is False
    audit.assert_not_called()


@pytest.mark.parametrize("arguments", [
    {}, {"prompt": "ok", "max_tokens": True}, {"prompt": "ok", "max_tokens": 0},
    {"prompt": "ok", "max_tokens": 2.0}, {"prompt": "", "max_tokens": 2},
    {"prompt": "ok", "temperature": 9},
])
def test_colibri_invalid_input_rejected_before_provider(arguments):
    from integrations.colibri import colibri_mcp_server as colibri
    with patch.object(colibri.ColibriBridge, "complete") as complete:
        result = colibri.handle_request({
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "colibri:complete", "arguments": arguments},
        })
    assert result["error"]["code"] == -32602
    complete.assert_not_called()


@pytest.mark.parametrize("success", [True, False])
def test_colibri_uses_real_provider_contract_and_propagates_failure(success):
    from integrations.colibri import colibri_mcp_server as colibri
    provider_result = {"status": "ok" if success else "error",
                       "content": "answer" if success else "",
                       "error": "" if success else "offline"}
    with patch.object(colibri.ColibriBridge, "complete", return_value=provider_result) as complete:
        result = colibri.handle_request({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "colibri:complete",
                       "arguments": {"prompt": "probe", "max_tokens": 2}},
        })
    complete.assert_called_once_with(prompt="probe", system=None,
                                     max_tokens=2, temperature=0.7)
    assert result["result"]["isError"] is (not success)
    if success:
        assert result["result"]["content"][0]["text"] == "answer"


def test_colibri_reports_unavailable_provider_as_error():
    from integrations.colibri import colibri_mcp_server as colibri
    with patch.object(colibri.ColibriBridge, "complete",
                      return_value={"status": "unavailable", "reason": "offline"}) as complete:
        result = colibri.handle_request({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "colibri:complete",
                       "arguments": {"prompt": "probe", "max_tokens": 512}},
        })
    assert result["result"]["isError"] is True
    complete.assert_called_once_with(prompt="probe", system=None,
                                     max_tokens=512, temperature=0.7)


def test_mci_memory_range_and_integral_float_are_adapted():
    from mci.mcp_server import mci_server
    with patch("mci.mcp_server.metabus.memory.get_recent_context", return_value=[]) as memory:
        for value in [True, -1, 1001]:
            result = asyncio.run(mci_server.handle_request({"method": "tools/call", "params": {"name": "mci_get_memory", "arguments": {"limit": value}}}))
            assert result["isError"] is True
        memory.assert_not_called()
        result = asyncio.run(mci_server.handle_request({"method": "tools/call", "params": {"name": "mci_get_memory", "arguments": {"limit": 2.0}}}))
    assert result.get("isError") is not True
    memory.assert_called_once_with(2)


@pytest.mark.parametrize("name,arguments", [
    ("mci_register_agent", {"agent_id": "probe", "name": "Probe", "capabilities": [123]}),
    ("mci_post_task", {"description": "Probe", "required_capabilities": [123]}),
])
def test_mci_invalid_payload_never_publishes(name, arguments):
    from mci.mcp_server import mci_server
    with patch("mci.mcp_server.metabus.publish") as publish:
        result = asyncio.run(mci_server.handle_request({"method": "tools/call", "params": {"name": name, "arguments": arguments}}))
    assert result["isError"] is True
    publish.assert_not_called()
