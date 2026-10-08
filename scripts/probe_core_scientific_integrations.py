"""R671: CLI, MCP stdio, downloads reais e composição de dados rastreável."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def cli(output, name, operation, config):
    path = output / (name + "-config.json")
    dump(path, config)
    run = subprocess.run([sys.executable, "-m", "marceloclaro.cli", "ciencia", operation,
                          "--config", str(path)], cwd=ROOT, text=True, capture_output=True, timeout=300)
    (output / (name + "-stdout.json")).write_text(run.stdout, encoding="utf-8")
    (output / (name + "-stderr.txt")).write_text(run.stderr, encoding="utf-8")
    result = json.loads(run.stdout)
    print(json.dumps({"phase": name, "status": result.get("status"), "reason": result.get("reason")}), flush=True)
    return result


async def mcp_probe(output):
    params = StdioServerParameters(command=sys.executable, args=["-m", "integrations.ecosystem_mcp"], cwd=str(ROOT))
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            inventory = await session.list_tools()
            call = await session.call_tool("ecosystem_scientific_runtime", {"config": {
                "runtime": "mirofish", "model": "llama3.2:latest",
                "prompt": "Duas personagens sintéticas discutem reprodução científica. Responda brevemente em português e não confunda o cenário com dados observados.",
                "output_dir": str(output / "mcp-mirofish"), "timeout_seconds": 180}})
            report = call.structuredContent
            if not report:
                report = json.loads(next(c.text for c in call.content if c.type == "text"))
            # FastMCP pode envolver o retorno em result conforme sua versão.
            if isinstance(report, dict) and "result" in report and "status" not in report:
                report = report["result"]
            return {"tools": [t.name for t in inventory.tools], "runtime": report,
                    "is_error": call.isError}


def main():
    output = ROOT / "docs/evidence" / ("R671_REAL_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    output.mkdir(exist_ok=False)
    files = ["integrations/live_scientific_runtime.py", "integrations/dataset_cli.py",
             "integrations/scientific_plugins.py", "integrations/ecosystem_mcp.py",
             "marceloclaro/orchestrator.py", "marceloclaro/runtime_actions.py",
             "marceloclaro/science_cli.py", "scripts/probe_core_scientific_integrations.py"]
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files}
    hf = cli(output, "huggingface", "dataset", {"provider": "huggingface", "dataset_id": "scikit-learn/iris",
             "filenames": ["Iris.csv"], "output_dir": str(output / "hf")})
    kaggle = cli(output, "kaggle", "dataset", {"provider": "kaggle", "dataset_id": "uciml/iris",
             "filenames": ["Iris.csv"], "revision": "1", "output_dir": str(output / "kaggle")})
    manifests = [r["manifest_path"] for r in (hf, kaggle) if r.get("status") == "completed"]
    custom = cli(output, "custom", "personalizar", {"source_manifests": manifests,
                 "output_dir": str(output / "custom"), "name": "iris-core-personalizado",
                 "domain": "botanical_measurements", "seed": 668}) if manifests else {"status": "blocked"}
    hermes = cli(output, "hermes", "runtime", {"runtime": "hermes", "model": "llama3.2:latest",
                 "prompt": "Explique em português, em duas frases, por que geração por agente não substitui dados observacionais e como reproduzir uma análise.",
                 "output_dir": str(output / "cli-hermes"), "timeout_seconds": 180})
    mcp = asyncio.run(mcp_probe(output))
    checks = {"hf_download": hf.get("status") == "completed",
              "kaggle_download": kaggle.get("status") == "completed",
              "pinned_versions": hf.get("version_pinned") is True and kaggle.get("version_pinned") is True,
              "custom_real_observations": custom.get("status") == "completed" and custom.get("synthetic") is False,
              "no_split_leakage": custom.get("split_integrity", {}).get("overlap_groups") == 0,
              "cli_hermes": hermes.get("status") == "completed" and hermes.get("inference_executed") is True,
              "mcp_mirofish": mcp["runtime"].get("status") == "completed" and mcp["runtime"].get("inference_executed") is True,
              "central_memory_receipts": all(r.get("metacognition", {}).get("persisted") is True for r in (hf, kaggle, custom, hermes, mcp["runtime"])),
              "code_unchanged": all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == sha for p, sha in hashes.items())}
    report = {"success": all(checks.values()), "checks": checks, "code_sha256": hashes,
              "hf": hf, "kaggle": kaggle, "custom": custom, "cli_hermes": hermes, "mcp": mcp,
              "external_validation": False, "scope": "real_download_and_local_inference_in_synthetic_scenario"}
    dump(output / "probe.json", report)
    print(json.dumps({"success": report["success"], "checks": checks, "evidence": str(output / "probe.json")}), flush=True)
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
