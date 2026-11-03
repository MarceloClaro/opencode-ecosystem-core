#!/usr/bin/env python3
"""Rebuild every character reference from the Demucs vocals stem."""
import hashlib
import json
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCALS = ROOT / 'pilot-P0006/stems/vocals.wav'
DIALOGUE = json.loads((ROOT / 'pilot-P0006/dialogue-dub-characters.json').read_text())
VOICES = ROOT / 'voices/voices.json'
OUT = ROOT / 'pilot-P0006/references-clean'
OUT.mkdir(parents=True, exist_ok=True)
MAPPING = {'char_male_a': 'spk1', 'char_cagla': 'spk2',
           'char_ruya': 'spk3', 'char_mother': 'spk4'}
TARGET = {'char_male_a': 9.0, 'char_cagla': 12.0,
          'char_ruya': 6.0, 'char_mother': 7.0}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def duration(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                 'format=duration', '-of', 'csv=p=0', str(path)],
                                capture_output=True, text=True, check=True).stdout.strip())


units_by_char = {}
for unit in DIALOGUE['units']:
    units_by_char.setdefault(unit['character_id'], []).append(unit)

manifest = {}
for character, units in units_by_char.items():
    selected, total = [], 0.0
    for unit in units:
        if total >= TARGET[character]:
            break
        selected.append(unit)
        total += unit['slot_seconds']
    chunks = []
    for unit in selected:
        tmp = OUT / f'.{character}-{unit["id"]}.wav'
        subprocess.run([
            'ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{unit["start_part"]:.3f}',
            '-t', f'{unit["slot_seconds"]:.3f}', '-i', str(VOCALS), '-vn',
            '-ac', '1', '-ar', '24000', '-c:a', 'pcm_s16le', '-y', str(tmp),
        ], check=True, timeout=120)
        with wave.open(str(tmp), 'rb') as stream:
            chunks.append(stream.readframes(stream.getnframes()))
        tmp.unlink()
    raw = OUT / f'.{character}-raw.wav'
    gap = b'\x00\x00' * (int(24000 * (0.02 if character == 'char_ruya' else 0.12)))
    with wave.open(str(raw), 'wb') as stream:
        stream.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        for index, chunk in enumerate(chunks):
            if index and gap:
                stream.writeframes(gap)
            stream.writeframes(chunk)
    target = OUT / f'{character}.wav'
    subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error', '-i', str(raw),
        '-af', 'loudnorm=I=-20:TP=-2:LRA=7', '-ar', '24000', '-ac', '1',
        '-c:a', 'pcm_s16le', '-y', str(target),
    ], check=True, timeout=120)
    raw.unlink()
    manifest[character] = {
        'path': str(target.relative_to(ROOT)), 'sha256': sha256(target),
        'duration_seconds': round(duration(target), 3),
        'source': 'Demucs htdemucs vocals stem',
        'source_units': [unit['id'] for unit in selected],
        'normalization': 'loudnorm I=-20 TP=-2 LRA=7',
    }
# update registry and local speaker audit
registry = json.loads(VOICES.read_text())
speakers = json.loads((ROOT / 'pilot-P0006/speakers.json').read_text())
for character, record in manifest.items():
    old = registry['characters'][character]
    old.setdefault('reference_before_demucs', old['reference'])
    old.setdefault('reference_before_demucs_sha256', old['sha256'])
    old['reference'] = record['path']
    old['sha256'] = record['sha256']
    old['voice_status'] = 'cloned_from_demucs_vocals'
    old['source_units'] = record['source_units']
    old['cleanup'] = 'Demucs vocals stem + loudnorm'
    local = MAPPING[character]
    speakers['speakers'][local].setdefault('reference_before_demucs',
                                           speakers['speakers'][local]['reference'])
    speakers['speakers'][local].setdefault('reference_before_demucs_sha256',
                                           speakers['speakers'][local]['sha256'])
    speakers['speakers'][local]['reference'] = record['path']
    speakers['speakers'][local]['sha256'] = record['sha256']
    speakers['speakers'][local]['duration_seconds'] = record['duration_seconds']
    speakers['speakers'][local]['cleanup'] = 'Demucs vocals stem + loudnorm'
VOICES.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'pilot-P0006/speakers.json').write_text(
    json.dumps(speakers, ensure_ascii=False, indent=2) + '\n')
(OUT / 'references-clean.json').write_text(json.dumps({
    'schema_version': 1, 'part_id': DIALOGUE['part_id'],
    'source_stem': str(VOCALS.relative_to(ROOT)),
    'characters': manifest,
    'limitations': ['Demucs separation is an estimate; bleed may remain',
                    'reference identity is not verified',
                    'phone-filtered voice of the mother may remain narrowband'],
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v['duration_seconds'] for k, v in manifest.items()},
                 ensure_ascii=False))
