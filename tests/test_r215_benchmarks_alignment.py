# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R215: Alinhamento com Benchmarks SOTA
"""

import unittest
from mci.metacognitive_evaluator import classify_metacognitive_tier
from sdd.spec_engine import spec_registry, spec_verifier


class TestR215BenchmarksAlignment(unittest.TestCase):

    def test_spec_r215_registered(self):
        spec = spec_registry.get("SPEC-935-R215")
        self.assertIsNotNone(spec, "SPEC-935-R215 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_anti_overclaim_tier_policy(self):
        # Sem validação externa, readiness 95 não pode virar superhuman_verified
        tier = classify_metacognitive_tier(95.0, external_validation=False)
        self.assertEqual(tier, "metacognitive_superhuman_candidate")

        # Com validação externa, readiness 95 vira superhuman_verified
        tier_v = classify_metacognitive_tier(95.0, external_validation=True)
        self.assertEqual(tier_v, "metacognitive_superhuman_verified")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R215")
        if spec:
            spec.add_criterion("Alinhamento SOTA ativo", lambda out: out.get("aligned") is True)
        res = spec_verifier.verify("SPEC-935-R215", {"aligned": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
