"""R894: perfis persistentes, gate de catálogo e ativação pelo primário."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def api():
    assert importlib.util.find_spec("agents.lifecycle") is not None, "Falta ciclo de vida governado"
    return importlib.import_module("agents.lifecycle")


@pytest.fixture
def repo(tmp_path):
    for folder in ("agents/catalog", "specs", "tests"):
        (tmp_path / folder).mkdir(parents=True)
    (tmp_path / "specs/SPEC-935-R894-fixture.md").write_text("# Fixture local")
    (tmp_path / "tests/test_r894_fixture.py").write_text("def test_contract(): assert True\n")
    return tmp_path


def profile():
    return {"agent_id": "fixture-audit", "name": "Fixture Audit",
            "description": "Revisar rastreabilidade de um alvo de teste local.",
            "capabilities": ["evidence_audit"],
            "spec_file": "specs/SPEC-935-R894-fixture.md",
            "test_file": "tests/test_r894_fixture.py",
            "prompt": "Leia o alvo solicitado e apresente achados com fonte e limitações."}


def test_create_validates_before_persisting_and_never_claims_execution(repo):
    service = api().AgentLifecycleService(repo)
    report = service.create(profile())
    assert report["definition_validated"] is True
    assert report["executed"] is False
    assert report["agent_id"] == "fixture-audit"
    assert service.validate("fixture-audit")["source_sha256"] == report["source_sha256"]
    meta = yaml.safe_load((repo / "agents/catalog/fixture-audit.md").read_text().split("---", 2)[1])
    assert meta["parent"] == "marceloclaro"
    assert meta["permission"]["task"] == "deny"
    assert meta["permission"]["bash"]["*"] == "deny"
    assert "profile_fixture_audit" in meta["tags"]


@pytest.mark.parametrize("field,value", [
    ("agent_id", "../escape"), ("agent_id", "marceloclaro"),
    ("capabilities", []), ("capabilities", ["a", 1]),
    ("description", ""), ("allow_edit", "true"),
    ("spec_file", "../elsewhere.md"), ("test_file", "tests/missing.py"),
    ("prompt", ""), ("permission", {"task": "allow"}),
])
def test_invalid_creation_never_writes_a_card(repo, field, value):
    p = profile()
    p[field] = value
    with pytest.raises(ValueError):
        api().AgentLifecycleService(repo).create(p)
    assert list((repo / "agents/catalog").iterdir()) == []


def test_duplicate_and_symlink_preserve_existing_bytes(repo, tmp_path):
    service = api().AgentLifecycleService(repo)
    service.create(profile())
    target = repo / "agents/catalog/fixture-audit.md"
    original = target.read_bytes()
    with pytest.raises(ValueError):
        service.create(profile())
    assert target.read_bytes() == original
    target.unlink()
    outside = repo / "outside.md"
    outside.write_bytes(original)
    target.symlink_to(outside)
    with pytest.raises(ValueError):
        service.validate("fixture-audit")


@pytest.mark.parametrize("mutation", ["task", "bash", "output", "parent", "spec", "duplicate_key"])
def test_tampered_policy_or_contract_is_rejected(repo, mutation):
    service = api().AgentLifecycleService(repo)
    service.create(profile())
    path = repo / "agents/catalog/fixture-audit.md"
    raw = path.read_text()
    meta = yaml.safe_load(raw.split("---", 2)[1])
    if mutation == "task":
        meta["permission"]["task"] = "allow"
    elif mutation == "bash":
        meta["permission"]["bash"]["*"] = "allow"
    elif mutation == "output":
        del meta["output_contract"]
    elif mutation == "parent":
        meta["parent"] = "other"
    elif mutation == "spec":
        meta["spec_file"] = "specs/missing.md"
    elif mutation == "duplicate_key":
        raw = raw.replace("parent: marceloclaro", "parent: marceloclaro\nparent: other")
    if mutation != "duplicate_key":
        raw = "---\n" + yaml.safe_dump(meta) + "---\n" + raw.split("---", 2)[2]
    path.write_text(raw)
    with pytest.raises(ValueError):
        service.validate("fixture-audit")


def test_unbaselined_card_cannot_bypass_loader_contract(repo):
    p = repo / "agents/catalog/bypass.md"
    p.write_text("---\nname: bypass\ntags: [audit]\n---\nUnmanaged")
    with pytest.raises(ValueError):
        api().enforce_catalog_contract(p, p.read_bytes(), repo_root=repo)


def test_historical_baseline_is_content_bound(repo):
    import hashlib
    p = repo / "agents/catalog/old.md"
    p.write_text("---\nname: old\n---\nLegacy")
    baseline = {"schema_version": 1, "files": {"agents/catalog/old.md": hashlib.sha256(p.read_bytes()).hexdigest()}}
    (repo / "agents/lifecycle_baseline.json").write_text(json.dumps(baseline))
    assert api().enforce_catalog_contract(p, p.read_bytes(), repo_root=repo)["mode"] == "legacy_baseline"
    p.write_text(p.read_text() + "\nchanged")
    with pytest.raises(ValueError):
        api().enforce_catalog_contract(p, p.read_bytes(), repo_root=repo)


def test_requested_and_observed_roles_are_persistent_and_validated():
    path = ROOT / "agents/session_profiles.json"
    assert path.is_file(), "Perfis históricos ainda não foram incorporados"
    manifest = json.loads(path.read_text())
    ids = {r["agent_id"] for r in manifest["profiles"]}
    assert {"architecture-source-audit", "architecture-flows", "readme-contract-audit",
            "readme-usage-audit", "readme-all-flows", "r881-final-audit", "r886-review",
            "metacognition-audit", "evaluate-repositories", "codesight-source",
            "repos-rea-analysis", "scientific-profile", "whoosh-persistence"} <= ids
    assert len(ids) == len(manifest["profiles"])
    for row in manifest["profiles"]:
        report = api().AgentLifecycleService(ROOT).validate(row["agent_id"])
        assert report["definition_validated"] is True
        assert report["executed"] is False


def test_primary_exposes_lifecycle_and_preserves_execution_boundary(tmp_path, monkeypatch):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    assert hasattr(MarceloClaroOrchestrator, "agent_profile_action"), "Falta entrada no primário"
    from mci.blackboard import blackboard
    busmod = importlib.import_module("mci.metabus")
    monkeypatch.setattr(busmod, "MEMORY_FILE", str(tmp_path / "memory.json"))
    monkeypatch.setattr(busmod, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(busmod.metabus, "memory", busmod.MetacognitiveMemory())
    original_registry, original_tasks = dict(blackboard.registry), dict(blackboard.tasks)
    before = copy.deepcopy(busmod.metabus.memory.confidence_ledger)
    try:
        core = MarceloClaroOrchestrator(auto_load_agents=False)
        report = core.agent_profile_action({"operation": "activate", "agent_id": "readme-contract-audit",
                                            "task": "Auditar o contrato de uso do README com fontes locais."})
        assert report["definition_validated"] is True
        assert report["registered"] is True
        assert report["executed"] is False
        task = blackboard.tasks[report["task_id"]]
        assert task.assigned_to == "readme-contract-audit"
        assert "profile_readme_contract_audit" in task.required_capabilities
        assert task.context["agent_profile"]["source_sha256"] == report["source_sha256"]
        assert task.status != "completed"
        assert busmod.metabus.memory.confidence_ledger == before
    finally:
        blackboard.registry.clear()
        blackboard.registry.update(original_registry)
        blackboard.tasks.clear()
        blackboard.tasks.update(original_tasks)


def test_cli_and_mcp_expose_same_primary_contract(tmp_path, monkeypatch, capsys):
    assert importlib.util.find_spec("marceloclaro.governed_cli") is not None
    from integrations import ecosystem_mcp
    from marceloclaro.governed_cli import run_governed_cli
    calls = []
    class Primary:
        def agent_profile_action(self, config):
            calls.append(config)
            return {"status": "definition_validated", "definition_validated": True, "executed": False}
    spy = Primary()
    def factory(**_):
        return spy
    assert run_governed_cli("agentes", ["validar", "readme-contract-audit"], factory) == 0
    assert json.loads(capsys.readouterr().out)["executed"] is False
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: spy)
    assert hasattr(ecosystem_mcp, "ecosystem_agent_profile")
    import asyncio
    result = asyncio.run(ecosystem_mcp.ecosystem_agent_profile({"operation": "validate", "agent_id": "readme-contract-audit"}))
    assert result["definition_validated"] is True
    assert calls == [{"operation": "validate", "agent_id": "readme-contract-audit"}] * 2


def test_unknown_mcp_profile_fields_rejected_before_primary(monkeypatch):
    from integrations import ecosystem_mcp
    assert hasattr(ecosystem_mcp, "ecosystem_agent_profile")
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: pytest.fail("Validação tardia"))
    import asyncio
    with pytest.raises(ValueError):
        asyncio.run(ecosystem_mcp.ecosystem_agent_profile({"operation": "inventory", "execute": True}))


def test_managed_ids_cannot_collide_with_hyphen_capability(repo):
    service = api().AgentLifecycleService(repo)
    first = profile()
    first["agent_id"] = "foo-bar"
    service.create(first)
    second = profile()
    second["agent_id"] = "foo_bar"

    with pytest.raises(ValueError):
        service.create(second)

    assert not (repo / "agents/catalog/foo_bar.md").exists()


def test_other_profile_cannot_claim_reserved_exclusive_capability(repo):
    document = profile()
    document["capabilities"] = ["profile_other_audit"]

    with pytest.raises(ValueError):
        api().AgentLifecycleService(repo).create(document)

    assert list((repo / "agents/catalog").iterdir()) == []


def test_direct_card_cannot_add_another_reserved_profile_tag(repo):
    service = api().AgentLifecycleService(repo)
    service.create(profile())
    path = repo / "agents/catalog/fixture-audit.md"
    header, body = path.read_text()[4:].split("\n---\n", 1)
    meta = yaml.safe_load(header)
    meta["tags"].append("profile_other_audit")
    meta["skills"][0]["tags"] = list(meta["tags"])
    path.write_text("---\n" + yaml.safe_dump(meta) + "---\n" + body)

    with pytest.raises(ValueError):
        service.validate("fixture-audit")


def test_create_rejects_symlink_in_catalog_ancestor(repo, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "catalog").mkdir()
    (repo / "agents/catalog").rmdir()
    (repo / "agents").rmdir()
    (repo / "agents").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError):
        api().AgentLifecycleService(repo).create(profile())

    assert list((outside / "catalog").iterdir()) == []


def test_catalog_generator_rejects_policy_changed_after_loader_validation(repo, monkeypatch):
    from integrations import opencode_cli
    from marceloclaro import catalog_loader
    monkeypatch.setattr(api(), "ROOT", repo)
    service = api().AgentLifecycleService(repo)
    service.create(profile())
    path = repo / "agents/catalog/fixture-audit.md"
    original_loader = catalog_loader.load_catalog_definitions

    def load_then_tamper():
        definitions = original_loader(str(repo / "agents/catalog"))
        header, body = path.read_text()[4:].split("\n---\n", 1)
        meta = yaml.safe_load(header)
        meta["permission"]["bash"]["*"] = "allow"
        path.write_text("---\n" + yaml.safe_dump(meta) + "---\n" + body)
        return definitions

    monkeypatch.setattr(catalog_loader, "load_catalog_definitions", load_then_tamper)
    with pytest.raises(ValueError):
        opencode_cli._catalog_agents()


def test_essential_generator_uses_validated_policy_bytes(repo, monkeypatch):
    from integrations import opencode_cli
    lifecycle = api()
    source = repo / "agents/legacy.md"
    source.write_text("---\nname: legacy\npermission:\n  bash:\n    '*': deny\n---\nInstrução histórica.\n")
    import hashlib
    (repo / "agents/lifecycle_baseline.json").write_text(json.dumps({
        "files": {"agents/legacy.md": hashlib.sha256(source.read_bytes()).hexdigest()}}))
    monkeypatch.setattr(lifecycle, "ROOT", repo)
    monkeypatch.setattr(opencode_cli, "ROOT", str(repo))
    original_enforce = lifecycle.enforce_catalog_contract

    def enforce_then_tamper(path, raw, **kwargs):
        receipt = original_enforce(path, raw, **kwargs)
        source.write_text(source.read_text().replace("'*': deny", "'*': allow"))
        return receipt

    monkeypatch.setattr(lifecycle, "enforce_catalog_contract", enforce_then_tamper)

    generated = opencode_cli._essential_agents()

    assert generated["legacy"]["permission"]["bash"]["*"] == "deny"
