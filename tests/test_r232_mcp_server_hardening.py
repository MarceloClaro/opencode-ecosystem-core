# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R232: Fortalecimento dos Servidores MCP
"""

import asyncio
import unittest
from unittest.mock import patch
from sdd.spec_engine import spec_registry, spec_verifier
from scanners.scanners_mcp_server import list_tools as list_scanners_tools, call_tool as call_scanners_tool
from colibri.colibri_mcp_server import list_tools as list_colibri_tools, call_tool as call_colibri_tool


class TestR232McpServerHardening(unittest.TestCase):

    def test_spec_r232_registered(self):
        spec = spec_registry.get("SPEC-935-R232")
        self.assertIsNotNone(spec, "SPEC-935-R232 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_async_scanners_mcp_tools(self):
        tools = asyncio.run(list_scanners_tools())
        names = [t.name for t in tools]
        self.assertIn("super_rigor_audit", names)
        self.assertIn("scientific_reasoning_scan", names)
        self.assertIn("merkle_integrity_check", names)

        res = asyncio.run(call_scanners_tool("merkle_integrity_check", {}))
        self.assertFalse(getattr(res, "isError", False))
        self.assertIn("merkle_root", res.content[0].text)

    @patch("colibri.colibri_mcp_server.provider.ensure_server_running")
    def test_async_colibri_mcp_tools(self, mock_running):
        mock_running.return_value = True
        tools = asyncio.run(list_colibri_tools())
        names = [t.name for t in tools]
        self.assertIn("colibri_generate", names)
        self.assertIn("colibri_status", names)

        res = asyncio.run(call_colibri_tool("colibri_status", {}))
        self.assertFalse(res.isError)

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R232")
        if spec:
            spec.add_criterion("Servidores MCP fortalecidos", lambda out: out.get("mcp") is True)
        res = spec_verifier.verify("SPEC-935-R232", {"mcp": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
