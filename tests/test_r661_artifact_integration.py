"""R661: portabilidade com identidade, políticas e prova atual no disco."""

from pathlib import Path
import json

import pytest
from integrations.harness_federation import HarnessHarvester, HarnessEmitter
from reversa_universal.skill_dispatch import ReversaSkillDispatcher
from transformer.harness_head import HarnessRegistry


def test_prepopulated_routing_card_remains_resolvable(tmp_path):
    from integrations.harness_federation.artifact import build_artifact
    from transformer.harness_head import HarnessRegistry

    source = tmp_path / "SKILL.md"
    source.write_text("---\nname: review\ndescription: Revisar código\n---\nLeia invariantes.\n")
    artifact = build_artifact(source_path=str(source), ecosystem="codex", kind="skill",
                              name="review", description="Revisar código", origin="user")
    registry = HarnessRegistry(repo_root=str(tmp_path))
    registry._artifacts = [artifact]
    assert registry.cards()[0]["agent_id"] == artifact.artifact_id
    assert registry.find(artifact.artifact_id) is artifact



def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def skill(path, name="demo", body="Leia references/guide.md.", restricted=False):
    return write(path, f"---\nname: {name}\ndescription: Skill de integração\n"
                 + ("disable-model-invocation: true\n" if restricted else "")
                 + f"---\n\n{body}\n")


def harvester(tmp_path):
    repo, home = tmp_path / "repo", tmp_path / "home"
    repo.mkdir(exist_ok=True)
    home.mkdir(exist_ok=True)
    return HarnessHarvester(str(repo), str(home)), repo, home


def test_modern_codex_skills_and_plugin_cache_are_discovered(tmp_path):
    h, repo, home = harvester(tmp_path)
    local = skill(home / ".codex/skills/local/SKILL.md", "local")
    plugin = skill(home / ".codex/plugins/cache/vendor/plugin/1.0.0/skills/plugin/SKILL.md", "plugin")
    found = h.discover()
    assert {str(local), str(plugin)} <= {a.source_path for a in found}
    assert next(a for a in found if a.source_path == str(plugin)).origin == "third_party"


def test_distinct_homonyms_have_distinct_ids_and_destinations(tmp_path):
    h, repo, home = harvester(tmp_path)
    for owner in ("a", "b"):
        skill(home / f".claude/plugins/cache/{owner}/1.0.0/skills/demo/SKILL.md", body=f"Corpo {owner}")
    artifacts = [a for a in h.discover() if a.kind == "skill"]
    assert len(artifacts) == 2
    assert len({a.artifact_id for a in artifacts}) == 2
    paths = [HarnessEmitter(str(repo)).emit_skill(a)["path"] for a in artifacts]
    assert len(set(paths)) == 2
    assert [(a.artifact_id, a.emission_slug) for a in artifacts] == [(a.artifact_id, a.emission_slug) for a in h.discover() if a.kind == "skill"]


def test_identical_mirrors_deduplicate_without_losing_provenance(tmp_path):
    h, repo, home = harvester(tmp_path)
    for owner in ("cache/a", "marketplaces/a"):
        skill(home / f".claude/plugins/{owner}/skills/demo/SKILL.md")
    artifacts = [a for a in h.discover() if a.kind == "skill"]
    assert len(artifacts) == 1
    assert len(artifacts[0].duplicate_paths) == 1


def test_same_body_with_distinct_invocation_policy_does_not_deduplicate(tmp_path):
    h, repo, home = harvester(tmp_path)
    skill(home / ".claude/skills/a/SKILL.md")
    b = skill(home / ".claude/skills/b/SKILL.md")
    write(b.parent / "agents/openai.yaml", "policy:\n  allow_implicit_invocation: false\n")
    assert len([a for a in h.discover() if a.kind == "skill"]) == 2


def test_emitted_skill_preserves_policy_and_contained_references(tmp_path):
    h, repo, home = harvester(tmp_path)
    source = skill(home / ".claude/skills/demo/SKILL.md", restricted=True)
    write(source.parent / "agents/openai.yaml", "policy:\n  allow_implicit_invocation: false\n")
    write(source.parent / "references/guide.md", "Instruções do guia.")
    artifact = next(a for a in h.discover() if a.kind == "skill")
    emitted = HarnessEmitter(str(repo)).emit_skill(artifact)
    target = Path(emitted["path"])
    assert target.parent.joinpath("references/guide.md").read_text() == "Instruções do guia."
    decision = ReversaSkillDispatcher(repo, extra_roots=[home]).plan(artifact.emission_slug)
    assert decision.execution_mode == "read-and-execute"
    assert decision.user_invoked is True
    assert decision.instruction_root == str(target.parent)
    assert decision.source_skill_path == str(source)
    assert emitted["installed"] is False


def test_modified_source_refuses_emission_and_handoff(tmp_path):
    h, repo, home = harvester(tmp_path)
    source = skill(home / ".claude/skills/demo/SKILL.md")
    registry = HarnessRegistry(str(repo), harvester=h)
    artifact = registry.artifacts()[0]
    source.write_text(source.read_text() + "alterado")
    result = HarnessEmitter(str(repo)).emit_skill(artifact)
    assert result["status"] == "refused"
    assert not repo.joinpath(".opencode").exists()
    handoff = registry.plan_handoff(artifact.artifact_id)
    assert handoff["status"] == "refused"
    assert "source_changed" in handoff["reasons"]


def test_source_symlink_escape_is_refused(tmp_path):
    h, repo, home = harvester(tmp_path)
    source = skill(home / ".claude/skills/demo/SKILL.md")
    outside = write(tmp_path / "outside.md", "Segredo fora da skill.")
    (source.parent / "references").mkdir()
    (source.parent / "references/guide.md").symlink_to(outside)
    artifact = next(a for a in h.discover() if a.kind == "skill")
    report = HarnessEmitter(str(repo)).emit_skill(artifact)
    assert report["status"] == "refused"
    assert "support_path_escape" in report["reasons"]


def test_destination_symlink_escape_is_refused(tmp_path):
    h, repo, home = harvester(tmp_path)
    skill(home / ".claude/skills/demo/SKILL.md")
    artifact = next(a for a in h.discover() if a.kind == "skill")
    outside = tmp_path / "outside"
    outside.mkdir()
    repo.joinpath(".opencode").symlink_to(outside, target_is_directory=True)
    report = HarnessEmitter(str(repo)).emit_skill(artifact)
    assert report["status"] == "refused"
    assert not outside.joinpath("skills/demo/SKILL.md").exists()


@pytest.mark.parametrize("prompts", ["Faça a revisão.", ["Faça a revisão.", "Prepare testes."]])
def test_plugin_prompts_preserve_values_types_and_portable_interface(tmp_path, prompts):
    h, repo, home = harvester(tmp_path)
    interface = {"displayName": "Plugin", "shortDescription": "Integração", "defaultPrompt": prompts}
    write(repo / ".codex-plugin/plugin.json", json.dumps({"name": "demo-plugin", "description": "Plugin",
          "extensions": {"com.openai.interface": interface}, "skills": "./skills"}))
    skill(repo / "skills/demo/SKILL.md")
    artifact = next(a for a in h.discover() if a.kind == "plugin")
    report = HarnessEmitter(str(tmp_path / "out")).export_codex_plugin(artifact)
    manifest = json.loads(Path(report["path"]).read_text())
    assert manifest["extensions"]["com.openai"]["interface"]["defaultPrompt"] == prompts
    assert manifest["interface"]["defaultPrompt"] == prompts
    assert Path(report["path"]).parent.joinpath(manifest["skills"], "demo/SKILL.md").exists()
    assert report["installed"] is False


def test_plan_handoff_uses_current_source_without_execution(tmp_path):
    h, repo, home = harvester(tmp_path)
    source = skill(home / ".claude/skills/demo/SKILL.md", restricted=True)
    registry = HarnessRegistry(str(repo), harvester=h)
    artifact = registry.artifacts()[0]
    result = registry.plan_handoff(artifact.artifact_id)
    assert result["status"] == "ready"
    assert result["source_path"] == str(source)
    assert result["instruction_root"] == str(source.parent)
    assert result["execution_mode"] == "read-and-execute"
    assert result["executed"] is result["execution_verified"] is result["installed"] is False
    assert result["source_file_sha256"] == artifact.source_file_sha256
    assert registry.plan_handoff("missing")["status"] == "not_found"


def test_cross_ecosystem_homonyms_do_not_overwrite_targets(tmp_path):
    h, repo, home = harvester(tmp_path)
    skill(home / ".claude/skills/demo/SKILL.md", body="Claude")
    skill(home / ".codex/skills/demo/SKILL.md", body="Codex")
    artifacts = [a for a in h.discover() if a.kind == "skill"]
    assert len({a.artifact_id for a in artifacts}) == 2
    assert len({a.emission_slug for a in artifacts}) == 2
    report = HarnessEmitter(str(repo)).emit_all(artifacts)
    assert len(report["emitted_paths"]) == 2


def test_support_hash_drift_refuses_emission(tmp_path):
    h, repo, home = harvester(tmp_path)
    source = skill(home / ".claude/skills/demo/SKILL.md")
    support = write(source.parent / "references/guide.md", "antes")
    artifact = next(a for a in h.discover() if a.kind == "skill")
    support.write_text("depois")
    assert "support_changed" in HarnessEmitter(str(repo)).emit_skill(artifact)["reasons"]


@pytest.mark.parametrize("name", [None, [], {}, False, "x" * 241])
def test_skill_name_requires_bounded_string(tmp_path, name):
    with pytest.raises(ValueError):
        ReversaSkillDispatcher(tmp_path).plan(name)


@pytest.mark.parametrize("policy", ["disable_model_invocation: 'false'", "allow_implicit_invocation: 'false'",
                                    "disable_model_invocation: null", "allow_implicit_invocation: []"])
def test_inherited_invocation_policy_rejects_non_boolean_values(tmp_path, policy):
    write(tmp_path / ".agents/skills/demo/SKILL.md",
                 "---\nname: demo\nx-invocation-policy:\n  " + policy + "\n---\nTexto")
    with pytest.raises(ValueError, match="invalid_invocation_policy"):
        ReversaSkillDispatcher(tmp_path).plan("demo")


def test_source_metadata_cannot_authorize_arbitrary_file_read(tmp_path, monkeypatch):
    outside = write(tmp_path / "outside/secret.md", "Arquivo externo")
    write(tmp_path / "repo/.agents/skills/demo/SKILL.md",
                 f"---\nname: demo\nx-source-skill-path: {outside}\n"
                 f"x-source-instruction-root: {outside.parent}\nx-source-skill-sha256: " + "0" * 64 + "\n---\nTexto")
    original = Path.read_bytes
    def guarded_read(p):
        assert p != outside, "Dispatcher tentou ler arquivo fora das raízes configuradas"
        return original(p)
    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    with pytest.raises(ValueError, match="source_root_untrusted"):
        ReversaSkillDispatcher(tmp_path / "repo").plan("demo")


def test_skill_read_is_bounded_before_parsing(tmp_path):
    write(tmp_path / ".agents/skills/demo/SKILL.md", "x" * (128 * 1024 + 1))
    with pytest.raises(ValueError, match="skill_too_large"):
        ReversaSkillDispatcher(tmp_path).plan("demo")


def test_plugin_without_skill_payload_omits_broken_declaration(tmp_path):
    h, repo, home = harvester(tmp_path)
    write(repo / ".codex-plugin/plugin.json", json.dumps({"name": "plugin", "skills": "./absent"}))
    artifact = next(a for a in h.discover() if a.kind == "plugin")
    report = HarnessEmitter(str(tmp_path / "out")).export_codex_plugin(artifact)
    assert "skills" not in json.loads(Path(report["path"]).read_text())


@pytest.mark.parametrize("policy", ["allow_implicit_invocation: false", "disable-model-invocation: true"])
def test_frontmatter_nested_policy_remains_restrictive_after_emission(tmp_path, policy):
    h, repo, home = harvester(tmp_path)
    write(home / ".claude/skills/demo/SKILL.md", "---\nname: demo\ndescription: Restrita\npolicy:\n  " + policy + "\n---\nLeia o texto.")
    artifact = next(a for a in h.discover() if a.kind == "skill")
    assert ReversaSkillDispatcher(home / ".claude", extra_roots=[home / ".claude/skills"]).plan("demo").user_invoked
    report = HarnessEmitter(str(repo)).emit_skill(artifact)
    assert report["status"] == "emitted"
    assert ReversaSkillDispatcher(repo, extra_roots=[home]).plan(artifact.emission_slug).user_invoked


@pytest.mark.parametrize("directory", [".opencode/skills", ".agents/skills", ".codex/skills"])
def test_core_project_skill_roots_join_federated_handoff(tmp_path, directory):
    h, repo, home = harvester(tmp_path)
    source = write(repo / directory / "core-hooks/SKILL.md",
                   "---\nname: core-hooks\ndescription: Hooks do Core\npolicy:\n  allow_implicit_invocation: false\n---\nLeia instruções.")
    registry = HarnessRegistry(str(repo), harvester=h)
    artifact = next(a for a in registry.artifacts() if a.name == "core-hooks")
    assert artifact.origin == "first_party"
    assert len([a for a in registry.artifacts() if a.source_path == str(source)]) == 1
    handoff = registry.plan_handoff(artifact.artifact_id)
    assert handoff["status"] == "ready"
    assert handoff["execution_mode"] == "read-and-execute"
    assert handoff["invocation_policy"]["allow_implicit_invocation"] is False


def test_portable_plugin_root_discovery_preserves_nested_interface_and_reports_scope(tmp_path):
    h, repo, home = harvester(tmp_path)
    package = home / ".codex/plugins/cache/vendor/plugin/1.0.0"
    manifest = {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "name": "my-plugin",
                "extensions": {"com.openai": {"interface": {"defaultPrompt": "Faça a revisão.", "displayName": "Plugin"}}}}
    write(package / "plugin.json", json.dumps(manifest))
    skill(package / "skills/demo/SKILL.md")
    write(package / "mcp.json", '{"mcpServers":{"example":{"command":"do-not-execute"}}}')
    write(package / "docs/example/plugin.json", json.dumps(manifest))
    plugins = [a for a in h.discover() if a.kind == "plugin"]
    assert len(plugins) == 1
    assert plugins[0].metadata["manifest_format"] == "agent_plugins_1_0"
    exported = HarnessEmitter(str(repo)).export_codex_plugin(plugins[0])
    data = json.loads(Path(exported["path"]).read_text())
    assert data["extensions"]["com.openai"]["interface"]["defaultPrompt"] == "Faça a revisão."
    assert Path(exported["path"]).parent.joinpath(data["skills"], "demo/SKILL.md").is_file()
    assert exported["portable_package"] is False
    assert exported["omitted_components"] == ["mcp"]


def test_prepopulated_routing_cards_always_resolve_in_find(tmp_path):
    h, repo, home = harvester(tmp_path)
    skill(home / ".claude/skills/demo/SKILL.md")
    artifact = next(a for a in h.discover() if a.kind == "skill")
    registry = HarnessRegistry(str(repo))
    registry._artifacts = [artifact]
    assert registry._all_artifacts is None
    cards = registry.cards()
    assert len(cards) == 1
    assert registry.find(cards[0]["artifact_id"]) is artifact
