# -*- coding: utf-8 -*-
"""
Testes da SPEC-935-R434 — Ponte dsh Raciocinada até Score 97
=============================================================
Loop reflexivo com multi-raciocínio, calibração e grading iterativo
sobre a ponte R433. Runners injetados garantem determinismo.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdd.spec_engine import spec_registry

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DSH_DIR = os.path.join(REPO_ROOT, "deepseek-harness")
MONOREPO = os.path.join(DSH_DIR, "DEEPSEEK-HARNESS")


def _long_response(prompt: str) -> str:
    """Resposta longa e ancorada para garantir grade 7/7 (len>=40, overlap>=5)."""
    return (
        f"{prompt} — resposta detalhada e ancorada que repete {prompt} "
        f"com substância adicional suficiente para o GradingHead reconhecer "
        f"ancoragem completa e substância mínima, atingindo nota máxima 7/7 no gate 97."
    )


def _fake_runner_ok(prompt: str, cwd=None):
    return {
        "status": "completed",
        "session_id": "sess-97-ok",
        "final_response": _long_response(prompt),
        "events": [
            {"method": "session.event", "payload": {"event": {"type": "agent.turn.completed"}}},
        ],
    }


def _fake_runner_fail_then_ok_factory():
    state = {"calls": 0}

    def runner(prompt: str, cwd=None):
        state["calls"] += 1
        if state["calls"] == 1:
            raise RuntimeError("falha transitória na primeira iteração")
        return _fake_runner_ok(prompt, cwd=cwd)

    runner.state = state
    return runner


@unittest.skipUnless(os.path.isdir(MONOREPO), "deepseek-harness/ não extraído")
class TestR434SpecAndPreReason(unittest.TestCase):

    def test_spec_r434_registered_green(self):
        spec = spec_registry.get("SPEC-935-R434")
        self.assertIsNotNone(spec, "SPEC-935-R434 deve estar no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_pre_reason_returns_best_engine(self):
        from integrations.deepseek_harness.reasoning_loop import DeepSeekReasoningLoop

        loop = DeepSeekReasoningLoop()
        out = loop.pre_reason("analisar pacotes core do dsh e propor melhoria")
        self.assertIn(out["best_engine"], [
            "z3", "sympy", "kanren", "critical", "bayesian", "causal",
            "temporal", "fuzzy", "chain_of_thought", "analogical",
            "counterfactual", "quantum",
        ])
        self.assertTrue(out["refined_prompt"])
        self.assertIn("raciocínio", out["refined_prompt"])

    def test_grade_substantial_anchored(self):
        from integrations.deepseek_harness.reasoning_loop import DeepSeekReasoningLoop

        loop = DeepSeekReasoningLoop()
        objective = "produção autônoma raciocinada do dsh com qualidade até 97"
        response = _long_response(objective)
        grade = loop.grade_response(objective, response)
        self.assertGreaterEqual(grade["score"], 5)
        self.assertGreaterEqual(grade["normalized"], 0.7)
        self.assertEqual(grade["max_score"], 7)

    def test_calibrate_completed_returns_high(self):
        from integrations.deepseek_harness.reasoning_loop import DeepSeekReasoningLoop

        loop = DeepSeekReasoningLoop()
        outcome = {"results": [{"status": "completed", "final_response": _long_response("x")}]}
        grade = {"score": 7, "normalized": 1.0, "max_score": 7}
        cal = loop.calibrate(outcome, grade)
        self.assertGreaterEqual(cal["calibrated_confidence"], 0.7)


@unittest.skipUnless(os.path.isdir(MONOREPO), "deepseek-harness/ não extraído")
class TestR434IterativeLoop(unittest.TestCase):

    def setUp(self):
        from integrations.deepseek_harness.reasoning_loop import DeepSeekReasoningLoop

        self.loop = DeepSeekReasoningLoop(max_iters=3, target=0.97)

    def tearDown(self):
        # Limpa workers do bridge
        try:
            self.loop.bridge.pool.scale(0)
            from mci.blackboard import blackboard

            for wid in list(blackboard.registry.keys()):
                if wid.startswith("dsh-worker-"):
                    del blackboard.registry[wid]
        except Exception:
            pass

    def test_run_achieves_target_in_one_iter(self):
        result = self.loop.run(
            "produção autônoma raciocinada do dsh com qualidade até 97",
            runner=_fake_runner_ok,
            workers=1,
            max_iters=3,
            target=0.97,
        )
        self.assertTrue(result["achieved_target"])
        self.assertLessEqual(result["iterations"], 3)
        self.assertGreaterEqual(result["iterations"], 1)
        best = result["best"]
        self.assertIsNotNone(best)
        self.assertGreaterEqual(best["grade"]["score"], 6)
        self.assertGreaterEqual(best["calibrated_value"], 0.97)

    def test_run_reflects_on_failure_then_succeeds(self):
        runner = _fake_runner_fail_then_ok_factory()
        result = self.loop.run(
            "tarefa com falha transitória que deve refletir e recuperar",
            runner=runner,
            workers=1,
            max_iters=3,
            target=0.97,
        )
        # Deve ter 2 iterações (falha + sucesso) e atingir o gate
        self.assertEqual(len(result["history"]), 2)
        self.assertTrue(result["history"][0]["outcome"]["results"][0]["status"] in ("error", "failed") or
                        result["history"][0]["grade"]["score"] < 6 or
                        result["history"][0]["calibrated_value"] < 0.97)
        self.assertTrue(result["achieved_target"])
        self.assertEqual(result["history"][-1]["outcome"]["results"][0]["status"], "completed")


@unittest.skipUnless(os.path.isdir(MONOREPO), "deepseek-harness/ não extraído")
class TestR434OrchestratorIterative(unittest.TestCase):

    def test_orchestrator_has_iterative_method(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator

        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        self.assertTrue(hasattr(orch, "orchestrate_deepseek_harness_iterative"))
        self.assertTrue(hasattr(orch, "dsh_reasoning_status"))
        status = orch.dsh_reasoning_status()
        self.assertIsInstance(status, dict)
        self.assertIn("reasoning_engines", status)

    def test_orchestrate_iterative_achieves_green(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator

        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        out = orch.orchestrate_deepseek_harness_iterative(
            "produção autônoma raciocinada do dsh com qualidade até 97",
            workers=1,
            runner=_fake_runner_ok,
            max_iters=3,
            target=0.97,
        )
        self.assertTrue(out["achieved_target"])
        best = out["best"]
        self.assertIsNotNone(best)
        verif = best["outcome"]["verification"]
        self.assertEqual(verif["status"], "green")
        self.assertLessEqual(out["iterations"], 3)

    def test_loop_spec_registered(self):
        from sdd.loop_spec import loop_spec_registry

        spec = loop_spec_registry.get("dsh-reasoning-97")
        self.assertIsNotNone(spec, "LoopSpec dsh-reasoning-97 deve estar registrado")
        self.assertEqual(spec.max_iterations, 3)
        self.assertIn("success", spec.terminal_states)
