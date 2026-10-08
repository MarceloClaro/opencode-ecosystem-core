"""Valida a configuração resolvida sem registrar valores de credenciais."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from integrations.harness_runtime import HarnessRuntime

runtime = HarnessRuntime()
with tempfile.TemporaryFile(mode="w+") as stream:
    subprocess.run([runtime._resolve_cli("opencode"), "debug", "config"],
                   stdout=stream, stderr=subprocess.PIPE, text=True, timeout=45,
                   cwd=runtime.repo_root, check=True)
    stream.seek(0)
    config = json.load(stream)
summary = {"default_agent": config.get("default_agent"),
           "network_enabled": config.get("mcp", {}).get("ecosystem-network", {}).get("enabled"),
           "mcp_count": len(config.get("mcp", {})),
           "command_present": "ecosystem" in config.get("command", {})}
print(json.dumps(summary, ensure_ascii=False, indent=2))
Path(".backups/r640/effective-config.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
