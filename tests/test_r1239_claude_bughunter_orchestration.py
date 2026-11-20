"""R1239: catálogo fechado e rota defensiva sob MarceloClaro; sem Burp runtime."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_catalog_validates_pinned_provenance_and_exposes_only_safe_route():
    from integrations.claude_bughunter_catalog import load_catalog

    catalog = load_catalog(ROOT)
    assert catalog["schema_version"] == "r1239.v1"
    assert catalog["orchestrator"] == "marceloclaro"
    assert catalog["status"] == "reference_only"
    package = catalog["package"]
    assert package["repository"] == "elementalsouls/Claude-BugHunter"
    assert package["commit"] == "0e70a021e59d6875004e7a563f8511aca2ba3bc1"
    assert package["archive_sha256"] == (
        "17d47b16d6db7214ebeb80565cd471f558f876efaff5a2fee1f6f718f498e371"
    )
    assert package["snapshot_file_count"] == 341
    assert package["upstream_skill_count"] == 83
    assert package["upstream_command_count"] == 15
    assert catalog["entries"] == [
        {
            "id": "claude-bughunter-safe",
            "kind": "first_party_skill",
            "path": ".opencode/skills/claude-bughunter-safe/SKILL.md",
            "policy": "defensive_review_only",
            "invocation": "explicit",
            "executed": False,
        }
    ]
    serialized = json.dumps(catalog, ensure_ascii=False).casefold()
    assert "skill_index.json" not in serialized
    assert "upstream_skill_descriptions" not in catalog
    assert "upstream_commands" not in catalog


def test_catalog_fails_closed_when_package_manifest_is_tampered(tmp_path):
    from integrations.claude_bughunter_catalog import load_catalog

    federation = tmp_path / "federation"
    federation.mkdir()
    for filename in (
        "claude-bughunter-package-r1236.json",
        "claude-bughunter-mcp-r1239.json",
    ):
        (federation / filename).write_bytes((ROOT / "federation" / filename).read_bytes())
    (tmp_path / "external/claude-bughunter-snapshot").mkdir(parents=True)
    local_skill = tmp_path / ".opencode/skills/claude-bughunter-safe/SKILL.md"
    local_skill.parent.mkdir(parents=True)
    local_skill.write_text("local safe skill", encoding="utf-8")

    manifest_path = federation / "claude-bughunter-package-r1236.json"
    tampered = json.loads(manifest_path.read_text(encoding="utf-8"))
    tampered["source"]["commit"] = "f" * 40
    manifest_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="proveniência|commit|manifesto"):
        load_catalog(tmp_path)

    manifest_path.write_bytes((ROOT / "federation/claude-bughunter-package-r1236.json").read_bytes())
    burp_path = federation / "claude-bughunter-mcp-r1239.json"
    tampered_burp = json.loads(burp_path.read_text(encoding="utf-8"))
    tampered_burp["enabled"] = True
    burp_path.write_text(json.dumps(tampered_burp), encoding="utf-8")
    with pytest.raises(ValueError, match="Burp MCP|fail-closed|estado"):
        load_catalog(tmp_path)


def test_status_and_plan_are_exposed_through_marcelo_claro():
    from marceloclaro.integration_service import CoreIntegrationService
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    class Registry:
        def inventory(self):
            return {"by_kind": {}, "ecosystems_present": [], "ecosystems_missing": []}

    service = CoreIntegrationService(ROOT, registry=Registry())
    orchestrator = MarceloClaroOrchestrator.__new__(MarceloClaroOrchestrator)
    orchestrator._integration_service = service

    status = orchestrator.integration_status()
    assert status["orchestrator"] == "marceloclaro"
    assert status["reference_packages"]["claude_bughunter"]["status"] == "reference_only"
    plan = orchestrator.claude_bughunter_plan()
    assert plan["orchestrator"] == "marceloclaro"
    assert plan["status"] == "instruction_only"
    assert plan["route"]["id"] == "claude-bughunter-safe"
    assert plan["skill_plan"]["found"] is True
    assert plan["executed"] is plan["execution_verified"] is False
    assert plan["burp_mcp"]["enabled"] is False
    assert plan["burp_mcp"]["target_testing_authorized"] is False


def test_cli_and_mcp_plan_dispatch_only_to_primary_orchestrator(monkeypatch, capsys):
    from integrations import ecosystem_mcp
    from marceloclaro.integration_cli import run_integration_cli

    class OrchestratorSpy:
        def __init__(self):
            self.calls = 0

        def claude_bughunter_plan(self):
            self.calls += 1
            return {
                "status": "instruction_only",
                "orchestrator": "marceloclaro",
                "executed": False,
                "execution_verified": False,
            }

    orchestrator = OrchestratorSpy()
    assert run_integration_cli(["bughunter"], orchestrator=orchestrator) == 0
    assert json.loads(capsys.readouterr().out)["orchestrator"] == "marceloclaro"
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: orchestrator)
    result = asyncio.run(ecosystem_mcp.ecosystem_claude_bughunter_plan())
    assert result["status"] == "instruction_only"
    assert orchestrator.calls == 2
    from integrations.opencode_cli import build_config
    generated = build_config()
    assert "ecosystem_claude_bughunter_plan" in generated["command"]["integracoes"]["template"]
    assert "burp" not in json.dumps(generated.get("mcp", {}), ensure_ascii=False).casefold()


def test_official_burp_mcp_authorization_is_recorded_but_prerequisites_block_enablement():
    readiness = json.loads(
        (ROOT / "federation/claude-bughunter-mcp-r1239.json").read_text(encoding="utf-8")
    )
    assert readiness["schema_version"] == "r1239.burp.v1"
    assert readiness["provider"] == "portswigger-official"
    assert readiness["authorization_granted"] is True
    assert readiness["endpoint"] == "http://127.0.0.1:9876"
    assert readiness["transport"] == "stdio_proxy_to_local_sse"
    assert readiness["status"] == "blocked_missing_local_runtime"
    assert readiness["enabled"] is False
    assert readiness["opencode_server_configured"] is False
    assert readiness["observed_prerequisites"] == {
        "java_executable_found": False,
        "proxy_jar_found_in_search_roots": False,
        "burp_directories_found_under_home": False,
    }
    assert readiness["observation"]["scope_is_comprehensive"] is False
    assert readiness["burp_started"] is False
    assert readiness["mcp_connected"] is False
    assert readiness["http_requests_sent"] is False
    assert readiness["target_testing_authorized"] is False


def test_no_burp_server_or_target_testing_is_claimed():
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert "burp" not in json.dumps(config, ensure_ascii=False).casefold()

    from integrations.claude_bughunter_catalog import load_catalog

    result = load_catalog(ROOT)["burp_mcp"]
    assert result["authorization_granted"] is True
    assert result["enabled"] is False
    assert result["opencode_server_configured"] is False
    assert result["http_requests_sent"] is False
    assert result["target_testing_authorized"] is False
