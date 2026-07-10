# -*- coding: utf-8 -*-
"""
Testes R109 — Loop Engineering formal no SDD + loop real do pipeline
cientifico (TDD: RED -> GREEN -> REFACTOR)
=====================================================================
Testa sdd/loop_spec.py (LoopSpecification, LoopSpecRegistry, is_stagnant)
e MarceloClaroOrchestrator.run_scientific_discovery_loop: estados
terminais nomeados, deteccao de estagnacao e a LoopSpecification
registrada para o pipeline cientifico.

Baseado em Macedo (2026), "Stop Hand-Holding Your Coding Agent: Engineering
the Loops that Replace Step-by-Step Prompting" (arXiv:2607.00038).

Requisitos (SPEC-935-R109):
  - LoopSpecification.validate() aplica o checklist de boa-formacao
    (trigger justificado, verificacao honesta, maker-checker se nivel>=4,
    estados terminais nomeados, orcamento e estagnacao configurados,
    memoria declarada)
  - is_stagnant() replica o formato de EvoEngine.is_stagnant
  - run_scientific_discovery_loop() atinge cada um dos 5 estados
    terminais nomeados conforme o cenario
  - describe_scientific_loop() expoe uma LoopSpecification bem formada
"""

import copy

import pytest


@pytest.fixture(autouse=True)
def _isolate_metacognitive_memory():
    """Ver justificativa em tests/test_r108_marceloclaro_scientific_fusion.py."""
    from mci.metabus import metabus

    snapshot = (
        copy.deepcopy(metabus.memory.episodic),
        copy.deepcopy(metabus.memory.semantic),
        copy.deepcopy(metabus.memory.confidence_ledger),
    )
    yield
    metabus.memory.episodic, metabus.memory.semantic, metabus.memory.confidence_ledger = snapshot
    metabus.memory._save()


def _make_orchestrator():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    return MarceloClaroOrchestrator(auto_load_agents=False)


# ── 1. is_stagnant ────────────────────────────────────────────────────

class TestIsStagnant:
    def test_not_stagnant_with_few_points(self):
        from sdd.loop_spec import is_stagnant
        assert is_stagnant([10.0], window=3) is False
        assert is_stagnant([10.0, 20.0], window=3) is False

    def test_stagnant_when_variation_below_threshold(self):
        from sdd.loop_spec import is_stagnant
        assert is_stagnant([50.0, 50.01, 50.0], window=3, threshold=0.02) is True

    def test_not_stagnant_when_variation_above_threshold(self):
        from sdd.loop_spec import is_stagnant
        assert is_stagnant([10.0, 50.0, 90.0], window=3, threshold=0.02) is False


# ── 2. LoopSpecification.validate() ──────────────────────────────────

class TestLoopSpecificationValidate:
    def _well_formed_kwargs(self):
        return dict(
            name="teste",
            description="loop de teste",
            use_when="quando testando",
            trigger="manual",
            trigger_justification="o resultado de uma rodada muda a proxima",
            goal="objetivo verificavel",
            verification_level=1,
            verification_description="assert real",
            architecture="solo",
            terminal_states=["success", "blocked"],
            stagnation_window=3,
            stagnation_threshold=0.02,
            max_iterations=5,
            memory_location="arquivo em disco",
        )

    def test_well_formed_loop_passes(self):
        from sdd.loop_spec import LoopSpecification
        loop = LoopSpecification(**self._well_formed_kwargs())
        v = loop.validate()
        assert v["well_formed"] is True
        assert v["issues"] == []
        assert v["verification_zone"] == "autonomous"

    def test_missing_trigger_justification_flagged(self):
        from sdd.loop_spec import LoopSpecification
        kwargs = self._well_formed_kwargs()
        kwargs["trigger_justification"] = ""
        loop = LoopSpecification(**kwargs)
        v = loop.validate()
        assert v["well_formed"] is False
        assert any("golden rule" in i for i in v["issues"])

    def test_level4_judge_without_maker_checker_flagged(self):
        """Anti-padrao 'self-approving loop': verificador nivel 4+ com
        arquitetura solo (quem produz tambem aprova)."""
        from sdd.loop_spec import LoopSpecification
        kwargs = self._well_formed_kwargs()
        kwargs["verification_level"] = 4
        kwargs["architecture"] = "solo"
        loop = LoopSpecification(**kwargs)
        v = loop.validate()
        assert v["well_formed"] is False
        assert any("maker-checker" in i for i in v["issues"])
        assert v["verification_zone"] == "assisted"

    def test_level4_judge_with_maker_checker_ok(self):
        from sdd.loop_spec import LoopSpecification
        kwargs = self._well_formed_kwargs()
        kwargs["verification_level"] = 4
        kwargs["architecture"] = "maker_checker"
        loop = LoopSpecification(**kwargs)
        v = loop.validate()
        assert not any("maker-checker" in i for i in v["issues"])

    def test_only_success_terminal_state_flagged(self):
        """Um so estado terminal nao distingue sucesso de nenhum modo de parada."""
        from sdd.loop_spec import LoopSpecification
        kwargs = self._well_formed_kwargs()
        kwargs["terminal_states"] = ["success"]
        loop = LoopSpecification(**kwargs)
        v = loop.validate()
        assert v["well_formed"] is False

    def test_zero_budget_flagged_as_runaway_risk(self):
        from sdd.loop_spec import LoopSpecification
        kwargs = self._well_formed_kwargs()
        kwargs["max_iterations"] = 0
        loop = LoopSpecification(**kwargs)
        v = loop.validate()
        assert v["well_formed"] is False
        assert any("runaway" in i for i in v["issues"])

    def test_missing_memory_location_flagged(self):
        from sdd.loop_spec import LoopSpecification
        kwargs = self._well_formed_kwargs()
        kwargs["memory_location"] = ""
        loop = LoopSpecification(**kwargs)
        v = loop.validate()
        assert v["well_formed"] is False

    def test_to_markdown_contains_all_sections(self):
        from sdd.loop_spec import LoopSpecification
        loop = LoopSpecification(**self._well_formed_kwargs())
        doc = loop.to_markdown()
        for section in ("Trigger", "Objetivo e Verificação", "Arquitetura",
                        "Estados Terminais Nomeados", "Regra de Parada",
                        "Memória", "Guardrails", "Boa-formação"):
            assert section in doc


# ── 3. LoopSpecRegistry ──────────────────────────────────────────────

class TestLoopSpecRegistry:
    def test_register_and_get(self):
        from sdd.loop_spec import LoopSpecification, LoopSpecRegistry
        registry = LoopSpecRegistry()
        loop = LoopSpecification(
            name="teste-registro", description="d", use_when="u",
            trigger_justification="j", goal="g",
            verification_description="v", memory_location="m",
        )
        registry.register(loop)
        assert registry.get("teste-registro") is loop
        assert any(item["name"] == "teste-registro" for item in registry.list())


# ── 4. describe_scientific_loop() ────────────────────────────────────

class TestDescribeScientificLoop:
    def test_scientific_loop_spec_is_well_formed_and_autonomous(self):
        orch = _make_orchestrator()
        spec = orch.describe_scientific_loop()
        assert spec["validation"]["well_formed"] is True
        assert spec["validation"]["verification_zone"] == "autonomous"
        assert spec["verification_level"] <= 2
        assert set(["success", "blocked", "stalled", "exhausted", "error"]).issubset(
            set(spec["terminal_states"])
        )


# ── 5. run_scientific_discovery_loop: estados terminais ──────────────

class TestLoopTerminalStates:
    def test_error_stops_immediately_without_burning_budget(self, monkeypatch):
        orch = _make_orchestrator()

        def fake_pipeline(self, seed_domain, max_rounds=3, venue="abnt", strict_gates=True):
            return {"status": "error", "error": "falha forcada", "stages": {},
                    "calibrated_confidences": {}, "metacognitive_report": {}}

        monkeypatch.setattr(type(orch), "scientific_discovery_pipeline", fake_pipeline)

        result = orch.run_scientific_discovery_loop("dominio", max_iterations=5)

        assert result["terminal_state"] == "error"
        assert result["iterations_used"] == 1  # nao insiste apos erro

    def test_success_stops_at_first_passing_iteration(self, monkeypatch):
        orch = _make_orchestrator()
        calls = []

        def fake_pipeline(self, seed_domain, max_rounds=3, venue="abnt", strict_gates=True):
            calls.append(max_rounds)
            return {
                "status": "completed",
                "gate_decision": {"passed": True},
                "stages": {"r101": {"history": [{"ideas": [{"id": "i1", "scores": {"overall": 0.9}}]}]}},
                "calibrated_confidences": {},
                "metacognitive_report": {"readiness_score": 80.0, "tier": "research_grade"},
            }

        monkeypatch.setattr(type(orch), "scientific_discovery_pipeline", fake_pipeline)

        result = orch.run_scientific_discovery_loop("dominio", max_iterations=5)

        assert result["terminal_state"] == "success"
        assert result["iterations_used"] == 1
        assert calls == [3]  # primeira iteracao usa o max_rounds base

    def test_no_op_when_evosci_generates_no_ideas(self, monkeypatch):
        orch = _make_orchestrator()

        def fake_pipeline(self, seed_domain, max_rounds=3, venue="abnt", strict_gates=True):
            return {
                "status": "blocked",
                "gate_decision": {"passed": False},
                "stages": {"r101": {"history": [{"ideas": []}]}},
                "calibrated_confidences": {},
                "metacognitive_report": {"readiness_score": 10.0},
            }

        monkeypatch.setattr(type(orch), "scientific_discovery_pipeline", fake_pipeline)

        result = orch.run_scientific_discovery_loop("dominio", max_iterations=5)

        assert result["terminal_state"] == "no_op"
        assert result["iterations_used"] == 1

    def test_stalled_when_readiness_score_stops_improving(self, monkeypatch):
        orch = _make_orchestrator()
        scores = iter([50.0, 50.01, 50.0, 99.0])  # os 3 primeiros estagnam

        def fake_pipeline(self, seed_domain, max_rounds=3, venue="abnt", strict_gates=True):
            return {
                "status": "blocked",
                "gate_decision": {"passed": False},
                "stages": {"r101": {"history": [{"ideas": [{"id": "i1", "scores": {"overall": 0.5}}]}]}},
                "calibrated_confidences": {},
                "metacognitive_report": {"readiness_score": next(scores)},
            }

        monkeypatch.setattr(type(orch), "scientific_discovery_pipeline", fake_pipeline)

        result = orch.run_scientific_discovery_loop(
            "dominio", max_iterations=10, stagnation_window=3, stagnation_threshold=0.02,
        )

        assert result["terminal_state"] == "stalled"
        assert result["iterations_used"] == 3
        assert result["readiness_history"] == [50.0, 50.01, 50.0]

    def test_blocked_when_budget_exhausted_without_stagnation_or_success(self, monkeypatch):
        orch = _make_orchestrator()
        # Scores sobem monotonicamente o suficiente para nunca estagnar
        # dentro da janela, mas o gate nunca passa.
        scores = iter([10.0, 25.0, 40.0])

        def fake_pipeline(self, seed_domain, max_rounds=3, venue="abnt", strict_gates=True):
            return {
                "status": "blocked",
                "gate_decision": {"passed": False},
                "stages": {"r101": {"history": [{"ideas": [{"id": "i1", "scores": {"overall": 0.5}}]}]}},
                "calibrated_confidences": {},
                "metacognitive_report": {"readiness_score": next(scores)},
            }

        monkeypatch.setattr(type(orch), "scientific_discovery_pipeline", fake_pipeline)

        result = orch.run_scientific_discovery_loop(
            "dominio", max_iterations=3, stagnation_window=3, stagnation_threshold=0.02,
        )

        assert result["terminal_state"] == "blocked"
        assert result["iterations_used"] == 3
        assert "Gate do R103 nunca foi aprovado" in result["reason"]

    def test_escalates_max_rounds_across_iterations(self, monkeypatch):
        """A cada iteracao o max_rounds do EvoSci aumenta — feedback real
        entre voltas, nao so repeticao identica (golden rule)."""
        orch = _make_orchestrator()
        calls = []

        def fake_pipeline(self, seed_domain, max_rounds=3, venue="abnt", strict_gates=True):
            calls.append(max_rounds)
            return {
                "status": "blocked",
                "gate_decision": {"passed": False},
                "stages": {"r101": {"history": [{"ideas": [{"id": "i1", "scores": {"overall": 0.5}}]}]}},
                "calibrated_confidences": {},
                "metacognitive_report": {"readiness_score": float(len(calls) * 10)},
            }

        monkeypatch.setattr(type(orch), "scientific_discovery_pipeline", fake_pipeline)

        orch.run_scientific_discovery_loop("dominio", max_iterations=3, stagnation_threshold=0.001)

        assert calls == [3, 4, 5]
