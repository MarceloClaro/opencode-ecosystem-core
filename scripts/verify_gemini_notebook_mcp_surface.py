"""Handshake e operação reais da superfície MCP central, sem conteúdo da conta."""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def run():
    server = StdioServerParameters(command=sys.executable,
                                  args=["-m", "integrations.ecosystem_mcp"], cwd=str(ROOT))
    async with asyncio.timeout(90):
        async with stdio_client(server) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                initialized = await session.initialize()
                tools = await session.list_tools()
                reply = await session.call_tool("ecosystem_gemini_notebook", {"config": {
                    "operation": "mcp", "tool": "server_info", "arguments": {}}})
                result = json.loads(reply.content[0].text)
                receipt = {"scope": "actual_central_mcp_stdio_to_official_server",
                           "central_server": initialized.serverInfo.name,
                           "tool_present": any(tool.name == "ecosystem_gemini_notebook" for tool in tools.tools),
                           "central_tool_count": len(tools.tools), "is_error": reply.isError,
                           "operation_status": result.get("status"),
                           "official_process_executed": result.get("process_executed"),
                           "official_response_sha256": result.get("response_sha256"),
                           "session_id": result.get("session_id"),
                           "persistent_session": result.get("persistent_session", False),
                           "metacognition": result.get("metacognition"),
                           "remote_mutation_executed": False,
                           "reply_sha256": hashlib.sha256(reply.model_dump_json().encode()).hexdigest()}
    path = ROOT / "docs/evidence/R674_REAL_CORE_MCP.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))
    return 0 if receipt["operation_status"] == "completed" and not receipt["is_error"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
