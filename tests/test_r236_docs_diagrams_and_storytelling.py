# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R236: Documentação Visual, Fluxogramas e Storytelling
"""

import os
import unittest
from sdd.spec_engine import spec_registry, spec_verifier


class TestR236DocsDiagramsAndStorytelling(unittest.TestCase):

    def setUp(self):
        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_spec_r236_registered(self):
        spec = spec_registry.get("SPEC-935-R236")
        self.assertIsNotNone(spec, "SPEC-935-R236 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_readme_contains_mermaid_diagrams(self):
        readme_path = os.path.join(self.repo_root, "README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("```mermaid", content)
        self.assertIn("Fluxograma Intuitivo", content)
        self.assertIn("Arquitetura Técnica Multilateral", content)
        self.assertIn("Ciclo de Vida SDD / TDD", content)

    def test_criteria_only_inspection(self):
        spec = spec_registry.get("SPEC-935-R236")
        if spec:
            spec.add_criterion("Fluxogramas e Storytelling validados", lambda out: out.get("docs") is True)
        res = spec_verifier.verify("SPEC-935-R236", {"docs": True}, require_red_history=False)
        self.assertTrue(res["verified"])
        self.assertEqual(res["verification_scope"], "criteria_only")
        self.assertEqual(res["status"], "criteria_passed")


if __name__ == "__main__":
    unittest.main()
