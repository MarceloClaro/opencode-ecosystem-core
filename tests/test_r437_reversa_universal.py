# -*- coding: utf-8 -*-
"""
Testes SPEC-935-R437 — Reversa Universal em artigos, repos, códigos e scanners de gaps
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, ".")

from sdd.spec_engine import spec_registry


class TestR437Spec(unittest.TestCase):
    def test_spec_r437_green(self):
        spec = spec_registry.get("SPEC-935-R437")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.status, "green")


class TestEngineInventory(unittest.TestCase):
    def test_inventory_rag(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        inv = eng.inventory("rag")
        self.assertGreater(inv["total_files"], 0)
        self.assertIn("python", inv["languages"])
        self.assertGreaterEqual(inv["metrics"]["total_files"], 1)

    def test_modules_rag_scientific(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        mods = eng.modules("rag")
        # rag deve ter módulo 'rag' com ScientificRAG
        names = [m["name"] for m in mods]
        self.assertTrue(any("rag" in n.lower() or n == "." for n in names))
        # Verifica que scientific.py foi detectado com classe ScientificRAG
        all_classes = sum([m["classes"] for m in mods], [])
        self.assertIn("ScientificRAG", all_classes)

    def test_dependencies_root(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        deps = eng.dependencies(".")
        # Repo tem requirements ou pyproject ou package.json
        self.assertIsInstance(deps["all"], list)
        # Se houver deps, devem ter name
        if deps["count"] > 0:
            self.assertIn("name", deps["all"][0])

    def test_gaps_synthetic_fixture(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Cria fixture com TODO, sem README, sem tests, com secret
            (tmp_path / "app.py").write_text("import os\n# TODO: fix this\npassword = \"123456\"\n" + "x=1\n"*600, encoding="utf-8")
            (tmp_path / "utils.py").write_text("def foo():\n    pass\n", encoding="utf-8")
            (tmp_path / "requirements.txt").write_text("flask\nrequests==2.28.0\n", encoding="utf-8")
            gaps_data = eng.gaps(tmp_path)
            gap_types = [g["type"] for g in gaps_data["gaps"]]
            self.assertIn("todo_fixme", gap_types)
            self.assertIn("hardcoded_secret", gap_types)
            self.assertIn("missing_docs", gap_types)
            self.assertIn("stale_deps", gap_types)

    def test_analyze_with_output_root(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            res = eng.analyze("rag", output_root=str(out))
            self.assertIn("inventory", res)
            self.assertIn("modules", res)
            self.assertIn("dependencies", res)
            self.assertIn("gaps", res)
            self.assertIn("recommendations", res)
            self.assertTrue((out / "inventory.md").exists())
            self.assertTrue((out / "gaps.md").exists())
            self.assertGreater(len(res["files_written"]), 0)

    def test_analyze_nonexistent_path(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        res = eng.analyze("/tmp/nonexistent_path_xyz_12345")
        self.assertIn("error", res)

    def test_enhance_reasoning_research_manuscript(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        analysis = eng.analyze("rag")
        # enhance_reasoning
        ctx = {"query": "causal inference"}
        enriched = eng.enhance_reasoning(ctx, analysis)
        self.assertIn("reversa_modules", enriched)
        # enhance_research
        q2 = eng.enhance_research("causal inference", analysis)
        self.assertIsInstance(q2, str)
        self.assertTrue(q2.startswith("causal"))
        # enhance_manuscript
        sections = {"introdução": "texto", "métodos": "texto"}
        res = eng.enhance_manuscript(sections, analysis)
        self.assertIn("suggestions", res)


class TestBridge(unittest.TestCase):
    def test_analyze_and_reflect(self):
        from reversa_universal.bridge import ReversaBridge
        from mci.metabus import metabus
        bridge = ReversaBridge()
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "mod.py").write_text("class Foo:\n    def bar(self): pass\n", encoding="utf-8")
            res = bridge.analyze_and_reflect(tmp)
            self.assertIn("modules", res)
            # Verifica tópico semântico
            slug = Path(tmp).name.lower()
            # Procura tópico que começa com reversa_universal.
            topics = [k for k in metabus.memory.semantic.keys() if k.startswith("reversa_universal.")]
            self.assertTrue(any(slug in t or "tmp" in t for t in topics) or len(topics) > 0)

    def test_enhance_gaps(self):
        from reversa_universal.bridge import ReversaBridge
        bridge = ReversaBridge()
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "app.py").write_text("# TODO: fix\n", encoding="utf-8")
            analysis = bridge.engine.analyze(tmp)
            report = {"evolutionary": {"total_gaps": 2, "recommendation": "test"}, "domain": "test"}
            enhanced = bridge.enhance_gaps(report, analysis=analysis)
            self.assertIn("reversa_gaps", enhanced["evolutionary"])
            self.assertIn("reversa", enhanced)
            self.assertGreater(enhanced["evolutionary"]["total_gaps"], 2)

    def test_bridge_status(self):
        from reversa_universal.bridge import ReversaBridge
        bridge = ReversaBridge()
        s = bridge.status()
        self.assertIn("engine_available", s)


class TestReversaScannerPath(unittest.TestCase):
    def test_scanner_with_path_delegates(self):
        from scanners.reversa_scanner import reversa_scanner
        # Usa path real com código
        result = reversa_scanner.scan("rag/scientific.py")
        self.assertGreaterEqual(result.score, 5.0)
        self.assertTrue(any("Reversa Universal" in f or "Código" in f for f in result.findings))

    def test_scanner_textual_still_works(self):
        from scanners.reversa_scanner import reversa_scanner
        result = reversa_scanner.scan("def foo():\n    pass\n# TODO: fix\n")
        self.assertGreaterEqual(result.score, 5.0)


class TestDiagnosticPipelineReversa(unittest.TestCase):
    def test_pipeline_with_path_domain_reversa(self):
        from scanners.pipeline import diagnostic_pipeline
        report = diagnostic_pipeline.run(corpus="rag", domain="reversa")
        self.assertIn("reversa", report)
        self.assertIn("score", report["reversa"])


class TestOrchestratorReversa(unittest.TestCase):
    def test_orchestrator_methods_exist(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        for m in ("reversa_analyze", "reversa_on_article", "reversa_on_repo", "reversa_on_scripts", "reversa_enhance_gaps", "reversa_status", "reversa_bridge"):
            self.assertTrue(hasattr(orch, m), f"faltando {m}")

    def test_reversa_analyze_via_orchestrator(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        res = orch.reversa_analyze("rag")
        self.assertIn("modules", res)
        self.assertIn("inventory", res)

    def test_reversa_on_scripts(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        res = orch.reversa_on_scripts("rag/*.py", base_dir=".")
        self.assertIn("matched_files", res)

    def test_reversa_enhance_gaps_via_orchestrator(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        report = {"evolutionary": {"total_gaps": 1, "recommendation": "x"}, "domain": "test"}
        enhanced = orch.reversa_enhance_gaps(report, path="rag")
        self.assertIn("reversa", enhanced)
        self.assertIn("reversa_gaps", enhanced["evolutionary"])

    def test_reversa_status(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        s = orch.reversa_status()
        self.assertIsInstance(s, dict)


if __name__ == "__main__":
    unittest.main()
