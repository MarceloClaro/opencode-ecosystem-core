# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R231: Atualização da Documentação e Storytelling
"""

import os
import unittest
from sdd.spec_engine import spec_registry, spec_verifier

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestR231DocsAndStorytellingUpdate(unittest.TestCase):

    def test_spec_r231_registered(self):
        spec = spec_registry.get("SPEC-935-R231")
        self.assertIsNotNone(spec, "SPEC-935-R231 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_readme_contains_storytelling(self):
        readme_path = os.path.join(REPO_ROOT, "README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Presentation On Storytelling", content)
        self.assertIn("Act I — A Ilha de Agentes", content)
        self.assertIn("MerkleIntegrityGuard", content)

    def test_architecture_contains_merkle_and_mcp(self):
        arch_path = os.path.join(REPO_ROOT, "ARCHITECTURE.md")
        with open(arch_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("MerkleIntegrityGuard", content)
        self.assertIn("Servidores MCP Interoperáveis", content)

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R231")
        if spec:
            spec.add_criterion("Documentação e Storytelling validados", lambda out: out.get("docs") is True)
        res = spec_verifier.verify("SPEC-935-R231", {"docs": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
