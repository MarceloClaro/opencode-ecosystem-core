"""R1069: atenção executiva e Centro de Produção Global, sem executar terceiros."""
from __future__ import annotations

import asyncio
import sys

import pytest

from integrations.external_skills import ExternalSkill, plan, probe, status
from marceloclaro.production_center import ProductionCenter
from transformer.executive import ExecutiveAttention


def fake_registry(tmp_path, *, requires_consent: bool = False,
                  safe_argv: tuple[str, ...] = ()):
    path = tmp_path / "fake-skill"
    path.mkdir()
    (path / "SKILL.md").write_text("---\nname: fake\n---\n", encoding="utf-8")
    (path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (path / "run.py").write_text("print('noop')\n", encoding="utf-8")
    entry = ExternalSkill(
        skill_id="fake", path=path, license="MIT",
        kind="state-machine-skill", entrypoint="run.py",
        dependencies=(), requires_consent=requires_consent,
        safe_argv=safe_argv,
    )
    return {"fake": entry}


def test_executive_attention_prefers_specify_over_stop():
    decision = ExecutiveAttention().evaluate(
        "produzir um diagrama da arquitetura",
        {"stage": "intake", "budget": 8, "consent": False, "evidence_count": 0},
        [
            {"action_id": "specify", "description": "especificar escopo e critérios",
             "stage": "intake", "risk": 0.0, "cost": 0.5, "evidence_gain": 0.6,
             "confidence": 0.8, "available": True},
            {"action_id": "stop", "description": "parar e devolver bloqueio",
             "stage": "intake", "risk": 0.0, "cost": 0.1, "evidence_gain": 0.0,
             "confidence": 0.2, "available": True},
        ],
    )
    assert decision["selected"] == "specify"
    assert decision["ranking"][0][0] == "specify"
    assert abs(sum(decision["weights"].values()) - 1.0) < 1e-9
    assert "não é rede neural" in decision["policy"]


def test_executive_attention_hard_gates_consent_and_budget():
    decision = ExecutiveAttention().evaluate(
        "executar algo",
        {"stage": "execute", "budget": 1, "consent": False, "evidence_count": 1},
        [
            {"action_id": "risky", "description": "executar adaptador com conta",
             "stage": "execute", "risk": 0.8, "cost": 0.5, "evidence_gain": 0.5,
             "confidence": 0.8, "available": True, "requires_consent": True},
            {"action_id": "expensive", "description": "executar algo caro",
             "stage": "execute", "risk": 0.1, "cost": 2.0, "evidence_gain": 0.5,
             "confidence": 0.8, "available": True},
        ],
    )
    assert "consent_required" in decision["excluded"]["risky"]
    assert "budget_exceeded" in decision["excluded"]["expensive"]


def test_production_center_completes_plan_without_execution(tmp_path):
    center = ProductionCenter(registry=fake_registry(tmp_path))
    report = center.run("documentar o fluxo de produção", budget=8.0)
    assert report["status"] == "completed"
    assert report["stage"] == "complete"
    assert report["selected_adapter"] == "fake"
    assert [row["action"] for row in report["history"]] == [
        "specify", "route", "execute:fake", "verify", "reflect", "deliver",
    ]
    assert report["execution_plan"]["status"] == "planned"
    assert report["execution_plan"]["executed"] is False
    assert report["confidence_promoted"] is False
    assert report["external_validation"] is False
    assert report["human_review_required"] is True


def test_safe_checks_run_only_declared_read_only_argv(tmp_path):
    safe = (sys.executable, "-c", "print('safe-ok')")
    center = ProductionCenter(registry=fake_registry(tmp_path, safe_argv=safe))
    without = center.run("documentar o fluxo")
    assert "safe_check" not in (without["execution_plan"] or {})

    with_safe = center.run("documentar o fluxo", allow_safe_checks=True)
    assert with_safe["status"] == "completed"
    check = with_safe["execution_plan"]["safe_check"]
    assert check["returncode"] == 0
    assert "safe-ok" in check["stdout"]
    assert check["read_only"] is True


def test_production_center_requires_consent(tmp_path):
    center = ProductionCenter(registry=fake_registry(tmp_path, requires_consent=True))
    blocked = center.run("criar um perfil de pessoa", consent=False)
    assert blocked["status"] == "awaiting_consent"
    assert blocked["selected_adapter"] == "fake"
    assert any(row["action"] == "consent:fake" for row in blocked["history"])

    allowed = center.run("criar um perfil de pessoa", consent=True)
    assert allowed["status"] == "completed"
    assert allowed["selected_adapter"] == "fake"


def test_production_center_budget_is_bounded(tmp_path):
    center = ProductionCenter(registry=fake_registry(tmp_path))
    report = center.run("produzir algo", budget=1.0)
    assert report["status"] in {"completed", "budget_exhausted"}
    assert report["cost_spent"] <= 8.0
    assert report["budget"] >= 0.0


def test_external_registry_status_and_plan(tmp_path):
    registry = fake_registry(tmp_path)
    current = status(registry=registry)["adapters"][0]
    assert current["ready"] is True
    assert current["status"] == "ready"
    planned = plan("fake", "documentar o fluxo", registry=registry)
    assert planned["status"] == "planned"
    assert planned["executed"] is False
    assert "handoff" in planned


def test_external_registry_consent_gate(tmp_path):
    registry = fake_registry(tmp_path, requires_consent=True)
    blocked = plan("fake", "criar perfil", registry=registry)
    assert blocked["status"] == "consent_required"
    allowed = plan("fake", "criar perfil", consent=True, registry=registry)
    assert allowed["status"] == "planned"


def test_probe_without_rea_sources_is_unsupported(tmp_path):
    registry = fake_registry(tmp_path)
    result = probe("fake", registry=registry)
    assert result["status"] == "unsupported"
    assert result["executed"] is False


def test_mcp_production_routes_to_primary(monkeypatch):
    from integrations import ecosystem_mcp

    calls = []

    class Primary:
        def production_center_action(self, config):
            calls.append(config)
            return {"status": "planned", "executed": False}

    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: Primary())
    result = asyncio.run(ecosystem_mcp.ecosystem_production(
        {"operation": "plan", "goal": "produzir um diagrama"}))
    assert calls == [{"operation": "plan", "goal": "produzir um diagrama"}]
    assert result == {"status": "planned", "executed": False}
    names = {tool.name for tool in asyncio.run(ecosystem_mcp.mcp.list_tools())}
    assert "ecosystem_production" in names
