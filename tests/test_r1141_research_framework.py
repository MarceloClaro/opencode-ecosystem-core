"""Framework de pesquisa GJQ no Core (R1141)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

import integrations.gjq_research_framework as framework

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "integrations/gjq_runtime_mcp.py"


def test_status_is_local_and_catalogued():
    payload = framework.status()
    assert payload["framework"] == "core-gjq-quantum-research"
    assert payload["network_access"] is False
    assert payload["hardware_executed"] is False
    assert payload["catalog"]["experiments"]
    assert payload["framework_ready"] is True
    assert payload["agents"]["research"] == "gjq-quantum-research"


def test_plan_has_phases_gates_and_hash():
    payload = framework.plan(
        "Comparar layouts com desenho pareado",
        backend_name="FAS-CPU",
        shots=2048,
        required_capabilities=["research", "audit"],
    )
    assert payload["executed"] is False
    assert payload["hardware_executed"] is False
    assert payload["shots"] == 2048
    assert payload["phases"]
    assert payload["gates"]["confirm"] is True
    assert payload["routed_agents"]["research"] == "gjq-quantum-research"
    assert len(payload["manifest_sha256"]) == 64


def test_domain_specific_plan():
    classification = framework.plan(
        "classificar padroes", backend_name="FAS-CPU", domain="classification"
    )
    assert classification["domain"] == "classification"
    assert "feature map" in " ".join(classification["phases"])
    assert "classification" in classification["routed_agents"]
    cooking = framework.plan(
        "otimizar processo", backend_name="FAS-CPU", domain="cooking"
    )
    assert cooking["domain"] == "cooking"
    assert "sensorial" in " ".join(cooking["phases"])
    with pytest.raises(ValueError):
        framework.plan("x", backend_name="FAS-CPU", domain="desconhecido")


def test_plan_rejects_unknown_objective_or_backend():
    with pytest.raises(ValueError):
        framework.plan("")
    with pytest.raises(ValueError):
        framework.plan("x", backend_name="nao-existe")
    with pytest.raises(ValueError):
        framework.plan("x", experiment="E99")


def test_mcp_exposes_research_tools():
    spec = importlib.util.spec_from_file_location("gjq_mcp_research", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    tools = module.create_server()._tool_manager._tools
    assert "gjq_research_status" in tools
    assert "gjq_research_plan" in tools
    status = tools["gjq_research_status"].fn()
    assert status["network_access"] is False
    plan = tools["gjq_research_plan"].fn("pesquisa", "FAS-CPU", None, 1024, False, None)
    assert plan["executed"] is False
