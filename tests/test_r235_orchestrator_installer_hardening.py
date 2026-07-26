# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R235: Hardening da Orquestração e Instalador Windows 1-Click
"""

import os
import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from marceloclaro.orchestrator import MarceloClaroOrchestrator


class TestR235OrchestratorInstallerHardening(unittest.TestCase):

    def setUp(self):
        self.orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)

    def test_spec_r235_registered(self):
        spec = spec_registry.get("SPEC-935-R235")
        self.assertIsNotNone(spec, "SPEC-935-R235 deve estar registrada no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_orchestrator_has_mira_and_research_hub(self):
        # Confirma que MiraPresentationAgent e ResearchHub são acessíveis sem isolamento
        self.assertTrue(hasattr(self.orchestrator, "register_mira_agent"))
        self.assertTrue(hasattr(self.orchestrator, "research"))

    def test_audit_and_certify_includes_cli_and_standalone(self):
        res = self.orchestrator.audit_and_certify("Teste de Hardening R235")
        self.assertIn("cli_ecosystem_bridge", res)
        self.assertIn("standalone_readiness", res)
        self.assertEqual(res["standalone_readiness"]["standalone_score"], 100.0)

    def test_installer_script_exists(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ps_path = os.path.join(repo_root, "installer", "windows", "Install-OpenCodeEcosystem.ps1")
        sh_path = os.path.join(repo_root, "installer", "windows", "provision.sh")
        self.assertTrue(os.path.exists(ps_path), "Install-OpenCodeEcosystem.ps1 deve existir")
        self.assertTrue(os.path.exists(sh_path), "provision.sh deve existir")

    def test_spec_verifier_execution(self):
        spec = spec_registry.get("SPEC-935-R235")
        if spec:
            spec.add_criterion("Hardening de Orquestração validado", lambda out: out.get("audit") is True)
        res = spec_verifier.verify("SPEC-935-R235", {"audit": True})
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "green")


if __name__ == "__main__":
    unittest.main()
