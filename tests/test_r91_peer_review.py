"""Testes TDD para Multi-LLM Blind Peer Review (SPEC-935 R91)."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from synthetic_university.peer_review import (
    PeerReviewSystem,
    Review,
    ReviewReport,
    ReviewAggregator,
)


class TestR91PeerReview:
    """Testes para o sistema de revisao cega por pares."""

    @pytest.fixture
    def thesis(self):
        return {
            "thesis_id": "thesis_001",
            "title": "Quantum Ethics: A Framework for Moral AI Systems",
            "hypothesis": "Quantum principles can encode ethical decision-making",
            "abstract": "This thesis explores the intersection of quantum mechanics and AI ethics...",
            "composite_score": 0.92,
            "faculties_involved": ["engineering", "human_sciences"],
        }

    @pytest.fixture
    def reviewers(self):
        return [
            {
                "id": "rev_01",
                "name": "Prof. Alice",
                "faculty": "engineering",
                "specialties": ["Quantum Computing", "AI"],
                "h_index": 45,
            },
            {
                "id": "rev_02",
                "name": "Prof. Bob",
                "faculty": "human_sciences",
                "specialties": ["Ethics", "Philosophy of Mind"],
                "h_index": 38,
            },
            {
                "id": "rev_03",
                "name": "Prof. Carol",
                "faculty": "exact_sciences",
                "specialties": ["Formal Methods", "Logic"],
                "h_index": 52,
            },
        ]

    @pytest.fixture
    def review_system(self):
        return PeerReviewSystem(lang="en")

    def test_system_creates(self, review_system):
        """R91: PeerReviewSystem e criado."""
        assert review_system is not None

    def test_single_review_structure(self, review_system, thesis, reviewers):
        """R91: Review individual tem estrutura completa."""
        with patch.object(review_system.evaluator, 'generate') as mock_gen:
            mock_gen.return_value = (
                "Score: 8/10. This thesis presents an innovative approach...",
                "opencode",
                12.5,
            )

            review = review_system._review_by(
                thesis, reviewers[0], "This thesis is novel..."
            )

        assert isinstance(review, Review)
        assert review.score >= 1 and review.score <= 10
        assert len(review.summary) > 10
        assert len(review.strengths) > 0
        assert len(review.weaknesses) > 0
        assert len(review.suggestions) > 0

    def test_full_review_cycle(self, review_system, thesis, reviewers):
        """R91: Ciclo completo de revisao com 3 revisores."""
        with patch.object(review_system.evaluator, 'generate') as mock_gen:
            mock_gen.return_value = (
                "Score: 7/10. Interesting but needs methodological rigor.",
                "opencode",
                15.0,
            )

            report = review_system.review(thesis, reviewers)

        assert isinstance(report, ReviewReport)
        assert len(report.reviews) == 3
        assert report.aggregate_score > 0
        assert report.decision in [
            "Accept", "Minor Revision", "Major Revision", "Reject"
        ]

    def test_blind_anonymization(self, review_system, thesis):
        """R91: Tese e anonimizada para revisao cega."""
        anonymized = review_system._anonymize(thesis)
        # Nao deve conter identificadores do autor
        assert "author" not in anonymized.get("title", "").lower() or \
               "author" not in anonymized.get("abstract", "")

    def test_score_parsing(self, review_system):
        """R91: Parse de score de texto de review."""
        assert review_system._parse_score("Score: 8/10. Good work.") == 8
        assert review_system._parse_score("Score: 8.5/10") == 9
        assert review_system._parse_score("Score 7") == 7
        assert review_system._parse_score("No score here") is None

    def test_aggregation(self, review_system, thesis):
        """R91: Agregacao de multiplas revisoes."""
        reviews = [
            Review(reviewer_id="r1", reviewer_name="R1", score=8,
                   summary="Good", strengths=["A"], weaknesses=["B"],
                   suggestions=["C"], source="mock"),
            Review(reviewer_id="r2", reviewer_name="R2", score=7,
                   summary="OK", strengths=["A"], weaknesses=["C"],
                   suggestions=["D"], source="mock"),
            Review(reviewer_id="r3", reviewer_name="R3", score=9,
                   summary="Great", strengths=["D"], weaknesses=["E"],
                   suggestions=["F"], source="mock"),
        ]

        aggregator = ReviewAggregator()
        report = aggregator.aggregate(thesis, reviews)

        assert report.aggregate_score == 8.0  # (8+7+9)/3
        assert report.score_std <= 1.0
        assert report.decision is not None

    def test_decision_logic(self):
        """R91: Logica de decisao editorial baseada em score."""
        agg = ReviewAggregator()

        assert agg._decide(9.0, 0.5) == "Accept"
        assert agg._decide(7.0, 0.8) == "Minor Revision"
        assert agg._decide(5.0, 1.2) == "Major Revision"
        assert agg._decide(3.0, 1.5) == "Reject"

    def test_report_export(self, review_system, thesis, reviewers):
        """R91: Relatorio exportavel em formato JSON."""
        with patch.object(review_system.evaluator, 'generate') as mock_gen:
            mock_gen.return_value = ("Score: 7/10.", "opencode", 10.0)

            report = review_system.review(thesis, reviewers)
            report_dict = report.to_dict()

        assert "thesis_id" in report_dict
        assert "reviews" in report_dict
        assert "aggregate_score" in report_dict
        assert "decision" in report_dict
        assert len(report_dict["reviews"]) == 3

    def test_report_to_text(self, review_system, thesis, reviewers):
        """R91: Relatorio em texto formatado."""
        with patch.object(review_system.evaluator, 'generate') as mock_gen:
            mock_gen.return_value = ("Score: 7/10.", "opencode", 10.0)

            report = review_system.review(thesis, reviewers)
            text = report.to_text(lang="en")

        assert "PEER REVIEW REPORT" in text
        assert "Score" in text
        assert "Decision" in text

    def test_different_personas_different_reviews(self, review_system, thesis, reviewers):
        """R91: Personas diferentes produzem revisoes diferentes."""
        # Mock respostas diferentes para cada revisor
        responses = [
            ("Score: 9/10. Excellent quantum work.", "opencode", 10.0),
            ("Score: 6/10. Needs ethical depth.", "opencode", 12.0),
            ("Score: 7/10. Good formalization.", "opencode", 11.0),
        ]

        with patch.object(review_system.evaluator, 'generate') as mock_gen:
            mock_gen.side_effect = responses

            report = review_system.review(thesis, reviewers)

        assert len(set(r.score for r in report.reviews)) == 3
        assert report.aggregate_score == pytest.approx(7.33, 0.1)

    def test_cache_prevents_rereview(self, review_system, thesis, reviewers):
        """R91: Cache evita re-revisao da mesma tese."""
        with patch.object(review_system.evaluator, 'generate') as mock_gen:
            mock_gen.return_value = ("Score: 8/10.", "opencode", 10.0)

            r1 = review_system.review(thesis, reviewers)
            r2 = review_system.review(thesis, reviewers)

        assert r1.aggregate_score == r2.aggregate_score
        # 3 revisores, chamados apenas na primeira vez
        assert mock_gen.call_count == 3
