"""Contraprovas adicionais: recibos, concorrência, demux e áudio curto."""
import copy
from pathlib import Path
from types import SimpleNamespace

import pytest

from integrations import video_editor as ve
from integrations import video_editor_advanced as advanced
from tests.test_r1046_video_editor_advanced import project, plan


def test_track_options_cannot_be_ignored(tmp_path):
    p = project(tmp_path); p['tracks'][0]['muted'] = True
    with pytest.raises(ValueError, match='track'):
        plan(p, 'multitrack')


def test_short_audio_is_not_hidden_by_container_duration(tmp_path, monkeypatch):
    info = {'duration_seconds': 3, 'video': {'frames': 75, 'fps': '25/1', 'width': 64,
             'height': 48, 'duration_seconds': 3}, 'audio': {'sample_rate': 48000,
             'channels': 2, 'duration_seconds': 1}}
    monkeypatch.setattr(ve, 'probe_media', lambda *a, **k: copy.deepcopy(info))
    monkeypatch.setattr(advanced.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0, stdout='75\n'))
    with pytest.raises(ValueError, match='audio|contract'):
        advanced.verify_output(tmp_path/'out.mp4', {'frames':75, 'width':64, 'height':48,
                               'fps':[25,1], 'sample_rate':48000, 'channels':2})


def test_advanced_probe_uses_protocol_and_demux_allowlist(tmp_path, monkeypatch):
    p = project(tmp_path); result = plan(p, 'multitrack'); calls=[]
    def runner(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout='{}')
    monkeypatch.setattr(advanced.subprocess, 'run', runner)
    with pytest.raises(ValueError):
        advanced.preflight(result, inspect_media=True)
    assert calls and '-protocol_whitelist' in calls[0] and '-format_whitelist' in calls[0]


def test_orphan_receipt_blocks_before_render(tmp_path):
    p = project(tmp_path)
    result = ve.plan(p, 'trim', {'clip_id':'c1', 'output':str(tmp_path/'out.mp4')})
    (tmp_path/'out.mp4.receipt.json').write_text('{}')
    calls=[]
    def runner(argv, **kwargs):
        calls.append(argv); Path(argv[-1]).write_bytes(b'output')
        return SimpleNamespace(returncode=0)
    with pytest.raises(FileExistsError):
        ve.render(result, runner=runner, probe_fn=lambda _: {'video':{'frames':50}})
    assert not calls and not (tmp_path/'out.mp4').exists()


def test_promotion_uses_exclusive_destination(tmp_path, monkeypatch):
    p = project(tmp_path)
    output = tmp_path/'out.mp4'
    result = ve.plan(p, 'trim', {'clip_id':'c1', 'output':str(output)})
    link = ve.os.link
    def concurrent_writer(src, dest):
        Path(dest).write_bytes(b'concurrent-original')
        return link(src, dest)
    monkeypatch.setattr(ve.os, 'link', concurrent_writer)
    def runner(argv, **kwargs):
        Path(argv[-1]).write_bytes(b'render')
        return SimpleNamespace(returncode=0)
    with pytest.raises(FileExistsError):
        ve.render(result, runner=runner, probe_fn=lambda _: {'video':{'frames':50}})
    assert output.read_bytes() == b'concurrent-original'


def test_real_vfr_is_flagged_and_blocked(tmp_path):
   import shutil, subprocess
   if not shutil.which('ffmpeg'):
       pytest.skip('ffmpeg unavailable')
   source = tmp_path / 'vfr.mp4'
   subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i',
                   'testsrc2=s=64x48:r=25:d=2','-vf','select=not(mod(n\\,5))',
                   '-fps_mode','passthrough','-pix_fmt','yuv420p','-y',str(source)],
                  check=True, timeout=60)
   info = ve.probe_media(source, allow_silent=True)
   assert info['video']['variable_frame_rate'] is True
   assert info['video']['frames'] == 10
   p = project(tmp_path)
   p['sources']['red'].update(path=str(source), sha256=ve.file_hash(source),
                              variable_frame_rate=True, frames=10)
   p['tracks'][0]['clips'][0]['out_frame'] = 10
   p['tracks'][1]['clips'][0].update(in_frame=0, out_frame=10)
   p['tracks'][2]['clips'][0].update(in_frame=0, out_frame=10)
   with pytest.raises(ValueError, match='VFR'):
       plan(p, 'multitrack')
