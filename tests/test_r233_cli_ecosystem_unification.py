# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R233: Unificação Multilateral de CLIs
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from integrations.cli_ecosystem_bridge import CliEcosystemBridge


class TestR233CliEcosystemUnification(unittest.TestCase):

    def setUp(self):
        self.bridge = CliEcosystemBridge()

    def test_spec_r233_registered(self):
        spec = spec_registry.get("SPEC-935-R233")
        self.assertIsNotNone(spec, "SPEC-935-R233 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_discover_cli_capabilities(self):
        caps = self.bridge.discover_cli_capabilities()
        self.assertIn("opencode_codex", caps)
        self.assertIn("claude_code", caps)
        self.assertIn("antigravity_cli", caps)
        self.assertTrue(caps["opencode_codex"]["active"])

    def test_export_agent_cards_to_claude(self):
        res = self.bridge.export_agent_cards_to_claude()
        self.assertEqual(res["status"], "synced_with_claude_code")
        self.assertGreater(res["total_exported"], 0)

    def test_export_skills_to_antigravity(self):
        res = self.bridge.export_skills_to_antigravity()
        self.assertEqual(res["status"], "synced_with_antigravity_cli")
        self.assertIn("supported_sidecars", res)

    def test_get_unified_status(self):
        res = self.bridge.get_unified_status()
        self.assertEqual(res["unified_status"], "fully_synchronized")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R233")
        if spec:
            spec.add_criterion("Ponte Multilateral de CLIs validada", lambda out: out.get("bridge") is True)
        res = spec_verifier.verify("SPEC-935-R233", {"bridge": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
