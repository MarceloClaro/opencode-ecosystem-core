"""CLI do provider de navegador coordenado; configuração por arquivo JSON."""
import argparse
import json
from pathlib import Path


def run_browser_cli(argv, orchestrator_factory):
    parser = argparse.ArgumentParser(prog="marceloclaro browser")
    parser.add_argument("operation", nargs="?", default="status", choices=("status", "run"))
    parser.add_argument("config_file", nargs="?")
    try:
        args = parser.parse_args(argv)
        if (args.operation == "run") != (args.config_file is not None):
            parser.error("run exige arquivo JSON; status não aceita arquivo")
        config = json.loads(Path(args.config_file).read_text()) if args.config_file else {"operation": "status"}
        if not isinstance(config, dict) or config.get("operation", args.operation) != args.operation:
            raise ValueError("A configuração deve ser objeto com operation correspondente à CLI.")
        config["operation"] = args.operation
        report = orchestrator_factory(auto_load_agents=False).browser_action(config)
    except SystemExit as exc:
        return int(exc.code)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "invalid", "success": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("success") else 1
