"""Testes TDD para Academic Novelty Analysis (SPEC-935 R93)."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from synthetic_university.novelty_analysis import (
    NoveltyAnalyzer,
    NoveltyReport,
    ContributionMap,
)


class TestR93NoveltyAnalysis:
    """Testes para analise de novidade academica."""

    @pytest.fixture
    def thesis(self):
        return {
            "thesis_id": "thesis_001",
            "title": "Quantum Ethics: A Framework for Moral AI Systems",
            "hypothesis": "Quantum principles can encode ethical decision-making",
            "abstract": "Novel framework bridging quantum mechanics and AI ethics.",
            "concepts": ["quantum ethics", "moral AI", "formal verification"],
            "composite_score": 0.92,
        }

    @pytest.fixture
    def analyzer(self):
        return NoveltyAnalyzer(lang="en")

    def test_analyzer_creates(self, analyzer):
        """R93: NoveltyAnalyzer e criado."""
        assert analyzer is not None

    def test_novelty_analysis(self, analyzer, thesis):
        """R93: Analise completa de novidade."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.return_value = [
                {"title": "Paper on quantum computing ethics", "year": 2024, "relevance": 0.7},
                {"title": "AI ethics survey", "year": 2023, "relevance": 0.5},
            ]

            report = analyzer.analyze(thesis)

        assert isinstance(report, NoveltyReport)
        assert report.novelty_score > 0
        assert report.novelty_score <= 100
        assert len(report.related_works) > 0

    def test_novelty_components(self, analyzer, thesis):
        """R93: Score de novidade tem componentes."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.return_value = []

            report = analyzer.analyze(thesis)

        assert report.components is not None
        assert "originality" in report.components
        assert "non_triviality" in report.components
        assert "impact_potential" in report.components

    def test_contribution_map(self, analyzer, thesis):
        """R93: Mapa de contribuicoes vs estado da arte."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.return_value = [
                {"title": "Existing ethics framework", "year": 2022, "relevance": 0.8},
            ]

            report = analyzer.analyze(thesis)

        assert report.contribution_map is not None
        assert len(report.contribution_map.additions) > 0

    def test_related_works_semantic(self, analyzer, thesis):
        """R93: Trabalhos relacionados tem analise semantica."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.return_value = [
                {"title": "Related paper A", "year": 2024, "relevance": 0.9},
            ]

            report = analyzer.analyze(thesis)

        assert len(report.related_works) > 0
        for rw in report.related_works:
            assert "title" in rw
            assert "year" in rw
            assert "relevance" in rw

    def test_positioning_statement(self, analyzer, thesis):
        """R93: Relatorio de posicionamento academico."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.return_value = []

            report = analyzer.analyze(thesis)
            statement = report.positioning

        assert statement is not None
        assert len(statement) > 50

    def test_report_export(self, analyzer, thesis):
        """R93: Relatorio exportavel como dict/JSON."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.return_value = []

            report = analyzer.analyze(thesis)
            d = report.to_dict()

        assert "thesis_id" in d
        assert "novelty_score" in d
        assert "components" in d
        assert "positioning" in d

    def test_search_fallback(self, analyzer, thesis):
        """R93: Fallback quando busca falha."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.side_effect = ConnectionError("Network error")

            # Nao deve lancar excecao
            report = analyzer.analyze(thesis)

        assert report is not None
        assert report.novelty_score > 0

    def test_cache(self, analyzer, thesis):
        """R93: Cache evita re-analise."""
        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.return_value = [{"title": "Existing work", "year": 2023, "relevance": 0.6}]

            r1 = analyzer.analyze(thesis)
            r2 = analyzer.analyze(thesis)

        assert r1.novelty_score == r2.novelty_score
        assert mock_search.call_count == 1  # so primeira vez

    def test_different_theses_different_scores(self, analyzer):
        """R93: Teses diferentes tem scores diferentes."""
        t1 = {"thesis_id": "t1", "title": "Bold new paradigm", "hypothesis": "Revolutionary idea",
              "abstract": "disruptive approach", "concepts": ["novel"], "composite_score": 0.9}
        t2 = {"thesis_id": "t2", "title": "Incremental improvement", "hypothesis": "Small optimization",
              "abstract": "minor enhancement", "concepts": ["standard"], "composite_score": 0.6}

        with patch.object(analyzer, '_search_literature') as mock_search:
            mock_search.side_effect = [
                [{"title": "Standard paper", "year": 2024, "relevance": 0.3}],
                [{"title": "Many existing papers", "year": 2024, "relevance": 0.9}],
            ]

            r1 = analyzer.analyze(t1)
            r2 = analyzer.analyze(t2)

        # Tese mais inovadora deve ter score maior
        assert r1.novelty_score >= r2.novelty_score
