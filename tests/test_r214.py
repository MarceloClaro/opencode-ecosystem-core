# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R214: ColibriProvider Integration
"""

import unittest
from unittest.mock import patch, MagicMock
from integrations.colibri_provider import ColibriProvider, MODELS, PROVIDER_ID


class TestColibriProvider(unittest.TestCase):

    def setUp(self):
        self.provider = ColibriProvider(host="127.0.0.1", port=8090)

    def test_provider_initialization_and_port(self):
        self.assertEqual(self.provider.port, 8090)
        self.assertEqual(self.provider.base_url, "http://127.0.0.1:8090/v1")

    def test_models_catalog(self):
        self.assertIn("olmoe-1b-7b", MODELS)
        self.assertIn("glm-5.2-colibri", MODELS)
        self.assertEqual(MODELS["olmoe-1b-7b"]["provider"], PROVIDER_ID)

    def test_health_check_structure(self):
        health = self.provider.health_check()
        self.assertEqual(health["provider"], PROVIDER_ID)
        self.assertEqual(health["port"], 8090)
        self.assertIn("supported_models", health)
        self.assertIn("olmoe-1b-7b", health["supported_models"])

    @patch("urllib.request.urlopen")
    def test_is_available_true(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        self.assertTrue(self.provider.is_available())

    @patch("urllib.request.urlopen")
    def test_is_available_false(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")
        self.assertFalse(self.provider.is_available())

    @patch.object(ColibriProvider, "is_available", return_value=False)
    def test_complete_when_unavailable(self, mock_avail):
        result = self.provider.complete("Olá", auto_start=False)
        self.assertFalse(result["success"])
        self.assertIn("inacessível", result["error"])

    @patch.object(ColibriProvider, "is_available", return_value=True)
    @patch("urllib.request.urlopen")
    def test_complete_success(self, mock_urlopen, mock_avail):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json_response = b'{"choices": [{"message": {"content": "Resposta do Colibri"}}]}'
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.provider.complete("Teste de prompt", model="olmoe-1b-7b")
        self.assertTrue(res["success"])
        self.assertEqual(res["content"], "Resposta do Colibri")
        self.assertEqual(res["provider"], PROVIDER_ID)


if __name__ == "__main__":
    unittest.main()
