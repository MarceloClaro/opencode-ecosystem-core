# -*- coding: utf-8 -*-
"""
Testes TDD dos subsistemas avançados portados do OpenCode_Ecosystem
===================================================================
Cobre: Trust Engine (SPEC-007/038), Token Economy (SPEC-008/022~025),
Scanners (SPEC-009), MASWOS (SPEC-010), Reasoning + Quantum (SPEC-011),
Evolution (SPEC-012) e Integrações CLI (SPEC-013/046).
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── SPEC-007: Trust Engine ──────────────────────────────────────────────

class TestTrustEngine:
    def test_gate_allows_and_learns(self):
        from trust import create_trust_engine
        engine = create_trust_engine()
        decision = engine.execute("delegate:coder")
        assert decision.allowed is True  # baseline permite ação nova
        # Shadow mode: score conservador (<= 0.5) nas primeiras execuções
        for _ in range(engine.scorer.SHADOW_MODE_THRESHOLD + 2):
            engine.learn("delegate:coder", success=True)
        score_after = engine.scorer.get_trust("delegate:coder").trust_score
        assert score_after > 0.5  # confiança cresce após sair do shadow mode

    def test_trust_decays_on_failures(self):
        from trust import create_trust_engine
        engine = create_trust_engine()
        for _ in range(5):
            engine.learn("delegate:flaky", success=False)
        score = engine.scorer.get_trust("delegate:flaky").trust_score
        assert score < 0.5  # confiança cai com falhas repetidas

    def test_natural_forgetting_stores_and_recalls(self):
        from trust import create_trust_engine
        engine = create_trust_engine()
        engine.memory.store("lição importante sobre timeout de API", importance=0.9)
        slot = engine.memory.recall("timeout")
        assert slot is not None


# ── SPEC-008: Token Economy ─────────────────────────────────────────────

class TestTokenEconomy:
    def test_stake_and_release_on_success(self):
        from economy import TokenEconomy
        eco = TokenEconomy()
        eco.post_task("orch", "t-ok", "normal")
        eco.commit("agent-a", "t-ok", 5.0)
        before = eco.balance("agent-a")
        result = eco.resolve("t-ok", success=True)
        assert result["positions"][0]["status"] == "released"
        assert eco.balance("agent-a") > before  # stake devolvido + recompensa

    def test_slashing_on_failure(self):
        from economy import TokenEconomy
        eco = TokenEconomy()
        eco.post_task("orch", "t-fail", "high")
        eco.commit("agent-b", "t-fail", 4.0)
        result = eco.resolve("t-fail", success=False)
        assert result["positions"][0]["status"] == "slashed"
        assert eco.balance("agent-b") < 100.0  # perdeu parte do stake

    def test_fee_market_priority_pricing(self):
        from economy import TokenEconomy
        eco = TokenEconomy()
        low = eco.post_task("orch", "t-low", "low")
        high = eco.post_task("orch", "t-high", "high")
        assert high.total_fee > low.total_fee  # prioridade alta custa mais


# ── SPEC-009: Pipeline de Scanners ──────────────────────────────────────

class TestDiagnosticPipeline:
    def test_run_returns_all_sections(self):
        from scanners import DiagnosticPipeline
        pipeline = DiagnosticPipeline()
        report = pipeline.run(
            "Estudo com metodologia reprodutível e validação estatística.",
            domain="test",
            goals=[{"name": "g", "description": "avaliar", "goal_type": "evaluative"}],
        )
        for section in ["noological", "teleological", "potentiality", "evolutionary"]:
            assert section in report
        assert "recommendation" in report["evolutionary"]

    def test_pipeline_survives_empty_corpus(self):
        from scanners import DiagnosticPipeline
        report = DiagnosticPipeline().run("", domain="")
        assert "evolutionary" in report  # degradação graciosa


# ── SPEC-010: Pipeline Acadêmico MASWOS ─────────────────────────────────

class TestMaswos:
    def test_dry_run_has_16_stages(self):
        from academic import MaswosPipeline, MASWOS_STAGES
        assert len(MASWOS_STAGES) == 16
        run = MaswosPipeline().run("tópico de teste")
        assert len(run.stages) == 16
        assert all(s.status == "skipped" for s in run.stages)  # dry-run

    def test_quality_gate_blocks_weak_manuscript(self):
        from academic import MaswosPipeline
        run = MaswosPipeline().run("tópico", manuscript="texto raso sem estrutura")
        assert run.approved is False

    def test_delegation_mode_completes_stages(self):
        from academic import MaswosPipeline
        pipeline = MaswosPipeline(delegate_fn=lambda a, c, d: f"saída de {a}")
        run = pipeline.run("tópico", stages=["estatistica", "qa_qualis_a1"])
        assert sum(1 for s in run.stages if s.status == "completed") == 2


# ── SPEC-011: Reasoning + Quantum ───────────────────────────────────────

class TestReasoning:
    def test_all_four_engines_exist(self):
        from reasoning import multi_reasoning
        assert set(multi_reasoning.engines.keys()) == {"z3", "sympy", "kanren", "critical"}

    def test_critical_engine_always_available(self):
        from reasoning import multi_reasoning
        result = multi_reasoning.reason("isso sempre funciona", engine="critical")
        assert result.available is True
        assert "SÍNTESE" in " ".join(result.steps)

    def test_auto_routing(self):
        from reasoning import MultiReasoningEngine
        assert MultiReasoningEngine._route("resolver equação x=2") == "sympy"
        assert MultiReasoningEngine._route("verificar restrição sat") == "z3"


class TestQuantum:
    def test_bell_state_correlations(self):
        from reasoning import bell_state
        counts = bell_state(seed=42).measure(shots=500)
        assert set(counts.keys()) <= {"00", "11"}  # apenas estados correlacionados

    def test_ghz_entanglement(self):
        from reasoning import ghz_state
        sim = ghz_state(3, seed=42)
        probs = sim.probabilities()
        assert set(probs.keys()) == {"000", "111"}
        assert abs(sim.entanglement_entropy() - 1.0) < 0.01  # 1 bit de entropia

    def test_qubit_range_validation(self):
        from reasoning import QuantumSimulator
        with pytest.raises(ValueError):
            QuantumSimulator(1)  # abaixo do mínimo
        with pytest.raises(ValueError):
            QuantumSimulator(101)  # acima do máximo

    def test_experiment_suite_reproducible(self):
        from reasoning import run_experiment_suite
        r1 = run_experiment_suite(2, seeds=[42], shots=100)
        r2 = run_experiment_suite(2, seeds=[42], shots=100)
        assert r1["experiments"]["bell"]["runs"][0]["counts"] == \
               r2["experiments"]["bell"]["runs"][0]["counts"]


# ── SPEC-012: Ciclos Evolutivos ─────────────────────────────────────────

class TestEvolution:
    def test_round_numbering_continues_from_r46(self, tmp_path):
        from evolution.cycles import EvolutionRegistry
        registry = EvolutionRegistry(state_path=str(tmp_path / "cycles.json"))
        cycle = registry.record("objetivo", ["mudança"], score=8.0)
        assert cycle.round_id == "R47"
        cycle2 = registry.record("objetivo 2", ["mudança 2"], score=9.0)
        assert cycle2.round_id == "R48"
        assert registry.average_score() == 8.5

    def test_documented_cycles_indexed(self):
        from evolution import evolution_registry
        docs = evolution_registry.load_documented_cycles()
        assert len(docs) >= 10  # evo-*.md portados do original


# ── SPEC-013: Integrações CLI ───────────────────────────────────────────

class TestIntegrations:
    def test_antigravity_queues_when_cli_absent(self):
        from integrations.antigravity import AntigravityBridge
        bridge = AntigravityBridge(cli_command="antigravity-inexistente")
        result = bridge.delegate("teste")
        assert result["status"] == "queued"
        assert os.path.exists(result["handoff_file"])
        os.remove(result["handoff_file"])  # limpeza

    def test_opencode_config_has_all_agents(self):
        from integrations.opencode_cli import build_config
        config = build_config()
        assert len(config["agent"]) >= 128  # catálogo completo
        assert "marceloclaro" in config["agent"]
        # O orquestrador primário prevalece sobre homônimos do catálogo
        assert config["agent"]["marceloclaro"]["mode"] == "primary"
        assert "metacognitive-interconnect" in config["mcp"]
        assert "diagnose" in config["command"]


# ── Integração com o orquestrador ───────────────────────────────────────

@pytest.fixture(scope="class")
def orchestrator():
    import mci.metabus as mb  # noqa: F401
    import mci.blackboard as bb  # noqa: F401
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    return MarceloClaroOrchestrator()

class TestOrchestratorIntegration:
    def test_catalog_registered_on_boot(self, orchestrator):
        assert orchestrator.catalog_size >= 128

    def test_status_includes_all_subsystems(self, orchestrator):
        status = orchestrator.status()
        for key in ["trust", "economy", "catalog_agents",
                    "reasoning_engines", "antigravity"]:
            assert key in status

    def test_diagnose_records_reflection(self, orchestrator):
        from mci.metabus import metabus
        before = len(metabus.memory.episodic)
        orchestrator.diagnose("corpus de teste com metodologia", domain="test")
        assert len(metabus.memory.episodic) > before

    def test_reason_integration(self, orchestrator):
        result = orchestrator.reason("resolver", engine="sympy", expression="2*x = 8")
        assert "4" in result["conclusion"]

    def test_quantum_integration(self, orchestrator):
        report = orchestrator.quantum_experiment(n_qubits=2, seeds=[42], shots=64)
        assert "bell" in report["experiments"]
