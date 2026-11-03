"""R1037: derive speech gaps from local ASR word timestamps.

No translation, diarization, synthesis, audio editing or scene semantics.
Candidates are midpoints of measured gaps; human audiovisual review remains.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

FFPROBE = shutil.which('ffprobe')


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label}: finite number required')
    return float(value)


def _rate(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{1,12}(?:/\d{1,12})?', value):
        raise ValueError('fps: rational string required')
    try:
        rate = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('fps: invalid rational') from exc
    if not 0 < rate <= 1000:
        raise ValueError('fps outside (0, 1000]')
    return rate


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _audio_duration(path):
    if not FFPROBE:
        raise ValueError('ffprobe not installed for audio duration check')
    result = subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'a:0',
                             '-show_entries', 'stream=codec_type:format=duration',
                             '-of', 'json', str(path)],
                            capture_output=True, text=True, timeout=120)
    if result.returncode != 0 or result.stderr.strip():
        raise ValueError('audio duration probe failed')
    try:
        data = json.loads(result.stdout)
        if not data.get('streams'):
            raise ValueError('no audio stream')
        return float(data['format']['duration'])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError('audio duration unavailable') from exc


def _intervals(alignment):
    if not isinstance(alignment, dict):
        raise ValueError('alignment object required')
    duration = _number(alignment.get('duration'), 'alignment duration')
    if duration <= 0:
        raise ValueError('alignment duration must be positive')
    segments = alignment.get('segments')
    if not isinstance(segments, list):
        raise ValueError('alignment segments list required')
    tolerance = 0.05
    intervals = []
    degenerate = 0
    for segment in segments:
        if not isinstance(segment, dict):
            raise ValueError('segment object required')
        start = _number(segment.get('start'), 'segment start')
        end = _number(segment.get('end'), 'segment end')
        if start < 0 or end <= start or end > duration + tolerance:
            raise ValueError('segment outside ASR duration')
        words = segment.get('words')
        if words is None:
            words = []
        if not isinstance(words, list):
            raise ValueError('segment words list required')
        if words:
            for word in words:
                if not isinstance(word, dict):
                    raise ValueError('word object required')
                wstart = _number(word.get('start'), 'word start')
                wend = _number(word.get('end'), 'word end')
                text = word.get('text')
                if not isinstance(text, str) or not text.strip():
                    raise ValueError('aligned word text required')
                if wstart < 0 or wend < wstart or wend > duration + tolerance:
                    raise ValueError('word outside ASR duration')
                if wend - wstart <= 1e-9:
                    degenerate += 1
                    continue
                intervals.append([wstart, wend])
        elif isinstance(segment.get('text'), str) and segment['text'].strip():
            intervals.append([start, end])
        # Empty segment without words is not asserted to be speech.
    return duration, intervals, degenerate


def _merge(intervals):
    merged = []
    for start, end in sorted(intervals, key=lambda item: (item[0], item[1])):
        if merged and start <= merged[-1][1] + 1e-9:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def dialogue_pauses(alignment, *, fps, total_frames, min_gap_seconds=0.25,
                    max_gap_seconds=8.0, audio=None, count_tolerance_seconds=0.5):
    """Return gap midpoints and merged speech intervals in seconds and frames.

    The ASR duration may exceed the frame-derived duration by up to
    ``count_tolerance_seconds`` (audio priming/tail). Candidates are clamped.
    """
    rate = _rate(fps)
    if type(total_frames) is not int or isinstance(total_frames, bool) or total_frames < 2:
        raise ValueError('total_frames must be an integer >= 2')
    total_seconds = float(Fraction(total_frames, 1) / rate)
    duration, intervals, degenerate = _intervals(alignment)
    if duration > total_seconds + count_tolerance_seconds:
        raise ValueError('ASR duration exceeds total_frames duration; check mapping')
    minimum = _number(min_gap_seconds, 'min_gap_seconds')
    maximum = _number(max_gap_seconds, 'max_gap_seconds')
    if minimum < 0 or maximum <= 0 or minimum > maximum:
        raise ValueError('invalid gap range')
    audio_check = {'checked': False, 'path': None}
    if audio is not None:
        file = Path(audio)
        if file.is_symlink() or not file.is_file():
            raise ValueError('audio: existing regular file required')
        expected = alignment.get('audio_sha256')
        if not isinstance(expected, str) or _sha256(file) != expected:
            raise ValueError('audio hash mismatch; ASR does not belong to this file')
        measured = _audio_duration(file)
        if abs(measured - duration) > max(0.1, 2 / float(rate)):
            raise ValueError('audio duration mismatch')
        audio_check = {'checked': True, 'path': str(file.resolve()),
                       'sha256': expected, 'duration_seconds': measured}
    merged = _merge(intervals)
    gaps = []
    for left, right in zip(merged, merged[1:]):
        gap = right[0] - left[1]
        if minimum <= gap <= maximum:
            gaps.append((left[1], right[0], gap))
    frames = []
    for start, end, _gap in gaps:
        midpoint = Fraction(str((start + end) / 2))
        frame = math.floor(midpoint * rate + Fraction(1, 2))
        frames.append(max(1, min(total_frames - 1, frame)))
    pause_frames = sorted(set(frames))
    speech_frames = []
    for start, end in merged:
        first = max(0, min(total_frames, math.floor(Fraction(str(start)) * rate)))
        last = max(0, min(total_frames, math.ceil(Fraction(str(end)) * rate)))
        if last > first:
            speech_frames.append([first, last])
    return {
        'schema_version': 1,
        'method': 'asr_word_gap_midpoint',
        'fps': f'{rate.numerator}/{rate.denominator}',
        'total_frames': total_frames,
        'total_seconds': total_seconds,
        'audio_sha256': alignment.get('audio_sha256'),
        'asr_duration_seconds': duration,
        'min_gap_seconds': minimum,
        'max_gap_seconds': maximum,
        'speech_intervals': [[round(a, 6), round(b, 6)] for a, b in merged],
        'speech_intervals_frames': speech_frames,
        'pause_frames': pause_frames,
        'gap_count': len(gaps),
        'degenerate_words_skipped': degenerate,
        'audio_check': audio_check,
        'limitations': [
            'ASR gaps are acoustic evidence, not semantic scene boundaries',
            'small ASR models may miss speech or merge words; human review required',
            'a gap midpoint may fall on breath, music or an unsuitable visual cut',
            'no translation, diarization, lip sync or audiovisual approval performed',
        ],
    }


def _write_new(path, content):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(content)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--alignment', required=True)
    parser.add_argument('--fps', required=True)
    parser.add_argument('--total-frames', required=True, type=int)
    parser.add_argument('--out', required=True)
    parser.add_argument('--min-gap', type=float, default=0.25)
    parser.add_argument('--max-gap', type=float, default=8.0)
    parser.add_argument('--audio')
    args = parser.parse_args(argv)
    try:
        alignment = json.loads(Path(args.alignment).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('alignment unreadable') from exc
    result = dialogue_pauses(alignment, fps=args.fps, total_frames=args.total_frames,
                             min_gap_seconds=args.min_gap, max_gap_seconds=args.max_gap,
                             audio=args.audio)
    _write_new(args.out, json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'pause_frames': len(result['pause_frames']),
                      'speech_intervals': len(result['speech_intervals']),
                      'gap_count': result['gap_count'],
                      'audio_checked': result['audio_check']['checked']}))


if __name__ == '__main__':
    main()
