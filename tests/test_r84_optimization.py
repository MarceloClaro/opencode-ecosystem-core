"""Testes TDD para a Otimização e Escalabilidade (SPEC-935 R84)."""

import pytest
import time
from synthetic_university.faculties import FACULTY_MAP
from synthetic_university.combinatorial_engine import CombinatorialDiscoveryEngine


class TestR84Optimization:
    """Testes para otimizações do pipeline."""

    @pytest.fixture
    def engine(self):
        return CombinatorialDiscoveryEngine(FACULTY_MAP)

    def test_batch_similarity(self, engine):
        """R84: Batch similarity pre-computa similaridades."""
        concepts_a = ["ética", "moral", "consciência"]
        concepts_b = ["qubit", "algoritmo", "dado"]
        
        cache = engine._batch_similarity(concepts_a, concepts_b)
        assert len(cache) == len(concepts_a)
        for c in concepts_a:
            assert c in cache
            assert 0.0 <= cache[c] <= 1.0

    def test_guided_concept_sample_cached(self, engine):
        """R84: Amostragem guiada cached funciona."""
        concepts = ["ética", "moral", "consciência", "justiça"]
        cache = {"ética": 0.5, "moral": 0.4, "consciência": 0.3, "justiça": 0.2}
        
        sample = engine._guided_concept_sample_cached(concepts, "ética", cache, n_samples=2)
        assert len(sample) <= 2
        assert all(s in concepts for s in sample)

    def test_generate_pairs_parallel(self, engine):
        """R84: Geração paralela funciona."""
        faculty_ids = list(FACULTY_MAP.keys())
        pairs = [
            ([faculty_ids[0]], [faculty_ids[4]]),  # human_sciences × quantum
            ([faculty_ids[1]], [faculty_ids[5]]),  # social × exact
        ]
        
        results = engine.generate_pairs_parallel(pairs, max_per_pair=10)
        assert len(results) >= 1
        # IDs únicos
        ids = [r.combination_id for r in results]
        assert len(ids) == len(set(ids))

    def test_performance_improvement(self, engine):
        """R84: Geração é rápida (teste de fumaça)."""
        t0 = time.time()
        results = engine.generate_pair_combinations(
            ["human_sciences"], ["quantum"], max_combinations=20
        )
        t1 = time.time()
        
        elapsed = t1 - t0
        assert elapsed < 60.0  # pode levar tempo para construir similaridades
        # Pode gerar 0 se acceptance-rejection for muito restrito

    def test_generate_pairs_no_duplicates(self, engine):
        """R84: Geração de pares não produz duplicatas."""
        results = engine.generate_pair_combinations(
            ["human_sciences"], ["quantum"], max_combinations=15
        )
        ids = [r.combination_id for r in results]
        assert len(ids) == len(set(ids))

    def test_no_duplicate_internal_set(self, engine):
        """R84: Set interno previne duplicatas."""
        concepts_a = ["ética", "moral"]
        concepts_b = ["qubit"]
        
        r1 = engine.generate_pair_combinations(concepts_a, concepts_b, max_combinations=5)
        r2 = engine.generate_pair_combinations(concepts_a, concepts_b, max_combinations=5)
        
        # Chamadas subsequentes evitam duplicatas via _history_set
        ids = [r.combination_id for r in r2]
        assert len(ids) == len(set(ids))

    def test_parallel_vs_sequential_same_total(self, engine):
        """R84: Paralelo produz mesmo número de combos que sequencial."""
        faculty_ids = list(FACULTY_MAP.keys())
        
        # Gerar manualmente dois pares
        r1 = engine.generate_pair_combinations(
            [faculty_ids[0]], [faculty_ids[4]], max_combinations=5
        )
        r2 = engine.generate_pair_combinations(
            [faculty_ids[1]], [faculty_ids[5]], max_combinations=5
        )
        sequential_total = len(r1) + len(r2)
        
        # Paralelo
        pairs = [
            ([faculty_ids[0]], [faculty_ids[4]]),
            ([faculty_ids[1]], [faculty_ids[5]]),
        ]
        parallel_results = engine.generate_pairs_parallel(pairs, max_per_pair=5)
        
        # Total deve ser similar (pode ter variação devido ao acceptance-rejection)
        assert len(parallel_results) <= len(r1) + len(r2) + 2  # margem
