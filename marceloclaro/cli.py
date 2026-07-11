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
[9] Pesquisa científica (busca em 11 fontes + fichamento ABNT/APA)
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
[9] Pesquisa científica — busca um tema em 11 fontes acadêmicas (arXiv,
    Semantic Scholar, Crossref, OpenAlex, Europe PMC, SciELO, PubMed,
    bioRxiv/medRxiv, CORE, GitHub, Kaggle), baixa os PDFs que conseguir
    (acesso aberto direto e, como fallback para artigos pagos, via
    scihub-cli — opcional, `pip install scihub-cli`), converte para
    Markdown e gera fichamento + resenha crítica em ABNT e APA — tudo
    numa pasta única dentro de pesquisa/.

Manual completo (linguagem simples): MANUAL.md
Manual técnico (arquitetura): ARCHITECTURE.md
Guia de instalação (Windows/Linux/macOS): installer/README.md

Comandos diretos (sem menu):
    python3 -m marceloclaro.cli status
    python3 -m marceloclaro.cli agents
    python3 -m marceloclaro.cli doctor
    python3 -m marceloclaro.cli helpdesk
    python3 -m marceloclaro.cli ajuda
    python3 -m marceloclaro.cli pesquisa "<tema>" [--max-papers N] [--platforms a,b,c] [--no-download]
"""


def _parse_pesquisa_flags(args):
    """Interpreta as flags opcionais do comando direto `pesquisa`."""
    max_papers = 8
    platforms = None
    download = True
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--max-papers" and i + 1 < len(args):
            max_papers = int(args[i + 1])
            i += 2
        elif arg == "--platforms" and i + 1 < len(args):
            platforms = [p.strip() for p in args[i + 1].split(",") if p.strip()]
            i += 2
        elif arg == "--no-download":
            download = False
            i += 1
        else:
            i += 1
    return {"max_papers": max_papers, "platforms": platforms, "download": download}


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
        elif cmd in ("pesquisa", "research"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli pesquisa "<tema>" '
                      "[--max-papers N] [--platforms a,b,c] [--no-download]")
                sys.exit(1)
            topic = sys.argv[2]
            flags = _parse_pesquisa_flags(sys.argv[3:])
            manifest = orchestrator.research(topic, **flags)
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
        elif cmd in ("ajuda", "help", "-h", "--help"):
            print(AJUDA_TEXT)
        else:
            print(f"Comando desconhecido: {cmd}.")
            print("Use 'status', 'agents', 'doctor', 'helpdesk', 'pesquisa' ou 'ajuda'.")
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

        elif choice == "9":
            topic = input("Tema da pesquisa: ").strip()
            if not topic:
                print("Tema vazio, operação cancelada.")
                continue
            max_papers_raw = input("Número máximo de artigos (padrão 8): ").strip()
            max_papers = int(max_papers_raw) if max_papers_raw.isdigit() else 8
            baixar = input("Baixar PDFs quando possível? (S/n): ").strip().lower() != "n"
            print("Buscando em 11 fontes acadêmicas... isso pode levar alguns minutos.")
            manifest = orchestrator.research(topic, max_papers=max_papers, download=baixar)
            resumo = manifest["resumo"]
            print(f"\nPesquisa concluída: {resumo['artigos_selecionados']} artigos, "
                  f"{resumo['pdfs_baixados']} PDFs, {resumo['fichamentos']} fichamentos, "
                  f"{resumo['resenhas']} resenhas críticas.")
            print(f"Pasta: {manifest['folder']}")

        elif choice == "0":
            print("Encerrando o orquestrador. Até logo.")
            break

        else:
            print("Opção inválida. Digite [7] para ver a ajuda.")


if __name__ == "__main__":
    main()
