"""Fixtures CPU reais: predicados de pixels/áudio, não aprovação estética."""
from array import array
import json
import math
from pathlib import Path
import shutil
import subprocess

import pytest

from integrations import video_editor as ve
from tests.test_r1046_video_editor_advanced import clip

pytestmark = pytest.mark.skipif(not shutil.which('ffmpeg') or not shutil.which('ffprobe'),
                                reason='real FFmpeg/ffprobe required; no fake fallback')


def run(args):
    p = subprocess.run(args, capture_output=True, timeout=60)
    assert p.returncode == 0, p.stderr.decode(errors='replace')[-1600:]
    return p.stdout


def fixture_project(root, *, fps='25/1', silent=False):
    root.mkdir(parents=True, exist_ok=True)
    sources = {}
    for name in ('red', 'blue', 'gray'):
        path = root / f'{name}.mp4'
        args = ['ffmpeg', '-nostdin', '-v', 'error', '-f', 'lavfi', '-i',
                f'color=c={name}:s=64x48:r={fps}:d=3']
        if not silent:
            args += ['-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=3']
        args += ['-vf', 'setsar=1', '-c:v', 'libx264', '-threads', '1', '-pix_fmt', 'yuv420p']
        if not silent:
            args += ['-c:a', 'aac', '-ac', '2']
        run([*args, '-y', str(path)])
        info = ve.probe_media(path, allow_silent=True)
        record = ve.project_from_probe(name, info, allow_silent=True)
        sources[name] = record['sources'][name]
    p = record
    p.update(root=str(root), sources=sources, project_id='real')
    p['tracks'] = [
        {'id': 'v1', 'kind': 'video', 'clips': [clip('c1', 'red', 'v1', end=75)]},
        {'id': 'v2', 'kind': 'video', 'clips': [clip('c2', 'blue', 'v2', 25, end=25)]},
        {'id': 'a1', 'kind': 'audio', 'clips': [] if silent else [clip('a1', 'red', 'a1', 25, end=25)]}]
    return p


def do_render(p, op, output='result.mp4', **params):
    plan = ve.plan(p, op, {'output': str(Path(p['root']) / output), **params})
    result = ve.render(plan)
    receipt = json.loads(Path(result['receipt']).read_text())
    assert receipt['technical_checks_passed'] is True
    for k in ('audiovisual_approved', 'translation_accuracy_verified', 'scientific_validity_verified'):
        assert receipt[k] is False
    return plan, result


def rgb(path):
    return run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-threads', '1', 'pipe:1'])


def pixel(data, frame, x=32, y=24):
    offset = ((frame * 48 + y) * 64 + x) * 3
    return tuple(data[offset:offset+3])


def audio_rms(path, start, end):
    data = run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-map', '0:a:0',
                '-ac', '1', '-ar', '48000', '-f', 'f32le', 'pipe:1'])
    samples = array('f'); samples.frombytes(data)
    segment = samples[int(start*48000):int(end*48000)]
    assert len(segment) == int((end-start)*48000) or abs(len(segment)-(end-start)*48000) < 2
    return math.sqrt(sum(x*x for x in segment) / len(segment))


def test_real_overlay_boundaries_z_order_audio_delay_and_cache(tmp_path):
    p = fixture_project(tmp_path)
    p['tracks'][1]['clips'][0]['transform'] = {'x': 16, 'y': 12, 'width': 32, 'height': 24}
    plan, result = do_render(p, 'multitrack')
    assert plan['expected_frames'] == 75
    data = rgb(result['output'])
    assert len(data) == 75*64*48*3
    for frame in (0, 24, 50, 74):
        r, g, b = pixel(data, frame); assert r > 200 and b < 40, (frame,r,g,b)
    for frame in (25, 30, 49):
        r, g, b = pixel(data, frame); assert b > 200 and r < 40, (frame,r,g,b)
        r, g, b = pixel(data, frame, 2, 2); assert r > 200 and b < 40
    assert audio_rms(result['output'], .2, .8) < .001
    assert audio_rms(result['output'], 1.2, 1.8) > .02
    assert audio_rms(result['output'], 2.2, 2.8) < .001
    assert ve.render(plan)['status'] == 'cached'


@pytest.mark.parametrize('effect', ['fade', 'wipeleft', 'slideleft', 'dissolve'])
def test_real_transitions(effect, tmp_path):
    p = fixture_project(tmp_path)
    p['tracks'][0]['clips'][0]['out_frame'] = 50
    p['tracks'][1]['clips'][0]['out_frame'] = 50
    plan, result = do_render(p, 'transition', clip_ids=['c1','c2'], duration_frames=10, effect=effect)
    assert plan['expected_frames'] == 90
    data = rgb(result['output'])
    assert pixel(data, 5)[0] > 200
    assert pixel(data, 80)[2] > 200
    if effect == 'fade':
        r,g,b = pixel(data, 45); assert 70 < r < 180 and 70 < b < 180


def test_real_color_brightness_and_saturation(tmp_path):
    p = fixture_project(tmp_path)
    p['tracks'][0]['clips'][0].update(source='gray', out_frame=25)
    _, result = do_render(p, 'color_grade', clip_id='c1', color={'brightness': .2})
    before = pixel(rgb(p['sources']['gray']['path']), 5)
    after = pixel(rgb(result['output']), 5)
    assert sum(after)/3 > sum(before)/3 + 30
    p['tracks'][0]['clips'][0]['source'] = 'red'
    _, result = do_render(p, 'color_grade', output='gray-out.mp4', clip_id='c1', color={'saturation': 0})
    channels = pixel(rgb(result['output']), 5)
    assert max(channels)-min(channels) < 5


def test_real_rational_rate_and_silent_sources(tmp_path):
    p = fixture_project(tmp_path, fps='30000/1001', silent=True)
    p['tracks'][0]['clips'][0]['out_frame'] = 60
    p['tracks'][1]['clips'][0]['out_frame'] = 60
    plan, result = do_render(p, 'transition', clip_ids=['c1','c2'], duration_frames=15)
    assert plan['expected_frames'] == 105
    assert ve.probe_media(result['output'])['video']['fps'] == '30000/1001'
    assert audio_rms(result['output'], .2, .8) < .0001
