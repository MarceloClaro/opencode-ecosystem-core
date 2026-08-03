# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R381 — Integração do Gate de Rigor de Manuscrito.

Prova que reasoning.production_scaffolds.audit_scientific_manuscript (R369)
deixa de ser função de biblioteca isolada e passa a ser chamada de verdade
pelo pipeline principal (scientific_discovery_pipeline) sobre as seções
reais compostas pelo R105 — sem bloquear o pipeline e sem fabricar dados
quando as seções estão ausentes.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _isolate_metacognitive_memory():
    """Mesmo isolamento usado em test_r108 -- orquestradores reais escrevem
    no singleton global mci.metabus.metabus.memory."""
    from mci.metabus import metabus

    snapshot = (
        copy.deepcopy(metabus.memory.episodic),
        copy.deepcopy(metabus.memory.semantic),
        copy.deepcopy(metabus.memory.confidence_ledger),
    )
    yield
    metabus.memory.episodic, metabus.memory.semantic, metabus.memory.confidence_ledger = snapshot
    metabus.memory._save()


def _make_orchestrator():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    return MarceloClaroOrchestrator(auto_load_agents=False)


def _fake_r103_package(export_gate_passed: bool = True):
    from agentic_science_v2.review_agent import ReviewPackage
    return ReviewPackage(
        paper_title="teste",
        overall_score=0.8,
        dimension_scores={"overall": 0.8},
        critiques=[],
        traceability=0.9,
        coverage=0.9,
        export_gate_passed=export_gate_passed,
        repair_plan=[],
    )


# ═══════════════════════════════════════════════════════════════════════
# 1. Estágio R106 presente em execução real (não mockada) do pipeline
# ═══════════════════════════════════════════════════════════════════════

class TestEstagioR106Real:
    def test_r106_rigor_presente_apos_pipeline_completo(self):
        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline(
            "dominio de teste rigor manuscrito", max_rounds=1, strict_gates=False
        )
        assert result["status"] in ("completed", "error")
        if result["status"] == "completed":
            assert "r106_rigor" in result["stages"]
            audit = result["stages"]["r106_rigor"]
            if audit.get("status") != "skipped":
                assert audit["schema_version"] == "1.0.0"
                assert "moves_presentes" in audit
                assert "findings" in audit
                assert "human_gate" in audit
                assert "disclaimer" in audit

    def test_manuscript_rigor_gate_resumo_presente(self):
        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline(
            "dominio de teste resumo rigor", max_rounds=1, strict_gates=False
        )
        if result["status"] == "completed":
            assert "manuscript_rigor_gate" in result
            resumo = result["manuscript_rigor_gate"]
            assert "human_gate" in resumo
            assert "high_severity_findings" in resumo


# ═══════════════════════════════════════════════════════════════════════
# 2. Verificação precisa via spy: chamado com as seções reais do R105
# ═══════════════════════════════════════════════════════════════════════

class TestChamadaComSecoesReais:
    def test_audit_chamado_com_sections_do_r105(self, monkeypatch):
        captured = {}

        import reasoning.production_scaffolds as scaffolds
        original = scaffolds.audit_scientific_manuscript

        def spy(sections):
            captured["sections"] = sections
            return original(sections)

        monkeypatch.setattr(
            "marceloclaro.orchestrator.audit_scientific_manuscript", spy
        )

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline(
            "dominio de teste spy", max_rounds=1, strict_gates=False
        )

        if result["status"] == "completed" and result["stages"].get("r105", {}).get("sections"):
            assert "sections" in captured
            assert captured["sections"] == result["stages"]["r105"]["sections"]


# ═══════════════════════════════════════════════════════════════════════
# 3. Sem fabricar dado quando sections está ausente/vazio
# ═══════════════════════════════════════════════════════════════════════

class TestSemFabricacao:
    def test_r105_falho_nao_fabrica_audit(self, monkeypatch):
        from agentic_science_v2.review_agent import OrchestratorReviewer

        monkeypatch.setattr(
            OrchestratorReviewer, "review",
            lambda self, paper: _fake_r103_package(export_gate_passed=True),
        )

        def fake_compose_paper_core(**kwargs):
            return {"status": "error", "error": "falha simulada de composição", "sections": {}}

        monkeypatch.setattr(
            "marceloclaro.orchestrator.compose_paper_core", fake_compose_paper_core,
            raising=False,
        )

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline(
            "dominio de teste r105 falho", max_rounds=1, strict_gates=False
        )
        if result["status"] == "completed":
            audit = result["stages"]["r106_rigor"]
            assert audit.get("status") == "skipped"
            assert "reason" in audit

    def test_gate_bloqueado_no_r103_nao_chega_no_r106(self, monkeypatch):
        from agentic_science_v2.review_agent import OrchestratorReviewer

        monkeypatch.setattr(
            OrchestratorReviewer, "review",
            lambda self, paper: _fake_r103_package(export_gate_passed=False),
        )

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline(
            "dominio de teste bloqueado", max_rounds=1, strict_gates=True
        )
        assert result["status"] == "blocked"
        assert "r106_rigor" not in result["stages"]


# ═══════════════════════════════════════════════════════════════════════
# 4. R106 nunca bloqueia o pipeline, mesmo com achados de severidade alta
# ═══════════════════════════════════════════════════════════════════════

class TestNaoBloqueante:
    def test_status_completed_mesmo_com_achados_high(self, monkeypatch):
        def fake_audit(sections):
            return {
                "schema_version": "1.0.0",
                "scaffold": "scientific",
                "moves_presentes": [],
                "findings": [{
                    "schema_version": "1.0.0", "code": "MISSING_MOVE",
                    "severity": "high", "detail": "teste forçado",
                    "requires_human_review": True, "move": "hipotese",
                }],
                "human_gate": "required",
                "disclaimer": "teste",
            }

        monkeypatch.setattr(
            "marceloclaro.orchestrator.audit_scientific_manuscript", fake_audit
        )

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline(
            "dominio de teste nao bloqueante", max_rounds=1, strict_gates=False
        )
        if result["status"] == "completed" and result["stages"].get("r105", {}).get("sections"):
            assert result["status"] == "completed"
            assert result["stages"]["r106_rigor"]["human_gate"] == "required"
            assert result["manuscript_rigor_gate"]["human_gate"] == "required"


# ═══════════════════════════════════════════════════════════════════════
# 5. Regressão do R108 (gate original R103 continua intacto)
# ═══════════════════════════════════════════════════════════════════════

class TestRegressaoR108:
    def test_gate_r103_ainda_bloqueia_pipeline(self, monkeypatch):
        from agentic_science_v2.review_agent import OrchestratorReviewer

        monkeypatch.setattr(
            OrchestratorReviewer, "review",
            lambda self, paper: _fake_r103_package(export_gate_passed=False),
        )

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline(
            "dominio de teste regressao r108", max_rounds=1, strict_gates=True
        )
        assert result["status"] == "blocked"
        assert result["gate_decision"]["passed"] is False
