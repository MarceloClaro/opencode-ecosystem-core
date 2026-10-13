# -*- coding: utf-8 -*-
"""TDD SPEC-935-R755 — Teorema de Eficiência do Roteamento por Atenção."""
import os
import unittest
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
LEAN_FILE = os.path.join(REPO, "plugins/lean-nucleo-verificacao/teoremas/roteamento_atencao.lean")
PROJETO = os.environ.get("CORE_LEAN_PROJECT", str(Path.home() / "lean-build/lean-mathlib-demo"))
TEM_PROJETO = os.path.isfile(os.path.join(PROJETO, "lakefile.toml")) and os.path.isdir(os.path.join(PROJETO, ".lake"))
TEOREMAS = ["softmax_soma_um", "combinacao_convexa_limitada", "roteamento_guloso_otimo", "softmax_invariante_max", "softmax_mem_Ioo", "combinacao_convexa_limitada_baixo", "softmax_peso_total_singleton", "peso_cresce_com_escore", "topk_dominam_resto", "temperatura_aguca_maximo", "sem_overflow_apos_max"]


class TestTeoremaRoteamentoR755(unittest.TestCase):

    def test_spec_r755_registered(self):
        from sdd.spec_engine import spec_registry
        self.assertIsNotNone(spec_registry.get("SPEC-935-R755"))

    def test_arquivo_lean_existe_sem_sorry(self):
        self.assertTrue(os.path.isfile(LEAN_FILE), f"teorema ausente: {LEAN_FILE}")
        with open(LEAN_FILE, encoding="utf-8") as f:
            src = f.read()
        for nome in TEOREMAS:
            self.assertIn(nome, src, f"teorema {nome} ausente no .lean")
        baixo = src.lower()
        self.assertNotIn("sorry", baixo, "sorry bloqueado")
        self.assertNotIn("admit", baixo, "admit bloqueado")

    @unittest.skipUnless(TEM_PROJETO, "projeto demo lake+mathlib ausente")
    def test_machine_checked_no_projeto(self):
        from integrations.lean_proof_mcp import lean_verify
        with open(LEAN_FILE, encoding="utf-8") as f:
            src = f.read()
        r = lean_verify(src, project_dir=PROJETO)
        self.assertTrue(r["is_valid"], f"erros: {r.get('errors')}")
        self.assertEqual(r["status"], "machine_checked")

    def test_axiomas_auditaveis(self):
        audit = os.path.join(REPO, "plugins/lean-nucleo-verificacao/bancada/axiomas.txt")
        self.assertTrue(os.path.isfile(audit), f"auditoria ausente: {audit}")
        with open(audit, encoding="utf-8") as f:
            txt = f.read()
        for nome in TEOREMAS:
            self.assertIn(nome, txt, f"axiomas de {nome} ausentes")
        self.assertNotIn("sorryAx", txt, "sorryAx inadmissível")


if __name__ == "__main__":
    unittest.main()
