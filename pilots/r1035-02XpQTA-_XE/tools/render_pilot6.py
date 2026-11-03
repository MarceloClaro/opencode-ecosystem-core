#!/usr/bin/env python3
"""Render pilot P0006: center-cancelled background + PT-BR TTS + subtitles.

This is a draft. It does not claim source separation, lip sync or approval.
"""
import hashlib
import json
import re
import subprocess
import wave
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'parts-final/parts/02XpQTA-_XE-P0006.mp4'
DIALOGUE = ROOT / 'pilot-P0006/dialogue-dub-characters.json'
TTS = ROOT / 'pilot-P0006/tts-manifest-v2.json'
SUBS = ROOT / 'pilot-P0006/subtitles-v2'
OUT = ROOT / 'pilot-P0006/render-v3'
OUT.mkdir(parents=True, exist_ok=True)
SR = 24000


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams',
                             '-show_format', '-of', 'json', str(path)],
                            capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    video = next(stream for stream in data['streams'] if stream['codec_type'] == 'video')
    audio = next((stream for stream in data['streams'] if stream['codec_type'] == 'audio'), None)
    return {'duration': float(data['format']['duration']),
            'video': {'codec': video.get('codec_name'), 'width': video.get('width'),
                      'height': video.get('height'), 'fps': video.get('avg_frame_rate'),
                      'frames': int(video.get('nb_read_frames', video.get('nb_frames', 0)))},
            'audio': None if audio is None else {'codec': audio.get('codec_name'),
                      'sample_rate': audio.get('sample_rate'), 'channels': audio.get('channels')}}


def loudness(path):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path),
                             '-af', 'ebur128', '-f', 'null', '-'],
                            capture_output=True, text=True, timeout=600)
    text = result.stderr
    integrated = re.findall(r'I:\s*(-?[0-9.]+) LUFS', text)
    peak = re.findall(r'True peak:\s*(-?[0-9.]+) dBFS', text)
    if not peak:
        peak = re.findall(r'Peak:\s*(-?[0-9.]+) dBFS', text)
    return {'integrated_lufs': float(integrated[-1]) if integrated else None,
            'true_peak_dbfs': float(peak[-1]) if peak else None}


def build_dialogue():
    dialogue = json.loads(DIALOGUE.read_text())
    tts = json.loads(TTS.read_text())
    by_id = {unit['id']: unit for unit in tts['units']}
    frames = int(round(float(dialogue['part_duration_seconds']) * SR))
    buffer = array('i', [0]) * frames
    peak = 0
    for unit in dialogue['units']:
        line = by_id[unit['id']]
        with wave.open(str(ROOT / line['artifact']), 'rb') as stream:
            if stream.getframerate() != SR or stream.getnchannels() != 1 or stream.getsampwidth() != 2:
                raise SystemExit(f'bad TTS format: {line["artifact"]}')
            samples = array('h')
            samples.frombytes(stream.readframes(stream.getnframes()))
        start = int(round(float(unit['start_part']) * SR))
        for offset, sample in enumerate(samples):
            index = start + offset
            if index >= frames:
                break
            value = buffer[index] + sample
            buffer[index] = value
            peak = max(peak, abs(value))
    gain = 1.0
    if peak > 30000:
        gain = 0.90 * 32767 / peak
        buffer = array('i', (int(value * gain) for value in buffer))
    target = OUT / 'dialogue-24k.wav'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    with wave.open(str(target), 'wb') as stream:
        stream.setparams((1, 2, SR, 0, 'NONE', 'not compressed'))
        data = array('h', (max(-32768, min(32767, value)) for value in buffer))
        stream.writeframes(data.tobytes())
    return target, {'peak_before_gain': peak, 'gain': round(gain, 6),
                    'duration_seconds': frames / SR, 'sha256': sha256(target)}


def render_soft(dialogue_wav):
    target = OUT / 'P0006-ptbr-soft.mp4'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    command = [
        'ffmpeg', '-nostdin', '-v', 'error',
        '-i', str(PART), '-i', str(dialogue_wav), '-i', str(SUBS / 'subtitles.pt-BR.srt'),
        '-filter_complex',
        '[0:a]pan=stereo|c0=0.5*c0-0.5*c1|c1=0.5*c1-0.5*c0,volume=2.8[bg];'
        '[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=1.0[vo];'
        '[bg][vo]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,'
        'alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a]',
        '-map', '0:v:0', '-map', '[a]', '-map', '2:s',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-c:s', 'mov_text',
        '-metadata:s:s:0', 'language=por', '-movflags', '+faststart', '-y', str(target),
    ]
    subprocess.run(command, check=True, timeout=1800)
    return target


def render_bar(soft, expected_frames, expected_duration):
    target = OUT / 'P0006-ptbr-bar.mp4'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    command = [
        'ffmpeg', '-nostdin', '-v', 'error', '-i', str(soft),
        '-map', '0:v:0', '-map', '0:a:0', '-sn',
        '-vf',
        'drawbox=x=0:y=540:w=1280:h=180:color=black@1.0:t=fill,'
        'subtitles=' + str(SUBS / 'subtitles.pt-BR.ass').replace(':', '\\:')
        + ':fontsdir=/usr/share/fonts/truetype/dejavu',
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
        '-fps_mode', 'cfr', '-frames:v', str(expected_frames),
        '-t', f'{expected_duration:.6f}',
        '-c:a', 'copy', '-movflags', '+faststart', '-y', str(target),
    ]
    subprocess.run(command, check=True, timeout=1800)
    return target


def main():
    dialogue, dialogue_meta = build_dialogue()
    expected = probe(PART)
    expected_frames = expected['video']['frames']
    expected_duration = expected_frames / 25.0
    soft = render_soft(dialogue)
    bar = render_bar(soft, expected_frames, expected_duration)
    manifest = {
        'schema_version': 1,
        'part_id': '02XpQTA-_XE-P0006',
        'status': 'draft_rendered_pending_human_review',
        'lipsync': False,
        'source_separation': 'center_channel_cancellation_heuristic',
        'dialogue': dialogue_meta,
        'outputs': {},
        'limitations': [
            'center cancellation reduces but does not remove original dialogue',
            'dubbed timing is fitted; overlap may occur in rapid lines',
            'no lip sync and no native-speaker review',
            'soft variant still shows original burned-in English subtitles',
            'bar variant covers the lower 140 px and burns PT-BR subtitles',
        ],
    }
    for path in (soft, bar):
        output_probe = probe(path)
        if output_probe['video']['frames'] != expected['video']['frames']:
            raise SystemExit(f'frame count changed: {path.name}')
        if abs(output_probe['duration'] - expected['duration']) > 0.15:
            raise SystemExit(f'duration changed: {path.name}')
        manifest['outputs'][path.name] = {
            'sha256': sha256(path), 'bytes': path.stat().st_size,
            'probe': output_probe, 'loudness': loudness(path),
            'states': {'technical_qa': 'pending', 'audiovisual_review': 'pending',
                       'approval': 'pending'},
        }
    (OUT / 'render-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'soft': str(soft), 'bar': str(bar)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
