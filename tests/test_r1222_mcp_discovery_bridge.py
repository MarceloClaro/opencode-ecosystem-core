"""R1222: compatibilidade server/discover e manifesto Apps SDK do plugin WSL."""
from __future__ import annotations

import asyncio
import importlib
import json
import os
from pathlib import Path
import select
import subprocess
import sys
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
    assert set(result['capabilities']) >= {'tools', 'resources', 'prompts'}
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


def test_process_line_forwards_all_other_messages(bridge):
    sent = []

    async def send(line):
        sent.append(line)

    for line in (
        json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}}) + '\n',
        json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n',
        'linha-invalida\n',
    ):
        assert asyncio.run(bridge.process_line(line, send)) is None
    assert sent == [
        json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}}) + '\n',
        json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n',
        'linha-invalida\n',
    ]


def _write(proc, payload):
    proc.stdin.write(json.dumps(payload, ensure_ascii=False) + '\n')
    proc.stdin.flush()


def _read_response(proc, request_id, timeout=20):
    ready, _, _ = select.select([proc.stdout], [], [], timeout)
    if not ready:
        raise AssertionError(f'sem resposta para id={request_id}')
    while True:
        line = proc.stdout.readline()
        if not line:
            raise AssertionError(f'stdout fechado antes do id={request_id}')
        payload = json.loads(line)
        if payload.get('id') == request_id:
            return payload


def test_bridge_end_to_end_discover_initialize_and_tools(bridge):
    proc = subprocess.Popen(
        [sys.executable, '-B', '-m', 'integrations.ecosystem_mcp_tunnel'],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        _write(proc, {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'server/discover',
            'params': {'_meta': {}},
        })
        discover = _read_response(proc, 1)
        assert discover['result']['supportedVersions'] == ['2025-11-25']

        _write(proc, {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2025-11-25',
                'capabilities': {},
                'clientInfo': {'name': 'r1222-probe', 'version': '1.0'},
            },
        })
        initialize = _read_response(proc, 2)
        assert initialize['result']['protocolVersion'] == '2025-11-25'

        _write(proc, {'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        _write(proc, {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/list', 'params': {}})
        tools = _read_response(proc, 3)
        names = {item['name'] for item in tools['result']['tools']}
        assert len(names) == 26
        assert 'ecosystem_integration_status' in names
        _write(proc, {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'ecosystem_integration_status',
                'arguments': {},
            },
        })
        called = _read_response(proc, 4)
        result = called['result']
        assert result.get('isError') is not True
        report = result.get('structuredContent')
        if not isinstance(report, dict):
            report = json.loads(result['content'][0]['text'])
        assert report['readiness']['state'] == 'CONFIG_ONLY'
        assert report['readiness']['external_clients'] == 'not_observable'
        assert report['executed'] is False
        assert report['execution_verified'] is False
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


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
