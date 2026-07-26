# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R221: Self-Correction Engine
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from mci.self_correction import SelfCorrectionEngine


class TestR221SelfCorrectionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SelfCorrectionEngine()

    def test_spec_r221_registered(self):
        spec = spec_registry.get("SPEC-935-R221")
        self.assertIsNotNone(spec, "SPEC-935-R221 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_correction_cycle_success(self):
        spec = spec_registry.get("SPEC-935-R221")
        if spec:
            spec.add_criterion("Validação de autocorreção em circuito fechado", lambda out: out.get("status") == "corrected")

        def mock_fix():
            return True

        result = self.engine.run_correction_cycle(
            spec_id="SPEC-935-R221",
            error_context={"description": "Teste de falha controlada em módulo"},
            fix_fn=mock_fix,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["stage"], "applied")
        self.assertGreater(len(self.engine.get_correction_history()), 0)

    def test_correction_cycle_failed_fix(self):
        def failing_fix():
            return False

        result = self.engine.run_correction_cycle(
            spec_id="SPEC-935-R221",
            error_context={"description": "Teste de falha no fix"},
            fix_fn=failing_fix,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["stage"], "patch")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R221")
        if spec:
            spec.add_criterion("Spec verifier autocorreção ok", lambda out: out.get("status") == "corrected")
        res = spec_verifier.verify("SPEC-935-R221", {"status": "corrected"})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
