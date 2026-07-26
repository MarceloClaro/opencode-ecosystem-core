# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R225: External Validation Harness
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from benchmarks.external_validation_harness import ExternalValidationHarness


class TestR225ExternalValidationHarness(unittest.TestCase):

    def setUp(self):
        self.harness = ExternalValidationHarness()

    def test_spec_r225_registered(self):
        spec = spec_registry.get("SPEC-935-R225")
        self.assertIsNotNone(spec, "SPEC-935-R225 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_register_validation_proof_valid(self):
        res = self.harness.register_validation_proof(
            evaluator_id="external_auditor_01",
            benchmark_name="GAIA_Benchmark_Suite",
            score=94.5,
            signature="SIG_AUDIT_2026_OK",
        )
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["tier"], "metacognitive_superhuman_verified")
        self.assertGreater(len(self.harness.get_verified_proofs()), 0)

    def test_register_validation_proof_invalid_score(self):
        res = self.harness.register_validation_proof(
            evaluator_id="external_auditor_02",
            benchmark_name="SWE_Bench",
            score=82.0,
            signature="SIG_AUDIT_LOW",
        )
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["tier"], "research_grade")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R225")
        if spec:
            spec.add_criterion("External Validation Harness validado", lambda out: out.get("proof") is True)
        res = spec_verifier.verify("SPEC-935-R225", {"proof": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
