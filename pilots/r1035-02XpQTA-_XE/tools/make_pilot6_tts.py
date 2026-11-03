#!/usr/bin/env python3
"""Synthesize pilot P0006 lines with XTTS v2; draft, no lip sync or approval."""
import hashlib
import json
import subprocess
from pathlib import Path
import torch
import soundfile as sf
import TTS.tts.models.xtts as xtts

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE = ROOT / 'pilot-P0006/dialogue-dub.json'
SPEAKERS = ROOT / 'pilot-P0006/speakers.json'
OUT = ROOT / 'pilot-P0006/tts'
TMP = ROOT / 'pilot-P0006/tts-tmp'
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
SNAP = Path('/home/marceloclaro/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/345b56f6fbe25cca7103f7f34e471b8fe8e4945f')
SPEED = 1.3
MAX_ATEMPO = 1.5


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def duration(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                             '-of', 'csv=p=0', str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def load_audio(path, sampling_rate):
    import librosa
    wav, _ = librosa.load(path, sr=sampling_rate, mono=True)
    return torch.from_numpy(wav).unsqueeze(0)


xtts.load_audio = load_audio
from TTS.api import TTS
torch.set_num_threads(4)
tts = TTS(model_path=str(SNAP / 'model.pth'), config_path=str(SNAP / 'config.json'),
          progress_bar=False)
dialogue = json.loads(DIALOGUE.read_text())
registry = json.loads(SPEAKERS.read_text())
manifest = []
for unit in dialogue['units']:
    speaker = unit['speaker']
    reference = ROOT / registry['speakers'][speaker]['reference']
    raw = TMP / f'{unit["id"]}-raw.wav'
    clipped = TMP / f'{unit["id"]}-clipped.wav'
    final = OUT / f'{unit["id"]}.wav'
    if final.exists():
        raise SystemExit(f'refusing overwrite: {final}')
    wav = tts.tts(text=unit['fit_text_pt'], speaker_wav=str(reference), language='pt',
                  speed=SPEED, split_sentences=False, max_new_tokens=200,
                  enable_text_splitting=False)
    sf.write(str(raw), wav, 24000)
    subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error', '-i', str(raw), '-af',
        'silenceremove=start_periods=1:start_silence=0.02:start_threshold=-35dB,'
        'areverse,silenceremove=start_periods=1:start_silence=0.02:start_threshold=-35dB,areverse',
        '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', '-y', str(clipped),
    ], check=True, timeout=120)
    raw_seconds = duration(clipped)
    available = float(unit['available_seconds'])
    tempo = 1.0
    overrun = False
    if raw_seconds > available + 0.10:
        tempo = min(MAX_ATEMPO, raw_seconds / max(0.20, available + 0.05))
        subprocess.run([
            'ffmpeg', '-nostdin', '-v', 'error', '-i', str(clipped),
            '-af', f'atempo={tempo:.6f}', '-ar', '24000', '-ac', '1',
            '-c:a', 'pcm_s16le', '-y', str(final),
        ], check=True, timeout=120)
        final_seconds = duration(final)
        overrun = final_seconds > available + 0.30
    else:
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(clipped),
                        '-c:a', 'copy', '-y', str(final)], check=True, timeout=120)
        final_seconds = raw_seconds
    manifest.append({
        'id': unit['id'], 'speaker': speaker, 'text': unit['fit_text_pt'],
        'reference': registry['speakers'][speaker]['reference'],
        'reference_sha256': registry['speakers'][speaker]['sha256'],
        'available_seconds': available, 'slot_seconds': unit['slot_seconds'],
        'raw_seconds': round(raw_seconds, 3), 'final_seconds': round(final_seconds, 3),
        'atempo': round(tempo, 6), 'overrun': overrun,
        'artifact': str(final.relative_to(ROOT)), 'sha256': sha256(final),
        'start_part': unit['start_part'],
    })
    print(unit['id'], speaker, f'{raw_seconds:.2f}->{final_seconds:.2f}/{available:.2f}', flush=True)
payload = {
    'schema_version': 1,
    'part_id': dialogue['part_id'],
    'engine': 'XTTS v2 CPU, patched librosa loader',
    'language': 'pt',
    'speed': SPEED,
    'max_atempo': MAX_ATEMPO,
    'status': 'tts_generated_pending_audiovisual_review',
    'identity_verified': False,
    'units': manifest,
    'limitations': [
        'machine TTS and cloning; no native-speaker or audiovisual approval',
        'some lines may overrun the next line start; review overlap',
        'no lip sync, no subtitles and no final mix in this step',
        'XTTS v2 CPML non-commercial; publication not assumed',
    ],
}
(ROOT / 'pilot-P0006/tts-manifest.json').write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'lines': len(manifest), 'overruns': sum(x['overrun'] for x in manifest)}))
