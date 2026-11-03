"""R1046: contratos negativos e planos antes da implementação; CPU local."""
import copy
import json
from pathlib import Path

import pytest

from integrations import video_editor as ve


def project(tmp_path):
    sources = {}
    for name in ('red', 'blue'):
        p = tmp_path / (name + '.mp4')
        p.write_bytes(name.encode())
        sources[name] = {'path': str(p), 'sha256': ve.file_hash(p),
                         'frames': 50, 'fps': [25, 1], 'width': 64, 'height': 48,
                         'has_audio': True, 'variable_frame_rate': False}
    return {'schema_version': 1, 'version': ve.VERSION, 'project_id': 'fixture',
            'root': str(tmp_path), 'fps': [25, 1], 'width': 64, 'height': 48,
            'sample_rate': 48000, 'channels': 2, 'sources': sources,
            'tracks': [{'id': 'v1', 'kind': 'video', 'clips': [clip('c1', 'red', 'v1')]},
                       {'id': 'v2', 'kind': 'video', 'clips': [clip('c2', 'blue', 'v2', 25)]},
                       {'id': 'a1', 'kind': 'audio', 'clips': [clip('a1', 'red', 'a1', 25)]}]}


def clip(cid, source, track, start=0, end=50):
    return {'id': cid, 'source': source, 'track': track, 'in_frame': 0,
            'out_frame': end, 'start_frame': start, 'speed': 1, 'volume': 1}


def plan(p, operation, **params):
    return ve.plan(p, operation, {'output': str(Path(p['root']) / 'out.mp4'), **params})


def test_multitrack_plan_frames_z_order_audio_and_no_mutation(tmp_path):
    p = project(tmp_path)
    p['tracks'][1]['clips'][0]['transform'] = {'x': 16, 'y': 8, 'width': 32, 'height': 24, 'opacity': .5}
    before = copy.deepcopy(p)
    result = plan(p, 'multitrack')
    assert p == before
    assert result['expected_frames'] == 75
    assert result['frame_tolerance'] == 0
    graph = result['args'][result['args'].index('-filter_complex') + 1]
    assert 'overlay=' in graph and 'repeatlast=0' in graph
    assert 'adelay=48000S' in graph and 'amix=' in graph
    assert result['advanced_contract']['version'] == 1
    assert len(result['inputs']) == 2


def test_transition_frame_arithmetic_and_color_plan(tmp_path):
    p = project(tmp_path)
    result = plan(p, 'transition', clip_ids=['c1', 'c2'], duration_frames=10, effect='fade')
    assert result['expected_frames'] == 90
    assert 'xfade=transition=fade:duration=0.4:offset=1.6' in ' '.join(result['args'])
    assert 'acrossfade=' in ' '.join(result['args'])
    grade = plan(p, 'color_grade', clip_id='c1', color={'brightness': .1, 'saturation': 0, 'rm': .2})
    assert grade['expected_frames'] == 50
    assert 'eq=' in ' '.join(grade['args']) and 'colorbalance=' in ' '.join(grade['args'])


@pytest.mark.parametrize('effect', ['fade;movie=/etc/passwd', 'custom', 'unknown'])
def test_invalid_effect(tmp_path, effect):
    with pytest.raises(ValueError, match='effect'):
        plan(project(tmp_path), 'transition', clip_ids=['c1', 'c2'], duration_frames=10, effect=effect)


@pytest.mark.parametrize('n', [0, -1, 50, True, 2.5])
def test_invalid_overlap_duration(tmp_path, n):
    with pytest.raises(ValueError, match='duration'):
        plan(project(tmp_path), 'transition', clip_ids=['c1', 'c2'], duration_frames=n)


@pytest.mark.parametrize('color', [{'gamma': float('nan')}, {'contrast': float('inf')},
                                  {'brightness': True}, {'saturation': 4},
                                  {'rs': -2}, {'gamma': '1;null'}, {'lut': 'a.cube'}])
def test_invalid_color(tmp_path, color):
    with pytest.raises(ValueError, match='color|gamma|contrast|brightness|saturation|rs'):
        plan(project(tmp_path), 'color_grade', clip_id='c1', color=color)


@pytest.mark.parametrize('transform', [{'x': -1}, {'width': 33}, {'opacity': float('nan')},
                                      {'opacity': 2}, {'x': 100}, {'rotate': 30},
                                      {'corner_radius': -1}, {'corner_radius': 999},
                                      {'corner_radius': True}])
def test_invalid_transform(tmp_path, transform):
    p = project(tmp_path)
    p['tracks'][1]['clips'][0]['transform'] = transform
    with pytest.raises(ValueError):
        plan(p, 'multitrack')


@pytest.mark.parametrize('edit', ['vfr', 'speed', 'path', 'symlink', 'subtitle', 'keyframes'])
def test_unsupported_or_unsafe_inputs(tmp_path, edit):
    p = project(tmp_path)
    if edit == 'vfr': p['sources']['red']['variable_frame_rate'] = True
    if edit == 'speed': p['tracks'][0]['clips'][0]['speed'] = 2
    if edit == 'path': p['sources']['red']['path'] = '/etc/passwd'
    if edit == 'symlink':
        (tmp_path / 'link.mp4').symlink_to(tmp_path / 'red.mp4')
        p['sources']['red']['path'] = str(tmp_path / 'link.mp4')
    if edit == 'subtitle': p['tracks'].append({'id': 's', 'kind': 'subtitle', 'clips': [clip('s1', 'red', 's')]})
    if edit == 'keyframes': p['tracks'][0]['clips'][0]['keyframes'] = [1]
    with pytest.raises(ValueError):
        plan(p, 'multitrack')


def test_mixed_fps_is_explicitly_conformed_and_rounded_up(tmp_path):
    p = project(tmp_path)
    p['sources']['red']['fps'] = [30, 1]
    p['tracks'][1]['clips'] = []
    p['tracks'][2]['clips'] = []
    result = plan(p, 'multitrack')
    # 50 frames @30 fps = 1.6667 s -> 42 frames @25 fps (ceil).
    assert result['expected_frames'] == 42
    assert any('conformed from 30/1' in warning for warning in result['warnings'])
    assert result['inputs'][0]['source_fps'] == [30, 1]
    assert result['inputs'][0]['conformed_to_timeline'] is True
    assert plan(p, 'color_grade', clip_id='c1', color={'brightness': 0.1})['expected_frames'] == 42


def test_plan_and_source_integrity_block_even_dry_run(tmp_path):
    p = project(tmp_path)
    result = plan(p, 'multitrack')
    bad = copy.deepcopy(result); bad['args'][0] = 'sh'
    with pytest.raises(ValueError, match='integrity|hash'):
        ve.render(bad, dry_run=True)
    Path(p['sources']['red']['path']).write_bytes(b'changed')
    with pytest.raises(ValueError, match='integrity|hash'):
        ve.render(result, dry_run=True)


def test_silent_source_project_opt_in_and_unknown_params(tmp_path):
    info = {'path': str(tmp_path / 'silent.mp4'), 'sha256': 'a' * 64,
            'video': {'frames': 25, 'fps': '25/1', 'width': 64, 'height': 48}, 'audio': None}
    p = ve.project_from_probe('silent', info, allow_silent=True)
    assert p['sources']['silent']['has_audio'] is False
    assert p['sample_rate'] == 48000
    with pytest.raises(ValueError):
        plan(project(tmp_path), 'multitrack', magic=True)


def test_fps_rational_and_silent_transition(tmp_path):
    p = project(tmp_path); p['fps'] = [30000, 1001]
    for src in p['sources'].values(): src.update(fps=[30000, 1001], has_audio=False)
    result = plan(p, 'transition', clip_ids=['c1', 'c2'], duration_frames=10)
    assert result['expected_frames'] == 90
    assert 'anullsrc' in ' '.join(result['args'])


def test_corner_radius_uses_alpha_mask(tmp_path):
    p = project(tmp_path)
    p['tracks'][1]['clips'][0]['transform'] = {'width': 32, 'height': 24, 'x': 16,
                                                'y': 8, 'opacity': .8,
                                                'corner_radius': 8}
    result = plan(p, 'multitrack')
    graph = result['args'][result['args'].index('-filter_complex') + 1]
    assert 'geq=' in graph and 'hypot(' in graph and 'alpha(X,Y)*0.8' in graph


def test_preset_is_explicit_and_invalid_blocked(tmp_path):
    p = project(tmp_path)
    result = plan(p, 'multitrack', preset='veryfast')
    assert result['encoding']['preset'] == 'veryfast'
    assert result['args'][result['args'].index('-preset') + 1] == 'veryfast'
    for bad in ('faster;rm', 'placebo', '', None):
        with pytest.raises(ValueError, match='preset'):
            plan(p, 'multitrack', preset=bad)


def test_quality_scope_never_autoapproves_semantics():
    from integrations.video_editor_advanced import quality_scope
    result = quality_scope(True)
    assert result['technical_checks_passed'] is True
    assert result['audiovisual_approved'] is False
    assert result['translation_accuracy_verified'] is False
    assert result['scientific_validity_verified'] is False
