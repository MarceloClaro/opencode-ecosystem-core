#!/usr/bin/env python3
"""Extract speaker reference clips for pilot P0006; no identity verification."""
import hashlib
import json
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'parts-extracted/parts/02XpQTA-_XE-P0006.mp4'
DIALOGUE = ROOT / 'pilot-P0006/dialogue-reviewed.json'
OUT = ROOT / 'pilot-P0006/references'
OUT.mkdir(parents=True, exist_ok=True)
SILENCE = b'\x00\x00' * int(24000 * 0.15)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


dialogue = json.loads(DIALOGUE.read_text())
groups = {}
for unit in dialogue['units']:
    if unit['slot_seconds'] < 0.30:
        continue
    groups.setdefault(unit['speaker'], []).append(unit)

metadata = {}
for speaker, units in sorted(groups.items()):
    chunks = []
    for unit in units:
        raw = OUT / f'.{speaker}-{unit["id"]}.wav'
        subprocess.run([
            'ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{unit["start_part"]:.3f}',
            '-t', f'{unit["slot_seconds"]:.3f}', '-i', str(PART), '-vn',
            '-ac', '1', '-ar', '24000', '-c:a', 'pcm_s16le', '-y', str(raw),
        ], check=True, timeout=120)
        with wave.open(str(raw), 'rb') as stream:
            chunks.append(stream.readframes(stream.getnframes()))
        raw.unlink()
    target = OUT / f'{speaker}.wav'
    with wave.open(str(target), 'wb') as stream:
        stream.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        for index, chunk in enumerate(chunks):
            if index:
                stream.writeframes(SILENCE)
            stream.writeframes(chunk)
    with wave.open(str(target), 'rb') as stream:
        duration = stream.getnframes() / stream.getframerate()
    metadata[speaker] = {
        'role_hint': {'spk1': 'homem na cena A', 'spk2': 'Çağla (inferido)',
                      'spk3': 'Rüya (inferido)', 'spk4': 'mãe ao telefone (inferida)'}.get(speaker, ''),
        'reference': str(target.relative_to(ROOT)),
        'sha256': sha256(target),
        'duration_seconds': round(duration, 3),
        'source_units': [unit['id'] for unit in units],
        'limitations': ['reference may contain original music/effects',
                        'identity not verified; consent is user-declared'],
    }
registry = {
    'schema_version': 1,
    'part_id': dialogue['part_id'],
    'voice_cloning_authorized_by_user': True,
    'documents_verified': False,
    'identity_verified': False,
    'speakers': metadata,
    'limitations': [
        'speaker labels are heuristic, not biometric identification',
        'reference clips come from the mixed source and may include music/effects',
        'XTTS v2 is CPML non-commercial; no publication or commercial use assumed',
    ],
}
(ROOT / 'pilot-P0006/speakers.json').write_text(
    json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'references': {k: v['duration_seconds'] for k, v in metadata.items()}},
                 ensure_ascii=False))
