"""R662: integração real de interfaces; executores externos ficam fora destes testes."""
import asyncio
import json
import pytest


class Registry:
    def __init__(self):
        self.calls = []

    def inventory(self):
        return {"total": 2, "by_kind": {"skill": 1, "plugin": 1},
                "ecosystems_present": ["codex"], "ecosystems_missing": []}

    def plan_handoff(self, artifact_id):
        self.calls.append(artifact_id)
        return {"artifact_id": artifact_id, "found": True, "status": "ready",
                "executed": False, "execution_verified": False}


def fixture_repo(tmp_path):
    (tmp_path / "AGENTS.md").write_text("instruções", encoding="utf-8")
    (tmp_path / "agent.md").write_text("agente", encoding="utf-8")
    (tmp_path / "server.py").write_text("raise RuntimeError('NÃO EXECUTAR')", encoding="utf-8")
    config = {"default_agent": "marceloclaro", "instructions": ["AGENTS.md"],
              "agent": {"marceloclaro": {"mode": "primary", "prompt": "{file:./agent.md}"}},
              "command": {"integracoes": {"agent": "marceloclaro"}},
              "mcp": {"local": {"type": "local", "enabled": True,
                                "command": ["python3", "server.py"]}}}
    (tmp_path / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    return config


def service(tmp_path):
    from marceloclaro.integration_service import CoreIntegrationService
    return CoreIntegrationService(tmp_path, registry=Registry())


def test_status_covers_six_components_without_claiming_execution(tmp_path):
    fixture_repo(tmp_path)
    result = service(tmp_path).status()
    assert result["status"] == "config_checked"
    assert set(result["components"]) == {"agents", "hooks", "mcp", "cli", "plugins", "skills"}
    assert result["execution_verified"] is False
    assert result["components"]["agents"]["configured_count"] == 1
    assert result["components"]["plugins"]["count"] == 1


def test_config_detects_broken_agent_and_file_before_any_execution(tmp_path):
    config = fixture_repo(tmp_path)
    config["command"]["integracoes"]["agent"] = "inexistente"
    config["mcp"]["local"]["command"][1] = "missing.py"
    (tmp_path / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    result = service(tmp_path).status()
    assert result["status"] == "error"
    assert {issue["code"] for issue in result["issues"]} >= {"command_agent_missing", "mcp_entry_missing"}
    assert result["executed"] is False


@pytest.mark.parametrize("config", [[], None, {"agent": []}, {"mcp": []}, {"instructions": "x"},
                                     {"default_agent": []}, {"agent": {"a": {}}, "command": {"x": {"agent": []}}}])
def test_malformed_configuration_is_not_reported_as_ready(tmp_path, config):
    (tmp_path / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    assert service(tmp_path).status()["status"] == "error"


def test_repository_reference_cannot_escape_root(tmp_path):
    config = fixture_repo(tmp_path)
    outside = tmp_path.parent / "outside-r662.md"
    outside.write_text("fora", encoding="utf-8")
    config["agent"]["marceloclaro"]["prompt"] = "{file:../outside-r662.md}"
    (tmp_path / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    result = service(tmp_path).status()
    assert "reference_outside_repository" in {i["code"] for i in result["issues"]}


def test_handoff_uses_registered_artifact_and_rejects_path(tmp_path):
    current = service(tmp_path)
    assert current.handoff("codex:skill:user:example")["found"]
    assert current.registry.calls == ["codex:skill:user:example"]
    with pytest.raises(ValueError):
        current.handoff("../../secret")
    assert len(current.registry.calls) == 1


def test_skill_plan_reads_policy_and_is_instruction_only(tmp_path, monkeypatch):
    monkeypatch.delenv("REVERSA_SKILLS_ROOT", raising=False)
    skill = tmp_path / ".opencode/skills/restrita"
    skill.mkdir(parents=True)
    document = "---\nname: restrita\ndisable-model-invocation: true\n---\nLeia a referência local.\n"
    (skill / "SKILL.md").write_text(document, encoding="utf-8")
    result = service(tmp_path).skill_plan("restrita")
    assert result["found"] is True
    assert result["execution_mode"] == "read-and-execute"
    assert result["skill_document"] == document
    assert len(result["source_file_sha256"]) == 64
    assert result["executed"] is result["execution_verified"] is False


class OrchestratorSpy:
    def __init__(self):
        self.calls = []

    def integration_status(self):
        self.calls.append(("status",))
        return {"status": "config_checked", "executed": False}

    def integration_handoff(self, artifact_id):
        self.calls.append(("handoff", artifact_id))
        return {"status": "ready", "executed": False}

    def integration_skill_plan(self, skill_name):
        self.calls.append(("skill", skill_name))
        return {"status": "instruction_only", "found": True, "executed": False}


def test_cli_and_mcp_delegate_to_same_orchestrator(monkeypatch, capsys):
    from marceloclaro.integration_cli import run_integration_cli
    from integrations import ecosystem_mcp as surface
    orch = OrchestratorSpy()
    monkeypatch.setattr(surface, "get_library_orchestrator", lambda: orch)
    assert run_integration_cli(["status"], orchestrator=orch) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "config_checked"
    assert asyncio.run(surface.ecosystem_integration_status())["executed"] is False
    assert run_integration_cli(["handoff", "codex:skill:user:example"], orchestrator=orch) == 0
    assert asyncio.run(surface.ecosystem_artifact_handoff("codex:skill:user:example"))["status"] == "ready"
    assert run_integration_cli(["skill", "restrita"], orchestrator=orch) == 0
    assert asyncio.run(surface.ecosystem_skill_plan("restrita"))["found"]
    assert orch.calls == [("status",), ("status",), ("handoff", "codex:skill:user:example"),
                          ("handoff", "codex:skill:user:example"), ("skill", "restrita"), ("skill", "restrita")]


def test_cli_rejects_unknown_flags_before_constructing_orchestrator(capsys):
    from marceloclaro.integration_cli import run_integration_cli
    assert run_integration_cli(["status", "--execute"]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_slash_command_uses_primary_and_read_only_tools():
    from integrations.opencode_cli import build_config
    command = build_config()["command"]["integracoes"]
    assert command["agent"] == "marceloclaro"
    assert "ecosystem_integration_status" in command["template"]
    assert "ecosystem_artifact_handoff" in command["template"]


def test_local_mcp_launchers_use_project_runtime_and_resolve_fetch(monkeypatch):
    from integrations import opencode_cli
    from integrations.harness_runtime import HarnessRuntime
    monkeypatch.setattr(HarnessRuntime, "resolve_cli_path", lambda self, name: "/isolated/bin/" + name)
    config = opencode_cli.build_config()
    for name, server in config["mcp"].items():
        if any(arg.endswith(".py") for arg in server["command"]):
            assert server["command"][0] == ".venv/bin/python", name
    assert config["mcp"]["fetch"]["command"][0] == "/isolated/bin/uvx"


def test_mcp_rejects_bad_handoff_before_orchestrator(monkeypatch):
    from integrations import ecosystem_mcp as surface
    monkeypatch.setattr(surface, "get_library_orchestrator", lambda: pytest.fail("sem delegação inválida"))
    with pytest.raises(ValueError):
        asyncio.run(surface.ecosystem_artifact_handoff("../../secret"))
