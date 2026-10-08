"""R669: cartões carregáveis, permissões e roteamento real em estado isolado."""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

import pytest
import yaml

from marceloclaro import catalog_loader


ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    "scientific-capabilities-audit": ("scientific_capabilities_audit", "evidence_integrity"),
    "simulation-game-audit": ("simulation_game_audit", "game_theory"),
    "book-mcp": ("book_mcp", "schema_validation"),
    "book-finetuning": ("book_finetuning", "group_split"),
    "library-architecture": ("library_architecture", "source_provenance"),
    "hooks-integration": ("hooks_integration", "fail_closed"),
    "mcp-cli-integration": ("mcp_cli_integration", "protocol_verification"),
    "live-mirofish-hermes": ("live_mirofish_hermes", "external_runtime_inference"),
}


def card_path(slug):
    path = ROOT / "agents/catalog" / f"{slug}.md"
    assert path.is_file(), f"Perfil operacional ausente: {slug}"
    return path


def metadata(slug):
    content = card_path(slug).read_text(encoding="utf-8")
    return yaml.safe_load(content.split("---", 2)[1])


@pytest.mark.parametrize("slug", ROLES)
def test_each_requested_card_loads_with_capability_contract(tmp_path, slug):
    shutil.copy2(card_path(slug), tmp_path / f"{slug}.md")
    definitions = catalog_loader.load_catalog_definitions(str(tmp_path))
    assert len(definitions) == 1
    card = definitions[0]
    assert card["agent_id"] == slug
    assert set(ROLES[slug]).issubset(card["capabilities"])
    assert card["skills"] and all(skill["examples"] for skill in card["skills"])
    assert card["metadata"]["a2a_version"] == "1.0"
    assert card["metadata"]["extended_agent_card"] is True
    assert "model" not in metadata(slug), "Não atrelar o perfil a um modelo específico."


@pytest.mark.parametrize("slug", ROLES)
def test_compiled_permissions_and_prompt_reference_are_operational(slug):
    from integrations.opencode_cli import _catalog_agents

    card_path(slug)
    compiled = _catalog_agents()[slug]
    assert compiled["mode"] == "subagent"
    assert compiled["prompt"] == f"{{file:./agents/catalog/{slug}.md}}"
    permissions = compiled["permission"]
    assert all(permissions[key] == "allow" for key in ("read", "glob", "grep"))
    bash = permissions["bash"]
    assert isinstance(bash, dict) and bash["*"] == "deny"
    assert bash["python3 -m pytest tests/test_r669_requested_agents.py -q"] == "allow"
    assert any("test_r" in command and action == "allow" for command, action in bash.items())
    expected_edit = "allow" if slug in {"hooks-integration", "mcp-cli-integration"} else "deny"
    assert permissions["edit"] == expected_edit
    assert permissions["webfetch"] == "deny"
    assert permissions["task"] == "deny", "Delegação adicional passa pela entrada central."


@pytest.mark.parametrize("slug", ROLES)
def test_method_guidance_resolves_to_existing_core_interfaces(slug):
    meta = metadata(slug)
    contracts = meta["method_contracts"]
    tree = ast.parse((ROOT / "marceloclaro/orchestrator.py").read_text(encoding="utf-8"))
    orchestrator = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                        and node.name == "MarceloClaroOrchestrator")
    methods = {node.name for node in orchestrator.body if isinstance(node, ast.FunctionDef)}
    assert contracts["orchestrator"]
    assert set(contracts["orchestrator"]).issubset(methods)
    assert meta["capability_state"] == "declared"
    native = {"read", "glob", "grep", "bash", "write", "edit"}
    assert set(meta["tools"]).issubset(native)
    assert set(ROLES[slug]).issubset(meta["tags"])
    assert meta["language"] == "pt-BR"


@pytest.fixture(scope="module")
def central_probe(tmp_path_factory):
    isolated = tmp_path_factory.mktemp("r669")
    catalog = isolated / "catalog"
    catalog.mkdir()
    for slug in ROLES:
        shutil.copy2(card_path(slug), catalog / f"{slug}.md")
    source = textwrap.dedent(r'''
        import importlib, json, os, sys
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch

        roles = json.loads(sys.argv[1])
        base = Path(sys.argv[2])
        loader = importlib.import_module("marceloclaro.catalog_loader")
        loader.CATALOG_DIR = str(base / "catalog")
        original_load_definitions = loader.load_catalog_definitions
        loader.load_catalog_definitions = lambda *args, **kwargs: original_load_definitions(str(base / "catalog"))
        bus_module = importlib.import_module("mci.metabus")
        board_module = importlib.import_module("mci.blackboard")
        bus, board = bus_module.metabus, board_module.blackboard
        orch_module = importlib.import_module("marceloclaro.orchestrator")
        bootstrap = importlib.import_module("mci.agent_registry_bootstrap")
        bootstrap_cards = bootstrap.load_catalog_agents(base / "catalog")

        # Sem embeddings ou executor MIRA: CFP/ALL_OF, bus, cartões, gate de
        # confiança e atribuição permanecem reais. A redução só escolhe o ID
        # único já habilitado pelo Blackboard, com descrição explícita.
        registered_skills = []
        semantic = SimpleNamespace(
            register_agent_skills=lambda **kw: registered_skills.append(kw["agent_id"]),
            get_stats=lambda: {"handbook": {"total_skills": len(registered_skills)},
                               "engine": {"provider": "isolated-no-embedding"}})
        class ExactRequestedID:
            def route(self, description):
                return {"agent": description.split(":", 1)[0],
                        "confidence": 1.0, "method": "explicit-test-id"}
        with patch.dict(sys.modules, {"transformer.semantic_matcher": SimpleNamespace(semantic_matcher=semantic)}), \
             patch.object(orch_module, "register_all_agents", lambda bus: 0), \
             patch.object(orch_module.MarceloClaroOrchestrator, "register_mira_agent", lambda self: None):
            orch = orch_module.MarceloClaroOrchestrator(
                auto_load_agents=True, reduction_layer=ExactRequestedID())
        assert Path(bus_module.STATE_DIR) == base / "state"

        result = {"catalog_size": orch.catalog_size, "registry": sorted(board.registry),
                  "semantic_registration": sorted(registered_skills), "routes": {},
                  "bootstrap": bootstrap_cards, "method_results": {}}
        from rag.book_library import LocalBookLibrary
        orch._book_library = LocalBookLibrary(base / "books", base / "library.sqlite3")
        (base / "books").mkdir()
        from marceloclaro.integration_service import CoreIntegrationService
        config_repo = base / "config"
        config_repo.mkdir()
        (config_repo / "AGENTS.md").write_text("Instruções locais", encoding="utf-8")
        (config_repo / "primary.md").write_text("Perfil central", encoding="utf-8")
        (config_repo / "opencode.json").write_text(json.dumps({
            "default_agent": "marceloclaro", "instructions": ["AGENTS.md"],
            "agent": {"marceloclaro": {"mode": "primary", "prompt": "{file:./primary.md}"}},
            "command": {}, "mcp": {}}), encoding="utf-8")
        inventory = SimpleNamespace(inventory=lambda: {
            "total": 0, "by_kind": {}, "ecosystems_present": [], "ecosystems_missing": []})
        orch._integration_service = CoreIntegrationService(config_repo, registry=inventory)

        for slug, required in roles.items():
            task_id = orch.delegate(slug + ": procedimento local", required_capabilities=required,
                                    context={"validation_scope": "synthetic_local"})
            task = board.tasks[task_id]
            result["routes"][slug] = {"task_id": task_id, "assigned_to": task.assigned_to,
                                    "status": task.status, "context": task.context,
                                    "eligible": orch.pending_cfps.get(task_id)}
        missing = orch.delegate("book-mcp: capacidade ausente",
                               required_capabilities=["book_mcp", "r669_nonexistent_capability"])
        result["missing"] = {"status": board.tasks[missing].status,
                             "assigned_to": board.tasks[missing].assigned_to}

        # Chamadas funcionais locais reais, com entrada sintética. Isto é prova
        # dos métodos que os perfis orientam; não é inferência dos sete agentes.
        result["method_results"]["scientific-capabilities-audit"] = orch.knowledge_evolution_plan(
            problem="Auditar capacidades declaradas", target_state=["synthetic_analysis"],
            modules={"synthetic": [{"id": "synthetic_analysis", "state": "declared"}]}, candidates=[])
        result["method_results"]["simulation-game-audit"] = orch.nash_analysis("prisoners_dilemma")
        result["method_results"]["book-mcp"] = orch.library_query("MCP", top_k=1)
        result["method_results"]["library-architecture"] = orch.library_status()
        result["method_results"]["book-finetuning"] = orch.finetuning_prepare_data([
            {"id": str(i), "group_id": "source-" + str(i),
             "input": "Pergunta " + str(i), "output": "Resposta " + str(i)} for i in range(3)], seed=42)
        from hooks.policy import check_bash
        result["method_results"]["hooks-integration"] = {
            "status": orch.integration_status(), "destructive": check_bash("rm -rf /"),
            "local_test": check_bash("python3 -m pytest tests/test_r669_requested_agents.py -q")}
        result["method_results"]["mcp-cli-integration"] = orch.integration_status()
        result["method_results"]["live-mirofish-hermes"] = orch.scientific_runtime_run(
            runtime="hermes", prompt="Entrada sintética delimitada", model="local-test",
            runtime_dir=str(base / "missing-runtime"), output_dir=str(base / "runtime-output"))
        result["events"] = [json.loads(line) for line in Path(bus_module.EVENTS_FILE).read_text().splitlines()]
        result["inference_executed"] = False
        print("R669_RESULT=" + json.dumps(result, ensure_ascii=False))
    ''')
    env = dict(os.environ, MCI_STATE_DIR=str(isolated / "state"),
               OPENCODE_HOOKS_AUDIT=str(isolated / "hooks.jsonl"))
    completed = subprocess.run([sys.executable, "-c", source, json.dumps(ROLES), str(isolated)],
                               cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, completed.stderr[-5000:]
    output = next(line for line in completed.stdout.splitlines() if line.startswith("R669_RESULT="))
    return json.loads(output.partition("=")[2])


def test_auto_load_registers_actual_catalog_and_bootstrap_agrees(central_probe):
    result = central_probe
    assert result["catalog_size"] == len(ROLES)
    assert result["registry"] == sorted(ROLES)
    assert result["semantic_registration"] == sorted(ROLES)
    cards = {card["agent_id"]: card for card in result["bootstrap"]}
    assert set(cards) == set(ROLES)
    for slug, capabilities in ROLES.items():
        assert set(capabilities).issubset(cards[slug]["capabilities"])


@pytest.mark.parametrize("slug", ROLES)
def test_central_capability_routing_assigns_without_completing(central_probe, slug):
    route = central_probe["routes"][slug]
    assert route["assigned_to"] == slug
    assert route["eligible"] == [slug]
    assert route["status"] == "assigned"
    assert route["context"]["metacognitive_briefing"]["orchestrator"] == "marceloclaro"
    events = [event for event in central_probe["events"]
              if event.get("payload", {}).get("task_id") == route["task_id"]]
    sources = {event["topic"]: event["source"] for event in events}
    assert sources["task.post"] == sources["task.volunteer"] == "marceloclaro"
    assert sources["task.cfp"] == sources["task.assigned"] == "blackboard"
    assert "task.complete" not in sources
    assert central_probe["inference_executed"] is False


def test_all_of_requires_missing_capability_and_preserves_unassigned(central_probe):
    assert central_probe["missing"]["assigned_to"] is None
    assert central_probe["missing"]["status"] != "assigned"


def test_profile_method_paths_execute_scoped_local_checks(central_probe):
    result = central_probe["method_results"]
    science = result["scientific-capabilities-audit"]
    assert science["observed_capabilities"] == []
    assert science["metacognition"]["execution_promoted"] is False
    assert result["simulation-game-audit"]["equilibria"]
    assert result["book-mcp"]["abstained"] is True
    assert result["library-architecture"]["books"] == 0
    prepared = result["book-finetuning"]
    assert prepared["status"] == "accepted"
    assert prepared["manifest"]["effective_group_count"] == 3
    assert set(prepared["splits"]) == {"train", "validation", "test"}
    assert result["hooks-integration"]["destructive"]["allow"] is False
    assert result["hooks-integration"]["local_test"]["allow"] is True
    assert result["mcp-cli-integration"]["status"] == "config_checked"
    assert result["mcp-cli-integration"]["execution_verified"] is False
    assert result["live-mirofish-hermes"]["status"] == "blocked"
    assert result["live-mirofish-hermes"]["inference_executed"] is False
