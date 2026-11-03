#!/usr/bin/env python3
"""Separate P0006 into Demucs stems; clean references and music bed."""
import hashlib
import json
import subprocess
from pathlib import Path
import torch
import soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'parts-final/parts/02XpQTA-_XE-P0006.mp4'
OUT = ROOT / 'pilot-P0006/stems'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = OUT / 'source-44k.wav'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


if SOURCE.exists():
    raise SystemExit(f'refusing overwrite: {SOURCE}')
subprocess.run([
    'ffmpeg', '-nostdin', '-v', 'error', '-i', str(PART), '-vn',
    '-ac', '2', '-ar', '44100', '-c:a', 'pcm_s16le', '-y', str(SOURCE),
], check=True, timeout=300)
wav, sr = sf.read(str(SOURCE), dtype='float32', always_2d=True)
if sr != 44100:
    raise SystemExit(f'unexpected sample rate: {sr}')
tensor = torch.from_numpy(wav.T).unsqueeze(0)
torch.set_num_threads(4)
model = get_model('htdemucs')
model.eval()
with torch.no_grad():
    sources = apply_model(model, tensor, device='cpu', shifts=0, split=True,
                          overlap=0.25, progress=False)[0]
stems = {}
for name, stem in zip(model.sources, sources):
    target = OUT / f'{name}.wav'
    sf.write(str(target), stem.T.numpy(), sr, subtype='FLOAT')
    stems[name] = {'path': str(target.relative_to(ROOT)), 'sha256': sha256(target),
                   'duration_seconds': round(stem.shape[-1] / sr, 3)}
music = sources[[model.sources.index(name) for name in ('drums', 'bass', 'other')]].sum(dim=0)
music_path = OUT / 'music.wav'
sf.write(str(music_path), music.T.numpy(), sr, subtype='FLOAT')
stems['music'] = {'path': str(music_path.relative_to(ROOT)), 'sha256': sha256(music_path),
                  'duration_seconds': round(music.shape[-1] / sr, 3)}
manifest = {
    'schema_version': 1,
    'part_id': '02XpQTA-_XE-P0006',
    'model': 'htdemucs (Demucs 4.1.0)',
    'sample_rate': sr,
    'channels': 2,
    'source_audio': str(SOURCE.relative_to(ROOT)),
    'source_sha256': sha256(SOURCE),
    'stems': stems,
    'status': 'stems_generated_pending_mix_and_review',
    'limitations': [
        'source separation is an estimate; residual bleed may remain',
        'music stem is drums+bass+other, not a semantic music classifier',
        'original vocals stem is for reference/QA, not for the final mix',
        'no audiovisual approval',
    ],
}
(OUT / 'stems-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'stems': sorted(stems), 'sr': sr,
                  'duration': stems['music']['duration_seconds']}, ensure_ascii=False))
