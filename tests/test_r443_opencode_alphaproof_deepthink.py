# -*- coding: utf-8 -*-
"""
Testes Unitários e de Integração para a SPEC-935-R443
======================================================
Validação TDD dos motores nativos:
- OpenCode AlphaProof (Proof-Tree Search & Formal Tactics)
- OpenCode Deep Think (Test-Time Compute & Trajectory Search)
- Erdős & Hirzebruch Open Problems Solver
- Integração MarceloClaroOrchestrator e Doctor Check 16
"""

import unittest
from sdd.spec_engine import spec_registry
from integrations.deepmind import (
    OpenCodeAlphaProof,
    OpenCodeDeepThink,
    ErdosSeriesAnalyzer,
    HirzebruchEigenweightCalculator,
    OpenProblemsResearchWorkflow,
    FormalProofVerifier,
)
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from marceloclaro.doctor import _check_opencode_deepthink_alphaproof, run_doctor


class TestOpenCodeAlphaProofDeepThinkR443(unittest.TestCase):

    def setUp(self):
        self.verifier = FormalProofVerifier()
        self.alphaproof = OpenCodeAlphaProof(verifier=self.verifier)
        self.deep_think = OpenCodeDeepThink(verifier=self.verifier, alphaproof=self.alphaproof)
        self.erdos = ErdosSeriesAnalyzer()
        self.hirz = HirzebruchEigenweightCalculator()
        self.workflow = OpenProblemsResearchWorkflow()
        self.orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)

    def test_spec_r443_registered(self):
        """Valida que SPEC-935-R443 está carregada no registro formal SDD."""
        spec = spec_registry.get("SPEC-935-R443")
        self.assertIsNotNone(spec, "SPEC-935-R443 deve estar registrada no SpecRegistry")

    def test_alphaproof_algebraic_proof_tree_search(self):
        """Valida a busca em árvore para identidades algébricas."""
        goal = "(a + b)*(a - b) = a**2 - b**2"
        res = self.alphaproof.search_proof(goal, max_depth=3)
        self.assertTrue(res["is_proven"])
        self.assertEqual(res["confidence_score"], 1.0)
        self.assertIn("AlgebraicSimplify", res["tactics_applied"])
        self.assertIn("\\item", res["latex_proof_block"])

    def test_alphaproof_inductive_tactic(self):
        """Valida a aplicação da tática de indução matemática na árvore."""
        goal = "A soma dos primeiros n cubos e igual a (n*(n+1)/2)^2"
        res = self.alphaproof.search_proof(goal, max_depth=3)
        self.assertTrue(res["is_proven"])
        self.assertGreaterEqual(res["confidence_score"], 0.90)
        self.assertIn("MathematicalInduction", res["tactics_applied"])

    def test_alphaproof_contradiction_tactic(self):
        """Valida a aplicação de redução ao absurdo."""
        goal = "Nao existem inteiros positivos x, y tais que 4*x**2 - y**2 = 1"
        res = self.alphaproof.search_proof(goal, max_depth=2)
        self.assertTrue(res["is_proven"])
        self.assertIn("ReductioAdAbsurdum", res["tactics_applied"])

    def test_deep_think_trajectory_expansion(self):
        """Valida a expansão concorrente de trajetórias de raciocínio profundo com compute budget."""
        prob = "Demonstrar a estabilidade assintótica do atrator de Lorentz em variedades Riemannianas compactas."
        res = self.deep_think.think(prob, domain="physics", compute_budget=3)

        self.assertEqual(res["compute_budget"], 3)
        self.assertEqual(res["total_trajectories_evaluated"], 3)
        self.assertGreaterEqual(res["best_grade_0_to_7"], 5)
        self.assertIn("<think>", res["final_solution"])
        self.assertIn("[Deep Think Decision]", res["final_solution"])

    def test_erdos_series_irrationality(self):
        """Valida a demonstração de irracionalidade da série rápida de Erdős (generalização Erdős-1051)."""
        res = self.erdos.analyze_rapid_series(base_c=1)
        self.assertTrue(res.is_irrational)
        self.assertEqual(res.conjecture_id, "Erdos-1051-c1")
        self.assertGreaterEqual(len(res.proof_steps), 4)
        self.assertIn("\\documentclass{article}", res.latex_document)
        self.assertIn("Erdos", res.latex_document)
        self.assertGreaterEqual(res.confidence_score, 0.95)

    def test_hirzebruch_eigenweight_computation(self):
        """Valida a computação de autopesos de Hirzebruch (Feng-Yun-Zhang)."""
        res = self.hirz.compute_eigenweights(dim=4, rank=2)
        self.assertEqual(res.variety_dim, 4)
        self.assertEqual(len(res.eigenweights), 4)
        self.assertTrue(res.is_arithmetic_valid)
        self.assertIn("\\begin{table}", res.latex_table)
        self.assertIn("Feng--Yun--Zhang", res.latex_table)
        self.assertGreater(res.proportionality_constant, 0.0)

    def test_open_problems_workflow(self):
        """Valida o workflow completo para problemas abertos (Erdős e Hirzebruch)."""
        erdos_work = self.workflow.solve_conjecture("erdos", params={"c": 2})
        self.assertEqual(erdos_work["status"], "proven_irrational")
        self.assertEqual(erdos_work["confidence"], 0.99)

        hirz_work = self.workflow.solve_conjecture("hirzebruch", params={"dim": 3, "rank": 1})
        self.assertEqual(hirz_work["status"], "eigenweights_computed")
        self.assertEqual(hirz_work["confidence"], 0.98)

    def test_orchestrator_deepthink_alphaproof_integration(self):
        """Valida os métodos nativos integrados ao MarceloClaroOrchestrator."""
        dt_res = self.orchestrator.deep_think("Convergência do Fluxo de Ricci", domain="geometry", compute_budget=2)
        self.assertIn("best_trajectory", dt_res)

        ap_res = self.orchestrator.alphaproof_search("exp(x) > 0 para todo x real")
        self.assertTrue(ap_res["is_proven"])

        conj_res = self.orchestrator.solve_open_conjecture("erdos", params={"c": 1})
        self.assertEqual(conj_res["status"], "proven_irrational")

    def test_doctor_check_16_deepthink_alphaproof(self):
        """Valida que o 16º check do doctor passa e reporta integridade."""
        check = _check_opencode_deepthink_alphaproof()
        self.assertEqual(check.status, "pass")
        self.assertIn("OpenCode AlphaProof & Deep Think ativos", check.detail)

        doc_report = run_doctor()
        self.assertGreaterEqual(doc_report["checks_total"], 16)
        self.assertEqual(doc_report["checks_failed"], 0)


if __name__ == "__main__":
    unittest.main()
