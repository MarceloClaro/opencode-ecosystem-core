"""R678: contrato e atribuição central do especialista Library empty input audit."""
import ast
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from integrations.opencode_cli import _catalog_agents, build_config
from marceloclaro.catalog_loader import load_catalog_definitions

ROOT = Path(__file__).resolve().parents[1]
SLUG = "library-empty-input-audit"
ROLES = {SLUG: ["library_empty_input_audit", "empty_input_abstention"]}
METHODS = {"library_status", "library_query", "library_page", "integration_status"}


def test_card_loads_with_requested_name_and_declared_capability():
    path = ROOT / "agents/catalog" / (SLUG + ".md")
    assert path.is_file()
    meta = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
    card = next(item for item in load_catalog_definitions() if item["agent_id"] == SLUG)
    assert meta["display_name"] == "Library empty input audit"
    assert meta["language"] == "pt-BR" and meta["capability_state"] == "declared"
    assert meta["spec"] == "SPEC-935-R678-library-empty-input-specialist.md"
    assert "model" not in meta
    assert set(ROLES[SLUG]).issubset(card["capabilities"])
    assert card["metadata"]["a2a_version"] == "1.0"
    assert card["metadata"]["extended_agent_card"] is True
    assert meta["skills"] and all(skill["examples"] for skill in meta["skills"])


def test_method_contract_uses_only_existing_central_library_interfaces():
    path = ROOT / "agents/catalog" / (SLUG + ".md")
    meta = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
    tree = ast.parse((ROOT / "marceloclaro/orchestrator.py").read_text(encoding="utf-8"))
    orchestrator = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                        and node.name == "MarceloClaroOrchestrator")
    methods = {node.name for node in orchestrator.body if isinstance(node, ast.FunctionDef)}
    assert set(meta["method_contracts"]["orchestrator"]) == METHODS
    assert METHODS.issubset(methods)


def test_compiled_permissions_keep_read_only_audit_and_central_entry():
    card = _catalog_agents()[SLUG]
    assert card["mode"] == "subagent"
    assert card["prompt"] == "{file:./agents/catalog/" + SLUG + ".md}"
    permissions = card["permission"]
    assert all(permissions[key] == "allow" for key in ("read", "glob", "grep"))
    assert permissions["edit"] == permissions["webfetch"] == permissions["task"] == "deny"
    assert permissions["bash"]["*"] == "deny"
    assert permissions["bash"]["python3 -m pytest tests/test_r678_library_empty_input_specialist.py -q"] == "allow"
    assert permissions["bash"]["python3 -m pytest tests/test_r677_empty_library_request.py -q"] == "allow"
    assert build_config()["default_agent"] == "marceloclaro"


def test_saved_configuration_matches_generator():
    saved = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert SLUG in saved["agent"]
    assert saved == build_config()


@pytest.fixture(scope="module")
def central_probe(tmp_path_factory):
    # CFP/ALL_OF, Blackboard, MetaBus e registro A2A permanecem reais; o ensaio
    # isolado R669 não executa embeddings, LLMs ou inferência do especialista.
    spec = importlib.util.spec_from_file_location("_r678_a2a_probe", ROOT / "tests/test_r669_requested_agents.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROLES = ROLES
    return module.central_probe.__wrapped__(tmp_path_factory)


def test_actual_registration_bootstrap_and_missing_capability(central_probe):
    assert central_probe["registry"] == central_probe["semantic_registration"] == [SLUG]
    assert central_probe["catalog_size"] == 1
    assert {card["agent_id"] for card in central_probe["bootstrap"]} == {SLUG}
    assert central_probe["missing"]["assigned_to"] is None
    assert central_probe["missing"]["status"] != "assigned"


def test_actual_assignment_events_preserve_primary_route_without_fake_completion(central_probe):
    route = central_probe["routes"][SLUG]
    assert route["assigned_to"] == SLUG and route["eligible"] == [SLUG]
    assert route["status"] == "assigned"
    assert route["context"]["metacognitive_briefing"]["orchestrator"] == "marceloclaro"
    events = [event for event in central_probe["events"]
              if event.get("payload", {}).get("task_id") == route["task_id"]]
    sources = {event["topic"]: event["source"] for event in events}
    assert sources["task.post"] == sources["task.volunteer"] == "marceloclaro"
    assert sources["task.cfp"] == sources["task.assigned"] == "blackboard"
    assert "task.complete" not in sources
    assert central_probe["inference_executed"] is False
