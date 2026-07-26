# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R219: Agent Evaluation Harness
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from benchmarks.agent_eval_harness import AgentEvalHarness


class TestR219AgentEvalHarness(unittest.TestCase):

    def setUp(self):
        self.harness = AgentEvalHarness()

    def test_spec_r219_registered(self):
        spec = spec_registry.get("SPEC-935-R219")
        self.assertIsNotNone(spec, "SPEC-935-R219 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_tsr_and_tool_accuracy_calculation(self):
        self.harness.record_run("T1", "agent-code", success=True, tool_calls_count=2, tool_calls_correct=2, duration_seconds=0.5)
        self.harness.record_run("T2", "agent-code", success=True, tool_calls_count=2, tool_calls_correct=1, duration_seconds=1.2)
        self.harness.record_run("T3", "agent-code", success=False, tool_calls_count=1, tool_calls_correct=0, duration_seconds=2.0)

        tsr = self.harness.calculate_tsr("agent-code")
        self.assertEqual(tsr, 66.67)

        acc = self.harness.calculate_tool_accuracy("agent-code")
        self.assertEqual(acc, 60.0)

    def test_percentiles_calculation(self):
        for i in range(10):
            self.harness.record_run(f"T{i}", "agent-test", success=True, duration_seconds=float(i + 1))

        pcts = self.harness.calculate_percentiles("agent-test")
        self.assertIn("p50", pcts)
        self.assertIn("p90", pcts)
        self.assertIn("p99", pcts)
        self.assertGreater(pcts["p90"], pcts["p50"])

    def test_benchmark_report_generation(self):
        self.harness.record_run("T1", "marceloclaro", success=True, duration_seconds=0.3)
        report = self.harness.generate_benchmark_report()
        self.assertEqual(report["total_runs"], 1)
        self.assertEqual(report["overall_tsr"], 100.0)
        self.assertIn("marceloclaro", report["by_agent"])

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R219")
        if spec:
            spec.add_criterion("Agent Eval Harness validado", lambda out: out.get("harness") is True)
        res = spec_verifier.verify("SPEC-935-R219", {"harness": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
