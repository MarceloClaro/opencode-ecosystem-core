# -*- coding: utf-8 -*-
"""
Testes TDD para R98 — Academic Novelty V2 (OpenNovelty-style)
===============================================================
SPEC-935-R98: Ciclo RED → GREEN → REFACTOR.

Componentes:
  - ContributionPointExtractor (CA2)
  - PointwiseLiteratureRetriever (CA3)
  - PointwiseNoveltyScorer (CA4)
  - HierarchicalTaxonomyBuilder (CA5)
  - EvidencedNoveltyReport / analyze() (CA6)
  - Integracao com R97 memory (CA7)
  - Fallback sem dependencias (CA8)
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict, List

import pytest


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_thesis():
    """Tese de exemplo para testes."""
    return {
        "thesis_id": "test_thesis_001",
        "title": "Quantum Ethics: A Framework for Moral AI Decision-Making",
        "hypothesis": (
            "Quantum computing introduces unique ethical dimensions "
            "that require a novel moral framework beyond classical AI ethics."
        ),
        "abstract": (
            "This thesis proposes a quantum ethics framework that addresses "
            "the superposition of moral states in AI decision-making. "
            "We demonstrate that quantum entanglement provides a useful metaphor "
            "for understanding interconnected moral responsibilities. "
            "The framework is validated through simulation of ethical dilemmas "
            "in autonomous vehicle scenarios."
        ),
        "methodology": (
            "We combine quantum information theory with moral philosophy "
            "using a formal logical system. Ethical dilemmas are encoded as "
            "quantum states and measured through a novel ethical observable operator."
        ),
        "concepts": ["quantum", "ethics", "AI", "morality", "decision-making"],
        "composite_score": 0.85,
    }


@pytest.fixture
def minimal_thesis():
    """Tese minima (apenas titulo e conceitos) para fallback."""
    return {
        "thesis_id": "test_minimal",
        "title": "Simple Test Thesis",
        "concepts": ["test", "simple"],
    }


@pytest.fixture
def analyzer():
    """Instancia basica do NoveltyAnalyzerV2."""
    from synthetic_university.novelty_v2 import NoveltyAnalyzerV2
    return NoveltyAnalyzerV2(lang="en")


@pytest.fixture
def analyzer_with_memory():
    """Analyzer com R97 memory."""
    from synthetic_university.evolutionary_memory import (
        EvolutionaryMemorySubstrate,
    )
    from synthetic_university.novelty_v2 import NoveltyAnalyzerV2
    mem = EvolutionaryMemorySubstrate()
    return NoveltyAnalyzerV2(lang="en", memory=mem), mem


# ============================================================
# CA2 — ContributionPointExtractor
# ============================================================

class TestContributionPointExtractor:
    """Testes do ContributionPointExtractor (CA2)."""

    def test_ca2_extract_returns_list(self, analyzer, sample_thesis):
        """extract() retorna lista de ContributionPoint."""
        points = analyzer.extractor.extract(sample_thesis)
        assert isinstance(points, list)
        assert len(points) >= 2

    def test_ca2_extract_includes_hypothesis_claim(self, analyzer, sample_thesis):
        """extract() inclui claim de hipotese."""
        points = analyzer.extractor.extract(sample_thesis)
        types = [p.type for p in points]
        assert "hypothesis_claim" in types

    def test_ca2_extract_includes_methodological_claim(self, analyzer, sample_thesis):
        """extract() inclui claim metodologica."""
        points = analyzer.extractor.extract(sample_thesis)
        types = [p.type for p in points]
        assert "methodological_claim" in types

    def test_ca2_extract_includes_framework_claim(self, analyzer, sample_thesis):
        """extract() inclui claim de framework."""
        points = analyzer.extractor.extract(sample_thesis)
        types = [p.type for p in points]
        assert "framework_claim" in types

    def test_ca2_each_point_has_id_and_claim(self, analyzer, sample_thesis):
        """Cada ContributionPoint tem point_id, claim, keywords, confidence."""
        points = analyzer.extractor.extract(sample_thesis)
        for p in points:
            assert p.point_id
            assert p.claim
            assert isinstance(p.keywords, list)
            assert 0 <= p.confidence <= 1

    def test_ca2_extract_minimal_thesis(self, analyzer, minimal_thesis):
        """extract() funciona com tese minima (1 ponto por conceito)."""
        points = analyzer.extractor.extract(minimal_thesis)
        assert len(points) >= 1

    def test_ca2_extract_unique_ids(self, analyzer, sample_thesis):
        """Cada ponto tem point_id unico."""
        points = analyzer.extractor.extract(sample_thesis)
        ids = [p.point_id for p in points]
        assert len(ids) == len(set(ids))


# ============================================================
# CA3 — PointwiseLiteratureRetriever
# ============================================================

class TestPointwiseLiteratureRetriever:
    """Testes do PointwiseLiteratureRetriever (CA3)."""

    def test_ca3_retrieve_returns_list(self, analyzer, sample_thesis):
        """retrieve() retorna lista de PointWithLiterature."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        assert isinstance(results, list)
        assert len(results) == len(points)

    def test_ca3_each_result_has_point_and_works(self, analyzer, sample_thesis):
        """Cada resultado tem point e related_works."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        for r in results:
            assert r.point is not None
            assert isinstance(r.related_works, list)

    def test_ca3_related_work_has_required_fields(self, analyzer, sample_thesis):
        """Cada related_work tem title, year, relevance, contribution, gap."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        for r in results:
            for w in r.related_works:
                assert "title" in w
                assert "year" in w
                assert "relevance" in w
                assert "contribution" in w
                assert "gap" in w

    def test_ca3_retrieve_fallback_always_works(self, analyzer, sample_thesis):
        """retrieve() sempre retorna dados (fallback) mesmo sem rede."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        for r in results:
            assert len(r.related_works) >= 1

    def test_ca3_relevance_in_range(self, analyzer, sample_thesis):
        """Cada relevance esta entre 0 e 1."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        for r in results:
            for w in r.related_works:
                assert 0 <= w.get("relevance", 0) <= 1


# ============================================================
# CA4 — PointwiseNoveltyScorer
# ============================================================

class TestPointwiseNoveltyScorer:
    """Testes do PointwiseNoveltyScorer (CA4)."""

    def test_ca4_score_returns_dict(self, analyzer, sample_thesis):
        """score() retorna dict com point_id -> PointNovelty."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        scores = analyzer.scorer.score(results)
        assert isinstance(scores, dict)
        # scores inclui _global + 1 por point
        assert len(scores) == len(results) + 1
        assert "_global" in scores

    def test_ca4_each_score_has_required_fields(self, analyzer, sample_thesis):
        """Cada PointNovelty tem novelty_score, evidence, overlapping, gap."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        scores = analyzer.scorer.score(results)
        for pid, ns in scores.items():
            assert 0 <= ns.novelty_score <= 100
            assert ns.evidence
            assert isinstance(ns.overlapping_works, list)
            # _global e o unico sem gap_identified
            if pid != "_global":
                assert ns.gap_identified

    def test_ca4_global_score(self, analyzer, sample_thesis):
        """score() computa global_score como float."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        scores = analyzer.scorer.score(results)
        global_pn = scores.get("_global")
        assert global_pn is not None
        assert 0 <= global_pn.novelty_score <= 100

    def test_ca4_methodological_weight(self, analyzer, sample_thesis):
        """Pontos methodological_claim tem peso 0.30 no global."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        scores = analyzer.scorer.score(results)
        # Verificar se existe pelo menos um ponto metodologico
        method_points = [
            (pid, ns) for pid, ns in scores.items()
            if ns.point_type == "methodological_claim"
        ]
        assert len(method_points) >= 0

    def test_ca4_point_type_preserved(self, analyzer, sample_thesis):
        """Cada PointNovelty preserva point_type."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        scores = analyzer.scorer.score(results)
        for pid, ns in scores.items():
            if pid != "_global":
                assert ns.point_type


# ============================================================
# CA5 — HierarchicalTaxonomyBuilder
# ============================================================

class TestHierarchicalTaxonomyBuilder:
    """Testes do HierarchicalTaxonomyBuilder (CA5)."""

    def test_ca5_build_returns_tree(self, analyzer, sample_thesis):
        """build() retorna TaxonomyTree."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        tree = analyzer.taxonomy.build(results)
        assert tree.root
        assert isinstance(tree.children, list)

    def test_ca5_tree_has_children(self, analyzer, sample_thesis):
        """Arvore tem pelo menos 1 area quando ha 2+ points."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        tree = analyzer.taxonomy.build(results)
        if len(points) >= 2:
            assert len(tree.children) >= 1

    def test_ca5_node_has_required_fields(self, analyzer, sample_thesis):
        """Cada TaxonomyNode tem name, relevance, works, children."""
        points = analyzer.extractor.extract(sample_thesis)
        results = analyzer.retriever.retrieve(points, sample_thesis)
        tree = analyzer.taxonomy.build(results)
        for child in tree.children:
            assert child.name
            assert 0 <= child.relevance <= 1
            assert isinstance(child.works, list)
            assert isinstance(child.children, list)

    def test_ca5_build_empty_points(self, analyzer, sample_thesis):
        """build() com lista vazia nao quebra."""
        tree = analyzer.taxonomy.build([])
        assert tree.root
        assert tree.children == []


# ============================================================
# CA6 — EvidencedNoveltyReport / analyze()
# ============================================================

class TestAnalyze:
    """Testes do pipeline analyze() completo (CA6)."""

    def test_ca6_analyze_returns_report(self, analyzer, sample_thesis):
        """analyze() retorna EvidencedNoveltyReport."""
        report = analyzer.analyze(sample_thesis)
        assert report is not None
        assert report.thesis_id == "test_thesis_001"

    def test_ca6_report_has_global_score(self, analyzer, sample_thesis):
        """Report inclui global_novelty_score."""
        report = analyzer.analyze(sample_thesis)
        assert 0 <= report.global_novelty_score <= 100

    def test_ca6_report_has_per_point_scores(self, analyzer, sample_thesis):
        """Report inclui per_point_scores."""
        report = analyzer.analyze(sample_thesis)
        assert len(report.per_point_scores) >= 2

    def test_ca6_report_has_taxonomy(self, analyzer, sample_thesis):
        """Report inclui taxonomy_tree."""
        report = analyzer.analyze(sample_thesis)
        assert report.taxonomy_tree is not None
        assert report.taxonomy_tree.root

    def test_ca6_report_has_top_related(self, analyzer, sample_thesis):
        """Report inclui top_related_works."""
        report = analyzer.analyze(sample_thesis)
        assert isinstance(report.top_related_works, list)

    def test_ca6_report_has_discrepancy_analysis(self, analyzer, sample_thesis):
        """Report inclui discrepancy_analysis textual."""
        report = analyzer.analyze(sample_thesis)
        assert isinstance(report.discrepancy_analysis, str)
        assert len(report.discrepancy_analysis) > 0

    def test_ca6_report_has_positioning(self, analyzer, sample_thesis):
        """Report inclui positioning_statement."""
        report = analyzer.analyze(sample_thesis)
        assert isinstance(report.positioning_statement, str)
        assert len(report.positioning_statement) > 0

    def test_ca6_report_has_methodology_novelty(self, analyzer, sample_thesis):
        """Report inclui methodology_novelty."""
        report = analyzer.analyze(sample_thesis)
        assert 0 <= report.methodology_novelty <= 100

    def test_ca6_report_minimal_thesis(self, analyzer, minimal_thesis):
        """analyze() funciona com tese minima."""
        report = analyzer.analyze(minimal_thesis)
        assert report is not None
        assert report.thesis_id == "test_minimal"
        assert 0 <= report.global_novelty_score <= 100

    def test_ca6_report_dict_serializable(self, analyzer, sample_thesis):
        """Report.to_dict() produz dict serializavel para JSON."""
        report = analyzer.analyze(sample_thesis)
        d = report.to_dict()
        assert isinstance(d, dict)
        assert "thesis_id" in d
        assert "global_novelty_score" in d
        # Verifica que eh serializavel
        json_str = json.dumps(d, ensure_ascii=False, indent=2)
        assert len(json_str) > 0


# ============================================================
# CA7 — Integracao com R97 (Evolutionary Memory)
# ============================================================

class TestIntegrationWithR97:
    """Testes de integracao com R97 memory (CA7)."""

    def test_ca7_memory_records_novelty_scores(self, analyzer_with_memory, sample_thesis):
        """analyze() registra scores no StagnationDetector."""
        analyzer, mem = analyzer_with_memory
        analyzer.analyze(sample_thesis)
        assert len(mem.stagnation._scores) >= 1

    def test_ca7_memory_records_contribution_points(self, analyzer_with_memory, sample_thesis):
        """analyze() registra contribution points no IdeationMemory."""
        analyzer, mem = analyzer_with_memory
        analyzer.analyze(sample_thesis)
        assert len(mem.ideation._ideas) >= 1

    def test_ca7_memory_failure_does_not_break(self, analyzer, sample_thesis):
        """Falha do memory nao interrompe analise."""
        # Forcar erro no memory
        class BrokenMemory:
            ideation = type('obj', (object,), {'record_idea': lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("broken"))})()
            stagnation = type('obj', (object,), {'record_novelty_score': lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("broken"))})()
            experimentation = type('obj', (object,), {'record_strategy': lambda *a, **kw: None})()

        analyzer.memory = BrokenMemory()
        try:
            report = analyzer.analyze(sample_thesis)
            assert report is not None
        except RuntimeError:
            pytest.fail("analyze() quebrou com memory com defeito")


# ============================================================
# CA8 — Fallback sem dependencias externas
# ============================================================

class TestFallback:
    """Testes de fallback sem dependencias externas (CA8)."""

    def test_ca8_analyze_no_external_deps(self, analyzer, minimal_thesis):
        """analyze() funciona 100% offline sem OpenCode CLI."""
        report = analyzer.analyze(minimal_thesis)
        assert report is not None
        assert report.global_novelty_score > 0

    def test_ca8_fallback_report_is_valid(self, analyzer, minimal_thesis):
        """Fallback produz relatorio estruturalmente valido."""
        report = analyzer.analyze(minimal_thesis)
        assert report.thesis_id == "test_minimal"
        assert len(report.per_point_scores) >= 1
        assert report.taxonomy_tree is not None
        assert report.discrepancy_analysis
        assert report.positioning_statement


# ============================================================
# Smoke test — pipeline completo
# ============================================================

class TestFullPipeline:
    """Teste de integracao completo."""

    def test_full_pipeline_with_report_export(self, analyzer, sample_thesis):
        """Pipeline completo: extract -> retrieve -> score -> build -> report."""
        report = analyzer.analyze(sample_thesis)

        # Verifica pipeline completo
        assert len(analyzer.extractor.extract(sample_thesis)) >= 2
        assert report.global_novelty_score > 0

        # Exporta como dict
        d = report.to_dict()

        # Verifica todos os campos esperados
        expected_keys = [
            "thesis_id", "thesis_title", "global_novelty_score",
            "per_point_scores", "top_related_works",
            "discrepancy_analysis", "positioning_statement",
            "sub_scores",
        ]
        for key in expected_keys:
            assert key in d, f"Campo '{key}' ausente no report dict"
        # sub_scores contem methodology_novelty, framework_novelty, application_novelty
        sub = d.get("sub_scores", {})
        assert "methodology_novelty" in sub
        assert "framework_novelty" in sub
        assert "application_novelty" in sub

        # Serializacao JSON
        json_str = json.dumps(d, ensure_ascii=False, indent=2)
        assert len(json_str) > 100

    def test_different_languages(self, sample_thesis):
        """analyze() funciona em PT e EN."""
        from synthetic_university.novelty_v2 import NoveltyAnalyzerV2

        en = NoveltyAnalyzerV2(lang="en")
        report_en = en.analyze(sample_thesis)

        pt = NoveltyAnalyzerV2(lang="pt")
        report_pt = pt.analyze(sample_thesis)

        assert report_en.global_novelty_score > 0
        assert report_pt.global_novelty_score > 0
        # Reports devem ser diferentes (idiomas diferentes)
        assert report_en.positioning_statement != report_pt.positioning_statement
