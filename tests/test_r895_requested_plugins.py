"""R895: plugins pedidos no registro canônico, sem executar tarefas externas."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations.scientific_plugins import PLUGINS, ScientificPluginService

REQUESTED = {
    "superpowers", "scigrant", "wolfram", "anthropic-skills",
    "cowork-plugin-management", "bio-research", "plugin-creator", "data", "design",
    "visualize", "human-resources", "work-pets", "enterprise-search",
    "life-sciences-literature", "legal", "productivity", "dr-alex-ramos",
    "contas-escolares-airam-veras", "medico-virtual-supremo", "sites",
}


def cache_package(cache: Path, plugin_id: str, *, explicit_only=False):
    _, relative, version = PLUGINS[plugin_id]
    package = cache / relative / version
    skill = package / "skills/exemplo/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: exemplo\ndescription: Instrução local de teste\n"
                     + ("disable-model-invocation: true\n" if explicit_only else "")
                     + "---\nInstrução de teste; não é uma execução de tarefa.\n", encoding="utf-8")
    if explicit_only:
        policy = skill.parent / "agents/openai.yaml"
        policy.parent.mkdir()
        policy.write_text("policy:\n  allow_implicit_invocation: false\n", encoding="utf-8")
    return package


def test_all_twenty_requested_plugins_share_existing_registry(tmp_path):
    from integrations import scientific_plugins
    assert REQUESTED <= set(PLUGINS)
    assert set(getattr(scientific_plugins, "REQUESTED_PLUGIN_IDS", ())) == REQUESTED
    result = ScientificPluginService(tmp_path).status()
    rows = {item["id"]: item for item in result["plugins"]}
    assert REQUESTED <= set(rows)
    assert result["executed"] is False
    assert all(rows[pid]["instructions_installed"] is False for pid in REQUESTED)
    assert all(rows[pid]["local_connector_execution"] is False for pid in REQUESTED)
    assert rows["sites"]["connector_scope"] == "authenticated_host"
    assert rows["work-pets"]["connector_scope"] == "authenticated_host"


def test_sync_all_twenty_preserves_explicit_policy_and_does_not_run_hooks(tmp_path, monkeypatch):
    assert REQUESTED <= set(PLUGINS)
    cache = tmp_path / "cache"
    for pid in sorted(REQUESTED):
        package = cache_package(cache, pid, explicit_only=True)
        (package / "hooks.json").write_text('{"hooks":{"PreToolUse":["NEVER_EXECUTE"]}}')
    monkeypatch.setattr("subprocess.run", lambda *a, **k: pytest.fail("Importação não executa hooks ou conectores"))
    service = ScientificPluginService(tmp_path / "repo")

    result = service.sync(cache_root=cache, plugin_ids=sorted(REQUESTED))

    assert result["status"] == "completed"
    assert {entry["id"] for entry in result["plugins"]} == REQUESTED
    assert result["executed"] is False and result["credentials_copied"] is False
    assert len(service._registry()) == 20
    for pid in sorted(REQUESTED):
        plan = service.skill(pid, "exemplo")
        assert plan["status"] == "instruction_only" and plan["executed"] is False
        assert plan["policy"]["disable_model_invocation"] is True
        assert plan["policy"]["allow_implicit_invocation"] is False
    rows = {row["id"]: row for row in service.status()["plugins"]}
    assert all(rows[pid]["hash_integrity"] is True for pid in REQUESTED)


def test_missing_package_keeps_batch_uninstalled(tmp_path):
    assert "superpowers" in PLUGINS
    cache_package(tmp_path / "cache", "data")
    service = ScientificPluginService(tmp_path / "repo")
    with pytest.raises(ValueError, match="ausente"):
        service.sync(cache_root=tmp_path / "cache", plugin_ids=["data", "superpowers"])
    assert not service.storage.exists()


def test_status_and_skill_fail_closed_after_package_tampering(tmp_path):
    cache = tmp_path / "cache"
    cache_package(cache, "data")
    service = ScientificPluginService(tmp_path / "repo")
    imported = service.sync(cache_root=cache, plugin_ids=["data"])["plugins"][0]
    target = Path(imported["package_root"]) / "skills/exemplo/SKILL.md"
    target.write_text("Instruções adulteradas", encoding="utf-8")

    row = next(row for row in service.status()["plugins"] if row["id"] == "data")

    assert row.get("hash_integrity") is False
    assert row["instructions_installed"] is False
    assert row.get("instruction_status") == "integrity_failed"
    with pytest.raises(ValueError, match="integridade"):
        service.skill("data", "exemplo")


@pytest.mark.parametrize("filename", [".env", ".env.production"])
def test_source_credentials_rejected_before_copy(tmp_path, filename):
    cache = tmp_path / "cache"
    package = cache_package(cache, "data")
    (package / filename).write_text("PRIVATE_VALUE=fixture-only", encoding="utf-8")
    service = ScientificPluginService(tmp_path / "repo")

    with pytest.raises(ValueError, match="credenciais|sensível"):
        service.sync(cache_root=cache, plugin_ids=["data"])

    assert not service.storage.exists()


def test_stale_registry_version_cannot_advertise_ready_instructions(tmp_path):
    cache = tmp_path / "cache"
    cache_package(cache, "data")
    service = ScientificPluginService(tmp_path / "repo")
    service.sync(cache_root=cache, plugin_ids=["data"])
    registry = service._registry()
    registry["data"]["version"] = "0.0.0-historical"
    service._write(service._path("registry.json"), registry)

    row = next(row for row in service.status()["plugins"] if row["id"] == "data")

    assert row["instructions_installed"] is False
    assert row["hash_integrity"] is False
    assert row["instruction_status"] == "version_mismatch"
    with pytest.raises(ValueError, match="Versão"):
        service.skill("data", "exemplo")


@pytest.mark.parametrize("plugin_id,operation,arguments,expected", [
    ("work-pets", "list", {"limit": 5}, "mcp__codex_apps__pets_list_pets"),
    ("sites", "list", {"limit": 5, "role": "owner"}, "mcp__codex_apps__sites_list_sites"),
    ("wolfram", "query", {"query": "2+3"}, "mcp__codex_apps__wolfram_wolframalpha"),
])
def test_safe_host_operations_emit_bound_tickets_only(tmp_path, plugin_id, operation, arguments, expected):
    service = ScientificPluginService(tmp_path)
    request = service.request(plugin_id, operation, arguments)
    assert request["host_tool"] == expected
    assert request["arguments"] == arguments
    assert request["status"] == "awaiting_host" and request["executed"] is False
    assert len(request["request_sha256"]) == 64
    assert not service._path("responses").exists()


@pytest.mark.parametrize("plugin_id,operation,arguments", [
    ("sites", "create", {"title": "Não publicar"}),
    ("sites", "deploy", {"project_id": "not-a-real-id"}),
    ("sites", "list", {"role": "admin"}),
    ("sites", "list", {"limit": True}),
    ("work-pets", "create", {"name": "Não criar"}),
    ("work-pets", "select", {"pet_id": "default"}),
    ("work-pets", "list", {"limit": 21}),
    ("plugin-creator", "create", {"file": "not-an-archive"}),
    ("scigrant", "workflow", {}),
])
def test_import_does_not_authorize_external_mutations_or_grant_workflow(tmp_path, plugin_id, operation, arguments):
    service = ScientificPluginService(tmp_path)
    with pytest.raises(ValueError):
        service.request(plugin_id, operation, arguments)
    assert not service.storage.exists()


@pytest.mark.parametrize("payload", [
    {"isError": True, "content": [{"type": "text", "text": "Internal error"}]},
    {"structuredContent": {"status": "authentication_required"}},
    {"structuredContent": {"status": "not_entitled"}},
    {"structuredContent": {"status": "temporarily_unavailable"}},
])
def test_failed_or_unentitled_host_does_not_become_completed(tmp_path, payload):
    service = ScientificPluginService(tmp_path)
    request = service.request("scigrant", "workflow", {}, intent="grant_writing")
    result = service.accept_host_response(
        request["request_id"], host_tool=request["host_tool"],
        request_sha256=request["request_sha256"], result=payload, reported_by="fixture-host")
    assert result["status"] == "failed"
    assert result["local_connector_execution"] is False
    assert result["external_validation"] is False
    assert service.result(request["request_id"])["status"] == "failed"


def test_wolfram_legacy_input_is_normalized_to_official_schema(tmp_path):
    service = ScientificPluginService(tmp_path)
    request = service.request("wolfram", "query", {"input": "2+3"})
    assert request["arguments"] == {"query": "2+3"}
    assert json.loads(service._path("requests", request["request_id"] + ".json").read_text())["arguments"] == {"query": "2+3"}


@pytest.mark.parametrize("relative", [
    "docs/authorization.md", "docs/password-guidance.md", "docs/secrets/README.md",
])
def test_documentation_names_do_not_become_secret_payload_fields(tmp_path, relative):
    import hashlib

    cache = tmp_path / "cache"
    package = cache_package(cache, "data")
    document = package / relative
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("Documentação pública de exemplo; nenhum segredo.\n", encoding="utf-8")
    service = ScientificPluginService(tmp_path / "repo")

    try:
        result = service.sync(cache_root=cache, plugin_ids=["data"])
    except ValueError as exc:
        pytest.fail(f"Nome de documentação válido impediu sincronização: {exc}")

    entry = result["plugins"][0]
    assert result["status"] == "completed"
    assert entry["files"][relative] == hashlib.sha256(document.read_bytes()).hexdigest()
    assert service._registry()["data"] == entry
    assert (Path(entry["package_root"]) / relative).read_bytes() == document.read_bytes()
    row = next(row for row in service.status()["plugins"] if row["id"] == "data")
    assert row["hash_integrity"] is True
    assert service.sync(cache_root=cache, plugin_ids=["data"])["plugins"][0] == entry


@pytest.mark.parametrize("filename", ["credentials.json", "auth.json", "tokens.json", ".env.production"])
def test_documentation_exception_does_not_import_credential_files(tmp_path, filename):
    cache = tmp_path / "cache"
    package = cache_package(cache, "data")
    forbidden = package / "docs" / filename
    forbidden.parent.mkdir()
    forbidden.write_text("fixture-only; no live credentials", encoding="utf-8")
    service = ScientificPluginService(tmp_path / "repo")
    with pytest.raises(ValueError, match="credenciais|sensível"):
        service.sync(cache_root=cache, plugin_ids=["data"])
    assert not service.storage.exists()


@pytest.mark.parametrize("field", ["authorization", "api_key", "password", "access_token"])
def test_manifest_exception_does_not_relax_host_payloads(tmp_path, field):
    service = ScientificPluginService(tmp_path)
    with pytest.raises(ValueError, match="segredo"):
        service.request("wolfram", "query", {"query": {field: "fixture-only"}})
    assert not service.storage.exists()
    request = service.request("wolfram", "query", {"query": "2+3"})
    with pytest.raises(ValueError, match="segredo"):
        service.accept_host_response(
            request["request_id"], host_tool=request["host_tool"],
            request_sha256=request["request_sha256"],
            result={"files": {"docs/authorization.md": "0" * 64}, field: "fixture-only"},
            reported_by="fixture-host")
    assert not service._path("responses", request["request_id"] + ".json").exists()


@pytest.mark.parametrize("files", [
    {"../outside.md": "0" * 64}, {"/absolute.md": "0" * 64},
    {"docs/.env.production": "0" * 64}, {"docs/credentials.json": "0" * 64},
    {"docs/readme.md": "not-a-sha256"}, {"docs/readme.md": 123},
])
def test_retained_manifest_paths_and_hashes_are_validated_before_registry_write(tmp_path, files):
    cache = tmp_path / "cache"
    cache_package(cache, "data")
    cache_package(cache, "wolfram")
    service = ScientificPluginService(tmp_path / "repo")
    service.sync(cache_root=cache, plugin_ids=["data"])
    registry_path = service._path("registry.json")
    registry = json.loads(registry_path.read_bytes())
    registry["data"]["files"] = files
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    before = registry_path.read_bytes()

    with pytest.raises(ValueError, match="[Mm]anifesto|[Cc]aminho|hash|credenciais|sensível"):
        service.sync(cache_root=cache, plugin_ids=["wolfram"])

    assert registry_path.read_bytes() == before
