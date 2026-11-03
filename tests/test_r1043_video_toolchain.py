"""R1043: registro de ferramentas/modelos, licenças e recomendações locais."""
import importlib
import json
from pathlib import Path

import pytest


def api():
    return importlib.import_module('integrations.video_toolchain')


def test_registry_is_valid_and_unique():
    m = api()
    report = m.validate_registry()
    assert report['count'] >= 30
    assert 'ffmpeg' in report['ids'] and 'remotion' in report['ids']
    rows = {row['id']: row for row in m.REGISTRY}
    assert rows['remotion']['status'] == 'integrated'
    assert rows['ffmpeg']['adapter'] == 'integrations.video_editor'


def test_recommend_diarization_and_animation():
    m = api()
    diar = {row['id'] for row in m.recommend('diarization')}
    assert 'pyannote-3-1' in diar
    anim = {row['id'] for row in m.recommend('animation')}
    assert 'remotion' in anim and 'motion-canvas' in anim
    dubbing = {row['id'] for row in m.recommend('dubbing')}
    assert 'videolingo' in dubbing


def test_license_gate_blocks_unknown_and_copyleft():
    m = api()
    by_id = {row['id']: row for row in m.REGISTRY}
    assert m.can_integrate(by_id['baocut'])['allow'] is False
    assert m.can_integrate(by_id['moviepy'])['allow'] is True
    assert m.can_integrate(by_id['openchatcut'])['allow'] is False
    assert m.can_integrate(by_id['openchatcut'],
                           accepted_licenses=('openchatcut',))['allow'] is True
    assert m.can_integrate(by_id['ffmpeg'])['allow'] is False
    assert m.can_integrate(by_id['ffmpeg'], accepted_licenses=('ffmpeg',))['allow'] is True
    assert m.can_integrate(by_id['xtts-v2'])['allow'] is False


def test_detect_has_no_execution_claim():
    m = api()
    detected = m.detect()
    assert set(detected) == {'system', 'modules', 'note'}
    assert 'ffmpeg' in detected['system']
    assert 'execução' in detected['note']


def test_export_is_json_serializable():
    m = api()
    payload = json.loads(m.to_json())
    assert payload['validation']['count'] == len(m.REGISTRY)
    assert payload['detected']['system']['ffmpeg'] is True


def test_extracted_skill_and_manifest_exist():
    root = Path(__file__).resolve().parents[1]
    skill = root / '.opencode/skills/video-editor-universal'
    assert (skill / 'SKILL.md').is_file()
    for name in ('modelos-e-comandos.md', 'claude-skills-extraidas.md',
                 'toolchain.md', 'claude-skills-manifest.json'):
        assert (skill / 'references' / name).is_file()
    manifest = json.loads((skill / 'references/claude-skills-manifest.json').read_text())
    assert len(manifest['skills']) == 10
    assert all(len(row['tree_sha256']) == 64 for row in manifest['skills'])
    assert 'Tiago Lemos' in manifest['attribution']
    assert 'Tiago Lemos' in (skill / 'SKILL.md').read_text()
