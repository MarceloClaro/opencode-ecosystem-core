#!/usr/bin/env python3
"""R1047 — dublagem PT-BR com voz clonada, slide traduzido e legenda.

Não sobrescreve o original. Usa XTTS local, referência declarada pelo operador
e vídeo full-frame sem cartão. A aprovação editorial/linguística continua
humana; o manifesto registra isso explicitamente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BASE = Path(os.environ.get('OPENCODE_PILOT_BASE', Path.home() / '.cache/opencode-pilot'))
PILOT = Path(__file__).resolve().parents[1]
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def run(args, **kwargs):
    proc = subprocess.run(args, capture_output=True, text=True, **kwargs)
    if proc.returncode:
        tail = (proc.stderr or proc.stdout or '')[-1800:]
        raise RuntimeError(f'command failed ({args[0]}): {tail}')
    return proc.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def duration(path: Path) -> float:
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'default=nw=1:nk=1', str(path)]).strip())


def norm_tts_text(text: str) -> str:
    """Remove ponto final; mantém vírgulas e dois-pontos para pausa natural."""
    return re.sub(r'[.!?]+\s*$', '', text.strip())


def trim_silence(source: Path, target: Path) -> None:
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(source), '-af',
         'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,'
         'areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,'
         'areverse,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo',
         '-ar', '48000', '-ac', '2', str(target)])


def atempo(source: Path, target: Path, factor: float) -> None:
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(source), '-af',
         f'atempo={factor:.8f},aresample=48000,'
         'aformat=sample_fmts=fltp:channel_layouts=stereo',
         '-ar', '48000', '-ac', '2', str(target)])


def load_xtts():
    """Carrega XTTS com leitura WAV via soundfile, sem torchcodec."""
    os.environ.setdefault('TTS_HOME', str(BASE / 'tts'))
    os.environ.setdefault('XDG_DATA_HOME', str(BASE / 'xdg'))
    os.environ.setdefault('COQUI_TOS_AGREED', '1')
    import librosa
    import soundfile as sf
    import torch
    import TTS.tts.models.xtts as xtts

    def _load_audio_sf(path, sampling_rate):
        wav, sr = sf.read(path, dtype='float32', always_2d=False)
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        if sr != sampling_rate:
            wav = librosa.resample(wav, orig_sr=sr, target_sr=sampling_rate)
        return torch.from_numpy(wav).float().unsqueeze(0)

    xtts.load_audio = _load_audio_sf
    from TTS.api import TTS
    return TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cpu')


def srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}'


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, centiseconds = divmod(centiseconds, 3600_00)
    minutes, centiseconds = divmod(centiseconds, 60_00)
    secs, centiseconds = divmod(centiseconds, 100)
    return f'{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}'


def write_subtitles(events, out_dir: Path):
    srt = []
    for index, event in enumerate(events, start=1):
        srt.append(f'{index}\n{srt_time(event["start"])} --> {srt_time(event["end"])}\n'
                   + '\n'.join(event['lines']) + '\n')
    srt_path = out_dir / 'captions-r1047.pt-BR.srt'
    srt_path.write_text('\n'.join(srt), encoding='utf-8')

    ass_path = out_dir / 'captions-r1047.pt-BR.ass'
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,42,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,120,120,58,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    lines = []
    for event in events:
        text = '\\N'.join(event['lines'])
        lines.append(f'Dialogue: 0,{ass_time(event["start"])},{ass_time(event["end"])},'
                     f'Caption,,0,0,0,,{text}')
    ass_path.write_text(header + '\n'.join(lines) + '\n', encoding='utf-8')
    return srt_path, ass_path


def loudness(path: Path):
    proc = subprocess.run(
        ['ffmpeg', '-nostdin', '-hide_banner', '-i', str(path), '-af',
         'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
        capture_output=True, text=True)
    match = re.search(r'\{[^{}]*"input_i"[^{}]*\}', proc.stderr, re.S)
    if not match:
        return {'raw': 'unavailable'}
    return json.loads(match.group(0))


def probe(path: Path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                           '-of', 'json', str(path)]))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--narration', type=Path,
                        default=Path(__file__).with_name('narration.pt-BR.json'))
    parser.add_argument('--out-dir', type=Path,
                        default=Path(__file__).with_name('out'))
    parser.add_argument('--video', type=Path, default=PILOT / 'presenter-middle-1080.mp4')
    parser.add_argument('--patch', type=Path,
                        default=Path(__file__).with_name('slide-patch-r1047.png'))
    parser.add_argument('--mask', type=Path,
                        default=Path(__file__).with_name('slide-patch-r1047-mask.png'))
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args(argv)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    if not args.video.is_file() or not args.patch.is_file() or not args.mask.is_file():
        raise SystemExit('vídeo, patch ou máscara ausente')
    narration = json.loads(args.narration.read_text(encoding='utf-8'))
    if not narration.get('segments'):
        raise SystemExit('narração sem segmentos')
    reference = Path(narration['voice_reference'])
    if not reference.is_file():
        reference = BASE / 'refs/presenter-ref.wav'
    if not reference.is_file():
        raise SystemExit(f'referência ausente: {reference}')

    tts = load_xtts()
    raw_dir = out / 'segments'
    raw_dir.mkdir(exist_ok=True)
    segments = []
    for segment in narration['segments']:
        raw = raw_dir / f"raw-{segment['id']}.wav"
        clean = raw_dir / f"clean-{segment['id']}.wav"
        if args.force or not raw.is_file():
            tts.tts_to_file(
                text=norm_tts_text(segment['tts_text']),
                speaker_wav=str(reference), language='pt',
                file_path=str(raw), split_sentences=False,
                speed=float(narration['speed']))
        trim_silence(raw, clean)
        segments.append({**segment, 'raw': raw, 'clean': clean,
                         'duration': duration(clean)})

    gap = float(narration['gap_seconds'])
    start = float(narration['start_seconds'])
    max_end = float(narration['max_end_seconds'])
    total = sum(item['duration'] for item in segments) + gap * (len(segments) - 1)
    available = max_end - start
    tempo = max(1.0, total / available)
    # Aceleração só se necessária; 1.18 é o limite de naturalidade desta rodada.
    if tempo > 1.18:
        raise SystemExit(f'narração longa demais: {total:.2f}s; '
                         f'atempo {tempo:.2f} acima do limite 1.18')
    for item in segments:
        if tempo > 1.001:
            fitted = raw_dir / f"fit-{item['id']}.wav"
            atempo(item['clean'], fitted, tempo)
            item['duration'] = duration(fitted)
        else:
            fitted = item['clean']
        item['fitted'] = fitted
        item['duration'] = duration(fitted)

    # Recalcula inícios sequenciais e eventos de legenda sem sobreposição.
    cursor = start
    for item in segments:
        item['start'] = cursor
        item['end'] = cursor + item['duration']
        cursor = item['end'] + gap
    events = []
    for index, item in enumerate(segments):
        next_start = (segments[index + 1]['start'] if index + 1 < len(segments)
                      else max_end)
        events.append({'start': item['start'],
                       'end': min(item['end'] + 0.25, next_start - 0.05, max_end),
                       'lines': item['subtitle_lines']})
    if cursor - gap > max_end:
        raise SystemExit('narração excede a janela de 20 s')
    for event in events:
        chars = len(' '.join(event['lines']))
        cps = chars / max(0.1, event['end'] - event['start'])
        if cps > 17:
            raise SystemExit(f'legenda acima de 17 CPS: {cps:.1f}')

    # Mix: silêncio de 20 s + cada segmento no seu início, depois loudness.
    inputs = ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo:d=20']
    filters = []
    labels = ['[0:a]']
    for index, item in enumerate(segments, start=1):
        inputs += ['-i', str(item['fitted'])]
        delay = round(item['start'] * 1000)
        filters.append(f'[{index}:a]adelay={delay}|{delay}[a{index}]')
        labels.append(f'[a{index}]')
    mix = (''.join(labels)
           + f'amix=inputs={len(labels)}:duration=first:dropout_transition=0:normalize=0,'
             'loudnorm=I=-16:TP=-1.5:LRA=11,atrim=0:20,'
             'afade=t=in:st=0:d=0.25,afade=t=out:st=19.6:d=0.4[a]')
    audio = out / 'dub-r1047.pt-BR.wav'
    run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex',
         ';'.join(filters + [mix]), '-map', '[a]', '-t', '20',
         '-ar', '48000', '-ac', '2', str(audio)])

    srt, ass = write_subtitles(events, out)
    video = out / 'quantum-ptbr-r1047.mp4'
    label = "voz sintética • PT-BR"
    overlay = (
        f"[0:v]fps=30,setsar=1[base];"
        f"[1:v]format=rgba[patch];[2:v]format=gray[mask];"
        f"[patch][mask]alphamerge[patchm];"
        f"[base][patchm]overlay=210:76:format=auto,"
        f"subtitles=filename='{ass}':fontsdir=/usr/share/fonts/truetype/dejavu,"
        f"drawtext=fontfile='{FONT}':text='{label}':fontcolor=white@0.65:fontsize=17:"
        f"x=w-tw-40:y=72:box=1:boxcolor=black@0.35:boxborderw=8[v];"
        f"[3:a]atrim=0:20,asetpts=PTS-STARTPTS[a]"
    )
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(args.video),
         '-loop', '1', '-i', str(args.patch), '-loop', '1', '-i', str(args.mask),
         '-i', str(audio), '-filter_complex', overlay,
         '-map', '[v]', '-map', '[a]', '-t', '20',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k',
         '-ar', '48000', '-movflags', '+faststart', str(video)])

    frames = out / 'frames'
    frames.mkdir(exist_ok=True)
    for second in (2, 8, 14, 18):
        run(['ffmpeg', '-y', '-v', 'error', '-ss', str(second), '-i', str(video),
             '-frames:v', '1', str(frames / f'frame-{second:02d}.png')])
    contact = out / 'contact.png'
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(video), '-vf',
         "select='eq(n,60)+eq(n,240)+eq(n,420)+eq(n,540)',scale=640:360,tile=2x2",
         '-frames:v', '1', str(contact)])

    manifest = {
        'schema_version': 'r1047.quantum.dub.v1',
        'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'source': {'video': str(args.video), 'sha256': sha256(args.video),
                   'card_present': False},
        'voice': {'model': narration['model'], 'license': narration['model_license'],
                  'reference': str(reference), 'reference_sha256': sha256(reference),
                  'consent': narration['consent'], 'speed': narration['speed']},
        'script': {'path': str(args.narration), 'sha256': sha256(args.narration),
                   'segments': [{'id': item['id'], 'text': item['tts_text'],
                                 'display': item['display_text'],
                                 'start': round(item['start'], 3),
                                 'speech_end': round(item['end'], 3),
                                 'duration': round(item['duration'], 3)}
                                for item in segments],
                   'tempo_factor': round(tempo, 6)},
        'subtitle': {'srt': str(srt), 'srt_sha256': sha256(srt),
                     'ass': str(ass), 'ass_sha256': sha256(ass),
                     'cps_max': round(max(len(' '.join(e['lines'])) /
                                         (e['end'] - e['start']) for e in events), 2)},
        'audio': {'path': str(audio), 'sha256': sha256(audio),
                  'duration': duration(audio), 'loudness': loudness(audio)},
        'video': {'path': str(video), 'sha256': sha256(video),
                  'bytes': video.stat().st_size,
                  'probe': probe(video)},
        'claims': {
            'voice_clone_generated': True,
            'subtitle_generated': True,
            'slide_translated': True,
            'presenter_card_present': False,
            'lip_sync_resynchronized': False,
            'audiovisual_approved': False,
            'translation_human_reviewed': False,
            'scientific_validity_verified': False,
            'published': False
        },
        'limitations': [
            'A voz é sintética e pode conter artefatos; revisão auditiva humana pendente.',
            'O vídeo base tem lip sync anterior; a nova locução NÃO foi re-sincronizada nesta rodada.',
            'A tradução do slide e da fala é interpretativa; revisão bilíngue humana pendente.',
            'Testes técnicos não aprovam estética, naturalidade, emoção ou validade científica.',
            'Uso não comercial; XTTS/CPML e consentimento declarado, não verificado.'
        ]
    }
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                                        encoding='utf-8')
    print(json.dumps({'video': str(video), 'manifest': str(out / 'manifest.json'),
                      'sha256': manifest['video']['sha256'],
                      'segments': manifest['script']['segments'],
                      'tempo_factor': manifest['script']['tempo_factor'],
                      'subtitle_cps_max': manifest['subtitle']['cps_max']},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
