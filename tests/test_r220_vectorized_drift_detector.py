# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R220: Vectorized Goal Drift Detector
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from trust.vectorized_drift import VectorizedGoalDriftDetector


class TestR220VectorizedDriftDetector(unittest.TestCase):

    def setUp(self):
        self.detector = VectorizedGoalDriftDetector()

    def test_spec_r220_registered(self):
        spec = spec_registry.get("SPEC-935-R220")
        self.assertIsNotNone(spec, "SPEC-935-R220 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_calculate_similarity_identical(self):
        sim = self.detector.calculate_similarity("Refatorar módulo de testes", "Refatorar módulo de testes")
        self.assertGreaterEqual(sim, 0.99)

    def test_calculate_similarity_unrelated(self):
        sim = self.detector.calculate_similarity("Refatorar código em Python", "Culinária italiana receita de massa")
        self.assertLess(sim, 0.15)

    def test_check_drift_detection(self):
        res = self.detector.check_drift(
            goal="Desenvolver algoritmo de otimização de banco de dados",
            context="Astronomia observacional e telescópios ópticos",
            threshold=0.15,
        )
        self.assertTrue(res["drifted"])
        self.assertEqual(res["status"], "drift_detected")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R220")
        if spec:
            spec.add_criterion("Vectorized Drift Detector validado", lambda out: out.get("drift") is True)
        res = spec_verifier.verify("SPEC-935-R220", {"drift": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
