# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R222: ResearchHub Integration
"""

import unittest
from unittest.mock import patch, MagicMock
from sdd.spec_engine import spec_registry, spec_verifier
from research.hub_router_bridge import ResearchHubBridge


class TestR222ResearchHubIntegration(unittest.TestCase):

    def setUp(self):
        self.bridge = ResearchHubBridge()

    def test_spec_r222_registered(self):
        spec = spec_registry.get("SPEC-935-R222")
        self.assertIsNotNone(spec, "SPEC-935-R222 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    @patch("research.hub_router_bridge.ResearchHub")
    def test_execute_and_publish(self, mock_hub_cls):
        mock_hub_instance = MagicMock()
        mock_hub_instance.folder = "/tmp/mock_producao/pesquisa"
        mock_hub_instance.run.return_value = {
            "resumo": {"artigos_selecionados": 3, "pdfs_baixados": 2, "fichamentos": 3, "resenhas": 3}
        }
        mock_hub_cls.return_value = mock_hub_instance

        manifest = self.bridge.execute_and_publish("Inteligência Artificial Quântica", max_papers=3, download=False)
        self.assertIn("bridge_status", manifest)
        self.assertEqual(manifest["bridge_status"], "published_to_blackboard_and_metabus")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R222")
        if spec:
            spec.add_criterion("Ponte de integração do ResearchHub validada", lambda out: out.get("bridge") is True)
        res = spec_verifier.verify("SPEC-935-R222", {"bridge": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
