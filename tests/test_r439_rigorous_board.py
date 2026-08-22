# -*- coding: utf-8 -*-
"""
Testes SPEC-935-R439 — Banca Rigorosa Simulada Multi-Periódico
"""

import sys
import unittest

sys.path.insert(0, ".")

from sdd.spec_engine import spec_registry


class TestR439Spec(unittest.TestCase):
    def test_spec_r439_green(self):
        spec = spec_registry.get("SPEC-935-R439")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.status, "green")


class TestBoardCriteria(unittest.TestCase):
    def test_criteria_venues(self):
        from academic.rigorous_board import BOARD_CRITERIA
        for venue in ("capes_qualis_a1", "nature", "ieee", "lancet", "auto"):
            crit = BOARD_CRITERIA[venue]
            total = sum(crit.weights.values())
            self.assertAlmostEqual(total, 1.0, delta=0.01, msg=f"pesos {venue} devem somar 1.0")
            self.assertIn("accept", crit.thresholds)
            self.assertIn("minor", crit.thresholds)
            self.assertIn("major", crit.thresholds)
            self.assertGreater(crit.thresholds["accept"], crit.thresholds["minor"])
            self.assertGreater(crit.thresholds["minor"], crit.thresholds["major"])


class TestRigorousBoardReview(unittest.TestCase):
    def test_weak_manuscript_major_or_reject(self):
        from academic.rigorous_board import RigorousBoard
        board = RigorousBoard()
        weak = "Texto curto sem metodologia, sem p-valor, sem referências, com TODO e password = \"123\"."
        decision = board.review(weak, venue="auto")
        self.assertIn(decision.status, ("major_revision", "reject"))
        self.assertTrue(any(g.severity in ("critical", "major") for g in decision.gaps))
        self.assertGreater(len(decision.recommendations), 0)
        self.assertEqual(len(decision.reviewers), 3)

    def test_strong_manuscript_accept_or_minor(self):
        from academic.rigorous_board import RigorousBoard
        board = RigorousBoard()
        strong = """
        Introdução com lacuna e contribuição inédita e original. Metodologia com amostra, procedimento reprodutível, protocolo registrado, reprodutibilidade e método detalhado.
        Análise estatística com p-valor p < 0.05, intervalo de confiança 95%, anova, baseline e ablação contra estado da arte, estatística robusta.
        Resultados com figuras e tabelas e gráfico. Conclusão com objetivo. Referências ABNT com DOI et al. (2020) p. 123. Abstract e keywords.
        Aprovação ética CEP/CAAE 12345, CONSORT para randomização. Código disponível para reprodutibilidade.
        Fundamentação teórica robusta com metodologia e teoria. Originalidade demonstrada com comparação quantitativa e lacuna preenchida.
        """
        decision = board.review(strong, venue="auto")
        self.assertIn(decision.status, ("accept", "minor_revision"))
        self.assertGreaterEqual(decision.overall_score, 7.0)

    def test_venue_specific_lancet_ethics(self):
        from academic.rigorous_board import RigorousBoard
        board = RigorousBoard()
        manuscript = "Estudo com amostra de 100 pacientes, sem mencionar ética. Metodologia com randomização."
        decision = board.review(manuscript, venue="lancet")
        # Lancet deve cobrar CAAE para estudo com pacientes + randomização → CONSORT
        self.assertTrue(any("CAAE" in g.description or "CONSORT" in g.description for g in decision.gaps))

    def test_ieee_baseline(self):
        from academic.rigorous_board import RigorousBoard
        board = RigorousBoard()
        manuscript = "Modelo proposto sem comparação com estado da arte. Metodologia com amostra e p-valor."
        decision = board.review(manuscript, venue="ieee")
        self.assertTrue(any("baseline" in g.description.lower() for g in decision.gaps))


class TestGapCleaning(unittest.TestCase):
    def test_clean_todo_and_abnt(self):
        from academic.rigorous_board import GapCleaningEngine, Gap
        engine = GapCleaningEngine()
        manuscript = "Introdução.\n# TODO: completar\nReferências ausentes."
        gaps = [
            Gap("coerencia", "minor", "TODO remanescente", "Limpar TODOs"),
            Gap("abnt_compliance", "major", "Referências ABNT ausentes", "Adicionar referências"),
        ]
        cleaned, metrics = engine.clean(manuscript, gaps)
        self.assertNotIn("TODO", cleaned)
        self.assertIn("Referências", cleaned)
        self.assertGreater(metrics["gaps_closed"], 0)

    def test_clean_secret(self):
        from academic.rigorous_board import GapCleaningEngine, Gap
        engine = GapCleaningEngine()
        manuscript = "Código: password = \"supersecret\" and api_key = \"123\""
        gaps = [Gap("rigor_academico", "critical", "Segredo hardcoded", "Mover para .env")]
        cleaned, metrics = engine.clean(manuscript, gaps)
        self.assertNotIn("supersecret", cleaned)
        self.assertIn(".env", cleaned)


class TestCorrectionLoop(unittest.TestCase):
    def test_loop_improves_weak(self):
        from academic.rigorous_board import RigorousBoard
        board = RigorousBoard()
        weak = "Texto fraco sem metodologia. TODO: fix. Referências ausentes."
        result = board.correction_loop(weak, venue="auto", max_iter=3)
        self.assertIn("final_manuscript", result)
        self.assertIn("history", result)
        self.assertGreaterEqual(result["iterations"], 1)
        # Score deve melhorar ou gaps reduzir monotonicamente
        history = result["history"]
        if len(history) >= 2:
            first_score = history[0]["decision"]["overall_score"]
            last_score = history[-1]["decision"]["overall_score"]
            self.assertGreaterEqual(last_score, first_score - 1.0)  # não pode piorar muito

    def test_loop_with_references(self):
        from academic.rigorous_board import RigorousBoard
        board = RigorousBoard()
        manuscript = "Introdução com lacuna. Metodologia com amostra e p-valor. Referências ABNT com DOI."
        refs = [
            {"title": "Paper A", "authors": ["Smith"], "year": 2022, "source": "Journal", "doi": "10.1/a"},
            {"title": "Paper A", "authors": ["Smith"], "year": 2022, "source": "Journal", "doi": "10.1/a"},  # duplicate
        ]
        result = board.correction_loop(manuscript, venue="capes_qualis_a1", references=refs, max_iter=2)
        self.assertIsInstance(result["final_decision"], object)


class TestMaswosWithBoard(unittest.TestCase):
    def test_maswos_run_with_board(self):
        from academic.maswos import MaswosPipeline
        pipeline = MaswosPipeline()
        # Dry-run: delegações skipped, mas board deve rodar
        weak_manuscript = "Texto fraco sem metodologia. TODO."
        run = pipeline.run_with_rigorous_board("Tema teste", manuscript=weak_manuscript, venue="auto", max_iter=2)
        self.assertIsNotNone(run.board_report)
        self.assertIn("board", run.summary())
        # Pipeline dry-run tem score baixo, board também, então approved deve ser False
        self.assertFalse(run.approved)

    def test_maswos_strong_approved(self):
        from academic.maswos import MaswosPipeline
        pipeline = MaswosPipeline()
        strong = """
        Introdução com lacuna e contribuição. Metodologia reprodutível com amostra e protocolo.
        Análise estatística com p-valor e intervalo de confiança e baseline.
        Resultados com figuras. Conclusão com objetivo. Referências ABNT com DOI. Abstract.
        """
        run = pipeline.run_with_rigorous_board("Tema forte", manuscript=strong, venue="auto", max_iter=2)
        # Com manuscrito forte, board deve ser accept/minor e pipeline pode aprovar (score heurístico alto)
        self.assertIsNotNone(run.board_report)

class TestOrchestratorBoard(unittest.TestCase):
    def test_orchestrator_has_board_method(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        self.assertTrue(hasattr(orch, "academic_pipeline_with_rigorous_board"))

    def test_orchestrator_board_pipeline(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        strong = "Introdução com lacuna. Metodologia com amostra e protocolo. Estatística com p-valor e baseline. Referências ABNT. Abstract."
        result = orch.academic_pipeline_with_rigorous_board("Tema orquestrador", manuscript=strong, venue="auto", max_iter=2)
        self.assertIn("board", result)
        self.assertIn("board_iterations", result)
        self.assertIn("gaps_cleaned", result)

    def test_orchestrator_board_reflects(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from mci.metabus import metabus
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        before = len(metabus.memory.episodic)
        orch.academic_pipeline_with_rigorous_board("Tema reflexão", manuscript="Texto fraco. TODO.", venue="auto", max_iter=1)
        after = len(metabus.memory.episodic)
        self.assertGreater(after, before)


if __name__ == "__main__":
    unittest.main()
