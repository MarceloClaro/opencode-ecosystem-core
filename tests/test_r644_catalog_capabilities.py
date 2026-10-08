"""SPEC-935-R644: declarações legadas não perdem capacidades no catálogo."""

import pytest

from marceloclaro import catalog_loader


def test_legacy_tags_add_declared_capabilities_and_deduplicate():
    caps = catalog_loader._derive_capabilities("researcher", {
        "category": "research",
        "tags": ["search", " summarize ", "cite", "literature-review", "summarize"],
    })
    assert {"search", "summarize", "cite", "literature_review"}.issubset(caps)
    assert len(caps) == len(set(caps))
    assert caps[:3] == ["research", "search", "literature_review"]


def test_legacy_explicit_capabilities_are_supported():
    caps = catalog_loader._derive_capabilities("generic", {
        "capabilities": ["summarize", "cite", "Code Review"],
    })
    assert {"summarize", "cite", "code_review"}.issubset(caps)


def test_a2a_skills_keep_priority_over_legacy_metadata():
    caps = catalog_loader._derive_capabilities("researcher", {
        "category": "research",
        "skills": [{"id": "review", "tags": ["review", "code-review"]}],
        "tags": ["summarize"],
        "capabilities": ["cite"],
    })
    assert caps == ["review", "code_review"]


@pytest.mark.parametrize("invalid", ["summarize", {"extendedAgentCard": True}, True, 3, None])
def test_legacy_fields_require_lists(invalid):
    caps = catalog_loader._derive_capabilities("generic", {
        "tags": invalid,
        "capabilities": invalid,
    })
    assert caps == ["general"]


def test_legacy_lists_reject_non_string_or_empty_entries():
    caps = catalog_loader._derive_capabilities("generic", {
        "tags": ["", "  ", None, True, 3, {}, "summarize"],
        "capabilities": ["cite", "cite", ["unsafe"]],
    })
    assert caps == ["general", "cite", "summarize"]


def test_derived_skill_tags_match_legacy_capabilities(tmp_path):
    (tmp_path / "researcher.md").write_text(
        "---\nname: researcher\ncategory: research\n"
        "tags: [search, summarize, cite, literature_review]\n---\n# Researcher\n",
        encoding="utf-8",
    )
    definition = catalog_loader.load_catalog_definitions(str(tmp_path))[0]
    assert {"summarize", "cite"}.issubset(definition["capabilities"])
    assert definition["skills"][0]["tags"] == definition["capabilities"]


def test_base_then_catalog_registration_preserves_declared_capabilities(monkeypatch):
    from marceloclaro.agent_loader import load_agent_definitions
    from mci.blackboard import blackboard

    base = next(card for card in load_agent_definitions() if card["agent_id"] == "researcher")
    catalog = next(card for card in catalog_loader.load_catalog_definitions() if card["agent_id"] == "researcher")
    monkeypatch.setattr(blackboard, "registry", {})
    blackboard._handle_registration({"payload": {**base, "schema": {"old": True}}})
    blackboard.registry["researcher"].status = "busy"
    blackboard._handle_registration({"payload": catalog})
    card = blackboard.registry["researcher"]
    assert {"search", "summarize", "cite", "literature_review"}.issubset(card.capabilities)
    assert card.status == "available"
    assert card.input_schema == {}
