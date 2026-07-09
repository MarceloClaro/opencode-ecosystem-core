# -*- coding: utf-8 -*-
"""
Testes TDD para R102 — Deep Research Agent
===========================================
SDD First → TDD → Implementation.

Cobre: EvidenceGraph, BFRS Agent, DFRS Agent, Orchestrator, Sandbox.
"""

import pytest

from agentic_science_v2.evidence_graph import (
    EvidenceGraph,
    Entity, Relation, Evidence,
    ENTITY_TYPES, RELATION_TYPES,
)
from agentic_science_v2.deep_research import (
    BFRSAgent, DFRSAgent, OrchestratorAgent,
    ExecutionSandbox, KnowledgeBaseRegistry,
    ResearchPlan, ResearchReport,
    run_deep_research,
)


# ============================================================
# Testes: EvidenceGraph
# ============================================================

class TestEvidenceGraph:
    def test_add_entity(self):
        g = EvidenceGraph()
        e = g.add_entity("BRAF", "gene", "B-Raf proto-oncogene")
        assert e.id in g.entities
        assert e.name == "BRAF"
        assert e.entity_type == "gene"

    def test_add_entity_duplicate_by_name(self):
        g = EvidenceGraph()
        e1 = g.add_entity("BRAF", "gene")
        e2 = g.add_entity("BRAF", "gene")
        assert e1.id == e2.id  # mesma entidade

    def test_add_entity_with_evidence(self):
        g = EvidenceGraph()
        e = g.add_entity("TP53", "gene",
                          evidence_text="Tumor suppressor gene",
                          source="PubMed:12345")
        assert len(e.evidence) == 1
        ev = g.get_evidence(e.evidence[0])
        assert ev is not None
        assert ev.source == "PubMed:12345"

    def test_get_entity_by_id(self):
        g = EvidenceGraph()
        e = g.add_entity("EGFR", "gene")
        retrieved = g.get_entity(e.id)
        assert retrieved is not None
        assert retrieved.name == "EGFR"

    def test_find_entity_by_name(self):
        g = EvidenceGraph()
        g.add_entity("ALK", "gene")
        found = g.find_entity_by_name("ALK")
        assert found is not None
        assert found.name == "ALK"

    def test_find_entity_by_name_case_insensitive(self):
        g = EvidenceGraph()
        g.add_entity("ALK", "gene")
        found = g.find_entity_by_name("alk")
        assert found is not None

    def test_get_entities_by_type(self):
        g = EvidenceGraph()
        g.add_entity("BRAF", "gene")
        g.add_entity("Melanoma", "disease")
        g.add_entity("EGFR", "gene")
        genes = g.get_entities_by_type("gene")
        assert len(genes) == 2

    def test_add_relation(self):
        g = EvidenceGraph()
        e1 = g.add_entity("BRAF", "gene")
        e2 = g.add_entity("Melanoma", "disease")
        rel = g.add_relation(e1.id, e2.id, "CAUSES")
        assert rel is not None
        assert rel.source_id == e1.id
        assert rel.target_id == e2.id
        assert rel.relation_type == "CAUSES"

    def test_add_relation_nonexistent_source(self):
        g = EvidenceGraph()
        e2 = g.add_entity("Melanoma", "disease")
        rel = g.add_relation("nonexistent", e2.id, "CAUSES")
        assert rel is None

    def test_add_relation_duplicate(self):
        g = EvidenceGraph()
        e1 = g.add_entity("BRAF", "gene")
        e2 = g.add_entity("Melanoma", "disease")
        r1 = g.add_relation(e1.id, e2.id, "CAUSES")
        r2 = g.add_relation(e1.id, e2.id, "CAUSES")
        assert r1.id == r2.id  # mesma relacao

    def test_add_relation_bidirectional(self):
        g = EvidenceGraph()
        e1 = g.add_entity("DrugA", "drug")
        e2 = g.add_entity("TargetB", "gene")
        rel = g.add_relation(e1.id, e2.id, "TARGETS", bidirectional=True)
        assert rel.bidirectional
        assert e1.id in g._adjacency
        assert e2.id in g._adjacency

    def test_get_relations(self):
        g = EvidenceGraph()
        e1 = g.add_entity("BRAF", "gene")
        e2 = g.add_entity("Melanoma", "disease")
        e3 = g.add_entity("Vemurafenib", "drug")
        g.add_relation(e1.id, e2.id, "CAUSES")
        g.add_relation(e3.id, e2.id, "TREATS")
        rels = g.get_relations(e1.id)
        assert len(rels) == 1
        rels_all = g.get_relations(e2.id)
        assert len(rels_all) == 2

    def test_find_paths(self):
        g = EvidenceGraph()
        e1 = g.add_entity("BRAF", "gene")
        e2 = g.add_entity("MAPK", "pathway")
        e3 = g.add_entity("Melanoma", "disease")
        g.add_relation(e1.id, e2.id, "IN_PATHWAY")
        g.add_relation(e2.id, e3.id, "CAUSES")
        paths = g.find_paths(e1.id, e3.id, max_depth=3)
        assert len(paths) >= 1

    def test_find_paths_no_path(self):
        g = EvidenceGraph()
        e1 = g.add_entity("A", "gene")
        e2 = g.add_entity("Z", "disease")
        paths = g.find_paths(e1.id, e2.id, max_depth=3)
        assert paths == []

    def test_subgraph_query(self):
        g = EvidenceGraph()
        e1 = g.add_entity("BRAF", "gene")
        e2 = g.add_entity("Melanoma", "disease")
        e3 = g.add_entity("Vemurafenib", "drug")
        g.add_relation(e1.id, e2.id, "CAUSES")
        g.add_relation(e3.id, e2.id, "TREATS")
        sub = g.subgraph_query([e1.id], max_depth=2)
        assert sub["total_entities"] >= 1
        assert "BRAF" in [e["name"] for e in sub["entities"]]

    def test_stats(self):
        g = EvidenceGraph()
        g.add_entity("BRAF", "gene")
        g.add_entity("Melanoma", "disease")
        stats = g.stats()
        assert stats["entities"] == 2
        assert stats["relations"] == 0
        assert "gene" in stats["entity_types"]

    def test_export_visualization(self):
        g = EvidenceGraph()
        e1 = g.add_entity("BRAF", "gene")
        e2 = g.add_entity("Melanoma", "disease")
        g.add_relation(e1.id, e2.id, "CAUSES")
        viz = g.export_visualization()
        assert "nodes" in viz
        assert "edges" in viz
        assert len(viz["nodes"]) == 2
        assert len(viz["edges"]) == 1


# ============================================================
# Testes: BFRSAgent
# ============================================================

class TestBFRSAgent:
    def test_explores_entities(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        bfrs = BFRSAgent(graph, kb, max_breadth=3)
        discoveries = bfrs.explore(["BRAF"], max_sources=2)
        assert discoveries["entities"] >= 1
        assert len(discoveries["sources_used"]) >= 1

    def test_discovers_relations(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        bfrs = BFRSAgent(graph, kb)
        discoveries = bfrs.explore(["Melanoma"], max_sources=2)
        assert discoveries["relations"] >= 1

    def test_respects_max_breadth(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        bfrs = BFRSAgent(graph, kb, max_breadth=1)
        discoveries = bfrs.explore(
            ["BRAF", "EGFR", "ALK"], max_sources=1
        )
        # So 1 entidade semente processada
        assert bfrs.call_count == 1

    def test_reset(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        bfrs = BFRSAgent(graph, kb)
        bfrs.explore(["BRAF"])
        bfrs.reset()
        assert bfrs.call_count == 0


# ============================================================
# Testes: DFRSAgent
# ============================================================

class TestDFRSAgent:
    def test_investigates_deep(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        dfrs = DFRSAgent(graph, kb, max_depth=2)
        findings = dfrs.investigate("BRAF")
        assert findings["depth_reached"] >= 0
        assert findings["entities_found"] >= 0

    def test_collects_evidence(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        dfrs = DFRSAgent(graph, kb, max_depth=2)
        findings = dfrs.investigate("TP53")
        assert "evidence_collected" in findings

    def test_respects_max_depth(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        dfrs = DFRSAgent(graph, kb, max_depth=1)
        findings = dfrs.investigate("BRAF")
        assert findings["depth_reached"] <= 1

    def test_reset(self):
        graph = EvidenceGraph()
        kb = KnowledgeBaseRegistry()
        dfrs = DFRSAgent(graph, kb)
        dfrs.investigate("BRAF")
        dfrs.reset()
        assert dfrs.call_count == 0


# ============================================================
# Testes: ExecutionSandbox
# ============================================================

class TestExecutionSandbox:
    def test_execute_code(self):
        sandbox = ExecutionSandbox()
        result = sandbox.execute("print('hello')")
        assert result["success"] is True
        assert "output" in result

    def test_query_api(self):
        sandbox = ExecutionSandbox()
        result = sandbox.query_api("pubmed", {"query": "BRAF"})
        assert result["status"] == "success"
        assert len(result["results"]) > 0

    def test_query_api_cache(self):
        sandbox = ExecutionSandbox()
        r1 = sandbox.query_api("test", {"q": "cache"})
        r2 = sandbox.query_api("test", {"q": "cache"})
        assert r1["results"] == r2["results"]  # mesmo objeto (cache)

    def test_cross_validate(self):
        sandbox = ExecutionSandbox()
        statements = [
            {"text": "BRAF causes melanoma", "sources": ["PubMed:1"]},
        ]
        validated = sandbox.cross_validate(statements)
        assert len(validated) == 1
        assert "confidence" in validated[0]

    def test_summary(self):
        sandbox = ExecutionSandbox()
        sandbox.execute("test")
        summary = sandbox.summary()
        assert summary["total_executions"] == 1


# ============================================================
# Testes: OrchestratorAgent
# ============================================================

class TestOrchestratorAgent:
    def test_initializes_all_subsystems(self):
        orch = OrchestratorAgent()
        assert orch.graph is not None
        assert orch.bfrs is not None
        assert orch.dfrs is not None
        assert orch.sandbox is not None
        assert orch.kb is not None

    def test_create_plan(self):
        orch = OrchestratorAgent()
        plan = orch._create_plan(
            "What treatments target BRAF melanoma?",
            "hybrid", 3, 5,
        )
        assert isinstance(plan, ResearchPlan)
        assert len(plan.sub_questions) >= 1

    def test_create_plan_mechanism_keyword(self):
        orch = OrchestratorAgent()
        plan = orch._create_plan(
            "What is the mechanism of action?",
            "hybrid", 3, 5,
        )
        strategies = [sq["strategy"] for sq in plan.sub_questions]
        assert "depth_first" in strategies

    def test_research_complete_flow(self):
        orch = OrchestratorAgent(max_rounds=1, max_actions=5)
        report = orch.research(
            "What genes are associated with diabetes?",
            strategy="hybrid",
        )
        assert isinstance(report, ResearchReport)
        assert report.question == "What genes are associated with diabetes?"
        assert len(report.sections) >= 1
        assert report.confidence >= 0.0

    def test_research_builds_evidence_graph(self):
        orch = OrchestratorAgent(max_rounds=1, max_actions=5)
        orch.research("BRAF melanoma treatment")
        stats = orch.graph.stats()
        assert stats["entities"] >= 1

    def test_sufficiency_check(self):
        orch = OrchestratorAgent()
        # Grafo vazio
        sufficient, gaps = orch._check_sufficiency("test")
        assert not sufficient
        assert len(gaps) >= 1

    def test_sufficiency_check_sufficient(self):
        orch = OrchestratorAgent()
        orch.graph.add_entity("A", "gene")
        orch.graph.add_entity("B", "disease")
        orch.graph.add_entity("C", "drug")
        e1 = orch.graph.find_entity_by_name("A")
        e2 = orch.graph.find_entity_by_name("B")
        e3 = orch.graph.find_entity_by_name("C")
        orch.graph.add_relation(e1.id, e2.id, "CAUSES")
        orch.graph.add_relation(e3.id, e2.id, "TREATS")
        orch.graph.add_relation(e1.id, e3.id, "TARGETS")
        sufficient, gaps = orch._check_sufficiency("test")
        assert sufficient

    def test_summary(self):
        orch = OrchestratorAgent()
        orch.research("diabetes", max_depth=2)
        summary = orch.summary()
        assert summary["rounds"] >= 1
        assert summary["bfrs_calls"] >= 0
        assert summary["dfrs_calls"] >= 0

    def test_to_dict(self):
        orch = OrchestratorAgent(max_rounds=1, max_actions=3)
        orch.research("cancer")
        d = orch.to_dict()
        assert "summary" in d
        assert "plans" in d
        assert "reports" in d
        assert "evidence_graph" in d

    def test_research_multiple_rounds(self):
        orch = OrchestratorAgent(max_rounds=2, max_actions=8)
        report = orch.research(
            "What is the mechanism of diabetes treatment?",
            strategy="hybrid", max_depth=2,
        )
        assert report is not None


# ============================================================
# Testes: KnowledgeBaseRegistry
# ============================================================

class TestKnowledgeBaseRegistry:
    def test_list_sources(self):
        kb = KnowledgeBaseRegistry()
        sources = kb.list_sources()
        assert len(sources) >= 3

    def test_query_returns_results(self):
        kb = KnowledgeBaseRegistry()
        results = kb.query("pubmed", "BRAF melanoma")
        assert len(results) >= 1

    def test_query_diabetes(self):
        kb = KnowledgeBaseRegistry()
        results = kb.query("pubmed", "diabetes treatment")
        assert any("Metformin" in r["entity"] for r in results)

    def test_query_alzheimer(self):
        kb = KnowledgeBaseRegistry()
        results = kb.query("pubmed", "alzheimer")
        assert any("APP" in r["entity"] for r in results)

    def test_query_unknown_returns_generic(self):
        kb = KnowledgeBaseRegistry()
        results = kb.query("pubmed", "some_random_unknown_topic")
        assert len(results) >= 1


# ============================================================
# Testes: Helper function
# ============================================================

class TestRunDeepResearch:
    def test_helper_function(self):
        result = run_deep_research(
            "What drugs target BRAF?",
            max_rounds=1, max_depth=2,
        )
        assert "summary" in result
        assert "reports" in result
        assert len(result["reports"]) >= 1


# ============================================================
# Testes: Entity dataclass
# ============================================================

class TestEntity:
    def test_to_dict(self):
        e = Entity(name="BRAF", entity_type="gene",
                    description="Kinase")
        d = e.to_dict()
        assert d["name"] == "BRAF"
        assert d["type"] == "gene"


# ============================================================
# Testes: Relation dataclass
# ============================================================

class TestRelation:
    def test_to_dict(self):
        r = Relation(source_id="a", target_id="b",
                      relation_type="CAUSES")
        d = r.to_dict()
        assert d["source"] == "a"
        assert d["type"] == "CAUSES"
