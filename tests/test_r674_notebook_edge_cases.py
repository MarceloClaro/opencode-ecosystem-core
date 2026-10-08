"""R674: contratos reais de download e estados assíncronos, sem efeitos remotos."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from integrations.gemini_notebook import GeminiNotebookService, validate_notebook_config


class Transport:
    def __init__(self):
        self.calls = []
        self.discovery_calls = 0
        self.payload = {"status": "success"}
        self.writer = None
    async def discover_mcp(self, *args):
        self.discovery_calls += 1
        return {"status": "completed", "tools": [
            {"name": name, "inputSchema": schema} for name, schema in {
                "notebook_list": {"type": "object", "properties": {}},
                "download_artifact": {"type": "object", "properties": {
                    "output_path": {"type": "string"}, "artifact_type": {"type": "string"}}},
                "download_all_artifacts": {"type": "object", "properties": {
                    "output_dir": {"type": "string"}, "notebook_id": {"type": "string"}}},
                "notebook_query_start": {"type": "object", "properties": {
                    "notebook_id": {"type": "string"}, "query": {"type": "string"}}},
                "batch": {"type": "object", "properties": {
                    "action": {"type": "string"}, "confirm": {"type": "boolean"}}},
                "pipeline": {"type": "object", "properties": {
                    "action": {"type": "string"}, "notebook_id": {"type": "string"},
                    "pipeline_name": {"type": "string"}}},
                "studio_create": {"type": "object", "properties": {
                    "artifact_type": {"type": "string"}, "confirm": {"type": "boolean"}}},
            }.items()]}
    async def call_mcp(self, tool, arguments, *args):
        self.calls.append((tool, arguments))
        if self.writer:
            self.writer(arguments)
        return self.reply()
    async def run_cli(self, argv, *args):
        self.calls.append(argv)
        if self.writer:
            self.writer(argv)
        return self.reply()
    def reply(self):
        return {"status": "completed", "process_executed": True,
                "transport_success": True, "business_success": True,
                "result": {"structuredContent": self.payload}}
    def resolve_binary(self, name):
        return None


@pytest.fixture(scope="module")
def catalog():
    from integrations.gemini_notebook_catalog import cli_inventory
    return cli_inventory()


@pytest.fixture
def api(tmp_path, monkeypatch, catalog):
    transport = Transport()
    service = GeminiNotebookService(tmp_path, transport=transport)
    monkeypatch.setattr(service, "_cli_catalog", lambda: catalog)
    return service, transport


def test_normal_cli_vector_is_forwarded_with_executable(api):
    service, transport = api
    result = service.run(operation="cli", argv=["nlm", "notebook", "list", "--json"])
    assert result["status"] == "completed"
    assert transport.calls == [["nlm", "notebook", "list", "--json"]]


@pytest.mark.parametrize("flag", ["-d", "--output-dir", "--output-dir=exports"])
def test_bulk_cli_download_normalizes_every_official_output_alias(api, flag):
    service, transport = api
    def materialize(argv):
        option = next(arg for arg in argv if arg.startswith("--output-dir=") or arg in {"-d", "--output-dir"})
        raw = option.split("=", 1)[1] if "=" in option else argv[argv.index(option) + 1]
        target = Path(raw)
        assert target.is_absolute() and target.is_relative_to(service.output_root)
        (target / "Notebook").mkdir(parents=True)
        (target / "Notebook/report.md").write_bytes(b"report fixture")
    transport.writer = materialize
    args = ["nlm", "download", "all", "nb", flag]
    if "=" not in flag:
        args.append("exports")
    result = service.run(operation="cli", argv=args, confirm=True)
    assert result["status"] == "completed"
    assert result["artifacts"][0]["sha256"] == hashlib.sha256(b"report fixture").hexdigest()


@pytest.mark.parametrize("kind", ["audio", "video", "slide-deck", "infographic", "report",
                                  "mind-map", "data-table", "file", "quiz", "flashcards"])
def test_all_cli_single_artifact_types_remain_inside_output_root(api, kind):
    service, transport = api
    def materialize(argv):
        target = Path(argv[argv.index("-o") + 1])
        assert target.is_absolute() and target.is_relative_to(service.output_root)
        target.write_bytes(b"artifact fixture")
    transport.writer = materialize
    result = service.run(operation="cli", argv=["nlm", "download", kind, "nb", "-o", "artifact.bin"], confirm=True)
    assert result["status"] == "completed" and len(result["artifacts"]) == 1


def test_chat_export_destination_is_normalized(api):
    service, transport = api
    transport.writer = lambda argv: Path(argv[argv.index("-o") + 1]).write_bytes(b"transcript")
    result = service.run(operation="cli", argv=["nlm", "chats", "export", "nb", "-o", "chat.md"], confirm=True)
    assert result["status"] == "completed" and result["artifacts"]


@pytest.mark.parametrize("tool,args", [
    ("download_artifact", {"output_path": "../outside.wav"}),
    ("download_all_artifacts", {"output_dir": "../outside", "notebook_id": "nb"}),
])
def test_bad_mcp_download_path_rejected_before_server(api, tool, args):
    service, transport = api
    with pytest.raises(ValueError):
        service.run(operation="mcp", tool=tool, arguments=args, confirm=True)
    assert transport.discovery_calls == 0 and not transport.calls


def test_output_root_symlink_cannot_escape_workspace(api, tmp_path):
    service, transport = api
    outside = tmp_path.parent / (tmp_path.name + "-outside")
    outside.mkdir()
    service.output_root.parent.mkdir()
    service.output_root.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        service.run(operation="mcp", tool="download_artifact", arguments={"output_path": "audio.wav"}, confirm=True)
    assert not transport.calls


def test_mcp_dry_run_does_not_start_external_server(api):
    service, transport = api
    result = service.run(operation="mcp", tool="notebook_list", dry_run=True)
    assert result["status"] == "prepared"
    assert transport.discovery_calls == 0 and not transport.calls
    assert result["remote_operation_executed"] is False


def test_file_download_cannot_be_satisfied_by_directory(api):
    service, transport = api
    def materialize(arguments):
        target = Path(arguments["output_path"])
        target.mkdir()
        (target / "unrelated.txt").write_bytes(b"unrelated")
    transport.writer = materialize
    result = service.run(operation="mcp", tool="download_artifact", arguments={"output_path": "audio.wav"}, confirm=True)
    assert result["status"] == "failed"


def test_download_symlink_is_not_file_proof(api):
    service, transport = api
    old = service.root / "old.wav"
    old.write_bytes(b"old")
    transport.writer = lambda args: Path(args["output_path"]).symlink_to(old)
    result = service.run(operation="mcp", tool="download_artifact", arguments={"output_path": "audio.wav"}, confirm=True)
    assert result["status"] == "failed"


def test_async_query_status_is_pending_not_completed(api):
    service, transport = api
    transport.payload = {"status": "in_progress", "query_id": "q1"}
    result = service.run(operation="mcp", tool="notebook_query_start",
                         arguments={"notebook_id": "nb", "query": "question"}, confirm=True)
    assert result["status"] == "pending"
    assert result["business_success"] is not True


def test_batch_partial_outcomes_remain_partial(api):
    service, transport = api
    transport.payload = {"status": "success", "succeeded": 1, "failed": 1,
                         "items": [{"success": True}, {"success": False, "error": "failed"}]}
    result = service.run(operation="mcp", tool="batch", arguments={"action": "create"}, confirm=True)
    assert result["status"] == "partial" and result["business_success"] is False


def test_generation_acceptance_is_pending(api):
    service, transport = api
    transport.payload = {"status": "in_progress", "artifact_id": "art"}
    result = service.run(operation="mcp", tool="studio_create",
                         arguments={"artifact_type": "audio", "confirm": True}, confirm=True)
    assert result["status"] == "pending"


def test_generic_pipeline_dry_run_preserves_conservative_effect(api):
    service, transport = api
    args = {"action": "run", "pipeline_name": "user-defined", "notebook_id": "nb"}
    result = service.run(operation="mcp", tool="pipeline", arguments=args, dry_run=True)
    assert result["status"] == "blocked" and result["effect"] == "destructive"
    assert not transport.calls and transport.discovery_calls == 0
    assert args == {"action": "run", "pipeline_name": "user-defined", "notebook_id": "nb"}


def test_false_success_and_auth_expiry_do_not_become_complete(api):
    service, transport = api
    transport.payload = {"status": "expired", "success": False}
    result = service.run(operation="mcp", tool="notebook_list")
    assert result["status"] == "failed" and result["business_success"] is False


@pytest.mark.parametrize("value", ["Bearer abcd", "token=abcd", "eyJabcdefghijk.abcdefghijk.abcdefghijk",
                                  "AIza" + "a" * 24])
def test_credential_shaped_values_rejected_before_effects(value):
    with pytest.raises(ValueError):
        validate_notebook_config({"operation": "mcp", "tool": "source_add", "arguments": {"text": value}})


def test_skill_import_preserves_agents_section(api):
    service, transport = api
    result = service.run(operation="skill")
    assert result["status"] == "prepared"
    assert len(result["files"]) == 8
    assert (service.root / ".opencode/skills/nlm-skill/AGENTS_SECTION.md").is_file()


def test_dry_run_validates_hashed_version_matched_schema_without_server(api):
    service, transport = api
    import asyncio
    service._save_catalog(asyncio.run(transport.discover_mcp()), [])
    transport.discovery_calls = 0
    result = service.run(operation="mcp", tool="notebook_list", dry_run=True)
    assert result["schema_validated"] is True and result["validation_scope"] == "cached_schema"
    assert transport.discovery_calls == 0
    with pytest.raises(ValueError):
        service.run(operation="mcp", tool="notebook_list", arguments={"unknown": 1}, dry_run=True)


def test_tampered_cache_cannot_validate_schema(api):
    service, transport = api
    import asyncio
    saved = service._save_catalog(asyncio.run(transport.discover_mcp()), [])
    path = Path(saved["catalog_path"])
    data = json.loads(path.read_text())
    data["package_version"] = "tampered"
    path.write_text(json.dumps(data))
    result = service.run(operation="mcp", tool="notebook_list", dry_run=True)
    assert result["validation_scope"] == "policy_only"
    assert result["schema_validated"] is False


def test_confirmed_mcp_operation_supplies_official_confirm_parameter(api):
    service, transport = api
    service.run(operation="mcp", tool="studio_create", arguments={"artifact_type": "audio"}, confirm=True)
    assert transport.calls[0][1]["confirm"] is True


def test_contradictory_mcp_confirm_is_rejected_before_call(api):
    service, transport = api
    with pytest.raises(ValueError):
        service.run(operation="mcp", tool="studio_create",
                    arguments={"artifact_type": "audio", "confirm": False}, confirm=True)
    assert not transport.calls


def test_confirmed_cli_operation_supplies_official_confirmation_flag(api):
    service, transport = api
    service.run(operation="cli", argv=["nlm", "audio", "create", "nb"], confirm=True)
    assert "--confirm" in transport.calls[0]


def test_private_session_identifier_is_not_accepted_by_shared_config():
    with pytest.raises(ValueError):
        validate_notebook_config({"operation": "mcp", "tool": "source_add",
                                  "arguments": {"session_id": "private"}})


def test_skill_preserves_upstream_mit_license(api):
    service, transport = api
    result = service.run(operation="skill")
    assert result["license"]["id"] == "MIT"
    license_path = Path(result["license"]["target"])
    assert license_path.read_text().startswith("MIT License")
    assert result["license"]["sha256"] == hashlib.sha256(license_path.read_bytes()).hexdigest()


def test_service_opts_into_persistent_mcp_session(tmp_path):
    service = GeminiNotebookService(tmp_path)
    assert service.transport.persistent is True


def test_pipeline_preview_comes_from_real_builtin_definition(api):
    service, transport = api
    result = service.run(operation="mcp", tool="pipeline", arguments={
        "action": "run", "pipeline_name": "multi-format", "notebook_id": "nb"}, dry_run=True)
    assert result["effect"] == "write"
    assert result["pipeline"]["step_count"] == 3
    assert len(result["pipeline"]["definition_sha256"]) == 64
    assert result["pipeline"]["definition_source"]["kind"] == "builtin"
    assert transport.discovery_calls == 0 and not transport.calls


def test_pipeline_cli_uses_same_builtin_definition_before_execution(api):
    service, transport = api
    result = service.run(operation="cli", argv=["nlm", "pipeline", "run", "multi-format",
                                                "--notebook", "nb"], dry_run=True)
    assert result["effect"] == "write" and result["pipeline"]["step_count"] == 3
    assert not transport.calls


@pytest.mark.parametrize("field", ["steps", "_pipeline_steps"])
def test_caller_cannot_supply_pipeline_steps_as_effect_evidence(api, field):
    service, transport = api
    with pytest.raises(ValueError):
        service.run(operation="mcp", tool="pipeline", arguments={"action": "run",
                    "pipeline_name": "multi-format", "notebook_id": "nb",
                    field: [{"action": "notebook_query", "params": {"query": "pretend read"}}]}, dry_run=True)
    assert not transport.calls and transport.discovery_calls == 0


def test_pipeline_changed_between_preflight_and_dispatch_is_blocked(api, monkeypatch):
    import integrations.gemini_notebook_pipeline as module
    service, transport = api
    plans = iter([{"status": "prepared", "effect": "write", "definition_sha256": "a" * 64,
                   "effective_steps_sha256": "a" * 64, "steps": []},
                  {"status": "prepared", "effect": "write", "definition_sha256": "b" * 64,
                   "effective_steps_sha256": "b" * 64, "steps": []}])
    monkeypatch.setattr(module, "pipeline_preflight", lambda *a, **k: next(plans))
    result = service.run(operation="mcp", tool="pipeline", arguments={
        "action": "run", "pipeline_name": "multi-format", "notebook_id": "nb"}, confirm=True)
    assert result["status"] == "blocked" and result["reason"] == "pipeline_definition_changed"
    assert not transport.calls


def test_cli_configuration_change_resets_volatile_mcp_session(api):
    service, transport = api
    resets = []
    async def close(*args):
        resets.append(True)
        return {"status": "completed"}
    transport.close_persistent = close
    result = service.run(operation="cli", argv=["nlm", "config", "set", "auth.default_profile", "work"], confirm=True)
    assert resets == [True]
    assert result["session_reset"] is True and result["volatile_jobs_may_be_discarded"] is True


def test_cli_read_does_not_discard_pending_jobs(api):
    service, transport = api
    async def close(*args):
        pytest.fail("Leitura não pode encerrar sessão de jobs")
    transport.close_persistent = close
    result = service.run(operation="cli", argv=["nlm", "config", "show"])
    assert result["status"] == "completed" and not result.get("session_reset")
