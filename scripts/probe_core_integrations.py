"""Prova R662: configuração, descoberta/emissão e interfaces CLI/MCP reais.

Somente leitura e emissão isolada de instruções. Não executa scripts de skills.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def require(condition: bool, message: str):
    if not condition:
        raise RuntimeError(message)


def unpack(result):
    require(not result.isError, "Ferramenta MCP devolveu erro.")
    if result.structuredContent is not None:
        return result.structuredContent
    return json.loads(next(block.text for block in result.content if block.type == "text"))


async def probe():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from integrations.harness_federation.emit import HarnessEmitter
    from integrations.opencode_cli import build_config
    from reversa_universal.skill_dispatch import ReversaSkillDispatcher
    from transformer.harness_head import HarnessRegistry

    source_files = ("marceloclaro/integration_service.py", "marceloclaro/integration_cli.py",
                    "marceloclaro/orchestrator.py", "integrations/ecosystem_mcp.py",
                    "integrations/opencode_cli.py", "opencode.json")
    result = {"spec_id": "SPEC-935-R662", "ts": datetime.now(timezone.utc).isoformat(),
              "evidence_kind": "real_local_cli_stdio_and_disk_artifacts",
              "skill_scripts_executed": False, "llm_inference": False,
              "code_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                              for name in source_files}}
    generated = json.loads((ROOT / "opencode.json").read_text())
    require(generated == build_config(), "opencode.json diverge do gerador.")
    result["configuration_reproduced"] = True

    registry = HarnessRegistry(repo_root=str(ROOT), kinds=None)
    skill = next(a for a in registry.artifacts() if a.kind == "skill" and a.name == "core-hooks"
                 and Path(a.source_path).is_relative_to(ROOT))
    plan = registry.plan_handoff(skill.artifact_id)
    require(plan["status"] == "ready", "Handoff do artefato recusado.")
    with tempfile.TemporaryDirectory(prefix="r662-emitted-") as directory:
        report = HarnessEmitter(repo_root=directory).emit_skill(skill)
        require(report["status"] == "emitted", "Emissão de instruções falhou.")
        emitted = Path(report["path"])
        decision = ReversaSkillDispatcher(directory, extra_roots=[ROOT]).plan_path(emitted)
        require(decision.found, "Skill emitida não resolvida.")
        require(decision.execution_mode == plan["execution_mode"], "Emissão alterou política de invocação.")
        result["disk_pipeline"] = {"artifact_id": skill.artifact_id,
                                   "source_path": skill.source_path,
                                   "source_file_sha256": skill.source_file_sha256,
                                   "emitted_file_sha256": hashlib.sha256(emitted.read_bytes()).hexdigest(),
                                   "execution_mode": decision.execution_mode,
                                   "support_file_count": len(report.get("support_files", [])),
                                   "emitted": True, "installed_in_host": False,
                                   "executed": False, "temporary_destination_removed": True}
    env = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix="r662-mci-state-") as state:
        env.update({"MCI_STATE_DIR": state, "MCI_AUTOREGISTER": "0"})
        cli_status = subprocess.run([sys.executable, "-m", "marceloclaro.cli", "integracoes", "status"],
                                    cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
        require(cli_status.returncode == 0, "CLI integracoes status falhou.")
        result["cli_status"] = json.loads(cli_status.stdout)
        cli_skill = subprocess.run([sys.executable, "-m", "marceloclaro.cli", "integracoes", "skill", "core-hooks"],
                                   cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
        require(cli_skill.returncode == 0, "CLI integracoes skill falhou.")
        expected_skill = json.loads(cli_skill.stdout)
        params = StdioServerParameters(command=sys.executable,
                                       args=["-m", "integrations.ecosystem_mcp"],
                                       cwd=str(ROOT), env=env)
        async with stdio_client(params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                names = {tool.name for tool in tools}
                require({"ecosystem_integration_status", "ecosystem_artifact_handoff", "ecosystem_skill_plan",
                         "ecosystem_library_search"} <= names, "Ferramentas não expostas no transporte.")
                readonly = {tool.name: tool.annotations.readOnlyHint for tool in tools
                            if tool.name in {"ecosystem_integration_status", "ecosystem_artifact_handoff", "ecosystem_skill_plan"}}
                require(all(readonly.values()), "Ferramentas de consulta sem indicação de leitura.")
                status = unpack(await session.call_tool("ecosystem_integration_status", {}))
                require(status == result["cli_status"], "CLI e MCP divergem no diagnóstico.")
                prepared = unpack(await session.call_tool("ecosystem_skill_plan", {"skill_name": "core-hooks"}))
                require(prepared == expected_skill, "CLI e MCP divergem na política/documento da skill.")
                handed = unpack(await session.call_tool("ecosystem_artifact_handoff", {"artifact_id": skill.artifact_id}))
                require(handed["status"] == "ready" and handed["executed"] is False, "Plano MCP falhou.")
                invalid = await session.call_tool("ecosystem_artifact_handoff", {"artifact_id": "../../secret"})
                require(invalid.isError, "MCP aceitou caminho como ID.")
                books = unpack(await session.call_tool("ecosystem_library_search", {"query": "MCP tools", "top_k": 2}))
                result["mcp_stdio"] = {"tools": sorted(names), "read_only_annotations": readonly,
                                       "status_matches_cli": True, "skill_matches_cli": True,
                                       "skill_file_sha256": prepared["source_file_sha256"],
                                       "handoff_status": handed["status"], "invalid_path_rejected": invalid.isError,
                                       "library_status": books.get("status"), "orchestrator": "marceloclaro"}
    result["success"] = True
    return result


def main():
    try:
        result = asyncio.run(asyncio.wait_for(probe(), timeout=240))
    except Exception as exc:
        result = {"spec_id": "SPEC-935-R662", "success": False,
                  "error_type": type(exc).__name__, "error": str(exc)}
    output = ROOT / "docs/evidence/R662_CORE_INTEGRATIONS_REAL.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"success": result["success"], "output": str(output)}, ensure_ascii=False))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
