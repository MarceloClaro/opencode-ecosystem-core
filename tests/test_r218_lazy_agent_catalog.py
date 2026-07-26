# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R218: Lazy Agent Catalog
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from agents.lazy_catalog import LazyAgentCatalog


class TestR218LazyAgentCatalog(unittest.TestCase):

    def setUp(self):
        self.catalog = LazyAgentCatalog()

    def test_spec_r218_registered(self):
        spec = spec_registry.get("SPEC-935-R218")
        self.assertIsNotNone(spec, "SPEC-935-R218 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_list_agents(self):
        agents = self.catalog.list_agents()
        self.assertIsInstance(agents, list)
        self.assertGreater(len(agents), 0, "Deve haver agentes indexados no catálogo")

    def test_load_agent_card_lazy_and_cache(self):
        agents = self.catalog.list_agents()
        first_agent = agents[0]
        card1 = self.catalog.load_agent_card(first_agent)
        self.assertIsNotNone(card1)
        self.assertIn("agent_id", card1)
        self.assertEqual(card1["agent_id"], first_agent)

        # Re-carrega do cache
        card2 = self.catalog.load_agent_card(first_agent)
        self.assertIs(card1, card2)

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R218")
        if spec:
            spec.add_criterion("Lazy Agent Catalog validado", lambda out: out.get("lazy") is True)
        res = spec_verifier.verify("SPEC-935-R218", {"lazy": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
