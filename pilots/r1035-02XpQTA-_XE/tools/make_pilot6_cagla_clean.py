#!/usr/bin/env python3
"""Regenerate all Cagla turns with the compact clean reference; fit and validate."""
import hashlib, json, subprocess
from pathlib import Path
import torch, soundfile as sf
import TTS.tts.models.xtts as xtts

ROOT = Path(__file__).resolve().parents[1]
TURNS = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
REF = ROOT / 'pilot-P0006/references-clean/char_cagla-compact.wav'
OUT = ROOT / 'pilot-P0006/tts-cagla-clean'
OUT.mkdir(parents=True, exist_ok=True)
SNAP = Path('/home/marceloclaro/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/345b56f6fbe25cca7103f7f34e471b8fe8e4945f')
IDS = ['T002', 'T004', 'T006', 'T008', 'T010', 'T012', 'T014', 'T016', 'T018', 'T020', 'T022']
TEXT = {'T008': 'Bem.', 'T010': 'E você?', 'T014': 'Por quê? Por quê?',
        'T022': 'Mãe, nada. A gente se diverte.'}


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
tts = TTS(model_path=str(SNAP / 'model.pth'), config_path=str(SNAP / 'config.json'),
          progress_bar=False)
by_id = {t['id']: t for t in TURNS['turns']}
manifest = []
for turn_id in IDS:
    turn = by_id[turn_id]
    text = TEXT.get(turn_id, turn['fit_text_pt'])
    words = len(text.split()); tokens = min(220, max(100, 20 * words + 40))
    raw = OUT / f'.{turn_id}-raw.wav'; clip = OUT / f'.{turn_id}-clip.wav'
    final = OUT / f'{turn_id}.wav'
    if final.exists():
        raise SystemExit(f'refusing overwrite: {final}')
    wav = tts.tts(text=text, speaker_wav=str(REF), language='pt', speed=1.0,
                  split_sentences=False, max_new_tokens=tokens,
                  enable_text_splitting=False)
    sf.write(str(raw), wav, 24000)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(raw), '-af',
                    'silenceremove=start_periods=1:start_silence=0.02:start_threshold=-35dB,'
                    'silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-25dB,'
                    'areverse,silenceremove=start_periods=1:start_silence=0.02:start_threshold=-35dB,areverse',
                    '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', '-y', str(clip)],
                   check=True, timeout=120)
    seconds = duration(clip); available = float(turn['available_seconds']); tempo = 1.0
    if seconds > available + 0.10:
        tempo = min(1.50, seconds / max(0.25, available + 0.05))
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(clip),
                        '-af', f'rubberband=tempo={tempo:.4f}', '-ar', '24000', '-ac', '1',
                        '-c:a', 'pcm_s16le', '-y', str(final)], check=True, timeout=120)
        final_seconds = duration(final)
    else:
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(clip),
                        '-c:a', 'copy', '-y', str(final)], check=True, timeout=120)
        final_seconds = seconds
    raw.unlink(); clip.unlink()
    manifest.append({'id': turn_id, 'character_id': 'char_cagla', 'text': text,
                     'reference': str(REF.relative_to(ROOT)), 'reference_sha256': sha256(REF),
                     'available_seconds': available, 'final_seconds': round(final_seconds, 3),
                     'atempo': round(tempo, 6), 'overrun': final_seconds > available + 0.35,
                     'artifact': str(final.relative_to(ROOT)), 'sha256': sha256(final)})
    print(turn_id, round(seconds, 2), '->', round(final_seconds, 2), '/', available, flush=True)
(OUT / 'cagla-clean-manifest.json').write_text(json.dumps({
    'schema_version': 1, 'part_id': TURNS['part_id'], 'takes': manifest,
    'limitations': ['clean compact reference; short lines shortened; no approval'],
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'takes': len(manifest)}))
