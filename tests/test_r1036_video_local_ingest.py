"""R1036 fixtures are synthetic; they say nothing about the real episode."""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'integrations/video_local_ingest.py'
FFMPEG = shutil.which('ffmpeg')
FFPROBE = shutil.which('ffprobe')
pytestmark = pytest.mark.skipif(not (FFMPEG and FFPROBE), reason='ffmpeg/ffprobe ausentes')


def api():
    assert MODULE.is_file(), 'ingestão local ainda ausente'
    spec = importlib.util.spec_from_file_location('video_local_ingest', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope='module')
def fixture(tmp_path_factory):
    folder = tmp_path_factory.mktemp('r1036-fixture')
    video = folder / 'fixture.mp4'
    subprocess.run([
        FFMPEG, '-v', 'error', '-f', 'lavfi', '-i',
        'testsrc2=size=160x90:rate=10:duration=3', '-f', 'lavfi', '-i',
        'sine=frequency=440:sample_rate=44100:duration=3', '-c:v', 'libx264',
        '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-g', '10', '-c:a', 'aac',
        '-b:a', '96k', '-shortest', '-movflags', '+faststart', str(video),
    ], check=True, timeout=60)
    return video


def test_probe_cfr_fixture(fixture):
    probe = api().probe_source(fixture)
    assert probe['frame_count'] == 30
    assert probe['fps'] == '10/1'
    assert abs(probe['duration_seconds'] - 3.0) < 0.11
    assert probe['width'] == 160 and probe['height'] == 90
    assert probe['has_audio'] is True
    assert probe['timing_mode'] == 'cfr_compatible'
    assert probe['timing_basis'] == 'probe_declared_cfr'
    assert len(probe['sha256']) == 64


def test_probe_counts_when_container_omits_frames(tmp_path, fixture):
    remux = tmp_path / 'fixture.mkv'
    subprocess.run([FFMPEG, '-v', 'error', '-i', str(fixture), '-c', 'copy', str(remux)],
                   check=True, timeout=60)
    with pytest.raises(ValueError, match='frame'):
        api().probe_source(remux)
    probe = api().probe_source(remux, count_frames=True)
    assert probe['frame_count'] == 30


def test_probe_rejects_missing_and_nonmedia(tmp_path):
    with pytest.raises(ValueError):
        api().probe_source(tmp_path / 'absent.mp4')
    junk = tmp_path / 'junk.mp4'
    junk.write_bytes(b'not media')
    with pytest.raises(ValueError):
        api().probe_source(junk)


def test_plan_from_inspection(fixture):
    m = api()
    probe = m.probe_source(fixture)
    plan = m.plan_from_inspection(probe, min_seconds=1, max_seconds=1.5,
                                  target_seconds=1, context_seconds=0)
    assert plan['total_frames'] == 30
    assert plan['fps'] == '10/1'
    assert plan['source']['sha256'] == probe['sha256']
    assert plan['source']['timing_mode'] == 'cfr'
    assert len(plan['segments']) == 3
    assert all(s['duration_seconds'] == 1 for s in plan['segments'])


def test_vfr_or_unverified_is_blocked(fixture):
    m = api()
    probe = m.probe_source(fixture)
    probe['timing_mode'] = 'vfr_or_unverified'
    with pytest.raises(ValueError, match='CFR|timing'):
        m.plan_from_inspection(probe, min_seconds=1, max_seconds=1.5, target_seconds=1)


def test_extract_parts_exact_and_manifest(fixture, tmp_path):
    m = api()
    probe = m.probe_source(fixture)
    plan = m.plan_from_inspection(probe, min_seconds=1, max_seconds=1.5,
                                  target_seconds=1, context_seconds=0)
    out = tmp_path / 'extraction'
    manifest = m.extract_parts(fixture, plan, out)
    assert manifest['status'] == 'extracted_pending_edit_and_review'
    assert manifest['counts'] == {'planned': 3, 'extracted': 3}
    assert len(manifest['parts']) == 3
    for part, segment in zip(manifest['parts'], plan['segments']):
        artifact = Path(part['artifact']['path'])
        assert artifact.is_file()
        assert part['artifact']['sha256'] == m.sha256_file(artifact)
        assert part['frame_count'] == 10
        assert part['states']['editing'] == 'pending'
        assert part['states']['approval'] == 'pending'
        receipt = out / 'receipts' / f"{segment['id']}.json"
        assert json.loads(receipt.read_text())['segment_id'] == segment['id']
    assert m.verify_manifest(out / 'extraction-manifest.json')
    with pytest.raises(FileExistsError):
        m.extract_parts(fixture, plan, out)


@pytest.fixture(scope='module')
def cgop_intermediate(fixture, tmp_path_factory):
    folder = tmp_path_factory.mktemp('r1036-cgop')
    video = folder / 'cgop.mp4'
    subprocess.run([
        FFMPEG, '-v', 'error', '-i', str(fixture), '-map', '0:v:0', '-map', '0:a:0',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23', '-pix_fmt', 'yuv420p',
        '-flags', '+cgop', '-x264-params', 'open-gop=0', '-fps_mode', 'cfr',
        '-force_key_frames', '1,2', '-c:a', 'copy', '-movflags', '+faststart',
        str(video),
    ], check=True, timeout=60)
    return video


def test_source_keyframes(fixture):
    m = api()
    result = m.source_keyframes(fixture)
    assert result['keyframe_frames'][:4] == [0, 10, 20]
    assert max(result['keyframe_frames']) < result['total_frames']
    assert result['unaligned_count'] == 0
    assert result['frame_aligned'] is True


def test_extract_from_derived_intermediate(fixture, cgop_intermediate, tmp_path):
    m = api()
    probe = m.probe_source(fixture)
    plan = m.plan_from_inspection(probe, min_seconds=1, max_seconds=1.5,
                                  target_seconds=1, context_seconds=0)
    derived = {'source_sha256': plan['source']['sha256'],
               'sha256': m.sha256_file(cgop_intermediate),
               'bytes': cgop_intermediate.stat().st_size,
               'frame_count': 30, 'method': 'closed_gop_test'}
    manifest = m.extract_parts(cgop_intermediate, plan, tmp_path / 'derived',
                               derived_source=derived)
    assert manifest['intermediate']['sha256'] == derived['sha256']
    assert manifest['counts'] == {'planned': 3, 'extracted': 3}
    assert all(part['frame_count'] == 10 for part in manifest['parts'])
    assert m.verify_manifest(tmp_path / 'derived/extraction-manifest.json')


def test_extract_single_part(fixture, tmp_path):
    m = api()
    probe = m.probe_source(fixture)
    plan = m.plan_from_inspection(probe, min_seconds=4, max_seconds=5, target_seconds=4)
    assert len(plan['segments']) == 1
    manifest = m.extract_parts(fixture, plan, tmp_path / 'single')
    assert manifest['parts'][0]['frame_count'] == 30
    assert manifest['extraction_method'] == 'stream_copy_per_part_at_keyframe'


def test_extract_rejects_non_keyframe_boundary(fixture, tmp_path):
    m = api()
    probe = m.probe_source(fixture)
    plan = m.plan_from_inspection(probe, min_seconds=0.4, max_seconds=0.6,
                                  target_seconds=0.5)
    assert any(s['end_frame'] % 10 for s in plan['segments'][:-1])
    with pytest.raises(ValueError, match='keyframe'):
        m.extract_parts(fixture, plan, tmp_path / 'non-keyframe')
    assert not (tmp_path / 'non-keyframe' / 'extraction-manifest.json').exists()


def test_extract_rejects_changed_source_and_bad_plan(fixture, tmp_path):
    m = api()
    probe = m.probe_source(fixture)
    plan = m.plan_from_inspection(probe, min_seconds=1, max_seconds=1.5, target_seconds=1,
                                  context_seconds=0)
    original = fixture.read_bytes()
    try:
        fixture.write_bytes(original + b'x')
        with pytest.raises(ValueError, match='hash'):
            m.extract_parts(fixture, plan, tmp_path / 'changed')
    finally:
        fixture.write_bytes(original)
    plan['segments'][0]['end_frame'] += 1
    with pytest.raises(ValueError):
        m.extract_parts(fixture, plan, tmp_path / 'bad')


def test_verify_manifest_detects_modified_artifact(fixture, tmp_path):
    m = api()
    probe = m.probe_source(fixture)
    plan = m.plan_from_inspection(probe, min_seconds=1, max_seconds=1.5,
                                  target_seconds=1, context_seconds=0)
    out = tmp_path / 'verify'
    manifest = m.extract_parts(fixture, plan, out)
    artifact = Path(manifest['parts'][0]['artifact']['path'])
    artifact.write_bytes(b'changed')
    with pytest.raises(ValueError, match='hash|size'):
        m.verify_manifest(out / 'extraction-manifest.json')
