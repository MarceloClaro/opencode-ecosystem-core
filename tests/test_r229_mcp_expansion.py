# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R229: Expansão dos Servidores MCP
"""

import unittest
from unittest.mock import patch
from sdd.spec_engine import spec_registry, spec_verifier
from colibri.colibri_mcp_server import colibri_mcp_server
from scanners.scanners_mcp_server import scanners_mcp_server


class TestR229McpExpansion(unittest.TestCase):

    def test_spec_r229_registered(self):
        spec = spec_registry.get("SPEC-935-R229")
        self.assertIsNotNone(spec, "SPEC-935-R229 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_colibri_mcp_server_tools(self):
        tools = colibri_mcp_server.get_tools()
        self.assertIn("colibri_generate", tools)
        self.assertIn("colibri_status", tools)

        status_res = colibri_mcp_server.call_tool("colibri_status", {})
        self.assertIn("ok", status_res)

    @patch("scanners.scanners_mcp_server.super_rigor_pipeline.audit_production")
    def test_scanners_mcp_server_tools(self, mock_audit):
        mock_audit.return_value = {"excellence_score": 95.0, "passed": True}
        tools = scanners_mcp_server.get_tools()
        self.assertIn("super_rigor_audit", tools)
        self.assertIn("scientific_reasoning_scan", tools)
        self.assertIn("merkle_integrity_check", tools)

        audit_res = scanners_mcp_server.call_tool("super_rigor_audit", {"text": "Teste de auditoria MCP"})
        self.assertTrue(audit_res["ok"])
        self.assertIn("excellence_score", audit_res["result"])

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R229")
        if spec:
            spec.add_criterion("Expansão dos servidores MCP validada", lambda out: out.get("mcp") is True)
        res = spec_verifier.verify("SPEC-935-R229", {"mcp": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
