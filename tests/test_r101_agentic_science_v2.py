# -*- coding: utf-8 -*-
"""
Testes TDD para R101 — Agentic Science V2
==========================================
SDD First → TDD → Implementation.

Cobre: agents, evolutionary_engine, environment, orchestrator.
"""

import json
import os
import sys
import time

import pytest

from agentic_science_v2.agents import (
    MentorAgent,
    PrimeResearcherAgent,
    ReviewerAgent,
    EvolutionManagerAgent,
    ProblemCluster,
    ResearchIdea,
    TaskDecomposition,
)
from agentic_science_v2.evolutionary_engine import EvoEngine, EvolutionRound
from agentic_science_v2.environment import (
    PermissionsEngine,
    ArtifactEngine,
    BudgetEngine,
    HITLEngine,
    Artifact,
    Budget,
)
from agentic_science_v2.orchestrator import (
    AgenticScienceV2,
    CycleReport,
    run_agentic_science_v2,
)


# ============================================================
# Testes: MentorAgent
# ============================================================

class TestMentorAgent:
    def test_constructs_problem_space(self):
        mentor = MentorAgent()
        clusters = mentor.construct_problem_space(num_clusters=3)
        assert len(clusters) == 3
        for c in clusters:
            assert isinstance(c, ProblemCluster)
            assert c.title
            assert c.domains
            assert 0.0 <= c.feasibility <= 1.0
            assert 0.0 <= c.novelty_potential <= 1.0

    def test_constructs_with_knowledge_graph(self):
        kg = {"concepts": ["entanglement", "variational", "quantum"]}
        mentor = MentorAgent(knowledge_graph=kg)
        clusters = mentor.construct_problem_space(num_clusters=2)
        assert len(clusters) == 2
        # Deve conter conceitos do grafo
        all_concepts = set()
        for c in clusters:
            all_concepts.update(c.concepts)
        assert "quantum" in all_concepts or "entanglement" in all_concepts

    def test_selects_best_cluster(self):
        mentor = MentorAgent()
        mentor.construct_problem_space(num_clusters=3)
        selected = mentor.select_cluster()
        assert selected is not None
        assert isinstance(selected, ProblemCluster)

    def test_selects_with_feedback(self):
        mentor = MentorAgent()
        mentor.construct_problem_space(num_clusters=3)
        selected = mentor.select_cluster(
            feedback={"novelty_boost": 0.5}
        )
        assert selected is not None
        assert len(mentor.feedback_history) == 1

    def test_evaluates_fitness(self):
        mentor = MentorAgent()
        ideas = [
            ResearchIdea(scores={"novelty": 0.8, "feasibility": 0.6,
                                 "excitement": 0.7}),
            ResearchIdea(scores={"novelty": 0.5, "feasibility": 0.9,
                                 "excitement": 0.4}),
        ]
        fitness = mentor.evaluate_fitness(ideas)
        assert "avg_novelty" in fitness
        assert "avg_feasibility" in fitness
        assert "overall" in fitness
        assert fitness["avg_novelty"] == 0.65

    def test_evaluates_empty_fitness(self):
        mentor = MentorAgent()
        fitness = mentor.evaluate_fitness([])
        assert fitness["overall"] == 0.0

    def test_resets_state(self):
        mentor = MentorAgent()
        mentor.construct_problem_space(num_clusters=2)
        mentor.reset()
        assert mentor.clusters == []
        assert mentor.feedback_history == []


# ============================================================
# Testes: PrimeResearcherAgent
# ============================================================

class TestPrimeResearcherAgent:
    def test_decomposes_tasks(self):
        cluster = ProblemCluster(
            title="Quantum ML",
            domains=["quantum", "ML"],
            concepts=["entanglement", "variational"],
            description="Quantum ML test",
        )
        researcher = PrimeResearcherAgent()
        td = researcher.decompose_tasks(cluster)
        assert isinstance(td, TaskDecomposition)
        assert td.cluster_id == cluster.id
        assert len(td.tasks) >= 3

    def test_generates_ideas(self):
        cluster = ProblemCluster(
            title="Bio-Inspired AI",
            domains=["biology", "AI"],
            concepts=["neural", "evolution", "swarm"],
        )
        researcher = PrimeResearcherAgent()
        ideas = researcher.generate_ideas(cluster, num_ideas=3)
        assert len(ideas) == 3
        for idea in ideas:
            assert isinstance(idea, ResearchIdea)
            assert idea.hypothesis
            assert idea.cluster_id == cluster.id

    def test_refines_ideas_with_feedback(self):
        researcher = PrimeResearcherAgent()
        ideas = [
            ResearchIdea(hypothesis="Test H1"),
            ResearchIdea(hypothesis="Test H2"),
        ]
        feedback = [
            {"suggestion": "Add experiment details"},
            {"suggestion": "Improve methodology"},
        ]
        refined = researcher.refine_ideas(ideas, feedback)
        assert len(refined) == 2
        assert "Refined" in refined[0].hypothesis

    def test_uses_memory_when_available(self):
        memory = type("MockMemory", (), {
            "get_successful_directions": lambda self, top_k=1: [
                {"idea": "Previous successful direction"}
            ]
        })()
        researcher = PrimeResearcherAgent(ideation_memory=memory)
        cluster = ProblemCluster(
            title="Climate Informatics",
            domains=["climate"],
            concepts=["modeling", "prediction"],
        )
        ideas = researcher.generate_ideas(cluster, num_ideas=1)
        assert len(ideas) == 1


# ============================================================
# Testes: ReviewerAgent
# ============================================================

class TestReviewerAgent:
    def test_review_fills_scores(self):
        reviewer = ReviewerAgent()
        idea = ResearchIdea(
            hypothesis="Quantum computing for drug discovery",
            concepts=["quantum", "drug", "ML"],
        )
        reviewed = reviewer.review(idea)
        assert "novelty" in reviewed.scores
        assert "feasibility" in reviewed.scores
        assert "excitement" in reviewed.scores
        assert "overall" in reviewed.scores
        assert reviewed.rationale

    def test_batch_review(self):
        reviewer = ReviewerAgent()
        ideas = [
            ResearchIdea(hypothesis="Idea 1", concepts=["a"]),
            ResearchIdea(hypothesis="Idea 2", concepts=["b", "c"]),
        ]
        reviewed = reviewer.batch_review(ideas)
        assert len(reviewed) == 2
        assert all("overall" in i.scores for i in reviewed)

    def test_ranking(self):
        reviewer = ReviewerAgent()
        ideas = [
            ResearchIdea(hypothesis="Low", concepts=["a"],
                         scores={"overall": 0.3}),
            ResearchIdea(hypothesis="High", concepts=["b", "c"],
                         scores={"overall": 0.9}),
        ]
        ranked = reviewer.get_ranking(ideas)
        assert ranked[0].hypothesis == "High"

    def test_suggestions_for_low_novelty(self):
        reviewer = ReviewerAgent()
        idea = ResearchIdea(
            hypothesis="Test",
            concepts=["a"],
            scores={"novelty": 0.2, "feasibility": 0.8,
                    "excitement": 0.5, "overall": 0.4},
        )
        suggestions = reviewer.get_suggestions(idea)
        assert "novelty" in suggestions.lower() or "Aumentar" in suggestions

    def test_suggestions_for_balanced_idea(self):
        reviewer = ReviewerAgent()
        idea = ResearchIdea(
            hypothesis="Great idea",
            concepts=["a", "b", "c"],
            scores={"novelty": 0.8, "feasibility": 0.7,
                    "excitement": 0.8, "overall": 0.77},
        )
        suggestions = reviewer.get_suggestions(idea)
        assert suggestions == "Idea bem equilibrada"


# ============================================================
# Testes: EvolutionManagerAgent
# ============================================================

class TestEvolutionManagerAgent:
    def test_distills_ideation(self):
        manager = EvolutionManagerAgent()
        ideas = [
            ResearchIdea(id="i1", hypothesis="Great idea",
                         scores={"novelty": 0.9, "feasibility": 0.8,
                                 "excitement": 0.9, "overall": 0.87}),
            ResearchIdea(id="i2", hypothesis="OK idea",
                         scores={"novelty": 0.4, "feasibility": 0.5,
                                 "excitement": 0.4, "overall": 0.43}),
        ]
        manager.distill_ideation(ideas, top_k=2)
        assert len(manager.ideation_memory["top_ideas"]) == 2
        assert len(manager.ideation_memory["successful_directions"]) == 2
        assert len(manager.ideation_memory["failed_directions"]) >= 0

    def test_distills_experimentation(self):
        manager = EvolutionManagerAgent()
        strategies = [
            {"name": "strategy_a", "success_rate": 0.8},
            {"name": "strategy_b", "success_rate": 0.3},
        ]
        manager.distill_experimentation(strategies)
        assert len(manager.experimentation_memory["effective_strategies"]) == 1

    def test_retrieves_directions(self):
        manager = EvolutionManagerAgent()
        manager.ideation_memory["successful_directions"] = [
            {"idea": "A", "avg_score": 0.8},
            {"idea": "B", "avg_score": 0.7},
        ]
        successful = manager.get_successful_directions(top_k=1)
        assert len(successful) == 1
        assert successful[0]["idea"] == "A"

    def test_summary(self):
        manager = EvolutionManagerAgent()
        summary = manager.summary()
        assert "ideation" in summary
        assert "experimentation" in summary
        assert summary["ideation"]["successful"] == 0

    def test_resets_memory(self):
        manager = EvolutionManagerAgent()
        manager.ideation_memory["successful_directions"].append(
            {"idea": "test"}
        )
        manager.reset()
        assert len(manager.ideation_memory["successful_directions"]) == 0


# ============================================================
# Testes: EvoEngine
# ============================================================

class TestEvoEngine:
    def test_selection(self):
        engine = EvoEngine()
        entities = [
            {"id": "e1", "concepts": ["a", "b"]},
            {"id": "e2", "concepts": ["c", "d"]},
            {"id": "e3", "concepts": ["e", "f"]},
        ]
        fitness = {"e1": 0.9, "e2": 0.5, "e3": 0.7}
        selected = engine.select(entities, fitness)
        assert len(selected) >= 1

    def test_crossover(self):
        engine = EvoEngine()
        parent_a = {"id": "a", "concepts": ["quantum", "ML"]}
        parent_b = {"id": "b", "concepts": ["biology", "neural"]}
        child_a, child_b = engine.crossover(parent_a, parent_b)
        assert child_a["evolution"] == "crossover"
        assert child_b["evolution"] == "crossover"

    def test_mutation(self):
        engine = EvoEngine(mutation_rate=1.0)
        entity = {"id": "e1", "concepts": ["a", "b"]}
        mutated = engine.mutate(entity, novelty_pool=["new_concept"])
        assert mutated["evolution"] == "mutation"

    def test_mutation_without_novelty_pool(self):
        engine = EvoEngine(mutation_rate=1.0)
        entity = {"id": "e1", "concepts": ["a", "b"]}
        mutated = engine.mutate(entity)
        assert len(mutated["concepts"]) >= 1

    def test_inheritance(self):
        engine = EvoEngine()
        entities = [
            {"id": "e1", "concepts": ["a"]},
            {"id": "e2", "concepts": ["b"]},
            {"id": "e3", "concepts": ["c"]},
        ]
        fitness = {"e1": 0.9, "e2": 0.5, "e3": 0.7}
        inherited = engine.inherit(entities, fitness, top_k=0.5)
        assert len(inherited) >= 1
        for e in inherited:
            assert e["evolution"] == "inheritance"

    def test_diversity_empty(self):
        engine = EvoEngine()
        assert engine.compute_diversity([]) == 1.0

    def test_diversity_identical(self):
        engine = EvoEngine()
        entities = [
            {"id": "e1", "concepts": ["a", "b"]},
            {"id": "e2", "concepts": ["a", "b"]},
        ]
        div = engine.compute_diversity(entities)
        assert div < 0.5  # baixa diversidade

    def test_diversity_different(self):
        engine = EvoEngine()
        entities = [
            {"id": "e1", "concepts": ["a", "b"]},
            {"id": "e2", "concepts": ["c", "d"]},
        ]
        div = engine.compute_diversity(entities)
        assert div > 0.5  # alta diversidade

    def test_full_step(self):
        engine = EvoEngine()
        entities = [
            {"id": "e1", "concepts": ["quantum", "ML"]},
            {"id": "e2", "concepts": ["biology", "neural"]},
            {"id": "e3", "concepts": ["climate", "data"]},
        ]
        fitness = {"e1": 0.9, "e2": 0.6, "e3": 0.7}
        new_pop, record = engine.step(entities, fitness)
        assert isinstance(record, EvolutionRound)
        assert record.round_number == 1
        assert len(record.operations) >= 3  # selection, crossover, mutation
        assert len(new_pop) >= 1

    def test_stagnation_detection(self):
        engine = EvoEngine()
        # Simular 3 rodadas sem melhora
        for i in range(3):
            engine.history.append(EvolutionRound(
                round_number=i + 1,
                avg_fitness_after=0.5,
            ))
        assert engine.is_stagnant(window=3, threshold=0.02)

    def test_stagnation_false_when_improving(self):
        engine = EvoEngine()
        for i in range(3):
            engine.history.append(EvolutionRound(
                round_number=i + 1,
                avg_fitness_after=0.5 + i * 0.1,
            ))
        assert not engine.is_stagnant(window=3, threshold=0.02)

    def test_summary(self):
        engine = EvoEngine()
        summary = engine.summary()
        assert "total_rounds" in summary
        assert "current_diversity" in summary
        assert "config" in summary


# ============================================================
# Testes: PermissionsEngine
# ============================================================

class TestPermissionsEngine:
    def test_creates_session(self):
        perm = PermissionsEngine()
        sid = perm.create_session()
        assert sid in perm._active_sessions
        assert os.path.exists(perm.get_workspace(sid))

    def test_closes_session(self):
        perm = PermissionsEngine()
        sid = perm.create_session()
        perm.close_session(sid)
        assert sid not in perm._active_sessions

    def test_gpu_default_deny(self):
        perm = PermissionsEngine()
        sid = perm.create_session()
        # Aquire sucesso
        assert perm.acquire_gpu(sid, "gpu:0")
        # Segunda tentativa falha
        assert not perm.acquire_gpu("other_sess", "gpu:0")

    def test_gpu_release(self):
        perm = PermissionsEngine()
        sid = perm.create_session()
        perm.acquire_gpu(sid, "gpu:0")
        perm.release_gpu("gpu:0")
        assert "gpu:0" not in perm._gpu_locks

    def test_cannot_access_evaluator(self):
        perm = PermissionsEngine()
        sid = perm.create_session()
        assert not perm.can_access_evaluator(sid)

    def test_status(self):
        perm = PermissionsEngine()
        sid = perm.create_session()
        status = perm.status()
        assert status["active_sessions"] == 1


# ============================================================
# Testes: ArtifactEngine
# ============================================================

class TestArtifactEngine:
    def test_stores_artifact(self):
        engine = ArtifactEngine()
        art = Artifact(session_id="s1", name="test", content="data")
        aid = engine.store(art)
        assert aid in engine.artifacts

    def test_retrieves_artifact(self):
        engine = ArtifactEngine()
        art = Artifact(session_id="s1", name="test", content="data")
        aid = engine.store(art)
        retrieved = engine.get(aid)
        assert retrieved is not None
        assert retrieved.name == "test"

    def test_top_k_by_score(self):
        engine = ArtifactEngine()
        for i in range(5):
            art = Artifact(
                session_id="s1",
                name=f"art_{i}",
                score=float(i),
            )
            engine.store(art)
        top = engine.get_top_k(3)
        assert len(top) == 3
        # Maior score primeiro
        assert top[0].score == 4.0

    def test_session_artifacts(self):
        engine = ArtifactEngine()
        engine.store(Artifact(session_id="s1", name="a1"))
        engine.store(Artifact(session_id="s2", name="a2"))
        engine.store(Artifact(session_id="s1", name="a3"))
        s1_arts = engine.get_session_artifacts("s1")
        assert len(s1_arts) == 2

    def test_summary(self):
        engine = ArtifactEngine()
        engine.store(Artifact(session_id="s1", name="t1", score=0.9))
        summary = engine.summary()
        assert summary["total_artifacts"] >= 1


# ============================================================
# Testes: BudgetEngine
# ============================================================

class TestBudgetEngine:
    def test_creates_budget(self):
        engine = BudgetEngine()
        budget = engine.create_budget("s1", max_time=60, max_cost=5.0)
        assert isinstance(budget, Budget)
        assert budget.max_wall_clock_seconds == 60

    def test_spend_tracks_cost(self):
        engine = BudgetEngine()
        engine.create_budget("s1", max_time=60, max_cost=5.0)
        assert engine.spend("s1", 1.0)
        budget = engine.get_budget("s1")
        assert budget.api_cost_spent == 1.0

    def test_exhausted_on_cost(self):
        engine = BudgetEngine()
        engine.create_budget("s1", max_time=60, max_cost=1.0)
        engine.spend("s1", 1.5)
        assert engine.is_exhausted("s1")

    def test_not_exhausted_initially(self):
        engine = BudgetEngine()
        engine.create_budget("s1", max_time=60, max_cost=10.0)
        assert not engine.is_exhausted("s1")

    def test_budget_remaining(self):
        engine = BudgetEngine()
        engine.create_budget("s1", max_time=60, max_cost=10.0)
        budget = engine.get_budget("s1")
        assert budget.remaining_budget() == 10.0

    def test_summary(self):
        engine = BudgetEngine()
        engine.create_budget("s1", max_time=60, max_cost=10.0)
        summary = engine.summary()
        assert summary["total_budgets"] == 1
        assert summary["exhausted_budgets"] == 0


# ============================================================
# Testes: HITLEngine
# ============================================================

class TestHITLEngine:
    def test_logs_event(self):
        hitl = HITLEngine()
        hitl.log_event("test", "Mensagem de teste")
        assert len(hitl.events) == 1
        assert hitl.events[0]["type"] == "test"

    def test_request_approval(self):
        hitl = HITLEngine()
        approved = hitl.request_approval("run_experiment", {"cost": 5})
        assert approved
        # Deve ter gerado 2 eventos (request + grant)
        assert len(hitl.events) == 2

    def test_pause_resume(self):
        hitl = HITLEngine()
        hitl.pause()
        assert hitl.paused
        hitl.resume()
        assert not hitl.paused

    def test_intervene(self):
        hitl = HITLEngine()
        hitl.intervene("Use different model")
        assert len(hitl.interventions) == 1
        assert hitl.interventions[0]["instruction"] == "Use different model"

    def test_recent_events(self):
        hitl = HITLEngine()
        for i in range(5):
            hitl.log_event(f"event_{i}", str(i))
        recent = hitl.recent_events(3)
        assert len(recent) == 3

    def test_summary(self):
        hitl = HITLEngine()
        hitl.log_event("start", "Began")
        summary = hitl.summary()
        assert summary["total_events"] == 1
        assert summary["paused"] is False


# ============================================================
# Testes: Orchestrator (AgenticScienceV2)
# ============================================================

class TestAgenticScienceV2:
    def test_initializes_all_subsystems(self):
        asc = AgenticScienceV2()
        assert asc.mentor is not None
        assert asc.researcher is not None
        assert asc.reviewer is not None
        assert asc.evo_manager is not None
        assert asc.evo_engine is not None
        assert asc.permissions is not None
        assert asc.artifacts is not None
        assert asc.budgets is not None
        assert asc.hitl is not None

    def test_run_cycle(self):
        asc = AgenticScienceV2(max_rounds=3, ideas_per_round=2)
        report = asc.run_cycle()
        assert isinstance(report, CycleReport)
        assert report.round_number == 1
        assert len(report.ideas) == 2
        assert "overall" in report.fitness
        assert report.cluster is not None

    def test_run_cycle_with_seed(self):
        asc = AgenticScienceV2(max_rounds=2)
        report = asc.run_cycle(
            seed_domains=["Quantum Machine Learning"],
            num_clusters=1,
        )
        assert report.cluster is not None
        assert "quantum" in report.cluster.title.lower() or \
               "Quantum" in report.cluster.title

    def test_run_full_multiple_rounds(self):
        asc = AgenticScienceV2(max_rounds=3, ideas_per_round=2)
        reports = asc.run_full()
        assert len(reports) >= 1
        assert len(reports) <= 3

    def test_summary(self):
        asc = AgenticScienceV2(max_rounds=2)
        asc.run_cycle()
        summary = asc.summary()
        assert summary["rounds_completed"] >= 1
        assert "evolution" in summary
        assert "memory" in summary
        assert "environment" in summary

    def test_stop(self):
        asc = AgenticScienceV2(max_rounds=5)
        asc.run_cycle()
        asc.stop()
        assert not asc.running

    def test_to_dict(self):
        asc = AgenticScienceV2(max_rounds=2)
        asc.run_cycle()
        d = asc.to_dict()
        assert "config" in d
        assert "summary" in d
        assert "history" in d
        assert len(d["history"]) == 1

    def test_stagnation_stops_early(self):
        asc = AgenticScienceV2(max_rounds=10, ideas_per_round=1)
        # Forcar estagnacao rapida
        asc.run_cycle()
        # Simular estagnacao congelando fitness
        for r in asc.history:
            r.evolution.avg_fitness_after = 0.5
        asc.evo_engine.history = [
            EvolutionRound(round_number=i + 1, avg_fitness_after=0.5)
            for i in range(3)
        ]
        # Proximo run_full deve parar cedo
        reports = asc.run_full()
        assert len(reports) < 10  # must stop early

    def test_helper_function(self):
        result = run_agentic_science_v2(max_rounds=2)
        assert "config" in result
        assert "summary" in result


# ============================================================
# Testes: ProblemCluster
# ============================================================

class TestProblemCluster:
    def test_to_dict(self):
        pc = ProblemCluster(
            title="Test Domain",
            domains=["test"],
            concepts=["a", "b"],
            feasibility=0.7,
            novelty_potential=0.8,
        )
        d = pc.to_dict()
        assert d["title"] == "Test Domain"
        assert d["feasibility"] == 0.7
        assert d["novelty_potential"] == 0.8


# ============================================================
# Testes: ResearchIdea
# ============================================================

class TestResearchIdea:
    def test_to_dict(self):
        idea = ResearchIdea(
            title="Test Idea",
            hypothesis="Test hypothesis",
            scores={"novelty": 0.8, "overall": 0.75},
        )
        d = idea.to_dict()
        assert d["title"] == "Test Idea"
        assert d["scores"]["novelty"] == 0.8
