# -*- coding: utf-8 -*-
"""
Testes TDD — SPEC-917: Evolução dos Motores de Raciocínio
=========================================================

RED → GREEN → REFACTOR:
- Estes testes especificam o comportamento esperado da evolução dos
  raciocínios antes da finalização/refatoração da implementação.
- Cobrem segurança (sem execução dinâmica), 12 motores, cache, visualização, paralelismo
  e avaliação de qualidade.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


EXPECTED_ENGINES = {
    "z3",
    "sympy",
    "kanren",
    "critical",
    "bayesian",
    "causal",
    "temporal",
    "fuzzy",
    "chain_of_thought",
    "analogical",
    "counterfactual",
    "quantum",
}


class TestSpec917Safety:
    def test_reasoning_engines_do_not_use_eval(self):
        source = Path("reasoning/engines.py").read_text(encoding="utf-8")
        assert "eval(" not in source
        assert "# noqa: S307" not in source


class TestSpec917Engines:
    def test_expected_engines_are_registered(self):
        from reasoning import multi_reasoning

        assert set(multi_reasoning.engines.keys()) == EXPECTED_ENGINES
        assert len(multi_reasoning.available_engines) >= 9

    def test_auto_routing_expanded(self):
        from reasoning import MultiReasoningEngine

        assert MultiReasoningEngine._route("resolver equação x=2") == "sympy"
        assert MultiReasoningEngine._route("verificar restrição sat") == "z3"
        assert MultiReasoningEngine._route("qual a probabilidade pelo teorema de Bayes?") == "bayesian"
        assert MultiReasoningEngine._route("isso causa aquele efeito?") == "causal"
        assert MultiReasoningEngine._route("ordenar cronologia antes e depois") == "temporal"
        assert MultiReasoningEngine._route("raciocinar passo a passo") == "chain_of_thought"
        assert MultiReasoningEngine._route("e se outro cenário tivesse ocorrido?") == "counterfactual"
        assert MultiReasoningEngine._route("simular emaranhamento quântico de qubits") == "quantum"

    def test_bayesian_engine_computes_posterior_from_error_rates(self):
        from reasoning import BayesianEngine

        result = BayesianEngine().reason(
            "teste raro com falso positivo",
            prior=0.01,
            likelihood=0.99,
            evidence=0.0,
            false_positive_rate=0.10,
        )

        assert result.engine == "bayesian"
        assert "P(hipótese | evidência)" in result.conclusion
        assert any("Posterior" in step for step in result.steps)
        assert result.confidence > 0.5

    def test_causal_engine_distinguishes_correlation_from_causality(self):
        from reasoning import CausalEngine

        result = CausalEngine().reason(
            "causa provável com temporalidade e gradiente",
            cause="exposição X",
            effect="desfecho Y",
            hill_criteria={
                "força": True,
                "consistência": True,
                "temporalidade": True,
                "gradiente": True,
                "plausibilidade": True,
                "coerência": True,
                "experimental": True,
            },
        )

        assert "provavelmente causal" in result.conclusion
        assert any("Bradford" in step or "Escada da Causalidade" in step for step in result.steps)

    def test_temporal_engine_orders_events(self):
        from reasoning import TemporalEngine

        result = TemporalEngine().reason(
            "ordenar linha do tempo",
            events=[
                {"nome": "C", "tempo": 3},
                {"nome": "A", "tempo": 1},
                {"nome": "B", "tempo": 2},
            ],
        )

        assert "Primeiro: 'A'" in result.conclusion
        assert "Último: 'C'" in result.conclusion
        assert "Sem ciclos" in result.conclusion

    def test_fuzzy_engine_handles_linguistic_terms(self):
        from reasoning import FuzzyReasoningEngine

        result = FuzzyReasoningEngine().reason(
            "avaliação difusa",
            propositions=[
                {"texto": "qualidade", "termo": "alto", "peso": 1.0},
                {"texto": "risco", "termo": "médio", "peso": 1.0},
            ],
            operator="average",
        )

        assert "Valor fuzzy agregado" in result.conclusion
        assert result.confidence >= 0.7

    def test_chain_of_thought_decomposes_query(self):
        from reasoning import ChainOfThoughtEngine

        result = ChainOfThoughtEngine().reason("analisar problema complexo")
        joined = "\n".join(result.steps)

        assert "CADEIA DE PENSAMENTO" in joined
        assert "Passo 1" in joined
        assert "passos de raciocínio" in result.conclusion

    def test_analogical_engine_maps_structural_correspondences(self):
        from reasoning import AnalogicalEngine

        result = AnalogicalEngine().reason(
            "analogia entre sistema nervoso e rede neural",
            source="sistema nervoso",
            target="rede neural",
            source_attrs=["neurônio transmite sinal", "sinapse ajusta peso"],
            target_attrs=["nó transmite sinal", "peso ajusta conexão"],
        )

        assert "Analogia estrutural" in result.conclusion
        assert result.confidence >= 0.5

    def test_counterfactual_engine_builds_alternative_world(self):
        from reasoning import CounterfactualEngine

        result = CounterfactualEngine().reason(
            "e se a decisão tivesse sido diferente?",
            fact="decisão A ocorreu",
            alternative="decisão B ocorreu",
            antecedents=["premissa 1 alterada", "premissa 2 alterada"],
        )

        assert "MUNDO CONTRAFACTUAL" in "\n".join(result.steps)
        assert "distância" in result.conclusion
        assert result.confidence > 0.3

    def test_quantum_reasoning_engine_wraps_quantum_suite(self):
        from reasoning import QuantumReasoningEngine

        result = QuantumReasoningEngine().reason(
            "simular estado quântico Bell",
            n_qubits=2,
            shots=64,
        )

        assert result.engine == "quantum"
        assert "experimentos quânticos" in result.conclusion
        assert any("bell" in step.lower() for step in result.steps)


class TestSpec917Infrastructure:
    def test_top_level_exports_infrastructure_components(self):
        from reasoning import ParallelReasoning, ReasoningEvaluator, ReasoningVisualizer

        assert ReasoningVisualizer is not None
        assert ParallelReasoning is not None
        assert ReasoningEvaluator is not None

    def test_reasoning_cache_lru_hit_ratio(self):
        from reasoning.cache import ReasoningCache

        cache = ReasoningCache(max_size=2, default_ttl=60)
        key = cache.make_key("consulta", "critical")
        cache.set(key, {"engine": "critical", "confidence": 0.7}, engine="critical")

        assert cache.get(key)["engine"] == "critical"
        assert cache.get(key)["confidence"] == 0.7
        assert cache.stats["hit_ratio"] >= 0.5

    def test_reasoning_visualizer_generates_mermaid(self):
        from reasoning.visualizer import ReasoningVisualizer

        mermaid = ReasoningVisualizer().chain_to_mermaid(
            query="teste visual",
            steps=["premissa", "inferência", "conclusão"],
            engine="critical",
        )

        assert mermaid.startswith("flowchart TD")
        assert "premissa" in mermaid
        assert "conclusão" in mermaid

    def test_parallel_reasoning_runs_ensemble(self):
        from reasoning.parallel import ParallelReasoning

        from reasoning import MultiReasoningEngine

        result = ParallelReasoning(MultiReasoningEngine()).ensemble("analisar criticamente")

        assert result["query"] == "analisar criticamente"
        assert "results" in result
        assert result["best_engine"] in EXPECTED_ENGINES

    def test_parallel_reasoning_has_speedup_on_slow_fake_engines(self):
        from reasoning.parallel import ParallelReasoning

        class FakeResult:
            def __init__(self, engine):
                self.engine = engine

            def to_dict(self):
                return {"engine": self.engine, "confidence": 0.5, "steps": ["ok"]}

        class SlowEngine:
            def __init__(self, name):
                self.name = name

            def reason(self, query):
                time.sleep(0.05)
                return FakeResult(self.name)

        class FakeMulti:
            engines = {f"e{i}": SlowEngine(f"e{i}") for i in range(4)}

        started = time.time()
        for engine in FakeMulti.engines.values():
            engine.reason("q")
        sequential = time.time() - started

        started = time.time()
        result = ParallelReasoning(FakeMulti(), max_workers=4).ensemble("q")
        parallel = time.time() - started

        assert result["mode"] == "parallel"
        assert sequential / parallel > 1.5

    def test_reasoning_evaluator_scores_result(self):
        from reasoning import ReasoningResult
        from reasoning.evaluator import ReasoningEvaluator

        score = ReasoningEvaluator().evaluate(
            ReasoningResult(
                engine="critical",
                query="teste",
                conclusion="conclusão consistente",
                confidence=0.8,
                steps=["premissa", "inferência", "síntese"],
            )
        )

        assert 0 <= score["overall"] <= 1
        assert score["coherence"] > 0
        assert score["coverage"] > 0
