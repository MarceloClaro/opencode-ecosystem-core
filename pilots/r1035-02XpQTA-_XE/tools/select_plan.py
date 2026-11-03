#!/usr/bin/env python3
"""Select a 60-90 s plan whose cuts land at ASR pauses.

This is an analysis tool, not a renderer. It uses the tested R1035 planner and
R1037 gap extractor. It writes a NEW plan directory and a selection report.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from integrations.video_dialogue_timing import dialogue_pauses  # noqa: E402
from integrations.video_local_ingest import source_keyframes  # noqa: E402
from integrations.video_segment_audit import (  # noqa: E402
    export_plan, plan_digest, plan_segments, validate_coverage)


def load(path):
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'unreadable JSON: {path}') from exc
    if not isinstance(data, dict):
        raise SystemExit(f'object required: {path}')
    return data


def metrics(plan):
    segments = plan['segments']
    durations = [segment['duration_seconds'] for segment in segments]
    return {
        'parts': len(segments),
        'min_duration': min(durations),
        'max_duration': max(durations),
        'mean_duration': sum(durations) / len(durations),
        'cuts_inside_speech': sum(bool(s['cut_inside_speech']) for s in segments),
        'technical_cuts': sum(s['boundary_kind'] == 'technical_cut' for s in segments),
        'pause_boundaries': sum(s['boundary_kind'] in
                               ('pause_candidate', 'scene_and_pause_candidate')
                               for s in segments),
        'duration_exceptions': sum(bool(s['duration_exception']) for s in segments),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspection', required=True)
    parser.add_argument('--asr', required=True)
    parser.add_argument('--audio', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--video-id')
    parser.add_argument('--targets', default=','.join(str(value) for value in range(61, 90)))
    parser.add_argument('--min-seconds', type=float, default=60)
    parser.add_argument('--max-seconds', type=float, default=90)
    parser.add_argument('--context-seconds', type=float, default=2)
    parser.add_argument('--min-gap', type=float, default=0.25)
    parser.add_argument('--max-gap', type=float, default=30.0)
    args = parser.parse_args()
    inspection = load(args.inspection)
    if inspection.get('timing_mode') != 'cfr_compatible':
        raise SystemExit('source timing is not CFR-compatible')
    total_frames = inspection.get('frame_count')
    fps = inspection.get('fps')
    asr = load(args.asr)
    words = dialogue_pauses(asr, fps=fps, total_frames=total_frames,
                            min_gap_seconds=args.min_gap,
                            max_gap_seconds=args.max_gap,
                            audio=args.audio)
    segment_asr = {'audio_sha256': asr.get('audio_sha256'),
                   'duration': asr.get('duration'),
                   'segments': [{**segment, 'words': []}
                                for segment in asr.get('segments', [])]}
    segments_only = dialogue_pauses(segment_asr, fps=fps, total_frames=total_frames,
                                    min_gap_seconds=args.min_gap,
                                    max_gap_seconds=args.max_gap)
    keyframes = source_keyframes(inspection['path'])
    if not keyframes['frame_aligned']:
        raise SystemExit('source has unaligned keyframes; exact split is unsafe')
    keyframe_set = set(keyframes['keyframe_frames'])
    speech_mask = bytearray(total_frames + 1)
    for start, end in words['speech_intervals_frames']:
        speech_mask[start:end] = b'\x01' * (end - start)
    safe_keyframes = sorted(frame for frame in keyframe_set if not speech_mask[frame])
    if not safe_keyframes:
        raise SystemExit('NO keyframe outside speech; refusing a technical-cut plan')
    pause_frames = safe_keyframes
    video_id = args.video_id or Path(inspection['path']).stem
    source = {
        'path': inspection['path'],
        'sha256': inspection['sha256'],
        'frame_count': total_frames,
        'fps': fps,
        'timing_verified': True,
        'timing_mode': 'cfr',
        'has_audio': inspection.get('has_audio') is True,
    }
    trials = []
    for target in [float(value) for value in args.targets.split(',')]:
        plan = plan_segments(video_id, total_frames, fps,
                             min_seconds=args.min_seconds,
                             max_seconds=args.max_seconds,
                             target_seconds=target,
                             context_seconds=args.context_seconds,
                             pause_frames=pause_frames,
                             speech_intervals=words['speech_intervals_frames'])
        plan['source'] = source
        validate_coverage(plan)
        non_keyframe = sum(segment['end_frame'] not in keyframe_set
                           for segment in plan['segments'][:-1])
        trial = {'target_seconds': target, **metrics(plan),
                 'non_keyframe_boundaries': non_keyframe,
                 'plan_sha256': plan_digest(plan)}
        trials.append({'trial': trial, 'plan': plan})
    trials.sort(key=lambda item: (
        item['trial']['cuts_inside_speech'],
        item['trial']['non_keyframe_boundaries'],
        item['trial']['technical_cuts'],
        item['trial']['duration_exceptions'],
        abs(item['trial']['mean_duration'] - item['trial']['target_seconds']),
        item['trial']['parts'],
    ))
    chosen = trials[0]
    if chosen['trial']['non_keyframe_boundaries']:
        raise SystemExit('no plan with all boundaries at source keyframes')
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f'output exists; refusing overwrite: {out}')
    export_plan(chosen['plan'], out)
    report = {
        'schema_version': 1,
        'video_id': video_id,
        'source_sha256': inspection['sha256'],
        'asr_sha256': words.get('audio_sha256'),
        'asr_duration_seconds': words.get('asr_duration_seconds'),
        'pause_candidates_word_gaps': len(words['pause_frames']),
        'pause_candidates_segment_gaps': len(segments_only['pause_frames']),
        'keyframe_count': len(keyframe_set),
        'keyframe_max_gap_frames': max(b - a for a, b in zip(keyframes['keyframe_frames'],
                                                             keyframes['keyframe_frames'][1:])),
        'safe_keyframe_candidates': len(safe_keyframes),
        'speech_intervals': len(words['speech_intervals']),
        'audio_check': words['audio_check'],
        'chosen': chosen['trial'],
        'boundary_keyframes': [
            {'segment_id': segment['id'], 'end_frame': segment['end_frame'],
             'pts_seconds': keyframes['keyframe_pts'][str(segment['end_frame'])]}
            for segment in chosen['plan']['segments'][:-1]],
        'trials': [item['trial'] for item in trials],
        'limitations': [
            'ASR gaps are acoustic candidates; the chosen plan still needs review',
            'no translation, diarization, TTS, lip sync or human approval performed',
            'selection prefers zero cuts inside speech, then fewer technical cuts',
        ],
    }
    (out / 'plan-selection.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'out': str(out.resolve()), 'chosen': chosen['trial'],
                      'trials': len(trials)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
