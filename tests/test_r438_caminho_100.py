# -*- coding: utf-8 -*-
"""
Testes SPEC-935-R438 — Caminho para 100 (5 gaps residuais)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, ".")

from sdd.spec_engine import spec_registry


class TestR438Spec(unittest.TestCase):
    def test_spec_r438_green(self):
        spec = spec_registry.get("SPEC-935-R438")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.status, "green")


class TestG1LoopSpecs(unittest.TestCase):
    def test_loop_specs_files_exist(self):
        for name in ("dsh-reasoning-97", "harness-reasoning-97"):
            path = Path(f"specs/loops/{name}.md")
            self.assertTrue(path.exists(), f"{path} deve existir")
            content = path.read_text(encoding="utf-8")
            self.assertIn(name, content)

    def test_doctor_loop_specs_pass(self):
        from marceloclaro.doctor import run_doctor
        report = run_doctor()
        # Encontra check loop_specs
        loops_check = next((c for c in report["checks"] if c["name"] == "loop_specs"), None)
        self.assertIsNotNone(loops_check)
        self.assertEqual(loops_check["status"], "pass", f"doctor loop_specs deve passar, got {loops_check}")


class TestG2WebSearcher(unittest.TestCase):
    def test_unified_searcher_has_web_default(self):
        from rag.enhanced_search_rag import UnifiedSearcher, AntigravityWebSearcher
        us = UnifiedSearcher(searchers=[])
        # web_searcher padrão deve ser AntigravityWebSearcher (mesmo quando CLI ausente, retorna [] mas não None)
        self.assertIsNotNone(us.web_searcher)
        self.assertTrue(hasattr(us.web_searcher, "search"))

    def test_search_with_web_provider_calls_web(self):
        from rag.enhanced_search_rag import UnifiedSearcher

        class FakeWeb:
            def __init__(self):
                self.called = False
            def search(self, query, limit=5):
                self.called = True
                return [{"title": "Web Result", "year": 2026, "doi": "10.9/web"}]

        fake_web = FakeWeb()
        us = UnifiedSearcher(searchers=[], web_searcher=fake_web)
        # Sem provider=web, não deve chamar web
        res_no_web = us.search("test query", limit=5)
        self.assertFalse(fake_web.called)
        self.assertEqual(len(res_no_web), 0)
        # Com provider=web, deve chamar
        fake_web.called = False
        res_web = us.search("test query", limit=5, providers=["web"])
        self.assertTrue(fake_web.called)
        self.assertEqual(len(res_web), 1)
        self.assertEqual(res_web[0]["title"], "Web Result")
        # Com http no query, também deve chamar mesmo sem providers
        fake_web.called = False
        us2 = UnifiedSearcher(searchers=[], web_searcher=fake_web)
        res_http = us2.search("https://example.com/paper", limit=5)
        self.assertTrue(fake_web.called)

    def test_antigravity_wrapper_available(self):
        from rag.enhanced_search_rag import AntigravityWebSearcher
        ws = AntigravityWebSearcher()
        self.assertTrue(hasattr(ws, "search"))
        self.assertTrue(hasattr(ws, "available"))
        # Quando CLI ausente, search retorna [] sem erro
        res = ws.search("test", limit=2)
        self.assertIsInstance(res, list)


class TestG3TomliFallback(unittest.TestCase):
    def test_tomli_fallback_when_tomllib_fails(self):
        # Simula falha de import tomllib e verifica que tomli é tentado
        import reversa_universal.engine as eng_module
        import builtins
        original_import = builtins.__import__

        tomli_tried = []

        def fake_import(name, *args, **kwargs):
            if name == "tomllib":
                raise ImportError("simulated tomllib failure")
            if name == "tomli":
                tomli_tried.append(True)
                # Retorna mock com loads que falha para cair no fallback regex
                import types
                mock = types.ModuleType("tomli")
                def fake_loads(txt):
                    raise ValueError("fake tomli failure to trigger regex fallback")
                mock.loads = fake_loads
                return mock
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            # Cria engine nova para testar dependencies com pyproject.toml
            eng = eng_module.ReversaUniversalEngine()
            # Cria tmp com pyproject.toml simples
            import tempfile
            from pathlib import Path as P
            with tempfile.TemporaryDirectory() as tmp:
                P(tmp, "pyproject.toml").write_text('[project]\nname="test"\n', encoding="utf-8")
                # Não deve lançar, deve cair no fallback e retornar deps vazio ou parcial
                deps = eng.dependencies(tmp)
                # Verifica que tomli foi tentado
                self.assertTrue(tomli_tried, "tomli deve ter sido tentado quando tomllib falha")

    def test_dependencies_still_works_with_tomllib(self):
        from reversa_universal.engine import ReversaUniversalEngine
        eng = ReversaUniversalEngine()
        deps = eng.dependencies(".")
        self.assertIsInstance(deps["all"], list)


class TestG4HarnessWorkerPool(unittest.TestCase):
    def test_harness_worker_pool_exists(self):
        from integrations.harness.harness_worker_pool import HarnessWorkerPool
        pool = HarnessWorkerPool()
        self.assertEqual(pool.PREFIX, "harness-worker-")
        self.assertIn("harness_execution", pool.WORKER_CAPABILITIES)

    def test_universal_bridge_uses_harness_pool(self):
        from integrations.harness.universal_bridge import UniversalHarnessBridge
        from integrations.harness.harness_worker_pool import HarnessWorkerPool
        bridge = UniversalHarnessBridge()
        self.assertIsInstance(bridge.pool, HarnessWorkerPool)

    def test_scale_and_submit(self):
        from integrations.harness.harness_worker_pool import HarnessWorkerPool

        def runner(prompt, **kw):
            return {"status": "completed", "final_response": f"ok {prompt}"}

        pool = HarnessWorkerPool()
        try:
            pool.scale(2)
            self.assertEqual(len(pool.list_workers()), 2)
            self.assertTrue(all("harness-worker-" in w["agent_id"] for w in pool.list_workers()))
            results = pool.submit("teste harness worker pool", runner=runner)
            self.assertEqual(len(results), 2)
            self.assertTrue(all(r["status"] == "completed" for r in results))
        finally:
            pool.scale(0)
            # cleanup
            try:
                from mci.blackboard import blackboard
                for wid in list(blackboard.registry.keys()):
                    if wid.startswith("harness-worker-"):
                        del blackboard.registry[wid]
            except Exception:
                pass


class TestG5AverageScoreDocs(unittest.TestCase):
    def test_average_score_docstring(self):
        from evolution.cycles import EvolutionRegistry
        doc = EvolutionRegistry.average_score.__doc__ or ""
        self.assertIn("média móvel", doc.lower())
        self.assertIn("não é gate", doc.lower())

    def test_readme_mentions_average(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("média móvel", readme.lower())
        self.assertIn("não gate", readme.lower())

    def test_doctor_101_specs(self):
        from marceloclaro.doctor import run_doctor
        report = run_doctor()
        specs = next((c for c in report["checks"] if c["name"] == "specs_formais"), None)
        self.assertIsNotNone(specs)
        # Após R438, deve ser 101
        self.assertIn("101", specs["detail"])


class TestCompatibility(unittest.TestCase):
    def test_r433_r437_still_green(self):
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_r433_deepseek_harness_bridge.py", "tests/test_r434_deepseek_harness_reasoning.py", "tests/test_r435_harness_universal.py", "tests/test_r436_enhanced_search_rag.py", "tests/test_r437_reversa_universal.py", "-q"],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, f"R433-R437 devem permanecer GREEN: {result.stdout[-500:]}")


if __name__ == "__main__":
    unittest.main()
