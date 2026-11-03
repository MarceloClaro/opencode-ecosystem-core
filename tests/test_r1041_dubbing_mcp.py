"""MCP real e ferramentas pequenas, sem comandos livres nem caminhos do cliente."""
import asyncio
import importlib
import json
import os
from pathlib import Path
import sys

import pytest


def api():
    return importlib.import_module('integrations.dubbing_mcp')


def test_catalog_small_and_annotations(tmp_path):
    server = api().create_server(tmp_path)
    tools = asyncio.run(server.list_tools())
    names = {t.name for t in tools}
    assert names == {'dubbing_status', 'dubbing_prepare', 'dubbing_part', 'dubbing_audit_pilot'}
    for t in tools:
        assert t.annotations.openWorldHint is False
        assert t.annotations.destructiveHint is False
        assert t.annotations.readOnlyHint is (t.name != 'dubbing_prepare')
        assert 'root' not in t.inputSchema.get('properties', {})
        assert 'command' not in t.inputSchema.get('properties', {})


def test_missing_operator_root_fails_closed(monkeypatch):
    monkeypatch.delenv('DUBBING_PROJECT_ROOT', raising=False)
    with pytest.raises(ValueError): api().create_server()


def test_bounded_call_and_reject_traversal(tmp_path, monkeypatch):
    from integrations import dubbing_batch
    seen = []
    monkeypatch.setattr(dubbing_batch, 'status', lambda root: {'status': 'not_prepared'})
    monkeypatch.setattr(dubbing_batch, 'part', lambda *args: seen.append(args))
    server = api().create_server(tmp_path)
    answer = asyncio.run(server.call_tool('dubbing_status', {}))
    assert len(str(answer)) < 4000
    with pytest.raises(Exception):
        asyncio.run(server.call_tool('dubbing_part', {'part_id': '../../secret'}))
    assert not seen


def test_stdio_roundtrip(tmp_path):
    api()  # RED is missing implementation, not failure starting a process.
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    (tmp_path/'parts-plan-final').mkdir()
    (tmp_path/'analysis').mkdir()
    (tmp_path/'parts-plan-final/segments.json').write_text(json.dumps({
        'fps': '25/1', 'total_frames': 25, 'segments': [
            {'id': 'test-P0001', 'start_frame': 0, 'end_frame': 25}]}))
    (tmp_path/'analysis/asr-tr.json').write_text(json.dumps({'duration': 1, 'segments': []}))

    async def check():
        params = StdioServerParameters(command=sys.executable,
            args=['-m', 'integrations.dubbing_mcp'],
            cwd=str(Path(__file__).resolve().parents[1]),
            env={**os.environ, 'DUBBING_PROJECT_ROOT': str(tmp_path)})
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                catalog = await client.list_tools()
                assert len(catalog.tools) == 4
                result = await client.call_tool('dubbing_prepare', {})
                assert not result.isError
                result = await client.call_tool('dubbing_status', {})
                assert not result.isError
                text = '\n'.join(getattr(c, 'text', '') for c in result.content)
                assert 'prepared_not_dubbed' in text and len(text) < 6000
                denied = await client.call_tool('dubbing_part', {'part_id': '../escape'})
                assert denied.isError
    asyncio.run(check())
