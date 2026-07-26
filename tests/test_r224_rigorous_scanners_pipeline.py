# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R224: SuperRigorPipeline
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from scanners.pipeline import super_rigor_pipeline, SuperRigorPipeline


class TestR224RigorousScannersPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = super_rigor_pipeline

    def test_spec_r224_registered(self):
        spec = spec_registry.get("SPEC-935-R224")
        self.assertIsNotNone(spec, "SPEC-935-R224 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_audit_production_high_rigor(self):
        text = (
            "Desenvolvimento de modelo de IA com hipóteses testáveis e falsificabilidade popperiana. "
            "Experimento realizado com grupo de controle, amostragem aleatória, cálculo de p-valor "
            "e baseline reprodutibilidade."
        )
        res = self.pipeline.audit_production(text)
        self.assertIn("excellence_score", res)
        self.assertIn("scientific_rigor", res)
        self.assertGreaterEqual(res["excellence_score"], 0.0)

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R224")
        if spec:
            spec.add_criterion("SuperRigorPipeline validado", lambda out: out.get("pipeline") is True)
        res = spec_verifier.verify("SPEC-935-R224", {"pipeline": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
