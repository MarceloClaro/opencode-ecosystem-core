"""Prova R670: requisições centrais e recibos de chamadas reais do host."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/evidence/R670_HOST_REAL"
WOLFRAM = '''p={{{3,3},{0,5}},{{5,0},{1,1}}}; profiles=Tuples[Range[2],2];
nash=Select[profiles,Function[s,And@@Table[p[[s[[1]],s[[2]],i]]>=Max[Table[Extract[p,Append[ReplacePart[s,i->a],i]],{a,2}]],{i,2}]]];
pareto=Select[profiles,Function[s,Not[AnyTrue[profiles,Function[t,And@@Thread[Extract[p,t]>=Extract[p,s]]&&Or@@Thread[Extract[p,t]>Extract[p,s]]]]]]];
ExportString[<|"pure_nash"->nash,"pareto_profiles"->pareto|>,"JSON"]'''
CONFIGS = {
    "wolfram": {"plugin_id": "wolfram", "action": "evaluate", "arguments": {"code": WOLFRAM, "timeConstraint": 30}},
    "genomic": {"plugin_id": "genomic-intelligence", "action": "list_models", "arguments": {"task": "promoter"}},
    "ngs": {"plugin_id": "ngs-analysis-workbench", "action": "targets", "arguments": {}},
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def call(name, config):
    path = OUT / (name + "-config.json")
    dump(path, config)
    process = subprocess.run([sys.executable, "-m", "marceloclaro.cli", "ciencia", "plugins", "--config", str(path)],
                             cwd=ROOT, text=True, capture_output=True, timeout=60)
    result = json.loads(process.stdout)
    dump(OUT / (name + "-result.json"), result)
    if process.returncode:
        raise RuntimeError(name + ": " + result.get("reason", result.get("status", "failed")))
    return result


def main():
    OUT.mkdir(exist_ok=True)
    if sys.argv[1:] == ["prepare"]:
        for name, config in CONFIGS.items():
            path = OUT / (name + "-request-result.json")
            result = json.loads(path.read_text()) if path.exists() else call(name + "-request", {"operation": "request", **config})
            print(json.dumps({"name": name, "request": result}, ensure_ascii=False))
        return
    if sys.argv[1:] != ["accept"]:
        raise ValueError("Use prepare ou accept; não chama conectores opacos no WSL")
    results = {}
    for name in CONFIGS:
        request = json.loads((OUT / (name + "-request-result.json")).read_text())
        response = json.loads((OUT / (name + "-host-response.json")).read_text())
        # As respostas vêm das ferramentas efetivamente chamadas no host Codex.
        existing = call(name + "-lookup", {"operation": "result", "request_id": request["request_id"]})
        receipt = existing if existing.get("status") != "awaiting_host" else call(name + "-receipt", {
            "operation": "response", "request_id": request["request_id"],
            "request_sha256": request["request_sha256"], "host_tool": request["host_tool"],
            "result": response, "reported_by": "Codex desktop authenticated MCP host"})
        results[name] = receipt
    results["registry"] = call("registry", {"operation": "status"})
    for action in ("version", "auth_status"):
        results["boltz_" + action] = call("boltz-" + action, {"operation": "local", "plugin_id": "boltz-api-cli", "action": action})
    results["pubmed"] = call("pubmed", {"operation": "local", "plugin_id": "life-sciences-literature",
                            "action": "pubmed_search", "arguments": {"term": "reproducibility AND machine learning"}})
    text = results["wolfram"]["result"]["content"][0]["text"]
    wolfram = json.loads(json.loads(text.split("=", 1)[1].strip()))
    genomic = results["genomic"]["result"]["structuredContent"]
    ngs = results["ngs"]["result"]["structuredContent"]
    checks = {"host_receipts": all(results[n].get("status") == "completed" and results[n].get("host_reported_execution") is True for n in CONFIGS),
              "wolfram_game_computed": wolfram["pure_nash"] == [[2, 2]] and sorted(wolfram["pareto_profiles"]) == [[1, 1], [1, 2], [2, 1]],
              "genomic_catalog_read": genomic["task"] == "promoter" and bool(genomic["models"]),
              "ngs_infrastructure_read": ngs["count"] == len(ngs["targets"]) and ngs["count"] > 0,
              "all_packages_imported": all(p.get("instructions_installed") is True for p in results["registry"]["plugins"]),
              "boltz_authenticated": results["boltz_auth_status"]["exit_code"] == 0,
              "boltz_installed": results["boltz_version"]["status"] == "completed",
              "pubmed_executed": results["pubmed"]["status"] == "completed",
              "no_external_claim": all(results[n].get("external_validation") is False for n in CONFIGS)}
    report = {"success": all(checks.values()), "checks": checks, "results": results,
              "code_sha256": hashlib.sha256((ROOT / "integrations/scientific_plugins.py").read_bytes()).hexdigest(),
              "scope": "Actual host computation/catalog/infrastructure; local Boltz auth/version and PubMed search. No molecular prediction, NGS run or grant creation."}
    dump(OUT / "probe.json", report)
    print(json.dumps({"success": report["success"], "checks": checks, "evidence": str(OUT / "probe.json")}))
    if not report["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
