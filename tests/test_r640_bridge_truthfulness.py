"""R640: inventário e previews não comprovam sincronização ou execução."""

from integrations.cli_ecosystem_bridge import CliEcosystemBridge


def runtime_state(**installed):
    return {"executors": {name: {"installed": present, "available": present and name != "opencode", "path": f"/bin/{name}" if present else None, "cli": "agy" if name == "antigravity" else name, "execution_mode": "cli-read-only", "verification": "installation_only", "reason": "Instalação somente"} for name, present in installed.items()}}


def test_instruction_files_cannot_mark_missing_clis_installed(tmp_path, monkeypatch):
    for name in ("opencode.json", "CLAUDE.md", "AGENTS.md"):
        (tmp_path / name).write_text("{}", encoding="utf-8")
    monkeypatch.setattr("integrations.harness_runtime.HarnessRuntime.status", lambda self: runtime_state(opencode=False, claude=False, antigravity=False, codex=False))
    capabilities = CliEcosystemBridge(str(tmp_path)).discover_cli_capabilities()
    assert capabilities["opencode_codex"]["config_present"]
    assert capabilities["claude_code"]["config_present"]
    assert not any(info["active"] for info in capabilities.values())
    assert not capabilities["codex_cli"]["installed"]


def test_opencode_installation_is_distinct_from_codex(tmp_path, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.HarnessRuntime.status", lambda self: runtime_state(opencode=True, claude=False, antigravity=False, codex=False))
    capabilities = CliEcosystemBridge(str(tmp_path)).discover_cli_capabilities()
    assert capabilities["opencode_codex"]["cli"] == "opencode"
    assert capabilities["opencode_codex"]["label"] == "OpenCode CLI (chave legada opencode_codex)"
    assert capabilities["opencode_codex"]["active"]
    assert not capabilities["codex_cli"]["active"]


def test_export_methods_report_preview_without_creating_files(tmp_path):
    bridge = CliEcosystemBridge(str(tmp_path))
    cards = bridge.export_agent_cards_to_claude()
    skills = bridge.export_skills_to_antigravity()
    assert cards["status"] == "preview_only"
    assert cards["executed"] is False
    assert cards["written_count"] == cards["total_exported"] == 0
    assert cards["preview_count"] == len(cards["agents_preview"])
    assert skills["status"] == "inventory_only"
    assert skills["executed"] is False and skills["written_count"] == 0
    assert not skills.get("supported_sidecars")
    assert list(tmp_path.iterdir()) == []


def test_all_installed_never_claims_sync_or_execution(tmp_path, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.HarnessRuntime.status", lambda self: runtime_state(opencode=True, claude=True, antigravity=True, codex=True))
    state = CliEcosystemBridge(str(tmp_path)).get_unified_status()
    assert state["unified_status"] == "installed_unverified"
    assert state["missing"] == []
    assert state["execution_verified"] is False
    assert state["network_mcp_path"].endswith("integrations/ecosystem_mcp.py")


def test_absent_codex_is_reported_even_when_opencode_installed(tmp_path, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.HarnessRuntime.status", lambda self: runtime_state(opencode=True, claude=True, antigravity=True, codex=False))
    state = CliEcosystemBridge(str(tmp_path)).get_unified_status()
    assert state["unified_status"] == "partially_installed"
    assert state["missing"] == ["codex_cli"]
    assert state["execution_verified"] is False
