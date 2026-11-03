"""R1042: núcleo universal de edição. Planos e runner falsos; nenhum vídeo real."""
import importlib
import json
from pathlib import Path

import pytest


def api():
    return importlib.import_module('integrations.video_editor')


def probe(frames=250, fps='25/1', width=1280, height=720, rotation=0,
          vfr=False, audio=True):
    return {'path': '/media/source.mp4', 'sha256': 'a' * 64,
            'duration_seconds': frames / (25 if fps == '25/1' else 30),
            'format_name': 'mov,mp4', 'video': {
                'index': 0, 'codec': 'h264', 'width': width, 'height': height,
                'fps': fps, 'r_fps': '50/1' if vfr else fps,
                'frames': frames, 'rotation': rotation,
                'variable_frame_rate': vfr, 'pix_fmt': 'yuv420p'},
            'audio': ({'index': 1, 'codec': 'aac', 'sample_rate': 48000,
                       'channels': 2} if audio else None)}


def project(tmp_path=None):
    m = api()
    p = m.project_from_probe('source.mp4', probe(), project_id='demo')
    if tmp_path is not None:
        p['root'] = str(tmp_path)
    return p


def clip(cid='c1', start=0, inn=0, out=50, speed=1.0, source='source.mp4',
         track='v1'):
    return {'id': cid, 'track': track, 'source': source, 'in_frame': inn,
            'out_frame': out, 'start_frame': start, 'speed': speed, 'volume': 1.0}


def add(project, *clips):
    for c in clips:
        track = next(t for t in project['tracks'] if t['id'] == c['track'])
        track['clips'].append(c)
    return project


def test_rational_vfr_rotation_and_missing_video():
    m = api()
    assert m.parse_rational('30000/1001') == (30000, 1001)
    assert m.parse_rational('50/2') == (25, 1)
    with pytest.raises(ValueError): m.parse_rational('0/1')
    p = m.project_from_probe('source.mp4', probe(vfr=True, rotation=90))
    assert p['video']['variable_frame_rate'] is True
    assert (p['width'], p['height']) == (720, 1280)
    with pytest.raises(ValueError, match='video'):
        m.project_from_probe('source.mp4', {**probe(), 'video': None})
    with pytest.raises(ValueError, match='audio'):
        m.project_from_probe('source.mp4', probe(audio=False))


def test_timeline_rejects_overlap_outside_and_duplicate():
    m = api()
    p = add(project(), clip('c1', 0, 0, 50), clip('c2', 10, 0, 50))
    with pytest.raises(ValueError, match='overlap'): m.validate_project(p)
    p = add(project(), clip('c1', 0, 0, 500))
    with pytest.raises(ValueError, match='source'): m.validate_project(p)
    p = add(project(), clip('c1', 0, 0, 50), clip('c1', 60, 0, 50))
    with pytest.raises(ValueError, match='duplicate'): m.validate_project(p)
    p = add(project(), clip('c1', 0, 0, 50), clip('c3', 100, 0, 50))
    assert m.validate_project(p)['tracks'][0]['clips'][1]['id'] == 'c3'


def test_trim_plan_dry_run_and_speed_block():
    m = api()
    p = add(project(), clip('c1', 0, 25, 100))
    plan = m.plan(p, 'trim', {'clip_id': 'c1', 'output': 'out.mp4'})
    assert plan['expected_frames'] == 75
    assert '-ss' in plan['args'] and plan['args'].count('{output}') == 1
    out = m.render(plan, runner=lambda *a: (_ for _ in ()).throw(AssertionError('ran')),
                   probe_fn=lambda *a: probe(), dry_run=True)
    assert out['status'] == 'dry_run' and out['args']
    p2 = add(project(), clip('c2', 0, 0, 50, speed=1.5))
    with pytest.raises(ValueError, match='speed'):
        m.plan(p2, 'trim', {'clip_id': 'c2', 'output': 'out.mp4'})


def test_concat_and_frame_expectation():
    m = api()
    p = add(project(), clip('c1', 0, 0, 50), clip('c2', 50, 30, 80))
    plan = m.plan(p, 'concat', {'clip_ids': ['c1', 'c2'], 'output': 'out.mp4'})
    assert plan['expected_frames'] == 100
    assert 'concat=n=2:v=1:a=1' in ' '.join(plan['args'])


@pytest.mark.parametrize('op,params', [
    ('scale', {'width': 641, 'height': 720}),
    ('pad', {'width': 1280, 'height': 721, 'x': 0, 'y': 0}),
    ('crop', {'width': 639, 'height': 720, 'x': 0, 'y': 0})])
def test_even_dimensions(op, params):
    m = api()
    with pytest.raises(ValueError, match='even'):
        m.plan(project(), op, {**params, 'output': 'out.mp4'})


def test_subtitles_confined_and_quote_rejected(tmp_path):
    m = api()
    (tmp_path / 'subs.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nOi\n')
    p = project(tmp_path)
    plan = m.plan(p, 'subtitles', {'file': 'subs.srt', 'mode': 'soft',
                                   'output': 'out.mp4'})
    assert 'mov_text' in plan['args']
    with pytest.raises(ValueError, match='relative|escape'):
        m.plan(p, 'subtitles', {'file': '../subs.srt', 'mode': 'burn',
                                'output': 'out.mp4'})
    with pytest.raises(ValueError, match='quote|escape'):
        m.plan(p, 'subtitles', {'file': "a'b.srt", 'mode': 'burn',
                                'output': 'out.mp4'})


def test_render_receipt_cache_tamper_and_no_overwrite(tmp_path):
    m = api()
    p = add(project(tmp_path), clip('c1', 0, 0, 50))
    plan = m.plan(p, 'trim', {'clip_id': 'c1', 'output': str(tmp_path / 'out.mp4')})
    calls = []
    def runner(args, **kwargs):
        calls.append(args)
        Path(args[-1]).write_bytes(b'fake-video')
        return type('R', (), {'returncode': 0, 'stderr': ''})()
    result = m.render(plan, runner=runner, probe_fn=lambda *a: probe(frames=50))
    assert result['status'] == 'rendered' and len(calls) == 1
    again = m.render(plan, runner=runner, probe_fn=lambda *a: probe(frames=50))
    assert again['status'] == 'cached' and len(calls) == 1
    (tmp_path / 'out.mp4').write_bytes(b'tampered')
    with pytest.raises(ValueError, match='integrity'):
        m.render(plan, runner=runner, probe_fn=lambda *a: probe(frames=50))
    (tmp_path / 'occupied.mp4').write_bytes(b'old')
    plan2 = m.plan(p, 'trim', {'clip_id': 'c1', 'output': str(tmp_path / 'occupied.mp4')})
    with pytest.raises(FileExistsError):
        m.render(plan2, runner=runner, probe_fn=lambda *a: probe(frames=50))


def test_render_creates_missing_output_parent(tmp_path):
    m = api()
    p = add(project(tmp_path), clip('c1', 0, 0, 50))
    target = tmp_path / 'new' / 'nested' / 'out.mp4'
    plan = m.plan(p, 'trim', {'clip_id': 'c1', 'output': str(target)})
    def runner(args, **kwargs):
        Path(args[-1]).write_bytes(b'fake-video')
        return type('R', (), {'returncode': 0, 'stderr': ''})()
    result = m.render(plan, runner=runner, probe_fn=lambda *a: probe(frames=50))
    assert result['status'] == 'rendered' and target.is_file()


def test_extract_audio_declares_audio_media_type(tmp_path):
    m = api()
    p = add(project(tmp_path), clip('c1', 0, 0, 50))
    plan = m.plan(p, 'extract_audio', {'output': str(tmp_path / 'out.wav')})
    assert plan['media_type'] == 'audio' and plan['expected_frames'] is None


def test_dub_requires_adapter():
    m = api()
    with pytest.raises(ValueError, match='adapter'):
        m.plan(project(), 'dub', {'output': 'out.mp4'})
    m.register_operation('dub', lambda p, q: q, lambda p, q: {
        'operation': 'dub', 'inputs': [], 'output': q['output'], 'args': ['ffmpeg', '{output}'],
        'expected_frames': None, 'frame_tolerance': 0,
        'warnings': [], 'limitations': ['adapter fixture']})
    plan = m.plan(project(), 'dub', {'output': 'out.mp4'})
    assert plan['operation'] == 'dub'


def test_remotion_backend_requires_license_and_render_approval(tmp_path):
    m = api()
    proj = tmp_path / 'remotion'
    (proj / 'src').mkdir(parents=True)
    (proj / 'package.json').write_text(json.dumps({'dependencies': {'remotion': '4.0.0'}}))
    (proj / 'src/index.ts').write_text('import {registerRoot} from "remotion";\n')
    (proj / 'src/Demo.tsx').write_text(
        'export const Demo = () => null;\n'
        '<Composition id="Demo" durationInFrames={50} fps={25} width={1280} height={720} />\n')
    p = project(tmp_path)
    base = {'project_path': str(proj), 'composition_id': 'Demo',
            'props': {'title': 'teste'}, 'output': str(tmp_path / 'out.mp4'),
            'license_ack': True, 'render_approved': True}
    plan = m.plan(p, 'remotion', base)
    assert plan['backend'] == 'remotion' and 'remotion' in plan['args']
    assert plan['expected_frames'] == 50
    assert m.render(plan, dry_run=True)['status'] == 'dry_run'
    calls = []
    def runner(args, **kwargs):
        calls.append(args)
        target = next(a for a in args if a.endswith('.mp4'))
        Path(target).write_bytes(b'remotion-video')
        return type('R', (), {'returncode': 0, 'stderr': ''})()
    result = m.render(plan, runner=runner, probe_fn=lambda *a: probe(frames=50))
    assert result['status'] == 'rendered' and calls
    without = m.plan(p, 'remotion', {**base, 'render_approved': False})
    with pytest.raises(ValueError, match='approval|approved'):
        m.render(without, runner=runner, probe_fn=lambda *a: probe(frames=50))
    no_license = m.plan(p, 'remotion', {**base, 'license_ack': False})
    with pytest.raises(ValueError, match='license'):
        m.render(no_license, runner=runner, probe_fn=lambda *a: probe(frames=50))
    with pytest.raises(ValueError, match='composition'):
        m.plan(p, 'remotion', {**base, 'composition_id': 'Nope'})


def test_other_backend_requires_registration(tmp_path):
    m = api()
    p = add(project(tmp_path), clip('c1', 0, 0, 50))
    plan = m.plan(p, 'trim', {'clip_id': 'c1', 'output': str(tmp_path / 'out.mp4')})
    plan['backend'] = 'magic'
    plan['plan_sha256'] = m.digest(plan)
    with pytest.raises(ValueError, match='backend'):
        m.render(plan, runner=lambda *a, **k: None, probe_fn=lambda *a: probe(frames=50))
    m.register_backend('magic', lambda p: None)
    result = m.render(plan, dry_run=True)
    assert result['status'] == 'dry_run' and result['backend'] == 'magic'


def test_project_roundtrip_and_unknown_operation():
    m = api()
    p = add(project(), clip('c1', 0, 0, 50))
    assert m.load_project(m.dumps_project(p))['project_id'] == 'demo'
    with pytest.raises(ValueError, match='operation'):
        m.plan(p, 'explode', {})
