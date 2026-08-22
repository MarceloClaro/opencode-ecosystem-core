# -*- coding: utf-8 -*-
"""
Testes da SPEC-935-R433 — Ponte Orquestrada DeepSeek Harness
=============================================================
Valida a integração do DeepSeek Harness (`dsh`, deepseek-harness.zip) ao
OpenCode Ecosystem Core: inventário factual, canal de execução com runner
injetado, ingestão metacognitiva, pool escalável e fachada no orquestrador.

Execuções REAIS contra a API da DeepSeek NÃO são testadas aqui (requerem
DEEPSEEK_API_KEY); os runners são injetados (padrão TDD).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdd.spec_engine import spec_registry

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DSH_DIR = os.path.join(REPO_ROOT, "deepseek-harness")
MONOREPO = os.path.join(DSH_DIR, "DEEPSEEK-HARNESS")


def _fake_runner(prompt: str, cwd=None):
    """Runner injetado que simula um runtime dsh saudável (determinístico)."""
    return {
        "status": "completed",
        "session_id": "sess-test-001",
        "final_response": f"dsh-ok:{prompt[:32]}",
        "events": [
            {"method": "session.event",
             "payload": {"sessionId": "sess-test-001",
                         "event": {"type": "agent.turn.completed",
                                   "turns": 1}}},
            {"method": "session.event",
             "payload": {"sessionId": "sess-test-001",
                         "event": {"type": "tool.call.completed",
                                   "tool": "read"}}},
        ],
    }


@unittest.skipUnless(os.path.isdir(MONOREPO),
                     "deepseek-harness/ não extraído neste checkout")
class TestR433Inventory(unittest.TestCase):
    """C2 do SPEC — inventário factual do monorepo + artefatos Reversa."""

    def setUp(self):
        from integrations.deepseek_harness.inventory import DeepSeekHarnessInventory
        self.inventory = DeepSeekHarnessInventory(dsh_root=DSH_DIR)

    def test_spec_r433_registered_green(self):
        spec = spec_registry.get("SPEC-935-R433")
        self.assertIsNotNone(spec, "SPEC-935-R433 deve estar no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_discover_reports_reversa_metadata(self):
        data = self.inventory.discover()
        self.assertTrue(data["available"])
        self.assertEqual(data["reversa"]["phase"], "concluido")
        self.assertGreaterEqual(data["reversa"]["workspace_packages"], 200)
        self.assertGreaterEqual(data["reversa"]["modules_identified"], 10)
        self.assertEqual(data["identity"]["package_root"], "@deepseek-ai/dsh-root")

    def test_capability_groups_from_real_tree(self):
        groups = self.inventory.capability_groups()
        self.assertGreaterEqual(len(groups), 40,
                                "monorepo real tem ~49 grupos de pacotes")
        for expected in ("core", "subagent", "llm", "sdk", "session"):
            self.assertIn(expected, groups)

    def test_no_fabricated_metrics(self):
        data = self.inventory.discover()
        # Métricas vêm de contagem real da árvore, não de valores fixos.
        self.assertIsInstance(data["metrics"]["package_groups"], int)
        self.assertGreater(data["metrics"]["package_groups"], 0)


@unittest.skipUnless(os.path.isdir(MONOREPO),
                     "deepseek-harness/ não extraído neste checkout")
class TestR433Adapter(unittest.TestCase):
    """C2 — canal de execução; nunca simula sucesso sem canal real."""

    def setUp(self):
        from integrations.deepseek_harness.adapter import DeepSeekHarnessAdapter
        self.adapter = DeepSeekHarnessAdapter(dsh_root=DSH_DIR)

    def test_channel_resolution_is_explicit(self):
        channel = self.adapter.resolve_channel()
        self.assertIn(channel, ("sdk", "runtime-bin", "unavailable"))

    def test_run_task_without_channel_queues_handoff(self):
        if self.adapter.resolve_channel() != "unavailable":
            self.skipTest("canal real disponível neste ambiente")
        result = self.adapter.run_task("mapear pacotes core")
        self.assertEqual(result["status"], "unavailable")
        self.assertTrue(result.get("handoff_file"),
                        "handoff auditável deve ser enfileirado")

    def test_run_task_with_injected_runner(self):
        before = self.adapter.executions
        result = self.adapter.run_task("auditar sessões", runner=_fake_runner)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["final_response"].startswith("dsh-ok:"))
        self.assertEqual(self.adapter.executions, before + 1)

    def test_injected_runner_failure_is_reported_not_swallowed(self):
        def bad_runner(prompt, cwd=None):
            raise RuntimeError("runtime crash")
        result = self.adapter.run_task("tarefa falha", runner=bad_runner)
        self.assertEqual(result["status"], "error")
        self.assertIn("runtime crash", result["error"])


@unittest.skipUnless(os.path.isdir(MONOREPO),
                     "deepseek-harness/ não extraído neste checkout")
class TestR433Metacognition(unittest.TestCase):
    """C3 — eventos de sessão e Agent Notes do dsh → MetaBus."""

    def setUp(self):
        from integrations.deepseek_harness.metacognition import DSHMetacognitionIngestor
        from mci.metabus import metabus
        self.metabus = metabus
        self.ingestor = DSHMetacognitionIngestor(
            dsh_root=DSH_DIR, metabus=self.metabus)

    def test_ingest_session_events_creates_reflection(self):
        fake_events = _fake_runner("x")["events"]
        summary = self.ingestor.ingest_session_events(fake_events, task_id="task-dsh-1")
        self.assertEqual(summary["events_seen"], 2)
        self.assertGreaterEqual(summary["reflections_added"], 1)

    def test_ingest_agent_notes_registers_lessons(self):
        notes = self.ingestor.ingest_agent_notes(limit=5)
        self.assertGreaterEqual(notes["notes_scanned"], 0)
        # O repositório real tem notas implementadas — se existirem, devem
        # gerar tópicos semânticos com proveniência explícita.
        if notes["notes_scanned"] > 0:
            self.assertGreaterEqual(notes["topics_registered"], 1)
            semantic_store = getattr(self.metabus.memory, "semantic", None) or getattr(
                self.metabus.memory, "semantic_topics", None) or {}
            topic = semantic_store.get("deepseek_harness.agent_notes")
            self.assertIsNotNone(topic)


@unittest.skipUnless(os.path.isdir(MONOREPO),
                     "deepseek-harness/ não extraído neste checkout")
class TestR433WorkerPool(unittest.TestCase):
    """C4 — escala de workers dsh no Blackboard com trust/economy."""

    def setUp(self):
        from integrations.deepseek_harness.worker_pool import DeepSeekWorkerPool
        from mci.metabus import metabus
        self.pool = DeepSeekWorkerPool(metabus=metabus)

    def tearDown(self):
        self.pool.scale(0)

    def test_scale_registers_exact_workers(self):
        self.pool.scale(2)
        workers = [c for c in self.pool.list_workers()]
        self.assertEqual(len(workers), 2)
        for card in workers:
            self.assertIn("dsh_execution", card["capabilities"])

        self.pool.scale(1)
        self.assertEqual(len(self.pool.list_workers()), 1)

        self.pool.scale(0)
        self.assertEqual(len(self.pool.list_workers()), 0)

    def test_submit_runs_and_learns_outcome(self):
        self.pool.scale(1)
        results = self.pool.submit("produção autônoma de teste",
                                   runner=_fake_runner)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "completed")
        report = self.pool.report()
        self.assertEqual(report["runs"], 1)
        self.assertEqual(report["successes"], 1)

    def test_submit_parallel_across_workers(self):
        self.pool.scale(3)
        results = self.pool.submit("lote paralelo", runner=_fake_runner)
        self.assertEqual(len(results), 3)
        report = self.pool.report()
        self.assertEqual(report["runs"], 3)
        self.assertEqual(report["successes"], 3)


@unittest.skipUnless(os.path.isdir(MONOREPO),
                     "deepseek-harness/ não extraído neste checkout")
class TestR433BridgeAndOrchestrator(unittest.TestCase):
    """C5 — fachada + integração lazy no orquestrador."""

    def test_bridge_status_auditavel(self):
        from integrations.deepseek_harness.bridge import DeepSeekHarnessBridge
        bridge = DeepSeekHarnessBridge(dsh_root=DSH_DIR)
        status = bridge.status()
        self.assertTrue(status["inventory"]["available"])
        self.assertIn(status["adapter"]["channel"],
                      ("sdk", "runtime-bin", "unavailable"))
        self.assertIn("pool", status)

    def test_orchestrate_applies_sdd_gate(self):
        from integrations.deepseek_harness.bridge import DeepSeekHarnessBridge
        bridge = DeepSeekHarnessBridge(dsh_root=DSH_DIR)
        outcome = bridge.orchestrate(
            "produção autônoma orquestrada pelo Core",
            runner=_fake_runner,
        )
        self.assertIn("spec_id", outcome)
        self.assertTrue(outcome["spec_id"].startswith("TSPEC-"))
        self.assertEqual(outcome["verification"]["status"], "green")

    def test_orchestrator_has_lazy_dsh_method(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        self.assertTrue(hasattr(orch, "orchestrate_deepseek_harness"))
        # Lazy: sem execução anterior, o estado não exige zip nem SDK.
        state = orch.dsh_state()
        self.assertIsInstance(state, dict)


if __name__ == "__main__":
    unittest.main()
