"""R1036 local ingest and frame-exact part extraction.

This module never downloads, edits, translates, synthesizes voice or approves.
It probes a local file, plans with R1035 and extracts declared frame ranges in
one ffmpeg pass. Receipts are audit evidence, not proof of audiovisual quality.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

FFMPEG = shutil.which('ffmpeg')
FFPROBE = shutil.which('ffprobe')


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _segment_audit():
    return importlib.import_module('integrations.video_segment_audit')


def _fraction(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'\d{1,12}(?:/\d{1,12})?', value):
        raise ValueError(f'{label}: rational string required')
    try:
        rate = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f'{label}: invalid rational') from exc
    if not 0 < rate <= 1000:
        raise ValueError(f'{label}: outside (0, 1000]')
    return rate


def _fps_string(rate):
    return f'{rate.numerator}/{rate.denominator}'


def _float_or_none(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def _int_or_none(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _regular_file(path, label):
    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError(f'{label}: existing regular file required')
    return candidate.resolve()


def _run(command, timeout, label):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f'{label}: timeout after {timeout}s') from exc
    except OSError as exc:
        raise ValueError(f'{label}: local tool failed') from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or 'no diagnostic').strip()
        raise ValueError(f'{label}: exit {result.returncode}: {detail[-800:]}')
    if result.stderr.strip():
        raise ValueError(f'{label}: decoder/probe reported errors: {result.stderr.strip()[-800:]}')
    return result


def _ffprobe_json(path, extra, timeout, label):
    if not FFPROBE:
        raise ValueError('ffprobe not installed')
    command = [FFPROBE, '-v', 'error'] + list(extra) + ['-of', 'json', str(path)]
    result = _run(command, timeout, label)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f'{label}: invalid ffprobe JSON') from exc
    if not isinstance(data, dict):
        raise ValueError(f'{label}: malformed ffprobe output')
    return data


def probe_source(path, *, count_frames=False, timeout_seconds=3600):
    """Inspect a local file; a probe-level CFR claim is not a full VFR audit."""
    file = _regular_file(path, 'source')
    digest_before = sha256_file(file)
    size = file.stat().st_size
    if size <= 0:
        raise ValueError('source is empty')
    base = _ffprobe_json(file, ['-show_streams', '-show_format'], min(timeout_seconds, 300),
                         'source probe')
    streams = base.get('streams')
    if not isinstance(streams, list):
        raise ValueError('source probe returned no stream list')
    video = None
    audio = None
    for stream in streams:
        if not isinstance(stream, dict):
            continue
        if stream.get('codec_type') == 'video' and video is None:
            if (stream.get('disposition') or {}).get('attached_pic') in (1, True):
                continue
            video = stream
        elif stream.get('codec_type') == 'audio' and audio is None:
            audio = stream
    if video is None:
        raise ValueError('source has no usable video stream')
    if video.get('codec_name') in (None, ''):
        raise ValueError('video codec unavailable')
    width = _int_or_none(video.get('width'))
    height = _int_or_none(video.get('height'))
    if not width or not height:
        raise ValueError('video dimensions unavailable')
    try:
        avg_rate = _fraction(video.get('avg_frame_rate'), 'avg_frame_rate')
        raw_rate = _fraction(video.get('r_frame_rate'), 'r_frame_rate')
    except ValueError as exc:
        raise ValueError('source fps unavailable or invalid') from exc
    frame_count = _int_or_none(video.get('nb_frames'))
    count_basis = 'container_nb_frames'
    if count_frames:
        counted = _ffprobe_json(file, ['-count_frames', '-select_streams', 'v:0',
                                      '-show_entries', 'stream=nb_read_frames'],
                                timeout_seconds, 'frame count')
        counted_streams = counted.get('streams')
        if not isinstance(counted_streams, list) or not counted_streams:
            raise ValueError('frame count unavailable after decoding')
        frame_count = _int_or_none(counted_streams[0].get('nb_read_frames'))
        count_basis = 'decoded_nb_read_frames'
        if frame_count is None or frame_count < 1:
            raise ValueError('frame count unavailable after decoding; check keyframes/truncation')
    if frame_count is None or frame_count < 1:
        raise ValueError('frame count unavailable; rerun with count_frames=True')
    video_duration = _float_or_none(video.get('duration'))
    if video_duration is None:
        video_duration = _float_or_none((base.get('format') or {}).get('duration'))
    if video_duration is None or video_duration <= 0:
        raise ValueError('video duration unavailable')
    derived_duration = float(Fraction(frame_count, 1) / avg_rate)
    fps_tolerance = max(0.1, 1.5 / float(avg_rate))
    fps_equal = avg_rate == raw_rate
    duration_delta = abs(video_duration - derived_duration)
    cfr_compatible = fps_equal and duration_delta <= fps_tolerance
    format_info = base.get('format') or {}
    has_audio = audio is not None
    audio_codec = audio.get('codec_name') if has_audio else None
    sample_rate = _int_or_none(audio.get('sample_rate')) if has_audio else None
    channels = _int_or_none(audio.get('channels')) if has_audio else None
    audio_duration = _float_or_none(audio.get('duration')) if has_audio else None
    if has_audio and audio_duration is None:
        audio_duration = _float_or_none(format_info.get('duration'))
    audio_start = _float_or_none(audio.get('start_time')) if has_audio else None
    digest_after = sha256_file(file)
    if digest_before != digest_after:
        raise ValueError('source changed while being inspected')
    signature = {
        'container': format_info.get('format_name'),
        'video_codec': video.get('codec_name'),
        'width': width,
        'height': height,
        'pixel_format': video.get('pix_fmt'),
        'audio_codec': audio_codec,
        'sample_rate': sample_rate,
        'channels': channels,
    }
    return {
        'schema_version': 1,
        'path': str(file),
        'sha256': digest_before,
        'bytes': size,
        'format_name': format_info.get('format_name'),
        'duration_seconds': derived_duration,
        'container_duration_seconds': float(format_info['duration'])
        if _float_or_none(format_info.get('duration')) is not None else None,
        'video_duration_seconds': video_duration,
        'frame_count': frame_count,
        'frame_count_basis': count_basis,
        'fps': _fps_string(avg_rate),
        'avg_frame_rate': _fps_string(avg_rate),
        'r_frame_rate': _fps_string(raw_rate),
        'width': width,
        'height': height,
        'video_codec': video.get('codec_name'),
        'pixel_format': video.get('pix_fmt'),
        'has_audio': has_audio,
        'audio_codec': audio_codec,
        'sample_rate': sample_rate,
        'channels': channels,
        'audio_duration_seconds': audio_duration,
        'audio_start_time': audio_start,
        'timing_mode': 'cfr_compatible' if cfr_compatible else 'vfr_or_unverified',
        'timing_basis': 'probe_declared_cfr',
        'cfr_checks': {
            'avg_equals_r': fps_equal,
            'derived_duration_seconds': derived_duration,
            'video_duration_seconds': video_duration,
            'duration_delta_seconds': duration_delta,
            'tolerance_seconds': fps_tolerance,
        },
        'stream_signature': signature,
        'decode_clean': True,
        'limitations': [
            'probe-level CFR compatibility only; full packet timestamp audit not performed',
            'frame count basis is recorded; decoded count is authoritative',
            'decode clean means ffprobe reported no error, not perceptual quality',
        ],
    }


def plan_from_inspection(inspection, *, video_id=None, **options):
    """Connect an inspected local source to the R1035 CFR planner."""
    if not isinstance(inspection, dict):
        raise ValueError('inspection object required')
    if inspection.get('timing_mode') != 'cfr_compatible' or inspection.get('timing_basis') != 'probe_declared_cfr':
        raise ValueError('source is VFR or timing is unverified; CFR planning blocked')
    if inspection.get('decode_clean') is not True:
        raise ValueError('source decode was not clean')
    frame_count = inspection.get('frame_count')
    if type(frame_count) is not int or frame_count < 1:
        raise ValueError('inspection frame_count invalid')
    fps = inspection.get('fps')
    _fraction(fps, 'inspection fps')
    path = inspection.get('path')
    digest = inspection.get('sha256')
    if not isinstance(path, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('inspection path/hash invalid')
    if video_id is None:
        video_id = Path(path).stem
    plan = _segment_audit().plan_segments(video_id, frame_count, fps, **options)
    plan['source'] = {
        'path': path,
        'sha256': digest,
        'frame_count': frame_count,
        'fps': fps,
        'timing_verified': True,
        'timing_mode': 'cfr',
        'has_audio': inspection.get('has_audio') is True,
    }
    _segment_audit().validate_coverage(plan)
    return plan


def _write_new(path, content):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(content)


def _part_receipt(segment, source, plan_digest, probe, fps):
    expected_duration = segment['duration_seconds']
    audio_delta = None
    if source['has_audio']:
        if probe.get('audio_duration_seconds') is None:
            raise ValueError(f'{segment["id"]}: audio stream disappeared')
        audio_delta = float(probe['audio_duration_seconds']) - expected_duration
        tolerance = max(0.15, 3 / float(Fraction(fps)))
        if abs(audio_delta) > tolerance:
            raise ValueError(f'{segment["id"]}: audio boundary exceeds tolerance')
    rate = Fraction(probe['fps'])
    boundary_review = source['has_audio'] and (
        abs(float(probe.get('audio_start_time') or 0.0)) > 0.001
        or abs(float(audio_delta or 0.0)) > 1 / float(rate))
    return {
        'schema_version': 1,
        'segment_id': segment['id'],
        'source': {'path': source['path'], 'sha256': source['sha256']},
        'plan_sha256': plan_digest,
        'artifact': {
            'path': probe['path'],
            'sha256': probe['sha256'],
            'bytes': probe['bytes'],
        },
        'frame_count': probe['frame_count'],
        'fps': probe['fps'],
        'duration_seconds': probe['duration_seconds'],
        'stream_signature': probe['stream_signature'],
        'audio': {
            'present': probe['has_audio'],
            'start_time': probe.get('audio_start_time'),
            'duration_seconds': probe.get('audio_duration_seconds'),
            'delta_seconds': audio_delta,
        },
        'qa': {
            'decode_errors': 0,
            'frame_count_matches': True,
            'fps_matches': True,
            'duration_matches': True,
            'audio_present_matches': True,
            'audio_boundary_review_required': boundary_review,
            'audiovisual_sync_reviewed': False,
        },
        'states': {
            'extraction': 'completed',
            'editing': 'pending',
            'technical_qa': 'extraction_only_pending_human',
            'audiovisual_review': 'pending',
            'approval': 'pending',
        },
        'limitations': [
            'extraction only; no edit, translation, TTS, lip sync or subtitles',
            'no human audiovisual approval; assembly gate remains closed',
            'AAC boundary offsets are recorded and require normalization/review',
        ],
    }


def source_keyframes(path, *, timeout_seconds=600):
    """List frame-aligned source keyframes; used to guarantee exact splits."""
    if not FFPROBE:
        raise ValueError('ffprobe not installed')
    file = _regular_file(path, 'source')
    probe = probe_source(file, count_frames=False)
    rate = Fraction(probe['fps'])
    result = _run([FFPROBE, '-v', 'error', '-select_streams', 'v:0',
                   '-show_entries', 'packet=pts_time,flags', '-of', 'csv=p=0', str(file)],
                  timeout_seconds, 'keyframe probe')
    frames, pts_by_frame, unaligned = [], {}, 0
    for line in result.stdout.splitlines():
        parts = line.strip().split(',')
        if len(parts) < 2 or 'K' not in parts[1]:
            continue
        try:
            pts = float(parts[0])
        except ValueError as exc:
            raise ValueError('invalid keyframe timestamp') from exc
        frame = round(pts * float(rate))
        if abs(Fraction(frame, 1) / rate - Fraction(str(pts))) > Fraction(1, 10) / rate:
            unaligned += 1
            continue
        if frame < 0 or frame > probe['frame_count']:
            raise ValueError('keyframe outside source frame count')
        frames.append(frame)
        pts_by_frame[frame] = pts
    frames = sorted(set(frames))
    if not frames or frames[0] != 0:
        raise ValueError('source must begin with a keyframe')
    return {
        'schema_version': 1,
        'path': str(file),
        'sha256': probe['sha256'],
        'fps': probe['fps'],
        'total_frames': probe['frame_count'],
        'keyframe_frames': frames,
        'keyframe_pts': {str(frame): pts_by_frame[frame] for frame in frames},
        'unaligned_count': unaligned,
        'frame_aligned': unaligned == 0,
        'method': 'ffprobe_packet_keyframe_flags',
        'limitations': [
            'keyframe flags are container evidence; each extracted part is re-probed',
            'unaligned keyframes are excluded rather than rounded into a wrong frame',
        ],
    }


def extract_parts(source_path, plan, output_dir, *, derived_source=None,
                  timeout_seconds=None):
    """Extract each planned range with `-ss` + stream copy at a closed keyframe.

    A planned boundary that is not a keyframe fails closed. When the input is a
    derived closed-GOP intermediate, ``derived_source`` must bind it to the
    original plan source; the manifest records both. No reencode is performed.
    """
    if not FFMPEG:
        raise ValueError('ffmpeg not installed')
    source = _regular_file(source_path, 'source')
    audit = _segment_audit()
    audit.validate_coverage(plan)
    source_record = plan.get('source')
    if not isinstance(source_record, dict):
        raise ValueError('plan has no inspected source record')
    if source_record.get('timing_verified') is not True or source_record.get('timing_mode') != 'cfr':
        raise ValueError('plan source timing is not verified CFR')
    if type(source_record.get('has_audio')) is not bool:
        raise ValueError('plan source audio presence missing')
    digest = sha256_file(source)
    intermediate = None
    if derived_source is None:
        if Path(source_record.get('path', '')).resolve() != source:
            raise ValueError('plan source path mismatch')
        if digest != source_record.get('sha256'):
            raise ValueError('source hash mismatch; refusing extraction')
    else:
        if not isinstance(derived_source, dict):
            raise ValueError('derived_source object required')
        if derived_source.get('source_sha256') != source_record.get('sha256'):
            raise ValueError('derived source is not bound to plan source hash')
        if derived_source.get('sha256') != digest:
            raise ValueError('derived source hash mismatch')
        if derived_source.get('bytes') != source.stat().st_size:
            raise ValueError('derived source size mismatch')
        if derived_source.get('frame_count') != plan.get('total_frames'):
            raise ValueError('derived source frame count mismatch')
        intermediate = {
            'path': str(source), 'sha256': digest, 'bytes': source.stat().st_size,
            'frame_count': derived_source['frame_count'],
            'source_sha256': source_record['sha256'],
            'method': derived_source.get('method', 'derived_intermediate'),
        }
    out = Path(output_dir)
    if out.exists():
        raise FileExistsError(f'output exists; refusing overwrite: {out}')
    has_audio = source_record['has_audio']
    segments = plan['segments']
    boundaries = [segment['end_frame'] for segment in segments[:-1]]
    video_id = plan['video_id']
    rate = Fraction(plan['fps'])
    keyframes = source_keyframes(source)
    keyframe_set = set(keyframes['keyframe_frames'])
    missing = [frame for frame in boundaries if frame not in keyframe_set]
    if missing:
        raise ValueError(f'planned boundary is not a source keyframe: {missing[:5]}; replan')
    if timeout_seconds is None:
        timeout_seconds = 600
    if type(timeout_seconds) is not int or timeout_seconds < 60:
        raise ValueError('timeout_seconds must be an integer >= 60')
    out.mkdir(parents=True, exist_ok=False)
    parts_dir = out / 'parts'
    receipts_dir = out / 'receipts'
    parts_dir.mkdir()
    receipts_dir.mkdir()
    stream_maps = ['-map', '0:v:0'] + (['-map', '0:a:0'] if has_audio else [])
    log_lines = []
    for segment in segments:
        name = f'{video_id}-P{segment["index"]:04d}.mp4'
        part_path = parts_dir / name
        start_time = float(Fraction(segment['start_frame'], 1) / rate)
        duration = float(Fraction(segment['end_frame'] - segment['start_frame'], 1) / rate)
        command = [FFMPEG, '-nostdin', '-v', 'error', '-ss', f'{start_time:.6f}',
                   '-i', str(source)] + stream_maps + [
            '-map_metadata', '-1', '-sn', '-dn', '-c', 'copy',
            '-frames:v', str(segment['end_frame'] - segment['start_frame']),
            '-t', f'{duration:.6f}', '-avoid_negative_ts', 'make_zero',
            '-movflags', '+faststart', '-y', str(part_path),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            log_lines.append(f'# {segment["id"]}\nCOMMAND: ' + ' '.join(command)
                             + '\nSTATUS: timeout\n')
            _write_new(out / 'extraction.log', '\n'.join(log_lines))
            raise ValueError(f'{segment["id"]}: extraction timed out; no manifest') from exc
        except OSError as exc:
            log_lines.append(f'# {segment["id"]}\nCOMMAND: ' + ' '.join(command)
                             + '\nSTATUS: launch_failed\n')
            _write_new(out / 'extraction.log', '\n'.join(log_lines))
            raise ValueError('ffmpeg could not be launched') from exc
        log_lines.append(f'# {segment["id"]}\nCOMMAND: ' + ' '.join(command)
                         + f'\nRETURNCODE: {result.returncode}\nSTDERR: {result.stderr or ""}\n')
        if result.returncode != 0:
            _write_new(out / 'extraction.log', '\n'.join(log_lines))
            raise ValueError(f'{segment["id"]}: ffmpeg extraction failed: '
                             f'{(result.stderr or "no diagnostic")[-600:]}')
        if not part_path.is_file() or part_path.stat().st_size == 0:
            _write_new(out / 'extraction.log', '\n'.join(log_lines))
            raise ValueError(f'{segment["id"]}: output missing after extraction')
    _write_new(out / 'extraction.log', '\n'.join(log_lines))
    expected_names = [f'{video_id}-P{index:04d}.mp4' for index in range(1, len(segments) + 1)]
    actual_names = sorted(path.name for path in parts_dir.glob('*.mp4'))
    if actual_names != expected_names:
        raise ValueError(f'extracted file set mismatch: expected {len(expected_names)}, got {actual_names}')
    plan_digest = audit.plan_digest(plan)
    parts = []
    for segment, name in zip(segments, expected_names):
        part_path = parts_dir / name
        probe = probe_source(part_path, count_frames=True)
        expected_frames = segment['end_frame'] - segment['start_frame']
        if probe['frame_count'] != expected_frames:
            raise ValueError(f'{segment["id"]}: frame count {probe["frame_count"]} != {expected_frames}')
        if probe['fps'] != plan['fps']:
            raise ValueError(f'{segment["id"]}: fps {probe["fps"]} != {plan["fps"]}')
        if probe['has_audio'] is not has_audio:
            raise ValueError(f'{segment["id"]}: audio presence mismatch')
        duration_tolerance = max(0.1, 2 / float(rate))
        if abs(probe['video_duration_seconds'] - segment['duration_seconds']) > duration_tolerance:
            raise ValueError(f'{segment["id"]}: container duration outside tolerance')
        receipt = _part_receipt(segment, source_record, plan_digest, probe, plan['fps'])
        receipt['extraction_method'] = 'stream_copy_per_part_at_keyframe'
        receipt['reencoded'] = False
        if intermediate is not None:
            receipt['intermediate'] = {'path': intermediate['path'],
                                       'sha256': intermediate['sha256']}
        receipt_path = receipts_dir / f'{segment["id"]}.json'
        _write_new(receipt_path, json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        parts.append({
            'id': segment['id'],
            'start_frame': segment['start_frame'],
            'end_frame': segment['end_frame'],
            'frame_count': probe['frame_count'],
            'duration_seconds': probe['duration_seconds'],
            'artifact': receipt['artifact'],
            'receipt': str(receipt_path.resolve()),
            'states': receipt['states'],
        })
    if sha256_file(source) != digest:
        raise ValueError('source changed during extraction')
    manifest = {
        'schema_version': 1,
        'created_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'source': {
            'path': source_record['path'],
            'sha256': source_record['sha256'],
            'frame_count': source_record.get('frame_count'),
            'fps': plan['fps'],
            'timing_mode': source_record['timing_mode'],
            'has_audio': has_audio,
        },
        'intermediate': intermediate,
        'plan_sha256': plan_digest,
        'video_id': video_id,
        'fps': plan['fps'],
        'extraction_method': 'stream_copy_per_part_at_keyframe'
        + ('_from_closed_gop_intermediate' if intermediate else ''),
        'reencoded': False,
        'keyframes': {
            'count': len(keyframes['keyframe_frames']),
            'unaligned_count': keyframes['unaligned_count'],
            'boundary_frames': boundaries,
        },
        'counts': {'planned': len(segments), 'extracted': len(parts)},
        'status': 'extracted_pending_edit_and_review',
        'parts': parts,
        'limitations': [
            'extraction only; no editing, translation, TTS, lip sync, subtitles or approval',
            'stream copy preserves source codecs; editing must reencode if needed',
            'receipt policy is not a substitute for human audiovisual review',
            'AAC boundary offsets recorded; normalize/review before concatenation',
            'probe-level CFR compatibility, not full timestamp audit',
        ],
    }
    _write_new(out / 'extraction-manifest.json',
               json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    return manifest


def verify_manifest(manifest_path, plan=None):
    """Re-hash and re-decode every extracted part; detect any drift."""
    path = _regular_file(manifest_path, 'manifest')
    try:
        manifest = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('manifest unreadable') from exc
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        raise ValueError('unsupported manifest schema')
    if plan is not None:
        if manifest.get('plan_sha256') != _segment_audit().plan_digest(plan):
            raise ValueError('manifest plan hash mismatch')
    source = manifest.get('source')
    if not isinstance(source, dict):
        raise ValueError('manifest source missing')
    source_file = _regular_file(source.get('path', ''), 'source')
    if source_file.stat().st_size != source.get('bytes', source_file.stat().st_size):
        raise ValueError('source size mismatch; preserve original')
    if source.get('sha256') and sha256_file(source_file) != source.get('sha256'):
        raise ValueError('source hash mismatch; preserve original')
    intermediate = manifest.get('intermediate')
    if intermediate is not None:
        if not isinstance(intermediate, dict):
            raise ValueError('intermediate record malformed')
        intermediate_file = _regular_file(intermediate.get('path', ''), 'intermediate')
        if intermediate_file.stat().st_size != intermediate.get('bytes'):
            raise ValueError('intermediate size mismatch')
        if sha256_file(intermediate_file) != intermediate.get('sha256'):
            raise ValueError('intermediate hash mismatch')
        if intermediate.get('source_sha256') != source.get('sha256'):
            raise ValueError('intermediate is not bound to source hash')
    parts = manifest.get('parts')
    counts = manifest.get('counts')
    if not isinstance(parts, list) or not parts:
        raise ValueError('manifest parts missing')
    if not isinstance(counts, dict) or counts.get('planned') != len(parts) or counts.get('extracted') != len(parts):
        raise ValueError('manifest counts inconsistent')
    for part in parts:
        if not isinstance(part, dict):
            raise ValueError('part record malformed')
        artifact = part.get('artifact')
        if not isinstance(artifact, dict):
            raise ValueError('part artifact missing')
        artifact_path = Path(artifact.get('path', ''))
        if artifact_path.is_symlink() or not artifact_path.is_file():
            raise ValueError(f'artifact missing: {part.get("id")}')
        if artifact_path.stat().st_size != artifact.get('bytes'):
            raise ValueError(f'artifact size mismatch: {part.get("id")}')
        if sha256_file(artifact_path) != artifact.get('sha256'):
            raise ValueError(f'artifact hash mismatch: {part.get("id")}')
        receipt_path = Path(part.get('receipt', ''))
        if receipt_path.is_symlink() or not receipt_path.is_file():
            raise ValueError(f'receipt missing: {part.get("id")}')
        try:
            receipt = json.loads(receipt_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f'receipt unreadable: {part.get("id")}') from exc
        if receipt.get('artifact', {}).get('sha256') != artifact.get('sha256'):
            raise ValueError(f'receipt artifact hash mismatch: {part.get("id")}')
        if receipt.get('plan_sha256') != manifest.get('plan_sha256'):
            raise ValueError(f'receipt plan hash mismatch: {part.get("id")}')
        probe = probe_source(artifact_path, count_frames=True)
        if probe['frame_count'] != part.get('frame_count'):
            raise ValueError(f'frame count drift: {part.get("id")}')
        if probe['fps'] != manifest.get('fps'):
            raise ValueError(f'fps drift: {part.get("id")}')
        if probe['has_audio'] is not source.get('has_audio'):
            raise ValueError(f'audio presence drift: {part.get("id")}')
        tolerance = max(0.1, 2 / float(Fraction(manifest['fps'])))
        if abs(probe['duration_seconds'] - part.get('duration_seconds')) > tolerance:
            raise ValueError(f'duration drift: {part.get("id")}')
    return True


def _load_json(path, label):
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'{label}: unreadable JSON') from exc
    if not isinstance(data, dict):
        raise ValueError(f'{label}: object required')
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    cmd = sub.add_parser('probe')
    cmd.add_argument('--source', required=True)
    cmd.add_argument('--out', required=True)
    cmd.add_argument('--count-frames', action='store_true')
    cmd = sub.add_parser('plan')
    cmd.add_argument('--source', required=True)
    cmd.add_argument('--out', required=True)
    cmd.add_argument('--count-frames', action='store_true')
    cmd.add_argument('--video-id')
    cmd.add_argument('--min-seconds', type=float, default=60)
    cmd.add_argument('--max-seconds', type=float, default=90)
    cmd.add_argument('--target-seconds', type=float, default=75)
    cmd.add_argument('--context-seconds', type=float, default=2)
    cmd.add_argument('--candidates')
    cmd = sub.add_parser('keyframes')
    cmd.add_argument('--source', required=True)
    cmd.add_argument('--out', required=True)
    cmd = sub.add_parser('extract')
    cmd.add_argument('--source', required=True)
    cmd.add_argument('--plan', required=True)
    cmd.add_argument('--out', required=True)
    cmd.add_argument('--derived-source')
    cmd.add_argument('--timeout-seconds', type=int)
    cmd = sub.add_parser('verify')
    cmd.add_argument('--manifest', required=True)
    cmd.add_argument('--plan')
    args = parser.parse_args(argv)
    if args.action == 'probe':
        data = probe_source(args.source, count_frames=args.count_frames)
        _write_new(args.out, json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'frame_count': data['frame_count'], 'fps': data['fps'],
                          'timing_mode': data['timing_mode'], 'has_audio': data['has_audio'],
                          'sha256': data['sha256']}))
    elif args.action == 'plan':
        probe = probe_source(args.source, count_frames=args.count_frames)
        options = {}
        if args.candidates:
            options = _load_json(args.candidates, 'candidates')
            if set(options) - {'scene_frames', 'pause_frames', 'speech_intervals'}:
                raise ValueError('candidates: unsupported field')
        options.update({'min_seconds': args.min_seconds, 'max_seconds': args.max_seconds,
                        'target_seconds': args.target_seconds, 'context_seconds': args.context_seconds})
        plan = plan_from_inspection(probe, video_id=args.video_id, **options)
        _segment_audit().export_plan(plan, args.out)
        print(json.dumps({'parts': len(plan['segments']), 'total_frames': plan['total_frames'],
                          'fps': plan['fps'], 'provisional': True,
                          'source_sha256': probe['sha256'], 'out': str(Path(args.out).resolve())}))
    elif args.action == 'keyframes':
        data = source_keyframes(args.source)
        _write_new(args.out, json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'keyframes': len(data['keyframe_frames']),
                          'unaligned': data['unaligned_count'],
                          'frame_aligned': data['frame_aligned'],
                          'sha256': data['sha256']}))
    elif args.action == 'extract':
        plan = _load_json(args.plan, 'plan')
        derived = _load_json(args.derived_source, 'derived_source') if args.derived_source else None
        manifest = extract_parts(args.source, plan, args.out, derived_source=derived,
                                 timeout_seconds=args.timeout_seconds)
        print(json.dumps({'parts': len(manifest['parts']), 'status': manifest['status'],
                          'extraction_method': manifest['extraction_method'],
                          'manifest': str(Path(args.out).resolve() / 'extraction-manifest.json')}))
    else:
        plan = _load_json(args.plan, 'plan') if args.plan else None
        verify_manifest(args.manifest, plan=plan)
        print(json.dumps({'verified': True, 'manifest': str(Path(args.manifest).resolve())}))


if __name__ == '__main__':
    main()
