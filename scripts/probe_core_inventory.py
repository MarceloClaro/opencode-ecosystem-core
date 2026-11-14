#!/usr/bin/env python3
"""Read-only inventory + optional MCP coordinator transport observation.

No tool executions except ecosystem_integration_status (read-only) when --live.
"""
from __future__ import annotations
import argparse
import asyncio
import json
from pathlib import Path
import sys


def flatten(mcps):
    if not isinstance(mcps, dict):
        raise ValueError('mcp must be object')
    out = {}
    for name, entry in mcps.items():
        values = entry.items() if name == 'servers' and isinstance(entry, dict) and 'type' not in entry else [(name, entry)]
        for key, item in values:
            if key in out:
                raise ValueError('duplicate MCP ' + key)
            out[key] = item
    return out


def inventory(root):
    config = json.loads((root/'opencode.json').read_text(encoding='utf-8-sig'))
    agents = config.get('agent')
    if not isinstance(agents, dict):
        raise ValueError('agent map invalid')
    flat = flatten(config.get('mcp'))
    return {
        'schema': 'core-click-inventory/v1',
        'root': str(root),
        'primary_agent': config.get('default_agent'),
        'agent_count_configured': len(agents),
        'mcp_count_configured': len(flat),
        'mcp_names': sorted(flat),
        'mode': 'static',
        'limitations': ['Static count is not server activation or agent inference.'],
    }


async def observe_primary(root):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    interpreter = root/'.venv/bin/python'
    if not interpreter.is_file():
        raise FileNotFoundError(str(interpreter))
    params = StdioServerParameters(command=str(interpreter), args=['-m','integrations.ecosystem_mcp'], cwd=str(root))
    async with asyncio.timeout(65):
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                found = await client.list_tools()
                names = sorted(t.name for t in found.tools)
                result = {
                    'coordinator_transport': 'initialized',
                    'coordinator_tool_count': len(names),
                    'status_tool_declared': 'ecosystem_integration_status' in names,
                    'integration_status_called': False,
                    'observed_tool_names': names,
                }
                if result['status_tool_declared']:
                    call = await client.call_tool('ecosystem_integration_status', {})
                    result['integration_status_called'] = not bool(call.isError)
                    result['integration_status_returned_content_count'] = len(call.content)
                return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--live',action='store_true')
    options = ap.parse_args(argv)
    root = options.root.resolve()
    try:
        result = inventory(root)
    except Exception as exc:
        print(json.dumps({'error_type':type(exc).__name__, 'error':str(exc)[:250]},ensure_ascii=True))
        return 2
    if options.live:
        try:
            result['live'] = asyncio.run(observe_primary(root))
        except Exception as exc:
            result['live'] = {'coordinator_transport':'failed','error_type':type(exc).__name__,'error':str(exc)[:300]}
    print(json.dumps(result,ensure_ascii=True,indent=2,sort_keys=True))
    return 0

if __name__ == '__main__':
    sys.exit(main())
