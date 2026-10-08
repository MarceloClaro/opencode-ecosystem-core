"""Prova de transporte MCP e conclusão real, limitada a um turno de leitura."""
import asyncio
import json
import sys
from pathlib import Path
from datetime import timedelta

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]

def unpack(result):
    structured = getattr(result, "structuredContent", None)
    if structured:
        return structured
    return json.loads(next(block.text for block in result.content if block.type == "text"))

async def main():
    parameters = StdioServerParameters(command=sys.executable,
        args=["-m", "integrations.ecosystem_mcp"], cwd=str(ROOT))
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=150)) as session:
            await session.initialize()
            tools = [tool.name for tool in (await session.list_tools()).tools]
            status = unpack(await session.call_tool("ecosystem_status", {}))
            request = {
                "task": "Explique em duas frases como a atenção roteia agentes no ecossistema. Não use ferramentas nem altere arquivos.",
                "max_steps": 3 if "--default" in sys.argv else 1, "timeout": 75,
            }
            if "--default" not in sys.argv:
                request["ecosystem"] = "codex"
            result = unpack(await session.call_tool("ecosystem_run", request))
            report = {"kind": "real_mcp_execution", "tools": tools,
                      "network_status": status, "result": result}
            path = ROOT / (".backups/r640/network-mcp-default-probe.json" if "--default" in sys.argv
                           else ".backups/r640/network-mcp-probe.json")
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            summary = {key: result.get(key) for key in ("status", "success", "task_id", "agent_id",
                       "ecosystem", "origin_ecosystem", "execution_mode", "steps", "output", "error", "final_grade", "fallbacks")}
            print(json.dumps({"kind": report["kind"], "tools": tools, "result": summary},
                             ensure_ascii=False, indent=2))

asyncio.run(main())
