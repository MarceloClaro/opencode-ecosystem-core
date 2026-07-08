"""Testes TDD para o Benchmark (SPEC-935 R81)."""

import pytest
from synthetic_university.faculties import FACULTY_MAP
from synthetic_university.semantic_embedder import SemanticEmbedder


class TestBenchmark:
    """Testes para o sistema de benchmark."""

    @pytest.fixture
    def embedder(self):
        emb = SemanticEmbedder(dimension=768)
        if not emb.load("/tmp/semantic_embedder.pkl"):
            texts = []
            for fid, fac in FACULTY_MAP.items():
                texts.append(fac.descricao)
                texts.extend(fac.conceitos.values())
            emb.build_corpus(texts)
            emb.save("/tmp/semantic_embedder.pkl")
        return emb

    def test_all_concepts_returns_items(self):
        """R81: all_concepts retorna itens de todas as faculdades."""
        from synthetic_university.benchmark import all_concepts
        items = all_concepts(FACULTY_MAP)
        assert len(items) >= 100
        assert all(len(item) == 3 for item in items)

    def test_neural_coherence_symmetric(self, embedder):
        """R81: Coerência neural é simétrica."""
        from synthetic_university.benchmark import neural_coherence
        c1 = neural_coherence(embedder, "ética", "moral")
        c2 = neural_coherence(embedder, "moral", "ética")
        assert abs(c1 - c2) < 0.001

    def test_neural_coherence_range(self, embedder):
        """R81: Coerência neural está em [0, 1]."""
        from synthetic_university.benchmark import neural_coherence
        c1 = neural_coherence(embedder, "ética", "moral")
        c2 = neural_coherence(embedder, "qubit", "poesia")
        c3 = neural_coherence(embedder, "água", "água")
        for c in [c1, c2, c3]:
            assert 0.0 <= c <= 1.0

    def test_neural_coherence_same_higher(self, embedder):
        """R81: Mesmo conceito tem coerência máxima."""
        from synthetic_university.benchmark import neural_coherence
        c = neural_coherence(embedder, "algoritmo", "algoritmo")
        assert c > 0.90

    def test_baseline_random(self, embedder):
        """R81: Baseline random gera combinações."""
        from synthetic_university.benchmark import baseline_random
        results, dt = baseline_random(FACULTY_MAP, embedder, n_samples=100)
        assert len(results) == 100
        assert all('coherence' in r for r in results)
        assert dt > 0

    def test_baseline_jaccard(self, embedder):
        """R81: Baseline Jaccard gera combinações."""
        from synthetic_university.benchmark import baseline_jaccard
        results, dt = baseline_jaccard(FACULTY_MAP, embedder)
        assert len(results) >= 100
        assert dt > 0

    def test_baseline_refined(self, embedder):
        """R81: Pipeline refinado gera combinações."""
        from synthetic_university.benchmark import refined_pipeline
        results, dt = refined_pipeline(FACULTY_MAP, embedder)
        assert len(results) >= 20
        assert all('composite' in r for r in results)

    def test_analyze_output(self, embedder):
        """R81: Função analyze produz saída."""
        from synthetic_university.benchmark import baseline_random, refined_pipeline, analyze
        rnd, _ = baseline_random(FACULTY_MAP, embedder, n_samples=50)
        ref, _ = refined_pipeline(FACULTY_MAP, embedder)
        rows = analyze(
            [rnd, ref],
            ["Random", "Refined"],
            [1.0, 1.0]
        )
        assert len(rows) == 2
        assert "Random" in str(rows[0])
        assert "Refined" in str(rows[1])
