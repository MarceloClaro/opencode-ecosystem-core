# -*- coding: utf-8 -*-
"""
Testes TDD para SPEC-935-R747 — Núcleo Lean
Verificação total fail-closed, sem overclaim sem compilador.
"""

import hashlib
import json
import os
import re
import unittest
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
AGENTS = [
    "agents/catalog/49_agente_lean_verificacao_total.md",
    "agents/catalog/50_agente_lean_matematica_formal.md",
    "agents/catalog/51_agente_lean_tese_auditavel.md",
    "agents/catalog/52_agente_lean_software_critico.md",
    "agents/catalog/53_agente_lean_estudo_teoremas.md",
]
SKILLS = [
    ".opencode/skills/lean-verificacao-total/SKILL.md",
    ".opencode/skills/lean-tese-provas-auditaveis/SKILL.md",
]
PLUGIN_DIR = "plugins/lean-nucleo-verificacao"


class TestNucleoLeanR747(unittest.TestCase):

    def test_spec_r747_registered(self):
        from sdd.spec_engine import spec_registry
        spec = spec_registry.get("SPEC-935-R747")
        self.assertIsNotNone(spec, "SPEC-935-R747 deve estar registrada no SpecRegistry")

    def test_agentes_lean_existem(self):
        for rel in AGENTS:
            path = os.path.join(REPO, rel)
            self.assertTrue(os.path.isfile(path), f"agente ausente: {rel}")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("name:", content, f"frontmatter ausente em {rel}")
            self.assertTrue(
                ("fail-closed" in content.lower() or "fail_closed" in content.lower() or "bloqueador" in content.lower()),
                f"agente {rel} deve declarar bloqueadores fail-closed",
            )

    def test_skills_lean_existem(self):
        for rel in SKILLS:
            path = os.path.join(REPO, rel)
            self.assertTrue(os.path.isfile(path), f"skill ausente: {rel}")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("sorry", content.lower(), f"skill {rel} deve mencionar sorry")
            self.assertIn("admit", content.lower(), f"skill {rel} deve mencionar admit")

    def test_mcp_lean_verify_failclosed(self):
        from integrations.lean_proof_mcp import lean_verify
        ruim = "import Mathlib.Tactic\ntheorem t (x : Nat) : x + 0 = x := by\n  sorry"
        r1 = lean_verify(ruim)
        self.assertFalse(r1["is_valid"], "sorry deve invalidar")
        self.assertIn(r1["status"], {"incomplete_sorry", "axiom_nao_declarado", "bloqueado_sorry_admit"})
        bom = "import Mathlib.Tactic\ntheorem t (x : Nat) : x + 0 = x := by\n  simp"
        r2 = lean_verify(bom)
        self.assertTrue(r2["is_valid"])
        self.assertIn(r2["status"], {"syntax_verified", "machine_checked"})

    def test_mcp_lean_export_hash(self):
        from integrations.lean_proof_mcp import lean_export
        out = lean_export("soma_zero", "(n : Nat) : n + 0 = n", ["simp"])
        self.assertIn("theorem soma_zero", out["lean_source"])
        self.assertRegex(out["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(out["sha256"], hashlib.sha256(out["lean_source"].encode("utf-8")).hexdigest())

    def test_mcp_lean_autoformalize(self):
        from integrations.lean_proof_mcp import lean_autoformalize
        out = lean_autoformalize("para todo x natural, x + 0 = x", domain="algebra")
        src = out.get("lean_source", "")
        self.assertIn("theorem", src)
        self.assertIn("Mathlib", src)

    def test_plugin_manifesto(self):
        base = os.path.join(REPO, PLUGIN_DIR)
        self.assertTrue(os.path.isfile(os.path.join(base, "PLUGIN.md")))
        manifest_path = os.path.join(base, "lean-nucleo.json")
        self.assertTrue(os.path.isfile(manifest_path))
        with open(manifest_path, encoding="utf-8") as f:
            man = json.load(f)
        self.assertEqual(len(man.get("agentes", [])), 5)
        self.assertEqual(len(man.get("skills", [])), 2)
        self.assertIn("mcp", man)

    def test_sem_overclaim_sem_compilador(self):
        from integrations.lean_proof_mcp import lean_verify
        from integrations.deepmind.lean4_verifier import Lean4ProofVerifier
        v = Lean4ProofVerifier()
        if not v.has_compiler:
            bom = "import Mathlib.Tactic\ntheorem t (x : Nat) : x + 0 = x := by\n  simp"
            r = lean_verify(bom)
            # Sem compilador real, nunca alegar machine_checked como prova total sem ressalva:
            # implementação deve retornar syntax_verified e has_compiler=False na proveniência.
            self.assertNotEqual(r["status"], "machine_checked",
                                "sem compilador não deve alegar machine_checked")
            self.assertFalse(r["provenance"]["has_compiler"])


if __name__ == "__main__":
    unittest.main()
