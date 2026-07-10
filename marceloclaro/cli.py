# -*- coding: utf-8 -*-
"""
CLI do Orquestrador MarceloClaro
================================
Menu interativo de terminal para operar o ecossistema.

Uso:
    python3 -m marceloclaro.cli          # menu interativo
    python3 -m marceloclaro.cli status   # comando direto
    python3 -m marceloclaro.cli ajuda    # resumo de ajuda

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
[7] Ajuda / Manual
[8] Helpdesk (diagnóstico + sugestões em linguagem simples)
[0] Sair
"""

AJUDA_TEXT = """
O que cada opção faz, em termos simples:

[1] Agentes registrados — lista quem já está disponível para receber tarefas
    (cada "agente" é uma especialidade: pesquisador, revisor, escritor...).
[2] Postar tarefa — descreve um trabalho e o sistema escolhe automaticamente
    o agente mais adequado para fazê-lo (o "Blackboard" é o quadro de
    tarefas onde os agentes se candidatam).
[3] Reportar conclusão — informa que um agente terminou uma tarefa (sucesso
    ou falha); isso ensina o sistema a confiar mais ou menos nesse agente.
[4] Consultar memória — mostra o que o sistema já aprendeu/lembra de
    execuções anteriores (a "memória metacognitiva" é a memória compartilhada
    de todo o ecossistema, não de um agente só).
[5] Status geral — uma foto completa do estado atual: agentes, confiança,
    economia de tokens, etc.
[6] Doctor — verifica rapidamente (poucos segundos) se tudo está saudável:
    arquivos de configuração, histórico de evolução, CLIs externas instaladas.
[7] Esta ajuda.
[8] Helpdesk — roda o doctor e, para cada problema encontrado, sugere
    exatamente o que fazer (ex.: qual comando rodar para instalar algo que
    está faltando).

Manual completo (linguagem simples): MANUAL.md
Manual técnico (arquitetura): ARCHITECTURE.md
Guia de instalação (Windows/Linux/macOS): installer/README.md

Comandos diretos (sem menu):
    python3 -m marceloclaro.cli status
    python3 -m marceloclaro.cli agents
    python3 -m marceloclaro.cli doctor
    python3 -m marceloclaro.cli helpdesk
    python3 -m marceloclaro.cli ajuda
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
        elif cmd == "helpdesk":
            print(json.dumps(orchestrator.helpdesk(), indent=2, ensure_ascii=False))
        elif cmd in ("ajuda", "help", "-h", "--help"):
            print(AJUDA_TEXT)
        else:
            print(f"Comando desconhecido: {cmd}.")
            print("Use 'status', 'agents', 'doctor', 'helpdesk' ou 'ajuda'.")
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

        elif choice == "7":
            print(AJUDA_TEXT)

        elif choice == "8":
            helpdesk_report = orchestrator.helpdesk()
            print(f"\n{helpdesk_report['summary']}\n")
            for item in helpdesk_report["guidance"]:
                print(f"- [{item['status'].upper()}] {item['check']}: {item['problem']}")
                print(f"  Sugestão: {item['suggestion']}\n")

        elif choice == "0":
            print("Encerrando o orquestrador. Até logo.")
            break

        else:
            print("Opção inválida. Digite [7] para ver a ajuda.")


if __name__ == "__main__":
    main()
