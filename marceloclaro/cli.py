# -*- coding: utf-8 -*-
"""
CLI do Orquestrador MarceloClaro
================================
Menu interativo de terminal para operar o ecossistema.

Uso:
    python3 -m marceloclaro.cli          # menu interativo
    python3 -m marceloclaro.cli status   # comando direto

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import sys
import json

from marceloclaro.orchestrator import MarceloClaroOrchestrator

BANNER = r"""
==============================================================
   OPENCODE ECOSYSTEM CORE — Orquestrador MARCELOCLARO
   Metacognição distribuída: MetaBus + Blackboard + Reflexion
==============================================================
"""

MENU = """
[1] Listar agentes registrados (Agent Cards)
[2] Postar tarefa no Blackboard
[3] Reportar conclusão de tarefa
[4] Consultar memória metacognitiva (Global Workspace)
[5] Status geral do ecossistema
[6] Diagnóstico de saúde do ecossistema (doctor)
[0] Sair
"""


def main():
    orchestrator = MarceloClaroOrchestrator()

    # Modo comando direto
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            print(json.dumps(orchestrator.status(), indent=2, ensure_ascii=False))
        elif cmd == "agents":
            print(json.dumps(orchestrator.list_agents(), indent=2, ensure_ascii=False))
        elif cmd == "doctor":
            report = orchestrator.doctor()
            print(json.dumps(report, indent=2, ensure_ascii=False))
            sys.exit(0 if report["overall"] != "unhealthy" else 1)
        else:
            print(f"Comando desconhecido: {cmd}. Use 'status', 'agents' ou 'doctor'.")
        return

    # Modo interativo
    print(BANNER)
    while True:
        print(MENU)
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            print(json.dumps(orchestrator.list_agents(), indent=2, ensure_ascii=False))

        elif choice == "2":
            desc = input("Descrição da tarefa: ").strip()
            caps = input("Capacidades requeridas (separadas por vírgula, vazio = qualquer): ").strip()
            cap_list = [c.strip() for c in caps.split(",") if c.strip()]
            task_id = orchestrator.delegate(desc, cap_list)
            print(f"Tarefa postada: {task_id}")

        elif choice == "3":
            task_id = input("ID da tarefa: ").strip()
            agent_id = input("ID do agente executor: ").strip()
            result = input("Resultado (texto): ").strip()
            success = input("Sucesso? (s/n): ").strip().lower() != "n"
            orchestrator.report_completion(task_id, agent_id, result, success)
            print("Conclusão reportada. Reflexão metacognitiva disparada.")

        elif choice == "4":
            awareness = orchestrator.perceive()
            print(json.dumps(awareness, indent=2, ensure_ascii=False))

        elif choice == "5":
            print(json.dumps(orchestrator.status(), indent=2, ensure_ascii=False))

        elif choice == "6":
            print(json.dumps(orchestrator.doctor(), indent=2, ensure_ascii=False))

        elif choice == "0":
            print("Encerrando o orquestrador. Até logo.")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
