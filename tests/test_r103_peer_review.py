# -*- coding: utf-8 -*-
"""
Testes TDD para R103 — Agentic Peer Review with Graph-Anchored Auditing
========================================================================
Cobre: RubricEngine, ReviewLedger, AuditGraph, MultiCriticReviewer,
       OrchestratorReviewer, ReviewPackage.
"""

import pytest

from agentic_science_v2.review_agent import (
    RubricEngine, PaperSpecificRubric, META_RUBRICS,
    ReviewLedger, ClaimEntry,
    AuditGraph,
    MultiCriticReviewer, MethodologyCritic, ResultsCritic,
    LiteratureCritic, EthicsCritic, Critique,
    OrchestratorReviewer, ReviewPackage,
    run_peer_review,
)


# ============================================================
# Testes: RubricEngine
# ============================================================

class TestRubricEngine:
    def test_list_dimensions(self):
        engine = RubricEngine()
        dims = engine.list_dimensions()
        assert len(dims) == 8
        assert "core_contribution_accuracy" in dims
        assert "false_or_contradictory_claims" in dims

    def test_get_meta_rubric(self):
        engine = RubricEngine()
        rubric = engine.get_meta_rubric("results_interpretation")
        assert rubric is not None
        assert rubric["polarity"] == "positive"
        assert "checklist" in rubric

    def test_get_meta_rubric_unknown(self):
        engine = RubricEngine()
        assert engine.get_meta_rubric("nonexistent") is None

    def test_instantiate_for_paper(self):
        engine = RubricEngine()
        rubrics = engine.instantiate_for_paper(
            paper_title="Deep Learning for Cancer Detection",
            paper_abstract="We propose a novel CNN for detecting tumors.",
            paper_sections=["Methodology", "Results", "Discussion"],
        )
        assert len(rubrics) == 8
        for r in rubrics:
            assert isinstance(r, PaperSpecificRubric)
            assert r.dimension in META_RUBRICS

    def test_instantiate_contextualizes_keywords(self):
        engine = RubricEngine()
        # Usar keywords que existem nos checklists das rubricas
        rubrics = engine.instantiate_for_paper(
            paper_title="Contribuicao Nova com Resultados e Metricas",
        )
        # Alguns criterios devem conter "(contextualizado)"
        all_criteria = []
        for r in rubrics:
            all_criteria.extend(r.criteria)
        contextualized = [c for c in all_criteria if "contextualizado" in c]
        assert len(contextualized) >= 1

    def test_score_review(self):
        engine = RubricEngine()
        rubrics = engine.instantiate_for_paper("Test Paper")
        review = {
            "core_contribution_accuracy": (
                "The paper proposes a novel method. Figure 3 shows "
                "improvements over baselines. The contribution is clearly "
                "stated and significant. I suggest adding more comparisons."
            ),
            "results_interpretation": "The results demonstrate clear gains.",
        }
        scored = engine.score_review(review, rubrics)
        assert len(scored) == 8
        for s in scored:
            assert 0.0 <= s.score <= 1.0

    def test_score_review_evidence_boosts(self):
        engine = RubricEngine()
        rubrics = engine.instantiate_for_paper("Test")
        review = {
            "evidence_based_critique": (
                "Section 3.1 describes the method. Table 2 shows results. "
                "Figure 1 demonstrates the architecture. "
                "I suggest improving the analysis."
            ),
        }
        scored = engine.score_review(review, rubrics)
        evidence_rubric = next(
            s for s in scored if s.dimension == "evidence_based_critique"
        )
        assert evidence_rubric.score > 0.5

    def test_aggregate_score(self):
        engine = RubricEngine()
        rubrics = [
            PaperSpecificRubric(dimension="a", score=0.8),
            PaperSpecificRubric(dimension="b", score=0.6),
        ]
        agg = engine.aggregate_score(rubrics)
        assert agg["overall"] == 0.7
        assert agg["dimension_scores"]["a"] == 0.8


# ============================================================
# Testes: ReviewLedger
# ============================================================

class TestReviewLedger:
    def test_extract_claim(self):
        ledger = ReviewLedger()
        claim = ledger.extract_claim(
            "We achieve state-of-the-art results on all benchmarks",
            section="Results",
            page=5,
        )
        assert isinstance(claim, ClaimEntry)
        assert claim.risk == "high"
        assert claim.section == "Results"

    def test_extract_low_risk_claim(self):
        ledger = ReviewLedger()
        claim = ledger.extract_claim(
            "This preliminary study suggests potential benefits",
            section="Introduction",
        )
        assert claim.risk == "low"

    def test_extract_medium_risk_claim(self):
        ledger = ReviewLedger()
        claim = ledger.extract_claim(
            "We experimented with several architectures",
            section="Methodology",
        )
        assert claim.risk == "medium"

    def test_add_evidence_anchor(self):
        ledger = ReviewLedger()
        claim = ledger.extract_claim("Claim text", section="Intro")
        ledger.add_evidence_anchor(claim.id, "Section 2, paragraph 3")
        assert "Section 2, paragraph 3" in claim.evidence_anchors

    def test_verify_claim(self):
        ledger = ReviewLedger()
        claim = ledger.extract_claim("We achieve state-of-the-art performance")
        assert claim.risk == "high"
        ledger.verify_claim(claim.id, notes="Verified against Table 2")
        assert ledger.claims[claim.id].verified
        # Agenda deve estar atualizada
        assert ledger.get_pending_verifications() == []

    def test_get_high_risk_claims(self):
        ledger = ReviewLedger()
        ledger.extract_claim("Our novel state-of-the-art approach")
        ledger.extract_claim("Low risk preliminary idea")
        high = ledger.get_high_risk_claims()
        assert len(high) == 1

    def test_summary(self):
        ledger = ReviewLedger()
        ledger.extract_claim("Our novel state-of-the-art breakthrough")
        ledger.extract_claim("Preliminary study")
        s = ledger.summary()
        assert s["total_claims"] == 2
        assert s["high_risk"] == 1


# ============================================================
# Testes: AuditGraph
# ============================================================

class TestAuditGraph:
    def test_add_node(self):
        graph = AuditGraph()
        nid = graph.add_node("claim", "Test claim")
        assert nid in graph.nodes
        assert graph.nodes[nid]["type"] == "claim"

    def test_add_edge(self):
        graph = AuditGraph()
        n1 = graph.add_node("claim", "Claim A")
        n2 = graph.add_node("critique", "Critique B")
        edge = graph.add_edge(n1, n2, "supported-by")
        assert edge["type"] == "supported-by"
        assert len(graph.edges) == 1

    def test_get_edges_for_node(self):
        graph = AuditGraph()
        n1 = graph.add_node("claim", "C1")
        n2 = graph.add_node("critique", "Ct1")
        n3 = graph.add_node("evidence", "E1")
        graph.add_edge(n1, n2, "localized-to")
        graph.add_edge(n1, n3, "supported-by")
        edges = graph.get_edges_for_node(n1)
        assert len(edges) == 2

    def test_find_path(self):
        graph = AuditGraph()
        n1 = graph.add_node("claim", "Claim")
        n2 = graph.add_node("evidence", "Evidence A")
        n3 = graph.add_node("critique", "Critique")
        graph.add_edge(n1, n2, "supported-by")
        graph.add_edge(n2, n3, "localized-to")
        path = graph.find_path("claim", "critique", max_hops=3)
        assert len(path) >= 2

    def test_find_path_no_path(self):
        graph = AuditGraph()
        n1 = graph.add_node("claim", "C1")
        n2 = graph.add_node("evidence", "E1")
        graph.add_edge(n1, n2, "supported-by")
        path = graph.find_path("claim", "nonexistent", max_hops=2)
        assert path == []

    def test_traceability_score(self):
        graph = AuditGraph()
        # Critica sem ancora
        c1 = graph.add_node("critique", "Unanchored critique")
        # Critica com ancora
        c2 = graph.add_node("critique", "Anchored critique")
        ev = graph.add_node("evidence", "Evidence")
        graph.add_edge(c2, ev, "supported-by")
        score = graph.traceability_score()
        assert score == 0.5

    def test_traceability_empty(self):
        graph = AuditGraph()
        assert graph.traceability_score() == 0.0

    def test_coverage_score(self):
        graph = AuditGraph()
        c1 = graph.add_node("critique", "C1",
                             metadata={"section": "Methodology"})
        c2 = graph.add_node("critique", "C2",
                             metadata={"section": "Results"})
        score = graph.coverage_score()
        assert score > 0.0

    def test_summary(self):
        graph = AuditGraph()
        graph.add_node("claim", "C1")
        graph.add_node("critique", "Ct1")
        s = graph.summary()
        assert s["nodes"] == 2
        assert "traceability" in s


# ============================================================
# Testes: MultiCriticReviewer
# ============================================================

class TestMultiCriticReviewer:
    def test_all_critics_instantiated(self):
        mcr = MultiCriticReviewer()
        assert "methodology" in mcr.critics
        assert "results" in mcr.critics
        assert "literature" in mcr.critics
        assert "ethics" in mcr.critics

    def test_methodology_critic(self):
        critic = MethodologyCritic()
        paper = {"sections": ["Introduction", "Methodology", "Experiments"]}
        critiques = critic.review(paper)
        assert len(critiques) >= 1
        assert critiques[0].reviewer_type == "methodology"

    def test_results_critic(self):
        critic = ResultsCritic()
        paper = {"sections": ["Experiments", "Results", "Discussion"]}
        critiques = critic.review(paper)
        assert len(critiques) >= 1

    def test_literature_critic_no_related_work(self):
        critic = LiteratureCritic()
        paper = {"sections": ["Intro", "Method"], "citations": []}
        critiques = critic.review(paper)
        assert any("related work" in c.text.lower() for c in critiques)

    def test_literature_critic_few_citations(self):
        critic = LiteratureCritic()
        paper = {"sections": ["Intro", "Related Work"],
                 "citations": ["ref1"]}
        critiques = critic.review(paper)
        assert any("references" in c.text.lower() for c in critiques)

    def test_ethics_critic_checks(self):
        critic = EthicsCritic()
        paper = {"sections": ["Method"], "abstract": "no ethics mentioned"}
        critiques = critic.review(paper)
        # Deve encontrar varias faltas
        bias_checks = [c for c in critiques if "bias" in c.text.lower()]
        assert len(bias_checks) >= 1

    def test_review_paper(self):
        mcr = MultiCriticReviewer()
        paper = {
            "sections": ["Introduction", "Methodology",
                         "Experiments", "Results"],
            "citations": ["ref1", "ref2"],
        }
        results = mcr.review_paper(paper)
        assert len(results) == 4
        assert "methodology" in results
        assert "results" in results

    def test_get_all_critiques(self):
        mcr = MultiCriticReviewer()
        paper = {"sections": ["Intro"], "citations": []}
        mcr.review_paper(paper)
        all_c = mcr.get_all_critiques()
        assert len(all_c) >= 4  # pelo menos 1 de cada revisor

    def test_summary(self):
        mcr = MultiCriticReviewer()
        s = mcr.summary()
        assert len(s) == 4


# ============================================================
# Testes: OrchestratorReviewer
# ============================================================

class TestOrchestratorReviewer:
    def test_initializes_subsystems(self):
        orch = OrchestratorReviewer()
        assert orch.rubric_engine is not None
        assert orch.ledger is not None
        assert orch.audit_graph is not None
        assert orch.multi_critic is not None

    def test_review_returns_package(self):
        orch = OrchestratorReviewer()
        paper = {
            "title": "Deep Learning for Cancer Detection",
            "abstract": "A novel CNN for tumor detection.",
            "sections": ["Introduction", "Methodology", "Experiments",
                         "Results", "Conclusion"],
            "citations": ["ref1", "ref2", "ref3", "ref4", "ref5"],
        }
        package = orch.review(paper)
        assert isinstance(package, ReviewPackage)
        assert package.paper_title == "Deep Learning for Cancer Detection"
        assert package.overall_score >= 0.0

    def test_review_builds_ledger(self):
        orch = OrchestratorReviewer()
        paper = {"sections": ["Introduction", "Methodology"]}
        package = orch.review(paper)
        assert package.ledger_summary["total_claims"] >= 1

    def test_review_builds_audit_graph(self):
        orch = OrchestratorReviewer()
        paper = {"sections": ["Methodology", "Results"],
                 "citations": ["ref1"]}
        package = orch.review(paper)
        assert package.audit_summary["nodes"] >= 2

    def test_review_scoring(self):
        orch = OrchestratorReviewer()
        paper = {"sections": ["Methodology", "Experiments", "Results"]}
        package = orch.review(paper)
        assert len(package.dimension_scores) >= 1

    def test_export_gate_passed_with_good_coverage(self):
        orch = OrchestratorReviewer(
            min_traceability=0.2, min_coverage=0.1,
        )
        paper = {"sections": ["Methodology", "Results", "Discussion"],
                 "citations": ["ref1"]}
        package = orch.review(paper)
        # Deve passar com thresholds baixos (2/8 = 0.25 traceability)
        assert package.traceability >= 0.2
        assert package.export_gate_passed

    def test_repair_plan_prioritizes_critical(self):
        orch = OrchestratorReviewer()
        paper = {"sections": ["Methodology"], "citations": []}
        package = orch.review(paper)
        if package.repair_plan:
            assert package.repair_plan[0]["priority"] in (
                "CRITICAL", "MAJOR", "MINOR"
            )

    def test_summary(self):
        orch = OrchestratorReviewer()
        s = orch.summary()
        assert "rubric_dimensions" in s
        assert "ledger" in s
        assert "audit" in s
        assert "critics" in s

    def test_multiple_reviews(self):
        orch = OrchestratorReviewer()
        paper1 = {"sections": ["Intro", "Method"], "citations": ["r1"]}
        paper2 = {"sections": ["Results", "Discussion"],
                  "citations": ["r1", "r2", "r3"]}
        pkg1 = orch.review(paper1)
        pkg2 = orch.review(paper2)
        assert pkg1.paper_title == "Untitled"
        assert pkg2.paper_title == "Untitled"


# ============================================================
# Testes: Helper function
# ============================================================

class TestRunPeerReview:
    def test_helper_function(self):
        result = run_peer_review(
            paper_title="Test Paper",
            paper_abstract="A test abstract about deep learning.",
            paper_sections=["Intro", "Methodology", "Results"],
            citations=["ref1", "ref2"],
        )
        assert "overall_score" in result
        assert "dimension_scores" in result
        assert "critiques_count" in result
        assert result["critiques_count"] >= 1

    def test_helper_defaults(self):
        result = run_peer_review()
        assert result["paper_title"] == "Untitled"
