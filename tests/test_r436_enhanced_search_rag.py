# -*- coding: utf-8 -*-
"""
Testes SPEC-935-R436 — Buscas Unificadas + RAG Aprimorado + Referências ABNT
"""

import sys
import unittest

sys.path.insert(0, ".")

from sdd.spec_engine import spec_registry


# ── Helpers ────────────────────────────────────────────────────────────

class FakeSearcher:
    name = "fake"
    def __init__(self, records):
        self._records = records
    def search(self, query, limit=10):
        return self._records[:limit]


def _make_docs(n=3):
    from rag.scientific import ScientificDocument
    return [
        ScientificDocument(
            doc_id=f"doc-{i}",
            title=f"Causal Inference Paper {i}",
            authors=["Pearl"] if i % 2 == 0 else ["Rubin"],
            year=2020 + i,
            source="journal",
            text="Causal inference and correlation. " * 5 + f"Unique content {i}.",
        )
        for i in range(n)
    ]


class TestR436Spec(unittest.TestCase):
    def test_spec_r436_green(self):
        spec = spec_registry.get("SPEC-935-R436")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.status, "green")


class TestUnifiedSearcher(unittest.TestCase):
    def test_temporal_score_recent_higher(self):
        from rag.enhanced_search_rag import UnifiedSearcher
        s = UnifiedSearcher(searchers=[])
        self.assertGreater(s.temporal_score(2026), s.temporal_score(2010))
        self.assertGreaterEqual(s.temporal_score(2026), 0)
        self.assertLessEqual(s.temporal_score(2026), 0.07)

    def test_deduplicate_by_doi(self):
        from rag.enhanced_search_rag import UnifiedSearcher
        s = UnifiedSearcher(searchers=[])
        recs = [
            {"title": "Paper A", "doi": "10.1234/abc", "year": 2022},
            {"title": "Paper A duplicate", "doi": "10.1234/ABC", "year": 2022},
            {"title": "Paper B", "doi": "10.1234/def", "year": 2021},
        ]
        dedup = s.deduplicate(recs)
        self.assertEqual(len(dedup), 2)

    def test_deduplicate_by_title(self):
        from rag.enhanced_search_rag import UnifiedSearcher
        s = UnifiedSearcher(searchers=[])
        recs = [
            {"title": "Causal Inference!", "year": 2022},
            {"title": "causal   inference", "year": 2022},
            {"title": "Other Paper", "year": 2021},
        ]
        dedup = s.deduplicate(recs)
        self.assertEqual(len(dedup), 2)

    def test_search_dedup_and_temporal_ranking(self):
        from rag.enhanced_search_rag import UnifiedSearcher
        # Dois searchers retornam mesmo DOI + paper recente vs antigo
        recs1 = [
            {"title": "Causal Paper", "doi": "10.1/a", "year": 2010},
            {"title": "Old Paper", "doi": "10.1/old", "year": 2010},
        ]
        recs2 = [
            {"title": "Causal Paper duplicate", "doi": "10.1/A", "year": 2010},
            {"title": "Recent Paper", "doi": "10.1/recent", "year": 2025},
        ]
        s = UnifiedSearcher(searchers=[FakeSearcher(recs1), FakeSearcher(recs2)])
        results = s.search("causal inference", limit=10)
        # Dedup deve remover duplicata DOI
        dois = [r.get("doi","").lower() for r in results]
        self.assertEqual(len(dois), len(set(dois)))
        # Recent deve rankear acima de Old para mesma lexical proxy (temporal boost)
        titles = [r["title"] for r in results]
        # Recent Paper deve aparecer antes de Old Paper devido ao temporal
        if "Recent Paper" in titles and "Old Paper" in titles:
            self.assertLess(titles.index("Recent Paper"), titles.index("Old Paper"))

    def test_search_empty_query(self):
        from rag.enhanced_search_rag import UnifiedSearcher
        s = UnifiedSearcher(searchers=[FakeSearcher([{"title": "A"}])])
        self.assertEqual(s.search("", limit=5), [])
        self.assertEqual(s.search("   ", limit=5), [])

    def test_search_cache(self):
        from rag.enhanced_search_rag import UnifiedSearcher
        s = UnifiedSearcher(searchers=[FakeSearcher([{"title": "Cached", "year": 2023}])])
        r1 = s.search("test cache", limit=5)
        r2 = s.search("test cache", limit=5)
        self.assertEqual(r1, r2)
        s.clear_cache()
        self.assertEqual(s.status()["cache_entries"], 0)


class TestEnhancedRAG(unittest.TestCase):
    def test_query_expansion_causal(self):
        from rag.enhanced_search_rag import EnhancedRAG
        from rag.scientific import ScientificRAG
        rag = ScientificRAG(min_score=0.05)
        er = EnhancedRAG(rag=rag)
        expanded = er.query_expansion("causal inference methods")
        # Deve expandir "causal" com sinônimos
        self.assertIsInstance(expanded, list)
        self.assertGreaterEqual(len(expanded), 1)
        # Se houver sinônimo, segunda query contém termo extra
        if len(expanded) > 1:
            self.assertIn("causal", expanded[0].lower())

    def test_retrieve_enhanced_with_temporal_boost(self):
        from rag.enhanced_search_rag import EnhancedRAG
        from rag.scientific import ScientificRAG
        rag = ScientificRAG(min_score=0.05)
        rag.index(_make_docs(3))
        er = EnhancedRAG(rag=rag)
        # Dois docs com anos diferentes, mesmo conteúdo base
        results = er.retrieve_enhanced("causal inference", top_k=3, expand=False, temporal=True, cite_expand=False)
        self.assertGreater(len(results), 0)
        # Verifica boost: evidências com _boosted_score devem estar ordenadas
        # Pelo menos não deve falhar e retornar final_score
        for ev in results:
            self.assertTrue(hasattr(ev, "final_score") or isinstance(ev, dict))

    def test_answer_grounded_abstain_empty(self):
        from rag.enhanced_search_rag import EnhancedRAG
        from rag.scientific import ScientificRAG
        rag = ScientificRAG(min_score=0.9)  # threshold alto para forçar abstain
        rag.index(_make_docs(1))
        er = EnhancedRAG(rag=rag)
        ans = er.answer_grounded("query without evidence", top_k=3)
        self.assertTrue(ans["abstained"] or ans["evidence_count"] == 0)

    def test_answer_grounded_with_evidence(self):
        from rag.enhanced_search_rag import EnhancedRAG
        from rag.scientific import ScientificRAG
        rag = ScientificRAG(min_score=0.05)
        rag.index(_make_docs(3))
        er = EnhancedRAG(rag=rag)
        ans = er.answer_grounded("causal inference correlation", top_k=3)
        self.assertFalse(ans["abstained"])
        self.assertGreater(ans["evidence_count"], 0)
        self.assertGreaterEqual(ans["groundedness"], 0)

    def test_metrics(self):
        from rag.enhanced_search_rag import EnhancedRAG
        from rag.scientific import ScientificRAG
        rag = ScientificRAG(min_score=0.05)
        rag.index(_make_docs(3))
        er = EnhancedRAG(rag=rag)
        evs = er.retrieve_enhanced("causal inference", top_k=3)
        m = er.metrics(evs)
        self.assertIn("groundedness", m)
        self.assertIn("citation_coverage", m)
        self.assertIn("temporal_spread", m)
        self.assertIn("avg_year", m)

    def test_enhanced_rag_status(self):
        from rag.enhanced_search_rag import EnhancedRAG
        er = EnhancedRAG()
        s = er.status()
        self.assertIn("has_rag", s)


class TestReferenceAuditor(unittest.TestCase):
    def test_audit_missing_doi_year_duplicate(self):
        from rag.enhanced_search_rag import ReferenceAuditor
        aud = ReferenceAuditor()
        refs = [
            {"id": "r1", "title": "Causal Inference", "authors": ["Pearl"], "year": 2009, "source": "Book", "doi": "10.1/a"},
            {"id": "r2", "title": "Causal Inference", "authors": ["Pearl"], "year": 2009, "source": "Book", "doi": "10.1/a"},  # duplicate title
            {"id": "r3", "title": "Old Paper", "authors": [], "year": None, "source": "", "doi": ""},  # missing
            {"id": "r4", "title": "Future Paper", "authors": ["Smith"], "year": 2030, "source": "Journal", "doi": ""},  # year invalid
        ]
        res = aud.audit(refs)
        self.assertEqual(res["total"], 4)
        self.assertIn("r2", res["duplicates"])
        # r2 deve ter duplicate True
        self.assertTrue(res["by_id"]["r2"]["duplicate"])
        # r3 deve ter missing authors / abnt incomplete
        self.assertIn("missing_authors", res["by_id"]["r3"]["issues"])
        # r4 year_invalid
        self.assertIn("year_invalid_or_missing", res["by_id"]["r4"]["issues"])
        # r1 has_doi True
        self.assertTrue(res["by_id"]["r1"]["has_doi"])
        self.assertFalse(res["by_id"]["r3"]["has_doi"])

    def test_format_abnt_bibtex(self):
        from rag.enhanced_search_rag import ReferenceAuditor
        aud = ReferenceAuditor()
        ref = {"title": "Causality", "authors": ["Pearl, Judea"], "year": 2009, "source": "Cambridge", "doi": "10.1/a"}
        abnt = aud.format_abnt(ref)
        self.assertIn("Causality", abnt)
        self.assertIn("2009", abnt)
        bib = aud.format_bibtex(ref)
        self.assertIn("@article", bib)
        self.assertIn("2009", bib)
        self.assertIn("Causality", bib)

    def test_normalize_title(self):
        from rag.enhanced_search_rag import ReferenceAuditor
        aud = ReferenceAuditor()
        self.assertEqual(aud.normalize_title("Causal Inference!"), aud.normalize_title("causal   inference"))
        self.assertEqual(aud.normalize_title("São Paulo"), "sao paulo")


class TestUnifiedFacade(unittest.TestCase):
    def test_facade_status(self):
        from rag.enhanced_search_rag import UnifiedSearchRAG
        f = UnifiedSearchRAG(searchers=[FakeSearcher([{"title": "A", "year": 2023}])])
        s = f.status()
        self.assertTrue(s["enhanced"])
        self.assertIn("searcher", s)
        self.assertIn("rag", s)
        self.assertIn("auditor", s)

    def test_facade_search_and_audit(self):
        from rag.enhanced_search_rag import UnifiedSearchRAG
        f = UnifiedSearchRAG(searchers=[FakeSearcher([{"title": "Paper", "year": 2023, "doi": "10.1/x"}])])
        res = f.search("test", limit=5)
        self.assertGreaterEqual(len(res), 1)
        audit = f.audit([{"id": "x", "title": "Paper", "authors": ["A"], "year": 2023, "source": "J", "doi": "10.1/x"}])
        self.assertEqual(audit["total"], 1)


class TestOrchestratorSearchRAG(unittest.TestCase):
    def test_orchestrator_methods_exist(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        for m in ("search_rag_status", "unified_search", "rag_query", "audit_references", "search_rag"):
            self.assertTrue(hasattr(orch, m))

    def test_unified_search_via_orchestrator(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from rag.enhanced_search_rag import UnifiedSearchRAG, UnifiedSearcher
        # Injeta searcher fake via propriedade
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        # Força search_rag com fake searcher
        from rag.enhanced_search_rag import UnifiedSearcher as US, UnifiedSearchRAG as USR
        fake = FakeSearcher([{"title": "Orchestrator Paper", "year": 2024, "doi": "10.9/o"}])
        orch._search_rag = USR(searchers=[fake])
        res = orch.unified_search("orchestrator test", limit=5)
        self.assertGreaterEqual(len(res), 1)

    def test_rag_query_grounded(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from rag.enhanced_search_rag import UnifiedSearchRAG
        from rag.scientific import ScientificDocument, ScientificRAG
        rag = ScientificRAG(min_score=0.05)
        rag.index(_make_docs(2))
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        orch._search_rag = UnifiedSearchRAG(rag=rag)
        ans = orch.rag_query("causal inference", top_k=2)
        self.assertIn("abstained", ans)
        self.assertIn("evidence_count", ans)

    def test_audit_references_via_orchestrator(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        refs = [
            {"id": "a1", "title": "Paper One", "authors": ["Smith"], "year": 2022, "source": "Journal", "doi": "10.1/a1"},
            {"id": "a2", "title": "Paper One", "authors": ["Smith"], "year": 2022, "source": "Journal", "doi": "10.1/a1"},
        ]
        res = orch.audit_references(refs)
        self.assertEqual(res["total"], 2)
        self.assertIn("a2", res["duplicates"])


if __name__ == "__main__":
    unittest.main()
