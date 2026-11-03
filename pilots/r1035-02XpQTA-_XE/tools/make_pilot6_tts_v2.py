#!/usr/bin/env python3
"""Character-aware XTTS batch for P0006; one global reference per character."""
import hashlib
import json
import subprocess
from pathlib import Path
import torch
import soundfile as sf
import TTS.tts.models.xtts as xtts

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE = ROOT / 'pilot-P0006/dialogue-dub-characters.json'
REGISTRY = ROOT / 'voices/voices.json'
MAPPING = ROOT / 'pilot-P0006/speaker-map.json'
OUT = ROOT / 'pilot-P0006/tts-v2'
TMP = ROOT / 'pilot-P0006/tts-tmp-v2'
SNAP = Path('/home/marceloclaro/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/345b56f6fbe25cca7103f7f34e471b8fe8e4945f')
SPEED = 1.3
MAX_ATEMPO = 1.5

import sys
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_voice_registry import validate_dialogue, validate_registry  # noqa: E402

OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)


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

registry = validate_registry(json.loads(REGISTRY.read_text()), root=ROOT)
mapping = json.loads(MAPPING.read_text())
dialogue = json.loads(DIALOGUE.read_text())
receipt = validate_dialogue(dialogue, mapping, registry)
tts = TTS(model_path=str(SNAP / 'model.pth'), config_path=str(SNAP / 'config.json'),
          progress_bar=False)
manifest = []
for unit in dialogue['units']:
    character = unit['character_id']
    record = registry['characters'][character]
    reference = Path(record['reference'])
    expected_hash = record['sha256']
    text = unit['fit_text_pt']
    words = len(text.split())
    max_tokens = min(140, max(40, 18 * words + 20))
    raw = TMP / f'{unit["id"]}-raw.wav'
    clipped = TMP / f'{unit["id"]}-clipped.wav'
    final = OUT / f'{unit["id"]}.wav'
    if final.exists():
        raise SystemExit(f'refusing overwrite: {final}')
    wav = tts.tts(text=text, speaker_wav=str(reference), language='pt',
                  speed=SPEED, split_sentences=False, max_new_tokens=max_tokens,
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
    assert sha256(reference) == expected_hash
    manifest.append({
        'id': unit['id'], 'character_id': character, 'speaker': unit['speaker'],
        'text': text, 'reference': str(reference), 'reference_sha256': expected_hash,
        'registry_sha256': receipt['registry_sha256'],
        'available_seconds': available, 'slot_seconds': unit['slot_seconds'],
        'raw_seconds': round(raw_seconds, 3), 'final_seconds': round(final_seconds, 3),
        'atempo': round(tempo, 6), 'overrun': overrun,
        'artifact': str(final.relative_to(ROOT)), 'sha256': sha256(final),
        'start_part': unit['start_part'],
    })
    print(unit['id'], character, f'{raw_seconds:.2f}->{final_seconds:.2f}/{available:.2f}',
          'OVERRUN' if overrun else '', flush=True)
payload = {
    'schema_version': 1,
    'part_id': dialogue['part_id'],
    'engine': 'XTTS v2 CPU, patched librosa loader',
    'language': 'pt',
    'speed': SPEED,
    'max_atempo': MAX_ATEMPO,
    'voice_gate': {
        'status': receipt['status'],
        'registry_sha256': receipt['registry_sha256'],
        'mapping_sha256': receipt['mapping_sha256'],
        'characters': sorted(receipt['characters']),
    },
    'status': 'tts_generated_pending_audiovisual_review',
    'identity_verified': False,
    'units': manifest,
    'limitations': [
        'one global reference per character; no second voice for the same role',
        'machine TTS/cloning; no native-speaker or audiovisual approval',
        'some lines may overrun; review overlap',
        'no lip sync, no subtitles and no final mix in this step',
        'XTTS v2 CPML non-commercial; publication not assumed',
    ],
}
(ROOT / 'pilot-P0006/tts-manifest-v2.json').write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'lines': len(manifest), 'overruns': sum(x['overrun'] for x in manifest),
                  'characters': sorted(receipt['characters'])}, ensure_ascii=False))
