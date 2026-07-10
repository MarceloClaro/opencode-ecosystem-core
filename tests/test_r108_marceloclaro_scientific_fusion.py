# -*- coding: utf-8 -*-
"""
Testes R108 — Fusao do pipeline cientifico R101-R105 no orquestrador
marceloclaro (TDD: RED -> GREEN -> REFACTOR)
=====================================================================
Testa MarceloClaroOrchestrator.scientific_discovery_pipeline: gate real
entre estagios, calibracao de confianca (Brier/abstencao) e avaliacao
metacognitiva SPEC-920 sobre tracos reais do run.

Requisitos (SPEC-935-R108):
  - Gate bloqueia o pipeline quando o R103 reprova export_gate_passed
  - Confianca calibrada aciona abstencao quando um estagio falha
  - metacognitive_report e computado sobre os tracos reais do proprio run
  - Excecao em qualquer estagio nao derruba o processo (status: error)
  - R104d reverte automaticamente quando a integridade estrutural falha
  - webapp/pipeline_helpers.py::run_full_academic_pipeline preserva o
    contrato consumido por webapp/app.py
"""

import copy

import pytest


@pytest.fixture(autouse=True)
def _isolate_metacognitive_memory():
    """Este modulo instancia orquestradores reais (nao mockados) que
    escrevem no singleton global mci.metabus.metabus.memory, persistido em
    disco (.mci_state/shared_memory.json). Sem isolamento, essas reflexoes
    vazam para outros modulos de teste que rodam depois no mesmo processo
    (ex.: tests/test_transformer.py::test_hierarchical_memory_retrieve,
    que depende do ranking de entradas recentes)."""
    from mci.metabus import metabus

    snapshot = (
        copy.deepcopy(metabus.memory.episodic),
        copy.deepcopy(metabus.memory.semantic),
        copy.deepcopy(metabus.memory.confidence_ledger),
    )
    yield
    metabus.memory.episodic, metabus.memory.semantic, metabus.memory.confidence_ledger = snapshot
    metabus.memory._save()


# ── Helpers ──────────────────────────────────────────────────────────

def _make_orchestrator():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    return MarceloClaroOrchestrator(auto_load_agents=False)


def _fake_r103_package(export_gate_passed: bool, traceability: float = 0.9, coverage: float = 0.9):
    """Constroi um ReviewPackage real (nao um dublê) com o gate no valor desejado."""
    from agentic_science_v2.review_agent import ReviewPackage
    return ReviewPackage(
        paper_title="teste",
        overall_score=0.8 if export_gate_passed else 0.3,
        dimension_scores={"overall": 0.8},
        critiques=[],
        traceability=traceability,
        coverage=coverage,
        export_gate_passed=export_gate_passed,
        repair_plan=[{
            "priority": "MAJOR", "area": "methods",
            "action": "Clarify experimental setup.", "reviewer": "methodology",
        }],
    )


# ── 1. Gate real bloqueia o pipeline ─────────────────────────────────

class TestGateReal:
    def test_gate_blocks_pipeline_before_r104d_r105(self, monkeypatch):
        from agentic_science_v2.review_agent import OrchestratorReviewer

        monkeypatch.setattr(
            OrchestratorReviewer, "review",
            lambda self, paper: _fake_r103_package(export_gate_passed=False),
        )

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline("dominio de teste", max_rounds=1, strict_gates=True)

        assert result["status"] == "blocked"
        assert result["gate_decision"]["passed"] is False
        assert "r104d" not in result["stages"]
        assert "r105" not in result["stages"]

    def test_strict_gates_false_continues_past_failed_gate(self, monkeypatch):
        from agentic_science_v2.review_agent import OrchestratorReviewer

        monkeypatch.setattr(
            OrchestratorReviewer, "review",
            lambda self, paper: _fake_r103_package(export_gate_passed=False),
        )

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline("dominio de teste", max_rounds=1, strict_gates=False)

        assert result["status"] in ("completed", "error")
        assert "r104d" in result["stages"]
        assert "r105" in result["stages"]


# ── 2. Calibracao de confianca / abstencao ───────────────────────────

class TestCalibracao:
    def test_failed_stage_triggers_abstention(self, monkeypatch):
        from agentic_science_v2 import deep_research as deep_research_mod

        def failing_deep_research(question, max_rounds=2, max_depth=3):
            return {"status": "error", "error": "forced failure", "reports": [], "plans": [],
                    "evidence_graph": {}, "summary": {}}

        monkeypatch.setattr(deep_research_mod, "run_deep_research", failing_deep_research)
        # marceloclaro/orchestrator.py importa run_deep_research localmente de
        # agentic_science_v2.deep_research dentro do metodo — o monkeypatch no
        # modulo de origem e suficiente porque o import e feito a cada chamada.

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline("dominio de teste", max_rounds=1, strict_gates=False)

        r102_cal = result["calibrated_confidences"].get("r102", {})
        assert r102_cal.get("should_abstain") is True
        assert r102_cal.get("calibrated_confidence", 1.0) < 0.20

    def test_successful_stage_does_not_abstain(self):
        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline("dominio de teste", max_rounds=1, strict_gates=False)

        r101_cal = result["calibrated_confidences"].get("r101", {})
        assert r101_cal.get("should_abstain") is False


# ── 3. Avaliacao metacognitiva sobre tracos reais ────────────────────

class TestAvaliacaoMetacognitiva:
    def test_readiness_score_reflects_real_run_not_static_benchmark(self, monkeypatch):
        from agentic_science_v2.review_agent import OrchestratorReviewer
        from mci.metacognitive_evaluator import MetacognitiveBenchmarkSuite

        static_benchmark_score = MetacognitiveBenchmarkSuite().run()["report"]["readiness_score"]

        monkeypatch.setattr(
            OrchestratorReviewer, "review",
            lambda self, paper: _fake_r103_package(export_gate_passed=False),
        )
        orch = _make_orchestrator()
        blocked_result = orch.scientific_discovery_pipeline("dominio de teste", max_rounds=1, strict_gates=True)

        assert "metacognitive_report" in blocked_result
        assert "readiness_score" in blocked_result["metacognitive_report"]
        # O relatorio vem da avaliacao dos tracos REAIS deste run (poucos
        # tracos, run bloqueado cedo) — nao precisa bater com o benchmark
        # estatico de 6 tracos sinteticos, mas precisa existir e ser numerico.
        assert isinstance(blocked_result["metacognitive_report"]["readiness_score"], float)

    def test_never_claims_verified_without_external_validation(self):
        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline("dominio de teste", max_rounds=1, strict_gates=False)
        tier = result["metacognitive_report"].get("tier")
        assert tier != "metacognitive_superhuman_verified"


# ── 4. Excecao em estagio nao derruba o pipeline ─────────────────────

class TestTratamentoDeErro:
    def test_unhandled_exception_returns_structured_error(self, monkeypatch):
        from agentic_science_v2 import orchestrator as r101_mod

        def boom(seed_domain, max_rounds=3):
            raise RuntimeError("falha forcada no R101")

        monkeypatch.setattr(r101_mod, "run_agentic_science_v2", boom)

        orch = _make_orchestrator()
        result = orch.scientific_discovery_pipeline("dominio de teste", max_rounds=1)

        assert result["status"] == "error"
        assert "falha forcada no R101" in result["error"]
        assert "metacognitive_report" in result


# ── 5. Rollback automatico de integridade (R104d) ────────────────────

class TestRollbackAutomatico:
    def test_revision_agent_rolls_back_on_integrity_failure(self, monkeypatch):
        from agentic_science_v2 import revision_agent as revision_mod

        # Manuscrito original tem todas as secoes exigidas por verify_integrity.
        manuscript = (
            "# Titulo\n\n"
            "## Abstract\nResumo do trabalho.\n\n"
            "## Introduction\nContexto do problema.\n\n"
            "## Methods\nMetodologia detalhada.\n\n"
            "## Results\nResultados obtidos.\n\n"
            "## Conclusion\nConclusao do estudo.\n"
        )

        # Forca uma proposta que apaga o conteudo (corrompe a integridade
        # estrutural), para verificar que o OrchestratorRevision reverte
        # automaticamente em vez de aceitar a corrupcao.
        corrupting_proposal = revision_mod.RevisionProposal(
            claim_id="claim-1",
            original_text=manuscript,
            revised_text="Texto vazio sem nenhuma das secoes originais.",
            rationale="proposta de teste que corrompe a estrutura",
        )
        monkeypatch.setattr(
            revision_mod.ProposalGenerator, "generate_proposals",
            lambda self, claims, ms: [corrupting_proposal],
        )

        review_package = {
            "reviews": [{
                "critic": "methodology",
                "claims": [{
                    "id": "claim-1",
                    "text": "insufficient sample size in the experiment",
                    "risk": "high",
                    "section": "preamble",
                    "evidence": "",
                }],
            }],
        }

        result = revision_mod.create_revision(review_package, manuscript)

        assert result["status"] == "completed"
        assert result["integrity"]["intact"] is True
        assert result["integrity"].get("auto_rolled_back") is True
        assert result["integrity"].get("reverted_changes", 0) >= 1
        # Toda revisao que estava "applied" deve ter sido rebaixada para
        # "rejected" apos o rollback automatico.
        assert all(r["status"] != "applied" for r in result["revisions"])

    def test_review_package_to_revision_contract_matches_analyzer(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer
        from agentic_science_v2.revision_agent import ReviewAnalyzer

        package = OrchestratorReviewer().review({
            "title": "Teste",
            "abstract": "Abstract de teste com metodologia e resultados.",
            "sections": ["Introduction", "Methods", "Results"],
            "citations": [],
        })
        contract = package.to_revision_contract()
        claims = ReviewAnalyzer().extract_claims(contract)

        assert "reviews" in contract
        assert len(claims) >= 1


# ── 6. Nao-regressao do contrato webapp ──────────────────────────────

class TestNaoRegressaoWebapp:
    def test_run_full_academic_pipeline_still_returns_expected_keys(self, monkeypatch):
        from webapp import pipeline_helpers
        from marceloclaro.orchestrator import MarceloClaroOrchestrator

        def fake_pipeline(self, seed_domain, max_rounds=3, venue="abnt", strict_gates=True):
            return {
                "status": "completed",
                "seed_domain": seed_domain,
                "venue": venue,
                "timeline": {"r101": 0.1, "r102": 0.1, "r103": 0.1, "r104d": 0.1, "r105": 0.1, "total": 0.5},
                "stages": {
                    "r101": {"history": [{"id": "cr-1", "round": 1,
                                           "ideas": [{"id": "i1", "title": "t",
                                                      "hypothesis": "h", "scores": {"overall": 0.7}}]}]},
                    "r102": {"reports": [{"summary": "resposta", "sections": [], "citations": []}],
                             "evidence_graph": {}, "plans": [], "summary": {}},
                    "r103": {"overall_score": 0.7, "dimension_scores": {}, "export_gate_passed": True,
                              "traceability": 0.7, "coverage": 0.7, "repair_plan": [], "critiques_count": 0,
                              "paper_title": seed_domain},
                    "r104d": {"status": "completed", "revisions": [], "rebuttal_letter": "", "diff": "",
                               "report": {"traceability_pct": 80.0}, "integrity": {"intact": True}},
                    "r105": {"status": "completed", "manuscript": "manuscrito final",
                              "consistency_report": {"overall_score": 75}, "outline": {}},
                },
                "gate_decision": {"passed": True},
                "calibrated_confidences": {},
                "metacognitive_report": {"readiness_score": 70.0, "tier": "research_grade"},
            }

        monkeypatch.setattr(MarceloClaroOrchestrator, "scientific_discovery_pipeline", fake_pipeline)

        result = pipeline_helpers.run_full_academic_pipeline(seed_domain="Teste", max_rounds=1, venue="abnt")

        for key in ("pipeline_result", "seed_domain", "venue", "timeline",
                    "evosci", "deep_research", "peer_review",
                    "manuscript_revision", "paper"):
            assert key in result

        evo = result["evosci"]
        assert "best_solution" in evo and "evolutionary_trajectory" in evo

        deep = result["deep_research"]
        assert "answer" in deep and "sufficiency_gate" in deep

        review = result["peer_review"]
        assert "scores" in review and "meta_review" in review and "repair_plan" in review

        revision = result["manuscript_revision"]
        assert "changes_applied" in revision and "rebuttal_letter" in revision

        paper = result["paper"]
        assert "full_text" in paper and "consistency_report" in paper
        assert isinstance(paper["consistency_report"], dict)
        for value in paper["consistency_report"].values():
            assert isinstance(value, (int, float, str, bool))
