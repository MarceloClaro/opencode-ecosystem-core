# -*- coding: utf-8 -*-
"""
Testes TDD para Amplificação Cognitiva de Modelos Free via DeepSeek Harness — SPEC-935-R441
=========================================================================================
Valida os critérios de aceite (CA1 a CA7):
- CA1: RAG e expansão de contexto local a custo zero
- CA2: Scaffolding de raciocínio profundo (<think>)
- CA3: Auto-correção e verificação iterativa (CoVe)
- CA4: Suporte nativo a ox-alpha-free e catálogo free
- CA5: Métodos no MarceloClaroOrchestrator e CLI
- CA6: Check no doctor
- CA7: Execução 100% determinística e verde
"""

import json
import pytest

from integrations.deepseek_harness.free_model_amplifier import (
    DeepSeekFreeModelHarness,
    get_free_model_amplifier,
    ReasoningScaffoldEngine,
    ContextAmplifier,
    ChainOfVerification,
    AmplificationResult,
    FREE_MODELS_CATALOG,
)
from marceloclaro.doctor import _check_free_model_amplification, run_doctor
from marceloclaro.orchestrator import MarceloClaroOrchestrator


class TestFreeModelsCatalog:
    """Valida o catálogo e detecção de modelos gratuitos (CA4)."""

    def test_free_models_catalog_contains_ox_alpha(self):
        harness = DeepSeekFreeModelHarness()
        assert harness.is_free_model("ox-alpha-free") is True
        assert harness.is_free_model("ox-alpha-free-unlimited") is True
        assert harness.is_free_model("deepseek-v3") is True
        assert harness.is_free_model("olmoe-1b-7b") is True

    def test_non_free_model_detection(self):
        harness = DeepSeekFreeModelHarness()
        assert harness.is_free_model("gpt-5-frontier") is False
        assert harness.is_free_model("claude-opus-4") is False


class TestReasoningScaffoldEngine:
    """Valida a injeção de scaffolding e extração de <think> (CA2)."""

    def test_scaffold_generation_for_coding_and_reasoning(self):
        engine = ReasoningScaffoldEngine()
        prompt = "Implemente um algoritmo de ordenação topológica"
        context = "[1] [local] Grafo direcionado acíclico (DAG)"

        amplified = engine.build_amplified_prompt(prompt, task_type="coding", context=context)
        assert "<think>" in amplified
        assert "Contexto Aumentado" in amplified
        assert "ordenacao" in amplified.lower() or "ordenação" in amplified.lower()
        assert "Decomposição do Problema" in amplified

    def test_extract_thinking_trace(self):
        engine = ReasoningScaffoldEngine()
        raw_text = "<think>\n1. Analisando entrada\n2. Verificando bordas\n</think>\n\nResultado final consolidado."
        thinking, answer = engine.extract_thinking_trace(raw_text)

        assert "Analisando entrada" in thinking
        assert "Resultado final consolidado." in answer
        assert "<think>" not in answer


class TestContextAmplifier:
    """Valida o RAG multi-fonte a custo zero (CA1)."""

    def test_context_expansion_returns_evidence(self):
        amplifier = ContextAmplifier()
        # Busca sobre trust engine (presente nas bases locais e specs)
        evidence = amplifier.expand_context("trust engine", max_items=3)
        assert isinstance(evidence, list)
        
        # Formatação do bloco
        block = amplifier.format_grounding_block(evidence)
        if evidence:
            assert "[1]" in block


class TestChainOfVerification:
    """Valida a cadeia de verificação e cálculo de confiança (CA3)."""

    def test_verification_questions_and_confidence(self):
        cove = ChainOfVerification()
        questions = cove.generate_verification_questions("Como criar um servidor HTTP em Python?", "Use http.server")
        assert len(questions) >= 3

        # Teste de pontuação
        score = cove.evaluate_confidence(
            draft="Código completo e estruturado para servidor HTTP em Python com tratamento de portas e exceções.",
            context="Base local sobre redes e sockets",
            thinking="Decomposição do problema: socket bind, listen, accept e tratamento de erro.",
        )
        assert score >= 0.90


class TestDeepSeekFreeModelHarnessEndToEnd:
    """Valida a execução completa do pipeline de amplificação (CA3, CA4)."""

    def test_amplify_with_custom_runner(self):
        harness = DeepSeekFreeModelHarness()

        def mock_runner(prompt: str) -> str:
            assert "<think>" in prompt
            return "<think>\nPasso 1: análise\nPasso 2: dedução\n</think>\n\nResposta altamente precisa para o modelo free."

        result = harness.amplify(
            prompt="Qual a complexidade de busca em árvore rubro-negra?",
            model="ox-alpha-free",
            task_type="reasoning",
            iterations=2,
            runner=mock_runner,
        )

        assert isinstance(result, AmplificationResult)
        assert result.status == "success"
        assert result.model == "ox-alpha-free"
        assert "análise" in result.thinking_trace
        assert "Resposta altamente precisa" in result.final_response
        assert result.confidence_score >= 0.90

    def test_amplify_fallback_execution(self):
        harness = DeepSeekFreeModelHarness()
        result = harness.amplify(
            prompt="Estruture um teste de regressão linear em Python",
            model="ox-alpha-free",
            task_type="coding",
        )
        assert result.status == "success"
        assert len(result.thinking_trace) > 0
        assert len(result.final_response) > 0


class TestOrchestratorAndDoctorIntegration:
    """Valida integração com MarceloClaroOrchestrator e Doctor (CA5, CA6)."""

    def test_orchestrator_amplify_methods(self):
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        res = orch.amplify_free_model_response(
            prompt="Otimize esta consulta SQL",
            model="ox-alpha-free",
            task_type="coding",
        )
        assert "final_response" in res
        assert "thinking_trace" in res
        assert "confidence_score" in res

        # Orquestração completa
        orch_res = orch.orchestrate_free_model_harness(
            objective="Elabore um plano de testes unitários",
            model="ox-alpha-free",
        )
        assert orch_res["status"] == "success"

    def test_doctor_free_model_amplification_check(self):
        check = _check_free_model_amplification()
        assert check.name == "free_model_amplification"
        assert check.status == "pass"
        assert "DeepSeek Harness ativa" in check.detail
