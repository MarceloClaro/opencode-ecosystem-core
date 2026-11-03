"""R1035: provisional CFR partition plans and fail-closed receipt policy.

No network, decoder, render, voice synthesis or human approval is performed.
Frames are half-open editorial ranges. Context is NEVER an assembly input.
Receipts are operator-supplied assertions: hashes detect changes, not truth.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _integer(value, name, minimum=0, maximum=10**9):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f'{name}: integer outside allowed range')
    return value


def _number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'{name}: finite number required')
    return value


def _fps(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{1,12}(?:/\d{1,12})?', value):
        raise ValueError('fps: positive rational string required')
    try:
        rate = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('invalid fps') from exc
    if not 0 < rate <= 1000:
        raise ValueError('fps outside (0, 1000]')
    return rate


def _options(video_id, total_frames, fps, min_seconds, max_seconds,
             target_seconds, context_seconds):
    if not isinstance(video_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', video_id):
        raise ValueError('invalid video_id')
    _integer(total_frames, 'total_frames', 1)
    rate = _fps(fps)
    for key, value in [('min', min_seconds), ('max', max_seconds),
                       ('target', target_seconds), ('context', context_seconds)]:
        _number(value, key)
    if not 0 < min_seconds <= target_seconds <= max_seconds <= 86400:
        raise ValueError('invalid segment duration range')
    if not 0 <= context_seconds <= 90:
        raise ValueError('context must be in [0, 90] seconds')
    minimum = math.ceil(Fraction(str(min_seconds)) * rate)
    maximum = math.floor(Fraction(str(max_seconds)) * rate)
    if maximum < minimum:
        raise ValueError('duration range contains no integer frame length')
    context = math.ceil(Fraction(str(context_seconds)) * rate)
    return rate, minimum, maximum, context


def _candidates(frames, total, label):
    if frames is None:
        return []
    if not isinstance(frames, list) or len(frames) > 100000:
        raise ValueError(f'{label}: bounded list required')
    for frame in frames:
        _integer(frame, label, 0, total)
    return sorted(set(frames))


def _speech(intervals, total):
    if intervals is None:
        return []
    if not isinstance(intervals, list) or len(intervals) > 100000:
        raise ValueError('speech_intervals: bounded list required')
    result = []
    for pair in intervals:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError('speech interval must contain two frames')
        start, end = pair
        _integer(start, 'speech start', 0, total)
        _integer(end, 'speech end', 0, total)
        if end <= start:
            raise ValueError('speech interval reversed or empty')
        result.append([start, end])
    return sorted(result)


def _speech_mask(speech, total):
    """O(1) boundary lookup even with thousands of ASR speech intervals."""
    mask = bytearray(total + 1)
    for start, end in speech:
        mask[start:end] = b'\x01' * (end - start)
    return mask


def _boundary_kind(frame, total, scenes, pauses):
    if frame == total:
        return 'source_end'
    if frame in scenes and frame in pauses:
        return 'scene_and_pause_candidate'
    if frame in pauses:
        return 'pause_candidate'
    if frame in scenes:
        return 'scene_candidate'
    return 'technical_cut'


def plan_segments(video_id, total_frames, fps, *, min_seconds=60, max_seconds=90,
                  target_seconds=75, context_seconds=2, scene_frames=None,
                  pause_frames=None, speech_intervals=None):
    """Plan exact frame coverage; candidate labels are NOT scene detection.

    Select a feasible part count first; reserve a feasible tail at every cut.
    When the range is impossible, redistribute into short parts and flag them.
    VFR requires a separate timestamp-aware plan/normalization, not this API.
    """
    rate, minimum, maximum, context = _options(
        video_id, total_frames, fps, min_seconds, max_seconds, target_seconds, context_seconds)
    scenes = _candidates(scene_frames, total_frames, 'scene_frames')
    pauses = _candidates(pause_frames, total_frames, 'pause_frames')
    speech = _speech(speech_intervals, total_frames)
    speech_mask = _speech_mask(speech, total_frames)
    least = (total_frames + maximum - 1) // maximum
    most = total_frames // minimum
    feasible = least <= most
    preferred = max(1, round(Fraction(total_frames, 1) / rate / Fraction(str(target_seconds))))
    count = min(most, max(least, preferred)) if feasible else least
    if count > 10000:
        raise ValueError('plan exceeds 10000 parts; split into audited batches')
    effective_min = minimum if feasible else 1
    scene_set, pause_set = set(scenes), set(pauses)
    boundaries, start = [], 0
    for index in range(count - 1):
        remaining = count - index - 1
        lo = max(start + effective_min, total_frames - remaining * maximum)
        hi = min(start + maximum, total_frames - remaining * effective_min)
        desired = max(lo, min(hi, start + round(Fraction(total_frames - start, remaining + 1))))
        candidates = [f for f in scene_set | pause_set if lo <= f <= hi and not speech_mask[f]]
        if candidates:
            def score(frame):
                priority = 0 if frame in scene_set and frame in pause_set else (1 if frame in pause_set else 2)
                return priority, abs(frame - desired), frame
            end = min(candidates, key=score)
        else:
            alternatives = {desired, lo, hi}
            alternatives.update(f for interval in speech for f in interval if lo <= f <= hi)
            safe = [f for f in alternatives if not speech_mask[f]]
            end = min(safe, key=lambda f: (abs(f - desired), f)) if safe else desired
        boundaries.append(end)
        start = end
    boundaries.append(total_frames)
    result = {
        'schema_version': 1, 'video_id': video_id, 'total_frames': total_frames,
        'fps': f'{rate.numerator}/{rate.denominator}',
        'duration_seconds': float(total_frames / rate),
        'timing_basis': 'provisional_cfr_frame_index',
        'parameters': {'min_seconds': min_seconds, 'max_seconds': max_seconds,
                       'target_seconds': target_seconds, 'context_seconds': context_seconds},
        'candidates': {'scene_frames': scenes, 'pause_frames': pauses, 'speech_intervals': speech},
        'segments': [],
    }
    start = 0
    for index, end in enumerate(boundaries, 1):
        result['segments'].append({
            'id': f'{video_id}-P{index:04d}', 'index': index,
            'start_frame': start, 'end_frame': end,
            'start_seconds': float(start / rate), 'end_seconds': float(end / rate),
            'duration_seconds': float((end - start) / rate),
            'context_start_frame': max(0, start - context),
            'context_end_frame': min(total_frames, end + context),
            'boundary_kind': _boundary_kind(end, total_frames, scene_set, pause_set),
            'cut_inside_speech': end < total_frames and bool(speech_mask[end]),
            'duration_exception': not minimum <= end - start <= maximum,
            'review_required': True,
            'stages': {'planning': 'completed_provisional', 'extraction': 'pending',
                       'editing': 'pending', 'technical_qa': 'pending',
                       'audiovisual_review': 'pending', 'approval': 'pending'},
        })
        start = end
    validate_coverage(result)
    return result


def _same_time(value, expected, name):
    if abs(_number(value, name) - expected) > 1e-8:
        raise ValueError(f'{name}: inconsistent frame/time mapping')


def validate_coverage(plan):
    """Validate derived fields as well as gap-free, non-overlapping ranges."""
    if not isinstance(plan, dict) or type(plan.get('schema_version')) is not int or plan['schema_version'] != 1:
        raise ValueError('unsupported plan schema')
    try:
        params = plan['parameters']
        if not isinstance(params, dict):
            raise ValueError('parameters object required')
        rate, minimum, maximum, context = _options(
            plan['video_id'], plan['total_frames'], plan['fps'], **params)
        total = plan['total_frames']
        if plan.get('timing_basis') != 'provisional_cfr_frame_index':
            raise ValueError('unsupported timing basis; inspect source timestamps')
        _same_time(plan['duration_seconds'], float(total / rate), 'plan duration')
        candidates = plan['candidates']
        scenes = set(_candidates(candidates['scene_frames'], total, 'scene_frames'))
        pauses = set(_candidates(candidates['pause_frames'], total, 'pause_frames'))
        speech = _speech(candidates['speech_intervals'], total)
        speech_mask = _speech_mask(speech, total)
        segments = plan['segments']
        if not isinstance(segments, list) or not 1 <= len(segments) <= 10000:
            raise ValueError('nonempty bounded segments list required')
        expected_start = 0
        for index, segment in enumerate(segments, 1):
            if not isinstance(segment, dict):
                raise ValueError('segment object required')
            start = _integer(segment['start_frame'], 'start_frame', 0, total)
            end = _integer(segment['end_frame'], 'end_frame', 1, total)
            if start != expected_start or end <= start:
                raise ValueError('gap, overlap or empty editorial segment')
            if segment['id'] != f'{plan["video_id"]}-P{index:04d}' or _integer(segment['index'], 'index', 1) != index:
                raise ValueError('segment ID/order mismatch')
            _same_time(segment['start_seconds'], float(start / rate), 'start_seconds')
            _same_time(segment['end_seconds'], float(end / rate), 'end_seconds')
            _same_time(segment['duration_seconds'], float((end - start) / rate), 'duration_seconds')
            for key, expected in [('context_start_frame', max(0, start-context)),
                                  ('context_end_frame', min(total, end+context))]:
                if _integer(segment[key], key, 0, total) != expected:
                    raise ValueError('context mismatch; do not assemble context ranges')
            exception = not minimum <= end-start <= maximum
            inside = end < total and bool(speech_mask[end])
            if segment['duration_exception'] is not exception or segment['cut_inside_speech'] is not inside:
                raise ValueError('exception/speech flags inconsistent with frames')
            if segment['review_required'] is not True:
                raise ValueError('audiovisual review is mandatory')
            if segment['boundary_kind'] != _boundary_kind(end, total, scenes, pauses):
                raise ValueError('boundary evidence mismatch')
            expected_start = end
        if expected_start != total:
            raise ValueError('source tail missing')
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('malformed coverage plan') from exc
    return True


_EDITORIAL_FIELDS = ('id', 'index', 'start_frame', 'end_frame', 'start_seconds',
    'end_seconds', 'duration_seconds', 'context_start_frame', 'context_end_frame',
    'boundary_kind', 'cut_inside_speech', 'duration_exception', 'review_required')


def plan_digest(plan):
    """Bind approvals to the ENTIRE editorial plan and source, not only IDs."""
    validate_coverage(plan)
    snapshot = {key: plan.get(key) for key in ('schema_version', 'video_id', 'fps',
        'total_frames', 'duration_seconds', 'timing_basis', 'parameters', 'candidates', 'source')}
    snapshot['segments'] = [{key: s[key] for key in _EDITORIAL_FIELDS} for s in plan['segments']]
    try:
        payload = json.dumps(snapshot, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':'))
    except (TypeError, ValueError) as exc:
        raise ValueError('plan must contain finite JSON data') from exc
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _artifact(record, label):
    if not isinstance(record, dict):
        raise ValueError(f'{label}: artifact record required')
    path, expected = record.get('path'), record.get('sha256')
    if not isinstance(path, str) or not path or any(ord(c) < 32 for c in path):
        raise ValueError(f'{label}: invalid path')
    file = Path(path)
    if not file.is_absolute() or file.is_symlink() or not file.is_file():
        raise ValueError(f'{label}: existing absolute regular path required')
    if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
        raise ValueError(f'{label}: sha256 required')
    if file.stat().st_size == 0 or sha256_file(file) != expected:
        raise ValueError(f'{label}: hash mismatch or empty file')
    return file.resolve(), expected


def assembly_inputs(plan):
    """Gate DECLARED receipts, not media quality. Return ordered input paths.

    No concatenation is executed. A future renderer must recheck these inputs
    and independently decode/probe them immediately before assembly (TOCTOU).
    Human review records are not cryptographically authenticated by this API.
    """
    validate_coverage(plan)
    for segment in plan['segments']:
        if not isinstance(segment.get('edited'), dict) or not isinstance(segment.get('approval'), dict):
            raise ValueError(f'{segment["id"]}: edited artifact and approval required')
    source = plan.get('source')
    source_path, _ = _artifact(source, 'source')
    if source.get('timing_verified') is not True or source.get('timing_mode') != 'cfr':
        raise ValueError('source CFR timing must be inspected; VFR needs explicit mapping')
    if type(source.get('has_audio')) is not bool:
        raise ValueError('source audio presence must be inspected')
    binding = plan_digest(plan)
    paths, seen, signature = [], {source_path}, None
    rate = _fps(plan['fps'])
    for segment in plan['segments']:
        path, digest = _artifact(segment['edited'], 'edited')
        if path in seen:
            raise ValueError('duplicate edited input or source reused as output')
        seen.add(path)
        approval = segment['approval']
        if any(approval.get(key) is not True for key in ('approved', 'technical_qa', 'audiovisual_review')):
            raise ValueError('approval and both reviews must be explicitly true')
        if not isinstance(approval.get('reviewer'), str) or not approval['reviewer'].strip():
            raise ValueError('approval reviewer missing')
        qa = segment.get('technical_qa')
        if not isinstance(qa, dict) or qa.get('passed') is not True or qa.get('av_sync_reviewed') is not True:
            raise ValueError('technical QA and AV sync review required')
        for record in (approval, qa):
            if record.get('artifact_sha256') != digest or record.get('plan_sha256') != binding:
                raise ValueError('approval/QA artifact or plan hash mismatch')
        expected_frames = segment['end_frame'] - segment['start_frame']
        if _integer(qa.get('frame_count'), 'QA frame_count', 1) != expected_frames or _fps(qa.get('fps')) != rate:
            raise ValueError('QA frame count/fps mismatch')
        if abs(_number(qa.get('duration_seconds'), 'QA duration') - segment['duration_seconds']) > max(0.05, float(1/rate)):
            raise ValueError('QA duration mismatch')
        if type(qa.get('decode_errors')) is not int or qa['decode_errors'] != 0:
            raise ValueError('QA decode errors missing or nonzero')
        if qa.get('audio_present') is not source['has_audio']:
            raise ValueError('QA audio presence mismatch')
        streams = qa.get('stream_signature')
        required = ('video_codec', 'width', 'height', 'pixel_format')
        if source['has_audio']:
            required += ('audio_codec', 'sample_rate', 'channels')
        if not isinstance(streams, dict) or any(streams.get(key) in (None, '') for key in required):
            raise ValueError('QA stream signature incomplete')
        if signature is None:
            signature = streams
        elif signature != streams:
            raise ValueError('stream signatures differ; normalize and review before assembly')
        paths.append(str(path))
    return paths


def export_plan(plan, directory):
    """Write a NEW directory; never replace a prior plan or approval."""
    validate_coverage(plan)
    payload = json.dumps(plan, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    digest = plan_digest(plan)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    with (directory/'segments.json').open('x', encoding='utf-8') as stream:
        stream.write(payload)
    with (directory/'segments.csv').open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=_EDITORIAL_FIELDS)
        writer.writeheader()
        for segment in plan['segments']:
            writer.writerow({key: segment[key] for key in _EDITORIAL_FIELDS})
    with (directory/'plan-sha256.txt').open('x', encoding='ascii') as stream:
        stream.write(digest + '\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    cmd = sub.add_parser('plan', help='provisional plan, not extraction')
    cmd.add_argument('--video-id', required=True)
    cmd.add_argument('--total-frames', required=True, type=int)
    cmd.add_argument('--fps', required=True)
    cmd.add_argument('--candidates', help='local JSON: scene_frames, pause_frames, speech_intervals')
    cmd.add_argument('--out', required=True)
    for action in ('validate', 'assembly-check'):
        cmd = sub.add_parser(action)
        cmd.add_argument('plan')
    args = parser.parse_args(argv)
    if args.action == 'plan':
        options = json.loads(Path(args.candidates).read_text()) if args.candidates else {}
        if not isinstance(options, dict) or set(options) - {'scene_frames', 'pause_frames', 'speech_intervals'}:
            raise ValueError('candidate file must contain only supported candidate fields')
        plan = plan_segments(args.video_id, args.total_frames, args.fps, **options)
        export_plan(plan, args.out)
        print(json.dumps({'parts': len(plan['segments']), 'provisional': True, 'extracted': False}))
    else:
        plan = json.loads(Path(args.plan).read_text())
        if args.action == 'validate':
            print(json.dumps({'coverage_valid': validate_coverage(plan), 'plan_sha256': plan_digest(plan),
                              'media_qa_performed': False}))
        else:
            print(json.dumps({'inputs': assembly_inputs(plan), 'receipt_policy_passed': True,
                              'media_qa_performed': False, 'assembled': False}))


if __name__ == '__main__':
    main()
