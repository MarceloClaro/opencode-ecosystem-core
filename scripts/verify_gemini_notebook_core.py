"""Provas reais de leitura: grava recibos mínimos, sem conteúdo da conta."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path

from marceloclaro.orchestrator import MarceloClaroOrchestrator

ROOT = Path(__file__).resolve().parents[1]


def _notebook_count(report):
    value = report.get("result")
    if isinstance(value, dict):
        value = value.get("structuredContent", value)
        if "content" in value and value["content"]:
            try:
                value = json.loads(value["content"][0]["text"])
            except (ValueError, KeyError, TypeError):
                return None
        if isinstance(value, dict):
            return value.get("count", value.get("notebook_count", len(value.get("notebooks", []))))
    if isinstance(value, list):
        return len(value)
    return None


def main():
    from mci.metabus import metabus
    core = MarceloClaroOrchestrator(auto_load_agents=False)
    confidence_before = hashlib.sha256(json.dumps(metabus.memory.confidence_ledger, sort_keys=True).encode()).hexdigest()
    probes = [
        {"operation": "status"}, {"operation": "catalog"}, {"operation": "skill"},
        {"operation": "cli", "argv": ["nlm", "login", "--check"]},
        {"operation": "cli", "argv": ["nlm", "notebook", "list", "--json"]},
        {"operation": "mcp", "tool": "server_info", "arguments": {}},
        {"operation": "mcp", "tool": "notebook_list", "arguments": {}},
    ]
    receipts = []
    for config in probes:
        report = core.gemini_notebook_action(**config)
        receipt = {"operation": config["operation"], "tool": config.get("tool"),
                   "command": config.get("argv", []), "status": report.get("status"),
                   "process_executed": report.get("process_executed", False),
                   "hash": report.get("response_sha256", report.get("stdout_sha256", report.get("catalog_sha256", report.get("skill_sha256")))),
                   "metacognition": report.get("metacognition"),
                   "request_sha256": report.get("request_sha256"),
                   "session_id": report.get("session_id", report.get("mcp", {}).get("session_id")),
                   "persistent_session": report.get("persistent_session", report.get("mcp", {}).get("persistent_session", False)),
                   "reason": report.get("reason"), "mcp_tool_count": report.get("mcp_tool_count"),
                   "cli_entry_count": report.get("cli_entry_count")}
        if config.get("tool") == "notebook_list" or "notebook" in config.get("argv", []):
            receipt["notebook_count"] = _notebook_count(report)
        if config.get("argv") == ["nlm", "login", "--check"]:
            receipt["authentication_valid"] = "Authentication valid" in report.get("stdout", "")
        receipts.append(receipt)
        print(json.dumps(receipt, ensure_ascii=False), flush=True)
    versions = {name: importlib.metadata.version(name) for name in ("notebooklm-mcp-cli", "fastmcp", "mcp")}
    manifest = {"scope": "actual_read_only_central_probes", "versions": versions,
                "remote_generation_executed": False, "remote_mutation_executed": False,
                "externally_scientifically_validated": False, "receipts": receipts,
                "confidence_ledger_unchanged": confidence_before == hashlib.sha256(
                    json.dumps(metabus.memory.confidence_ledger, sort_keys=True).encode()).hexdigest()}
    path = ROOT / "docs/evidence/R674_REAL_CENTRAL.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"evidence_path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}))
    return 0 if all(row["status"] in {"completed", "prepared"} for row in receipts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
