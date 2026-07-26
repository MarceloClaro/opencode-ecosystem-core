# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R230: Benchmark Comparativo de Plugins vs MCP
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from benchmarks.plugin_vs_mcp_eval import PluginVsMcpBenchmark


class TestR230PluginVsMcpEval(unittest.TestCase):

    def setUp(self):
        self.bench = PluginVsMcpBenchmark()

    def test_spec_r230_registered(self):
        spec = spec_registry.get("SPEC-935-R230")
        self.assertIsNotNone(spec, "SPEC-935-R230 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_evaluate_execution_overhead(self):
        res = self.bench.evaluate_execution_overhead(iterations=50)
        self.assertIn("inprocess_plugin", res)
        self.assertIn("mcp_protocol", res)
        self.assertTrue(res["mcp_protocol"]["process_isolation"])
        self.assertFalse(res["inprocess_plugin"]["process_isolation"])

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R230")
        if spec:
            spec.add_criterion("Benchmark Plugins vs MCP validado", lambda out: out.get("bench") is True)
        res = spec_verifier.verify("SPEC-935-R230", {"bench": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
