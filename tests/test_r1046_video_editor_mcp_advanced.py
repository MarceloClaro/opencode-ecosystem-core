"""R1046: as operações avançadas passam pelo MCP sem shell e com paths confinados."""
import asyncio
import json

import pytest

from integrations import video_editor as ve
from integrations import video_editor_mcp


def text_of(result):
    return '\n'.join(getattr(item, 'text', '') for item in result)


def fixture_project(tmp_path):
    (tmp_path / 'media').mkdir()
    source = tmp_path / 'media/source.mp4'
    source.write_bytes(b'fake-source')
    info = {'path': str(source), 'sha256': ve.file_hash(source),
            'duration_seconds': 1.0,
            'video': {'width': 64, 'height': 48, 'fps': '25/1', 'frames': 25},
            'audio': {'sample_rate': 48000, 'channels': 2}}
    project = ve.project_from_probe('media/source.mp4', info, project_id='demo')
    project['root'] = str(tmp_path)
    project['tracks'] = [{'id': 'v1', 'kind': 'video', 'clips': [
        {'id': 'c1', 'track': 'v1', 'source': 'media/source.mp4',
         'in_frame': 0, 'out_frame': 25, 'start_frame': 0, 'speed': 1,
         'volume': 1}]}]
    (tmp_path / 'editor-projects').mkdir()
    (tmp_path / 'editor-projects/demo.json').write_text(ve.dumps_project(project))
    return source


def test_mcp_plan_exposes_advanced_operation(tmp_path):
    fixture_project(tmp_path)
    server = video_editor_mcp.create_server(tmp_path)
    result = asyncio.run(server.call_tool('editor_plan', {
        'project_id': 'demo', 'operation': 'multitrack',
        'params': {'output': 'out.mp4', 'preset': 'veryfast'}}))
    assert 'planned' in text_of(result)
    plans = list((tmp_path / 'editor-plans').glob('*.json'))
    assert len(plans) == 1
    plan = json.loads(plans[0].read_text())
    assert plan['operation'] == 'multitrack'
    assert plan['encoding']['preset'] == 'veryfast'
    assert plan['advanced_contract']['root'] == str(tmp_path)
    with pytest.raises(Exception):
        asyncio.run(server.call_tool('editor_plan', {
            'project_id': 'demo', 'operation': 'multitrack',
            'params': {'output': '../escape.mp4'}}))


def test_mcp_open_can_record_silent_media_explicitly(tmp_path, monkeypatch):
    (tmp_path / 'media').mkdir()
    media = tmp_path / 'media/silent.mp4'
    media.write_bytes(b'fake-silent')
    monkeypatch.setattr(ve, 'probe_media', lambda path, **kwargs: {
        'path': str(path), 'sha256': 'a' * 64, 'duration_seconds': 1.0,
        'video': {'width': 64, 'height': 48, 'fps': '25/1', 'frames': 25},
        'audio': None})
    server = video_editor_mcp.create_server(tmp_path)
    result = asyncio.run(server.call_tool('editor_open', {
        'media_path': 'media/silent.mp4', 'project_id': 'silent',
        'allow_silent': True}))
    assert 'opened' in text_of(result)
    project = json.loads((tmp_path / 'editor-projects/silent.json').read_text())
    assert project['sources']['media/silent.mp4']['has_audio'] is False
