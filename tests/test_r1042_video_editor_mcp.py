"""MCP do editor universal: catálogo pequeno, caminhos confinados, render só com aprovação."""
import asyncio
import importlib
import json
from pathlib import Path

import pytest


def api():
    return importlib.import_module('integrations.video_editor_mcp')


def fixture_root(tmp_path):
    (tmp_path / 'media').mkdir()
    (tmp_path / 'media' / 'source.mp4').write_bytes(b'fake-media')
    return tmp_path


def text_of(result):
    return '\n'.join(getattr(item, 'text', '') for item in result)


def test_catalog_and_root_required(tmp_path, monkeypatch):
    monkeypatch.delenv('EDITOR_PROJECT_ROOT', raising=False)
    with pytest.raises(ValueError):
        api().create_server()
    server = api().create_server(fixture_root(tmp_path))
    tools = asyncio.run(server.list_tools())
    assert {t.name for t in tools} == {
        'editor_open', 'editor_list_projects', 'editor_plan',
        'editor_render', 'editor_status'}
    for tool in tools:
        assert tool.annotations.openWorldHint is False
        assert 'command' not in tool.inputSchema.get('properties', {})


def test_open_confined_and_project_written(tmp_path, monkeypatch):
    from integrations import video_editor
    root = fixture_root(tmp_path)
    monkeypatch.setattr(video_editor, 'probe_media', lambda path: {
        'path': str(path), 'sha256': 'a' * 64, 'duration_seconds': 1.0,
        'video': {'width': 1280, 'height': 720, 'fps': '25/1', 'frames': 25},
        'audio': {'sample_rate': 48000, 'channels': 2}})
    server = api().create_server(root)
    result = asyncio.run(server.call_tool('editor_open', {
        'media_path': 'media/source.mp4', 'project_id': 'demo'}))
    assert 'opened' in text_of(result)
    project = json.loads((root / 'editor-projects' / 'demo.json').read_text())
    assert project['sources']['media/source.mp4']['frames'] == 25
    with pytest.raises(Exception):
        asyncio.run(server.call_tool('editor_open', {
            'media_path': '../escape.mp4', 'project_id': 'bad'}))


def test_plan_confines_output_and_returns_small_summary(tmp_path):
    root = fixture_root(tmp_path)
    server = api().create_server(root)
    (root / 'editor-projects').mkdir()
    project = {'schema_version': 1, 'version': 'R1042-1', 'project_id': 'demo',
               'root': str(root), 'fps': [25, 1], 'width': 1280, 'height': 720,
               'sample_rate': 48000, 'channels': 2,
               'sources': {'media/source.mp4': {'path': str(root / 'media/source.mp4'),
                   'sha256': 'a' * 64, 'frames': 25, 'fps': [25, 1]}},
               'tracks': [{'id': 'v1', 'kind': 'video', 'clips': [
                   {'id': 'c1', 'track': 'v1', 'source': 'media/source.mp4',
                    'in_frame': 0, 'out_frame': 25, 'start_frame': 0, 'speed': 1.0,
                    'volume': 1.0}]}]}
    (root / 'editor-projects' / 'demo.json').write_text(json.dumps(project))
    answer = asyncio.run(server.call_tool('editor_plan', {
        'project_id': 'demo', 'operation': 'trim',
        'params': {'clip_id': 'c1', 'output': 'out.mp4'}}))
    text = text_of(answer)
    assert 'plan_id' in text and len(text) < 6000
    with pytest.raises(Exception):
        asyncio.run(server.call_tool('editor_plan', {
            'project_id': 'demo', 'operation': 'trim',
            'params': {'clip_id': 'c1', 'output': '../escape.mp4'}}))


def test_render_requires_operator_approval(tmp_path, monkeypatch):
    from integrations import video_editor
    root = fixture_root(tmp_path)
    server = api().create_server(root)
    (root / 'editor-plans').mkdir()
    plan_id = 'b' * 16
    plan = {'operation': 'trim', 'backend': 'ffmpeg', 'output': str(root / 'out.mp4'),
            'args': ['ffmpeg', '{output}'], 'expected_frames': 25,
            'frame_tolerance': 0, 'warnings': [], 'limitations': [],
            'plan_sha256': 'b' * 64}
    (root / 'editor-plans' / f'{plan_id}.json').write_text(json.dumps(plan))
    calls = []
    monkeypatch.setattr(video_editor, 'render',
                        lambda p, **k: calls.append((p, k)) or {'status': 'rendered'})
    dry = asyncio.run(server.call_tool('editor_render', {
        'plan_id': plan_id, 'dry_run': True}))
    assert 'rendered' in text_of(dry) and len(calls) == 1
    assert calls[0][1].get('dry_run') is True
    with pytest.raises(Exception):
        asyncio.run(server.call_tool('editor_render', {
            'plan_id': plan_id, 'dry_run': False}))
    assert len(calls) == 1
    (root / 'editor-approvals').mkdir()
    (root / 'editor-approvals' / f'{plan_id}.json').write_text(json.dumps({
        'approved': True, 'reviewer': 'operator', 'plan_sha256': 'b' * 64}))
    allowed = asyncio.run(server.call_tool('editor_render', {
        'plan_id': plan_id, 'dry_run': False}))
    assert 'rendered' in text_of(allowed) and len(calls) == 2
    (root / 'editor-approvals' / f'{plan_id}.json').write_text(json.dumps({
        'approved': True, 'reviewer': 'operator', 'plan_sha256': 'c' * 64}))
    with pytest.raises(Exception):
        asyncio.run(server.call_tool('editor_render', {
            'plan_id': plan_id, 'dry_run': False}))
