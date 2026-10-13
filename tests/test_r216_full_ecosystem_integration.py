# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R216: Integração Completa do Ecossistema
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from integrations.model_router import _get_colibri, model_router


class TestR216FullEcosystemIntegration(unittest.TestCase):

    def test_spec_r216_registered(self):
        spec = spec_registry.get("SPEC-935-R216")
        self.assertIsNotNone(spec, "SPEC-935-R216 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_colibri_loader_in_model_router(self):
        provider, models = _get_colibri()
        self.assertIsNotNone(provider, "ColibriProvider deve ser carregado com sucesso")
        self.assertIn("olmoe-1b-7b", models)
        self.assertIn("glm-5.2-colibri", models)

    def test_criteria_only_inspection(self):
        spec = spec_registry.get("SPEC-935-R216")
        if spec:
            spec.add_criterion("Integração do ecossistema validada", lambda out: out.get("integrated") is True)
        res = spec_verifier.verify("SPEC-935-R216", {"integrated": True}, require_red_history=False)
        self.assertTrue(res["verified"])
        self.assertEqual(res["verification_scope"], "criteria_only")
        self.assertEqual(res["status"], "criteria_passed")


if __name__ == "__main__":
    unittest.main()
