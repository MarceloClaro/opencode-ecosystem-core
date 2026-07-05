# -*- coding: utf-8 -*-
"""
Demo Full Ecosystem — Demonstração end-to-end do ecossistema completo
=====================================================================
Exercita todos os subsistemas integrados ao orquestrador marceloclaro:
catálogo de 128+ agentes, Trust Engine, Token Economy, Scanners,
MASWOS Qualis A1, motores de raciocínio, módulo quântico, ciclos
evolutivos e integrações CLI.

Uso: python3 examples/demo_full_ecosystem.py
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.WARNING)

from marceloclaro.orchestrator import MarceloClaroOrchestrator


def main():
    print("=" * 70)
    print("OPENCODE ECOSYSTEM CORE — DEMONSTRAÇÃO COMPLETA")
    print("=" * 70)

    orch = MarceloClaroOrchestrator()

    # 1. Status geral do ecossistema
    st = orch.status()
    print(f"\n[1] ECOSSISTEMA INICIALIZADO")
    print(f"    Agentes registrados: {len(st['agents'])} "
          f"(catálogo especializado: {st['catalog_agents']})")
    print(f"    Motores de raciocínio: {st['reasoning_engines']}")
    print(f"    Trust Engine ativo: {list(st['trust'].keys())[:4]}")

    # 2. Delegação com Trust Gate + Token Economy + Attention Routing
    print(f"\n[2] DELEGAÇÃO METACOGNITIVA (trust gate + staking + atenção)")
    task_id = orch.delegate(
        "Revisar a arquitetura de segurança do módulo de autenticação",
        required_capabilities=["code_review"],
    )
    task = None
    from mci.blackboard import blackboard
    task = blackboard.tasks.get(task_id)
    assigned = getattr(task, "assigned_to", "?")
    print(f"    Tarefa {task_id} atribuída a: {assigned}")
    orch.report_completion(task_id, assigned, "Revisão concluída: 3 achados corrigidos.")
    eco = orch.economy.report()
    print(f"    Economia pós-tarefa: {eco['transactions']} transações, "
          f"stakes: {eco['stakes']}")

    # 3. Diagnóstico com os 5 scanners
    print(f"\n[3] PIPELINE DE DIAGNÓSTICO (5 scanners)")
    diag = orch.diagnose(
        "Este ecossistema aplica machine learning com validação estatística, "
        "metodologia reprodutível e testes automatizados para orquestração multiagente.",
        domain="multi_agent_systems",
        goals=[{"name": "qualidade", "description": "avaliar rigor do ecossistema",
                "goal_type": "evaluative"}],
    )
    print(f"    Lacunas totais: {diag['evolutionary']['total_gaps']}")
    print(f"    Recomendação: {diag['evolutionary']['recommendation']}")

    # 4. Pipeline acadêmico MASWOS Qualis A1
    print(f"\n[4] PIPELINE ACADÊMICO MASWOS (Qualis A1)")
    academic = orch.academic_pipeline(
        "Orquestração metacognitiva de sistemas multiagentes",
        manuscript="Introdução com metodologia, hipótese e objetivo. DOI 10.1000/x, "
                   "et al. Abstract, keywords, figura 1, tabela 2, p-valor 0.03, ANOVA, "
                   "intervalo de confiança, amostra, protocolo reprodutível, conclusão. "
                   "ABNT referências p. 10. Contribuição original preenche lacuna teórica.",
        stages=["diagnostico_escopo", "estatistica", "qa_qualis_a1"],
    )
    print(f"    Estágios: {academic['stages_completed']}/{academic['stages_total']}")
    print(f"    Nota AUTO_SCORE: {academic['final_score']}/10 "
          f"({'APROVADO' if academic['approved'] else 'reprovado'})")

    # 5. Motores de raciocínio
    print(f"\n[5] MOTORES DE RACIOCÍNIO")
    r1 = orch.reason("resolver x + 2 = 10", engine="sympy", expression="x + 2 = 10")
    print(f"    SymPy: {r1['conclusion']}")
    r2 = orch.reason("verificar restrições", engine="z3", constraints=["x > 3", "x < 10"])
    print(f"    Z3: {r2['conclusion']}")
    r3 = orch.reason("essa arquitetura sempre garante consistência", engine="critical")
    print(f"    Critical: confiança {r3['confidence']}")

    # 6. Módulo quântico
    print(f"\n[6] MÓDULO QUÂNTICO (suite reprodutível, 5 seeds)")
    q = orch.quantum_experiment(n_qubits=3, shots=512)
    for name, exp in q["experiments"].items():
        print(f"    {name}: melhor seed {exp['best_seed']}, pior seed {exp['worst_seed']}")

    # 7. Ciclo evolutivo
    print(f"\n[7] CICLO EVOLUTIVO")
    evo = orch.record_evolution(
        objective="Integrar componentes avançados do OpenCode_Ecosystem ao Core",
        changes=["Trust Engine", "Token Economy", "5 Scanners", "MASWOS",
                 "4 motores de raciocínio", "módulo quântico", "OpenCode CLI"],
        score=9.5,
        lessons=["A integração via singletons preserva o Global Workspace único.",
                 "Gates comportamentais devem ter fallback para não órfanar tarefas."],
    )
    print(f"    Registrado: {evo['round_id']} (score {evo['score']}, média {evo['avg_score']})")

    # 8. Integração externa (Antigravity)
    print(f"\n[8] INTEGRAÇÃO EXTERNA (Antigravity CLI)")
    ext = orch.delegate_external("Gerar diagrama da arquitetura", agent="image")
    print(f"    Status: {ext['status']}" +
          (f" ({ext.get('reason', '')})" if ext['status'] == 'queued' else ""))

    # 9. Memória metacognitiva final
    print(f"\n[9] MEMÓRIA METACOGNITIVA GLOBAL")
    final = orch.status()
    print(f"    Reflexões na memória episódica: {final['episodic_memory_size']}")
    print(f"    Score evolutivo médio: {final['evolution_avg_score']}")

    print("\n" + "=" * 70)
    print("DEMONSTRAÇÃO COMPLETA CONCLUÍDA COM SUCESSO")
    print("=" * 70)


if __name__ == "__main__":
    main()
