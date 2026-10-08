"""Contraprovas da ponte de plugins científicos R670."""
import hashlib
from pathlib import Path

import pytest

from integrations.scientific_plugins import ScientificPluginService, PLUGINS


def source(tmp_path):
    cache = tmp_path / "cache"
    root = cache / "claude-cowork/data/1.1.0"
    skill = root / "skills/analyze/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: analyze\ndescription: Análise\ndisable-model-invocation: true\n---\nLeia ../references/schema.md\n")
    ref = root / "skills/references/schema.md"
    ref.parent.mkdir()
    ref.write_text("Dados reais e limites.")
    return cache, root, skill


def test_twelve_requested_plugins_without_execution_claim(tmp_path):
    assert len(PLUGINS) == 12
    result = ScientificPluginService(tmp_path).status()
    assert len(result["plugins"]) == 12
    assert result["executed"] is False
    assert all(p["local_connector_execution"] is False for p in result["plugins"])


def test_import_preserves_files_and_policy(tmp_path):
    cache, original, skill = source(tmp_path)
    service = ScientificPluginService(tmp_path / "repo")
    result = service.sync(cache_root=cache, plugin_ids=["data"])
    assert result["status"] == "completed"
    installed = Path(result["plugins"][0]["package_root"])
    assert (installed / "skills/analyze/SKILL.md").read_bytes() == skill.read_bytes()
    assert (installed / "skills/references/schema.md").read_bytes() == (original / "skills/references/schema.md").read_bytes()
    plan = service.skill("data", "analyze")
    assert plan["policy"]["disable_model_invocation"] is True
    assert plan["executed"] is False
    assert plan["source_file_sha256"] == hashlib.sha256(skill.read_bytes()).hexdigest()


def test_changed_import_refuses_skill(tmp_path):
    cache, _, _ = source(tmp_path)
    service = ScientificPluginService(tmp_path / "repo")
    result = service.sync(cache_root=cache, plugin_ids=["data"])
    (Path(result["plugins"][0]["package_root"]) / "skills/analyze/SKILL.md").write_text("alterado")
    with pytest.raises(ValueError, match="integridade"):
        service.skill("data", "analyze")


def test_source_symlink_escape_refused(tmp_path):
    cache, root, _ = source(tmp_path)
    outside = tmp_path / "secret.txt"
    outside.write_text("não copiar")
    (root / "escaped.txt").symlink_to(outside)
    with pytest.raises(ValueError):
        ScientificPluginService(tmp_path / "repo").sync(cache_root=cache, plugin_ids=["data"])


def test_host_request_bound_to_known_tool_and_arguments(tmp_path):
    service = ScientificPluginService(tmp_path)
    request = service.request("genomic-intelligence", "list_models", {"task": "promoter"})
    assert request["status"] == "awaiting_host"
    assert request["executed"] is False
    assert request["host_tool"].endswith("genomic_intelligence_list_models")
    assert service.result(request["request_id"])["status"] == "awaiting_host"
    with pytest.raises(ValueError):
        service.request("genomic-intelligence", "run_shell", {"command": "anything"})


@pytest.mark.parametrize("payload", [{"task": float("nan")}, {"task": "x"*150000}, {"secret_token": "abc"}])
def test_invalid_or_secret_request_has_no_side_effect(tmp_path, payload):
    with pytest.raises(ValueError):
        ScientificPluginService(tmp_path).request("genomic-intelligence", "list_models", payload)
    assert not (tmp_path / ".opencode/scientific-plugins").exists()


def test_receipt_identity_replay_and_failure(tmp_path):
    service = ScientificPluginService(tmp_path)
    request = service.request("genomic-intelligence", "list_models", {"task": "promoter"})
    with pytest.raises(ValueError):
        service.accept_host_response(request["request_id"], host_tool="different",
            request_sha256=request["request_sha256"], result={"isError": False}, reported_by="Codex")
    result = service.accept_host_response(request["request_id"], host_tool=request["host_tool"],
        request_sha256=request["request_sha256"], result={"isError": True, "content": [{"type": "text", "text": "failed"}]}, reported_by="Codex")
    assert result["status"] == "failed"
    assert result["local_connector_execution"] is False
    assert result["external_validation"] is False
    with pytest.raises(ValueError):
        service.accept_host_response(request["request_id"], host_tool=request["host_tool"],
            request_sha256=request["request_sha256"], result={}, reported_by="Codex")


def test_success_receipt_is_reported_not_independently_verified(tmp_path):
    service = ScientificPluginService(tmp_path)
    request = service.request("genomic-intelligence", "list_models", {"task": "promoter"})
    result = service.accept_host_response(request["request_id"], host_tool=request["host_tool"],
        request_sha256=request["request_sha256"], result={"isError": False, "structuredContent": {"models": ["control"]}}, reported_by="Codex host")
    assert result["status"] == "completed"
    assert result["host_reported_execution"] is True
    assert result["source_authenticity"] == "host_reported"
    assert result["external_validation"] is False
    assert service.result(request["request_id"])["response_sha256"] == result["response_sha256"]


def test_scigrant_requires_writing_goal(tmp_path):
    service = ScientificPluginService(tmp_path)
    with pytest.raises(ValueError):
        service.request("scigrant", "workflow", {})
    request = service.request("scigrant", "workflow", {}, intent="grant_writing")
    assert request["arguments"] == {}


@pytest.mark.parametrize("value", ["../../secret", "x/y", "", "../"])
def test_paths_cannot_escape_ticket_or_skill_roots(tmp_path, value):
    service = ScientificPluginService(tmp_path)
    with pytest.raises(ValueError):
        service.result(value)
    with pytest.raises(ValueError):
        service.skill("data", value)


def test_local_python_skill_cannot_write_bytecode_into_imported_package(tmp_path, monkeypatch):
    import subprocess
    service = ScientificPluginService(tmp_path)
    script = tmp_path / "skill/scripts/ncbi_entrez.py"
    script.parent.mkdir(parents=True)
    script.write_text("# trusted test fixture")
    monkeypatch.setattr(service, "skill", lambda *args: {"instruction_root": str(script.parent.parent)})
    def runner(argv, **kwargs):
        assert "-B" in argv
        assert kwargs["env"]["PYTHONDONTWRITEBYTECODE"] == "1"
        return subprocess.CompletedProcess(argv, 0, '{"ok": true}', "")
    monkeypatch.setattr(subprocess, "run", runner)
    result = service.run_local("life-sciences-literature", "pubmed_search", {"term": "reproducibility"})
    assert result["status"] == "completed"
