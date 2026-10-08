"""Prova opt-in com processos externos e Ollama real; nunca usada como mock."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integrations.live_scientific_runtime import LiveScientificRuntime  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="llama3.2:latest")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--runtime", choices=("hermes", "mirofish", "both"), default="both")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "integrations/live_scientific_runtime.py"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    output = root / "docs/evidence" / ("R667_REAL_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    output.mkdir(exist_ok=False)
    prompt = ("Uma equipe compara duas técnicas de pesquisa. Analise como distinguir uma simulação de dois agentes "
              "de dados observacionais reais e sugira uma verificação de reprodutibilidade. Não faça previsões factuais. "
              "Responda em português com até três frases.")
    results = {}
    runtimes = ("hermes", "mirofish") if args.runtime == "both" else (args.runtime,)
    for runtime in runtimes:
        result = LiveScientificRuntime().run({"runtime": runtime, "prompt": prompt, "model": args.model,
            "output_dir": str(output / runtime), "timeout_seconds": args.timeout})
        results[runtime] = result
        print(json.dumps({"runtime": runtime, "status": result["status"], "model_calls": result.get("model_calls", 0),
                          "inference_executed": result["inference_executed"], "reason": result.get("reason")}, ensure_ascii=False), flush=True)
    checks = {name + "_executed": result["status"] == "completed" and result["external_process_executed"] and result["inference_executed"]
              for name, result in results.items()}
    checks["code_unchanged_during_probe"] = before == hashlib.sha256(source.read_bytes()).hexdigest()
    report = {"checks": checks, "success": all(checks.values()), "results": results,
              "adapter_sha256": before, "model": args.model, "model_provider": "Ollama loopback", "scope": "external_runtime_inference_and_synthetic_scenario"}
    (output / "probe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"success": report["success"], "evidence": str(output / "probe.json")}, ensure_ascii=False), flush=True)
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
