# -*- coding: utf-8 -*-
"""
Testes Unitários e de Integração para a SPEC-935-R444
======================================================
Validação TDD dos motores:
- Lean4ProofVerifier (Formatação, Análise Sintática, Detecção de Sorry e Kernel)
- EGraph & EqualitySaturationEngine (Egglog Paradigm, Congruence Closure)
- Integração MarceloClaroOrchestrator e Doctor Check 17
"""

import unittest
from sdd.spec_engine import spec_registry
from integrations.deepmind import (
    Lean4ProofVerifier,
    Lean4VerificationResult,
    EGraph,
    ENode,
    EqualitySaturationEngine,
)
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from marceloclaro.doctor import _check_lean4_egraph_engine, run_doctor


class TestLean4EGraphSaturationR444(unittest.TestCase):

    def setUp(self):
        self.lean_verifier = Lean4ProofVerifier()
        self.egraph_engine = EqualitySaturationEngine()
        self.orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)

    def test_spec_r444_registered(self):
        """Valida que SPEC-935-R444 está registrada no registro formal SDD."""
        spec = spec_registry.get("SPEC-935-R444")
        self.assertIsNotNone(spec, "SPEC-935-R444 deve estar registrada no SpecRegistry")

    def test_lean4_format_theorem(self):
        """Valida a formatação de código formal em Lean 4."""
        code = self.lean_verifier.format_theorem(
            theorem_name="add_comm_reals",
            statement="forall (a b : Real), a + b = b + a",
            proof_tactics=["intro a b", "ring"],
            parameters="(a b : Real)",
        )
        self.assertIn("theorem add_comm_reals", code)
        self.assertIn("import Mathlib.Tactic", code)
        self.assertIn(":= by", code)
        self.assertIn("ring", code)

    def test_lean4_verify_valid_code(self):
        """Valida código sintaticamente correto em Lean 4."""
        code = """
import Mathlib.Tactic

theorem pythagorean_id (x : Real) : x^2 + 0 = x^2 := by
  ring
"""
        res = self.lean_verifier.verify_lean_code(code)
        self.assertTrue(res.is_valid)
        self.assertIn(res.status, {"machine_checked", "syntax_verified"})
        self.assertIn("ring", res.tactics_used)
        self.assertFalse(res.has_sorry)

    def test_lean4_detect_sorry(self):
        """Valida a detecção rigorosa de passos em aberto com 'sorry'."""
        code = """
theorem unproven_claim (n : Nat) : n > 0 := by
  sorry
"""
        res = self.lean_verifier.verify_lean_code(code)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "incomplete_sorry")
        self.assertTrue(res.has_sorry)
        self.assertGreater(len(res.errors), 0)

    def test_lean4_syntax_delimiter_error(self):
        """Valida a rejeição de scripts com parênteses ou delimitadores desbalanceados."""
        bad_code = "theorem bad_delims (x : Real : x + (1 = 2 := by ring"
        res = self.lean_verifier.verify_lean_code(bad_code)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "syntax_error")

    def test_egraph_add_and_union(self):
        """Valida inserção básica e união no grafo de equivalência."""
        egraph = EGraph()
        n1 = egraph.add(ENode("x"))
        n2 = egraph.add(ENode("y"))
        self.assertNotEqual(egraph.find(n1), egraph.find(n2))

        egraph.union(n1, n2)
        self.assertEqual(egraph.find(n1), egraph.find(n2))

    def test_egraph_congruence_closure(self):
        """Valida o fechamento por congruência: se a=b, então f(a)=f(b)."""
        egraph = EGraph()
        a = egraph.add(ENode("a"))
        b = egraph.add(ENode("b"))
        fa = egraph.add(ENode("f", (a,)))
        fb = egraph.add(ENode("f", (b,)))

        self.assertNotEqual(egraph.find(fa), egraph.find(fb))

        egraph.union(a, b)
        egraph.rebuild()

        self.assertEqual(egraph.find(fa), egraph.find(fb))

    def test_egraph_equality_saturation_simplification(self):
        """Valida simplificação de (+ (* x 1) 0) para x via saturação de igualdade."""
        expr = "(+ (* x 1) 0)"
        res = self.egraph_engine.saturate(expr, max_iterations=3)

        self.assertTrue(res["is_saturated"])
        self.assertEqual(res["simplified_expr"], "x")
        self.assertGreaterEqual(res["rules_applied"], 2)

    def test_egraph_sub_self_simplification(self):
        """Valida a regra (- x x) -> 0."""
        expr = "(- x x)"
        res = self.egraph_engine.saturate(expr, max_iterations=2)
        self.assertEqual(res["simplified_expr"], "0")

    def test_orchestrator_lean4_and_egraph_integration(self):
        """Valida métodos integrados no MarceloClaroOrchestrator."""
        code = self.orchestrator.lean4_format_theorem("lin_id", "x + y = y + x", ["intro x y", "linarith"])
        self.assertIn("theorem lin_id", code)

        v_res = self.orchestrator.lean4_verify_code(code)
        self.assertTrue(v_res["is_valid"])

        sat_res = self.orchestrator.egraph_saturate_term("(+ y 0)")
        self.assertEqual(sat_res["simplified_expr"], "y")

    def test_doctor_check_17_lean4_egraph(self):
        """Valida que o 17º check do doctor passa e reporta 17 checks totais."""
        check = _check_lean4_egraph_engine()
        self.assertEqual(check.status, "pass")
        self.assertIn("Lean 4 & E-Graph ativos", check.detail)

        doc_report = run_doctor()
        self.assertGreaterEqual(doc_report["checks_total"], 17)
        self.assertEqual(doc_report["checks_failed"], 0)


if __name__ == "__main__":
    unittest.main()
