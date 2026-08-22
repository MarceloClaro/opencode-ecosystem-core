# -*- coding: utf-8 -*-
"""
Testes SPEC-935-R435 — Harness Universal Agnóstico a Modelo
============================================================
Valida que o harness funciona com qualquer modelo do OpenCode
(litert, colibri, openai, zen) via ModelRouter, com gate 97 preservado.
Runners injetados garantem determinismo sem credenciais.
"""

import sys
import unittest

sys.path.insert(0, ".")  # repo root

from sdd.spec_engine import spec_registry


def _long_resp(prompt: str) -> str:
    return (
        f"{prompt} — resposta universal detalhada e ancorada que repete {prompt} "
        f"com substância adicional suficiente para GradingHead 7/7 e gate 97 do harness universal."
    )


def _runner_ok(prompt: str, provider=None, model=None, task_type=None, **kw):
    # Compatível com assinatura universal e legada
    return {
        "status": "completed",
        "final_response": _long_resp(prompt),
        "content": _long_resp(prompt),
        "events": [{"method": "session.event", "payload": {"event": {"type": "agent.turn.completed"}}}],
        "provider": provider,
        "model": model,
    }


def _runner_simple(prompt: str, cwd=None, **kw):
    return {"status": "completed", "final_response": _long_resp(prompt), "events": []}


class TestR435Spec(unittest.TestCase):
    def test_spec_r435_registered_green(self):
        spec = spec_registry.get("SPEC-935-R435")
        self.assertIsNotNone(spec, "SPEC-935-R435 deve estar no SpecRegistry")
        self.assertEqual(spec.status, "green")


class TestR435Registry(unittest.TestCase):
    def test_discover_returns_providers_and_models(self):
        from integrations.harness.model_registry import HarnessModelRegistry

        reg = HarnessModelRegistry()
        data = reg.discover()
        self.assertIsInstance(data, dict)
        self.assertIn("providers", data)
        self.assertIn("total_models", data)
        self.assertGreaterEqual(data["total_models"], 5)
        # Ao menos 2 providers normalizados (litert, colibri, zen, openai, go)
        self.assertGreaterEqual(len(data["providers"]), 2)

    def test_route_coding_returns_routed(self):
        from integrations.harness.model_registry import HarnessModelRegistry

        reg = HarnessModelRegistry()
        route = reg.route("coding")
        self.assertTrue(getattr(route, "provider_id", None))
        self.assertTrue(getattr(route, "model_id", None))


class TestR435UniversalAdapter(unittest.TestCase):
    def test_resolve_model_coding(self):
        from integrations.harness.universal_adapter import UniversalHarnessAdapter

        ad = UniversalHarnessAdapter()
        r = ad.resolve_model("coding")
        self.assertTrue(getattr(r, "provider_id", None))
        self.assertTrue(getattr(r, "model_id", None))

    def test_run_task_with_runner_injected(self):
        from integrations.harness.universal_adapter import UniversalHarnessAdapter

        ad = UniversalHarnessAdapter()
        before = ad.executions
        res = ad.run_task("tarefa universal coding", task_type="coding", runner=_runner_ok)
        self.assertEqual(res["status"], "completed")
        self.assertIn("final_response", res)
        self.assertEqual(ad.executions, before + 1)

    def test_run_task_respects_forced_provider_model(self):
        from integrations.harness.universal_adapter import UniversalHarnessAdapter

        ad = UniversalHarnessAdapter()
        res = ad.run_task(
            "tarefa com modelo forçado",
            task_type="coding",
            provider="litert-lm",
            model="gemma-4-E2B-it",
            runner=_runner_ok,
        )
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res.get("routed_provider"), "litert-lm")
        self.assertEqual(res.get("routed_model"), "gemma-4-E2B-it")

    def test_run_task_with_legacy_runner_signature(self):
        from integrations.harness.universal_adapter import UniversalHarnessAdapter

        ad = UniversalHarnessAdapter()
        res = ad.run_task("compat legada", runner=_runner_simple)
        self.assertEqual(res["status"], "completed")


class TestR435UniversalBridge(unittest.TestCase):
    def test_bridge_status(self):
        from integrations.harness.universal_bridge import UniversalHarnessBridge

        b = UniversalHarnessBridge()
        s = b.status()
        self.assertIn("registry", s)
        self.assertIn("adapter", s)
        self.assertIn("pool", s)
        self.assertEqual(s["harness"], "universal")

    def test_orchestrate_creates_tspec_green(self):
        from integrations.harness.universal_bridge import UniversalHarnessBridge

        b = UniversalHarnessBridge()
        out = b.orchestrate("produção universal coding", task_type="coding", runner=_runner_ok, workers=1)
        self.assertIn("spec_id", out)
        self.assertTrue(out["spec_id"].startswith("TSPEC-"))
        self.assertEqual(out["verification"]["status"], "green")
        self.assertEqual(out["task_type"], "coding")

    def test_orchestrate_with_reasoning_task_type(self):
        from integrations.harness.universal_bridge import UniversalHarnessBridge

        b = UniversalHarnessBridge()
        out = b.orchestrate("resolver problema matemático", task_type="reasoning", runner=_runner_ok)
        self.assertEqual(out["verification"]["status"], "green")


class TestR435UniversalReasoningLoop(unittest.TestCase):
    def test_loop_achieves_97_any_task_type(self):
        from integrations.harness.universal_reasoning_loop import UniversalReasoningLoop

        for task_type in ("coding", "reasoning", "writing"):
            loop = UniversalReasoningLoop(max_iters=3, target=0.97)
            res = loop.run(_long_resp(f"tarefa {task_type} universal"), task_type=task_type, runner=_runner_ok, workers=1)
            self.assertTrue(res["achieved_target"], f"gate 97 deve ser atingido para task_type={task_type}")
            self.assertGreaterEqual(res["best"]["grade"]["score"], 6)
            self.assertGreaterEqual(res["best"]["calibrated_value"], 0.97)
            # cleanup
            try:
                loop.bridge.pool.scale(0)
                from mci.blackboard import blackboard

                for wid in list(blackboard.registry.keys()):
                    if wid.startswith(("harness-worker-", "dsh-worker-")):
                        del blackboard.registry[wid]
            except Exception:
                pass

    def test_loop_with_forced_provider(self):
        from integrations.harness.universal_reasoning_loop import UniversalReasoningLoop

        loop = UniversalReasoningLoop()
        res = loop.run(
            "tarefa litert específica",
            task_type="coding",
            provider="litert-lm",
            model="gemma-4-E2B-it",
            runner=_runner_ok,
            workers=1,
        )
        self.assertTrue(res["achieved_target"])
        self.assertEqual(res["provider"], "litert-lm")
        self.assertEqual(res["model"], "gemma-4-E2B-it")

    def test_loop_spec_registered(self):
        from sdd.loop_spec import loop_spec_registry

        spec = loop_spec_registry.get("harness-reasoning-97")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.max_iterations, 3)


class TestR435OrchestratorUniversal(unittest.TestCase):
    def test_orchestrator_has_harness_methods(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator

        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        for attr in ("harness", "harness_status", "orchestrate_harness", "orchestrate_harness_iterative", "harness_reasoning_loop"):
            self.assertTrue(hasattr(orch, attr), f"orquestrador deve ter {attr}")

    def test_orchestrate_harness_any_task_type(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator

        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        for task_type in ("coding", "reasoning"):
            out = orch.orchestrate_harness(
                f"produção harness {task_type} universal", task_type=task_type, runner=_runner_ok, workers=1
            )
            self.assertEqual(out["verification"]["status"], "green")

    def test_orchestrate_harness_iterative_97(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator

        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        out = orch.orchestrate_harness_iterative(
            "produção harness iterativa universal até 97",
            task_type="coding",
            provider="litert-lm",
            model="gemma-4-E2B-it",
            runner=_runner_ok,
            workers=1,
            max_iters=3,
            target=0.97,
        )
        self.assertTrue(out["achieved_target"])
        self.assertGreaterEqual(out["best"]["grade"]["score"], 6)
        # cleanup
        try:
            orch.harness.pool.scale(0)
            from mci.blackboard import blackboard

            for wid in list(blackboard.registry.keys()):
                if wid.startswith(("harness-worker-", "dsh-worker-")):
                    del blackboard.registry[wid]
        except Exception:
            pass

    def test_deepseek_compat_still_works(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator

        orch = MarceloClaroOrchestrator(auto_load_agents=False)

        def ds_runner(prompt, cwd=None, **kw):
            return {"status": "completed", "final_response": _long_resp(prompt), "events": []}

        out = orch.orchestrate_deepseek_harness("compat deepseek legada", workers=1, runner=ds_runner)
        self.assertIn("spec_id", out)
        self.assertEqual(out["verification"]["status"], "green")


if __name__ == "__main__":
    unittest.main()
