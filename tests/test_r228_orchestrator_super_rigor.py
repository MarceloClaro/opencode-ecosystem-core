# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R228: Orchestrator Super-Rigor Certification
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from marceloclaro.orchestrator import MarceloClaroOrchestrator


class TestR228OrchestratorSuperRigor(unittest.TestCase):

    def setUp(self):
        self.orchestrator = MarceloClaroOrchestrator()

    def test_spec_r228_registered(self):
        spec = spec_registry.get("SPEC-935-R228")
        self.assertIsNotNone(spec, "SPEC-935-R228 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_audit_and_certify(self):
        text = (
            "Desenvolvimento de modelo de IA com hipóteses falsificáveis popperianas, grupo de controle, "
            "amostragem aleatória e baseline reprodutibilidade."
        )
        res = self.orchestrator.audit_and_certify(text)
        self.assertEqual(res["orchestrator_id"], "marceloclaro")
        self.assertIn("excellence_score", res)
        self.assertIn("certificate", res)
        self.assertIn("merkle_root", res)
        self.assertIn(res["status"], ["certified_by_marceloclaro", "refinement_requested"])

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R228")
        if spec:
            spec.add_criterion("Aprimoramento do orquestrador validado", lambda out: out.get("orch") is True)
        res = spec_verifier.verify("SPEC-935-R228", {"orch": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
