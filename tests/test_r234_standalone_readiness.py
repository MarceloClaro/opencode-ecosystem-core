# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R234: Avaliação de Autossuficiência Standalone
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from benchmarks.standalone_readiness_eval import StandaloneReadinessEval


class TestR234StandaloneReadiness(unittest.TestCase):

    def setUp(self):
        self.evaluator = StandaloneReadinessEval()

    def test_spec_r234_registered(self):
        spec = spec_registry.get("SPEC-935-R234")
        self.assertIsNotNone(spec, "SPEC-935-R234 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_eval_standalone_readiness(self):
        res = self.evaluator.eval_standalone_readiness()
        self.assertIn("standalone_score", res)
        self.assertTrue(res["is_fully_autonomous"])
        self.assertFalse(res["external_dependencies_required"])

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R234")
        if spec:
            spec.add_criterion("Autonomia Standalone validada", lambda out: out.get("auto") is True)
        res = spec_verifier.verify("SPEC-935-R234", {"auto": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
