"""Superfícies coordenadas REA; transportes simulados, sem alvo externo."""
import asyncio
import copy
import json
import pytest


def test_generated_config_connects_rea_and_primary_command():
    from integrations.opencode_cli import build_config
    config = build_config()
    assert "rea" in config["mcp"]
    assert config["mcp"]["rea"] == {
        "type": "local",
        "command": [".venv/bin/python", "-m", "integrations.rea_bridge", "mcp"],
        "enabled": True,
        "timeout": 180000,
    }
    command = config["command"]["rea"]
    assert command["agent"] == "marceloclaro"
    assert "ecosystem_rea" in command["template"] and "$ARGUMENTS" in command["template"]
    assert config["agent"]["marceloclaro"]["tools"]["rea_*"] is False
    assert "catálogo completo" not in command["template"]
    assert config["tools"]["rea_*"] is False


def test_arxiv_launcher_uses_resolved_user_installation(monkeypatch):
    from integrations import opencode_cli
    monkeypatch.setattr(opencode_cli, "_mcp_launcher", lambda name: "/isolated/bin/" + name)
    assert opencode_cli.build_config()["mcp"]["arxiv-mcp"]["command"] == [
        "/isolated/bin/uvx", "arxiv-mcp-server"]


def test_gateway_preserves_complete_evidence_outside_model_context(tmp_path):
    import hashlib
    from marceloclaro.rea_reports import compact_rea_report
    evidence = {"evidence_id": "ev-test", "operation": "analyze_javascript_application",
                "confidence": "derived", "authority": "shipped-artifact",
                "limitations": ["Static analysis does not prove runtime execution"],
                "raw_result": "a" * 200_000,
                "normalized_result": {"statistics": {"parsed_javascript_files": 1},
                                      "graph": {"nodes": [1], "edges": [1, 2]}}}
    response = {"structuredContent": evidence, "content": [{"type": "text", "text": json.dumps(evidence)}]}
    digest = hashlib.sha256(json.dumps(response, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()
    report = {"status": "completed", "success": True, "response": response,
              "provenance": {"response_sha256": digest}, "metacognition": {"persisted": True}}
    compact = compact_rea_report(report, tmp_path)
    artifact = compact["evidence_artifact"]
    assert json.loads(open(artifact["path"]).read()) == response
    assert artifact["sha256"] == digest and artifact["complete"] is True
    assert compact["evidence"]["evidence_id"] == "ev-test"
    assert compact["evidence"]["limitations"] == evidence["limitations"]
    assert compact["evidence"]["statistics"]["parsed_javascript_files"] == 1
    assert len(json.dumps(compact)) < 12_000
    assert compact["metacognition"]["persisted"] is True
    assert "response" not in compact


def test_gateway_catalog_keeps_names_without_all_schemas(tmp_path):
    from marceloclaro.rea_reports import compact_rea_report
    tools = [{"name": f"tool_{i}", "inputSchema": {"description": "x" * 40_000}} for i in range(170)]
    compact = compact_rea_report({"status": "completed", "success": True,
                                  "operation": "catalog", "response": {"tools": tools}}, tmp_path)
    assert compact["tools"] == [f"tool_{i}" for i in range(170)]
    assert len(json.dumps(compact)) < 12_000


def test_gateway_session_preserves_identity_and_supported_tool_availability(tmp_path):
    from marceloclaro.rea_reports import compact_rea_report
    session = {"server_identity": {"package": {"name": "rea-agents", "version": "6.4.0"},
                                   "negotiated_protocol_version": "2025-11-25",
                                   "catalog": {"counts": {"mcp_tools": 170}, "tools": ["x" * 30_000]}},
               "analysis_provider_candidates": [{"provider": {"id": "ghidra"},
                    "availability": {"status": "unavailable", "code": "not_configured"}}],
               "tool_availability": [{"name": "analyze_javascript_application", "available": True,
                                      "reason": "available", "remediation": None}]}
    compact = compact_rea_report({"status": "completed", "success": True, "operation": "session",
                                  "response": {"structuredContent": {"result": session}}}, tmp_path)
    summary = compact["session"]
    assert summary["server_identity"]["package"]["version"] == "6.4.0"
    assert summary["server_identity"]["negotiated_protocol_version"] == "2025-11-25"
    assert summary["providers"][0]["availability"]["status"] == "unavailable"
    assert summary["tool_availability"][0]["available"] is True
    assert len(json.dumps(compact)) < 12_000


@pytest.mark.parametrize("value", [
    {"error": {"code": "provider_failure", "message": "Provider probe failed", "remediation": "Check provider state"}},
    {"result": {}}, {"result": {"server_identity": None}},
])
def test_failed_session_summary_keeps_error_without_inventing_identity(tmp_path, value):
    import hashlib
    from pathlib import Path
    from marceloclaro.rea_reports import compact_rea_report

    response = {"isError": True, "structuredContent": value}
    payload = json.dumps(response, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    digest = hashlib.sha256(payload).hexdigest()
    report = {"operation": "session", "status": "failed", "success": False,
              "error": "REA retornou uma sessão inválida.", "response": response,
              "provenance": {"response_sha256": digest}}
    compact = compact_rea_report(report, tmp_path)
    assert compact["status"] == "failed" and compact["success"] is False
    assert "session" not in compact
    assert compact["session_or_error_summary"] == value
    artifact = compact["evidence_artifact"]
    assert artifact["complete"] is True
    assert Path(artifact["path"]).read_bytes() == payload
    assert artifact["sha256"] == digest


@pytest.mark.parametrize("normalized", [None, {"graph": {"nodes": None}}, {"semantic_graph": None}])
def test_gateway_handles_malformed_upstream_evidence_without_hiding_failure(tmp_path, normalized):
    from marceloclaro.rea_reports import compact_rea_report
    report = {"status": "failed", "success": False,
              "response": {"structuredContent": {"evidence_id": "ev-invalid", "normalized_result": normalized}}}
    compact = compact_rea_report(report, tmp_path)
    assert compact["success"] is False and compact["status"] == "failed"
    assert compact["evidence_artifact"]["complete"] is True
    assert "response" not in compact


def test_orchestrator_records_result_without_confidence_promotion(monkeypatch):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator, metabus
    assert hasattr(MarceloClaroOrchestrator, "rea_action")
    from integrations import rea_bridge

    expected = {"status": "failed", "success": False,
                "provenance": {"repository": "https://github.com/MarceloClaro/rea",
                               "commit": "b" * 40, "version": "6.4.0",
                               "response_sha256": "a" * 64}}
    class Bridge:
        def __init__(self, *args, **kwargs):
            pass
        def action(self, config):
            assert config == {"operation": "session"}
            return copy.deepcopy(expected)
    monkeypatch.setattr(rea_bridge, "ReaBridge", Bridge)
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
    ledger = copy.deepcopy(metabus.memory.confidence_ledger)
    result = orchestrator.rea_action({"operation": "session"})
    assert result["status"] == "failed" and result["success"] is False
    assert result["metacognition"]["persisted"] is True
    assert result["metacognition"]["confidence_promoted"] is False
    assert result["metacognition"]["externally_validated"] is False
    assert metabus.memory.confidence_ledger == ledger
    entry = next(row for row in metabus.memory.episodic
                 if row["id"] == result["metacognition"]["observation_id"])
    assert entry["observation"]["response_sha256"] == "a" * 64
    semantic = metabus.memory.semantic["ecosystem.rea." + result["metacognition"]["scope_id"]]
    assert semantic["metadata"]["last_report_sha256"] == "a" * 64


def test_mcp_routes_to_primary_and_preserves_failure(monkeypatch):
    from integrations import ecosystem_mcp
    assert hasattr(ecosystem_mcp, "ecosystem_rea")
    calls = []
    class Primary:
        def rea_action(self, config):
            calls.append(config)
            return {"status": "unavailable", "success": False}
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: Primary())
    result = asyncio.run(ecosystem_mcp.ecosystem_rea({"operation": "catalog"}))
    assert calls == [{"operation": "catalog"}]
    assert result == {"status": "unavailable", "success": False}
    names = {tool.name for tool in asyncio.run(ecosystem_mcp.mcp.list_tools())}
    assert "ecosystem_rea" in names


def test_cli_returns_failure_and_does_not_load_catalog(monkeypatch, capsys):
    from marceloclaro import cli
    calls = []
    class Primary:
        def __init__(self, **kwargs):
            assert kwargs == {"auto_load_agents": False}
        def rea_action(self, config):
            calls.append(config)
            return {"status": "unavailable", "success": False}
    monkeypatch.setattr(cli, "MarceloClaroOrchestrator", Primary)
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "rea", "analyze", "/tmp/app", "--timeout", "30"])
    assert cli.main() == 1
    assert calls == [{"operation": "analyze", "path": "/tmp/app", "timeout_seconds": 30.0}]
    assert json.loads(capsys.readouterr().out)["success"] is False


def test_cli_rejects_unknown_operation_before_starting_process(monkeypatch):
    from marceloclaro import cli
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "rea", "execute"])
    assert cli.main() == 2


def test_doctor_reports_rea_without_claiming_live_execution(monkeypatch):
    from marceloclaro import doctor
    assert hasattr(doctor, "_check_rea")
    from integrations import rea_bridge
    class Bridge:
        def status(self, *, include_commit=True):
            return {"status": "ready", "success": True,
                    "provenance": {"version": "6.4.0"}}
    monkeypatch.setattr(rea_bridge, "ReaBridge", Bridge)
    result = doctor._check_rea()
    assert result.name == "rea" and result.status == "pass"
    assert "6.4.0" in result.detail and "MCP" in result.detail
