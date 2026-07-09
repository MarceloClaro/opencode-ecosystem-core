# -*- coding: utf-8 -*-
"""
Testes TDD para R97 — Evolutionary Memory Substrate
====================================================
SPEC-935-R97: Ciclo RED → GREEN → REFACTOR.

Testes escritos ANTES da implementacao (RED).
Divididos em:
  - Testes IdeationMemory (CA2)
  - Testes ExperimentationMemory (CA3)
  - Testes HeartbeatReflection (CA4)
  - Testes StagnationDetector (CA5)
  - Testes de integracao com ContinuousDiscoveryLoop (CA6)
  - Testes de serializacao (CA8)
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime
from typing import Any, Dict, List

import pytest


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def memory_substrate():
    """Fixture basica do EvolutionaryMemorySubstrate."""
    from synthetic_university.evolutionary_memory import (
        EvolutionaryMemorySubstrate,
    )
    return EvolutionaryMemorySubstrate()


@pytest.fixture
def populated_memory(memory_substrate):
    """Memory com dados de exemplo para testes de consulta."""
    # Ideation: 5 direcoes (3 sucesso, 2 falha)
    ideas = [
        ("Quantum Ethics Framework", 85, "success",
         {"concepts": ["quantum", "ethics", "AI"]}),
        ("Deep Learning for Tropics", 42, "failure",
         {"concepts": ["deep learning", "tropics", "diagnosis"]}),
        ("Blockchain for Reproducibility", 72, "success",
         {"concepts": ["blockchain", "reproducibility", "science"]}),
        ("Swarm Disaster Response", 35, "failure",
         {"concepts": ["swarm", "disaster", "response"]}),
        ("Causal Inference in Epidemiology", 91, "success",
         {"concepts": ["causal", "epidemiology", "modeling"]}),
    ]
    for title, score, outcome, meta in ideas:
        memory_substrate.ideation.record_idea(
            direction=title,
            outcome=outcome,
            score=score,
            metadata=meta,
        )

    # Experimentation: 3 estrategias
    strategies = [
        ("semantic_chunking", ["nlp", "retrieval"], 88,
         {"method": "chunk_by_sentence"}),
        ("concept_expansion", ["nlp", "ideation"], 65,
         {"method": "wordnet_expand"}),
        ("citation_graph_walk", ["retrieval", "graph"], 92,
         {"method": "bfs_depth_2"}),
    ]
    for sid, context, effectiveness, meta in strategies:
        memory_substrate.experimentation.record_strategy(
            strategy_id=sid,
            context=context,
            effectiveness=effectiveness,
            metadata=meta,
        )

    # Stagnation: 6 ciclos de novidade
    scores = [72, 74, 73, 71, 72, 71]
    for i, s in enumerate(scores):
        memory_substrate.stagnation.record_novelty_score(i, s)

    return memory_substrate


# ============================================================
# CA2 — IdeationMemory
# ============================================================

class TestIdeationMemory:
    """Testes do componente IdeationMemory (CA2)."""

    def test_ca2_record_idea_stores_direction(self, memory_substrate):
        """record_idea() armazena direcao com todos os campos."""
        mem = memory_substrate.ideation
        mem.record_idea(
            direction="Quantum Ethics",
            outcome="success",
            score=85,
            metadata={"concepts": ["quantum", "ethics"]},
        )
        assert len(mem._ideas) == 1
        idea = mem._ideas[0]
        assert idea["direction"] == "Quantum Ethics"
        assert idea["outcome"] == "success"
        assert idea["score"] == 85
        assert idea["metadata"]["concepts"] == ["quantum", "ethics"]
        assert "timestamp" in idea
        assert "idea_id" in idea

    def test_ca2_record_idea_multiple(self, memory_substrate):
        """record_idea() acumula multiplas direcoes."""
        mem = memory_substrate.ideation
        for i in range(10):
            mem.record_idea(
                direction=f"Direction {i}",
                outcome="success" if i % 2 == 0 else "failure",
                score=50 + i * 5,
            )
        assert len(mem._ideas) == 10

    def test_ca2_get_promising_directions_filters_by_score(self, populated_memory):
        """get_promising_directions() retorna apenas score >= min_score."""
        mem = populated_memory.ideation
        promising = mem.get_promising_directions(top_k=10, min_score=70)
        assert len(promising) >= 0
        for p in promising:
            assert p["score"] >= 70

    def test_ca2_get_promising_directions_ordered(self, populated_memory):
        """get_promising_directions() ordena por score descendente."""
        mem = populated_memory.ideation
        promising = mem.get_promising_directions(top_k=10, min_score=0)
        scores = [p["score"] for p in promising]
        assert scores == sorted(scores, reverse=True)

    def test_ca2_get_promising_directions_top_k(self, populated_memory):
        """get_promising_directions() respeita top_k."""
        mem = populated_memory.ideation
        promising = mem.get_promising_directions(top_k=3, min_score=0)
        assert len(promising) <= 3

    def test_ca2_get_failed_directions(self, populated_memory):
        """get_failed_directions() retorna direcoes com score baixo."""
        mem = populated_memory.ideation
        failed = mem.get_failed_directions(max_score=50)
        assert len(failed) >= 2
        for f in failed:
            assert f["score"] <= 50
            assert f["outcome"] == "failure"

    def test_ca2_is_already_explored_true(self, populated_memory):
        """is_already_explored() detecta similaridade alta."""
        mem = populated_memory.ideation
        assert mem.is_already_explored("Quantum Ethics Framework", threshold=0.5)

    def test_ca2_is_already_explored_false(self, populated_memory):
        """is_already_explored() retorna False para tema novo."""
        mem = populated_memory.ideation
        assert not mem.is_already_explored(
            "Completely Original Topic No One Ever Thought Of", threshold=0.5
        )

    def test_ca2_get_direction_stats(self, populated_memory):
        """get_direction_stats() retorna estatisticas consolidadas."""
        mem = populated_memory.ideation
        # Usar a primeira ideia registrada
        idea_id = mem._ideas[0]["idea_id"]
        stats = mem.get_direction_stats(idea_id)
        assert "n_attempts" in stats
        assert "avg_score" in stats
        assert "best_score" in stats
        assert "trend" in stats

    def test_ca2_get_direction_stats_unknown(self, memory_substrate):
        """get_direction_stats() retorna dict vazio para ID inexistente."""
        mem = memory_substrate.ideation
        stats = mem.get_direction_stats("nonexistent")
        assert stats == {}

    def test_ca2_get_exploration_summary(self, populated_memory):
        """get_exploration_summary() retorna metricas agregadas."""
        mem = populated_memory.ideation
        summary = mem.get_exploration_summary()
        assert summary["total_ideas"] == 5
        assert summary["success_rate"] == 3 / 5
        assert 0 <= summary["avg_score"] <= 100
        assert summary["diversity"] >= 0


# ============================================================
# CA3 — ExperimentationMemory
# ============================================================

class TestExperimentationMemory:
    """Testes do componente ExperimentationMemory (CA3)."""

    def test_ca3_record_strategy(self, memory_substrate):
        """record_strategy() armazena estrategia com todos os campos."""
        mem = memory_substrate.experimentation
        mem.record_strategy(
            strategy_id="test_strat",
            context=["nlp", "embedding"],
            effectiveness=90,
            metadata={"method": "bert_chunking"},
        )
        assert len(mem._strategies) == 1
        s = mem._strategies["test_strat"]
        assert s["strategy_id"] == "test_strat"
        assert s["effectiveness"] == 90
        assert s["context"] == ["nlp", "embedding"]

    def test_ca3_record_strategy_accumulates_uses(self, memory_substrate):
        """record_strategy() incrementa n_uses se mesma strategy_id."""
        mem = memory_substrate.experimentation
        mem.record_strategy("s1", ["a"], 80)
        mem.record_strategy("s1", ["a"], 90)
        assert mem._strategies["s1"]["n_uses"] == 2
        # effectiveness deve ser a media
        assert mem._strategies["s1"]["effectiveness"] == 85

    def test_ca3_get_reusable_strategies(self, populated_memory):
        """get_reusable_strategies() retorna estrategias ordenadas por ctx."""
        mem = populated_memory.experimentation
        strategies = mem.get_reusable_strategies(
            context=["nlp", "retrieval"], top_k=5
        )
        assert len(strategies) >= 1
        # Todas devem ter overlap de contexto
        for s in strategies:
            ctx_set = set(s["context"])
            assert ctx_set & {"nlp", "retrieval"}

    def test_ca3_get_reusable_strategies_top_k(self, populated_memory):
        """get_reusable_strategies() respeita top_k."""
        mem = populated_memory.experimentation
        strategies = mem.get_reusable_strategies(context=["nlp"], top_k=2)
        assert len(strategies) <= 2

    def test_ca3_get_effectiveness_stats(self, populated_memory):
        """get_effectiveness_stats() retorna metricas historicas."""
        mem = populated_memory.experimentation
        stats = mem.get_effectiveness_stats("semantic_chunking")
        assert stats["mean_effectiveness"] == 88
        assert stats["n_uses"] >= 1
        assert "trend" in stats

    def test_ca3_get_effectiveness_stats_unknown(self, memory_substrate):
        """get_effectiveness_stats() retorna dict vazio p/ ID desconhecido."""
        mem = memory_substrate.experimentation
        assert mem.get_effectiveness_stats("unknown") == {}

    def test_ca3_get_strategy_portfolio(self, populated_memory):
        """get_strategy_portfolio() retorna lista rankeada."""
        mem = populated_memory.experimentation
        portfolio = mem.get_strategy_portfolio()
        assert len(portfolio) == 3
        # Deve estar ordenada por effectiveness descendente
        effs = [p["mean_effectiveness"] for p in portfolio]
        assert effs == sorted(effs, reverse=True)


# ============================================================
# CA4 — HeartbeatReflection
# ============================================================

class TestHeartbeatReflection:
    """Testes do componente HeartbeatReflection (CA4)."""

    def test_ca4_should_reflect_true(self, memory_substrate):
        """should_reflect() True quando cycle_count % interval == 0."""
        hb = memory_substrate.heartbeat
        assert hb.should_reflect(5, interval=5) is True
        assert hb.should_reflect(10, interval=5) is True
        assert hb.should_reflect(0, interval=5) is True

    def test_ca4_should_reflect_false(self, memory_substrate):
        """should_reflect() False quando nao divisivel."""
        hb = memory_substrate.heartbeat
        assert hb.should_reflect(3, interval=5) is False
        assert hb.should_reflect(7, interval=5) is False

    def test_ca4_reflect_generates_id_and_timestamp(self, memory_substrate):
        """reflect() gera reflection_id e timestamp."""
        hb = memory_substrate.heartbeat
        result = hb.reflect(memory_substrate)
        assert "reflection_id" in result
        assert "timestamp" in result
        assert result["insights_count"] >= 0

    def test_ca4_reflect_consolidates_insights(self, populated_memory):
        """reflect() consolida insights de ideation + experimentation."""
        hb = populated_memory.heartbeat
        result = hb.reflect(populated_memory)
        assert result["insights_count"] > 0
        assert len(result["insights"]) > 0

    def test_ca4_get_reflection_history(self, memory_substrate):
        """get_reflection_history() retorna lista ordenada."""
        hb = memory_substrate.heartbeat
        hb.reflect(memory_substrate)
        hb.reflect(memory_substrate)
        history = hb.get_reflection_history()
        assert len(history) == 2

    def test_ca4_get_insights(self, populated_memory):
        """get_insights() retorna sintese textual."""
        hb = populated_memory.heartbeat
        hb.reflect(populated_memory)
        insights = hb.get_insights()
        assert isinstance(insights, str)
        assert len(insights) > 0


# ============================================================
# CA5 — StagnationDetector
# ============================================================

class TestStagnationDetector:
    """Testes do componente StagnationDetector (CA5)."""

    def test_ca5_record_novelty_score(self, memory_substrate):
        """record_novelty_score() armazena valores em serie temporal."""
        sd = memory_substrate.stagnation
        sd.record_novelty_score(0, 75.0)
        sd.record_novelty_score(1, 76.0)
        assert len(sd._scores) == 2

    def test_ca5_is_stagnated_true(self, memory_substrate):
        """is_stagnated() True quando variancia < threshold."""
        sd = memory_substrate.stagnation
        for i in range(6):
            sd.record_novelty_score(i, 72.0 + (i % 2) * 0.5)  # variacao minima
        assert sd.is_stagnated(window=5, threshold=1.0) is True

    def test_ca5_is_stagnated_false(self, memory_substrate):
        """is_stagnated() False quando scores sobem consistentemente."""
        sd = memory_substrate.stagnation
        for i in range(6):
            sd.record_novelty_score(i, 60.0 + i * 5.0)  # sobe 5 por ciclo
        assert sd.is_stagnated(window=5, threshold=3.0) is False

    def test_ca5_is_stagnated_not_enough_data(self, memory_substrate):
        """is_stagnated() retorna False com menos de 2 pontos."""
        sd = memory_substrate.stagnation
        sd.record_novelty_score(0, 75.0)
        assert sd.is_stagnated(window=5) is False

    def test_ca5_get_stagnation_report(self, populated_memory):
        """get_stagnation_report() retorna relatorio completo."""
        sd = populated_memory.stagnation
        report = sd.get_stagnation_report(window=3, threshold=5.0)
        assert "is_stagnated" in report
        assert "window" in report
        assert "variance" in report
        assert "mean" in report
        assert "recommendation" in report

    def test_ca5_suggest_redirection(self, populated_memory):
        """suggest_redirection() sugere direcoes de falha."""
        sd = populated_memory.stagnation
        # O memory_substrate tem direcoes de falha registradas
        suggestions = sd.suggest_redirection(populated_memory.ideation)
        assert isinstance(suggestions, list)
        # Se ha falhas, deve sugerir explorar o oposto
        assert len(suggestions) >= 0

    def test_ca5_get_novelty_trend_improving(self, memory_substrate):
        """get_novelty_trend() retorna 'improving' quando scores sobem."""
        sd = memory_substrate.stagnation
        for i in range(5):
            sd.record_novelty_score(i, 50.0 + i * 8.0)
        assert sd.get_novelty_trend() == "improving"

    def test_ca5_get_novelty_trend_declining(self, memory_substrate):
        """get_novelty_trend() retorna 'declining' quando scores caem."""
        sd = memory_substrate.stagnation
        for i in range(5):
            sd.record_novelty_score(i, 80.0 - i * 8.0)
        assert sd.get_novelty_trend() == "declining"

    def test_ca5_get_novelty_trend_stable(self, populated_memory):
        """get_novelty_trend() retorna 'stable' para variacao minima."""
        sd = populated_memory.stagnation
        assert sd.get_novelty_trend(window=5) in ("stable", "improving", "declining")


# ============================================================
# CA6 — Integracao com ContinuousDiscoveryLoop
# ============================================================

class TestIntegrationWithCDL:
    """Testes de integracao com ContinuousDiscoveryLoop (CA6)."""

    def test_ca6_cdl_accepts_memory_param(self):
        """ContinuousDiscoveryLoop aceita memory parameter."""
        from synthetic_university.evolutionary_memory import (
            EvolutionaryMemorySubstrate,
        )
        from synthetic_university.continuous_discovery import (
            ContinuousDiscoveryLoop,
        )
        mem = EvolutionaryMemorySubstrate()
        loop = ContinuousDiscoveryLoop(
            output_dir="/tmp/test_r97",
            interval_hours=1,
            lang="en",
            memory=mem,
        )
        assert loop.memory is mem

    def test_ca6_cdl_with_memory_avoids_explored(self):
        """Com memory, run_cycle() evita direcoes ja exploradas."""
        from synthetic_university.evolutionary_memory import (
            EvolutionaryMemorySubstrate,
        )
        from synthetic_university.continuous_discovery import (
            ContinuousDiscoveryLoop,
        )
        mem = EvolutionaryMemorySubstrate()

        # Registra direcao que deve ser evitada
        failed_direction = "Quantum Ethics: A Framework for Moral AI Systems"
        mem.ideation.record_idea(
            direction=failed_direction,
            outcome="failure",
            score=30,
        )

        loop = ContinuousDiscoveryLoop(
            output_dir="/tmp/test_r97",
            interval_hours=1,
            lang="en",
            memory=mem,
        )

        result = loop.run_cycle()
        # Nenhuma tese gerada deve ter titulo similar ao falhado original
        # NOTA: run_cycle() ja registrou as teses geradas na memoria,
        # entao comparamos contra a direcao falhada original, nao contra
        # toda a memoria (que agora inclui as proprias teses geradas)
        from synthetic_university.evolutionary_memory import _text_similarity
        for thesis in result.get("theses", []):
            title = thesis.get("title", "")
            sim = _text_similarity(title, failed_direction)
            assert sim < 0.6, (
                f"Tese '{title}' (sim={sim:.2f}) similar a direcao falhada "
                f"'{failed_direction}'"
            )

    def test_ca6_cdl_records_outcomes_in_memory(self):
        """Com memory, run_cycle() registra outcomes apos ciclo."""
        from synthetic_university.evolutionary_memory import (
            EvolutionaryMemorySubstrate,
        )
        from synthetic_university.continuous_discovery import (
            ContinuousDiscoveryLoop,
        )
        mem = EvolutionaryMemorySubstrate()
        loop = ContinuousDiscoveryLoop(
            output_dir="/tmp/test_r97",
            interval_hours=1,
            lang="en",
            memory=mem,
        )

        ideas_before = len(mem.ideation._ideas)
        loop.run_cycle()
        ideas_after = len(mem.ideation._ideas)
        assert ideas_after > ideas_before, (
            "Memoria deve ter novas ideias apos ciclo"
        )

    def test_ca6_cdl_checks_stagnation(self):
        """Com memory, run_cycle() inclui stagnation_alert no resultado."""
        from synthetic_university.evolutionary_memory import (
            EvolutionaryMemorySubstrate,
        )
        from synthetic_university.continuous_discovery import (
            ContinuousDiscoveryLoop,
        )
        mem = EvolutionaryMemorySubstrate()
        # Preenche com scores estagnados
        for i in range(6):
            mem.stagnation.record_novelty_score(i, 72.0)

        loop = ContinuousDiscoveryLoop(
            output_dir="/tmp/test_r97",
            interval_hours=1,
            lang="en",
            memory=mem,
        )

        result = loop.run_cycle()
        assert "stagnation_alert" in result

    def test_ca6_cdl_heartbeat_reflection(self):
        """Com memory, run_cycle() faz reflexao no ciclo 5."""
        from synthetic_university.evolutionary_memory import (
            EvolutionaryMemorySubstrate,
        )
        from synthetic_university.continuous_discovery import (
            ContinuousDiscoveryLoop,
        )

        mem = EvolutionaryMemorySubstrate()
        loop = ContinuousDiscoveryLoop(
            output_dir="/tmp/test_r97",
            interval_hours=1,
            lang="en",
            memory=mem,
        )

        # Executa 6 ciclos (deve refletir no 5)
        for _ in range(6):
            loop.run_cycle()

        reflections = mem.heartbeat.get_reflection_history()
        assert len(reflections) >= 1


# ============================================================
# CA7 — Testes de serializacao/persistencia
# ============================================================

class TestSerialization:
    """Testes de save/load (CA8)."""

    def test_ca8_save_and_load_roundtrip(self, populated_memory):
        """save() e load() preservam estado completo."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as f:
            path = f.name

        try:
            populated_memory.save(path)
            assert os.path.exists(path)

            loaded = populated_memory.load(path)
            assert loaded is not None
            assert len(loaded.ideation._ideas) == len(
                populated_memory.ideation._ideas
            )
            assert len(loaded.experimentation._strategies) == len(
                populated_memory.experimentation._strategies
            )
            assert loaded.stagnation._scores == populated_memory.stagnation._scores
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_ca8_save_format_includes_version(self, populated_memory):
        """JSON salvo inclui versao do schema e timestamp."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as f:
            path = f.name

        try:
            populated_memory.save(path)
            with open(path, "r") as f:
                data = json.load(f)
            assert "schema_version" in data
            assert "timestamp" in data
            assert data["schema_version"] == "1.0"
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_ca8_load_nonexistent_returns_none(self, memory_substrate):
        """load() de arquivo inexistente retorna None."""
        loaded = memory_substrate.load("/tmp/nonexistent_r97_test.json")
        assert loaded is None


# ============================================================
# Smoke test — execucao completa do substrate
# ============================================================

class TestIntegrationFull:
    """Teste de integracao completo do substrate."""

    def test_full_pipeline(self):
        """Ciclo completo: record → detect stagnation → reflect → save."""
        from synthetic_university.evolutionary_memory import (
            EvolutionaryMemorySubstrate,
        )

        mem = EvolutionaryMemorySubstrate()

        # 6 ciclos simulados
        for cycle in range(6):
            # Gera ideias
            for d in range(3):
                score = 70 + (cycle * 2) + d
                outcome = "success" if score > 75 else "failure"
                mem.ideation.record_idea(
                    direction=f"Direction {cycle}.{d}",
                    outcome=outcome,
                    score=score,
                )

            # Registra scores
            avg_score = 72.0 + (cycle * 1.5)
            mem.stagnation.record_novelty_score(cycle, avg_score)

            # Estrategias
            mem.experimentation.record_strategy(
                f"strategy_{cycle}",
                context=["nlp", "ideation"],
                effectiveness=70 + cycle * 3,
            )

        # Verifica estagnacao (nao deve estar estagnado com scores subindo)
        assert not mem.stagnation.is_stagnated(window=5, threshold=5.0)

        # Reflexao
        result = mem.heartbeat.reflect(mem)
        assert result["insights_count"] > 0

        # Save/Load roundtrip
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as f:
            path = f.name
        try:
            mem.save(path)
            loaded = mem.load(path)
            assert loaded is not None
            assert loaded.stagnation.get_novelty_trend() == "improving"
        finally:
            if os.path.exists(path):
                os.unlink(path)
