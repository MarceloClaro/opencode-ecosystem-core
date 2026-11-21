"""R1222: compatibilidade server/discover e manifesto Apps SDK do plugin WSL."""
from __future__ import annotations

import asyncio
import ast
import importlib
import io
import json
from pathlib import Path
import queue
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def bridge():
    return importlib.import_module('integrations.ecosystem_mcp_tunnel')


@pytest.fixture
def plugin():
    return importlib.import_module('integrations.chatgpt_plugin')


@pytest.fixture
def core(tmp_path):
    root = tmp_path / 'core'
    (root / 'integrations').mkdir(parents=True)
    (root / 'integrations/ecosystem_mcp.py').write_text('# fixture\n')
    (root / 'integrations/ecosystem_mcp_tunnel.py').write_text('# fixture\n')
    (root / 'integrations/chatgpt_status_mcp.py').write_text('# fixture\n')
    (root / '.venv/bin').mkdir(parents=True)
    (root / '.venv/bin/python').write_text('# fixture\n')
    return root


def test_discover_result_advertises_only_legacy_protocol(bridge):
    result = bridge.make_discover_result(7)['result']
    assert result['resultType'] == 'complete'
    assert result['supportedVersions'] == ['2025-11-25']
    assert '2026-07-28' not in result['supportedVersions']
    assert result['capabilities'] == {'tools': {'listChanged': False}}
    info = result['_meta']['io.modelcontextprotocol.serverInfo']
    assert info == {'name': 'ecosystem-network', 'version': '1.28.1'}
    assert result['ttlMs'] == 0
    assert result['cacheScope'] == 'private'


def test_process_line_answers_discover_without_child(bridge):
    to_child = []
    to_client = []

    async def send_child(line):
        to_child.append(line)

    async def send_client(line):
        to_client.append(line)

    line = json.dumps({
        'jsonrpc': '2.0',
        'id': 9,
        'method': 'server/discover',
        'params': {'_meta': {'io.modelcontextprotocol.clientInfo': {}}},
    }) + '\n'
    response = asyncio.run(bridge.process_line(line, send_child, send_client))
    parsed = json.loads(response)
    assert parsed['id'] == 9
    assert parsed['result']['supportedVersions'] == ['2025-11-25']
    assert to_child == []
    assert len(to_client) == 1
    assert json.loads(to_client[0]) == parsed


def test_process_line_forwards_only_valid_protocol_messages(bridge):
    sent = []

    async def send(line):
        sent.append(line)

    for line in (
        json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'ping', 'params': {}}) + '\n',
        json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n',
    ):
        assert asyncio.run(bridge.process_line(line, send)) is None
    assert [json.loads(line) for line in sent] == [
        {'jsonrpc': '2.0', 'id': 'tunnel-1', 'method': 'ping', 'params': {}},
        {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
    ]


CORE_NAMES = {
    'ecosystem_agent_profile', 'ecosystem_local_ci', 'ecosystem_knowledge_plan',
    'ecosystem_scientific_run', 'ecosystem_scientific_verify',
    'ecosystem_integration_status', 'ecosystem_rea', 'ecosystem_production',
    'ecosystem_code_context', 'ecosystem_browser', 'ecosystem_scientific_runtime',
    'ecosystem_dataset_download', 'ecosystem_dataset_custom',
    'ecosystem_scientific_plugins', 'ecosystem_gemini_notebook',
    'ecosystem_artifact_handoff', 'ecosystem_skill_plan',
    'ecosystem_claude_bughunter_plan', 'ecosystem_library_search',
    'ecosystem_quantum_catalog', 'ecosystem_knowledge_query',
    'ecosystem_text_spec', 'ecosystem_status', 'ecosystem_route',
    'ecosystem_run', 'ecosystem_workflow', 'ecosystem_workflow_status',
}
READ_NAMES = {
    'ecosystem_integration_status', 'ecosystem_artifact_handoff',
    'ecosystem_skill_plan', 'ecosystem_claude_bughunter_plan',
    'ecosystem_library_search', 'ecosystem_quantum_catalog',
    'ecosystem_knowledge_query', 'ecosystem_status', 'ecosystem_route',
    'ecosystem_workflow_status',
}


def test_core_tools_match_named_contract_without_import_or_call(bridge):
    tree = ast.parse((ROOT / 'integrations/ecosystem_mcp.py').read_text())
    names = {node.name for node in tree.body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
             and any(isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                     and isinstance(dec.func.value, ast.Name)
                     and dec.func.value.id == 'mcp' and dec.func.attr == 'tool'
                     for dec in node.decorator_list)}
    assert names == CORE_NAMES
    assert bridge.CORE_TOOL_NAMES == CORE_NAMES


def test_bridge_end_to_end_discover_initialize_and_tools_with_mock_child(bridge, monkeypatch, tmp_path):
    messages = queue.Queue()
    forwarded = []

    class Input:
        def write(self, line):
            payload = json.loads(line)
            forwarded.append(payload)
            method = payload['method']
            if method == 'initialize':
                result = {'protocolVersion':'2025-11-25',
                          'capabilities':{'tools':{},'resources':{},'prompts':{}},
                          'serverInfo':{'name':'mock-core','version':'test'}}
            elif method == 'tools/list':
                result = {'tools':[{'name':name,'inputSchema':{'type':'object'}}
                                   for name in sorted(CORE_NAMES | {'future_admin','burp_scan'})]}
            elif method == 'tools/call':
                assert payload['params'] == {'name':'ecosystem_integration_status','arguments':{}}
                result = {'content':[{'type':'text','text':'mock-status'}],
                          'structuredContent':{'executed':False,'execution_verified':False}}
            else:
                assert method == 'notifications/initialized'
                return
            messages.put(json.dumps({'jsonrpc':'2.0','id':payload['id'],'result':result})+'\n')

        def flush(self):
            pass

        def close(self):
            messages.put(None)

    class Output:
        def __iter__(self):
            while True:
                line = messages.get(timeout=5)
                if line is None:
                    return
                yield line

    class Child:
        stdin = Input()
        stdout = Output()
        def wait(self, timeout=None):
            return 0

    def popen(argv, **kwargs):
        assert argv[-1] == 'integrations.ecosystem_mcp'
        assert kwargs['stderr'] == bridge.subprocess.DEVNULL
        return Child()

    policy = bridge.ToolPolicy(root=tmp_path, authorizations=tmp_path/'absent')
    session = bridge.TunnelBridge(policy)
    monkeypatch.setattr(bridge, 'TunnelBridge', lambda: session)
    monkeypatch.setattr(bridge.subprocess, 'Popen', popen)
    payloads = [{
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'server/discover',
            'params': {'_meta': {}},
        }, {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2025-11-25',
                'capabilities': {},
                'clientInfo': {'name': 'r1222-probe', 'version': '1.0'},
            },
        }, {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/list', 'params': {}}, {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'ecosystem_integration_status',
                'arguments': {},
            },
        }, {'jsonrpc':'2.0','id':5,'method':'tools/call',
            'params':{'name':'burp_scan','arguments':{}}}]
    output = io.StringIO()
    monkeypatch.setattr(bridge.sys, 'stdin', io.StringIO(''.join(json.dumps(p)+'\n' for p in payloads)))
    monkeypatch.setattr(bridge.sys, 'stdout', output)
    assert bridge.main() == 0
    responses = {p['id']:p for p in map(json.loads,output.getvalue().splitlines())}
    assert responses[1]['result']['supportedVersions'] == ['2025-11-25']
    assert responses[2]['result']['capabilities'] == {'tools':{'listChanged':False}}
    assert {t['name'] for t in responses[3]['result']['tools']} == READ_NAMES
    assert responses[4]['result']['structuredContent'] == {'executed':False,'execution_verified':False}
    assert responses[5]['error']['code'] == -32602
    assert [p['method'] for p in forwarded] == ['initialize','notifications/initialized','tools/list','tools/call']


def test_runner_uses_discovery_bridge_by_default():
    runner = importlib.import_module('integrations.chatgpt_tunnel_full_mcp')
    assert runner.MCP_MODULE == 'integrations.ecosystem_mcp_tunnel'
    assert 'integrations.ecosystem_mcp_tunnel' in runner.build_mcp_command()
    assert (ROOT / 'integrations/ecosystem_mcp_tunnel.py').is_file()


def test_plugin_without_app_id_does_not_invent_mapping(plugin, core, tmp_path):
    dest = tmp_path / 'plugin-sem-app'
    result = plugin.build_plugin(core, dest)
    assert not (dest / '.app.json').exists()
    main = json.loads((dest / 'plugin.json').read_text())
    overlay = json.loads((dest / '.codex-plugin/plugin.json').read_text())
    assert 'apps' not in main
    assert 'apps' not in overlay
    assert '.app.json' not in result['files']


def test_plugin_with_explicit_app_id_maps_apps_sdk(plugin, core, tmp_path):
    dest = tmp_path / 'plugin-com-app'
    result = plugin.build_plugin(core, dest, app_id='plugin_asdk_exemplo')
    app = json.loads((dest / '.app.json').read_text())
    assert app == {'apps': {'opencode-ecosystem-core': {'id': 'plugin_asdk_exemplo'}}}
    main = json.loads((dest / 'plugin.json').read_text())
    overlay = json.loads((dest / '.codex-plugin/plugin.json').read_text())
    assert main['apps'] == app['apps']
    assert overlay['apps'] == './.app.json'
    assert '.app.json' in result['files']


def test_server_config_can_target_status_only(plugin, core):
    config = plugin.server_config(
        core, target='windows-wsl', server_module='integrations.chatgpt_status_mcp')
    assert config['command'] == 'wsl.exe'
    assert config['args'][-1] == 'integrations.chatgpt_status_mcp'
    with pytest.raises(ValueError):
        plugin.server_config(core, server_module='integrations.modulo_nao_permitido')


def test_invalid_app_id_does_not_create_directory(plugin, core, tmp_path):
    dest = tmp_path / 'plugin-id-invalido'
    with pytest.raises(ValueError):
        plugin.build_plugin(core, dest, app_id='x')
    assert not dest.exists()


def test_archive_includes_app_file(plugin, core, tmp_path):
    dest = tmp_path / 'plugin-archive'
    archive = tmp_path / 'plugin.zip'
    plugin.build_plugin(core, dest, app_id='plugin_asdk_exemplo')
    result = plugin.archive_plugin(dest, archive)
    with zipfile.ZipFile(archive) as package:
        names = set(package.namelist())
    assert '.app.json' in names
    assert result['sha256']
