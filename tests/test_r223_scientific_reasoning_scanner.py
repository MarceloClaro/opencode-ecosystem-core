# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R223: Scientific Reasoning Scanner
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from scanners.scientific_reasoning_scanner import ScientificReasoningScanner


class TestR223ScientificReasoningScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = ScientificReasoningScanner()

    def test_spec_r223_registered(self):
        spec = spec_registry.get("SPEC-935-R223")
        self.assertIsNotNone(spec, "SPEC-935-R223 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_scan_text_high_rigor(self):
        text = (
            "Se aplicarmos o algoritmo MoE, então o tempo de inferência reduz com métrica mensurável. "
            "Realizamos um experimento com grupo de controle e amostragem aleatória, avaliando p-valor < 0.01 "
            "e baseline reprodutibilidade."
        )
        res = self.scanner.scan_text(text)
        self.assertGreaterEqual(res["sri_score"], 70.0)
        self.assertEqual(res["status"], "high_rigor")

    def test_scan_text_fallacy_detection(self):
        text = "A nova abordagem obviamente prova que nosso modelo sempre funciona sem falhas."
        res = self.scanner.scan_text(text)
        self.assertGreater(len(res["detected_fallacies"]), 0)

    def test_evaluate_hypothesis(self):
        hyp = "Se aumentarmos a taxa de aprendizado, então o tempo de convergência reduz."
        res = self.scanner.evaluate_hypothesis(hyp)
        self.assertTrue(res["is_testable"])
        self.assertEqual(res["status"], "valid_hypothesis")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R223")
        if spec:
            spec.add_criterion("Scanner de raciocínio científico validado", lambda out: out.get("scanner") is True)
        res = spec_verifier.verify("SPEC-935-R223", {"scanner": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
