#!/usr/bin/env python3
"""Final pilot render: cleaned music stem, processed dialogue, stems + stereo."""
import hashlib
import json
import re
import subprocess
import wave
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'parts-final/parts/02XpQTA-_XE-P0006.mp4'
MUSIC = ROOT / 'pilot-P0006/stems/music-clean.wav'
VOCALS = ROOT / 'pilot-P0006/stems/vocals.wav'
TURNS = ROOT / 'pilot-P0006/dialogue-turns-reviewed.json'
TTS = ROOT / 'pilot-P0006/tts-manifest-final6.json'
SUBS = ROOT / 'pilot-P0006/subtitles-final6'
OUT = ROOT / 'pilot-P0006/render-final6'
OUT.mkdir(parents=True, exist_ok=True)
SR = 24000
VOICE_FILTER = (
    'aresample=48000,highpass=f=80,'
    'equalizer=f=2800:t=q:w=1.0:g=2,'
    'equalizer=f=6500:t=q:w=1.0:g=-2,'
    'acompressor=threshold=0.10:ratio=2.5:attack=8:release=120,'
    'deesser=i=0.4'
)


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
    video = next((stream for stream in data['streams']
                  if stream['codec_type'] == 'video'), None)
    audio = next((stream for stream in data['streams']
                  if stream['codec_type'] == 'audio'), None)
    return {'duration': float(data['format']['duration']),
            'video': None if video is None else {
                'codec': video.get('codec_name'), 'width': video.get('width'),
                'height': video.get('height'), 'fps': video.get('avg_frame_rate'),
                'frames': int(video.get('nb_read_frames', video.get('nb_frames', 0)))},
            'audio': None if audio is None else {
                'codec': audio.get('codec_name'),
                'sample_rate': audio.get('sample_rate'),
                'channels': audio.get('channels')}}


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
    turns = json.loads(TURNS.read_text())
    tts = json.loads(TTS.read_text())
    by_id = {turn['id']: turn for turn in tts['turns']}
    frames = int(round(float(turns['part_duration_seconds']) * SR))
    buffer = array('i', [0]) * frames
    peak = 0
    for turn in turns['turns']:
        line = by_id[turn['id']]
        with wave.open(str(ROOT / line['artifact']), 'rb') as stream:
            if stream.getframerate() != SR or stream.getnchannels() != 1 or stream.getsampwidth() != 2:
                raise SystemExit(f'bad TTS format: {line["artifact"]}')
            samples = array('h')
            samples.frombytes(stream.readframes(stream.getnframes()))
        fade_in = int(0.010 * SR)
        fade_out = int(0.030 * SR)
        for index in range(min(fade_in, len(samples))):
            samples[index] = int(samples[index] * index / fade_in)
        for index in range(1, min(fade_out, len(samples)) + 1):
            samples[-index] = int(samples[-index] * (index - 1) / fade_out)
        start = int(round(float(turn['start_part']) * SR))
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


def process_dialogue(raw):
    target = OUT / 'dialogue-processed.wav'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(raw),
                    '-af', VOICE_FILTER, '-ar', '48000', '-ac', '2',
                    '-c:a', 'pcm_s16le', '-y', str(target)],
                   check=True, timeout=600)
    return target


def mix_audio(dialogue):
    target = OUT / 'mix-48k.wav'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    command = [
        'ffmpeg', '-nostdin', '-v', 'error', '-i', str(MUSIC), '-i', str(dialogue),
        '-filter_complex',
        '[0:a]volume=1.8[music];'
        '[1:a]asplit=2[vo][sc];'
        '[music][sc]sidechaincompress=threshold=0.025:ratio=3.5:attack=20:release=300:makeup=1[ducked];'
        '[ducked][vo]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,'
        'alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a]',
        '-map', '[a]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', '-y', str(target),
    ]
    subprocess.run(command, check=True, timeout=1800)
    return target


def render_soft(mix):
    target = OUT / 'P0006-ptbr-final-soft.mp4'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    command = [
        'ffmpeg', '-nostdin', '-v', 'error', '-i', str(PART), '-i', str(mix),
        '-i', str(SUBS / 'subtitles.pt-BR.srt'),
        '-map', '0:v:0', '-map', '1:a:0', '-map', '2:s',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-c:s', 'mov_text', '-metadata:s:s:0', 'language=por',
        '-movflags', '+faststart', '-y', str(target),
    ]
    subprocess.run(command, check=True, timeout=1800)
    return target


def render_bar(soft, expected_frames, expected_duration):
    target = OUT / 'P0006-ptbr-final-bar.mp4'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    command = [
        'ffmpeg', '-nostdin', '-v', 'error', '-i', str(soft),
        '-map', '0:v:0', '-map', '0:a:0', '-sn',
        '-vf', 'drawbox=x=0:y=540:w=1280:h=180:color=black@1.0:t=fill,'
        'subtitles=' + str(SUBS / 'subtitles.pt-BR.ass').replace(':', '\\:')
        + ':fontsdir=/usr/share/fonts/truetype/dejavu',
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
        '-fps_mode', 'cfr', '-frames:v', str(expected_frames),
        '-t', f'{expected_duration:.6f}', '-c:a', 'copy',
        '-movflags', '+faststart', '-y', str(target),
    ]
    subprocess.run(command, check=True, timeout=1800)
    return target


def main():
    raw, raw_meta = build_dialogue()
    dialogue = process_dialogue(raw)
    mix = mix_audio(dialogue)
    expected = probe(PART)
    expected_frames = expected['video']['frames']
    expected_duration = expected_frames / 25.0
    soft = render_soft(mix)
    bar = render_bar(soft, expected_frames, expected_duration)
    tts = json.loads(TTS.read_text())
    manifest = {
        'schema_version': 1,
        'part_id': '02XpQTA-_XE-P0006',
        'status': 'draft_rendered_pending_human_review',
        'lipsync': False,
        'method': 'cleaned Demucs music stem + processed PT-BR dialogue + sidechain ducking',
        'voice_gate': tts['voice_gate'],
        'stems': {
            'music_clean': {'path': str(MUSIC.relative_to(ROOT)), 'sha256': sha256(MUSIC)},
            'vocals_original': {'path': str(VOCALS.relative_to(ROOT)), 'sha256': sha256(VOCALS)},
            'dialogue_raw': {'path': str(raw.relative_to(ROOT)), **raw_meta},
            'dialogue_processed': {'path': str(dialogue.relative_to(ROOT)),
                                   'sha256': sha256(dialogue), 'probe': probe(dialogue)},
            'mix': {'path': str(mix.relative_to(ROOT)), 'sha256': sha256(mix),
                    'probe': probe(mix), 'loudness': loudness(mix)},
        },
        'outputs': {},
        'limitations': [
            'Demucs separation is an estimate; residual bleed may remain',
            'EQ/denoise reduce stridency but cannot restore separation damage',
            'turn grouping and grammar review are drafts; native review pending',
            'no lip sync and no audiovisual approval',
            'soft variant still shows original burned-in English subtitles',
            'bar variant covers lower 180 px and burns PT-BR subtitles',
        ],
    }
    for path in (soft, bar):
        output_probe = probe(path)
        if output_probe['video']['frames'] != expected_frames:
            raise SystemExit(f'frame count changed: {path.name}')
        if abs(output_probe['duration'] - expected['duration']) > 0.20:
            raise SystemExit(f'duration changed: {path.name}')
        manifest['outputs'][path.name] = {
            'sha256': sha256(path), 'bytes': path.stat().st_size,
            'probe': output_probe, 'loudness': loudness(path),
            'states': {'technical_qa': 'pending', 'audiovisual_review': 'pending',
                       'approval': 'pending'},
        }
    (OUT / 'render-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'soft': str(soft), 'bar': str(bar), 'mix': str(mix),
                      'loudness': manifest['stems']['mix']['loudness']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
