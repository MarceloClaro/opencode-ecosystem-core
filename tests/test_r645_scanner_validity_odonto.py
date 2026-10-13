"""R645/R815: triagem lexical OdontoCA não substitui análise de risco de viés.

Os testes antigos congelavam bugs e uma versão passada do manuscrito. R815
substitui essas expectativas por contraprovas, sem alterar EN, PT ou S4 e sem
atribuir validação externa à avaliação interna registrada em S4.
"""
import unittest
from pathlib import Path

from scanners.scientific_reasoning_scanner import ScientificReasoningScanner

REPO = Path(__file__).resolve().parent.parent
EN_PATH = REPO / "odonto/Journal_of_Dentistry_Example_OdontoCA.md"
PT_PATH = REPO / "odonto/Journal_of_Dentistry_Example_OdontoCA_PT.md"


class TestR645ScannerValidityOdonto(unittest.TestCase):
    def setUp(self):
        self.scanner = ScientificReasoningScanner()
        self.en = EN_PATH.read_text(encoding="utf-8")
        self.pt = PT_PATH.read_text(encoding="utf-8")
        self.en_res = self.scanner.scan_text(self.en)
        self.pt_res = self.scanner.scan_text(self.pt)

    def test_whole_manuscript_scores_cannot_be_quality_or_bias_verdict(self):
        for result in (self.en_res, self.pt_res):
            self.assertEqual(result["score_kind"], "lexical_heuristic")
            self.assertFalse(result["scientific_quality_assessed"])
            self.assertFalse(result["risk_of_bias_assessed"])
            self.assertIn(result["status"], ("low_rigor", "moderate_rigor", "high_rigor"))

    def test_equivalent_methodology_excerpts_have_same_score(self):
        pt = self.scanner.scan_text("Amostragem aleatória com intervalo de confiança e baseline.")
        en = self.scanner.scan_text("Random sampling with a confidence interval and baseline.")
        self.assertEqual(pt["methodology_score"], 50.0)
        self.assertEqual(pt["methodology_score"], en["methodology_score"])

    def test_equivalent_falsifiability_excerpts_have_same_score(self):
        pt = self.scanner.scan_text("Hipótese falsificável em experimento com métrica.")
        en = self.scanner.scan_text("Falsifiable hypothesis in an experiment with a metric.")
        self.assertAlmostEqual(pt["falsifiability_score"], 66.67)
        self.assertEqual(pt["falsifiability_score"], en["falsifiability_score"])

    def test_actual_control_group_paragraphs_are_not_affirmative_methods(self):
        for text, label in ((self.en, "**Control group.**"), (self.pt, "**Grupo de controle.**")):
            paragraph = next(line for line in text.splitlines() if line.startswith(label))
            result = self.scanner.scan_text(paragraph)
            self.assertNotIn("design", result["matched_concepts"]["methodology"])
            self.assertIn("design", result["negated_concepts"]["methodology"])

    def test_control_or_sampling_recommendation_respects_study_design(self):
        for result in (self.en_res, self.pt_res):
            self.assertNotIn("Inclua detalhes explícitos sobre grupo de controle, amostragem e isolamento de variáveis.", result["recommendations"])

    def test_common_portuguese_words_do_not_get_conditional_credit(self):
        for word in ("sem", "segundo", "sempre", "seis", "sessão", "desejo"):
            self.assertEqual(self.scanner.scan_text(word)["falsifiability_score"], 0.0)
            self.assertFalse(self.scanner.evaluate_hypothesis(word)["is_testable"])

    def test_four_distinct_methods_do_not_saturate_the_dimension(self):
        result = self.scanner.scan_text("Grupo de controle. Amostragem. P-valor. Baseline.")
        self.assertAlmostEqual(result["methodology_score"], 66.67)

    def test_fallacy_triggers_do_not_fire_on_our_manuscript(self):
        for result in (self.en_res, self.pt_res):
            self.assertEqual(result["detected_fallacies"], [])

    def test_internal_probast_s4_remains_separate_from_scanner(self):
        s4 = (REPO / "odonto/Supplementary_File_S4_PROBAST_AI_Assessment.md").read_text(encoding="utf-8")
        self.assertIn("High", s4)
        for result in (self.en_res, self.pt_res):
            self.assertTrue(any("PROBAST" in item for item in result["limitations"]))
            self.assertFalse(result["risk_of_bias_assessed"])


if __name__ == "__main__":
    unittest.main()