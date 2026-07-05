# -*- coding: utf-8 -*-
"""
Testes da camada Transformer (embedder, atenção, pipeline, memória hierárquica).

Execução:
    pytest tests/test_transformer.py -v
"""

import os
import sys
import tempfile

os.environ.setdefault("MCI_STATE_DIR", tempfile.mkdtemp(prefix="mci_test_tf_"))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformer.embedder import TaskEmbedder, D_MODEL  # noqa: E402
from transformer.attention import AttentionRouter  # noqa: E402
from transformer.pipeline import TransformerPipeline, GradingHead, MAX_SCORE  # noqa: E402
from transformer.memory import HierarchicalMemory  # noqa: E402
from mci.metabus import metabus  # noqa: E402
from marceloclaro.orchestrator import MarceloClaroOrchestrator  # noqa: E402
from mci.blackboard import blackboard  # noqa: E402


def test_embedder_determinism_and_norm():
    emb = TaskEmbedder()
    v1 = emb.embed_text("pesquisar literatura acadêmica")
    v2 = emb.embed_text("pesquisar literatura acadêmica")
    assert v1 == v2, "Embedding deve ser determinístico"
    assert len(v1) == D_MODEL
    norm = sum(x * x for x in v1) ** 0.5
    assert abs(norm - 1.0) < 1e-6, "Embedding deve ser L2-normalizado"


def test_attention_routes_by_capability():
    router = AttentionRouter()
    cards = [
        {"agent_id": "researcher", "name": "Researcher",
         "description": "pesquisa e síntese", "capabilities": ["search", "cite"],
         "status": "available", "confidence_score": 0.5},
        {"agent_id": "coder", "name": "Coder",
         "description": "implementação de código", "capabilities": ["python", "debug"],
         "status": "available", "confidence_score": 0.5},
    ]
    ranking = router.route("Levantar literatura científica", ["search"], cards)
    assert ranking[0][0] == "researcher"
    # Pesos softmax somam 1
    assert abs(sum(w for _, w in ranking) - 1.0) < 1e-6


def test_attention_penalizes_busy_agents():
    router = AttentionRouter()
    cards = [
        {"agent_id": "a1", "name": "A1", "description": "genérico",
         "capabilities": ["x"], "status": "busy", "confidence_score": 0.9},
        {"agent_id": "a2", "name": "A2", "description": "genérico",
         "capabilities": ["x"], "status": "available", "confidence_score": 0.5},
    ]
    ranking = router.route("tarefa qualquer", ["x"], cards)
    assert ranking[0][0] == "a2", "Agente disponível deve vencer o ocupado"


def test_grading_head_scale():
    head = GradingHead()
    empty = head.grade("qualquer tarefa", "")
    assert empty["score"] == 0 and not empty["passed"]
    good = head.grade(
        "implementar parser YAML em python",
        "O parser YAML foi implementado em python com testes completos e "
        "cobertura integral, incluindo tratamento de erros do parser.",
    )
    assert 0 < good["score"] <= MAX_SCORE
    assert good["passed"]


def test_pipeline_generate_verify_revise():
    """O executor melhora a cada revisão: o pipeline deve convergir (Aletheia)."""
    attempts = {"n": 0}

    def executor(prompt, context):
        attempts["n"] += 1
        if attempts["n"] == 1:
            return "ok"  # saída fraca -> nota baixa -> revisão
        return ("O parser YAML foi implementado em python com testes e "
                "validação completa do parser conforme solicitado na tarefa.")

    pipeline = TransformerPipeline(num_layers=3)
    result = pipeline.run("implementar parser YAML em python", executor)
    assert result["final_grade"]["passed"]
    assert result["layers_used"] >= 2, "Deve ter havido pelo menos uma revisão"


def test_hierarchical_memory_retrieve():
    metabus.memory.add_reflection("researcher", "busca de artigos sobre atenção",
                                  "usar bases indexadas primeiro", 0.9)
    metabus.memory.add_reflection("coder", "correção de bug no parser yaml",
                                  "adicionar testes de regressão", 0.8)
    hmem = HierarchicalMemory(metabus.memory)
    results = hmem.retrieve("bug no parser yaml", top_entries=2)
    assert results, "Deve recuperar entradas"
    assert results[0]["agent_id"] == "coder", "Entrada mais relevante deve vir primeiro"


def test_orchestrator_full_transformer_cycle():
    orch = MarceloClaroOrchestrator(auto_load_agents=True)

    # Roteamento via atenção mantém o comportamento esperado
    task_id = orch.delegate("Pesquisar padrões de atenção", required_capabilities=["search"])
    assert blackboard.tasks[task_id].assigned_to == "researcher"

    # Pipeline gerar→verificar→revisar registrado na memória global
    result = orch.run_pipeline(
        "redigir resumo sobre atenção multi-cabeça",
        lambda p, c: ("O resumo sobre atenção multi-cabeça foi redigido com rigor, "
                      "explicando query, key e value conforme a tarefa."),
    )
    assert result["final_grade"]["passed"]

    # Auditoria de roteamento expõe as 4 cabeças
    explanation = orch.explain_routing("Pesquisar padrões", ["search"])
    assert set(explanation["heads"].keys()) == {"semantic", "capability", "confidence", "load"}

    # Recuperação hierárquica encontra a experiência do pipeline
    recall = orch.recall("resumo atenção multi-cabeça")
    assert recall
