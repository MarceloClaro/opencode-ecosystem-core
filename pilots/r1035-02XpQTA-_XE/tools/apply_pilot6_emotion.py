#!/usr/bin/env python3
"""Apply conservative emotion prosody to validated takes; fit/fallback on duration."""
import hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMOTION = json.loads((ROOT / 'pilot-P0006/dialogue-turns-emotion.json').read_text())
TTS = json.loads((ROOT / 'pilot-P0006/tts-manifest-final5.json').read_text())
OUT = ROOT / 'pilot-P0006/tts-emotion'
OUT.mkdir(parents=True, exist_ok=True)
by_id = {t['id']: t for t in TTS['turns']}
emotion_by_id = {t['id']: t for t in EMOTION['turns']}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def duration(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', str(path)], capture_output=True, text=True,
                                check=True).stdout.strip())


def render(source, target, tempo, pitch, gain):
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(source),
                    '-af', f'rubberband=tempo={tempo:.4f}:pitch={pitch:.4f},volume={gain:.2f}dB',
                    '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', '-y', str(target)],
                   check=True, timeout=120)


manifest = []
for turn in EMOTION['turns']:
    item = by_id[turn['id']]
    source = ROOT / item['artifact']
    target = OUT / f'{turn["id"]}.wav'
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    p = turn['intent']['prosody']
    tempo, pitch, gain = p['tempo'], p['pitch'], p['gain_db']
    available = float(item['available_seconds'])
    render(source, target, tempo, pitch, gain)
    seconds = duration(target)
    fallback = False
    if seconds > available + 0.35:
        # Reduce the tempo change toward neutral once.
        tempo = 1 + (tempo - 1) * 0.5
        render(source, target, tempo, pitch, gain)
        seconds = duration(target)
    if seconds > available + 0.35:
        fallback = True
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(source),
                        '-c:a', 'copy', '-y', str(target)], check=True, timeout=120)
        seconds = duration(target)
        tempo, pitch, gain = 1.0, 1.0, 0.0
    manifest.append({'id': turn['id'], 'character_id': turn['character_id'],
                     'emotion': turn['intent']['emotion'],
                     'intensity': turn['intent']['intensity'],
                     'irony': turn['intent']['irony'],
                     'tempo': round(tempo, 4), 'pitch': round(pitch, 4),
                     'gain_db': round(gain, 2), 'fallback_neutral': fallback,
                     'available_seconds': available, 'final_seconds': round(seconds, 3),
                     'artifact': str(target.relative_to(ROOT)), 'sha256': sha256(target),
                     'source_sha256': item['sha256']})
    print(turn['id'], turn['intent']['emotion'], f'{tempo:.3f}/{pitch:.3f}/{gain:+.1f}',
          f'{seconds:.2f}/{available:.2f}', 'FALLBACK' if fallback else '', flush=True)
payload = {'schema_version': 1, 'part_id': EMOTION['part_id'],
           'status': 'emotion_prosody_applied_pending_asr_gate', 'takes': manifest,
           'limitations': ['tempo/pitch/energy are prosody approximations, not certified emotion',
                           'fallback to neutral when duration exceeds limit',
                           'no native/audiovisual approval']}
(OUT / 'emotion-prosody-manifest.json').write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'takes': len(manifest),
                  'fallbacks': sum(t['fallback_neutral'] for t in manifest)}))
