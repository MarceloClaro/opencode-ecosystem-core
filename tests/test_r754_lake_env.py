# -*- coding: utf-8 -*-
"""TDD SPEC-935-R754 — lake-env com Mathlib (pula sem projeto demo)."""
import os
import unittest

PROJETO = "/home/marceloclaro/lean-build/lean-mathlib-demo"
TEM_PROJETO = os.path.isfile(os.path.join(PROJETO, "lakefile.toml")) and os.path.isdir(os.path.join(PROJETO, ".lake"))


@unittest.skipUnless(TEM_PROJETO, "projeto demo lake+mathlib ausente")
class TestLakeEnvR754(unittest.TestCase):

    def test_spec_r754_registered(self):
        from sdd.spec_engine import spec_registry
        self.assertIsNotNone(spec_registry.get("SPEC-935-R754"))

    def test_machine_checked_mathlib_no_projeto(self):
        from integrations.deepmind.lean4_verifier import Lean4ProofVerifier
        from integrations.lean_proof_mcp import lean_verify
        code = "import Mathlib.Tactic\n\ntheorem soma_zero (n : Nat) : n + 0 = n := by simp\n"
        r = Lean4ProofVerifier().verify_lean_code(code, project_dir=PROJETO)
        self.assertTrue(r.is_valid)
        self.assertEqual(r.status, "machine_checked")
        m = lean_verify(code, project_dir=PROJETO)
        self.assertTrue(m["is_valid"])
        self.assertEqual(m["status"], "machine_checked")

    def test_sorry_bloqueado_no_projeto(self):
        from integrations.lean_proof_mcp import lean_verify
        r = lean_verify("import Mathlib.Tactic\ntheorem t (x : Nat) : x + 0 = x := by\n  sorry", project_dir=PROJETO)
        self.assertFalse(r["is_valid"])

    def test_prova_errada_falha_no_projeto(self):
        from integrations.deepmind.lean4_verifier import Lean4ProofVerifier
        r = Lean4ProofVerifier().verify_lean_code("theorem t : 2 + 2 = 5 := by decide", project_dir=PROJETO)
        self.assertFalse(r.is_valid)
        self.assertEqual(r.status, "compiler_error")


if __name__ == "__main__":
    unittest.main()
