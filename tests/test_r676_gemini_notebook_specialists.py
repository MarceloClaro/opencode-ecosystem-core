"""R676: perfis carregáveis e atribuição real pelo Blackboard em estado isolado."""
import ast
import importlib.util
from pathlib import Path

import pytest
import yaml

from marceloclaro.catalog_loader import load_catalog_definitions
from integrations.opencode_cli import _catalog_agents, build_config

ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    "gemini-notebook-audit": ["gemini_notebook_audit", "notebook_evidence_integrity"],
    "gemini-notebook-upstream": ["gemini_notebook_upstream", "upstream_source_provenance"],
    "gemini-notebook-transport": ["gemini_notebook_transport", "notebook_protocol_transport"],
}


@pytest.mark.parametrize("slug,tags", ROLES.items())
def test_specialist_has_loadable_contract_and_current_methods(slug, tags):
    path = ROOT / "agents/catalog" / (slug + ".md")
    assert path.is_file()
    meta = yaml.safe_load(path.read_text().split("---", 2)[1])
    card = next(item for item in load_catalog_definitions() if item["agent_id"] == slug)
    assert set(tags).issubset(card["capabilities"])
    assert card["metadata"]["a2a_version"] == "1.0"
    assert meta["capability_state"] == "declared" and meta["language"] == "pt-BR"
    assert "model" not in meta
    assert meta["skills"] and all(item["examples"] for item in meta["skills"])
    tree = ast.parse((ROOT / "marceloclaro/orchestrator.py").read_text())
    core = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MarceloClaroOrchestrator")
    methods = {node.name for node in core.body if isinstance(node, ast.FunctionDef)}
    assert set(meta["method_contracts"]["orchestrator"]).issubset(methods)
    assert "gemini_notebook_action" in meta["method_contracts"]["orchestrator"]


@pytest.mark.parametrize("slug", ROLES)
def test_compilation_has_explicit_permissions_and_primary_route(slug):
    card = _catalog_agents()[slug]
    assert card["mode"] == "subagent"
    assert card["prompt"] == "{file:./agents/catalog/" + slug + ".md}"
    assert card["permission"]["task"] == "deny"
    assert card["permission"]["bash"]["*"] == "deny"
    assert card["permission"]["edit"] == ("allow" if slug == "gemini-notebook-transport" else "deny")
    config = build_config()
    assert config["command"]["gemini-notebook"]["agent"] == config["default_agent"] == "marceloclaro"


@pytest.fixture(scope="module")
def central_probe(tmp_path_factory):
    # Reutiliza o ensaio A2A isolado R669, com os três novos papéis como entrada.
    spec = importlib.util.spec_from_file_location("_r676_a2a_probe", ROOT / "tests/test_r669_requested_agents.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROLES = ROLES
    return module.central_probe.__wrapped__(tmp_path_factory)


def test_actual_a2a_registration_and_missing_capability(central_probe):
    assert central_probe["registry"] == sorted(ROLES)
    assert central_probe["catalog_size"] == 3
    assert central_probe["semantic_registration"] == sorted(ROLES)
    assert {item["agent_id"] for item in central_probe["bootstrap"]} == set(ROLES)
    assert central_probe["missing"]["assigned_to"] is None


@pytest.mark.parametrize("slug", ROLES)
def test_only_central_orchestrator_assigns_without_fake_completion(central_probe, slug):
    route = central_probe["routes"][slug]
    assert route["assigned_to"] == slug and route["eligible"] == [slug]
    assert route["status"] == "assigned"
    assert route["context"]["metacognitive_briefing"]["orchestrator"] == "marceloclaro"
    assert central_probe["inference_executed"] is False
