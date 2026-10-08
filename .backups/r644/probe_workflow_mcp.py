"""Prova real de duas etapas, transporte MCP e retomada sem repetição."""
import asyncio
from datetime import timedelta
import json
from pathlib import Path
import sys
from uuid import uuid4

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]


def unpack(result):
    if getattr(result, "isError", False):
        raise RuntimeError(str(result.content))
    return result.structuredContent or json.loads(next(item.text for item in result.content if item.type == "text"))


async def main():
    marker = "R644_TRANSFER_" + uuid4().hex[:12]
    nodes = [
        {"id": "analysis", "task": "Resuma em três frases a diferença entre roteamento inspirado em atenção e treinamento de uma rede Transformer. Inclua este código de rastreamento na entrega: " + marker + ". Não use ferramentas nem altere arquivos.",
         "required_capabilities": ["summarize"], "ecosystem": "codex"},
        {"id": "review", "task": "Revise a entrega da análise anterior. Identifique eventual exagero sobre rede neural e sugira uma formulação correta em até três frases. Repita o código de rastreamento recebido na entrega da dependência. Não use ferramentas nem altere arquivos.",
         "dependencies": ["analysis"], "required_capabilities": ["review"], "ecosystem": "antigravity"},
    ]
    params = StdioServerParameters(command=sys.executable, args=["-m", "integrations.ecosystem_mcp"], cwd=str(ROOT))
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=240)) as session:
            await session.initialize()
            tools = [tool.name for tool in (await session.list_tools()).tools]
            result = unpack(await session.call_tool("ecosystem_workflow", {"nodes": nodes, "max_steps": 2, "timeout": 180}))
            before = unpack(await session.call_tool("ecosystem_status", {}))
            resumed = unpack(await session.call_tool("ecosystem_workflow", {
                "nodes": nodes, "max_steps": 2, "timeout": 30, "workflow_id": result["workflow_id"], "resume": True}))
            after = unpack(await session.call_tool("ecosystem_status", {}))
            status = unpack(await session.call_tool("ecosystem_workflow_status", {"workflow_id": result["workflow_id"]}))
            attempts_before = {key: value.get("health", {}).get("last_attempt_at")
                               for key, value in before["runtime"]["executors"].items()}
            attempts_after = {key: value.get("health", {}).get("last_attempt_at")
                              for key, value in after["runtime"]["executors"].items()}
            reused = ({key: value.get("task_id") for key, value in result["nodes"].items()} ==
                      {key: value.get("task_id") for key, value in resumed["nodes"].items()})
            verified = (result["status"] == "completed" and resumed["status"] == "completed"
                        and reused and attempts_before == attempts_after and status["steps"] == 2
                        and marker in result["nodes"]["analysis"]["output"]
                        and marker in result["nodes"]["review"]["output"])
            report = {"kind": "real_mcp_two_node_workflow", "tools": tools, "result": result,
                      "resumed": resumed, "status": status, "health_before": attempts_before,
                      "health_after": attempts_after, "resume_reused_tasks": reused,
                      "resume_no_new_executor_attempts": attempts_before == attempts_after,
                      "dependency_marker": marker, "verified": verified}
            (ROOT / ".backups/r644/workflow-mcp-probe.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            summary = {"verified": verified, "workflow_id": result["workflow_id"], "status": result["status"],
                       "steps": result["steps"], "resume_no_new_executor_attempts": attempts_before == attempts_after,
                       "nodes": {key: {"status": node["status"], "task_id": node.get("task_id"),
                                       "agent_id": (node.get("result") or {}).get("agent_id"),
                                       "ecosystem": (node.get("result") or {}).get("ecosystem"),
                                       "output": node.get("output"), "error": node.get("error")}
                                 for key, node in result["nodes"].items()}}
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            if not verified:
                raise SystemExit(1)


asyncio.run(main())
