# -*- coding: utf-8 -*-
"""
CLI do Orquestrador MarceloClaro
================================
Menu interativo de terminal para operar o ecossistema.

Uso:
    python3 -m marceloclaro.cli          # menu interativo
    python3 -m marceloclaro.cli doctor    # diagnóstico estrutural em JSON
    python3 -m marceloclaro.cli status   # comando direto
    python3 -m marceloclaro.cli pesquisa "tema"  # pesquisa acadêmica
    python3 -m marceloclaro.cli apresentacao pasta  # deck MIRA

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
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
[10] Apresentação MIRA (manuscrito → deck de slides animados)
[0] Sair
"""

AJUDA_TEXT = """
O que cada opção faz, em termos simples:

[1] Agentes registrados — lista as especialidades disponíveis.
[2] Postar tarefa — descreve um trabalho para o Blackboard.
[3] Reportar conclusão — informa sucesso ou falha de uma tarefa.
[4] Consultar memória — mostra o contexto metacognitivo compartilhado.
[5] Status geral — exibe o estado do ecossistema.
[6] Doctor — verifica rapidamente specs, histórico, configuração e CLIs.
[7] Esta ajuda.
[8] Helpdesk — roda o doctor e sugere como corrigir cada pendência.
[9] Pesquisa científica — busca um tema em fontes acadêmicas, baixa PDFs
    quando possível e gera fichamento e resenha em ABNT/APA.
[10] Apresentação MIRA — transforma manuscrito.md em deck HTML de cards de
     vidro animados, navegável e acompanhado de relatório de conformidade.

Manual completo: MANUAL.md
Arquitetura técnica: ARCHITECTURE.md
Guia de instalação: installer/README.md

Comandos diretos:
    python3 -m marceloclaro.cli status
    python3 -m marceloclaro.cli agents
    python3 -m marceloclaro.cli doctor
    python3 -m marceloclaro.cli helpdesk
    python3 -m marceloclaro.cli pesquisa "tema" [--max-papers N] [--platforms a,b] [--no-download]
    python3 -m marceloclaro.cli apresentacao <pasta>
"""


def _parse_pesquisa_flags(args):
    """Interpreta as flags opcionais do comando direto ``pesquisa``."""
    max_papers = 8
    platforms = None
    download = True
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--max-papers" and index + 1 < len(args):
            max_papers = int(args[index + 1])
            index += 2
        elif arg == "--platforms" and index + 1 < len(args):
            platforms = [
                platform.strip()
                for platform in args[index + 1].split(",")
                if platform.strip()
            ]
            index += 2
        elif arg == "--no-download":
            download = False
            index += 1
        else:
            index += 1
    return {"max_papers": max_papers, "platforms": platforms, "download": download}


def main() -> int:
    # Modo comando direto
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "doctor":
            from marceloclaro import doctor as doctor_module

            report = doctor_module.run_doctor()
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report.get("overall") in {"healthy", "degraded"} else 1

        if cmd == "apm":
            from integrations.apm import APMPackageManager
            pm = APMPackageManager()
            subcmd = sys.argv[2] if len(sys.argv) > 2 else "audit"
            if subcmd == "init":
                manifest, lock = pm.init(overwrite=True)
                print(f"APM inicializado: {pm.manifest_path.name} e {pm.lock_path.name}")
                print(f"Total de primitivas: {sum(len(v) for v in manifest.primitives.values())}")
            elif subcmd == "install":
                lock = pm.install()
                print(f"APM dependências verificadas e lockfile atualizado: {pm.lock_path.name}")
            elif subcmd == "compile":
                target = sys.argv[3] if len(sys.argv) > 3 else "all"
                res = pm.compile(target=target)
                print(f"APM compilação concluída ({target}):")
                for k, v in res.items():
                    print(f"  - {k} -> {v}")
            elif subcmd == "audit":
                report = pm.audit()
                print(json.dumps(report.summary(), indent=2, ensure_ascii=False))
                return 0 if report.status in {"pass", "warn"} else 1
            elif subcmd == "pack":
                out = sys.argv[3] if len(sys.argv) > 3 else None
                pkg = pm.pack(out)
                print(f"APM pacote exportado: {pkg}")
            elif subcmd in ("list", "primitives"):
                prims = pm.list_primitives()
                print(json.dumps(prims, indent=2, ensure_ascii=False))
            else:
                print(f"Subcomando APM desconhecido: '{subcmd}'. Opções: init, install, compile, audit, pack, list.")
                return 1
            return 0

        orchestrator = MarceloClaroOrchestrator()
        if cmd == "status":
            print(json.dumps(orchestrator.status(), indent=2, ensure_ascii=False))
        elif cmd == "agents":
            print(json.dumps(orchestrator.list_agents(), indent=2, ensure_ascii=False))
        elif cmd == "helpdesk":
            print(json.dumps(orchestrator.helpdesk(), indent=2, ensure_ascii=False))
        elif cmd in ("ajuda", "help", "-h", "--help"):
            print(AJUDA_TEXT)
        elif cmd in ("pesquisa", "research"):
            if len(sys.argv) < 3:
                print(
                    'Uso: python3 -m marceloclaro.cli pesquisa "<tema>" '
                    "[--max-papers N] [--platforms a,b,c] [--no-download]"
                )
                raise SystemExit(1)
            topic = sys.argv[2]
            flags = _parse_pesquisa_flags(sys.argv[3:])
            print(json.dumps(orchestrator.research(topic, **flags), indent=2, ensure_ascii=False))
        elif cmd in ("apresentacao", "present", "mira"):
            if len(sys.argv) < 3:
                print("Uso: python3 -m marceloclaro.cli apresentacao <pasta_da_producao>")
                print("A pasta deve conter um arquivo manuscrito.md.")
                raise SystemExit(1)
            print(json.dumps(
                orchestrator.present(sys.argv[2]),
                indent=2,
                ensure_ascii=False,
            ))
        elif cmd in ("amplify", "amplificar", "dsh"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli amplify "<prompt>" [--model ox-alpha-free] [--type general|coding|reasoning|academic] [--iterations N]')
                raise SystemExit(1)
            prompt = sys.argv[2]
            model = "ox-alpha-free"
            task_type = "general"
            iterations = 2
            idx = 3
            while idx < len(sys.argv):
                if sys.argv[idx] == "--model" and idx + 1 < len(sys.argv):
                    model = sys.argv[idx + 1]
                    idx += 2
                elif sys.argv[idx] == "--type" and idx + 1 < len(sys.argv):
                    task_type = sys.argv[idx + 1]
                    idx += 2
                elif sys.argv[idx] == "--iterations" and idx + 1 < len(sys.argv):
                    iterations = int(sys.argv[idx + 1])
                    idx += 2
                else:
                    idx += 1
            res = orchestrator.amplify_free_model_response(
                prompt=prompt,
                model=model,
                task_type=task_type,
                iterations=iterations,
                use_rag=True,
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif cmd in ("aletheia", "prove", "decompor"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli aletheia "<proposição_ou_teorema>" [--domain general|math|physics|biology]')
                raise SystemExit(1)
            claim = sys.argv[2]
            domain = "general"
            if len(sys.argv) > 4 and sys.argv[3] == "--domain":
                domain = sys.argv[4]
            decomp = orchestrator.aletheia_decompose(claim, domain=domain)
            print(json.dumps(decomp, indent=2, ensure_ascii=False))
        elif cmd in ("deepthink", "think"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli deepthink "<problema>" [--budget 1-5] [--domain general|math|physics]')
                raise SystemExit(1)
            problem = sys.argv[2]
            budget = 3
            domain = "general"
            idx = 3
            while idx < len(sys.argv):
                if sys.argv[idx] == "--budget" and idx + 1 < len(sys.argv):
                    budget = int(sys.argv[idx + 1])
                    idx += 2
                elif sys.argv[idx] == "--domain" and idx + 1 < len(sys.argv):
                    domain = sys.argv[idx + 1]
                    idx += 2
                else:
                    idx += 1
            think_res = orchestrator.deep_think(problem, domain=domain, compute_budget=budget)
            print(json.dumps(think_res, indent=2, ensure_ascii=False))
        elif cmd in ("alphaproof", "prover"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli alphaproof "<teorema_ou_meta>"')
                raise SystemExit(1)
            theorem = sys.argv[2]
            proof_res = orchestrator.alphaproof_search(theorem)
            print(json.dumps(proof_res, indent=2, ensure_ascii=False))
        elif cmd in ("erdos", "conjecture", "hirzebruch"):
            conjecture_type = sys.argv[2] if len(sys.argv) > 2 else "erdos"
            params = {}
            if len(sys.argv) > 4 and sys.argv[3] == "--c":
                params["c"] = int(sys.argv[4])
            if len(sys.argv) > 4 and sys.argv[3] == "--dim":
                params["dim"] = int(sys.argv[4])
            res = orchestrator.solve_open_conjecture(conjecture_type, params=params)
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif cmd in ("lean4", "lean"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli lean4 "<codigo_lean_ou_caminho_arquivo>"')
                raise SystemExit(1)
            raw_input = sys.argv[2]
            if os.path.isfile(raw_input):
                with open(raw_input, "r", encoding="utf-8") as f:
                    code = f.read()
            else:
                code = raw_input
            lean_res = orchestrator.lean4_verify_code(code)
            print(json.dumps(lean_res, indent=2, ensure_ascii=False))
        elif cmd in ("egraph", "saturate", "egg"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli egraph "<expressao_s_expr>" (ex: "(+ (* x 1) 0)")')
                raise SystemExit(1)
            expr = sys.argv[2]
            egraph_res = orchestrator.egraph_saturate_term(expr)
            print(json.dumps(egraph_res, indent=2, ensure_ascii=False))
        elif cmd in ("geometry", "alphageometry", "wu"):
            prob_type = sys.argv[2] if len(sys.argv) > 2 else "midpoint_theorem"
            geom_res = orchestrator.solve_geometry_problem(prob_type)
            print(json.dumps(geom_res, indent=2, ensure_ascii=False))
        elif cmd in ("autoformalize", "formalize", "crossval"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli autoformalize "<enunciado_informal>"')
                raise SystemExit(1)
            informal_text = sys.argv[2]
            form_res = orchestrator.autoformalize_to_lean4(informal_text)
            print(json.dumps(form_res, indent=2, ensure_ascii=False))
        elif cmd in ("shortcuts", "atalhos"):
            from scripts.create_desktop_shortcuts import main as make_shortcuts
            make_shortcuts()
        elif cmd in ("clinical", "medico", "anamnese"):
            complaint = sys.argv[2] if len(sys.argv) > 2 else "Dor torácica atípica"
            mode = "professional_cds"
            if len(sys.argv) > 4 and sys.argv[3] == "--mode":
                mode = sys.argv[4]
            case_data = {
                "chief_complaint": complaint,
                "patient_profile": {"age": 52, "sex": "M", "egfr": 75.0, "comorbidities": ["Hipertensão"]},
                "duration": "2 dias",
                "severity": "moderada a grave",
            }
            clinical_res = orchestrator.investigate_clinical_case(case_data, mode=mode)
            print(json.dumps(clinical_res, indent=2, ensure_ascii=False))
        else:
            print(f"Comando desconhecido: {cmd}.")
            print("Use 'doctor', 'apm', 'amplify', 'aletheia', 'deepthink', 'alphaproof', 'erdos', 'lean4', 'egraph', 'geometry', 'autoformalize', 'clinical', 'shortcuts', 'imobench', 'status', 'agents', 'helpdesk', 'pesquisa' ou 'apresentacao'.")
        return 0

    # Modo interativo
    orchestrator = MarceloClaroOrchestrator()
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
            download = input("Baixar PDFs quando possível? (S/n): ").strip().lower() != "n"
            print("Buscando em 11 fontes acadêmicas... isso pode levar alguns minutos.")
            manifest = orchestrator.research(
                topic,
                max_papers=max_papers,
                download=download,
            )
            resumo = manifest["resumo"]
            print(
                f"\nPesquisa concluída: {resumo['artigos_selecionados']} artigos, "
                f"{resumo['pdfs_baixados']} PDFs, "
                f"{resumo['fichamentos']} fichamentos, "
                f"{resumo['resenhas']} resenhas críticas."
            )
            print(f"Pasta: {manifest['folder']}")

        elif choice == "10":
            folder = input("Pasta da produção (com manuscrito.md): ").strip()
            if not folder:
                print("Pasta vazia, operação cancelada.")
                continue
            print("Montando a apresentação MIRA (extract → plan → copywrite → build → animate → validate)...")
            result = orchestrator.present(folder)
            if result.get("ok") is False or result.get("error"):
                print(f"Falha: {result.get('error', 'produção inválida')}")
            else:
                status = "CONFORME" if result.get("passed") else "COM RESSALVAS"
                print(f"\nApresentação gerada ({status}).")
                print(f"Deck: {result.get('deck')}")
                print(f"Conformidade: {result.get('conformidade')}")

        elif choice == "0":
            print("Encerrando o orquestrador. Até logo.")
            break

        else:
            print("Opção inválida. Digite [7] para ver a ajuda.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
