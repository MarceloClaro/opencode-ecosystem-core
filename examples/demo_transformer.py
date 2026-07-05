# -*- coding: utf-8 -*-
"""
Demo da Camada Transformer — OpenCode Ecosystem Core
====================================================
Demonstra os quatro componentes Transformer-inspirados:
1. AttentionRouter (Multi-Head Attention para roteamento de tarefas)
2. TransformerPipeline (gerar → verificar → revisar, padrão Aletheia)
3. GradingHead (avaliação 0-7, padrão IMO-GradingBench)
4. HierarchicalMemory (recuperação em 2 níveis, padrão HTM)

Execução:
    python3 examples/demo_transformer.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marceloclaro.orchestrator import MarceloClaroOrchestrator


def main():
    print("=" * 64)
    print("DEMO TRANSFORMER — OpenCode Ecosystem Core / marceloclaro")
    print("=" * 64)

    orch = MarceloClaroOrchestrator()

    # ------------------------------------------------------------------
    # 1. Roteamento por Multi-Head Attention (com auditoria transparente)
    # ------------------------------------------------------------------
    print("\n[1] AUDITORIA DE ROTEAMENTO (4 cabeças de atenção)")
    explanation = orch.explain_routing(
        "Redigir manuscrito acadêmico sobre atenção multi-cabeça",
        ["academic_writing"],
    )
    print("    Ranking softmax (tarefa acadêmica):")
    for agent_id, weight in explanation["ranking"]:
        print(f"      {agent_id:<18} peso de atenção = {weight:.3f}")

    # ------------------------------------------------------------------
    # 2. Delegação real: a atenção escolhe o agente certo
    # ------------------------------------------------------------------
    print("\n[2] DELEGAÇÃO VIA ATENÇÃO")
    t1 = orch.delegate("Auditar integrações do ecossistema", ["audit"])
    t2 = orch.delegate("Escrever artigo IMRAD sobre metacognição", ["academic_writing"])
    from mci.blackboard import blackboard
    print(f"    {t1} -> {blackboard.tasks[t1].assigned_to}")
    print(f"    {t2} -> {blackboard.tasks[t2].assigned_to}")

    # ------------------------------------------------------------------
    # 3. Pipeline gerar → verificar → revisar (Aletheia + GradingBench)
    # ------------------------------------------------------------------
    print("\n[3] PIPELINE GERAR → VERIFICAR → REVISAR")
    attempts = {"n": 0}

    def simulated_executor(prompt, context):
        """Simula um agente que melhora após receber feedback de revisão."""
        attempts["n"] += 1
        if attempts["n"] == 1:
            return "rascunho inicial"  # fraco de propósito
        return ("O manuscrito sobre metacognição em sistemas multiagentes foi "
                "redigido com estrutura IMRAD completa, citações rastreáveis e "
                "análise rigorosa, conforme os requisitos da tarefa.")

    result = orch.run_pipeline(
        "redigir manuscrito sobre metacognição em sistemas multiagentes",
        simulated_executor,
    )
    for rev in result["revisions"]:
        print(f"    Camada {rev['layer']}: nota {rev['grade']['score']}/7 "
              f"({'aprovado' if rev['grade']['passed'] else 'revisar'})")
    print(f"    Resultado final: nota {result['final_grade']['score']}/7 "
          f"em {result['layers_used']} camada(s)")

    # ------------------------------------------------------------------
    # 4. Memória hierárquica (HTM): recuperação em 2 níveis
    # ------------------------------------------------------------------
    print("\n[4] RECUPERAÇÃO HIERÁRQUICA (HTM)")
    orch.report_completion(t1, "auditor", "Auditoria concluída sem falhas críticas", True)
    orch.report_completion(t2, "academic_writer", "Artigo IMRAD entregue e aprovado", True)

    memories = orch.recall("manuscrito metacognição", top_entries=3)
    for m in memories:
        print(f"    relevância={m['relevance']:.3f} | {m['agent_id']}: {m['context'][:60]}")

    print("\n[5] ESTADO FINAL (confidence ledger)")
    print(json.dumps(orch.status()["confidence_ledger"], indent=2, ensure_ascii=False))

    print("\nDemo concluída: atenção, pipeline, grading e memória hierárquica operando em conjunto.")


if __name__ == "__main__":
    main()
