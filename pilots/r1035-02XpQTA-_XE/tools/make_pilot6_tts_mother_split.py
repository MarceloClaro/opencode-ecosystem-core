#!/usr/bin/env python3
"""Synthesize the split mother phone lines with the clean mother reference."""
import hashlib, json, subprocess
from pathlib import Path
import torch, soundfile as sf
import TTS.tts.models.xtts as xtts

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / 'voices/voices.json').read_text())
OUT = ROOT / 'pilot-P0006/tts-reviewed'
OUT.mkdir(parents=True, exist_ok=True)
SNAP = Path('/home/marceloclaro/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/345b56f6fbe25cca7103f7f34e471b8fe8e4945f')
LINES = [('T017A', 'Alô, Çağla? Por que não atende?', 140, 2.92),
         ('T017B', 'Horas ligando, quase enlouqueci.', 120, 2.38)]


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


def load_audio(path, sampling_rate):
    import librosa
    wav, _ = librosa.load(path, sr=sampling_rate, mono=True)
    return torch.from_numpy(wav).unsqueeze(0)


xtts.load_audio = load_audio
from TTS.api import TTS
torch.set_num_threads(4)
record = REGISTRY['characters']['char_mother']
reference = ROOT / record['reference']
tts = TTS(model_path=str(SNAP / 'model.pth'), config_path=str(SNAP / 'config.json'),
          progress_bar=False)
manifest = []
for turn_id, text, tokens, available in LINES:
    raw = OUT / f'.{turn_id}-raw.wav'; clipped = OUT / f'.{turn_id}-clip.wav'
    final = OUT / f'{turn_id}.wav'
    if final.exists():
        raise SystemExit(f'refusing overwrite: {final}')
    wav = tts.tts(text=text, speaker_wav=str(reference), language='pt', speed=1.0,
                  split_sentences=False, max_new_tokens=tokens,
                  enable_text_splitting=False)
    sf.write(str(raw), wav, 24000)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(raw), '-af',
                    'silenceremove=start_periods=1:start_silence=0.02:start_threshold=-35dB,'
                    'areverse,silenceremove=start_periods=1:start_silence=0.02:start_threshold=-35dB,areverse',
                    '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', '-y', str(clipped)],
                   check=True, timeout=120)
    seconds = duration(clipped); tempo = 1.0
    if seconds > available + 0.10:
        tempo = min(1.15, seconds / max(0.25, available + 0.05))
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(clipped),
                        '-af', f'atempo={tempo:.6f}', '-ar', '24000', '-ac', '1',
                        '-c:a', 'pcm_s16le', '-y', str(final)], check=True, timeout=120)
        final_seconds = duration(final)
    else:
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(clipped),
                        '-c:a', 'copy', '-y', str(final)], check=True, timeout=120)
        final_seconds = seconds
    raw.unlink(); clipped.unlink()
    manifest.append({'id': turn_id, 'character_id': 'char_mother', 'text': text,
                     'reference': record['reference'], 'reference_sha256': record['sha256'],
                     'available_seconds': available, 'final_seconds': round(final_seconds, 3),
                     'atempo': round(tempo, 6), 'overrun': final_seconds > available + 0.35,
                     'artifact': str(final.relative_to(ROOT)), 'sha256': sha256(final)})
    print(turn_id, round(seconds, 2), '->', round(final_seconds, 2), '/', available, flush=True)
(OUT / 'mother-split-manifest.json').write_text(json.dumps({
    'schema_version': 1, 'part_id': '02XpQTA-_XE-P0006', 'fixes': manifest,
    'limitations': ['mother phone turn split into two lines for fit',
                    'same clean mother reference', 'no approval'],
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'lines': len(manifest)}))
