# -*- coding: utf-8 -*-
"""
Demo SDD/TDD — OpenCode Ecosystem Core
======================================
Demonstra as metodologias aplicadas a todos os componentes:

1. SDD (Specification-Driven Development): especificação ANTES da execução,
   com critérios de aceitação verificáveis e gate de verificação na conclusão.
2. TDD (Test-Driven Development): ciclo RED -> GREEN -> REFACTOR com
   reversão automática de refatorações que quebram critérios.
3. Auditoria de cobertura: specs formais SPEC-001..006 vinculadas a testes.

Execução:
    python3 examples/demo_sdd_tdd.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marceloclaro.orchestrator import MarceloClaroOrchestrator
from mci.blackboard import blackboard


def main():
    print("=" * 64)
    print("DEMO SDD/TDD — OpenCode Ecosystem Core / marceloclaro")
    print("=" * 64)

    # Modo SDD estrito: nenhuma entrega aceita sem passar na especificação
    orch = MarceloClaroOrchestrator(strict_sdd=True)

    # ------------------------------------------------------------------
    # 1. Auditoria de cobertura SDD (specs formais carregadas de specs/)
    # ------------------------------------------------------------------
    print("\n[1] COBERTURA SDD (especificações formais)")
    report = orch.audit_specs()
    for spec in report["formal"]:
        print(f"    {spec['spec_id']:<10} {spec['component']:<26} -> {spec['test_file']}")

    # ------------------------------------------------------------------
    # 2. Delegação SDD-first: a spec nasce ANTES da tarefa (fase RED)
    # ------------------------------------------------------------------
    print("\n[2] DELEGAÇÃO SDD-FIRST (spec antes da execução)")
    handle = orch.delegate_with_spec(
        "Redigir seção de metodologia com rigor acadêmico",
        required_capabilities=["academic_writing"],
        acceptance_criteria=["A entrega não pode ser vazia."],
    )
    task_id, spec_id = handle["task_id"], handle["spec_id"]
    agent = blackboard.tasks[task_id].assigned_to
    print(f"    Tarefa {task_id} vinculada à spec {spec_id} (RED)")
    print(f"    Contrato injetado no contexto do agente: {agent}")

    # Entrega VAZIA: o gate SDD estrito reprova e registra falha
    orch.report_completion(task_id, agent, "", True)
    print(f"    Entrega vazia -> status: {blackboard.tasks[task_id].status} (gate SDD reprovou)")

    # Nova tarefa com entrega válida: gate aprova
    handle2 = orch.delegate_with_spec(
        "Redigir seção de metodologia revisada",
        required_capabilities=["academic_writing"],
        acceptance_criteria=["A entrega não pode ser vazia."],
    )
    t2, s2 = handle2["task_id"], handle2["spec_id"]
    a2 = blackboard.tasks[t2].assigned_to
    orch.report_completion(t2, a2, "Metodologia redigida com desenho experimental e análise.", True)
    print(f"    Entrega válida -> status: {blackboard.tasks[t2].status} (spec {s2}: GREEN)")

    # ------------------------------------------------------------------
    # 3. Ciclo TDD completo: RED -> GREEN -> REFACTOR
    # ------------------------------------------------------------------
    print("\n[3] CICLO TDD (RED -> GREEN -> REFACTOR)")
    attempts = {"n": 0}

    def producer(objective, feedback):
        """Produtor que falha na 1ª iteração e corrige na 2ª (TDD real)."""
        attempts["n"] += 1
        if attempts["n"] == 1:
            return "rascunho"  # não satisfaz o critério de 80+ caracteres
        return ("Resumo executivo do ecossistema com arquitetura Transformer, "
                "camada MCI e protocolo SDD/TDD aplicado a todos os agentes.")

    result = orch.run_tdd_cycle(
        "produzir resumo executivo com no mínimo 80 caracteres",
        producer,
        acceptance_criteria=[
            ("Entrega possui >= 80 caracteres",
             lambda out: isinstance(out, str) and len(out) >= 80),
            ("Menciona SDD/TDD",
             lambda out: isinstance(out, str) and "SDD" in out),
        ],
        refactor_fn=lambda out, ctx: out.strip(),  # refatoração segura
    )
    for step in result["history"]:
        v = step["verification"]
        print(f"    [{step['phase'].upper():<8}] {v['passed_count']}/{v['total_count']} critérios")
    print(f"    Resultado: fase final = {result['phase']} | sucesso = {result['success']}")

    # ------------------------------------------------------------------
    # 4. Bateria pytest real (metacognição de qualidade de código)
    # ------------------------------------------------------------------
    print("\n[4] BATERIA DE TESTES REAL (pytest)")
    outcome = orch.run_test_suite()
    print(f"    {outcome['summary']} | all_passed = {outcome['all_passed']}")

    # ------------------------------------------------------------------
    # 5. Estado global com métricas SDD
    # ------------------------------------------------------------------
    print("\n[5] ESTADO GLOBAL (auditoria)")
    status = orch.status()
    print(json.dumps(status["sdd"], indent=2, ensure_ascii=False))

    print("\nDemo concluída: SDD e TDD ativos em todos os componentes e agentes.")


if __name__ == "__main__":
    main()
