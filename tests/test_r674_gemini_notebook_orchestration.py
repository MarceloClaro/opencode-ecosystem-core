"""Contraprovas do contrato central; nenhum efeito remoto nos testes."""
import asyncio
import json
from unittest.mock import Mock

import pytest

from integrations.gemini_notebook import GeminiNotebookService, validate_notebook_config


class Transport:
    def __init__(self):
        self.calls = []
        self.reply = {"status": "completed", "process_executed": True,
                      "result": {"content": []}, "response_sha256": "a" * 64}

    async def discover_mcp(self, timeout_seconds=60):
        return {"status": "completed", "process_executed": True, "name": "official",
                "version": "0.11.6", "tools": [
                    {"name": "notebook_list", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "batch", "inputSchema": {"type": "object", "properties": {
                        "action": {"type": "string"}, "artifact_type": {"type": "string"}}}},
                    {"name": "download_artifact", "inputSchema": {"type": "object", "properties": {
                        "output_path": {"type": "string"}}}},
                    {"name": "save_auth_tokens", "inputSchema": {"type": "object", "properties": {}}}]}

    async def call_mcp(self, tool_name, arguments, timeout_seconds=60):
        self.calls.append((tool_name, arguments))
        return self.reply.copy()

    async def run_cli(self, argv, timeout_seconds=60):
        self.calls.append(tuple(argv))
        return self.reply.copy()

    def resolve_binary(self, name):
        return None


def service(tmp_path):
    transport = Transport()
    return GeminiNotebookService(tmp_path, transport=transport), transport


@pytest.mark.parametrize("config", [
    {}, {"operation": "unknown"}, {"operation": "status", "argv": ["nlm"]},
    {"operation": "mcp", "tool": "notebook_list", "arguments": [],},
    {"operation": "mcp", "tool": "notebook_list", "confirm": "true"},
    {"operation": "mcp", "tool": "notebook_list", "timeout_seconds": float("nan")},
    {"operation": "mcp", "tool": "notebook_list", "timeout_seconds": True},
    {"operation": "mcp", "tool": "notebook_list", "timeout_seconds": 301},
    {"operation": "cli", "argv": "nlm notebook list"},
    {"operation": "cli", "argv": ["bash", "-c", "x"]},
    {"operation": "cli", "argv": ["nlm", "notebook\x00"]},
    {"operation": "mcp", "tool": "notebook_list", "arguments": {"cookie": "SECRET"}},
    {"operation": "cli", "argv": ["nlm", "login", "--cookies", "SECRET"]},
    {"operation": "mcp", "tool": "notebook_list", "profile": "other"},
])
def test_invalid_requests_rejected_before_side_effects(config):
    with pytest.raises(ValueError):
        validate_notebook_config(config)


def test_read_uses_actual_schema_and_official_transport(tmp_path):
    api, transport = service(tmp_path)
    result = api.run(operation="mcp", tool="notebook_list")
    assert result["status"] == "completed"
    assert transport.calls == [("notebook_list", {})]


def test_unknown_argument_not_sent_upstream(tmp_path):
    api, transport = service(tmp_path)
    with pytest.raises(ValueError):
        api.run(operation="mcp", tool="notebook_list", arguments={"invented": True})
    assert not transport.calls


def test_preflight_rejects_unknown_fields_inside_referenced_objects():
    schema = {"type": "object", "properties": {"item": {"$ref": "#/$defs/Entry"}},
              "$defs": {"Entry": {"type": "object", "properties": {"title": {"type": "string"}}}}}
    with pytest.raises(ValueError):
        GeminiNotebookService._validate_schema({"item": {"title": "ok", "invented": True}}, schema)


def test_disabled_tool_not_sent(tmp_path):
    api, transport = service(tmp_path)
    result = api.run(operation="mcp", tool="notebook_create", arguments={}, confirm=True)
    assert result["status"] == "blocked" and not transport.calls


def test_hidden_batch_studio_requires_confirmation(tmp_path):
    api, transport = service(tmp_path)
    result = api.run(operation="mcp", tool="batch", arguments={"action": "studio", "artifact_type": "audio"})
    assert result["status"] == "blocked" and not transport.calls


def test_dry_run_never_calls_tool_even_when_confirmed(tmp_path):
    api, transport = service(tmp_path)
    result = api.run(operation="mcp", tool="batch", arguments={"action": "studio"}, confirm=True, dry_run=True)
    assert result["status"] == "prepared" and not transport.calls


def test_private_auth_not_captured(tmp_path):
    api, transport = service(tmp_path)
    result = api.run(operation="mcp", tool="save_auth_tokens", confirm=True)
    assert result["status"] == "blocked" and not transport.calls


def test_download_cannot_escape_workspace(tmp_path):
    api, transport = service(tmp_path)
    with pytest.raises(ValueError):
        api.run(operation="mcp", tool="download_artifact", arguments={"output_path": "../escape.wav"}, confirm=True)
    assert not transport.calls


def test_success_without_download_is_failure(tmp_path):
    api, transport = service(tmp_path)
    result = api.run(operation="mcp", tool="download_artifact", arguments={"output_path": "audio.wav"}, confirm=True)
    assert result["status"] == "failed"


def test_download_requires_nonempty_file_and_reports_hash(tmp_path):
    api, transport = service(tmp_path)
    target = tmp_path / "outputs/gemini-notebook/audio.wav"
    target.parent.mkdir(parents=True)
    async def download(tool_name, arguments, timeout_seconds=60):
        target.write_bytes(b"real fixture bytes")
        return transport.reply.copy()
    transport.call_mcp = download
    result = api.run(operation="mcp", tool="download_artifact", arguments={"output_path": "audio.wav"}, confirm=True)
    assert result["status"] == "completed" and len(result["artifacts"][0]["sha256"]) == 64


def test_existing_download_cannot_satisfy_new_execution(tmp_path):
    api, transport = service(tmp_path)
    target = tmp_path / "outputs/gemini-notebook/audio.wav"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"old")
    with pytest.raises(ValueError):
        api.run(operation="mcp", tool="download_artifact", arguments={"output_path": "audio.wav"}, confirm=True)
    assert not transport.calls


def test_central_method_records_only_operational_receipt(monkeypatch, tmp_path):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    reply = {"status": "completed", "result": {"private_text": "PRIVATE"},
             "response_sha256": "a" * 64, "process_executed": True}
    monkeypatch.setattr(GeminiNotebookService, "run", lambda self, **kwargs: reply.copy())
    core = object.__new__(MarceloClaroOrchestrator)
    recorded = Mock(return_value={"persisted": True})
    core._record_knowledge_outcome = recorded
    result = core.gemini_notebook_action(operation="mcp", tool="notebook_list")
    assert result["metacognition"]["confidence_promoted"] is False
    assert "PRIVATE" not in json.dumps(recorded.call_args.args)
    assert "arguments" not in recorded.call_args.args[2]
    assert len(recorded.call_args.args[2]["request_sha256"]) == 64


def test_mcp_rejects_input_before_constructing_orchestrator(monkeypatch):
    from integrations import ecosystem_mcp as surface
    forbidden = Mock(side_effect=AssertionError("unexpected initialization"))
    monkeypatch.setattr(surface, "get_library_orchestrator", forbidden)
    with pytest.raises(ValueError):
        asyncio.run(surface.ecosystem_gemini_notebook({"operation": "invalid"}))
    forbidden.assert_not_called()


def test_science_cli_routes_notebook(tmp_path, capsys):
    from marceloclaro.science_cli import run_science_cli
    config = tmp_path / "request.json"
    config.write_text('{"operation":"status"}')
    core = Mock()
    core.gemini_notebook_action.return_value = {"status": "completed"}
    assert run_science_cli(["notebook", "--config", str(config)], core) == 0
    core.gemini_notebook_action.assert_called_once_with(operation="status")


def test_cli_job_loss_returns_failure(tmp_path, capsys):
    from marceloclaro.science_cli import run_science_cli
    config = tmp_path / "request.json"
    config.write_text('{"operation":"mcp","tool":"notebook_query_status","arguments":{"query_id":"job"}}')
    core = Mock()
    core.gemini_notebook_action.return_value = {"status": "lost"}
    assert run_science_cli(["notebook", "--config", str(config)], core) == 1
