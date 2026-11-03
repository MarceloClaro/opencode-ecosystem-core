"""R919: contraprovas locais para recibo, mensagem e contexto; sem inferência."""
from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

from integrations import opencode_agent_sdk as sdk


def receipt_module():
    name = 'scripts.build_documentation_receipt'
    assert importlib.util.find_spec(name) is not None, 'Gerador de recibo ausente'
    return importlib.import_module(name)


@pytest.fixture
def document_repo(tmp_path):
    from scripts.build_architecture_maps import build_snapshot

    root = tmp_path / 'repo'
    root.mkdir()
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'core.py').write_text('def run():\n    return 1\n', encoding='utf-8')
    (root / 'opencode.json').write_text('{"model":"ollama-local/llama3.2"}', encoding='utf-8')
    (root / 'README.md').write_text('# Fixture\n', encoding='utf-8')
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.name=fixture', '-c',
                    'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture'], check=True)
    folder = root / 'docs/architecture'
    (folder / 'flows').mkdir(parents=True)
    inventory = build_snapshot(root, source='worktree')
    (folder / 'architecture-inventory.json').write_text(json.dumps(inventory), encoding='utf-8')
    catalog = {'source': {'mode': 'worktree', 'base_commit': inventory['git']['commit'],
                          'worktree_sha256': inventory['git']['worktree_sha256']},
               'flows': [{'id': 'one', 'file': 'flows/one.mmd',
                          'sources': [{'path': 'core.py', 'symbol': 'run', 'line': 1,
                                       'sha256': hashlib.sha256((root/'core.py').read_bytes()).hexdigest()}]}]}
    (folder / 'flows.json').write_text(json.dumps(catalog), encoding='utf-8')
    (folder / 'flows/one.mmd').write_text('flowchart LR\n A --> B\n', encoding='utf-8')
    (folder / 'flows/one.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
    # Artefatos de fixture não são recibos de renderização real.
    for relative in (
        'README.md', 'docs/architecture_map.html',
        'docs/architecture/architecture-inventory.json', 'docs/architecture/flows.json',
        'docs/architecture/dependencies.mmd', 'docs/architecture/mermaid-correspondence.json',
        'docs/architecture/dependencies-mermaid.svg', 'docs/architecture/dependencies.svg',
        'docs/architecture/overview.dot', 'docs/architecture/overview.svg',
        'docs/architecture/curated-overview.svg', 'docs/architecture/viewer-template.html',
        'docs/ARQUITETURA_COMPLETA_CORE_R916.md', 'docs/ESTADO_ATUAL_CORE_R916.md',
        'docs/architecture/MODELOS_E_ECONOMIA_DE_TOKENS_R916.md',
        'docs/architecture/QUANTIZACAO_LOCAL_GITHUB_R916.md',
    ):
        path = root / relative
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture\n', encoding='utf-8')
    return root


def test_receipt_roundtrip_and_check_is_read_only(document_repo):
    module = receipt_module()
    root = document_repo
    assert module.main(['--root', str(root)]) == 0
    path = root / module.DEFAULT_OUTPUT
    before = path.read_bytes()
    receipt = json.loads(before)
    assert receipt['counts']['flows'] == 1
    assert receipt['counts']['source_anchors'] == 1
    assert receipt['render_manifest'][0]['source_path'] == 'docs/architecture/flows/one.mmd'
    assert receipt['render_manifest'][0]['svg_path'] == 'docs/architecture/flows/one.svg'
    assert receipt['externally_validated'] is False
    assert receipt['model_default_changed'] is False
    assert receipt['verification_scope'] == 'current_artifact_hashes_not_runtime_or_render_execution'
    assert module.main(['--root', str(root), '--check']) == 0
    assert path.read_bytes() == before
    receipt['externally_validated'] = True
    path.write_text(json.dumps(receipt), encoding='utf-8')
    assert module.main(['--root', str(root), '--check']) == 1


@pytest.mark.parametrize('relative', ['README.md', 'docs/architecture/flows/one.svg'])
def test_receipt_detects_artifact_drift(document_repo, relative):
    module = receipt_module()
    assert module.main(['--root', str(document_repo)]) == 0
    path = document_repo / module.DEFAULT_OUTPUT
    before = path.read_bytes()
    (document_repo / relative).write_text('changed\n', encoding='utf-8')
    assert module.main(['--root', str(document_repo), '--check']) == 1
    assert path.read_bytes() == before


@pytest.mark.parametrize('kind', ['source', 'catalog'])
def test_receipt_rejects_stale_source_or_catalog(document_repo, kind):
    module = receipt_module()
    if kind == 'source':
        (document_repo / 'core.py').write_text('def run():\n    return 2\n', encoding='utf-8')
    else:
        path = document_repo / 'docs/architecture/flows.json'
        catalog = json.loads(path.read_text())
        catalog['source']['worktree_sha256'] = '0' * 64
        path.write_text(json.dumps(catalog), encoding='utf-8')
    assert module.main(['--root', str(document_repo)]) == 2
    assert not (document_repo / module.DEFAULT_OUTPUT).exists()


@pytest.mark.parametrize('kind', ['traversal', 'duplicate_id', 'duplicate_file', 'symlink'])
def test_receipt_rejects_unsafe_or_duplicate_flow(document_repo, kind):
    module = receipt_module()
    path = document_repo / 'docs/architecture/flows.json'
    catalog = json.loads(path.read_text())
    flow = catalog['flows'][0]
    if kind == 'traversal':
        flow['file'] = '../../README.md'
    elif kind == 'duplicate_id':
        catalog['flows'].append(copy.deepcopy(flow))
    elif kind == 'duplicate_file':
        catalog['flows'].append({**copy.deepcopy(flow), 'id': 'two'})
    else:
        svg = document_repo / 'docs/architecture/flows/one.svg'
        svg.unlink()
        svg.symlink_to(document_repo / 'README.md')
    path.write_text(json.dumps(catalog), encoding='utf-8')
    assert module.main(['--root', str(document_repo)]) == 2
    assert not (document_repo / module.DEFAULT_OUTPUT).exists()


@pytest.mark.parametrize('destination', ['README.md', '../outside.json', 'docs/architecture/flows/one.mmd'])
def test_receipt_does_not_overwrite_artifacts(document_repo, destination):
    module = receipt_module()
    readme = (document_repo / 'README.md').read_bytes()
    assert module.main(['--root', str(document_repo), '--output', destination]) == 2
    assert (document_repo / 'README.md').read_bytes() == readme


@pytest.mark.parametrize('message,valid', [
    (None, False), ([], False), ('secret-provider-content', False),
    ({'content': {'unexpected': 1}}, False), ({'content': 7}, False),
    ({'content': 'ok', 'tool_calls': {}}, False),
    ({'content': 'ok', 'tool_calls': [{'id': 'x'}]}, False),
    ({'content': 'ok'}, True), ({'content': None, 'tool_calls': []}, True),
])
def test_chat_once_rejects_malformed_message(monkeypatch, message, valid):
    monkeypatch.setattr(sdk, '_http_json_detailed', lambda *_a, **_k: {
        'ok': True, 'http_status': 200, 'data': {'choices': [{'message': message}]}})
    try:
        answer = sdk.chat_once([{'role': 'user', 'content': 'secret-prompt'}],
                               'mock', 'http://localhost:9379/v1')
    except Exception as exc:
        assert False, f'Resposta malformada escapou como {type(exc).__name__}'
    assert answer['ok'] is valid
    if not valid:
        assert answer['code'] == 'invalid_provider_response'
        assert 'secret' not in str(answer)


def test_invalid_response_emits_only_error(monkeypatch):
    monkeypatch.setattr(sdk, '_http_json_detailed', lambda *_a, **_k: {
        'ok': True, 'http_status': 200,
        'data': {'choices': [{'message': {'content': {'secret': 'private'}}}]}})
    events = list(sdk.query('short', {'base_url': 'http://localhost:9379/v1', 'model': 'mock'}))
    assert [event['type'] for event in events] == ['error']
    assert events[0]['code'] == 'invalid_provider_response'
    assert 'private' not in str(events)


@pytest.mark.parametrize('via_env', [False, True])
def test_ollama_preflight_independent_of_configuration_source(monkeypatch, via_env):
    base = 'http://localhost:11434/v1'
    monkeypatch.setenv('OPENCODE_SDK_BASE_URL', base)
    monkeypatch.setenv('OPENCODE_SDK_MODEL', 'llama3.2')
    monkeypatch.setattr(sdk, 'provider_healthy', lambda *_a, **_k: True)
    monkeypatch.setattr(sdk, '_probe_ollama_context', lambda *_a, **_k: {
        'ok': True, 'context_window': 2048, 'source': 'ollama_api_show_modelfile_num_ctx'})
    sent = []
    monkeypatch.setattr(sdk, 'chat_once', lambda *_a, **_k: sent.append(1) or {'ok': True, 'content': 'ok'})
    opts = {'max_output_tokens': 512, 'context_safety_tokens': 128}
    if not via_env:
        opts.update(base_url=base, model='llama3.2')
    events = list(sdk.query('x' * 9000, opts))
    error = next((e for e in events if e['type'] == 'error'), None)
    assert error is not None and error.get('code') == 'context_budget_exceeded'
    assert not sent


def tool_conversation(monkeypatch, output, context_window):
    monkeypatch.setitem(sdk._TOOLS, 'large', {
        'description': '', 'parameters': {'type': 'object'}, 'fn': lambda _args: output})
    sent = []

    def fake_chat(messages, *_args, **_kwargs):
        sent.append(copy.deepcopy(messages))
        if messages[-1]['role'] == 'tool':
            return {'ok': True, 'content': 'ok'}
        return {'ok': True, 'tool_calls': [{'id': 'c1', 'type': 'function',
            'function': {'name': 'large', 'arguments': '{}'}}]}

    monkeypatch.setattr(sdk, 'chat_once', fake_chat)
    events = list(sdk.query('Execute large.', {'base_url': 'http://localhost:9379/v1',
        'model': 'mock', 'allowed_tools': ['large'], 'context_window': context_window,
        'max_turns': 2, 'max_output_tokens': 128}))
    return events, sent


@pytest.mark.parametrize('size', [10, 5000])
def test_tool_message_preserves_output_that_fits_context(monkeypatch, size):
    output = {'payload': 'x' * size}
    events, sent = tool_conversation(monkeypatch, output, 8192)
    assert next(e for e in events if e['type'] == 'tool_use')['output'] == output
    assert len(sent) == 2
    assert sent[1][-1]['content'] == json.dumps(output, ensure_ascii=False)
    assert events[-1] == {'type': 'result', 'finish': 'stop'}


def test_large_tool_output_blocks_next_request_without_truncation(monkeypatch):
    output = {'payload': 'x' * 12000}
    events, sent = tool_conversation(monkeypatch, output, 2048)
    assert next(e for e in events if e['type'] == 'tool_use')['output'] == output
    error = next((e for e in events if e['type'] == 'error'), None)
    assert error is not None and error.get('code') == 'context_budget_exceeded'
    assert len(sent) == 1
    assert not any(e['type'] == 'result' for e in events)
