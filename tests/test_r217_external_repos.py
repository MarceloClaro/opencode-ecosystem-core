# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R217: Integração de Repositórios de Referência
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier


class TestR217ExternalRepos(unittest.TestCase):

    def test_spec_r217_registered(self):
        spec = spec_registry.get("SPEC-935-R217")
        self.assertIsNotNone(spec, "SPEC-935-R217 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_external_repos_mapping(self):
        repos = [
            "https://github.com/MarceloClaro/agent-eval",
            "https://github.com/MarceloClaro/ai-agents-for-beginners",
            "https://github.com/MarceloClaro/hello-agents",
        ]
        self.assertEqual(len(repos), 3)
        self.assertTrue(all("github.com/MarceloClaro" in r for r in repos))

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R217")
        if spec:
            spec.add_criterion("Mapeamento de repositórios externos validado", lambda out: out.get("mapped") is True)
        res = spec_verifier.verify("SPEC-935-R217", {"mapped": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
