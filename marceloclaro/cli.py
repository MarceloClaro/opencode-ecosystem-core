# -*- coding: utf-8 -*-
"""
CLI do Orquestrador MarceloClaro
================================
Menu interativo de terminal para operar o ecossistema.

Uso:
    python3 -m marceloclaro.cli          # menu interativo
    python3 -m marceloclaro.cli doctor    # diagnóstico estrutural em JSON
    python3 -m marceloclaro.cli biblioteca buscar "split por grupo"
    python3 -m marceloclaro.cli fine-dados validar dados.json
    python3 -m marceloclaro.cli integracoes status
    python3 -m marceloclaro.cli tdd-history red SPEC-ID [--timeout 1200]
    python3 -m marceloclaro.cli status   # comando direto
    python3 -m marceloclaro.cli pesquisa "tema"  # pesquisa acadêmica
    python3 -m marceloclaro.cli apresentacao pasta  # deck MIRA

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import argparse
import os
import sys
import json
import pathlib

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
    python3 -m marceloclaro.cli integracoes status
    python3 -m marceloclaro.cli integracoes skill <nome>
    python3 -m marceloclaro.cli integracoes handoff <artifact_id>
    python3 -m marceloclaro.cli helpdesk
    python3 -m marceloclaro.cli pesquisa "tema" [--max-papers N] [--platforms a,b] [--no-download]
    python3 -m marceloclaro.cli pesquisa-full "tema" [--question '...'] [--per-source N] [--max-pdfs N]
    python3 -m marceloclaro.cli apresentacao <pasta>
    python3 -m marceloclaro.cli conteudo-offline plan catalogo.json --select categoria:tier
    python3 -m marceloclaro.cli reverse-scan --target "metodos.Meta-análise" [--file A.md] [--domain ecosystem|academic] [--json]
"""


def _parse_pesquisa_flags(args):
    """Interpreta as flags opcionais do comando direto ``pesquisa``."""
    max_papers = 8
    platforms = None
    download = True
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--max-papers":
            if index + 1 >= len(args):
                raise ValueError("--max-papers exige um inteiro positivo.")
            max_papers = int(args[index + 1])
            if max_papers < 1:
                raise ValueError("--max-papers exige um inteiro positivo.")
            index += 2
        elif arg == "--platforms":
            if index + 1 >= len(args) or args[index + 1].startswith("--"):
                raise ValueError("--platforms exige uma lista não vazia.")
            platforms = [
                platform.strip()
                for platform in args[index + 1].split(",")
                if platform.strip()
            ]
            if not platforms:
                raise ValueError("--platforms exige uma lista não vazia.")
            index += 2
        elif arg == "--no-download":
            download = False
            index += 1
        else:
            raise ValueError(f"Argumento de pesquisa desconhecido: {arg}")
    return {"max_papers": max_papers, "platforms": platforms, "download": download}


def _parse_effectful_options(cmd, argv):
    """Valida opções antes de construir executores ou alcançar serviços."""
    import argparse
    parser = argparse.ArgumentParser(prog="marceloclaro " + cmd, add_help=False, exit_on_error=False)
    if cmd in {"pesquisa-full", "research-full"}:
        parser.add_argument("--question")
        parser.add_argument("--objective")
        parser.add_argument("--per-source", type=int, default=10)
        parser.add_argument("--max-pdfs", type=int, default=20)
    elif cmd in {"podcast", "audio"}:
        for flag, dest in (("--title", "title"), ("--language", "language"), ("--length", "length"), ("--format", "fmt")):
            parser.add_argument(flag, dest=dest, default=argparse.SUPPRESS)
    elif cmd in {"amplify", "amplificar", "dsh"}:
        parser.add_argument("--model", default="ox-alpha-free")
        parser.add_argument("--type", dest="task_type", default="general")
        parser.add_argument("--iterations", type=int, default=2)
    else:
        parser.add_argument("--budget", type=int, default=3)
        parser.add_argument("--domain", default="general")
    try:
        namespace, unknown = parser.parse_known_args(argv)
    except argparse.ArgumentError as exc:
        raise ValueError(str(exc)) from exc
    if unknown:
        raise ValueError("Argumentos desconhecidos: " + " ".join(unknown))
    options = vars(namespace)
    for key in ("per_source", "iterations"):
        if key in options and options[key] < 1:
            raise ValueError(f"{key} deve ser positivo")
    if "max_pdfs" in options and options["max_pdfs"] < 0:
        raise ValueError("max_pdfs não pode ser negativo")
    if "budget" in options and not 1 <= options["budget"] <= 5:
        raise ValueError("budget deve estar entre 1 e 5")
    if any(isinstance(value, str) and not value.strip() for value in options.values()):
        raise ValueError("Opções textuais não podem ser vazias")
    return options


def _cmd_reverse_scan(argv):
    """Comando direto: planejamento reverso do futuro (R483 → CLI, R484).

    Uso:
        python3 -m marceloclaro.cli reverse-scan --target "metodos.Meta-análise" \
            [--file A.md [B.md ...]] [--domain ecosystem|academic] [--json]
    """
    targets: list[str] = []
    files: list[str] = []
    domain = "ecosystem"
    as_json = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--target" and i + 1 < len(argv):
            for target in argv[i + 1].split(","):
                target = target.strip()
                if target:
                    targets.append(target)
            i += 2
        elif arg == "--file" and i + 1 < len(argv):
            files.append(argv[i + 1])
            i += 2
        elif arg == "--domain" and i + 1 < len(argv):
            domain = argv[i + 1]
            i += 2
        elif arg == "--json":
            as_json = True
            i += 1
        else:
            i += 1

    if not targets:
        print(
            'Uso: python3 -m marceloclaro.cli reverse-scan --target "<capacidade>" '
            '[--file A.md [B.md ...]] [--domain ecosystem|academic] [--json]'
        )
        return 1

    # Corpus: arquivos explícitos ou specs/ do próprio Core (hermético, local).
    if files:
        texts: list[str] = []
        for path in files:
            try:
                texts.append(pathlib.Path(path).read_text(encoding="utf-8"))
            except OSError as exc:
                print(f"erro ao ler {path}: {exc}")
                return 1
    else:
        specs_dir = pathlib.Path(__file__).resolve().parent.parent / "specs"
        texts = [
            p.read_text(encoding="utf-8")
            for p in sorted(specs_dir.glob("SPEC-935-R*.md"))
        ]

    class _FileAudit:
        def __init__(self, corpus):
            self._corpus = corpus

        def get_all_text(self):
            return self._corpus

    from scanners.noological_scanner import NoologicalScanner
    from scanners.reverse_scanner import ReverseScanner

    ns = NoologicalScanner()
    scan = ns.scan(_FileAudit("\n\n".join(texts)), research_domain=domain)
    rs = ReverseScanner()
    report = rs.scan(scan, target_state=targets)

    if as_json:
        print(json.dumps({
            "target_state": report.target_state,
            "observed_capabilities": report.observed_capabilities,
            "reverse_closure": report.reverse_closure,
            "evolution_gap": report.evolution_gap,
            "opportunities": [
                {
                    k: getattr(o, k)
                    for k in ("capability", "domain", "potential", "cascade",
                              "centrality", "novelty", "ritual", "tier",
                              "possibly_ritual")
                }
                for o in report.opportunities
            ],
            "params": report.params,
            "warnings": report.warnings,
            "domain": domain,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"\nEstado futuro desejado (F): {', '.join(report.target_state)}")
    print(f"Domínio: {domain}")
    print(f"Capacidades observadas (A): {len(report.observed_capabilities)}")
    print(f"Fecho regressivo R(F): {len(report.reverse_closure)} capacidades")
    if report.warnings:
        print("Avisos:")
        for warning in report.warnings:
            print(f"  - {warning}")
    print("\nGap evolutivo (Δ) e oportunidades priorizadas:")
    for opportunity in sorted(report.opportunities, key=lambda o: -o.potential):
        flag = " [lacuna ritual]" if opportunity.possibly_ritual else ""
        print(
            f"  {opportunity.capability:45s} "
            f"p={opportunity.potential:.2f} "
            f"tier={opportunity.tier:12s}{flag}"
        )
    print()
    return 0


def _cmd_harness(argv):
    """
    `marceloclaro harness {inventory|route|emit}` — Federação de artefatos
    multi-harness (SPEC-935-R621).

    Fica antes da construção do orquestrador porque nenhum dos três
    subcomandos precisa do catálogo de agentes: carregar 200+ registros para
    então varrer o disco seria custo puro.
    """

    from transformer.harness_head import HarnessRegistry

    subcmd = argv[0] if argv else "inventory"
    flags = argv[1:]
    dry_run = "--execute" not in flags
    require_license = "--require-license" in flags
    top_k = 5
    for idx, arg in enumerate(flags):
        if arg == "--top" and idx + 1 < len(flags):
            top_k = int(flags[idx + 1])

    registry = HarnessRegistry()

    if subcmd == "inventory":
        report = registry.inventory()
        report["counted_agents"] = len(registry.cards())
        print(json.dumps(report, indent=2, ensure_ascii=False))
        # O código de saída julga a cobertura de *ecossistemas*, não de raízes:
        # `~/.codex` ausente é normal em uma máquina que usa Codex só via
        # repositório, e reprovar o comando por isso seria ruído.
        return 0 if not report.get("ecosystems_missing") else 1

    if subcmd == "route":
        if len(argv) < 2:
            print("Uso: marceloclaro harness route <descricao> [--top N]")
            return 1
        # A descrição é o primeiro argumento posicional; o resto da linha é
        # inteiro Flags. Juntar tudo (o que uma versão anterior fazia) engolia
        # o próprio valor de `--top` na busca e poluía o cosseno léxico.
        skip_next = False
        words = []
        for arg in argv[1:]:
            if skip_next:
                skip_next = False
                continue
            if arg == "--top":
                skip_next = True
                continue
            if arg.startswith("--"):
                continue
            words.append(arg)
        description = " ".join(words)
        report = registry.route(description, [])
        report["ranking"] = report["ranking"][:max(1, top_k)]
        report["counted_agents"] = len(registry.cards())
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["ranking"] else 1

    if subcmd == "emit":
        kinds = None
        if "--kinds" in flags:
            idx = flags.index("--kinds")
            if idx + 1 < len(flags):
                kinds = tuple(k.strip() for k in flags[idx + 1].split(",") if k.strip())
        artifacts = registry.artifacts()
        if kinds:
            wanted = set(kinds)
            artifacts = [a for a in artifacts if a.kind in wanted]
        report = registry.emitter(dry_run=dry_run).emit_all(
            artifacts, require_license=require_license)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if dry_run:
            print("\n(dry-run: nenhuma escrita realizada; use --execute para gravar)")
        return 0 if report["refused"] == 0 and report["skipped"] == 0 else 1

    print(f"Subcomando harness desconhecido: '{subcmd}'. Opções: inventory, route, emit.")
    return 1


def _cmd_network(argv):
    """Superfície local da mesma rede que o MCP expõe ao OpenCode."""
    import argparse
    from integrations.ecosystem_mcp import get_coordinator, get_workflow_coordinator

    parser = argparse.ArgumentParser(prog="marceloclaro network")
    parser.add_argument("action", choices=("status", "route", "run", "workflow", "workflow-status"))
    parser.add_argument("task", nargs="*")
    parser.add_argument("--ecosystem", choices=("claude", "antigravity", "codex", "chatgpt"))
    parser.add_argument("--capabilities", default="")
    parser.add_argument("--max-steps", type=int)
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--spec", help="Especificação vinculada; software exige RED executado")
    parser.add_argument("--workflow-id")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args(argv or ["status"])
    task = " ".join(args.task).strip()
    if args.action != "status" and not task:
        parser.error("informe a tarefa, o arquivo de etapas ou o identificador do workflow")
    if (args.resume or args.retry_failed or args.workflow_id) and args.action != "workflow":
        parser.error("as opções de retomada pertencem à ação workflow")
    if args.action in {"workflow", "workflow-status"} and (args.ecosystem is not None or args.capabilities):
        parser.error("informe ecosystem e required_capabilities em cada etapa do arquivo de workflow")
    required = [part.strip() for part in args.capabilities.split(",") if part.strip()]
    try:
        if args.action == "workflow":
            from pathlib import Path
            definition = json.loads(Path(task).read_text(encoding="utf-8"))
            nodes = definition.get("nodes") if isinstance(definition, dict) else definition
            report = get_workflow_coordinator().run(
                nodes, max_steps=args.max_steps if args.max_steps is not None else 6,
                timeout=args.timeout if args.timeout is not None else 180,
                workflow_id=args.workflow_id, resume=args.resume, retry_failed=args.retry_failed)
        elif args.action == "workflow-status":
            report = get_workflow_coordinator().status(task)
        elif args.action == "status":
            report = get_coordinator().status()
        elif args.action == "route":
            report = get_coordinator().route(task, required, args.ecosystem)
        else:
            delivery_options = {"spec_id": args.spec} if args.spec else {}
            report = get_coordinator().run(task, required,
                args.max_steps if args.max_steps is not None else 3,
                args.timeout if args.timeout is not None else 120, args.ecosystem, **delivery_options)
    except (ValueError, OSError) as exc:
        print(json.dumps({"success": False, "status": "invalid", "error": str(exc)},
                         ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get("success") is False or report.get("status") in {"blocked", "failed", "exhausted"} else 0


class _ArgParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _emit_cli(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def _cmd_quantum_catalog(argv):
    import argparse

    parser = _ArgParser(prog="quantum-catalog")
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("status")
    sub.add_parser("historico")
    sub.add_parser("importar")
    sub.add_parser("painel")
    lst = sub.add_parser("listar")
    lst.add_argument("--kind", choices=["repository", "organization"])
    lst.add_argument("--limit", type=int)
    lst.add_argument("--offset", type=int)
    lst.add_argument("--historico", action="store_true")
    search = sub.add_parser("buscar")
    search.add_argument("query")
    search.add_argument("--kind", choices=["repository", "organization"])
    search.add_argument("--limit", type=int)
    search.add_argument("--offset", type=int)
    search.add_argument("--stack")
    search.add_argument("--category")
    search.add_argument("--historico", action="store_true")
    ver = sub.add_parser("ver")
    ver.add_argument("identifier")
    try:
        args = parser.parse_args(argv)
    except ValueError as exc:
        _emit_cli({"status": "invalid", "error": str(exc)})
        return 2
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    try:
        if args.operation == "importar":
            result = orch.quantum_catalog_action({"operation": "import"})
            _emit_cli(result)
            return 0 if result.get("status") in {"imported", "unchanged"} else 2
        if args.operation == "painel":
            result = orch.quantum_catalog_action({"operation": "painel"})
            _emit_cli(result)
            return 0 if result.get("status") == "ok" else 2
        if args.operation == "status":
            config = {"operation": "status"}
        elif args.operation == "historico":
            config = {"operation": "history"}
        elif args.operation == "listar":
            config = {"operation": "list"}
            if args.kind:
                config["kind"] = args.kind
            if args.limit is not None:
                config["limit"] = args.limit
            if args.offset is not None:
                config["offset"] = args.offset
            if args.historico:
                config["include_historical"] = True
        elif args.operation == "buscar":
            config = {"operation": "search", "query": args.query}
            if args.kind:
                config["kind"] = args.kind
            if args.limit is not None:
                config["limit"] = args.limit
            if args.offset is not None:
                config["offset"] = args.offset
            if args.stack:
                config["stack"] = args.stack
            if args.category:
                config["category"] = args.category
            if args.historico:
                config["include_historical"] = True
        else:
            config = {"operation": "get", "identifier": args.identifier}
        result = orch.quantum_catalog_action(config)
        _emit_cli(result)
        return 0
    except ValueError as exc:
        _emit_cli({"status": "invalid", "error": str(exc)})
        return 2


def _cmd_conhecimento(argv):
    parser = _ArgParser(prog="conhecimento")
    sub = parser.add_subparsers(dest="operation", required=True)
    sources = sub.add_parser("fontes")
    search = sub.add_parser("buscar")
    search.add_argument("query")
    search.add_argument("--fonte", default="quantum_catalog")
    search.add_argument("--limite", type=int)
    try:
        args = parser.parse_args(argv)
    except ValueError as exc:
        _emit_cli({"status": "invalid", "error": str(exc)})
        return 2
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    try:
        if args.operation == "fontes":
            config = {"operation": "sources"}
        else:
            config = {"operation": "search", "source_id": args.fonte, "query": args.query}
            if args.limite is not None:
                config["limit"] = args.limite
        result = orch.knowledge_sources_action(config)
        _emit_cli(result)
        return 0
    except ValueError as exc:
        _emit_cli({"status": "invalid", "error": str(exc)})
        return 2


def main() -> int:
    # Modo comando direto
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "edge-quantizer":
            from integrations.ai_edge_quantizer_core import main as edge_quantizer_main
            return edge_quantizer_main(sys.argv[2:])
        if cmd == "itsfine":
            from integrations.itsfine_core import main as itsfine_main
            return itsfine_main(sys.argv[2:])
        if cmd in ("conteudo-offline", "offline-content"):
            from integrations.offline_content import main as offline_content_main
            return offline_content_main(sys.argv[2:])
        if cmd in ("federacao", "federation"):
            from integrations.federation_sync.cli import run as federation_run
            return federation_run(sys.argv[2:])
        if cmd == "doctor":
            import argparse
            from marceloclaro import doctor as doctor_module

            parser = argparse.ArgumentParser(prog="marceloclaro doctor")
            parser.add_argument("--live", action="store_true",
                                help="executa sondagens HTTP, CLIs e exemplos internos explicitamente")
            args = parser.parse_args(sys.argv[2:])
            report = doctor_module.run_doctor(live=args.live)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report.get("overall") in {"healthy", "degraded"} else 1

        if cmd == "core-check":
            from marceloclaro.core_check import run_core_check

            report = run_core_check()
            return 0 if report["overall"] in {"healthy", "degraded"} else 1

        if cmd == "code-context":
            from marceloclaro.code_context_cli import run_code_context_cli
            return run_code_context_cli(sys.argv[2:], MarceloClaroOrchestrator)

        if cmd in {"agentes", "ci-local"}:
            from marceloclaro.governed_cli import run_governed_cli
            return run_governed_cli(cmd, sys.argv[2:], MarceloClaroOrchestrator)

        if cmd == "rea":
            from marceloclaro.rea_cli import run_rea_cli
            return run_rea_cli(sys.argv[2:], MarceloClaroOrchestrator)

        if cmd == "browser":
            from marceloclaro.browser_cli import run_browser_cli
            return run_browser_cli(sys.argv[2:], MarceloClaroOrchestrator)

        if cmd == "tdd-history":
            if len(sys.argv) not in (4, 6) or sys.argv[2] not in ("red", "green"):
                print("Uso: marceloclaro tdd-history red|green SPEC-ID [--timeout SEGUNDOS]")
                return 1
            timeout = 1200
            try:
                if len(sys.argv) == 6:
                    if sys.argv[4] != "--timeout":
                        raise ValueError("Opção inválida.")
                    timeout = int(sys.argv[5])
                coordinator = MarceloClaroOrchestrator(auto_load_agents=False)
                result = coordinator.tdd_history_probe(sys.argv[3], sys.argv[2], timeout)
            except (ValueError, RuntimeError, OSError) as exc:
                print(json.dumps({"accepted": False, "error": str(exc)}, ensure_ascii=False))
                return 1
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["accepted"] and (sys.argv[2] == "red" or result["red_green_pair"]["verified"]) else 1

        if cmd == "apm":
            from integrations.apm import APMPackageManager
            pm = APMPackageManager()
            subcmd = sys.argv[2] if len(sys.argv) > 2 else "audit"
            if subcmd == "init":
                manifest, lock = pm.init(overwrite=True)
                print(f"APM inicializado: {pm.manifest_path.name} e {pm.lock_path.name}")
                print(f"Total de primitivas: {sum(len(v) for v in manifest.primitives.values())}")
            elif subcmd == "install":
                pm.install()
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

        if cmd in ("reverse-scan", "reverso"):
            return _cmd_reverse_scan(sys.argv[2:])

        if cmd in ("agent-register", "register-agents"):
            from mci.agent_registry_bootstrap import register_catalog_agents

            report = register_catalog_agents()
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0

        if cmd in ("ciencia", "science"):
            from marceloclaro.science_cli import run_science_cli
            return run_science_cli(sys.argv[2:])

        if cmd in ("notebook", "gemini-notebook"):
            from marceloclaro.science_cli import run_science_cli
            return run_science_cli(["notebook", *sys.argv[2:]])

        if cmd in ("integracoes", "integrations"):
            from marceloclaro.integration_cli import run_integration_cli

            return run_integration_cli(sys.argv[2:])

        if cmd == "biblioteca":
            from marceloclaro.library_cli import run_library_cli

            return run_library_cli(sys.argv[2:])

        if cmd == "fine-dados":
            from marceloclaro.library_cli import run_finetuning_cli

            return run_finetuning_cli(sys.argv[2:])

        if cmd == "quantum-catalog":
            return _cmd_quantum_catalog(sys.argv[2:])

        if cmd == "conhecimento":
            return _cmd_conhecimento(sys.argv[2:])

        if cmd == "harness":
            return _cmd_harness(sys.argv[2:])

        if cmd == "network" or cmd == "rede":
            return _cmd_network(sys.argv[2:])

        if cmd == "custos":
            # Governança de custo monetário estimado. Não instancia o
            # orquestrador: a leitura é do registro de tarifas, não do estado
            # do Blackboard.
            from integrations.cost_governance import report as cost_report

            print(json.dumps(cost_report(), indent=2, ensure_ascii=False))
            return 0

        known_commands = {
            "status", "agents", "helpdesk", "custos", "ajuda", "help", "-h", "--help",
            "pesquisa", "research", "pesquisa-full", "research-full",
            "apresentacao", "present", "mira", "podcast", "audio",
            "amplify", "amplificar", "dsh", "aletheia", "prove", "decompor",
            "deepthink", "think", "alphaproof", "prover", "erdos", "conjecture",
            "hirzebruch", "lean4", "lean", "egraph", "saturate", "egg",
            "geometry", "alphageometry", "wu", "autoformalize", "formalize",
            "crossval", "shortcuts", "atalhos", "clinical", "medico", "anamnese",
        }
        if cmd not in known_commands:
            print(f"Comando desconhecido: {cmd}. Use 'ajuda'.", file=sys.stderr)
            print("Use 'ajuda' para consultar os comandos, incluindo 'apresentacao'.")
            return 2
        if (cmd in {"pesquisa", "research", "pesquisa-full", "research-full", "podcast", "audio",
                    "amplify", "amplificar", "dsh", "deepthink", "think"} and len(sys.argv) < 3):
            print(f'Uso: python3 -m marceloclaro.cli {cmd} "<tema, pasta ou tarefa>" [opções]')
            raise SystemExit(1)
        research_flags = None
        service_options = None
        if cmd in {"pesquisa", "research"}:
            try:
                if len(sys.argv) < 3 or not sys.argv[2].strip() or sys.argv[2].startswith("--"):
                    raise ValueError("Pesquisa exige um tema.")
                research_flags = _parse_pesquisa_flags(sys.argv[3:])
            except ValueError as exc:
                print(f"Argumentos inválidos: {exc}", file=sys.stderr)
                return 2
        if cmd in {"pesquisa-full", "research-full", "podcast", "audio", "amplify", "amplificar", "dsh", "deepthink", "think"}:
            try:
                if len(sys.argv) < 3 or not sys.argv[2].strip() or sys.argv[2].startswith("--"):
                    raise ValueError("Comando exige tema, pasta ou tarefa.")
                service_options = _parse_effectful_options(cmd, sys.argv[3:])
            except ValueError as exc:
                print(f"Argumentos inválidos: {exc}", file=sys.stderr)
                return 2
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
            print(json.dumps(orchestrator.research(topic, **research_flags), indent=2, ensure_ascii=False))
        elif cmd in ("pesquisa-full", "research-full"):
            if len(sys.argv) < 3:
                print(
                    'Uso: python3 -m marceloclaro.cli pesquisa-full "<tema>" '
                    "[--question '...'] [--objective '...'] [--per-source N] [--max-pdfs N]"
                )
                raise SystemExit(1)
            topic = sys.argv[2]
            from research.orchestrate import run_full_research
            result = run_full_research(
                topic=topic, **service_options,
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
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
        elif cmd in ("podcast", "audio"):
            if len(sys.argv) < 3:
                print("Uso: python3 -m marceloclaro.cli podcast <pasta_da_producao> "
                      "[--title T] [--language pt-BR] [--length long] [--format deep_dive]")
                print("Gera um podcast (áudio m4a) do manuscrito.md da pasta via "
                      "Gemini Notebook (nlm). Fase 1 SPEC-972: uso explícito do operador.")
                raise SystemExit(1)
            podcast_result = orchestrator.podcast(sys.argv[2], **service_options)
            print(json.dumps(
                podcast_result,
                indent=2,
                ensure_ascii=False,
            ))
            return 1 if podcast_result.get("ok") is False or podcast_result.get("error") else 0
        elif cmd in ("amplify", "amplificar", "dsh"):
            if len(sys.argv) < 3:
                print('Uso: python3 -m marceloclaro.cli amplify "<prompt>" [--model ox-alpha-free] [--type general|coding|reasoning|academic] [--iterations N]')
                raise SystemExit(1)
            prompt = sys.argv[2]
            res = orchestrator.amplify_free_model_response(
                prompt=prompt,
                **service_options,
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
            think_res = orchestrator.deep_think(problem, domain=service_options["domain"], compute_budget=service_options["budget"])
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
            return 0 if lean_res.get("is_valid") is True and lean_res.get("status") == "machine_checked" else 1
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
            print("Use 'doctor', 'apm', 'amplify', 'aletheia', 'deepthink', 'alphaproof', 'erdos', 'lean4', 'egraph', 'geometry', 'autoformalize', 'clinical', 'shortcuts', 'imobench', 'status', 'agents', 'helpdesk', 'pesquisa', 'pesquisa-full', 'apresentacao' ou 'conteudo-offline'.")
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
