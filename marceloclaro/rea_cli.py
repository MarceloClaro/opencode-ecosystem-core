"""Entrada CLI de inspeção REA sob MarceloClaro (R808)."""
import argparse
import json
from typing import Callable, Any


def run_rea_cli(argv: list[str], orchestrator_factory: Callable[..., Any]) -> int:
    parser = argparse.ArgumentParser(prog="marceloclaro rea", description="REA local coordenado")
    parser.add_argument("operation", nargs="?", default="status",
                        choices=("status", "catalog", "session", "layers", "layer",
                                 "analyze", "analyze_binary", "setup", "inspect", "explain", "site", "agent"))
    parser.add_argument("path", nargs="?", help="Caminho local da aplicação, binário ou artefato")
    parser.add_argument("--layer", help="Camada REA a inspecionar (ver operação layers)")
    parser.add_argument("--encoding", choices=("raw", "hex"),
                        help="Codificação do bytecode na camada evm (padrão raw)")
    parser.add_argument("--procedure", help="Função nativa ou endereço a analisar (padrão main)")
    parser.add_argument("--timeout", type=float, default=60.0,
                        help="Prazo da operação em segundos (máximo 180)")
    parser.add_argument("--json", action="store_true", help="Saída JSON (padrão)")
    parser.add_argument("--kind", default="auto", help="Tipo do alvo local (auto/javascript/native/dotnet/html/plist/android/firmware/elf-layout)")
    parser.add_argument("--format", choices=("json", "text"), default="json", help="Formato da explicação local")
    parser.add_argument("--model", default="modelo-local", help="Modelo já instalado no endpoint local")
    parser.add_argument("--model-endpoint", default="http://127.0.0.1:11434/v1", help="Endpoint literal loopback do modelo")
    parser.add_argument("--port", type=int, default=8767, help="Porta loopback do site de instruções")
    parser.add_argument("--check", action="store_true", help="Confere configuração efetiva do agente sem executar inferência")
    parser.add_argument("--prompt", help="Mensagem para o cliente de agente local; sem mensagem abre interface interativa")
    try:
        args = parser.parse_args(argv)
        if (args.check or args.prompt is not None) and args.operation != "agent":
            parser.error("--check/--prompt somente são permitidos em agent")
        if args.operation == "layer":
            if args.layer is None or args.path is None:
                parser.error("layer exige --layer e caminho")
        elif args.operation in {"analyze", "analyze_binary", "inspect", "explain"}:
            if args.path is None:
                parser.error("analyze/analyze_binary exigem caminho")
        elif args.path is not None:
            parser.error("as operações status/catalog/session/layers não aceitam caminho")
        if args.layer is not None and args.operation != "layer":
            parser.error("--layer somente é permitido em layer")
        if args.encoding is not None and args.operation != "layer":
            parser.error("--encoding somente é permitido em layer")
        if args.procedure is not None and args.operation not in {"analyze_binary", "inspect"}:
            parser.error("--procedure somente é permitido em analyze_binary")
        config = {"operation": args.operation, "timeout_seconds": args.timeout}
        if args.path is not None:
            config["path"] = args.path
        if args.layer is not None:
            config["layer"] = args.layer
        if args.encoding is not None:
            config["encoding"] = args.encoding
        if args.procedure is not None:
            config["procedure"] = args.procedure
        primary = orchestrator_factory(auto_load_agents=False)
        if args.operation in {"setup", "inspect", "explain", "site", "agent"}:
            config.update(kind=args.kind, model=args.model, model_endpoint=args.model_endpoint, port=args.port,
                          check_only=args.check, prompt=args.prompt)
            report = primary.rea_assistant_action(config)
        else:
            report = primary.rea_action(config)
    except SystemExit as exc:
        return int(exc.code)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "invalid", "success": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    if args.format == "text":
        from integrations.rea_assistant import explain_report
        print(explain_report(report))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("success") is True else 1
