#!/usr/bin/env python3
"""QC técnico de vídeo local: streams, frames, loudness, silêncio e pretos.

Não é aprovação estética. Um `pass` significa apenas que os predicados
técnicos declarados passaram. Não usa rede, shell ou código de terceiro.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import re
import subprocess
import sys


def _run(args, timeout=120):
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if proc.returncode:
        raise RuntimeError((proc.stderr or proc.stdout or '')[-1200:])
    return proc.stdout


def probe(path: Path) -> dict:
    data = json.loads(_run([
        'ffprobe', '-v', 'error', '-count_frames', '-show_streams',
        '-show_format', '-of', 'json', str(path)]))
    streams = data.get('streams') or []
    video = next((s for s in streams if s.get('codec_type') == 'video'), None)
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    if video is None:
        raise ValueError('stream de vídeo ausente')
    frames = video.get('nb_read_frames') or video.get('nb_frames')
    fps = video.get('avg_frame_rate') or video.get('r_frame_rate') or '0/0'
    return {
        'path': str(path),
        'format': data.get('format', {}),
        'video': {
            'codec': video.get('codec_name'),
            'width': video.get('width'),
            'height': video.get('height'),
            'fps': fps,
            'frames': int(frames) if str(frames).isdigit() else None,
            'pix_fmt': video.get('pix_fmt'),
        },
        'audio': ({
            'codec': audio.get('codec_name'),
            'sample_rate': int(audio.get('sample_rate') or 0),
            'channels': int(audio.get('channels') or 0),
            'duration_seconds': float(audio['duration']) if audio.get('duration') else None,
        } if audio else None),
    }


def loudness(path: Path) -> dict:
    proc = subprocess.run([
        'ffmpeg', '-nostdin', '-hide_banner', '-i', str(path), '-af',
        'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
        capture_output=True, text=True, timeout=300)
    match = re.search(r'\{[^{}]*"input_i"[^{}]*\}', proc.stderr, re.S)
    if not match:
        return {'available': False, 'error': 'loudness indisponível'}
    data = json.loads(match.group(0))
    data['available'] = True
    return data


def silences(path: Path, threshold=-50, duration=0.5) -> list[dict]:
    proc = subprocess.run([
        'ffmpeg', '-nostdin', '-hide_banner', '-i', str(path), '-af',
        f'silencedetect=noise={threshold}dB:d={duration}', '-f', 'null', '-'],
        capture_output=True, text=True, timeout=300)
    starts = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', proc.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', proc.stderr)]
    return [{'start': start, 'end': end, 'seconds': round(end - start, 3)}
            for start, end in zip(starts, ends)]


def blacks(path: Path, duration=0.1, pix_th=0.10) -> list[dict]:
    proc = subprocess.run([
        'ffmpeg', '-nostdin', '-hide_banner', '-i', str(path), '-vf',
        f'blackdetect=d={duration}:pix_th={pix_th}', '-an', '-f', 'null', '-'],
        capture_output=True, text=True, timeout=300)
    starts = [float(x) for x in re.findall(r'black_start:([0-9.]+)', proc.stderr)]
    ends = [float(x) for x in re.findall(r'black_end:([0-9.]+)', proc.stderr)]
    return [{'start': start, 'end': end, 'seconds': round(end - start, 3)}
            for start, end in zip(starts, ends)]


def contact_sheet(path: Path, target: Path, frames: int | None) -> None:
    interval = max(1, (frames or 30) // 9)
    expr = f"select='not(mod(n,{interval}))',scale=320:-2,tile=3x3"
    _run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-vf', expr,
          '-frames:v', '1', '-y', str(target)])


def inspect(video: Path, *, expect_frames=None, expect_fps=None,
            loudness_target=-16.0, loudness_tolerance=1.0,
            max_true_peak=-1.5, max_silence=None, max_black=None,
            sheet: Path | None = None) -> dict:
    if video.is_symlink() or not video.is_file():
        raise FileNotFoundError(video)
    info = probe(video)
    checks = {}

    if expect_frames is not None:
        actual = info['video']['frames']
        checks['frame_count'] = {
            'ok': actual == expect_frames,
            'expected': expect_frames, 'actual': actual}
    if expect_fps is not None:
        actual = info['video']['fps']
        try:
            ok = Fraction(actual) == Fraction(expect_fps)
        except (ValueError, ZeroDivisionError):
            ok = False
        checks['fps'] = {'ok': ok, 'expected': expect_fps, 'actual': actual}

    measured = loudness(video)
    if measured.get('available'):
        integrated = float(measured['input_i'])
        true_peak = float(measured['input_tp'])
        checks['loudness'] = {
            'ok': abs(integrated - loudness_target) <= loudness_tolerance,
            'target': loudness_target, 'tolerance': loudness_tolerance,
            'actual': integrated}
        checks['true_peak'] = {
            'ok': true_peak <= max_true_peak,
            'max': max_true_peak, 'actual': true_peak}
    else:
        checks['loudness'] = {'ok': False, 'actual': None,
                              'error': measured.get('error')}

    silence = silences(video)
    if max_silence is not None:
        longest = max((item['seconds'] for item in silence), default=0.0)
        checks['silence'] = {
            'ok': longest <= max_silence,
            'max_allowed': max_silence, 'longest': longest}

    black = blacks(video)
    if max_black is not None:
        longest = max((item['seconds'] for item in black), default=0.0)
        checks['black'] = {
            'ok': longest <= max_black,
            'max_allowed': max_black, 'longest': longest}

    if sheet is not None:
        contact_sheet(video, sheet, info['video']['frames'])
        checks['contact_sheet'] = {
            'ok': sheet.is_file() and sheet.stat().st_size > 0,
            'path': str(sheet)}

    status = 'pass' if all(item.get('ok') for item in checks.values()) else 'fail'
    return {
        'schema_version': 1,
        'status': status,
        'probe': info,
        'checks': checks,
        'observations': {'silences': silence, 'black_intervals': black,
                         'loudness': measured},
        'limitations': [
            'QC técnico; não prova estética, inteligibilidade, emoção, lip sync ou tradução.',
            'Contato de frames é amostra; não substitui revisão humana.',
            'Silêncio e preto podem ser intencionais; o limite é contratual.',
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--expect-frames', type=int)
    parser.add_argument('--expect-fps')
    parser.add_argument('--loudness-target', type=float, default=-16.0)
    parser.add_argument('--loudness-tolerance', type=float, default=1.0)
    parser.add_argument('--max-true-peak', type=float, default=-1.5)
    parser.add_argument('--max-silence', type=float)
    parser.add_argument('--max-black', type=float)
    parser.add_argument('--contact-sheet', type=Path)
    args = parser.parse_args(argv)
    try:
        result = inspect(args.video, expect_frames=args.expect_frames,
                         expect_fps=args.expect_fps,
                         loudness_target=args.loudness_target,
                         loudness_tolerance=args.loudness_tolerance,
                         max_true_peak=args.max_true_peak,
                         max_silence=args.max_silence,
                         max_black=args.max_black,
                         sheet=args.contact_sheet)
    except FileNotFoundError:
        print('vídeo ausente ou inválido', file=sys.stderr)
        return 2
    except (RuntimeError, ValueError) as exc:
        print(f'falha de inspeção: {exc}', file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'out': str(args.out),
                      'checks': {k: v.get('ok') for k, v in result['checks'].items()}},
                     ensure_ascii=False))
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
