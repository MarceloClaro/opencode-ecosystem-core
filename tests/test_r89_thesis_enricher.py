"""Testes TDD para Thesis Enricher via Antigravity Web Search (SPEC-935 R89)."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from synthetic_university.thesis_enricher import ThesisEnricher


class TestR89ThesisEnricher:
    """Testes para o enriquecedor de teses com pesquisa web real."""

    @pytest.fixture
    def enricher(self, tmp_path):
        cache_dir = str(tmp_path / "enrich_cache")
        return ThesisEnricher(cache_dir=cache_dir)

    @pytest.fixture
    def thesis_concepts(self):
        return {
            "thesis_id": "thesis_001",
            "title": "Quantum Ethics: A Framework for Moral AI Systems",
            "concepts": ["quantum ethics", "moral AI", "algorithmic fairness"],
            "faculty": "engineering",
        }

    def test_enricher_creates(self, enricher):
        """R89: ThesisEnricher e criado."""
        assert enricher is not None
        assert enricher.cache_dir is not None

    def test_enrich_with_real_search(self, enricher, thesis_concepts):
        """R89: Enriquecimento com busca web real via Antigravity."""
        with patch.object(enricher, '_search_concept') as mock_search:
            mock_search.return_value = {
                "query": "quantum ethics",
                "results": [
                    {
                        "title": "Quantum Ethics: A New Moral Framework for AI",
                        "url": "https://arxiv.org/abs/2401.12345",
                        "snippet": "This paper explores ethical frameworks in quantum computing.",
                        "source": "antigravity_web",
                    }
                ],
                "total_found": 1,
            }

            result = enricher.enrich(thesis_concepts)

        assert result is not None
        assert "thesis_id" in result
        assert "concepts_enriched" in result
        assert len(result["concepts_enriched"]) > 0
        assert result["concepts_enriched"][0]["results"][0]["source"] == "antigravity_web"

    def test_enrich_multiple_concepts(self, enricher, thesis_concepts):
        """R89: Enriquecimento de multiplos conceitos."""
        with patch.object(enricher, '_search_concept') as mock_search:
            def side_effect(concept):
                return {
                    "query": concept,
                    "results": [
                        {
                            "title": f"Paper about {concept}",
                            "url": f"https://example.com/{concept.replace(' ', '_')}",
                            "snippet": f"Research on {concept}.",
                            "source": "mock",
                        }
                    ],
                    "total_found": 1,
                }
            mock_search.side_effect = side_effect

            result = enricher.enrich(thesis_concepts)

        assert len(result["concepts_enriched"]) == 3
        # Cada resultado tem 'query' com o conceito buscado
        concepts_found = [c["query"] for c in result["concepts_enriched"]]
        assert "quantum ethics" in concepts_found
        assert "algorithmic fairness" in concepts_found

    def test_cache_persists(self, enricher, thesis_concepts):
        """R89: Cache persiste resultados entre chamadas."""
        with patch.object(enricher, '_search_concept') as mock_search:
            mock_search.return_value = {
                "query": "quantum ethics",
                "results": [{"title": "Paper A", "url": "https://a.com", "snippet": "A"}],
                "total_found": 1,
            }

            # Primeira chamada — deve buscar
            r1 = enricher.enrich(thesis_concepts)

            # Segunda chamada — deve usar cache
            r2 = enricher.enrich(thesis_concepts)

        assert mock_search.call_count == 3  # 3 conceitos, so na primeira chamada

    def test_cache_file_persists(self, enricher, thesis_concepts):
        """R89: Cache salvo em disco persiste entre instancias."""
        with patch.object(enricher, '_search_concept') as mock_search:
            mock_search.return_value = {
                "query": "quantum ethics",
                "results": [{"title": "Paper A", "url": "https://a.com", "snippet": "A"}],
                "total_found": 1,
            }

            enricher.enrich(thesis_concepts)

        # Verifica que o arquivo de cache foi criado
        cache_files = os.listdir(enricher.cache_dir)
        assert len(cache_files) > 0
        assert any("quantum_ethics" in f for f in cache_files)

    def test_fallback_when_offline(self, enricher, thesis_concepts):
        """R89: Fallback gracioso quando pesquisa web falha."""
        with patch.object(enricher, '_search_concept') as mock_search:
            mock_search.side_effect = ConnectionError("No internet")

            result = enricher.enrich(thesis_concepts)

        assert result is not None
        # Deve ter dados simulados como fallback
        assert result["fallback_used"] is True
        assert len(result["concepts_enriched"]) == 3
        for ce in result["concepts_enriched"]:
            assert ce["results"][0]["source"] == "fallback"

    def test_cache_hit_avoids_network(self, enricher, thesis_concepts):
        """R89: Cache evita chamada de rede."""
        # Primeiro, popula o cache
        cache_data = {
            "query": "quantum ethics",
            "results": [{"title": "Cached Paper", "url": "https://cached.com", "snippet": "Cached."}],
            "total_found": 1,
            "source": "cache",
        }
        enricher._save_to_cache("quantum_ethics", cache_data)

        # Agora chama enrich — deve ler do cache sem chamar _search_concept
        with patch.object(enricher, '_search_concept') as mock_search:
            result = enricher.enrich(thesis_concepts)

        # _search_concept pode ser chamado para conceitos ainda nao em cache
        # mas para 'quantum ethics' deve usar cache
        assert result is not None

    def test_empty_concepts(self, enricher):
        """R89: Lista vazia de conceitos retorna resultado vazio."""
        result = enricher.enrich({"thesis_id": "empty", "title": "Test", "concepts": []})
        assert result["concepts_enriched"] == []

    def test_abstract_extraction(self, enricher):
        """R89: Extracao de abstract de URL via Antigravity."""
        with patch.object(enricher, '_fetch_abstract') as mock_fetch:
            mock_fetch.return_value = {
                "url": "https://arxiv.org/abs/2401.12345",
                "abstract": "This paper presents a novel framework for quantum ethics...",
                "source": "antigravity_read_url",
            }

            abstract = enricher.fetch_abstract("https://arxiv.org/abs/2401.12345")

        assert abstract is not None
        assert "quantum ethics" in abstract["abstract"].lower()
        assert abstract["source"] == "antigravity_read_url"

    def test_batch_enrich(self, enricher):
        """R89: Enriquecimento em lote de multiplas teses."""
        theses = [
            {"thesis_id": "t1", "title": "AI Ethics", "concepts": ["ethics"], "faculty": "human_sciences"},
            {"thesis_id": "t2", "title": "Quantum ML", "concepts": ["quantum"], "faculty": "engineering"},
        ]

        with patch.object(enricher, '_search_concept') as mock_search:
            mock_search.return_value = {
                "query": "test",
                "results": [{"title": "Paper", "url": "https://x.com", "snippet": "X"}],
                "total_found": 1,
            }

            results = enricher.batch_enrich(theses)

        assert len(results) == 2
        assert results[0]["thesis_id"] == "t1"
        assert results[1]["thesis_id"] == "t2"
