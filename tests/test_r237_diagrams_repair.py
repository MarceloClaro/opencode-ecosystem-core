# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R237: Reparo e Validação de Sintaxe dos Diagramas Mermaid
"""

import os
import unittest
from sdd.spec_engine import spec_registry, spec_verifier


class TestR237DiagramsRepair(unittest.TestCase):

    def setUp(self):
        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_spec_r237_registered(self):
        spec = spec_registry.get("SPEC-935-R237")
        self.assertIsNotNone(spec, "SPEC-935-R237 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_readme_mermaid_syntax_blocks(self):
        readme_path = os.path.join(self.repo_root, "README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Garante que cada ```mermaid possui seu fechamento ``` correspondente
        mermaid_opens = content.count("```mermaid")
        self.assertEqual(mermaid_opens, 4, "Devem existir 4 blocos de diagramas Mermaid no README.md")
        self.assertIn("Mapa da Arquitetura Completa (v3.7.0)", content)
        self.assertIn("subgraph Core [Core Subsystems]", content)

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R237")
        if spec:
            spec.add_criterion("Reparo de Diagramas validado", lambda out: out.get("repair") is True)
        res = spec_verifier.verify("SPEC-935-R237", {"repair": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
